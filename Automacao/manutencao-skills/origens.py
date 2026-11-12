"""URLs GitHub e referências; nenhuma configuração de autenticação é gravada."""
import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


def relative_path(value):
    p = PurePosixPath(value)
    if not value or value=='.' or p.is_absolute() or str(p) != value or any(x in {'.', '..', '.git'} for x in p.parts) or '\\' in value or any(ord(c)<32 for c in value):
        raise ValueError('Caminho solicitado inseguro')
    return value


def parse_url(value, *, allow_local=False):
    if not isinstance(value, str) or not value or any(ord(c)<33 for c in value) or '\\' in value:
        raise ValueError('URL de origem inválida')
    if allow_local and Path(value).is_absolute():
        return {'url':value, 'identity':str(Path(value).resolve()), 'owner':'fixture', 'repo':Path(value).name, 'tail':[], 'kind':None}
    ssh = re.fullmatch(r'git@github\.com:([^/]+)/([^/]+?)/?', value)
    if ssh:
        owner, repo = ssh.groups(); tail=[]; kind=None
        url='git@github.com:' + owner + '/' + repo.removesuffix('.git') + '.git'
    else:
        parsed=urlsplit(value)
        if parsed.query or parsed.fragment or parsed.hostname!='github.com' or parsed.password or parsed.port not in (None,22):
            raise ValueError('Somente URLs GitHub sem query, fragmento, senha ou porta personalizada')
        if parsed.scheme=='https' and parsed.username is None and parsed.port is None:
            parts=unquote(parsed.path).strip('/').split('/')
            if len(parts)<2: raise ValueError('Informe proprietário e repositório GitHub')
            owner,repo,*rest=parts
            kind=rest[0] if rest else None; tail=rest[1:]
            if kind not in (None,'tree','blob') or (kind is not None and len(tail)<1):
                raise ValueError('Use URL do repositório ou /tree/REF/caminho ou /blob/REF/SKILL.md')
            if tail: relative_path('/'.join(tail))
            url='https://github.com/' + owner + '/' + repo.removesuffix('.git') + '.git'
        elif parsed.scheme=='ssh' and parsed.username=='git' and parsed.port in (None,22):
            parts=parsed.path.strip('/').split('/')
            if len(parts)!=2: raise ValueError('Remoto SSH deve apontar ao repositório')
            owner,repo=parts;tail=[];kind=None
            url='git@github.com:' + owner + '/' + repo.removesuffix('.git') + '.git'
        else: raise ValueError('Use HTTPS ou SSH GitHub (usuário git)')
    repo=repo.removesuffix('.git')
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})',owner) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,99}',repo) or repo in ('.','..'):
        raise ValueError('Proprietário/repositório GitHub inválido')
    return {'url':url,'identity':(owner+'/'+repo).lower(),'owner':owner,'repo':repo,'tail':tail,'kind':kind}


def refs(git, url):
    output=git.run(Path.home(),'ls-remote','--symref',url,'HEAD','refs/heads/*','refs/tags/*')
    if len(output)>2_000_000: raise ValueError('Lista de referências remotas excessiva')
    default=None; revisions={}
    for row in output.splitlines():
        parts=row.split()
        if len(parts)==3 and parts[0]=='ref:' and parts[2]=='HEAD': default=parts[1].removeprefix('refs/heads/')
        if len(parts)==2 and re.fullmatch(r'[0-9a-f]{40}',parts[0]): revisions[parts[1]]=parts[0]
    if not default or 'refs/heads/'+default not in revisions: raise ValueError('Branch padrão remota indisponível')
    return default,revisions


def resolve(git, parsed, *, revision=None, path=None, existing=None):
    tail='/'.join(parsed['tail']); existing=existing or {}
    default=existing.get('default_branch'); available={}
    # Sem revisão explícita, uma origem existente permanece no commit registrado.
    if not tail and revision is None and existing:
        return {**existing,'requested_path':relative_path(path) if path else None}
    default, available=refs(git, parsed['url'])
    candidates=[]
    for key, commit in available.items():
        if key.startswith('refs/heads/'): kind='branch';name=key[11:]
        elif key.startswith('refs/tags/') and not key.endswith('^{}'): kind='tag';name=key[10:];commit=available.get(key+'^{}',commit)
        else: continue
        if (revision and name==revision) or (not revision and (tail==name or tail.startswith(name+'/'))):
            candidates.append((name,kind,commit))
    if tail and re.fullmatch(r'[0-9a-f]{40}',tail.split('/')[0]):
        candidates.append((tail.split('/')[0],'commit',tail.split('/')[0]))
    if revision and re.fullmatch(r'[0-9a-f]{40}',revision): candidates=[(revision,'commit',revision)]
    if not revision and not tail: candidates=[(default,'branch',available['refs/heads/'+default])]
    if not candidates: raise ValueError('Revisão/branch solicitada indisponível')
    # Branches com barras: maior prefixo válido, sem adivinhar o primeiro segmento.
    candidates.sort(key=lambda x:len(x[0]),reverse=True)
    if len(candidates)>1 and candidates[0][0]==candidates[1][0] and candidates[0][1]!=candidates[1][1]:
        raise ValueError('Branch/tag ambíguos; use um commit completo')
    name,kind,commit=candidates[0]
    derived=tail[len(name):].lstrip('/') if tail and (tail==name or tail.startswith(name+'/')) else None
    if tail and derived is None: raise ValueError('Revisão explícita não corresponde à URL')
    if path and derived and path!=derived: raise ValueError('Caminho explícito diverge da URL')
    scope=path or derived
    if scope: relative_path(scope)
    if parsed['kind']=='blob' and (not scope or not scope.endswith('SKILL.md')): raise ValueError('URL blob deve apontar a SKILL.md')
    if scope and Path(scope).name=='SKILL.md': scope=Path(scope).parent.as_posix();scope=None if scope=='.' else scope
    if existing and commit!=existing['commit']: raise ValueError('Origem já cadastrada: revisão diferente; use update, sem atualização implícita em add')
    return {**existing,'url':existing.get('url',parsed['url']),'default_branch':default,
            'branch':name if kind=='branch' else default,'commit':commit,'revision_type':kind,'revision_ref':name,'requested_path':scope}
