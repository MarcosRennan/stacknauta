# StackNauta

O StackNauta prepara esqueletos a partir de tecnologias, requisitos e skills
explicitamente declarados. Confere runtimes globais do asdf, copia skills e
recursos físicos e registra manifests e locks. Não instala dependências, executa
geradores, inicia serviços ou implementa negócio.

Ambientes suportados: **Codex CLI, OpenCode e Gemini via Antigravity CLI (`agy`)**.
Todos usam `AGENTS.md`, `.agents/skills/` e o contrato complementar
`.stacknauta/AGENT-INTEGRATION.md` do consumidor. Novos consumidores não dependem
de GEMINI.md. Distribuir uma skill não comprova sua consulta pelo agente.

## Comece aqui

| Guia | Finalidade |
|---|---|
| [Instalação Linux](Documentacao/INSTALACAO-LINUX.md) | Fedora, asdf, runtimes e acesso futuro por SSH |
| [Agentes](Documentacao/AGENTES.md) | Instalação e autenticação independentes de cada cliente |
| [Primeiros passos](Documentacao/PRIMEIROS-PASSOS.md) | Primeiro prompt, plano, autorização, aplicação e segundo prompt |
| [Validação](Documentacao/VALIDACAO.md) | Ambiente, biblioteca, scripts, regressão e consumidor |
| [Solução de problemas](Documentacao/SOLUCAO-DE-PROBLEMAS.md) | asdf, sandbox, Git, seleção, recursos e manifests |

## Estado consolidado

**105 aprovadas, 27 pendentes, duas excluídas, nove origens e onze pacotes.**
O [catálogo](Skills/catalogo.json) e o [lock de origens](Skills/fontes.lock.json)
são as fontes de verdade de revisões e distribuição.

| Categoria | Skills aprovadas |
|---|---:|
| Frontend | 8 |
| Backend | 19 |
| Mobile | 71 |
| Segurança | 7 |

A 4B validou comportamento dos três agentes conforme evidências aceitas pelo
usuário; a regressão consolidada da 2H tem 303 testes. A 4C testa uma **simulação
local**, não uma instalação em outro computador. Não há certificação de produção
ou de todos os workflows das skills. Nenhuma URL GitHub publicada foi confirmada.

## Pré-requisitos e instalação rápida

Linux com os recursos de filesystem do guia, Bash, coreutils/readlink, asdf e
**Python global instalado >=3.11**. Node global é necessário para JS/TS, determinados
helpers e parsing JS dos validadores. Baseline testada: Fedora 44 x86_64, asdf
0.20.2, Python 3.14.8 e Node 24.21.0; versões observadas não são mínimos universais.
Git é necessário para obter o clone, validá-lo e executar os testes.
React, TypeScript e bundlers não precisam ser instalados globalmente.

Não há instalador próprio, pip install ou npm install obrigatório para o núcleo.
Prepare o ambiente conforme o [guia Linux](Documentacao/INSTALACAO-LINUX.md), obtenha
uma cópia versionada confiável e execute da raiz:

```bash
asdf --version
asdf current
./Automacao/project-bootstrap/project-bootstrap --help
bash Automacao/python-global Skills/validacao/validar_biblioteca.py --copias --sintaxe-node --sem-smoke-fornecedor
```

## Primeiro uso

Abra um agente escolhido na raiz StackNauta. Declare linguagem, framework, alvo,
features, skills nominais e restrições; peça apenas planejamento inicialmente.
Revise requisitos, seleção/omissões, recursos, arquivos, runtimes, core_plan_id,
plan_id e pendências. Autorize o plano concreto: **hash não é autorização**.

O [exemplo React/TypeScript completo](Documentacao/PRIMEIROS-PASSOS.md) usa o
[pedido versionado](Documentacao/exemplos/portal-web.json), UI/UX Pro Max e Frontend
Design explícitas. A CLI real oferece agent-plan, agent-apply e agent-verify:

`/tmp/pedido-stacknauta.json` abaixo é um **placeholder**, não um arquivo criado
pelo clone. Crie primeiro sua configuração: o [guia de primeiros passos](Documentacao/PRIMEIROS-PASSOS.md)
contém o procedimento reproduzível para gerar o pedido a partir do exemplo versionado.
Use o caminho do pedido efetivamente criado nos três comandos.

```bash
# Prepare esse pedido fora do destino, conforme o guia de primeiros passos.
./Automacao/project-bootstrap/project-bootstrap agent-plan --config /tmp/pedido-stacknauta.json
# Somente depois da revisão e autorização; use plan_id, não core_plan_id.
read -r -p 'plan_id revisado e autorizado: ' STACKNAUTA_PLAN_ID
./Automacao/project-bootstrap/project-bootstrap agent-apply --config /tmp/pedido-stacknauta.json --plan-id "$STACKNAUTA_PLAN_ID"
./Automacao/project-bootstrap/project-bootstrap agent-verify --config /tmp/pedido-stacknauta.json
```

O desenvolvimento começa em nova sessão no consumidor verificado. O esqueleto
React não possui bundler, dependências instaladas ou scripts de build. Versões e
operações tecnológicas pendentes exigem decisão e autorização próprias.

## Contratos e rastreabilidade

- [Entrada e CLI](Automacao/project-bootstrap/README.md), [seleção explícita](Automacao/project-bootstrap/SELECAO.md), [ciclo de vida](Automacao/project-bootstrap/CICLO-DE-VIDA.md) e [integração](Automacao/integracao-agentes/README.md).
- [Distribuição e execução das skills](Skills/validacao/DISTRIBUICAO.md): consulte o README do pacote e o SKILL.md original antes de executar recursos de fornecedor.
- [Manutenção](Automacao/manutencao-skills/README.md) e [inclusão](Automacao/manutencao-skills/INCLUSAO.md) são fluxos separados que podem exigir rede e revisão; não fazem parte do bootstrap.
- [Relatórios históricos de integração](Automacao/validacao-integracao-agentes/RELATORIO.md), [ciclo de vida](Automacao/validacao-ciclo-arquivos/RELATORIO.md) e [inclusões](Automacao/validacao-inclusoes/RELATORIO.md): seus números refletem aquelas etapas, não o catálogo atual.

Os pacotes são versionados; consumo não depende de Skills/_repos, caches ignorados
ou relatórios locais. Não edite arquivos protegidos/hashes para aceitar conflitos.
Manifestos vinculam configuração e destino: relocação de consumidores e verificação
com geradores diferentes não são migrações automáticas.
