# Agentes suportados

[README](../README.md) · [Linux](INSTALACAO-LINUX.md) · [Primeiros passos](PRIMEIROS-PASSOS.md) · [Problemas](SOLUCAO-DE-PROBLEMAS.md)

Instale **somente os clientes desejados**, não todos por padrão. Autenticação,
contas, planos e modelos são independentes do StackNauta. Preserve a configuração
existente. Os comandos de instalação/autenticação abaixo são para uso futuro pelo
operador; **nenhum agente foi executado ou instalado na 4C**, nem para --version.
Registre a versão realmente instalada; não há matriz certificando toda versão
futura dos clientes. Fontes conferidas em 15/11/2026.

## Base comum

Abra o agente na raiz da cópia StackNauta, onde estão AGENTS.md e
`.agents/skills/project-bootstrap/SKILL.md`. A skill encaminha ao único núcleo
Python. No consumidor, use a raiz gerada: AGENTS orienta a leitura explícita de
`.stacknauta/AGENT-INTEGRATION.md` e dos SKILL.md relevantes. O caminho Markdown
não é prova de import automático.

Skills são cópias físicas, com aliases rasos que encaminham aos originais. O uso
dos recursos toma como base o diretório do SKILL.md **original**. Confira leitura
real, não só uma declaração do modelo. Requisitos e decisões aprovadas prevalecem
sobre sugestões das skills; a pertinência da tarefa controla a consulta posterior.

## Codex CLI

Fontes oficiais: [CLI](https://learn.chatgpt.com/docs/codex/cli),
[autenticação](https://learn.chatgpt.com/docs/auth),
[AGENTS](https://learn.chatgpt.com/docs/agent-configuration/agents-md) e
[skills](https://learn.chatgpt.com/docs/build-skills).

Uma opção oficial para Linux é o instalador standalone. Para revisá-lo antes de
executar, baixe-o para um arquivo temporário; não é instalação do StackNauta:

```bash
STACKNAUTA_CODEX_INSTALLER="$(mktemp -t stacknauta-codex-installer-XXXXXX.sh)"
curl -fsSL https://chatgpt.com/codex/install.sh -o "$STACKNAUTA_CODEX_INSTALLER"
cat "$STACKNAUTA_CODEX_INSTALLER"
# Somente se o operador aprovou o instalador e seus efeitos:
sh "$STACKNAUTA_CODEX_INSTALLER"
```

Depois, na máquina que está sendo preparada:

```bash
command -v codex
codex --version
# Execute da raiz StackNauta:
codex
```

No primeiro acesso, complete o sign-in oferecido pelo CLI (ChatGPT ou outro método
permitido na conta), sem gravar credenciais no repositório. Respeite confiança e
permissões. AGENTS.md fornece instruções de projeto; **não use /init para
substituir o arquivo existente**. Confira a skill project-bootstrap disponível na
sessão e invoque `$project-bootstrap` no prompt, ou peça sua consulta nominal.
Use o [primeiro prompt](PRIMEIROS-PASSOS.md); confirme leitura integral e launcher.

## OpenCode

Fontes: [instalação](https://opencode.ai/docs/),
[provedores](https://opencode.ai/docs/providers/),
[instruções](https://opencode.ai/docs/instructions/) e
[skills](https://opencode.ai/docs/skills/).

A documentação consultada apresenta OpenCode V2. Uma opção é o instalador oficial;
o fluxo de revisão abaixo equivale a baixar antes de executar:

```bash
STACKNAUTA_OPENCODE_INSTALLER="$(mktemp -t stacknauta-opencode-installer-XXXXXX.sh)"
curl -fsSL https://opencode.ai/v2/install -o "$STACKNAUTA_OPENCODE_INSTALLER"
cat "$STACKNAUTA_OPENCODE_INSTALLER"
# Somente após decisão explícita do operador:
bash "$STACKNAUTA_OPENCODE_INSTALLER"
```

A fonte também oferece `npm install -g @opencode/cli`, como **alternativa** com
Node/npm preparados; não execute ambas nem substitua uma instalação já usada.
Não é necessário instalar npm para usar o método standalone.

```bash
command -v opencode
opencode --version
# Execute da raiz StackNauta:
opencode
```

Se já está autenticado e com modelo/provedor escolhido, preserve-os. Para uma
configuração nova, no cliente execute `/connect`, selecione um provedor autorizado
e faça sua autenticação; depois `/models` permite escolher um modelo disponível.
DeepSeek é uma opção do histórico validado, **não é a única opção nem uma exigência
do núcleo**. Não altere o provedor para obedecer a uma sugestão de instalação.

AGENTS.md é reconhecido e `.agents/skills/` é uma fonte compatível. Confira
project-bootstrap no catálogo disponibilizado ao agente e peça explicitamente
seu uso. A referência `@project-bootstrap`, quando disponível na versão/interface,
também pode ser usada; a evidência necessária é a leitura real pela ferramenta
de skills. O [primeiro prompt](PRIMEIROS-PASSOS.md) preserva modelo/provedor.

## Gemini via Antigravity CLI (`agy`)

Fontes: [instalação](https://antigravity.google/docs/getting-started),
[autenticação](https://antigravity.google/docs/install/),
[modelos](https://antigravity.google/docs/models/),
[skills](https://antigravity.google/docs/skills),
[descoberta](https://antigravity.google/docs/customization-discovery).

Use o cliente Antigravity, cujo executável é **agy**. O procedimento oficial Linux
oferece instalador shell; revisão manual antes da execução:

```bash
STACKNAUTA_AGY_INSTALLER="$(mktemp -t stacknauta-agy-installer-XXXXXX.sh)"
curl -fsSL https://antigravity.google/cli/install.sh -o "$STACKNAUTA_AGY_INSTALLER"
cat "$STACKNAUTA_AGY_INSTALLER"
# Somente após decisão explícita do operador:
bash "$STACKNAUTA_AGY_INSTALLER"
```

O destino padrão documentado é ~/.local/bin/agy. Reabra o terminal se necessário:

```bash
command -v agy
agy --version
# Execute da raiz StackNauta:
agy
```

Complete a configuração inicial, autentique a conta Google aprovada pelo fluxo
oferecido e revise a confiança do workspace específico. O CLI pode reutilizar uma
sessão válida no keyring; sem ela, oferece autenticação pelo navegador. Ambientes
empresariais/remotos podem precisar dos passos específicos da fonte oficial.
Não é necessário configurar chave de API para o fluxo interativo padrão.

Escolha um **modelo Gemini disponível na conta** no seletor ou `/model`. Registre
o nome e versão do cliente, sem fixar um modelo comercial que pode mudar de nome
ou disponibilidade. Não selecione orquestração/subagentes para validar este fluxo.
Confira AGENTS.md e `/skills`; project-bootstrap deve aparecer no workspace.
Peça o primeiro planejamento nominalmente. Não exija GEMINI.md ou imports do
cliente convencional; ambos foram retirados do fluxo operacional do StackNauta.

## Host e sandbox são ambientes diferentes

Compare os diagnósticos seguros do [guia Linux](INSTALACAO-LINUX.md) no terminal
habitual e no ambiente onde o agente executa comandos. Ter shims no PATH não
garante que o diretório esteja visível no sandbox. A 2G registrou invisibilidade
dos diretórios globais asdf; isolamento de filesystem é **causa provável**, não
defeito definitivamente comprovado do StackNauta nem problema resolvido nesta etapa.

Não desabilite proteções como solução padrão, nem use Python/Node de sistema como
fallback. Registre os caminhos/operações negados e solicite avaliação do operador
pelas permissões nativas. Sem runtime global acessível, o bootstrap deve bloquear.
Autenticação do cliente também não garante acesso a todos os arquivos ou recursos.
