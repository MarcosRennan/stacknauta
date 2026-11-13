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
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Automacao/project-bootstrap"))
from stacknauta_core.core import encoded as json_bytes
from stacknauta_core.library import digest as sha
from stacknauta_core import BootstrapError
from stacknauta_core.filesystem import directory, relative_directory, rename_noreplace, DIR_FLAGS, READ_FLAGS
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
    if not relative or not p.parts or p.is_absolute() or str(p) != relative or any(x in {"..", ".git"} for x in p.parts) or "\\" in relative or any(ord(c) < 32 for c in relative):
        raise ValueError("Caminho inseguro: " + repr(relative))
    path = root
    for part in p.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Link simbólico indevido: " + relative)
    return path


def regular(info, name):
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 64_000_000:
        raise ValueError('Arquivo não regular, hardlink ou tamanho excessivo: ' + str(name))


def same_entry(parent, name, info):
    current = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
        raise ValueError('Arquivo substituído durante operação: ' + str(name))
    if stat.S_ISREG(info.st_mode): regular(current, name)


def _read_record(parent, name):
    fd = os.open(name, READ_FLAGS, dir_fd=parent)
    try:
        start = os.fstat(fd); regular(start, name)
        chunks, length = [], 0
        while chunk := os.read(fd, min(65536, 64_000_001 - length)):
            chunks.append(chunk); length += len(chunk)
            if length > 64_000_000: raise ValueError('Arquivo excede limite: ' + name)
        end = os.fstat(fd); regular(end, name)
        if (start.st_size, start.st_mtime_ns, start.st_ctime_ns) != (end.st_size, end.st_mtime_ns, end.st_ctime_ns) or length != end.st_size:
            raise ValueError('Arquivo mudou durante leitura: ' + name)
        same_entry(parent, name, end)
        data = b''.join(chunks)
        return data, {'sha256': sha(data), 'mode': stat.S_IMODE(end.st_mode)}
    finally: os.close(fd)


def read_record(root, relative):
    safe(root, relative)
    components = PurePosixPath(relative).parts
    with directory(root) as root_fd, relative_directory(root_fd, components[:-1]) as parent:
        return _read_record(parent, components[-1])


def read_bytes(root, relative):
    return read_record(root, relative)[0]


def _write_fd(fd, data, mode):
    if len(data) > 64_000_000: raise ValueError('Dados excedem limite de arquivo')
    os.ftruncate(fd, 0)
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written <= 0: raise OSError('Escrita incompleta')
        view = view[written:]
    os.fchmod(fd, mode)


def write_bytes(root, relative, data, mode=0o644, *, exclusive=False):
    safe(root, relative)
    components = PurePosixPath(relative).parts
    with directory(root) as root_fd, relative_directory(root_fd, components[:-1], create=True) as parent:
        flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
        fd = os.open(components[-1], flags | (os.O_EXCL if exclusive else 0), 0o600, dir_fd=parent)
        try:
            info = os.fstat(fd); regular(info, relative)
            same_entry(parent, components[-1], info)
            _write_fd(fd, data, mode)
            regular(os.fstat(fd), relative)
            same_entry(parent, components[-1], info)
        finally: os.close(fd)


def make_directory(root, relative, *, exclusive=False):
    safe(root, relative)
    components = PurePosixPath(relative).parts
    with directory(root) as root_fd, relative_directory(root_fd, components[:-1], create=True) as parent:
        if exclusive: os.mkdir(components[-1], 0o755, dir_fd=parent)
        with relative_directory(parent, components[-1:], create=not exclusive) as fd: os.fsync(fd)
        os.fsync(parent)
        os.fsync(root_fd)


def load(root, relative):
    return json.loads(read_bytes(root, relative))


def tree(root, *, exclude=()):
    result = {}
    def visit(fd, prefix='', depth=0):
        if depth > 128: raise ValueError('Árvore excede profundidade segura')
        for name in sorted(os.listdir(fd)):
            if not prefix and name in exclude: continue
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name, DIR_FLAGS, dir_fd=fd)
                try:
                    same_entry(fd, name, os.fstat(child))
                    visit(child, prefix + name + '/', depth + 1)
                finally: os.close(child)
            else:
                if not stat.S_ISREG(info.st_mode): raise ValueError('Link/arquivo especial no candidato: ' + prefix + name)
                result[prefix + name] = _read_record(fd, name)[1]
    with directory(root) as root_fd: visit(root_fd)
    return result


def atomic_json(path, data):
    temporary = path.name + '.tmp-' + uuid.uuid4().hex
    with directory(path.parent) as parent:
        try: _read_record(parent, path.name)
        except FileNotFoundError: pass
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        info = os.fstat(fd)
        try:
            _write_fd(fd, json_bytes(data), 0o600); os.fsync(fd)
            same_entry(parent, temporary, info)
            os.replace(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent)
            same_entry(parent, path.name, info)
            os.fsync(parent)
        finally:
            os.close(fd)
            try:
                same_entry(parent, temporary, info)
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError: pass


def move(source, destination):
    with directory(source.parent) as src, directory(destination.parent) as dst, directory(source) as opened:
        info = os.fstat(opened)
        same_entry(src, source.name, info)
        try:
            rename_noreplace(source.name, destination.name, src_dir_fd=src, dst_dir_fd=dst)
        except FileExistsError as exc:
            raise ValueError('Destino de publicação já existe: ' + str(destination)) from exc
        same_entry(dst, destination.name, info)
        os.fsync(src); os.fsync(dst)


def sync_tree(root, expected=None):
    """Confere e sincroniza arquivos conhecidos, depois diretórios de baixo para cima.

    expected permite preservar o cache antigo sem certificá-lo como distribuível.
    Qualquer falha impede o avanço do diário; não implica atomicidade global.
    """
    records = tree(root) if expected is None else expected
    directories = {()}
    with directory(root) as root_fd:
        for path, record in sorted(records.items()):
            components = PurePosixPath(path).parts
            safe(root, path)
            for length in range(1, len(components)):
                directories.add(components[:length])
            with relative_directory(root_fd, components[:-1]) as parent:
                fd = os.open(components[-1], READ_FLAGS, dir_fd=parent)
                try:
                    info = os.fstat(fd)
                    regular(info, path)
                    digest = hashlib.sha256()
                    length = 0
                    while chunk := os.read(fd, min(65536, 64_000_001 - length)):
                        length += len(chunk); digest.update(chunk)
                        if length > 64_000_000: raise ValueError('Arquivo excede limite: ' + path)
                    end = os.fstat(fd); regular(end, path)
                    if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (end.st_size, end.st_mtime_ns, end.st_ctime_ns) or length != end.st_size:
                        raise ValueError('Arquivo mudou durante sincronização: ' + path)
                    if {'sha256': digest.hexdigest(), 'mode': stat.S_IMODE(info.st_mode)} != record:
                        raise ValueError('Arquivo mudou antes da sincronização: ' + path)
                    os.fsync(fd)
                    same_entry(parent, components[-1], info)
                finally: os.close(fd)
        for components in sorted(directories, key=lambda p: (-len(p), p)):
            with relative_directory(root_fd, components) as fd: os.fsync(fd)


def check_javascript(candidate, relative, node, environment):
    """Node decide o formato por extensão/contexto, somente em bytes isolados.

    A cópia privada evita reabrir caminhos do fornecedor. O package.json vazio
    na raiz sintética delimita o escopo sem herdar configuração externa ao candidato.
    """
    data = read_bytes(candidate, relative)
    context = None
    for parent in PurePosixPath(relative).parents:
        if parent.name == 'node_modules': break
        package_path = (parent / 'package.json').as_posix()
        try: raw = read_bytes(candidate, package_path)
        except FileNotFoundError: continue
        except (OSError, ValueError, BootstrapError) as exc:
            raise ValueError('Contexto JavaScript não verificável: ' + package_path + ': ' + str(exc)) from exc
        try:
            if not isinstance(json.loads(raw), dict): raise ValueError('objeto JSON esperado')
        except (ValueError, UnicodeError) as exc:
            raise ValueError('Contexto JavaScript inválido: ' + package_path + ': ' + str(exc)) from exc
        context = (package_path, raw)
        break
    with tempfile.TemporaryDirectory(prefix='stacknauta-js-check-') as temporary:
        isolated = Path(temporary)
        write_bytes(isolated, 'package.json', context[1] if context and context[0] == 'package.json' else b'{}', exclusive=True)
        if context and context[0] != 'package.json': write_bytes(isolated, *context, exclusive=True)
        write_bytes(isolated, relative, data, exclusive=True)
        with directory(isolated) as fd:
            result = subprocess.run([node, '--check', f'/proc/self/fd/{fd}/{relative}'],
                cwd=isolated, env=environment, pass_fds=(fd,), capture_output=True, text=True, timeout=20)
        if result.returncode:
            label = 'Sintaxe de script inválida' if 'SyntaxError' in result.stderr and 'ERR_INVALID_PACKAGE_CONFIG' not in result.stderr else 'Validação JavaScript inconclusiva'
            raise ValueError(label + ': ' + relative + ': ' + result.stderr[:1000])


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
                   "-c", "http.lowSpeedLimit=100", "-c", "http.lowSpeedTime=15"]
        with directory(Path(repo).absolute()) as repo_fd:
            command += ['-C', f'/proc/self/fd/{repo_fd}', *args]
            r = subprocess.run(command, input=data, capture_output=True, text=not binary, env=environment, timeout=45, pass_fds=(repo_fd,))
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
        with directory(repo.parent.parent) as root_fd, relative_directory(root_fd, (repo.parent.name, repo.name), create=True): pass
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
            if mode == "120000":
                links.append((dest, data.decode())); continue
            write_bytes(repo, path, data, 0o755 if mode == '100755' else 0o644, exclusive=True)
        for dest, target in links:
            if not target or Path(target).is_absolute() or any(ord(c) < 32 for c in target) or not (dest.parent / target).resolve().is_relative_to(repo):
                raise ValueError("Link de origem inseguro: " + str(dest))
            with directory(repo) as root_fd, relative_directory(root_fd, dest.relative_to(repo).parts[:-1], create=True) as parent:
                os.symlink(target, dest.name, dir_fd=parent)
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
        return {p: read_record(self.root, p)[1]
                for p in self.git.run(self.root, "ls-files", "-z").split("\0") if p}

    def state_root(self):
        p = safe(self.root, ".stacknauta-updates")
        make_directory(self.root, '.stacknauta-updates')
        return p

    @contextlib.contextmanager
    def exclusive(self):
        with directory(self.state_root()) as parent:
            fd = os.open('lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, 0o600, dir_fd=parent)
            try:
                regular(os.fstat(fd), 'lock')
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); yield
            finally: os.close(fd)

    def validate(self, root):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and not (k.startswith("ASDF_") and k.endswith("_VERSION"))}
        environment.update(PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        with directory(root) as root_fd, relative_directory(root_fd, ('Skills', 'validacao')) as parent:
            script = os.open('validar_biblioteca.py', READ_FLAGS, dir_fd=parent)
            try:
                regular(os.fstat(script), 'validar_biblioteca.py')
                r = subprocess.run([sys.executable, '-I', '-S', '-B', f'/proc/self/fd/{script}'],
                    cwd=Path.home(), capture_output=True, text=True, env=environment, timeout=90, pass_fds=(script,))
            finally: os.close(script)
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
            suffix = Path(relative).suffix
            # package.json pode mudar a interpretação de um script intacto.
            if relative in baseline and sha(data) == baseline[relative]['sha256'] and suffix not in {'.js','.cjs','.mjs'}: continue
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
                command = ["bash", "-n"]
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
                    found = False
                    for choice in choices:
                        normalized = Path(os.path.normpath(choice))
                        if not normalized.is_relative_to(scope) or normalized.suffix not in {'.js', '.cjs', '.mjs', '.json'}: continue
                        try: read_bytes(candidate, normalized.relative_to(candidate).as_posix())
                        except FileNotFoundError: continue
                        found = True; break
                    if not found:
                        raise ValueError("Recurso JavaScript local ausente/externo: " + specifier)
                if node is None:
                    from stacknauta_core.runtimes import AsdfResolver
                    resolver = AsdfResolver(Path.home()); resolver.resolve([], extra_plugins=("nodejs",))
                    node = next(r["executable"] for r in resolver.diagnostics if r.get("command") == "node")
                check_javascript(candidate, relative, node, environment)
                continue
            r = subprocess.run(command, input=read_bytes(candidate, relative).decode(), cwd=Path.home(), env=environment, capture_output=True, text=True, timeout=20)
            if r.returncode: raise ValueError("Sintaxe de script inválida: " + relative + ": " + r.stderr[:1000])

    def begin(self):
        """Chamar sob exclusive; snapshot verificado de arquivos rastreados."""
        head = self.clean()
        self.validator(self.root)
        baseline = self.tracked(); session_id = uuid.uuid4().hex
        session = self.state_root() / session_id
        make_directory(session.parent, session_id, exclusive=True)
        candidate = session / "candidate"
        self.copy_snapshot(candidate, baseline)
        return session, candidate, head, baseline

    def copy_snapshot(self, candidate, baseline):
        make_directory(candidate.parent, candidate.name, exclusive=True)
        for relative, record in baseline.items():
            data = read_bytes(self.root, relative)
            if sha(data) != record["sha256"]: raise ValueError("Arquivo mudou durante preparação: " + relative)
            write_bytes(candidate, relative, data, record['mode'], exclusive=True)

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
                "atomicidade": "Troca de Skills por renames persistidos; sem atomicidade global entre renames e diário, com janela de indisponibilidade e rollback/backup."}
        sync_tree(candidate)
        atomic_json(session / "plan.json", plan)
        write_bytes(session, 'review.diff', ''.join(review).encode(), exclusive=True)
        sync_tree(session, {'review.diff': read_record(session, 'review.diff')[1]})
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
                write_bytes(candidate, 'Skills/fontes.lock.json', json_bytes(lock))
                outputs, details = refresh(candidate, changed, read_bytes, self.runtime, details, git_runner=self.git.run)
                for relative, data in outputs.items():
                    write_bytes(candidate, relative, data)
                self.check_changed_scripts(candidate, outputs, baseline)
                validation = self.validator(candidate)
                acquired = candidate / "Skills/_repos"
                if acquired.exists(): move(acquired, session / 'acquired')
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
                sync_tree(self.root / 'Skills', plan['candidate_tree'])
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
            sync_tree(candidate_root, expected)
            previous = {p.removeprefix('Skills/'): r for p,r in plan['baseline'].items() if p.startswith('Skills/')}
            sync_tree(self.root / 'Skills', previous)
            backup = session / "previous-Skills"
            if backup.exists(): raise ValueError("Backup preexistente; recuperação manual necessária")
            def phase(value): atomic_json(session / "journal.json", {"phase": value, "plan_id": plan_id})
            try:
                phase("moving_old"); move(safe(self.root, "Skills"), backup); phase("old_moved")
                if hook: hook("old_moved")
                move(candidate, self.root / "Skills"); phase("new_published")
                if hook: hook("new_published")
                self.validator(self.root)
                if tree(self.root / 'Skills') != plan['candidate_tree']:
                    raise ValueError('Biblioteca mudou após promoção; conclusão recusada')
                sync_tree(self.root / 'Skills', plan['candidate_tree'])
                phase("committed")
                return {"status": "aplicado", "session_id": identifier, "plan_id": plan_id,
                        "origens": [{**r, "resultado": ({"inclusao_revisada": "incluida",
                            "atualizacao_disponivel": "atualizada"}.get(r["estado"], "modificada")
                            if plan["files"] and r["estado"] != "sem_alteracoes" else "nao_modificada")}
                            for r in plan["origens"]], "backup": str(backup)}
            except BaseException as exc:
                # Mantém os tipos de exceção da API; a CLI distingue falha de
                # promoção de uma recusa anterior às escritas (hash/aprovação).
                exc.stacknauta_status = 'falha_aplicacao'
                try:
                    self._recover(session, plan)
                except BaseException as recovery_error:
                    recovery_error.stacknauta_status = 'falha_aplicacao'
                    raise
                atomic_json(session / 'application-failed.json', {'status': 'falha_aplicacao',
                    'session_id': identifier, 'plan_id': plan_id, 'motivo': str(exc),
                    'recuperacao': 'rolled_back', 'promovidas': []})
                raise

    def _recover(self, session, plan):
        journal = load(session, 'journal.json')
        if journal.get('plan_id') != plan['plan_id'] or journal.get('phase') not in {
            'prepared', 'moving_old', 'old_moved', 'new_published', 'committed', 'rolled_back'}:
            raise ValueError('Diário inconsistente; recuperação manual necessária')
        backup = safe(session, "previous-Skills"); active = safe(self.root, "Skills")
        expected = {p.removeprefix("Skills/"): r for p, r in plan["baseline"].items() if p.startswith("Skills/")}
        if backup.exists():
            # Cache anterior é preservado sem consulta; o restante precisa ser exato.
            if tree(backup, exclude=('_repos',)) != expected:
                raise ValueError('Backup alterado; recuperação manual necessária')
            sync_tree(backup, expected)
            if active.exists():
                if tree(active) != plan["candidate_tree"]: raise ValueError("Destino mudou; recuperação manual necessária, nada sobrescrito")
                failed = session / ("failed-Skills-" + uuid.uuid4().hex); move(active, failed)
            move(backup, active)
        else:
            try: observed = tree(active, exclude=('_repos',))
            except FileNotFoundError as exc:
                raise ValueError('Estado ambíguo sem backup e biblioteca ativa; recuperação manual necessária') from exc
            if observed != expected:
                raise ValueError('Estado ambíguo sem backup; recuperação manual necessária')
        sync_tree(active, expected)
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
