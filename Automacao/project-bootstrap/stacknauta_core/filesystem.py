"""Operações POSIX ancoradas em dirfd: não seguir symlinks nem substituir arquivos."""
import contextlib
import os
import secrets
import stat
from pathlib import Path, PurePosixPath

from . import BootstrapError

DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
MANIFEST = ".stacknauta/manifest.json"


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


def publish(root_fd, relative, data, hook=None):
    """Publica arquivo novo completo, sem rename/replace e sem link para a biblioteca.

    O link atômico é interno ao destino e existe apenas durante a publicação;
    o temporário próprio é removido, deixando um único inode físico nlink=1.
    Arquivos preexistentes nunca são abertos para escrita nem removidos.
    """
    components = parts(relative)
    with relative_directory(root_fd, components[:-1], create=True) as parent:
        temporary = ".stacknauta-tmp-" + secrets.token_hex(16)
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        try:
            try:
                view = memoryview(data)
                while view:
                    written = os.write(fd, view)
                    if written <= 0:
                        raise OSError("Escrita incompleta")
                    view = view[written:]
                os.fchmod(fd, 0o644)
                os.fsync(fd)
            finally:
                os.close(fd)
            if hook:
                hook(relative)
            try:
                os.link(temporary, components[-1], src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
            except FileExistsError:
                if read(root_fd, relative, len(data)) != data:
                    raise BootstrapError(f"Conflito concorrente preservado: {relative}")
            os.fsync(parent)
        finally:
            # Somente o temporário com nome exclusivo criado nesta chamada.
            os.unlink(temporary, dir_fd=parent)
            os.fsync(parent)


class Target:
    def __init__(self, destination, default_parent, protected=()):
        self.path = Path(destination)
        self.default_parent = Path(default_parent)
        self.protected = tuple(Path(p).resolve() for p in protected)

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

    def inspect(self, manifest, files):
        self.boundaries()
        expected = {MANIFEST: manifest, **files}
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
                new, unchanged = [], []
                for relative, data in expected.items():
                    existing = read(root, relative, len(data))
                    if existing is None:
                        new.append(relative)
                    elif existing == data:
                        unchanged.append(relative)
                    else:
                        raise BootstrapError(f"Arquivo preexistente diferente; preservado: {relative}")
                return {"create": sorted(new), "unchanged": sorted(unchanged)}
        except FileNotFoundError:
            return {"create": sorted(expected), "unchanged": []}
        except OSError as exc:
            raise BootstrapError(f"Destino inválido ou inacessível: {exc.strerror}") from exc

    def apply(self, manifest, files, hook=None):
        # Repete pré-check antes de qualquer escrita, para detectar alterações após o dry-run.
        state = self.inspect(manifest, files)
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
                    for relative, data in {MANIFEST: manifest, **files}.items():
                        previous = read(root, relative, len(data))
                        if previous is not None:
                            if previous != data:
                                raise BootstrapError(f"Conflito preservado: {relative}")
                            continue
                        publish(root, relative, data, hook)
            verified = self.inspect(manifest, files)
            if verified["create"]:
                raise BootstrapError("Estado final mudou durante a aplicação; revisão necessária")
            return {"status": "prepared", "created_files": len(state["create"]), "unchanged_files": len(state["unchanged"])}
        except (OSError, BootstrapError) as exc:
            raise BootstrapError(f"Aplicação interrompida sem substituir arquivos existentes. Reexecute o mesmo plano para completar arquivos ausentes; conflitos exigem revisão manual. Motivo: {exc}") from exc
