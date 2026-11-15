# Instalação Linux

[README](../README.md) · [Agentes](AGENTES.md) · [Primeiros passos](PRIMEIROS-PASSOS.md) · [Validação](VALIDACAO.md) · [Problemas](SOLUCAO-DE-PROBLEMAS.md)

Fontes conferidas em **15/11/2026**. Referência: Fedora 44 Workstation x86_64.
Instalações, downloads e autenticação deste guia são passos **futuros do usuário**;
não foram executados na auditoria 4C. O teste local reutiliza runtimes instalados.

## 1. Ferramentas e limites reais

```bash
cat /etc/os-release
uname -m
command -v bash git ssh curl readlink
```

| Ferramenta | Onde é necessária |
|---|---|
| Bash/coreutils, incluindo readlink -e | Launchers do StackNauta |
| Python global asdf >=3.11 | Executor obrigatório; biblioteca padrão, sem pip/venv |
| Node global asdf | JS/TS, helpers que o declarem e parsing JS dos validadores |
| Git | Obtenção/validação do clone, regressão e determinadas skills |
| OpenSSH e curl | Acesso remoto e provisionamento, não bootstrap offline |
| Compilador/make/headers | Preparação de runtimes por compilação, não uso cotidiano |
| Um agente autenticado | Fluxo conversacional; CLI de bootstrap também funciona diretamente |

Java/JVM, Go e Rust só são exigidos pela stack/skill declarada. Kotlin usa a JVM.
TypeScript, frameworks, SDKs e bundlers são escolhas posteriores, não ferramentas
globais obrigatórias para preparar um esqueleto.

O núcleo usa Linux/POSIX, descritores, O_NOFOLLOW, fsync, O_TMPFILE, publicação
por `/proc/self/fd` e renameat2/libc em operações aplicáveis. Nem todo filesystem
ou container fornece esses recursos. Não se certifica Windows, macOS ou qualquer
filesystem remoto. Confirme o destino físico com o bootstrap sintético.

## 2. Preparação Fedora — somente na futura máquina

Após revisar as instalações propostas:

```bash
sudo dnf install git openssh-clients curl bash coreutils tar gzip findutils
```

O asdf documenta Git/Bash com DNF; o Fedora documenta
[openssh-clients](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
e [curl](https://packages.fedoraproject.org/pkgs/curl/curl/). Não é necessário
openssh-server para clonar via SSH.

O plugin Python utiliza python-build. Para Fedora 42+, a
[receita de build](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
indica Tk 8 de compatibilidade; Python 3.14 também requer zstd para seu módulo:

```bash
sudo dnf install make gcc patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk8-devel libffi-devel xz-devel libuuid-devel gdbm-libs libnsl2 libzstd-devel
```

Confira disponibilidade de pacotes na distribuição utilizada. A lista não foi
instalada numa máquina nova. Para Fedora antigo ou Debian/Ubuntu, consulte a seção
própria da fonte; não traduza pacotes automaticamente. O plugin Node prefere
binários pré-compilados; se precisar compilar, siga os requisitos específicos de
[asdf-nodejs](https://github.com/asdf-vm/asdf-nodejs). Não se exige GCC para todo uso.

Para preparar Node pelo plugin, diagnostique também, sem instalar:

```bash
command -v gpg || printf '%s\n' 'gpg indisponível no PATH'
command -v gawk || printf '%s\n' 'gawk indisponível no PATH'
```

O [guia geral do asdf](https://asdf-vm.com/guide/getting-started.html#plugin-dependencies)
lista GnuPG e GNU Awk para esse plugin. `gawk` fornece o processamento `awk` usado
pelo plugin/node-build no Fedora. `gpg` é necessário em revisões ou fluxos que
verificam assinaturas OpenPGP; o plugin atual usa node-build com checksums e a
revisão local inspecionada não chama gpg. Confira os requisitos da revisão do
plugin/node-build escolhida e da versão Node: isso não torna ambas as ferramentas
obrigatórias para executar um Node já instalado ou o núcleo StackNauta.

Os pacotes Fedora são [gnupg2](https://packages.fedoraproject.org/pkgs/gnupg2/gnupg2/)
e [gawk](https://packages.fedoraproject.org/pkgs/gawk/gawk/). Provisionamento futuro,
separado do diagnóstico: execute **somente** o comando cujo requisito e ausência
foram confirmados, após decisão do operador; não instale automaticamente.

```bash
# Apenas se gpg for exigido pelo fluxo escolhido e estiver ausente:
sudo dnf install gnupg2
# Apenas se GNU Awk for exigido e estiver ausente:
sudo dnf install gawk
```

## 3. asdf moderno

**0.20.2** é a versão do asdf observada e da documentação consultada, não mínimo
universal do projeto. Escolha e confira o binário Linux/arquitetura em
[releases oficiais](https://github.com/asdf-vm/asdf/releases/tag/v0.20.2), inclusive
checksums publicados. O [guia de instalação](https://asdf-vm.com/guide/getting-started.html)
permite extrair o binário numa pasta do PATH, sem instalar Go para compilar asdf.

Na release oficial da versão escolhida, abra **Assets** e localize o próprio
`.tar.gz` para Linux e sua arquitetura (x86_64 corresponde a linux-amd64).
Confira o nome completo e copie o digest **sha256** exibido para esse artefato.
Na release 0.20.2 há também arquivos `.md5`: não use MD5 nem o SHA-256 desses
arquivos auxiliares para conferir o tar.gz. Se não localizar um SHA-256 oficial
correspondente, interrompa; não use um valor de terceiros ou o hash local como
valor esperado. Obtenha o arquivo e o digest de fonte oficial confiável.

Depois do download manual, informe o caminho e os 64 dígitos hexadecimais oficiais,
sem o prefixo `sha256:`. O bloco compara o valor local e só extrai se coincidirem:

```bash
(
  read -r -p 'Caminho do tar.gz do asdf baixado: ' STACKNAUTA_ASDF_ARCHIVE || exit 1
  test -f "$STACKNAUTA_ASDF_ARCHIVE" || { printf '%s\n' 'Arquivo não encontrado.' >&2; exit 1; }
  read -r -p 'SHA-256 oficial desse tar.gz: ' STACKNAUTA_ASDF_SHA256 || exit 1
  [[ "$STACKNAUTA_ASDF_SHA256" =~ ^[[:xdigit:]]{64}$ ]] || { printf '%s\n' 'SHA-256 oficial inválido.' >&2; exit 1; }
  STACKNAUTA_ASDF_LOCAL="$(sha256sum -- "$STACKNAUTA_ASDF_ARCHIVE")" || exit 1
  STACKNAUTA_ASDF_LOCAL="${STACKNAUTA_ASDF_LOCAL%% *}"
  printf 'SHA-256 local: %s\n' "$STACKNAUTA_ASDF_LOCAL"
  [[ "$STACKNAUTA_ASDF_LOCAL" == "${STACKNAUTA_ASDF_SHA256,,}" ]] || { printf '%s\n' 'SHA-256 divergente; extração bloqueada.' >&2; exit 1; }
  # Somente após coincidência e decisão de instalar na máquina nova:
  mkdir -p "$HOME/.local/bin" || exit 1
  tar -xzf "$STACKNAUTA_ASDF_ARCHIVE" -C "$HOME/.local/bin" asdf || exit 1
  export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$HOME/.local/bin:$PATH"
  type -a asdf
  asdf --version
)
```

Os parênteses interrompem o bloco em caso de erro sem encerrar seu terminal;
a exportação de PATH vale apenas dentro dele. Nenhum download é feito pelo bloco.
Antes de extrair, confira se já existe asdf e não sobrescreva uma instalação sem
decisão explícita. Para persistir o PATH, adicione a exportação uma única vez ao
arquivo apropriado, preservando seu conteúdo: Bash login usa ~/.bash_profile;
terminais interativos podem precisar de ~/.bashrc; Zsh usa ~/.zshrc. Reabra o
terminal e confira o resultado. Essas alterações pertencem ao operador da máquina
nova, nunca a uma correção silenciosa pelo StackNauta.

Desde 0.16, asdf é um binário; não copie instruções antigas de carregar asdf.sh.
Use `asdf set -u` para HOME e `asdf set` para o diretório atual, em vez de global/local.
Uma instalação antiga exige revisão própria da
[migração oficial](https://asdf-vm.com/guide/upgrading-to-v0-16.html).

## 4. Plugins e versões globais

Confira o que já existe; execute cada add somente se o plugin estiver ausente:

```bash
asdf plugin list
asdf plugin add python https://github.com/asdf-community/asdf-python.git
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
```

Fontes: [Python](https://github.com/asdf-community/asdf-python) e
[Node](https://github.com/asdf-vm/asdf-nodejs). Para reproduzir a baseline
observada, após aprovar versões/downloads:

```bash
asdf install python 3.14.8
asdf install nodejs 24.21.0
asdf set -u python 3.14.8
asdf set -u nodejs 24.21.0
```

Isso modifica o global da máquina nova. Não execute para alterar um ambiente
existente sem decisão do usuário. O núcleo exige Python >=3.11; **3.14.8 e 24.21.0
são versões testadas**, não mínimos inferidos. Não há mínimo geral de Node imposto
pelo núcleo nem matriz certificando todas as outras versões. Se o plugin não
oferecer a versão, pare e revise; não substitua por latest.

Formato esperado em `$HOME/.tool-versions`, uma versão concreta por plugin:

```text
python 3.14.8
nodejs 24.21.0
```

Não use system, múltiplos fallbacks ou rótulos dinâmicos. O asdf normalmente pode
priorizar variáveis ASDF_*_VERSION e arquivos locais; o StackNauta lê explicitamente
o global, isola overrides de versão nos probes e exige os executáveis físicos
correspondentes. Os validadores também exigem resolução corrente global.
[Seleção de versões oficial](https://asdf-vm.com/manage/versions.html).

## 5. Diagnóstico sem instalação

```bash
git --version
ssh -V
curl --version
asdf --version
asdf current
cat "$HOME/.tool-versions"
printf '%s\n' "$PATH"
command -v asdf python node
asdf which python
asdf which node
asdf where python 3.14.8
asdf where nodejs 24.21.0
asdf exec python --version
asdf exec node --version
```

Current deve indicar HOME/.tool-versions e instalação existente; which deve
apontar para installs/plugin/versão. Se escolheu outra versão, ajuste where.
Shims ausentes podem exigir `asdf reshim python 3.14.8` ou
`asdf reshim nodejs 24.21.0`, depois de comprovar instalação. Reshim modifica
shims, não é diagnóstico automático. Veja [problemas](SOLUCAO-DE-PROBLEMAS.md).

## 6. GitHub e SSH — obtenção futura

**Ainda não há URL GitHub publicada confirmada para o StackNauta.** Acesso remoto
e clone SSH só poderão ser validados depois da publicação e concessão de acesso.
Nenhum comando de autenticação ou geração de chave foi executado na 4C.

```bash
git --version
find "$HOME/.ssh" -maxdepth 1 -name '*.pub' -type f -print
```

Se .ssh não existir, find informa isso; não é falha do StackNauta. Reutilize chave
adequada existente. Se decidir criar outra, siga o
[procedimento oficial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent):

```bash
# Placeholder de email; escolha nome novo se houver conflito, nunca sobrescreva.
ssh-keygen -t ed25519 -C 'seu-email@example.com'
```

Escolha passphrase. **Somente a pública .pub** deve ser adicionada à conta em SSH
and GPG keys, conforme a [documentação](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
Não exiba, compartilhe ou commite a privada. Proteja-a com acesso do proprietário
(normalmente 0600) e o diretório com 0700; não faça chmod recursivo indiscriminado.
Configure o ssh-agent pelo guia se a chave escolhida não for localizada.

```bash
ssh -T git@github.com
```

No [teste oficial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection),
compare a fingerprint publicada antes de confiar no host. Mensagem de sucesso
identifica o usuário e ausência de shell; **exit 1 é esperado**. Autenticação não
garante acesso a um repositório privado ou autorização organizacional.

Quando houver URL real, copie-a do GitHub; não deduza uma URL para o projeto:

```bash
read -r -p 'URL SSH efetivamente publicada do StackNauta: ' STACKNAUTA_REPO_SSH
mkdir -p "$HOME/Projetos"
git clone -- "$STACKNAUTA_REPO_SSH" "$HOME/Projetos/StackNauta"
cd "$HOME/Projetos/StackNauta"
git remote -v
git status --short
```

`git@github.com:<ORGANIZACAO>/<REPOSITORIO>.git` é **placeholder de formato**,
não endereço publicado. Repositórios públicos e privados podem usar SSH; privados
exigem acesso. Não adicione origin numa cópia já configurada só para seguir o guia.

Identidade Git não é autenticação. Se precisar configurá-la, use valores próprios
e somente configuração local, dentro do clone:

```bash
git config --local user.name 'Seu Nome'
git config --local user.email 'seu-email@example.com'
```

Não é necessário commit/push para usar o bootstrap. Referência:
[GitHub SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
Depois confira a [validação](VALIDACAO.md), prepare apenas o
[agente desejado](AGENTES.md) e siga o [primeiro uso](PRIMEIROS-PASSOS.md).
