# StackNauta

**Etapa 1.5 — biblioteca versionada para cópia física.** São 101 skills aprovadas em nove pacotes autocontidos, 21 pendentes e duas excluídas. O `project-bootstrap` continua sem implementação. Nenhuma skill foi ativada em agentes ou em projetos consumidores.

## Organização

```text
StackNauta/
├── Automacao/
│   ├── project-bootstrap/.gitkeep
│   └── validacao-project-bootstrap/.gitkeep
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
├── .agents/skills/.gitkeep
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

A unidade autocontida é o pacote de origem/categoria. É possível copiar o pacote inteiro ou o conjunto fechado de uma skill. Para selecionar, usar o campo `distribution` de [catalogo.json](Skills/catalogo.json): `package`, `skill_directory` e `requires_skills`. `biblioteca.selected_files()` calcula esse fechamento transitivo e inclui os recursos comuns/licenças. Manter os caminhos relativos `skills/<nome>/` e os arquivos compartilhados do pacote. O mecanismo não configura agentes nem cria aplicações; ele é um contrato de dados para o bootstrap futuro.

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

[MANUTENCAO.md](Skills/manutencao/MANUTENCAO.md) descreve a preparação reproduzível e a atualização manual planejada. Não há aquisição/restauração automática nem atualização durante consumo. O cache pode ser necessário para uma nova preparação, mas não para copiar, validar ou usar os pacotes aprovados.

A Etapa 2 poderá implementar uma única lógica de bootstrap com adaptações para Codex, OpenCode com DeepSeek e Gemini CLI. Ela deverá preparar somente o esqueleto inicial e os conjuntos compatíveis selecionados, copiar recursos fisicamente e validar todos os runtimes globais asdf antes de escrever no destino. Desenvolvimento da aplicação começa depois.
