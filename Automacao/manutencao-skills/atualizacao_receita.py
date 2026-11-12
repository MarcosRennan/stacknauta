"""Refresh incremental do layout aprovado, reutilizando inventário e adaptações.

Não executa fornecedores nem reconstrói pacotes de origens não selecionadas.
Mudanças sem correspondência exata com o contrato anterior bloqueiam a promoção.
"""
import ast
import copy
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path



def replay_patch(data, patch):
    text = data.decode()
    hunks = re.split(r"^@@[^\n]*\n", patch, flags=re.M)[1:]
    if not hunks:
        raise ValueError("Adaptação sem hunks; revisão manual necessária")
    for hunk in hunks:
        rows = hunk.splitlines(keepends=True)
        if any(row[:1] not in {" ", "+", "-"} for row in rows):
            raise ValueError("Formato de adaptação não suportado; revisão manual necessária")
        before = "".join(row[1:] for row in rows if row.startswith((" ", "-")))
        after = "".join(row[1:] for row in rows if row.startswith((" ", "+")))
        if not before or text.count(before) != 1:
            raise ValueError("Contexto de adaptação mudou ou é ambíguo; revisão manual necessária")
        text = text.replace(before, after, 1)
    return text.encode()


def skill_prefix(source_path):
    parent = Path(source_path).parent.as_posix()
    return "" if parent == "." else parent + "/"


def source_bytes(root, source, records, path, read_bytes):
    from biblioteca import sha
    row = records.get(path)
    if not row or row['type'] != 'file': raise ValueError('Recurso ausente/não regular: '+path)
    data = read_bytes(root, source['directory']+'/'+path)
    if sha(data) != row['sha256']: raise ValueError('Hash incompatível com a aquisição: '+path)
    if __import__('hashlib').sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != row['git_blob']:
        raise ValueError('Blob Git incompatível: '+path)
    return data


def python_dependencies(before, after, local_modules):
    def imports(data):
        return {name for node in ast.walk(ast.parse(data)) for name in
                ([a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else
                 [node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module else [])}
    added = imports(after) - imports(before) - set(sys.stdlib_module_names) - set(local_modules)
    if added: raise ValueError('Nova dependência Python não atendida; revisão manual: '+', '.join(sorted(added)))


def relative_python_resources(data, path, files, read_module):
    """Resolve caminhos relativos sem executar código; exports dinâmicos exigem revisão."""
    tree = ast.parse(data)
    available = set(files)
    required = set()
    directories = {str(parent) for p in available for parent in Path(p).parents}

    def module(base):
        # Um pacote regular tem precedência sobre um módulo homônimo.
        if base + '/__init__.py' in available:
            return {base + '/__init__.py'}
        if base + '.py' in available:
            return {base + '.py'}
        if base in directories:
            return {p for p in available if p.startswith(base + '/') and p.endswith('.py')} or None
        return None

    def explicit_export(init, name):
        if init not in available:
            return False
        for node in ast.parse(read_module(init)).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                return True
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.level and node.module is None:
                    parent = Path(init).parent
                    if node.level <= len(parent.parts) + int('__init__.py' in available):
                        for _ in range(node.level - 1):
                            parent = parent.parent
                        if any((a.asname or a.name) == name and module((parent / a.name).as_posix()) is not None for a in node.names):
                            return True
                    continue  # O próprio import não prova que seu alvo existe.
                if any((a.asname or (a.name.split('.')[0] if isinstance(node, ast.Import) else a.name)) == name for a in node.names):
                    return True
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) and node.value is not None else []
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                return True
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        parent = Path(path).parent
        if node.level > len(parent.parts) + int('__init__.py' in available):
            raise ValueError('Dependência local relativa fora do pacote: ' + path)
        for _ in range(node.level - 1):
            parent = parent.parent
        names = [node.module] if node.module else [a.name for a in node.names]
        for name in names:
            base = parent.as_posix()
            components = name.split('.')
            resolved = None
            for index, component in enumerate(components):
                base = (Path(base) / component).as_posix()
                resolved = module(base)
                if resolved is None or (index < len(components)-1 and base + '/__init__.py' not in available and base + '.py' in available):
                    resolved = None
                    break
            init = (parent / '__init__.py').as_posix()
            if resolved is None:
                if node.module is None and ((name == '*' and init in available) or explicit_export(init, name)):
                    resolved = {init}
                else:
                    raise ValueError('Dependência local Python ausente/ambígua; revisão manual: ' + base)
            required.update(resolved)
            if node.module and (base + '/__init__.py' in available or base + '.py' not in available):
                for alias in node.names:
                    required.update(module(base + '/' + alias.name) or set())
            for ancestor in Path(base).parents:
                init_path = (ancestor / '__init__.py').as_posix()
                if init_path in available:
                    required.add(init_path)
    return required


def javascript_imports(data):
    groups = re.findall(r'''\b(?:require|import)\s*\(\s*["']([^"']+)["']|\bfrom\s*["']([^"']+)["']|\bimport\s*["']([^"']+)["']''', data.decode(errors='replace'))
    return {s for group in groups for s in group if s}


def category_indexes(cat, categories):
    from biblioteca import DOMAINS
    outputs={}
    for category in set(DOMAINS) & set(categories):
        lines=['# '+category,'','Biblioteca versionada; atualizações manuais. Nenhuma skill ativada.','',
               '| Skill | Status | Pacote ou impedimento |','|---|---|---|']
        for skill in cat['skills']:
            if skill['category']!=category: continue
            dist=skill['distribution'];name=skill['name']
            if dist: name=f"[{name}]({dist['package'].split('/',1)[1]}/{dist['skill_directory']}/SKILL.md)"
            lines.append(f"| {name} | {skill['distribution_status']} | {dist['package'] if dist else skill['decision_reason']} |")
        outputs['Skills/'+category+'/README.md']=('\n'.join(lines)+'\n').encode()
    return outputs


def recount(cat):
    counts = cat["counts"]
    counts.update(sources=len(cat["sources"]), catalogued_skills=len(cat["skills"]),
                  physical_skill_files=sum(s["physical_skill_files"] for s in cat["sources"]),
                  distribution_aliases=len(cat["distribution_aliases"]), distribution_packages=len(cat["distribution_packages"]),
                  by_category=dict(sorted(Counter(s["category"] for s in cat["skills"] if s["category"] is not None).items())),
                  by_scope=dict(sorted(Counter(s["scope"] for s in cat["skills"]).items())),
                  approved_by_category=dict(sorted(Counter(s["category"] for s in cat["skills"] if s["distribution_status"]=="approved").items())))
    unclassified = sum(s["category"] is None for s in cat["skills"])
    if unclassified: counts["unclassified_skills"] = unclassified
    else: counts.pop("unclassified_skills", None)
    for state in ("approved", "pending", "excluded"):
        counts[state+"_skills"] = sum(s["distribution_status"] == state for s in cat["skills"])
    counts["prepared_distribution_skills"] = counts["approved_skills"]


def inventory(root, source_ids, read_bytes, runtime, git_runner):
    from biblioteca import json_bytes
    import inventariar
    lock = json.loads(read_bytes(root, "Skills/fontes.lock.json"))
    # O inventário existente já aceita a lista de origens do lock. Só o lock da
    # cópia isolada é temporariamente filtrado; o ativo nunca é alterado aqui.
    full_lock = (root / "Skills/fontes.lock.json").read_bytes()
    (root / "Skills/fontes.lock.json").write_bytes(json_bytes({**lock, "sources": [s for s in lock["sources"] if s["id"] in source_ids]}))
    previous_root, previous_runtime, previous_git = inventariar.ROOT, inventariar.require_asdf_python, inventariar.git
    try:
        inventariar.ROOT = root
        inventariar.require_asdf_python = lambda: runtime
        inventariar.git = lambda repo, *args: git_runner(repo, *args).strip()
        raw, fresh_indexes, fresh_refs = inventariar.build()
    finally:
        inventariar.ROOT, inventariar.require_asdf_python, inventariar.git = previous_root, previous_runtime, previous_git
        (root / "Skills/fontes.lock.json").write_bytes(full_lock)
    return raw, fresh_indexes, fresh_refs


def refresh(root, source_ids, read_bytes, runtime, details=None, *, git_runner):
    """root é exclusivamente uma cópia isolada. read_bytes recusa links/hardlinks."""
    from biblioteca import json_bytes, sha
    import inventariar
    details = details if details is not None else {}
    cat = json.loads(read_bytes(root, "Skills/catalogo.json"))
    lock = json.loads(read_bytes(root, "Skills/fontes.lock.json"))
    policy = json.loads(read_bytes(root, "Skills/manutencao/distribuicao-politica.json"))
    indexes = json.loads(read_bytes(root, "Skills/validacao/arquivos.json"))
    references = json.loads(read_bytes(root, "Skills/validacao/recursos.json"))
    patches = json.loads(read_bytes(root, "Skills/validacao/adaptacoes.json"))
    old_skills = {s["id"]: s for s in cat["skills"]}
    old_sources = {s["id"]: s for s in cat["sources"]}
    full_lock = read_bytes(root, "Skills/fontes.lock.json")
    raw, fresh_indexes, fresh_refs = inventory(root, source_ids, read_bytes, runtime, git_runner)
    details["new_skill_paths_outside_scope"] = {
        sid: sorted(p for p in set(fresh_indexes[sid]["sparse_omitted_paths"]) - set(indexes[sid]["sparse_omitted_paths"])
                    if Path(p).name == "SKILL.md") for sid in source_ids
    }
    if any(details["new_skill_paths_outside_scope"].values()):
        raise ValueError("Novas skills fora do escopo de aquisição esparsa; análise e aquisição de recursos pendentes")
    new_skills = {s["id"]: s for s in raw["skills"]}
    if len(new_skills) != len(raw["skills"]): raise ValueError("IDs de skills duplicados na origem; revisão manual necessária")
    old_selected = {k for k, v in old_skills.items() if v["source_id"] in source_ids}
    details["new_skills_pending"] = sorted(set(new_skills) - old_selected)
    for identifier in details["new_skills_pending"]:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", new_skills[identifier]["name"]) or len(new_skills[identifier]["name"]) > 64:
            raise ValueError("Nome de nova skill inválido; revisão manual: " + identifier)
    removed = old_selected - set(new_skills)
    if removed:
        raise ValueError("Skills removidas/renomeadas exigem revisão manual: " + ", ".join(sorted(removed)))
    discovered = sorted(set(new_skills) - old_selected)
    for identifier in old_selected:
        old, new = old_skills[identifier], new_skills[identifier]
        if old["source_path"] != new["source_path"]:
            raise ValueError("Skill movida exige revisão manual: " + identifier)
        if old["distribution_status"] == "approved":
            if old["license"] != new["license"] or new["license"]["identified"].startswith(("unknown", "unidentified")):
                raise ValueError("Licença alterada/não identificada: " + identifier)
            before = {d["text"] for d in old["dependency_evidence"]}
            if {d["text"] for d in new["dependency_evidence"]} - before:
                raise ValueError("Novo pré-requisito exige revisão manual: " + identifier)
            closure = set(__import__("biblioteca").closure_for(identifier, old_skills))
            if set(new["sibling_skill_mentions"]) - set(old["sibling_skill_mentions"]) - closure:
                raise ValueError("Nova dependência entre skills exige revisão manual: " + identifier)
            added_resources = set(new["required_files"]) - set(old["required_files"])
            for other in new_skills.values():
                if other["id"] in closure: continue
                prefix = str(Path(other["source_path"]).parent) + "/"
                if any(p.startswith(prefix) for p in added_resources):
                    raise ValueError("Novo recurso de outra skill exige revisão de dependência: " + identifier)
    # Não distribuir uma nova skill escondida dentro de um diretório aprovado.
    for identifier in discovered:
        for existing in old_selected:
            old = old_skills[existing]
            if old["distribution_status"] == "approved" and new_skills[identifier]["source_path"].startswith(str(Path(old["source_path"]).parent) + "/"):
                raise ValueError("Nova skill aninhada em pacote aprovado exige revisão manual: " + identifier)
    fresh_records = {s: {r["path"]: r for r in idx["files"]} for s, idx in fresh_indexes.items()}
    old_records = {s: {r["path"]: r for r in indexes[s]["files"]} for s in source_ids}
    source_changes = {}
    for sid in source_ids:
        before, after = old_records[sid], fresh_records[sid]
        source_changes[sid] = [{"path": p, "before": before.get(p), "after": after.get(p)}
                               for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    if "ui-ux-pro-max" in source_ids:
        for change in source_changes["ui-ux-pro-max"]:
            p = change["path"]
            if p.startswith(("src/ui-ux-pro-max/templates/", "cli/src/")) or p == old_skills["ui-ux-pro-max:ui-ux-pro-max"]["source_path"]:
                raise ValueError("Distribuição/renderização UI/UX mudou; revisão manual necessária: " + p)
    patch_index = {(p["package"], p["path"]): p for p in patches}
    outputs, affected_packages, replacement_patches = {}, [], []

    def source_data(sid, path):
        source = next(s for s in lock["sources"] if s["id"] == sid)
        return source_bytes(root, source, fresh_records[sid], path, read_bytes)

    # O inventário também registra pendentes: validar todos os blobs materiais,
    # não só os recursos que serão distribuídos. skip-worktree não prova bytes.
    for sid in source_ids:
        for path, record in fresh_records[sid].items():
            if record["type"] == "file": source_data(sid, path)

    for descriptor in cat["distribution_packages"]:
        package = json.loads(read_bytes(root, descriptor["directory"] + "/PROVENANCE.json"))
        sid = package["source_id"]
        if sid not in source_ids:
            continue
        affected_packages.append(package["id"])
        new_commit = next(s["commit"] for s in lock["sources"] if s["id"] == sid)
        for relative, record in list(package["files"].items()):
            dest = package["directory"] + "/" + relative
            original = read_bytes(root, dest)
            inputs = record["inputs"]
            changed = any(fresh_records[sid].get(i["path"], {}).get("sha256") != i["sha256"] for i in inputs)
            if not inputs:
                if relative != "README.md":
                    raise ValueError("Artefato gerado sem receita incremental: " + dest)
                data = original.replace(package["commit"].encode(), new_commit.encode())
            elif len(inputs) > 1:
                if changed:
                    raise ValueError("Recurso renderizado mudou; revisão manual necessária: " + dest)
                data = original
            else:
                raw_data = source_data(sid, inputs[0]["path"])
                old_patch = patch_index.get((package["id"], relative))
                data = original if not changed else replay_patch(raw_data, old_patch["diff"]) if old_patch else raw_data
                if old_patch:
                    if old_patch["before_sha256"] != inputs[0]["sha256"]:
                        raise ValueError("Base de adaptação não corresponde à proveniência: " + dest)
                    replacement_patches.append({**old_patch, "before_sha256": sha(raw_data), "after_sha256": sha(data),
                        "diff": "".join(difflib.unified_diff(raw_data.decode().splitlines(True), data.decode().splitlines(True), fromfile="upstream", tofile="distribution"))})
            if len(inputs) > 1:
                replacement_patches.append(patch_index[(package["id"], relative)])
            record.update(sha256=sha(data), size=len(data), inputs=[{"path": i["path"], "sha256": fresh_records[sid][i["path"]]["sha256"]} for i in inputs])
            outputs[dest] = data
        # Novos recursos dentro das skills aprovadas: cópia integral e física.
        for identifier in package["skills"]:
            skill = old_skills[identifier]
            source_prefix = skill_prefix(skill["source_path"])
            mappings = [(source_prefix, skill["distribution"]["skill_directory"] + "/")]
            if identifier == "ui-ux-pro-max:ui-ux-pro-max":
                mappings += [("src/ui-ux-pro-max/" + p + "/", skill["distribution"]["skill_directory"] + "/" + p + "/") for p in ("scripts", "data")]
            for prefix, target in mappings:
                for path, row in fresh_records[sid].items():
                    if not path.startswith(prefix):
                        continue
                    if identifier == "ui-ux-pro-max:ui-ux-pro-max" and prefix == source_prefix and path[len(prefix):].startswith(("scripts/", "data/")):
                        source_data(sid, "src/ui-ux-pro-max/" + path[len(prefix):])
                        continue
                    rel = target + path[len(prefix):]
                    if rel in package["files"]:
                        continue
                    if Path(rel).name == "SKILL.md":
                        raise ValueError("SKILL.md adicional não aprovado: " + path)
                    data = source_data(sid, path)
                    package["files"][rel] = {"sha256": sha(data), "size": len(data), "mode": "100644",
                        "inputs": [{"path": path, "sha256": sha(data)}], "adaptation": None, "origin": "vendor"}
                    outputs[package["directory"] + "/" + rel] = data
        local_modules = {Path(p).stem for p in package["files"] if p.endswith(".py")}
        for relative in package["files"]:
            if not relative.endswith(".py"): continue
            dest = package["directory"] + "/" + relative
            before_path = root / dest
            before = before_path.read_bytes() if before_path.exists() else b""
            after = outputs[dest]
            python_dependencies(before, after, local_modules)
            relative_python_resources(after, relative, package['files'],
                                      lambda p: outputs[package['directory'] + '/' + p])
        package["commit"] = new_commit
        outputs[package["directory"] + "/PROVENANCE.json"] = json_bytes(package)
        descriptor["manifest_sha256"] = sha(outputs[package["directory"] + "/PROVENANCE.json"])
    for identifier, new in new_skills.items():
        if identifier in old_skills:
            old = old_skills[identifier]
            new.update(acquisition_category=new["category"], category=old["category"],
                       acquisition_validation=new.pop("validation"), distribution_status=old["distribution_status"],
                       decision_reason=old["decision_reason"], pending=old["pending"], validation=old["validation"],
                       distribution=copy.deepcopy(old["distribution"]))
            for field in ("compatibility", "inclusion_review"):
                if field in old: new[field] = copy.deepcopy(old[field])
            if 'inclusion_review' in old: new['required_files']=sorted(set(old['required_files']) | set(new['required_files']))
            if new["distribution"]:
                new["distribution"]["runtime_requirements"] = new["dependency_evidence"]
        else:
            reason = "Nova skill encontrada; análise e aprovação de distribuição pendentes."
            new.update(acquisition_category=new["category"], acquisition_validation=new.pop("validation"),
                       distribution_status="pending", distribution=None, decision_reason=reason, pending=[reason],
                       validation={"status": "not_distributed", "copy_plan_complete": False, "enabled": False,
                                   "agent_integration_tested": False, "vendor_workflow_certified": False})
            policy["rows"].append({"id": identifier, "status": "pending", "category": new["category"], "bundle": new["source_id"], "reason": reason})
    cat["skills"] = [new_skills.get(s["id"], s) for s in cat["skills"]] + [new_skills[k] for k in discovered]
    cat["python_executor"] = runtime
    sources = {s["id"]: s for s in raw["sources"]}
    cat["sources"] = [sources.get(s["id"], s) for s in cat["sources"]]
    cat["distribution_aliases"] = [a for a in cat["distribution_aliases"] if a["source_id"] not in source_ids] + raw["distribution_aliases"]
    recount(cat)
    for sid in source_ids:
        indexes[sid] = fresh_indexes[sid]
    references = {k: v for k, v in references.items() if k.split(":", 1)[0] not in source_ids}
    references.update(fresh_refs)
    patches = [p for p in patches if p["package"] not in affected_packages] + replacement_patches
    reviews = json.loads(read_bytes(root, "Skills/validacao/revisao-recursos.json"))
    # Uma nova referência não resolvida de skill aprovada nunca recebe exceção automática.
    for identifier, refs in fresh_refs.items():
        if new_skills[identifier]["distribution_status"] != "approved":
            continue
        allowed = {(r["document"], r["target"]) for r in reviews if r["skill_id"] == identifier}
        for item in refs:
            if item["status"] == "unresolved_requires_review" and (item["document"], item["target"]) not in allowed:
                raise ValueError("Referência nova não resolvida: " + identifier + ":" + item["target"])
    outputs.update({"Skills/manutencao/distribuicao-politica.json": json_bytes(policy),
                    "Skills/validacao/arquivos.json": json_bytes(indexes), "Skills/validacao/recursos.json": json_bytes(references),
                    "Skills/validacao/adaptacoes.json": json_bytes(patches)})
    cat["generation"].update(tool="Automacao/manutencao-skills/atualizacao_receita.py",
        tool_sha256=sha(read_bytes(root, "Automacao/manutencao-skills/atualizacao_receita.py")))
    cat["generation"].update(policy_sha256=sha(outputs["Skills/manutencao/distribuicao-politica.json"]),
        source_lock_sha256=sha(full_lock))
    outputs["Skills/catalogo.json"] = json_bytes(cat)
    affected_categories = {s["category"] for s in cat["skills"] if s["source_id"] in source_ids}
    outputs.update(category_indexes(cat,affected_categories))
    details.update(new_skills_pending=discovered, affected_packages=affected_packages, source_changes=source_changes)
    return outputs, details
