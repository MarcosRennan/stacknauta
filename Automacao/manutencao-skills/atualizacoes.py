"""Consulta, preparação isolada e promoção global com diário/backup, só stdlib."""
import contextlib
import difflib
import fcntl
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Automacao/project-bootstrap"))
from stacknauta_core.core import encoded as json_bytes
from stacknauta_core.library import digest as sha
from stacknauta_core import BootstrapError
from atualizacao_receita import refresh, python_dependencies, javascript_imports
from origens import parse_url

SOURCES = {"ui-ux-pro-max", "fastapi", "remy", "expo", "chrisbanes", "android", "sentry"}
NODE_BUILTINS = set(("assert assert/strict async_hooks buffer child_process cluster console constants crypto dgram diagnostics_channel "
                     "dns dns/promises domain events fs fs/promises http http2 https module net os path path/posix path/win32 "
                     "perf_hooks process punycode querystring readline readline/promises repl stream stream/consumers stream/promises "
                     "stream/web string_decoder sys timers timers/promises tls trace_events tty url util util/types v8 vm wasi "
                     "worker_threads zlib").split())


def safe(root, relative):
    p = PurePosixPath(relative)
    if not relative or p.is_absolute() or str(p) != relative or any(x in {"..", ".git"} for x in p.parts) or "\\" in relative or any(ord(c) < 32 for c in relative):
        raise ValueError("Caminho inseguro: " + repr(relative))
    path = root
    for part in p.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Link simbólico indevido: " + relative)
    return path


def read_bytes(root, relative):
    path = safe(root, relative)
    with path.open("rb") as stream:
        s = os.fstat(stream.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_size > 64_000_000:
            raise ValueError("Arquivo não regular, hardlink ou tamanho excessivo: " + relative)
        return stream.read()


def load(root, relative):
    return json.loads(read_bytes(root, relative))


def tree(root):
    result = {}
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs.sort(); files.sort()
        for name in dirs + files:
            p = Path(parent) / name
            if p.is_symlink():
                raise ValueError("Link no candidato distribuível: " + str(p))
        for name in files:
            p = Path(parent) / name; rel = p.relative_to(root).as_posix()
            result[rel] = {"sha256": sha(read_bytes(root, rel)), "mode": stat.S_IMODE(p.stat().st_mode)}
    return result


def atomic_json(path, data):
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("xb") as stream:
        stream.write(json_bytes(data)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)  # Apenas registro próprio; nunca pacote/arquivo do usuário.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: os.fsync(fd)
    finally: os.close(fd)


def move(source, destination):
    if os.path.lexists(destination): raise ValueError("Destino de publicação já existe: " + str(destination))
    os.rename(source, destination)
    for parent in {source.parent, destination.parent}:
        fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(fd)
        finally: os.close(fd)


class Git:
    def __init__(self, allow_local=False):
        self.allow_local = allow_local

    def run(self, repo, *args, data=None, binary=False):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_CONFIG_GLOBAL="/dev/null",
                           GIT_CONFIG_NOSYSTEM="1", GIT_ALLOW_PROTOCOL="https:ssh:file" if self.allow_local else "https:ssh",
                           GIT_SSH_COMMAND="ssh -oBatchMode=yes -oStrictHostKeyChecking=yes -oUpdateHostKeys=no")
        if not self.allow_local and args and args[0] in {'fetch','ls-remote'}:
            # Usar credenciais/proxy existentes, sem gravar config ou iniciar login.
            # Hooks/fsmonitor continuam desativados; não há checkout/filtros.
            environment.pop('GIT_CONFIG_GLOBAL');environment.pop('GIT_CONFIG_NOSYSTEM')
            environment.update(GCM_INTERACTIVE='never',GH_PROMPT_DISABLED='1')
        command = ["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-c", "gc.auto=0",
                   "-c", "maintenance.auto=false", "-c", "http.sslVerify=true", "-c", "fetch.fsckObjects=true",
                   "-c", "http.lowSpeedLimit=100", "-c", "http.lowSpeedTime=15", "-C", str(repo), *args]
        r = subprocess.run(command, input=data, capture_output=True, text=not binary, env=environment, timeout=45)
        if r.returncode:
            detail = r.stderr.decode(errors="replace") if binary else r.stderr
            raise ValueError("Consulta/operação Git falhou: " + detail.strip()[:1500])
        return r.stdout

    def head(self, root): return self.run(root, "rev-parse", "HEAD").strip()

    def remote(self, source):
        url, branch = source["url"], source["branch"]
        if parse_url(url, allow_local=self.allow_local)["tail"]:
            raise ValueError("URL não permitida para origem cadastrada")
        self.run(Path.home(), "check-ref-format", "refs/heads/" + branch)
        output = self.run(Path.home(), "ls-remote", "--symref", url, "HEAD", "refs/heads/" + branch)
        refs = {row.split()[1]: row.split()[0] for row in output.splitlines() if len(row.split()) == 2}
        commit = refs.get("refs/heads/" + branch)
        if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("Repositório/branch indisponível: " + source["id"] + ":" + branch)
        default = next((r.split()[1].removeprefix("refs/heads/") for r in output.splitlines() if r.startswith("ref: ") and r.endswith("\tHEAD")), source["default_branch"])
        return commit, default

    def acquire(self, source, repo, *, discover=False):
        repo.mkdir(parents=True)
        self.run(repo, "init", "--quiet", "--template=")
        self.run(repo, "config", "core.fsmonitor", "false")
        self.run(repo, "fetch", "--quiet", "--depth=1", "--no-tags", "--no-recurse-submodules", source["url"], source["commit"])
        self.run(repo, "symbolic-ref", "HEAD", "refs/heads/" + source["branch"])
        self.run(repo, "update-ref", "HEAD", source["commit"])
        self.run(repo, "read-tree", source["commit"])
        entries = self.run(repo, "ls-tree", "-r", "-z", source["commit"]).split("\0")
        if discover and source.get("sparse_paths"):
            source["sparse_paths"] = sorted(set(source["sparse_paths"]) | {
                str(PurePosixPath(e.split("\t",1)[1]).parent) for e in entries if e and PurePosixPath(e.split("\t",1)[1]).name == "SKILL.md"})
            if "." in source["sparse_paths"]: source["sparse_paths"] = []
        paths, links = [], []
        for entry in entries:
            if not entry: continue
            header, path = entry.split("\t", 1); mode, kind, oid = header.split()
            dest = safe(repo, path); paths.append(path)
            if mode == "160000": continue  # Nunca inicializar submódulos.
            sparse = source.get("sparse_paths", [])
            ancestor_license = PurePosixPath(path).name.upper().startswith(("LICENSE", "COPYING", "NOTICE")) and any(
                PurePosixPath(path).parent == PurePosixPath(prefix).parent or str(PurePosixPath(prefix)).startswith(str(PurePosixPath(path).parent) + "/") for prefix in sparse)
            if sparse and "/" in path and not ancestor_license and not any(path == prefix or path.startswith(prefix + "/") for prefix in sparse): continue
            if mode not in {"100644", "100755", "120000"}: raise ValueError("Modo Git não permitido: " + path)
            data = self.run(repo, "cat-file", "blob", oid, binary=True)
            if len(data) > 64_000_000: raise ValueError("Recurso excessivamente grande: " + path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if mode == "120000":
                links.append((dest, data.decode())); continue
            with dest.open("xb") as stream: stream.write(data)
            dest.chmod(0o755 if mode == "100755" else 0o644)
        for dest, target in links:
            if not target or Path(target).is_absolute() or any(ord(c) < 32 for c in target) or not (dest.parent / target).resolve().is_relative_to(repo):
                raise ValueError("Link de origem inseguro: " + str(dest))
            dest.symlink_to(target)
        for dest, _ in links:
            if not dest.exists() or not dest.resolve().is_relative_to(repo): raise ValueError("Link de origem externo/quebrado: " + str(dest))
        # Índice sem checkout: não executar filtros, smudge, Git LFS ou hooks.
        self.run(repo, "update-index", "--skip-worktree", "-z", "--stdin", data="\0".join(paths) + "\0")
        if self.head(repo) != source["commit"] or self.run(repo, "status", "--porcelain").strip():
            raise ValueError("Aquisição não corresponde ao commit")


class Updates:
    def __init__(self, root, *, runtime, allow_local=False, validator=None):
        self.root = Path(root).absolute()
        # Reutiliza a defesa de ancestrais físicos do núcleo, sem modificar seu motor.
        sys.path.insert(0, str(self.root / "Automacao/project-bootstrap"))
        from stacknauta_core.filesystem import directory
        with directory(self.root): pass
        self.git = Git(allow_local); self.runtime = runtime
        self.validator = validator or self.validate

    def sources(self):
        lock = load(self.root, "Skills/fontes.lock.json")
        catalog = load(self.root, "Skills/catalogo.json")
        ids=[s["id"] for s in lock["sources"]]
        if not ids or len(set(ids))!=len(ids) or any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid) for sid in ids):
            raise ValueError("Registro de origens vazio ou com IDs duplicados/inválidos")
        if len(catalog['sources'])!=len(ids) or {s["id"]: (s["commit"], s["url"]) for s in lock["sources"]} != {s["id"]: (s["commit"], s["url"]) for s in catalog["sources"]}:
            raise ValueError("Catálogo e lock divergem")
        for source in lock["sources"]:
            if not re.fullmatch(r"[0-9a-f]{40}", source["commit"]): raise ValueError("Commit inválido no lock")
            if not source["directory"].startswith("Skills/_repos/"): raise ValueError("Cache fora do caminho permitido")
            safe(self.root, source["directory"])
        identities=[parse_url(s['url'],allow_local=self.git.allow_local)['identity'] for s in lock['sources']]
        if len(set(identities))!=len(identities) or len({s['directory'] for s in lock['sources']})!=len(ids):
            raise ValueError("Origens ou diretórios duplicados no registro")
        return lock["sources"]

    def check(self, selected=None):
        sources = [s for s in self.sources() if selected is None or s["id"] in selected]
        def query(source):
            row = {"origem": source["id"], "branch": source["branch"], "atual": source["commit"], "disponivel": None}
            if source.get('revision_type') in {'commit','tag'}:
                return {**row,'estado':'revisao_fixada','motivo':'Revisão explícita; sem consulta de atualização nem seguimento automático de branch'}
            try:
                commit, default = self.git.remote(source)
                row.update(disponivel=commit, default_branch=default, estado="sem_alteracoes" if commit == source["commit"] else "atualizacao_disponivel")
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                row.update(estado="erro_consulta", erro=str(exc))
            return row
        with ThreadPoolExecutor(max_workers=7) as pool: return list(pool.map(query, sources))

    def clean(self):
        if self.git.run(self.root, "status", "--porcelain", "--untracked-files=all").strip():
            raise ValueError("Git principal tem alterações locais; preserve/registre-as antes de atualizar")
        return self.git.head(self.root)

    def tracked(self):
        return {p: {"sha256": sha(read_bytes(self.root, p)), "mode": stat.S_IMODE(safe(self.root, p).stat().st_mode)}
                for p in self.git.run(self.root, "ls-files", "-z").split("\0") if p}

    def state_root(self):
        p = safe(self.root, ".stacknauta-updates"); p.mkdir(exist_ok=True); return p

    @contextlib.contextmanager
    def exclusive(self):
        p = self.state_root() / "lock"
        fd = os.open(p, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1: raise ValueError("Arquivo de exclusão mútua inseguro")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); yield
        finally: os.close(fd)

    def validate(self, root):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and not (k.startswith("ASDF_") and k.endswith("_VERSION"))}
        environment.update(PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        r = subprocess.run([sys.executable, "-I", "-S", "-B", str(root / "Skills/validacao/validar_biblioteca.py")],
                           cwd=Path.home(), capture_output=True, text=True, env=environment, timeout=90)
        if r.returncode: raise ValueError("Validação da biblioteca falhou: " + (r.stdout + r.stderr)[-4000:])
        data = json.loads(r.stdout)
        # Não usar --copias: esse modo executa buscas do fornecedor. Aqui somente
        # fechamento físico e referências pelos mesmos helpers do validador.
        from biblioteca import selected_files
        sys.path.insert(0, str(root / "Skills/validacao"))
        from validar_biblioteca import check_links
        cat = load(root, "Skills/catalogo.json")
        for desc in cat["distribution_packages"]:
            package = load(root, desc["directory"] + "/PROVENANCE.json")
            source = next(s for s in cat["sources"] if s["id"] == package["source_id"])
            if package["commit"] != source["commit"] or package["repository"] != source["url"]:
                raise ValueError("Commit/URL da proveniência diverge: " + package["id"])
            for identifier in package["skills"]:
                paths, _ = selected_files(identifier, cat, package)
                for p in paths: read_bytes(root, desc["directory"] + "/" + p)
                _, broken = check_links(root / desc["directory"], paths, set(paths))
                if broken: raise ValueError("Fechamento de recursos inválido: " + identifier + ":" + repr(broken[:3]))
        return {"status": data["status"], "arquivos": data["package_files_verified"], "fechamentos": cat["counts"]["approved_skills"], "codigo_fornecedor_executado": False}

    def check_changed_scripts(self, candidate, outputs, baseline):
        node = None
        for relative, data in outputs.items():
            if relative in baseline and sha(data) == baseline[relative]["sha256"]: continue
            suffix = Path(relative).suffix
            if suffix == '.py':
                before = read_bytes(self.root, relative) if relative in baseline else b''
                package = candidate.joinpath(*Path(relative).parts[:3])
                python_dependencies(before, data, {p.stem for p in package.rglob('*.py')})
                continue
            if suffix in {".ts", ".tsx", ".rb", ".ps1"}:
                raise ValueError("Script alterado exige validação manual específica: " + relative)
            if suffix not in {".js", ".cjs", ".mjs", ".sh"}: continue
            environment = {k: v for k, v in os.environ.items() if k not in {"NODE_OPTIONS", "NODE_PATH", "LD_PRELOAD", "LD_LIBRARY_PATH", "BASH_ENV", "ENV"}}
            if suffix == ".sh":
                environment["BASH_ENV"] = "/dev/null"
                command = ["bash", "-n", str(candidate / relative)]
            else:
                before = read_bytes(self.root, relative) if relative in baseline else b""
                for specifier in javascript_imports(data) - javascript_imports(before):
                    if specifier.removeprefix("node:") in NODE_BUILTINS: continue
                    if not specifier.startswith(("./", "../")):
                        raise ValueError("Nova dependência JavaScript exige revisão manual: " + specifier)
                    target = (candidate / relative).parent / specifier
                    parts = Path(relative).parts
                    # Recurso novo entre skills/pacotes altera o fechamento:
                    # não inferir aprovação dessa dependência por existir no repo.
                    scope = candidate.joinpath(*parts[:5] if len(parts) > 5 and parts[3] == "skills" else parts[:3])
                    choices = [target, *[Path(str(target) + ext) for ext in (".js", ".cjs", ".mjs", ".json")],
                               *[target / ("index" + ext) for ext in (".js", ".cjs", ".mjs")]]
                    if not any(p.resolve().is_relative_to(scope.resolve()) and p.suffix in {".js", ".cjs", ".mjs", ".json"} and p.is_file() and not p.is_symlink() for p in choices):
                        raise ValueError("Recurso JavaScript local ausente/externo: " + specifier)
                if node is None:
                    from stacknauta_core.runtimes import AsdfResolver
                    resolver = AsdfResolver(Path.home()); resolver.resolve([], extra_plugins=("nodejs",))
                    node = next(r["executable"] for r in resolver.diagnostics if r.get("command") == "node")
                command = [node, "--check", str(candidate / relative)]
            r = subprocess.run(command, cwd=Path.home(), env=environment, capture_output=True, text=True, timeout=20)
            if r.returncode: raise ValueError("Sintaxe de script inválida: " + relative + ": " + r.stderr[:1000])

    def begin(self):
        """Chamar sob exclusive; snapshot verificado de arquivos rastreados."""
        head = self.clean()
        self.validator(self.root)
        baseline = self.tracked(); session_id = uuid.uuid4().hex
        session = self.state_root() / session_id; session.mkdir()
        candidate = session / "candidate"
        self.copy_snapshot(candidate, baseline)
        return session, candidate, head, baseline

    def copy_snapshot(self, candidate, baseline):
        candidate.mkdir()
        for relative, record in baseline.items():
            source = safe(self.root, relative); dest = safe(candidate, relative)
            data = read_bytes(self.root, relative)
            if sha(data) != record["sha256"]: raise ValueError("Arquivo mudou durante preparação: " + relative)
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data); dest.chmod(record["mode"])

    def finish(self, session, candidate, head, baseline, checks, details, validation):
        """Sela plano e diff compartilhados por atualização e inclusão."""
        session_id = session.name
        new_tree = tree(candidate / "Skills")
        diffs = []
        review = []
        for path, record in sorted(new_tree.items()):
            relative = "Skills/" + path
            if baseline.get(relative) == record: continue
            before = read_bytes(self.root, relative) if relative in baseline else b""
            after = read_bytes(candidate, relative)
            diffs.append({"path": relative, "before": baseline.get(relative), "after": record})
            try:
                review.extend(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True),
                                                  fromfile="atual/" + relative, tofile="candidato/" + relative))
            except UnicodeError: review.append("Binário alterado: " + relative + "\n")
        identity = {"schema_version": 1, "head": head, "baseline": baseline, "candidate_tree": new_tree,
                    "origens": checks, "details": details, "files": diffs}
        plan = {**identity, "plan_id": sha(json_bytes(identity)), "session_id": session_id,
                "status": "preparado", "validacao": validation,
                "autorizacao": "Revisar plano e review.diff; apply exige --approve e hash revisado.",
                "atomicidade": "Global por troca da pasta Skills, com janela de indisponibilidade e rollback/backup; nunca mistura arquivos de revisões."}
        atomic_json(session / "plan.json", plan)
        (session / "review.diff").write_text("".join(review))
        atomic_json(session / "journal.json", {"phase": "prepared", "plan_id": plan["plan_id"]})
        return plan

    def prepare(self, selected):
        if not selected or not set(selected) <= {s['id'] for s in self.sources()}: raise ValueError("Origem desconhecida")
        head = self.clean(); checks = self.check(set(selected))
        if any(r["estado"] == "erro_consulta" for r in checks):
            return {"status": "bloqueado", "origens": checks, "motivo": "Consulta incompleta; nenhuma promoção possível"}
        changed = {r["origem"] for r in checks if r["estado"] == "atualizacao_disponivel"}
        if not changed: return {"status": "sem_alteracoes", "origens": checks}
        with self.exclusive():
            session, candidate, head, baseline = self.begin()
            session_id = session.name
            details = {}
            try:
                lock = load(candidate, "Skills/fontes.lock.json")
                for source in lock["sources"]:
                    if source["id"] not in changed: continue
                    available = next(r for r in checks if r["origem"] == source["id"])
                    source.update(commit=available["disponivel"], default_branch=available["default_branch"],
                                  acquisition="shallow-depth-1-no-checkout-manual-materialization")
                    self.git.acquire(source, safe(candidate, source["directory"]))
                (candidate / "Skills/fontes.lock.json").write_bytes(json_bytes(lock))
                outputs, details = refresh(candidate, changed, read_bytes, self.runtime, details, git_runner=self.git.run)
                for relative, data in outputs.items():
                    p = safe(candidate, relative); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); p.chmod(0o644)
                self.check_changed_scripts(candidate, outputs, baseline)
                validation = self.validator(candidate)
                acquired = candidate / "Skills/_repos"
                if acquired.exists(): os.rename(acquired, session / "acquired")
                return self.finish(session, candidate, head, baseline, checks, details, validation)
            except (ValueError, OSError, SyntaxError, BootstrapError, subprocess.SubprocessError) as exc:
                result = {"status": "bloqueado", "session_id": session_id, "origens": checks, "details": details, "promovidas": [], "motivo": str(exc)}
                atomic_json(session / "blocked.json", result); return result

    def session(self, identifier):
        if not re.fullmatch(r"[0-9a-f]{32}", identifier): raise ValueError("Sessão inválida")
        return safe(self.root, ".stacknauta-updates/" + identifier)

    def apply(self, identifier, plan_id, *, approve=False, hook=None):
        if not approve: raise ValueError("Aplicação exige autorização explícita --approve")
        with self.exclusive():
            session = self.session(identifier); plan = load(session, "plan.json")
            identity = {k: plan[k] for k in ("schema_version", "head", "baseline", "candidate_tree", "origens", "details", "files")}
            if sha(json_bytes(identity)) != plan_id or plan["plan_id"] != plan_id: raise ValueError("Hash diverge do plano revisado")
            journal = load(session, "journal.json")
            if journal["plan_id"] != plan_id: raise ValueError("Diário não corresponde ao plano")
            if journal["phase"] == "committed":
                if tree(self.root / "Skills") != plan["candidate_tree"]: raise ValueError("Biblioteca mudou após aplicação")
                return {"status": "ja_aplicado", "session_id": identifier, "plan_id": plan_id}
            if journal["phase"] != "prepared": raise ValueError("Sessão não está preparada; use recover e revise o estado")
            if self.clean() != plan["head"] or self.tracked() != plan["baseline"]: raise ValueError("Git/arquivos mudaram desde a preparação")
            candidate_root = safe(session, "candidate")
            expected = {p: r for p, r in plan["baseline"].items() if not p.startswith("Skills/")}
            expected.update({"Skills/" + p: r for p, r in plan["candidate_tree"].items()})
            # Também selar os módulos de validação/receita fora de Skills, antes
            # de iniciar qualquer Python na cópia isolada.
            if tree(candidate_root) != expected: raise ValueError("Candidato alterado após revisão")
            candidate = safe(candidate_root, "Skills")
            self.validator(session / "candidate")
            backup = session / "previous-Skills"
            if backup.exists(): raise ValueError("Backup preexistente; recuperação manual necessária")
            def phase(value): atomic_json(session / "journal.json", {"phase": value, "plan_id": plan_id})
            try:
                phase("moving_old"); move(safe(self.root, "Skills"), backup); phase("old_moved")
                if hook: hook("old_moved")
                move(candidate, self.root / "Skills"); phase("new_published")
                if hook: hook("new_published")
                self.validator(self.root); phase("committed")
                return {"status": "aplicado", "session_id": identifier, "plan_id": plan_id,
                        "origens": [{**r, "resultado": "atualizada" if r["estado"] == "atualizacao_disponivel" else "nao_modificada"} for r in plan["origens"]], "backup": str(backup)}
            except BaseException:
                self._recover(session, plan)
                raise

    def _recover(self, session, plan):
        backup = safe(session, "previous-Skills"); active = safe(self.root, "Skills")
        if backup.exists():
            expected = {p.removeprefix("Skills/"): r for p, r in plan["baseline"].items() if p.startswith("Skills/")}
            # Cache anterior pode estar presente; conferir todos os arquivos rastreados.
            for path, record in expected.items():
                if sha(read_bytes(backup, path)) != record["sha256"] or stat.S_IMODE(safe(backup, path).stat().st_mode) != record["mode"]: raise ValueError("Backup alterado; recuperação manual necessária")
            if active.exists():
                if tree(active) != plan["candidate_tree"]: raise ValueError("Destino mudou; recuperação manual necessária, nada sobrescrito")
                failed = session / ("failed-Skills-" + uuid.uuid4().hex); move(active, failed)
            move(backup, active)
        else:
            for path, record in plan["baseline"].items():
                if path.startswith("Skills/") and (sha(read_bytes(self.root, path)) != record["sha256"] or stat.S_IMODE(safe(self.root, path).stat().st_mode) != record["mode"]):
                    raise ValueError("Estado ambíguo sem backup; recuperação manual necessária")
        atomic_json(session / "journal.json", {"phase": "rolled_back", "plan_id": plan["plan_id"]})

    def recover(self, identifier, *, approve=False):
        if not approve: raise ValueError("Recuperação exige --approve")
        with self.exclusive():
            session = self.session(identifier); plan = load(session, "plan.json")
            identity = {k: plan[k] for k in ("schema_version", "head", "baseline", "candidate_tree", "origens", "details", "files")}
            if sha(json_bytes(identity)) != plan["plan_id"]: raise ValueError("Plano de recuperação adulterado")
            journal = load(session, "journal.json"); phase = journal["phase"]
            if journal["plan_id"] != plan["plan_id"]: raise ValueError("Diário não corresponde ao plano")
            if phase == "committed": raise ValueError("Atualização concluída; reversão deliberada exige revisão separada")
            self._recover(session, plan)
            return {"status": "restaurado", "session_id": identifier}
