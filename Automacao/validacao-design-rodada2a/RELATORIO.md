# Etapa 4B — Rodada 2A: design e interfaces

Análise realizada em 13/11/2026. **Recomenda-se preparar somente Frontend Design
para uma futura decisão de incorporação, sempre por seleção explícita.** As três
candidatas Vercel têm valor funcional, mas permanecem pendentes por impedimentos
verificáveis. Impeccable permanece pendente por aquisição incompleta e necessidade
de análise específica. Nenhuma decisão de aprovação ou plano foi emitido.

## Baseline, escopo e integridade

HEAD inicial/final: `56b33bdfaac4a5e06c16418fface2611a52b7b24`. Git inicialmente
limpo. Foram lidos AGENTS.md, contratos de inclusão, seleção e manutenção e a
sintaxe real da CLI. A manutenção deste repositório não é inicialização de uma
aplicação; nenhum consumidor foi criado ou utilizado como fixture.

O validador existente passou no início e no fim, com pendências documentadas e
zero erros: **104 aprovadas, 27 pendentes, duas excluídas, oito origens e dez
pacotes**. Catálogo, locks, licenças, recursos e proveniência ativos permanecem
íntegros. A comparação dos hashes e modos dos **1.140 arquivos rastreados** não
encontrou alteração. Nenhuma fonte/skill solicitada já existia no catálogo; não
foram encontrados conflitos de nomes ou duplicatas de conteúdo nas candidatas.

O cache legado no backup da sessão `55d27dfc7feb4ee6848c2fcdd1974295` não foi
alterado ou limpo; seu SHA-256 continua
`5528002f2695efbd10807980a21f7dafda908178dec192aa14995eafc7b4afcf`.
Permanece a ressalva de recuperação manual documentada na Rodada 1D.3.

## Aquisições e revisões oficiais

Foram usados exclusivamente `skills add` e `skills review SESSION`, sem arquivo
de decisões. A aquisição materializa somente os caminhos escolhidos e arquivos
comuns da raiz/licenças ancestrais. O fetch Git ainda precisa dos objetos da
revisão: escopo esparso não garante um download pequeno.

| Fonte/escopo | Commit adquirido | Sessão | Review ID |
|---|---|---|---|
| Anthropic — `skills/frontend-design` | `2c5958ecac7cee2b583967a2c4981d0f4a75c579` | `78ab56b987824743915bca34f29e1090` | `693c6aa1be23fc91c05b9c4ae988055965392dc343f775487cf8fa0812be1b3a` |
| Vercel — `skills/react-best-practices` | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | `15a4ed09501944f5afd066ca7d0c8c56` | `2a4faa86f5737e718e3aaf41209c5acd573f86cba69cae6022bf0a79a5d3a67a` |
| Vercel — `skills/web-design-guidelines` | Mesmo commit Vercel, aquisição fixada por `--ref` | `99a8d40b47164db99a6515a20baeec44` | `4ad90e93d743938dec17b6eca4603ac93565470fb7fe54c3a28d50a7b7f2e829` |
| Vercel — `skills/composition-patterns` | Mesmo commit Vercel, aquisição fixada por `--ref` | `d27b1dfb321f4f039971b3e4f900281a` | `311b001a4de650741ad58a3a86f16db6130b4e76e2f2dacfe17b6c492f8c0c02` |

Comandos de aquisição executados, a partir da raiz:

```sh
Automacao/manutencao-skills/skills add https://github.com/anthropics/skills/tree/main/skills/frontend-design
Automacao/manutencao-skills/skills add https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices
Automacao/manutencao-skills/skills add https://github.com/vercel-labs/agent-skills --ref 1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62 --path skills/web-design-guidelines
Automacao/manutencao-skills/skills add https://github.com/vercel-labs/agent-skills --ref 1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62 --path skills/composition-patterns
```

Cada revisão foi executada com a sessão da tabela. As primeiras consultas de
rede no sandbox falharam por DNS; os mesmos comandos oficiais foram repetidos
com permissão de rede. Não se usou outro downloader, empacotador ou checkout.

### Impeccable: impedimento preservado

`skills add https://github.com/pbakaus/impeccable --path skill` resolveu o commit
`c4cd1924c389f68d37c687d9c2bbf13f12547c41`, mas o fetch excedeu os 45 segundos
permitidos. Uma única segunda tentativa, com `--ref` nesse commit, falhou pelo
mesmo timeout. Sessões preservadas: `da38f3badc394fa7a18d46017a274141` e
`54f1b195847444ccb19145905b72fddb`. Não houve aquisição íntegra, inventário,
review ID, hash de SKILL.md ou confirmação do fechamento. O commit é o solicitado
ao fetch, **não uma revisão adquirida e validada**. Não se mudou timeout/código,
reutilizou pacote incompleto ou repetiu indefinidamente.

**Pendente.** A [página pública atual](https://github.com/pbakaus/impeccable#readme)
apresenta uma skill com comandos, além de CLI, engine, hooks e integrações.
`audit`, `critique` e `polish` não foram comprovados como skills independentes.
O README descreve arquivos PRODUCT.md/DESIGN.md, download de engine e acesso
a catálogo externo; o modo live pode iniciar agentes com permissões/sandbox
desativados. Apache-2.0 é declarado, mas não validado localmente. Essas observações
são preliminares de `main`, não auditadas no commit. Não se executou instalador.
Não recomendar distribuição do conjunto sem resolver aquisição, dependências e
segurança; eventual subconjunto de refinamento exige fechamento próprio comprovado.

## Classificação individual e recursos

Os nomes oficiais Vercel diferem dos nomes dos diretórios. Os IDs abaixo são os
efetivamente retornados pela CLI, não IDs inventados para o relatório.

| ID completo | Classificação proposta | Recursos físicos | Motivo principal |
|---|---|---:|---|
| `gh-anthropics-skills:frontend-design` | **Recomendada** | 2 | Exploração contextual com processo concreto; licença e fechamento sem bloqueios |
| `gh-vercel-labs-agent-skills:vercel-react-best-practices` | **Pendente** | 76 | Licença sem texto identificado e três referências locais quebradas |
| `gh-vercel-labs-agent-skills:web-design-guidelines` | **Pendente** | 1 | Licença e regras externas/portabilidade não resolvidas |
| `gh-vercel-labs-agent-skills:vercel-composition-patterns` | **Pendente** | 14 | Licença; revisão necessária do escopo de APIs React 19 nos exemplos |
| Impeccable — ID de candidata não emitido | **Pendente** | Não certificado | Aquisição incompleta; conjunto não certificado como portátil |

Nenhuma classificação desta tabela foi escrita no catálogo ou submetida como
decisão. Não há candidata adicional aprovada ou proposta de incorporação em lote.

### Frontend Design — exploração criativa

[Conteúdo fixado](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/frontend-design/SKILL.md).
Resolve a repetição estética por decisões fundamentadas no assunto, público e
trabalho principal da interface. Propõe plano compacto de tokens, tipografia,
layout e princípios; compara-o ao briefing antes de implementar e faz autocrítica,
com screenshots quando disponíveis. Não é um novo catálogo de estilos.

Há sobreposição real com UI/UX Pro Max em cores, tipos e layout. O ganho é o
processo explícito de diferenciar cada projeto, testar escolhas contra o conteúdo
e evitar decoração automática. A skill reconhece que estilos considerados
genéricos podem ser legítimos quando o briefing os pede: a direção do cliente
prevalece. Não garante diversidade visual por sua mera presença.

Editorial, minimalismo, maximalismo, brutalismo, luxo ou corporativo devem surgir
do contexto e das aprovações, não de um preset compulsório. UI/UX Pro Max continua
fornecendo referências de estilos, produto, paleta e stack. Não se deve forçar
experimentação em interface orientada a dados, Design System existente ou tarefa
limitada a corrigir um componente.

Fechamento: `skills/frontend-design/SKILL.md` e `LICENSE.txt`, ambos 100644.
Sem scripts, imports ou dependências obrigatórias de ferramentas proprietárias.
Screenshots são opcionais. Fontes/imagens futuras precisam de licença e autorização
próprias; não há assets desse tipo neste fechamento. A licença específica é
Apache-2.0; preservar texto, avisos e proveniência e registrar alterações futuras.
O repositório tem escopos de licença por diretório. Os avisos globais de outros
componentes não significam que esta skill inclua seus binários/dependências.

### React Best Practices — profundidade técnica, com bloqueios

[Conteúdo fixado](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices/SKILL.md).
Inclui 70 regras, dois arquivos auxiliares de regras, SKILL.md, README.md,
AGENTS.md compilado e metadata.json. Todos os 76 recursos existem. A priorização
de waterfalls, bundles, SSR/RSC, dados e renderização, com exemplos de problema e
solução, agrega profundidade à busca React já presente na UI/UX Pro Max.

Essa sobreposição impede tratá-la como necessidade universal. UI/UX Pro Max já
cobre memoização medida, React Compiler, estado/contexto e compound components.
O ganho desta candidata é diagnóstico técnico focado, não substituição do sistema
visual ou adoção automática de Next.js. Recomendações de performance e números
de impacto dos exemplos não são garantias para o projeto consumidor.

Bloqueios reais do review:

- Licença identificada como `unknown`, apesar da declaração MIT.
- Divergência entre licença declarada e evidência disponível.
- AGENTS.md possui links `./async-defer-await.md` (linha 116),
  `./async-cheap-condition-before-await.md` (219) e `./server-hoist-static-io.md`
  (892). Os arquivos existem em `rules/`, não ao lado de AGENTS.md. Não se
  reescreveram links nem ignorou o erro; corrigir upstream ou tratar adaptação
  rastreável em etapa própria.

SWR, better-all, lru-cache, zod, MUI, lucide-react e Vercel Analytics aparecem em
exemplos: não são instalações obrigatórias para ler o guia. O próprio exemplo
better-all fornece alternativa com Promise.all. Receitas Next.js/RSC, Activity,
useEffectEvent e outras APIs exigem verificar stack e versão. Não se aplicam APIs
React em Vue/Svelte; não transformar bibliotecas em runtimes asdf.

A receita `rendering-hydration-no-flicker.md` usa script inline e localStorage;
avaliar CSP/nonce e dados confiáveis antes de copiá-la. Supressão de warnings
não deve esconder erros arbitrários de hidratação. Não foi comprovado o
comportamento dos exemplos TSX em runtime.

### Web Design Guidelines — invólucro remoto, não checklist embarcado

[Conteúdo fixado](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines/SKILL.md).
O único recurso é SKILL.md. Ele solicita buscar novas regras antes de cada revisão
em `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`,
via `WebFetch`, e produzir achados `file:line`. A dependência é explícita no texto,
mas não aparece como bloqueio de recurso Markdown local na análise automática.

Essa outra origem não foi adquirida nem analisada, respeitando as três fontes
autorizadas. Não há hash local das regras, licença certificada do material remoto
ou cobertura auditada de formulários, contraste, teclado e demais requisitos.
A descrição do repositório não substitui esses conteúdos. Não se pode afirmar
que a skill seja autônoma, offline ou que seu workflow seja portátil apenas por
copiar o Markdown. Também não é auditoria visual/renderizada nem prova de WCAG.

Valor potencial: revisão técnica objetiva e localizada. Sobreposição alta com
UI/UX Pro Max para regras básicas; ganho incremental ainda não comprovado no
material adquirido. Prioridade inferior a uma especialista local completa.

### Composition Patterns — refatoração especializada

[Conteúdo fixado](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/composition-patterns/SKILL.md).
Os 14 recursos incluem oito regras, dois auxiliares, guia compilado, README,
SKILL.md e metadata.json. Referências locais resolvidas; sem scripts próprios.
Há procedimentos concretos para proliferação de flags booleanas, variantes,
compound components, estado e interfaces de contexto. Aprofunda temas breves da
UI/UX Pro Max e pode servir à manutenção de bibliotecas de componentes React.

Não é motivo para criar providers, contextos ou DI em todo componente simples.
É condicional à complexidade e à arquitetura aprovada, sem trocar stack ou API
pública sem justificativa. TextInput/onChangeText/onPress dos exemplos não são
autorização para instalar React Native nem prova de compatibilidade DOM.

O aviso React 19+ em `react19-no-forwardref.md` não basta para certificar o restante
como React 18: `state-context-interface.md` também usa `use(Context)` e provider
direto em exemplos. Verificar versão e intenção antes de recomendar o conjunto
para qualquer React/Next.js. Não se inventaram listas de versões compatíveis.
Além disso, a licença ausente permanece bloqueante.

## Licenças, scripts e portabilidade

Na árvore Git **completa** do commit Vercel não há arquivos cujo nome comece com
LICENSE, COPYING ou NOTICE. README diz MIT; React e Composition declaram MIT no
frontmatter; package.json da raiz não fornece texto de licença. O mecanismo
existente exige evidência identificável e bloqueia as três. Não se fabricou um
LICENSE nem se inferiram permissões comerciais irrestritas. Uma próxima revisão
deve obter evidência redistribuível e preservar copyright/avisos aplicáveis.

Os fechamentos adquiridos contêm apenas Markdown, JSON e licença textual;
**zero scripts independentes** Shell/Python/JS/TS. Não foi necessária análise
sintática de scripts de candidatas. JSON foi parseado pela biblioteca padrão;
trechos TS/TSX em Markdown foram lidos, sem executar, importar ou typecheck.
`pnpm install/build/validate` no README React são instruções de manutenção do
fornecedor, não pré-requisitos para usar os documentos estáticos. Não foram
executados. Nenhum asset, imagem ou fonte de terceiros foi empacotado.

As aquisições Vercel incluem `CLAUDE.md → AGENTS.md` na raiz: link original interno,
conferido, **fora dos fechamentos** das três skills. A primeira inspeção adicional
que tentou tratar toda a aquisição como pacote físico recusou esse link; foi
delimitada ao índice e aos recursos corretos, sem mudar validadores ou copiar o
symlink. Todos os recursos das candidatas são arquivos regulares físicos.

| Material | Legibilidade nos três agentes | Recursos locais | Dependências/portabilidade | Testes nativos |
|---|---|---|---|---|
| Frontend Design | Provável | Completos | Sem ferramenta proprietária obrigatória; screenshots opcionais | Não executados |
| React Best Practices | Provável | Arquivos presentes; links quebrados | Leitura portátil, exemplos por stack/versão; licença bloqueia | Não executados |
| Composition Patterns | Provável | Completos | Leitura portátil, APIs/versionamento exigem revisão; licença bloqueia | Não executados |
| Web Design Guidelines | Markdown legível | Só invólucro | WebFetch e regras remotas não resolvidos entre agentes | Não executados |
| Impeccable | Não certificado | Não certificado | Aquisição incompleta | Não executados |

Nenhum Codex, OpenCode ou Gemini foi iniciado. Legibilidade, descoberta nativa,
ativação efetiva e funcionamento completo são evidências diferentes. Não se
certifica toda instrução futura de um agente por distribuir um contrato.

## Comparação e conjunto mínimo

| Questão | Parecer |
|---|---|
| Frontend Design complementa ou duplica UI/UX Pro Max? | Sobreposição de fundamentos, mas processo criativo contextual adicional; escolher sob demanda |
| Impeccable aprofunda refinamento? | Hipótese promissora; conteúdo distribuível e workflow não certificados nesta aquisição |
| Comandos Impeccable podem ser distribuídos isoladamente? | Não comprovado; não criar uma skill por nome de comando |
| Web Design Guidelines agrega auditoria? | Potencial, mas regras efetivas estão fora do pacote e desta análise |
| React Best Practices agrega valor? | Sim, profundidade técnica e exemplos; pendente, depois condicional à stack |
| Composition Patterns é redundante? | Parcialmente sobreposta; útil em APIs complexas, dispensável para componentes simples |
| Onde há conflito? | Criatividade sem briefing pode redesenhar identidade; auditorias estéticas podem impor gosto; otimização/composição indiscriminadas podem alterar arquitetura |
| O que depende de React/Next.js? | React Best Practices e Composition; receitas Next específicas não migram para React genérico |
| O que exige tratamento de portabilidade? | WebFetch/regras remotas; conjunto Impeccable; exemplos específicos e links Vercel |
| Mínimo viável para próxima decisão | UI/UX Pro Max existente + somente Frontend Design explícita |

Depois de resolver impedimentos, priorizar React Best Practices para problemas
medidos em React/Next.js e, separadamente, Composition para refatoração necessária.
Não incorporar as duas por padrão. Adiar Web Design Guidelines e Impeccable até
que seus ganhos e fechamentos completos sejam verificáveis. A divisão direção
inicial / exploração / refinamento / qualidade técnica é útil como responsabilidade,
mas não são quatro etapas obrigatórias nem quatro skills sempre selecionadas.

## Propostas declarativas, sem decisões

Categoria proposta para as quatro adquiridas: `Frontend`. Todas usam
`selection_mode: explicit`, `languages_any: [javascript, typescript]`,
`frameworks_all: []`, `architecture: null`, `tools: []`, `runtimes: []` e
`requires_skills: []`. Esses campos não instalam dependências nem tornam APIs
de aplicação runtimes. O núcleo conserva os runtimes exigidos pelas linguagens.

| Candidata | frameworks_any | features_all | Condição adicional |
|---|---|---|---|
| Frontend Design | react, nextjs, vue, nuxt, svelte, astro | ui | Exploração nominal; briefing e Design System aprovados prevalecem |
| React Best Practices | react, nextjs | ui, performance | Proposta contém `blocked` com licença/links/versões pendentes |
| Web Design Guidelines | Os seis frameworks web acima | ui, code-review | `blocked`: licença, conteúdo remoto e WebFetch |
| Composition Patterns | react, nextjs | ui, refactoring | `blocked`: licença e versões/APIs; complexidade real necessária |

O JSON contém as propostas completas, normalizadas pelo parser existente.
`blocked` impede tratar os esboços pendentes como compatibilidade liberada.
Não há proposta executável para Impeccable sem aquisição íntegra. Não se gerou
arquivo de decisões, `approved`, plano de bootstrap ou plano de promoção.

O contrato atual não expressa todos os critérios humanos: estágio criativo,
preservação de Design System, necessidade comprovada de refatoração ou pedido
em prosa não são novas features inventadas. A escolha nominal continua essencial.
Features listadas são conjunctivas. Versões aceitam listas concretas, não intervalos
ou inferência da versão React a partir de Next.js. Definir versões auditadas é
pendência, não autorização para instalar/atualizar qualquer versão.

HTML/CSS puros não estão no vocabulário de linguagens. Os esboços conservadores
restringem as skills aos seis frameworks web, embora parte do conteúdo possa
servir a vanilla. Não existe framework `vanilla`. React Native isolado/backend
não satisfazem essas propostas; combinação React + React Native continua ambígua
sem alvo web inequívoco. Não foi alterado o seletor para resolver esses limites.

Listas explícitas são o conjunto completo de raízes: para usar UI/UX Pro Max
junto à especialista, solicitar ambos os IDs. Compatibilidade não autoriza
instalações, execução, mudança de stack ou sobreposição de decisões visuais.

## Cenários ilustrativos, não executados

- Site novo sem identidade aprovada: UI/UX Pro Max orienta fundamentos; Frontend
  Design pode comparar alternativas de composição antes da aprovação visual.
- Landing page repetitiva: explorar uma alternativa baseada no assunto e público,
  sem aplicar um estilo supostamente original em todos os projetos.
- Site com Design System aprovado: preservar tokens e componentes; usar a busca
  UI/UX existente para correções pontuais. Uma nova direção criativa exige pedido.
- React com jank ou bundles grandes: após desbloqueio, especialista técnica focada
  em medições; não redesenhar identidade nem instalar Next/SWR por iniciativa.
- Biblioteca React com muitas variantes: Composition pode justificar refatoração,
  após revisar licença/versões; componente simples não exige esse tratamento.
- Vue/Svelte: não escolher especialistas exclusivas de React. Mobile nativo:
  não distribuir receitas DOM automaticamente. Vanilla: limite registrado.

## Verificações e estado final

Executados: duas validações existentes da biblioteca; quatro aquisições concluídas
e quatro revisões sem decisões; integridade de **114 arquivos regulares adquiridos**
por SHA-256 e Git blob, com três links de raiz conferidos separadamente; 93
ocorrências de recursos nos quatro fechamentos; hashes oficiais dos reviews e
HEAD/baseline das sessões conferidos. Inventários, caminhos, modos, URLs, imports
de exemplos e bloqueios constam do JSON. Recursos completos fisicamente não
significam referências sem erro ou dependências semânticas resolvidas.

Quatro propostas passaram pelo parser declarativo existente. Predicados da
proposta criativa aceitaram os seis frameworks web e rejeitaram vanilla/backend/
React Native isolado. Isso não é distribuição real ou aprovação. Não se testou
descoberta nativa ou eficácia visual das candidatas.

Não foram repetidas a suíte de 298 testes nem as 104 cópias físicas: nenhum
código executável ou pacote ativo mudou. O validador existente conferiu sintaxe
dos sete JavaScript ativos sem executá-los. Timeouts, falhas de DNS e indisponibilidade
das páginas públicas fixadas do Impeccable são registrados como impedimentos,
não resultados aprovados. Nenhum validador foi contornado.

SHA-256 dos SKILL.md adquiridos:

| Candidata | SHA-256 |
|---|---|
| Frontend Design | `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3` |
| React Best Practices | `71ed7794962fa6e803ee83030517b5b93a9f70fbfeb431ec4535c5480a8d8355` |
| Web Design Guidelines | `f4647ca866a3accf763777f83e7682954f0187cd6bea7eea0399796652414e8f` |
| Composition Patterns | `e38e0eaa609316b10423a9a138ed95e35099accd3f735585295c8a8f165c28a3` |

Novos arquivos fora do staging: este RELATORIO.md e [resultado.json](resultado.json).
Dentro de cada sessão há aquisições/inspeções e `rodada2a/` com retornos CLI e
verificações; as duas sessões bloqueadas também foram preservadas. Nenhuma cópia
de fornecedor integra os relatórios ou o índice Git. Sessões históricas e
relatórios anteriores não foram alterados. `/tmp/stacknauta-2a-*` contém logs e
snapshots desta análise; não foram versionados.

Git final: mesmo HEAD, nenhum arquivo rastreado modificado, apenas os dois novos
relatórios não rastreados em `Automacao/validacao-design-rodada2a/`. **Zero commits.**
Nenhuma aprovação, promoção, instalação, execução de fornecedor ou publicação.
App-Web e consumidores reais não receberam escrita; essa evidência decorre do
escopo das operações, não de auditoria forense de diretórios externos.

Próximo passo: revisar esta classificação e decidir se deseja preparar Frontend
Design em rodada própria. Resolver impedimentos Vercel com evidências de origem,
sem fabricar licenças ou corrigir silenciosamente o fornecedor. Impeccable exige
etapa própria antes de qualquer proposta distribuível. **Parado antes da aprovação.**
