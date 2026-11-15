# Primeiro projeto e início do desenvolvimento

[README](../README.md) · [Linux](INSTALACAO-LINUX.md) · [Agentes](AGENTES.md) · [Validação](VALIDACAO.md) · [Problemas](SOLUCAO-DE-PROBLEMAS.md)

Use uma cópia confiável, runtimes preparados e um destino novo. Este guia usa um
portal fictício, sem clientes reais. A entrada JSON está em
[exemplos/portal-web.json](exemplos/portal-web.json). React e TypeScript são
tecnologias declaradas, mas suas versões/toolchain ficam pendentes: o bootstrap
prepara um esqueleto, não uma aplicação executável.

## 1. Primeiro prompt: preparação, inicialmente só plano

Abra um dos [agentes](AGENTES.md) na raiz StackNauta. Exemplo de pedido:

```text
Use a skill project-bootstrap para planejar portal-astronomia-demo num destino novo que eu indicar.
Objetivo: interface web responsiva do portal fictício Arquivo das Estrelas, com cabeçalho, navegação, hero, introdução, três destaques educativos e rodapé.
Linguagem TypeScript, framework React, alvo web, feature ui.
Selecione nominalmente ui-ux-pro-max:ui-ux-pro-max e gh-anthropics-skills:frontend-design.
Preserve meu provedor/modelo atual. Não escolha arquitetura nem versões de framework ou compilador.
Não instale dependências, execute geradores ou serviços, use APIs ou baixe fontes/assets externos.
Use somente runtimes globais instalados do asdf. Preserve requisitos, decisões e arquivos gerenciados.
Mostre o plano completo e as pendências; aguarde minha autorização antes de aplicar.
```

Substitua “destino ... indicar” por um caminho novo com pai existente, ou aceite
explicitamente o padrão `$HOME/Projetos/<name>`. No Codex, `$project-bootstrap`
pode invocar a skill. Não basta o modelo declarar que a usou: confira leitura e
invocação real do launcher oficial.

A lista `skills` define as **raízes solicitadas**, sujeitas à compatibilidade,
sem sugestões automáticas complementares. Dependências transitivas obrigatórias
podem ampliar o fechamento e precisam aparecer no plano. `skills: []` desabilita
seleção; omitir skills habilita a seleção automática determinística, não equivale
a uma lista explícita. Skills marcadas explicit exigem escolha nominal; não são
adicionadas só por afinidade. [Contrato de seleção](../Automacao/project-bootstrap/SELECAO.md).

Features precisam usar tags suportadas, como `ui`. Não há campo JSON `target`:
o alvo web é declarado em description/constraints. Não acrescente chaves inventadas.
Arquitetura omitida continua sem escolha. Versões omitidas ficam pendentes para
operações tecnológicas posteriores, não são substituídas por latest.

## 2. Fluxo técnico equivalente e reproduzível

Os passos abaixo também podem ser executados diretamente no terminal, sem iniciar
agentes. Execute da raiz StackNauta. Usam apenas o launcher oficial e Python global
asdf. O diretório de trabalho temporário guarda pedido/evidências fora do consumidor:

```bash
# bloco: preparar-pedido
STACKNAUTA_DIR="$(pwd -P)"
STACKNAUTA_WORK="$(mktemp -d -t stacknauta-primeiro-uso-XXXXXX)"
bash "$STACKNAUTA_DIR/Automacao/python-global" - "$STACKNAUTA_DIR" "$STACKNAUTA_WORK" <<'PY'
import json, sys
from pathlib import Path
repo, work = map(Path, sys.argv[1:])
request = json.loads((repo / 'Documentacao/exemplos/portal-web.json').read_text())
request['destination'] = str(work / request['name'])
(work / 'pedido.json').write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
print(work / request['name'])
PY
```

É uma cópia declarativa do exemplo com destino novo; não implementa outra CLI.
Não altere a configuração entre revisão e aplicação. Para um destino permanente,
escolha-o antes do plano. Não reutilize um destino histórico de teste.

```bash
# bloco: planejar
"$STACKNAUTA_DIR/Automacao/project-bootstrap/project-bootstrap" agent-plan --config "$STACKNAUTA_WORK/pedido.json" > "$STACKNAUTA_WORK/plano.json"
cat "$STACKNAUTA_WORK/plano.json"
```

O agent-plan é dry-run: não cria o consumidor. Revise **todo** o JSON:

| Campo | O que conferir |
|---|---|
| config / agent_plan | Tecnologias, alvo, requisitos, restrições e arquitetura não inferida |
| runtimes / runtime_resolution | Versões globais instaladas e executáveis físicos; caminhos de diagnóstico são locais |
| skills.roots / selected / skipped | Duas raízes explícitas, fechamento e omissões justificadas |
| files / integration_files | Destinos relativos, recursos, hashes, classificação e ação |
| core_plan_id / plan_id | Hashes do núcleo e integração; a aplicação agent-* usa **plan_id** |
| agent_plan.tasks | Versão de React/compilador e operações ainda pendentes, sem execução |

Para a configuração exata do exemplo, esperam-se as duas skills, nenhuma adicional,
97 arquivos do núcleo e quatro de integração. O hash varia com destino/configuração;
nunca copie um hash de relatório antigo para aplicar outro plano.

## 3. Autorização e aplicação

No fluxo conversacional, só depois da revisão informe algo como:

```text
Autorizo aplicar exatamente o plano revisado para o destino informado, usando seu plan_id de integração. Não autorizo instalações, geradores, serviços ou implementação funcional.
```

O operador deve ter essa autorização também ao usar o terminal. Hash e
agent-plan.json não a concedem. Com o hash integral do **agent-plan** revisado:

```bash
# bloco: aplicar-autorizado
read -r -p 'Cole o plan_id integral revisado e autorizado: ' STACKNAUTA_PLAN_ID
"$STACKNAUTA_DIR/Automacao/project-bootstrap/project-bootstrap" agent-apply --config "$STACKNAUTA_WORK/pedido.json" --plan-id "$STACKNAUTA_PLAN_ID" > "$STACKNAUTA_WORK/aplicacao.json"
cat "$STACKNAUTA_WORK/aplicacao.json"
```

A CLI revalida o plano e recusa hash divergente. Incompatibilidade explícita,
recurso faltante, runtime ausente ou conflito bloqueiam antes de sobrescritas.
Não use force, não regenere hashes para encobrir problemas e não instale fallback.
Interrupções preservam arquivos; reaplicar o mesmo plano autorizado pode completar
ausências de inicialização, conforme o [ciclo de vida](../Automacao/project-bootstrap/CICLO-DE-VIDA.md).

## 4. Verificação e estrutura esperada

```bash
# bloco: verificar
"$STACKNAUTA_DIR/Automacao/project-bootstrap/project-bootstrap" agent-verify --config "$STACKNAUTA_WORK/pedido.json" > "$STACKNAUTA_WORK/verificacao.json"
cat "$STACKNAUTA_WORK/verificacao.json"
```

| Resultado | Interpretação |
|---|---|
| status verified, verification_state intact | Estrutura e conteúdo inicial conferidos |
| verified_with_evolution | Modificações/remoções permitidas, detalhadas em lifecycle e integration_lifecycle |
| modified / removed | Evolução relatada; não implica restauração ou validade semântica da aplicação |
| blocked, exit 2 ou erro | Ler stderr; resolver requisito/conflito sem adulterar manifests |

AGENTS/README/configurações de aplicação são evolutivos quando gerados; manifests,
locks, `.tool-versions` e `.agents/skills/` são protegidos. O contrato complementar
também é protegido. Ausência/alteração protegida bloqueia. Adicionais legítimos
em src/tests podem ser relatados; arquivos extras nas áreas protegidas são recusados.

```text
portal-astronomia-demo/
├── AGENTS.md
├── .tool-versions
├── package.json                 # dependencies vazias, sem scripts de build
├── tsconfig.json
├── docs/REQUIREMENTS.json
├── src/.gitkeep
├── tests/.gitkeep
├── .agents/skills/
│   ├── README.md
│   ├── stacknauta-ui-ux-pro-max/SKILL.md
│   ├── stacknauta-frontend-design/SKILL.md
│   ├── frontend-ui-ux-pro-max/...        # originais, recursos, licença
│   └── frontend-gh-anthropics-skills/... # original, licença e proveniência
└── .stacknauta/
    ├── AGENT-INTEGRATION.md
    ├── agent-integration.json
    ├── agent-plan.json
    ├── config.json
    ├── manifest.json
    ├── bootstrap-complete.json
    └── skills-lock.json
```

São cópias físicas; o alias manda ler o SKILL.md original e resolver scripts/dados
a partir dele. Não há GEMINI.md, node_modules ou aplicação React implementada.
Verified não é build, teste funcional, ativação de skill ou certificação de produção.

## 5. Segundo prompt: desenvolvimento no consumidor

No caminho impresso no passo 2, abra **manualmente** uma nova sessão do agente
escolhido. Não abra outra sessão no StackNauta para editar a aplicação por engano.
Confirme AGENTS.md, catálogo nativo e consulta pertinente ao contrato/skills.
Exemplo de segundo prompt:

```text
Desenvolva a estrutura de uma página inicial responsiva para o portal fictício Arquivo das Estrelas, com cabeçalho, navegação, hero, introdução, três destaques educativos e rodapé.
Use React e TypeScript, preserve os requisitos e decisões existentes e priorize acessibilidade, legibilidade e organização visual.
Não instale dependências nem use serviços externos. Se a aplicação não puder ser executada sem configurar a toolchain, informe a limitação e proponha o plano para minha aprovação.
```

O primeiro prompt preparou o projeto; o segundo autoriza desenvolvimento dentro
das restrições. A consulta das skills depende da tarefa e da descoberta do cliente,
não é ativação automática garantida. Confira encaminhadores, originais e recursos
lidos. Requisitos e decisões aprovadas prevalecem sobre sugestões.

Para tornar o app executável posteriormente, escolha versões concretas de React,
compilador e bundler, revise comandos, acesso à rede e instalação e autorize-os
separadamente. Não presuma Vite, Next.js, scripts npm ou serviços já fornecidos.
Depois do desenvolvimento, execute as verificações da stack e agent-verify;
integridade do esqueleto não substitui esses testes.
