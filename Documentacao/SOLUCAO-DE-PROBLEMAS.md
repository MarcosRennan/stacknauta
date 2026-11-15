# Solução de problemas

[README](../README.md) · [Linux](INSTALACAO-LINUX.md) · [Agentes](AGENTES.md) · [Uso](PRIMEIROS-PASSOS.md) · [Validação](VALIDACAO.md)

Diagnostique antes de mudar o ambiente. Não instale fallback, altere hashes,
desative sandbox ou apague consumidores para fazer uma verificação passar.
Os comandos de inspeção não iniciam agentes nem acessam serviços remotos.

## asdf e runtimes

```bash
type -a asdf
asdf --version
asdf current
cat "$HOME/.tool-versions"
printf '%s\n' "$PATH"
command -v python node
asdf which python
asdf which node
ls -ld "${ASDF_DATA_DIR:-$HOME/.asdf}" "${ASDF_DATA_DIR:-$HOME/.asdf}/shims"
```

| Sintoma | Inspeção e ação do operador |
|---|---|
| asdf indisponível | Confira executable/PATH e shell de login/interativo. Abra novo terminal após preparação; não invoque Python de sistema |
| Shims fora do PATH | Confira o diretório real de dados e a ordem do PATH; ajuste conscientemente a configuração da máquina, não o gerador |
| Runtime não instalado | `asdf list python` / `asdf list nodejs`; revise instalação futura pelo guia. Selecionar versão não a instala |
| Sem versão global | Confira HOME/.tool-versions; uma versão concreta por plugin, sem system/latest/lista de fallback |
| Resolução local diferente | Current informa o arquivo de origem; o bootstrap isola overrides, mas validadores e scripts de skills também exigem o global corrente. Não sobrescreva arquivos locais sem revisar |
| Python muito antigo | O contrato exige >=3.11; erros de parsing/import também podem anteceder o pré-check. Use runtime global aprovado, não modifique o código para ocultar a incompatibilidade |
| Reshim necessário | Depois de confirmar instalação, o operador pode regenerar os shims da versão escolhida. Reshim é alteração, não diagnóstico automático |
| Diretório global inacessível | Compare visibilidade/permissões no host e no ambiente do agente; PATH não comprova que o diretório está montado |

Python 3.14.8 e Node 24.21.0 são a baseline testada, não mínimos universais.
Não execute asdf install/update como resposta automática a um bloqueio.

## Agentes e Antigravity

```bash
# Na raiz do workspace aberto, não num diretório aleatório:
pwd -P
test -f AGENTS.md
test -d .agents/skills
find .agents/skills -maxdepth 2 -name SKILL.md -type f -print
```

| Sintoma | Diagnóstico |
|---|---|
| AGENTS não carregado | Confirme cwd/workspace correto, nome/case e arquivo acessível. Reabra sessão manualmente após revisar instruções; não gere outro AGENTS por cima |
| Skill ausente | No StackNauta procure project-bootstrap; no consumidor procure aliases stacknauta-*. Catálogo físico não comprova divulgação ao modelo. Confira `/skills` no agy e caminho real retornado |
| Alias existe, original não abre | Leia o encaminhador e resolva o link relativamente a ele. O bootstrap/verificador deve detectar recursos ausentes; não invente SKILL.md substituto |
| Workspace não confiável | Revise e aprove somente o workspace pretendido na interface nativa. Não migre configurações globais nem amplie confiança automaticamente |
| Host funciona, sandbox não | Compare asdf/current/which e ls absolutos nos dois ambientes. Na 2G, shims apareciam no PATH, mas o diretório não era visível no sandbox |
| Runtime invisível no agy | Isolamento de filesystem é causa provável registrada, não defeito definitivamente provado do StackNauta. Registre operação/caminho negado e avalie permissões nativas com o operador |

Não recomende desativar proteções como solução padrão. Se o ambiente não expõe
o runtime global, pare a operação dependente; não use /usr/bin/python ou Node de
sistema. Não é necessário GEMINI.md. Os nomes `.gemini/` de configuração pessoal
também podem pertencer ao Antigravity e não devem ser apagados por associação.

## Git, GitHub e SSH

| Problema | Como distinguir |
|---|---|
| StackNauta não publicado | Não há URL real para clonar; use cópia local confiável e registre validação remota pendente |
| Chave pública ausente | Inspecione nomes .pub; gere chave somente por decisão do usuário, sem sobrescrever privada existente |
| Permission denied (publickey) | Confira conta, chave escolhida/ssh-agent, chave pública cadastrada e autorização organizacional; não imprima a privada |
| Autenticação SSH exit 1 | Pode ser o sucesso esperado do teste GitHub sem shell; confira a mensagem, não apenas o exit code |
| Repository not found | URL incorreta, publicação ausente ou conta sem acesso; autenticar não concede permissão ao repo |
| Permission denied local | Confira proprietário, diretório pai e permissões efetivas. Git preserva o bit de execução, não todos os bits rwx; não faça chmod recursivo sem diagnóstico |

Siga os [passos SSH](INSTALACAO-LINUX.md). Eles exigem rede e não foram executados
na 4C. Não adicione origin, troque remotos ou tente push para diagnosticar.

## StackNauta e manifests

Leia stdout/stderr e código de saída; a CLI usa exit 2 para bloqueios previstos.

| Problema | Ação segura |
|---|---|
| Skill incompatível | Reveja stack, alvo, features e pré-requisitos declarados; não force seleção |
| Skill pendente/excluída | Consulte catálogo e contrato; não promova ou reclassifique durante bootstrap |
| Skill explicit não selecionada | Inclua o ID nominal quando desejado; não acrescente todas as sugestões automaticamente |
| Dependência incompatível | Revise o fechamento completo; não elimine uma dependência só para permitir cópia |
| Hash de plano diferente | Mudou config/runtime/biblioteca/gerador? Gere novo plano e revise antes de nova autorização; não troque o hash silenciosamente |
| Arquivo protegido alterado/ausente | Preserve a evidência, confronte com revisão confiável e investigue. Não regrave manifest/lock para aceitar o conteúdo |
| Recurso faltante | Verifique a integridade do clone e fechamento; não busque no cache para esconder pacote incompleto |
| Evolução permitida | Leia modified/removed/unmanaged e verification_state; verified_with_evolution não certifica sintaxe ou execução |
| Arquitetura pendente | Ausência não é autorização para escolher. Solicite decisão somente quando necessária ao trabalho |
| Filesystem/procfs indisponível | O bootstrap pode recusar publicação segura; use destino compatível aprovado, sem alterar permissões/proteções como workaround automático |

Os manifests persistem configuração e **destination absoluto**. `agent-verify`
usa esse destino; mover uma pasta e apontar ao config antigo não é migração.
Não edite manifests/hashes para certificar relocação. Reproduzir planos históricos
pode exigir a revisão original do gerador e biblioteca. [Contrato completo](../Automacao/project-bootstrap/CICLO-DE-VIDA.md).

## Aplicação consumidora

`dependencies: {}`, ausência de node_modules, bundler ou script npm são esperados
no exemplo. Verified/intact não significa React executável. Escolha versões e
toolchain com o usuário, revise rede/instalações, autorize operações e só então
configure build/testes. Não execute npm install, npx ou geradores implicitamente.
Se não for possível compilar sem instalações, informe a limitação com os arquivos
e pré-requisitos faltantes; isso não invalida a preparação estrutural do esqueleto.
