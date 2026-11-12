# StackNauta

**Etapa 3A — atualização manual das skills.** Consulta das sete origens e preparação isolada de atualizações, com revisão de diff, hash e autorização explícita antes de promover. A biblioteca aprovada permanece na revisão anterior; nenhuma atualização real foi aplicada nesta etapa. OpenCode/DeepSeek e Gemini CLI continuam pendentes de validação prática. Não certificado para produção.

```sh
./Automacao/manutencao-skills/skills check
./Automacao/manutencao-skills/skills update expo
./Automacao/manutencao-skills/skills update --all
# Os dois últimos comandos apenas preparam o dry-run.
```

Consulte [uso, segurança e recuperação](Automacao/manutencao-skills/README.md)
e o [relatório 3A](Automacao/validacao-atualizacoes/RELATORIO.md). Novas skills
permanecem pendentes. A atualização não modifica consumidores e não é executada
durante o bootstrap.

O núcleo prepara esqueleto, runtimes globais asdf e cópias físicas de skills
compatíveis. Arquivos evolutivos podem mudar ou ser removidos após inicialização
sem sobrescritas; manifestos, runtimes registrados e skills continuam protegidos.

Consulte a [política de arquivos e compatibilidade](Automacao/project-bootstrap/CICLO-DE-VIDA.md)
e o [relatório 2D](Automacao/validacao-ciclo-arquivos/RELATORIO.md). Novos projetos
usam manifesto schema 2 e marcador final de inicialização. Projetos schema 1
continuam reconhecidos sem migração nem reescrita. Conteúdo originalmente gerado
e hashes são preservados para rastreabilidade; não se atualizam para aceitar edições.

A biblioteca 1.5 permanece preservada: 101 skills aprovadas em nove pacotes, 21 pendentes e duas excluídas. Nenhum projeto consumidor antigo ou configuração global de agentes foi modificado.

## Núcleo do bootstrap

```bash
./Automacao/project-bootstrap/project-bootstrap agent-plan --config Automacao/project-bootstrap/examples/python-fastapi.json
# Revisar arquivos, hashes e autorização antes da aplicação.
./Automacao/project-bootstrap/project-bootstrap agent-apply --config Automacao/project-bootstrap/examples/python-fastapi.json --plan-id HASH_REVISADO
./Automacao/project-bootstrap/project-bootstrap agent-verify --config Automacao/project-bootstrap/examples/python-fastapi.json
```

O dry-run valida entradas, runtimes globais, compatibilidade de todo o fechamento e o destino antes de escrever. O destino padrão é `$HOME/Projetos/<name>`, com destino absoluto explicitamente configurável. A aplicação exige o hash revisado e não sobrescreve arquivos existentes. Não há geradores, instalação de dependências ou início de serviços automáticos.

Ver [integração compartilhada e exemplos](Automacao/integracao-agentes/README.md), [relatório da Etapa 2B](Automacao/validacao-integracao-agentes/RELATORIO.md) e [testes manuais posteriores](Automacao/integracao-agentes/TESTES-MANUAIS.md). A [interface original](Automacao/project-bootstrap/README.md), os [testes da Etapa 2A](Automacao/validacao-project-bootstrap/README.md) e STATUS.json preservam o contrato e estado histórico 2A; o catálogo continua descrevendo a biblioteca 1.5.

## Organização

```text
StackNauta/
├── Automacao/
│   ├── project-bootstrap/           # launcher, CLI, núcleo e exemplos
│   ├── validacao-project-bootstrap/ # testes originais preservados
│   ├── integracao-agentes/          # procedimento comum e testes manuais
│   ├── manutencao-skills/           # consulta, preparação, promoção e recuperação
│   ├── validacao-atualizacoes/      # fixtures Git e evidências 3A
│   ├── python-global               # executor asdf compartilhado pelos launchers
│   ├── validacao-ciclo-arquivos/    # investigação, compatibilidade e evidências 2D
│   └── validacao-integracao-agentes/ # testes 2B e evidências
├── Skills/
│   ├── Frontend/ui-ux-pro-max/
│   ├── Backend/{fastapi,remy,sentry}/
│   ├── Mobile/{expo,chrisbanes,android}/
│   ├── Seguranca/{android,sentry}/
│   ├── manutencao/                 # política, renderer e empacotador
│   ├── validacao/                  # validadores, auditorias e relatórios
│   ├── _repos/                     # cache opcional, ignorado pelo Git
│   ├── catalogo.json
│   └── fontes.lock.json
├── .agents/skills/project-bootstrap/SKILL.md
├── AGENTS.md
├── GEMINI.md                       # importa AGENTS.md
└── README.md
```

Cada pacote contém `skills/<nome>/`, licença(s) comuns, README de consumo e `PROVENANCE.json`. O manifesto registra cada arquivo, hash SHA-256, commit/caminho original e adaptações. Pastas de categoria mantêm índices de aprovadas e impedimentos. Fontes de terceiros permanecem intactas no cache.

| Categoria | Skills aprovadas |
|---|---:|
| Frontend | 4 |
| Backend | 19 |
| Mobile | 71 |
| Seguranca | 7 |

As 124 skills distintas vêm de 130 arquivos SKILL.md adquiridos: seis são cópias de distribuição UI/UX, sem contagem duplicada. Duas exclusões são o avaliador interno Expo e o plugin experimental Expo. A justificativa individual das outras 21 está em [PENDENCIAS.md](Skills/validacao/PENDENCIAS.md) e no catálogo.

## Consumo físico

Os pacotes e seus recursos são rastreados pelo Git principal. Uma clonagem local limpa contém a biblioteca completa aprovada **sem depender de `_repos/`**, de ferramentas globais novas ou de download durante o consumo. O repositório principal não tem remoto configurado e nada foi publicado.

A unidade autocontida é o pacote de origem/categoria. É possível copiar o pacote inteiro ou o conjunto fechado de uma skill. Para selecionar, usar o campo `distribution` de [catalogo.json](Skills/catalogo.json): `package`, `skill_directory` e `requires_skills`. `biblioteca.selected_files()` calcula esse fechamento transitivo e inclui os recursos comuns/licenças. O núcleo 2A reutiliza essa função e preserva o layout em namespaces sob `.agents/skills/`. Ele não altera os arquivos aprovados nem configura integrações específicas de agentes.

Skills com referências entre si são copiadas juntas quando necessárias. A família Expo inclui o router e as 23 skills estáveis no fechamento, seguindo o contrato do fornecedor. Licenças e recursos comuns são armazenados uma vez por pacote; não há links simbólicos, hardlinks de consumidores ou referências obrigatórias ao cache. O índice de proveniência completo pode descrever skills não selecionadas numa cópia parcial; validar essa cópia contra o plano selecionado, não exigir todos os arquivos do índice de pacote completo.

Antes de usar comandos das skills, ler o README do pacote. Os runtimes devem ser as versões globais instaladas do asdf, com caminho absoluto verificado. Ausência/override local deve interromper a operação; não usar runtime do sistema nem instalar ferramentas automaticamente. SDKs, CLIs autenticadas e hardware do consumidor são pré-requisitos de execução, não recursos que a biblioteca fornece ou autorização para instalá-los.

## Fontes fixadas

As revisões da Etapa 1 foram preservadas integralmente; não houve fetch ou atualização silenciosa na Etapa 1.5. A tabela mostra a contagem adquirida, incluindo entradas pendentes/excluídas, não apenas aprovadas.

| Origem | Branch padrão/adquirida | Commit completo | Skills distintas |
|---|---|---|---:|
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | main | `6ae86f61f520d6ca229d2f40e070410638c908c5` | 7 |
| [FastAPI](https://github.com/fastapi/fastapi) | master | `5add7a458d629b07311d48261f696b5ac2bb9a5f` | 1 |
| [Remy349](https://github.com/Remy349/skills) | main | `5d9eae132afea72518ba0f1f41919f9e37964362` | 3 |
| [Expo](https://github.com/expo/skills) | main | `a9e5bd3fa00b4e61f632e43f85da73aee1942582` | 25 |
| [Chris Banes](https://github.com/chrisbanes/skills) | main | `50d54366e577460b769ce05b50da007de9939783` | 21 |
| [Android](https://github.com/android/skills) | main | `5815d27fda564aa9f07ebdcb5e57ed3e8d904e0d` | 36 |
| [Sentry](https://github.com/getsentry/skills) | main | `e94f22214528d69899d09c627b3315ddc3544816` | 31 |

## UI/UX Pro Max e adaptações

O orquestrador `ui-ux-pro-max` foi renderizado a partir do template oficial `universal`, com renderer Python da biblioteca padrão. A saída anterior às adaptações foi comparada byte a byte à função oficial `renderSkillFile` nas configurações universal, Codex, OpenCode e Gemini: todas idênticas. Nenhuma CLI de instalação, build, dependência npm/Bun ou atualização global foi usada.

O pacote inclui os dados/scripts oficiais completos do orquestrador, referências, `banner-design`, `brand`, `ui-styling`, fontes de canvas e suas 27 licenças OFL. O único helper de tokens exigido por `brand` foi incluído como recurso compartilhado, sem criar SKILL.md para `design-system`. Os fluxos completos `design-system`, `slides` e `design` continuam pendentes porque a origem referencia assets de slides não fornecidos e fluxos dependentes. Nenhum asset foi fabricado.

Toda skill aprovada recebeu um contrato explícito de execução/cópia. Correções pontuais incluem caminhos de licença compartilhada, a referência Expo iOS, a rota Expo ausente, cópia física de entrypoints em `agents-md` e herança do executável Node no helper `brand`. Ver [adaptacoes.json](Skills/validacao/adaptacoes.json) para os diffs completos e [DISTRIBUICAO.md](Skills/validacao/DISTRIBUICAO.md) para escopo e limites.

## Validação

Executar a partir da raiz, com Python global asdf instalado:

```bash
asdf exec python Skills/validacao/validar_catalogo.py
asdf exec python Skills/validacao/validar_biblioteca.py --copias --sintaxe-node
```

O primeiro comando valida offline a distribuição e não exige cache. O segundo testa os planos de cópia física de todas as 101 skills, verifica sintaxe JS sem executar os scripts e faz buscas locais UI/UX previamente analisadas, sem persistir design systems ou criar aplicações. As cópias ficam em diretórios temporários novos. Nenhum projeto existente é usado como destino.

Para conferir também as sete origens locais:

```bash
asdf exec python Skills/validacao/validar_biblioteca.py --origens
```

Para repetir a clonagem local, primeiro manter um commit com árvore limpa e então executar:

```bash
asdf exec python Skills/validacao/testar_clone.py
```

O teste imprime o relatório sem escrever no Git principal; o origin local criado automaticamente pelo clone é removido no repositório temporário. Nenhum remoto é adicionado ao StackNauta original.

Os relatórios estão em [resultado.json](Skills/validacao/resultado.json), [clone-local.json](Skills/validacao/clone-local.json), [renderizacao-ui.json](Skills/validacao/renderizacao-ui.json) e [preservacao-etapa15.json](Skills/validacao/preservacao-etapa15.json). `arquivos.json` e `recursos.json` preservam o inventário de aquisição; [revisao-recursos.json](Skills/validacao/revisao-recursos.json) classifica as 28 menções antes não resolvidas. O relatório de preservação original da Etapa 1 continua disponível.

A aprovação cobre integridade, fechamento dos arquivos, licenças, cópia e funcionamento das buscas UI/UX testadas. Não certifica todos os scripts/fluxos de fornecedores, descoberta nos agentes ou execução de SDKs, autenticação e hardware. Frontmatter tem conferência estrutural básica e de licença, sem dependência PyYAML nova.

## Manutenção e próxima etapa

[MANUTENCAO.md](Skills/manutencao/MANUTENCAO.md) descreve a preparação histórica e
a atualização incremental manual da Etapa 3A. Não há atualização durante consumo.
O cache pode ser necessário para a preparação histórica, mas a CLI 3A adquire
candidatos isoladamente e o consumo continua independente de `_repos/`.

A Etapa 2A implementa a lógica única de esqueleto e seleção, preservada na 2B e
evoluída pela política de arquivos 2D. Na 3A, o mesmo executor asdf do launcher foi
extraído para reutilização na manutenção, sem alteração da lógica do núcleo.
A skill orienta o agente a revisar dois hashes e as duas listas de arquivos,
aplicar somente quando autorizado e interpretar operações tecnológicas pendentes.
A integração não concede autorização nem executa geradores.

Os aliases rasos `stacknauta-*` encaminham aos SKILL.md originais copiados fisicamente, preservando recursos e licenças sem duplicação. A descoberta nativa e o uso explícito no Codex atual têm evidências separadas; ativação automática numa nova sessão continua uma confirmação posterior. OpenCode/DeepSeek e Gemini CLI estão preparados estaticamente, sem aprovação prática nesta etapa.
