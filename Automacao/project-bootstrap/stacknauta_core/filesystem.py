"""Operações POSIX ancoradas em dirfd: não seguir symlinks nem substituir arquivos."""
import contextlib
import ctypes
import errno
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

from . import BootstrapError
from .lifecycle import classification

DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
MANIFEST = ".stacknauta/manifest.json"


def rename_noreplace(source, destination, *, src_dir_fd, dst_dir_fd):
    """renameat2 Linux: nunca substituir um destino criado concorrentemente."""
    rename = getattr(ctypes.CDLL(None, use_errno=True), 'renameat2', None)
    if rename is None:
        raise OSError(errno.ENOSYS, 'renameat2 indisponível; operação recusada')
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(src_dir_fd, os.fsencode(source), dst_dir_fd, os.fsencode(destination), 1):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), destination)


def parts(relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in relative or "\x00" in relative:
        raise BootstrapError(f"Caminho gerado inseguro: {relative}")
    return path.parts


@contextlib.contextmanager
def directory(path):
    """Abre cada componente físico, inclusive ancestrais, sem seguir links."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise BootstrapError("Diretório precisa ser absoluto e sem travessia")
    fd = os.open("/", DIR_FLAGS)
    try:
        for component in path.parts[1:]:
            new = os.open(component, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd
    finally:
        os.close(fd)


@contextlib.contextmanager
def relative_directory(root_fd, components, create=False):
    fd = os.dup(root_fd)
    try:
        for component in components:
            if create:
                try:
                    os.mkdir(component, 0o755, dir_fd=fd)
                    os.fsync(fd)
                except FileExistsError:
                    pass
            new = os.open(component, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd
    finally:
        os.close(fd)


def read(root_fd, relative, limit):
    components = parts(relative)
    try:
        with relative_directory(root_fd, components[:-1]) as parent:
            fd = os.open(components[-1], READ_FLAGS, dir_fd=parent)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise BootstrapError(f"Arquivo não regular ou hardlink perigoso: {relative}")
                if info.st_size > limit:
                    raise BootstrapError(f"Arquivo inesperadamente grande: {relative}")
                chunks, length = [], 0
                while True:
                    chunk = os.read(fd, min(65536, limit + 1 - length))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    length += len(chunk)
                    if length > limit:
                        raise BootstrapError(f"Arquivo excede o limite: {relative}")
                return b"".join(chunks)
            finally:
                os.close(fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise BootstrapError(f"Caminho perigoso ou ilegível: {relative} ({exc.strerror})") from exc


def fingerprint(root_fd, relative, *, expected=None):
    """Hash em streaming: tamanho original não é limite para arquivo evolutivo."""
    components = parts(relative)
    try:
        with relative_directory(root_fd, components[:-1]) as parent:
            fd = os.open(components[-1], READ_FLAGS, dir_fd=parent)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise BootstrapError(f"Arquivo não regular ou hardlink perigoso: {relative}")
                if expected is not None and info.st_size != expected["size"]:
                    current = {"size": info.st_size, "sha256": "not_read_size_mismatch"}
                    raise BootstrapError(f"Conflito de integridade; arquivo preexistente diferente, preservado: {relative} "
                                         f"(classe={classification(relative)}; esperado={expected}; atual={current})")
                digest = hashlib.sha256()
                size = 0
                remaining = info.st_size
                while remaining:
                    chunk = os.read(fd, min(65536, remaining))
                    if not chunk:
                        break
                    digest.update(chunk)
                    size += len(chunk)
                    remaining -= len(chunk)
                end = os.fstat(fd)
                if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (end.st_size, end.st_mtime_ns, end.st_ctime_ns) or size != end.st_size:
                    raise BootstrapError(f"Arquivo mudou durante verificação: {relative}")
                return {"sha256": digest.hexdigest(), "size": size}
            finally:
                os.close(fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise BootstrapError(f"Caminho perigoso ou ilegível: {relative} ({exc.strerror})") from exc


def inspect_files(root_fd, files, *, completed):
    state = {"create": [], "unchanged": [], "modified": {}, "removed": []}
    for relative, data in files.items():
        category = classification(relative)
        original = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        current = fingerprint(root_fd, relative, expected=original if category == "protected" or not completed else None)
        if current is None:
            if completed and category != "protected":
                state["removed"].append(relative)
            elif completed:
                raise BootstrapError(f"Arquivo protegido ausente: {relative}; restauração automática recusada")
            else:
                state["create"].append(relative)
        elif current == original:
            state["unchanged"].append(relative)
        elif completed and category != "protected":
            state["modified"][relative] = {"classification": category, "original": original, "current": current}
        else:
            raise BootstrapError(f"Conflito de integridade; arquivo preexistente diferente, preservado: {relative} "
                                 f"(classe={category}; esperado={original}; atual={current})")
    for key in ("create", "unchanged", "removed"):
        state[key].sort()
    return state


def inventory(root_fd, managed):
    """Lista adicionais sem ler conteúdo nem seguir links, inclusive em diretórios."""
    known_dirs = {"/".join(parts(path)[:i]) for path in managed for i in range(1, len(parts(path)))}
    result = []
    def visit(fd, prefix="", depth=0):
        if depth > 128:
            raise BootstrapError("Inventário excede profundidade segura de 128 diretórios")
        for name in sorted(os.listdir(fd)):
            path = prefix + name
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            is_dir = stat.S_ISDIR(info.st_mode)
            if path not in managed and path not in known_dirs:
                kind = "directory" if is_dir else "file" if stat.S_ISREG(info.st_mode) else "symlink_not_followed" if stat.S_ISLNK(info.st_mode) else "special_not_opened"
                result.append({"path": path, "kind": kind})
            if is_dir:
                child = os.open(name, DIR_FLAGS, dir_fd=fd)
                try:
                    visit(child, path + "/", depth + 1)
                finally:
                    os.close(child)
    try:
        visit(root_fd)
    except OSError as exc:
        raise BootstrapError(f"Inventário adicional inacessível: {exc.strerror}") from exc
    return result


def publish(root_fd, relative, data, hook=None):
    """Publica inode anônimo O_TMPFILE: zero nomes antes, um nome após linkat.

    /proc/self/fd é a referência do kernel ao descritor próprio, não um caminho
    fornecido pelo projeto. Sem suporte a O_TMPFILE/procfs, bloqueia sem fallback
    para hardlinks temporários nomeados. Nunca remove arquivos desconhecidos.
    """
    components = parts(relative)
    with relative_directory(root_fd, components[:-1], create=True) as parent:
        fd = os.open('.', os.O_WRONLY | os.O_TMPFILE | os.O_CLOEXEC, 0o600, dir_fd=parent)
        try:
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise OSError("Escrita incompleta")
                view = view[written:]
            os.fchmod(fd, 0o644)
            os.fsync(fd)
            if hook:
                hook(relative)
            try:
                os.link(f'/proc/self/fd/{fd}', components[-1], dst_dir_fd=parent, follow_symlinks=True)
            except FileExistsError:
                if read(root_fd, relative, len(data)) != data:
                    raise BootstrapError(f"Conflito concorrente preservado: {relative}")
            os.fsync(parent)
        finally:
            os.close(fd)  # O kernel descarta o inode se ainda não foi publicado.


class Target:
    def __init__(self, destination, default_parent, protected=()):
        self.path = Path(destination)
        self.default_parent = Path(default_parent)
        self.protected = tuple(Path(p).resolve() for p in protected)

    def manifest_schema(self):
        self.boundaries()
        try:
            with directory(self.path) as root:
                marker = read(root, MANIFEST, 10_000_000)
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise BootstrapError(f"Destino inválido ou inacessível: {exc.strerror}") from exc
        if marker is None:
            return None
        try:
            schema = json.loads(marker)["schema_version"]
            if type(schema) is not int or schema not in (1, 2):
                raise ValueError("schema não suportado")
            return schema
        except (ValueError, KeyError, TypeError) as exc:
            raise BootstrapError("Manifesto protegido inválido ou schema não suportado") from exc

    def pinned_inputs(self):
        """Lê evidências originais sem seguir links; o plano reconstruído as sela."""
        self.boundaries()
        try:
            with directory(self.path) as root:
                marker = read(root, MANIFEST, 10_000_000)
                if marker is None:
                    return None, None
                lock = read(root, '.stacknauta/skills-lock.json', 64_000_000)
        except FileNotFoundError:
            return None, None
        except OSError as exc:
            raise BootstrapError(f"Destino inválido ou inacessível: {exc.strerror}") from exc
        try:
            manifest = json.loads(marker)
            if lock is not None:
                expected = manifest['files']['.stacknauta/skills-lock.json']
                if expected != {'sha256': hashlib.sha256(lock).hexdigest(), 'size': len(lock)}:
                    raise ValueError('lock diverge do manifesto')
            return manifest, lock
        except (ValueError, KeyError, TypeError) as exc:
            raise BootstrapError('Manifesto/lock protegido inválido; evidência histórica insuficiente') from exc

    def boundaries(self):
        for protected in self.protected:
            if self.path == protected or self.path.is_relative_to(protected) or protected.is_relative_to(self.path):
                raise BootstrapError(f"Destino sobrepõe área protegida: {protected}")
        parent = self.path.parent
        try:
            with directory(parent):
                pass
        except FileNotFoundError:
            if parent != self.default_parent:
                raise BootstrapError("Diretório pai do destino explícito precisa existir; o núcleo não escreve fora do destino autorizado")
            try:
                with directory(parent.parent):
                    pass
            except OSError as exc:
                raise BootstrapError("Raiz padrão inválida ou com link simbólico") from exc
        except OSError as exc:
            raise BootstrapError("Ancestral do destino não é diretório físico acessível (symlinks são recusados)") from exc

    def inspect(self, manifest, files, *, completion=None):
        self.boundaries()
        expected = {MANIFEST: manifest, **files, **(dict([completion]) if completion else {})}
        try:
            with directory(self.path) as root:
                marker = read(root, MANIFEST, max(len(manifest), 10_000_000))
                if marker is None:
                    entries = os.listdir(root)
                    if entries:
                        # Recupera somente diretórios vazios deixados antes da primeira publicação.
                        if entries != [".stacknauta"]:
                            raise BootstrapError("Destino preexistente sem manifesto StackNauta; nada será sobrescrito")
                        with relative_directory(root, (".stacknauta",)) as metadata:
                            if os.listdir(metadata):
                                raise BootstrapError("Metadados preexistentes sem manifesto; revisão manual necessária")
                elif marker != manifest:
                    raise BootstrapError("Manifesto preexistente difere do plano; atualização/migração não faz parte desta etapa")
                completed = marker is not None and (completion is None or fingerprint(root, completion[0], expected={"sha256": hashlib.sha256(completion[1]).hexdigest(), "size": len(completion[1])}) is not None)
                state = inspect_files(root, expected, completed=completed)
                state["initialization"] = "legacy_complete" if marker is not None and completion is None else "complete" if completed else "initializing"
                state["unmanaged"] = inventory(root, expected)
                return state
        except FileNotFoundError:
            return {"create": sorted(expected), "unchanged": [], "modified": {}, "removed": [], "unmanaged": [], "initialization": "new"}
        except OSError as exc:
            raise BootstrapError(f"Destino inválido ou inacessível: {exc.strerror}") from exc

    def apply(self, manifest, files, hook=None, *, completion=None):
        # Repete pré-check antes de qualquer escrita, para detectar alterações após o dry-run.
        state = self.inspect(manifest, files, completion=completion)
        if not state["create"]:
            return {"status": "unchanged", "created_files": 0, "unchanged_files": len(state["unchanged"])}
        parent = self.path.parent
        try:
            if parent == self.default_parent:
                with directory(parent.parent) as above:
                    try:
                        os.mkdir(parent.name, 0o755, dir_fd=above)
                    except FileExistsError:
                        pass
            with directory(parent) as parent_fd:
                try:
                    os.mkdir(self.path.name, 0o755, dir_fd=parent_fd)
                except FileExistsError:
                    pass
                with relative_directory(parent_fd, (self.path.name,)) as root:
                    # Revalida propriedade/conflitos usando o MESMO descritor da escrita.
                    existing = read(root, MANIFEST, max(len(manifest), 10_000_000))
                    if existing is None:
                        entries = os.listdir(root)
                        if entries:
                            if entries != [".stacknauta"]:
                                raise BootstrapError("Destino ocupado durante aplicação; nenhum arquivo foi substituído")
                            with relative_directory(root, (".stacknauta",)) as metadata:
                                if os.listdir(metadata):
                                    raise BootstrapError("Metadados concorrentes preservados")
                    elif existing != manifest:
                        raise BootstrapError("Manifesto concorrente divergente")
                    expected = {MANIFEST: manifest, **files, **(dict([completion]) if completion else {})}
                    completed = existing is not None and (completion is None or fingerprint(root, completion[0], expected={"sha256": hashlib.sha256(completion[1]).hexdigest(), "size": len(completion[1])}) is not None)
                    anchored = inspect_files(root, expected, completed=completed)
                    for relative, data in expected.items():
                        if relative in anchored["create"]:
                            publish(root, relative, data, hook)
            verified = self.inspect(manifest, files, completion=completion)
            if verified["create"]:
                raise BootstrapError("Estado final mudou durante a aplicação; revisão necessária")
            return {"status": "prepared", "created_files": len(state["create"]), "unchanged_files": len(state["unchanged"])}
        except (OSError, BootstrapError) as exc:
            raise BootstrapError(f"Aplicação interrompida sem substituir arquivos existentes. Reexecute o mesmo plano para completar arquivos ausentes; conflitos exigem revisão manual. Motivo: {exc}") from exc
