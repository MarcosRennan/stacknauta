# Distribuição — Etapa 1.5

Resultado: **101 skills aprovadas**, **21 pendentes**, **duas excluídas**, organizadas em nove pacotes versionados. Zero ativações de agentes. Nenhum motor de bootstrap implementado.

## Unidade de distribuição e fechamento

Cada pacote de origem/categoria inclui diretórios reais `skills/<nome>/`, arquivos comuns e `PROVENANCE.json`. São pacotes autocontidos: nenhuma dependência obrigatória aponta para o cache de aquisição. As quatro categorias de consumo são Frontend, Backend, Mobile e Seguranca; manutencao e validacao guardam ferramentas/evidências, não skills de consumidor.

O catálogo distingue a categoria adquirida da categoria de distribuição. Algumas skills antes agrupadas em manutenção/validação, como Gradle, testes Compose e revisão Python, foram classificadas pelo domínio em que são consumidas. As decisões de todas as 124 entradas são explícitas em `manutencao/distribuicao-politica.json`, sem habilitação automática por descoberta de novos arquivos.

`distribution.requires_skills` contém os vínculos do conjunto de cópia. Referências de arquivos em skills irmãs exigem o diretório inteiro da irmã; o fechamento é transitivo. Para a família Expo, o router exige o conjunto das 23 skills estáveis. O conjunto parcial mantém o layout do pacote e inclui seus recursos comuns/licenças, sem links ou hardlinks. A função `selected_files()` somente calcula arquivos: não configura agentes, instala pacotes, executa geradores ou cria esqueleto de aplicação.

O manifesto de proveniência descreve o pacote completo. Uma cópia parcial tem legitimamente menos arquivos que o pacote inteiro e deve ser validada pelo plano selecionado. Essa distinção evita distribuir a biblioteca inteira para uma única skill Android ou repetir todos os recursos de uma origem sem necessidade.

Licenças de raiz são guardadas uma vez em cada pacote independente. Licenças específicas locais permanecem junto do material a que se aplicam, inclusive OWASP CC-BY-SA-4.0, ui-styling Apache-2.0 e 27 licenças OFL de fontes. Metadados Google Fonts também foram preservados, sem baixar fontes externas. A duplicação de uma licença raiz entre pacotes independentes de categorias distintas mantém cada um distribuível; os blobs iguais são deduplicados pelo Git.

## UI/UX Pro Max

O renderer próprio usa somente a biblioteca padrão Python e reproduz o método oficial `renderSkillFile` para instalação local. Os templates base, referência rápida e quatro configurações foram preservados e versionados com licença MIT. A equivalência byte a byte nas quatro configurações está em `renderizacao-ui.json`. Nenhum instalador, sincronizador, build ou dependência npm/Bun foi necessário.

O pacote aprovado usa o template `universal` e caminhos `<skill-dir>`/`<asdf-global-python>`, resolvidos pelo agente a partir do diretório real e do runtime global verificado. Não pressupõe `.claude`, `.agents`, `.opencode`, `.gemini` ou diretório absoluto da máquina. Os dados e scripts vêm da árvore oficial `src/ui-ux-pro-max`; referências adicionais vêm da skill canônica.

Quatro skills são distribuídas: `ui-ux-pro-max`, `banner-design`, `brand`, `ui-styling`. O diretório completo das quatro foi conservado; no orquestrador, os recursos canônicos espelhados foram substituídos pela árvore oficial de distribuição, sem duas cópias físicas. O helper `design-system/scripts/generate-tokens.cjs`, exigido pelo script brand, é recurso compartilhado real e tem proveniência própria. **Não há SKILL.md fictício para design-system.**

`design-system`, `slides` e `design` permanecem pendentes: a revisão adquirida cita uma biblioteca de animação CSS não fornecida e um exemplo de apresentação ausente, e o orquestrador design inclui esses fluxos. Não se inventou asset, não se reduziu silenciosamente o escopo desses SKILL.md e não se incluiu skill pendente no pacote.

## Adaptações explícitas

`adaptacoes.json` guarda os hashes anteriores/posteriores e unified diffs. Os `PROVENANCE.json` guardam hashes e caminhos de todos os inputs originais. As origens do cache não recebem nenhuma mudança.

- Contrato de execução e cópia inserido em cada SKILL.md aprovado; comandos de fornecedor ficam subordinados ao uso do runtime global asdf já instalado, sem instalação implícita ou fallback.
- Orquestrador UI/UX renderizado pelos templates oficiais, com caminhos portáteis e pré-requisito asdf; o antes do diff é a renderização oficial, cujos inputs estão identificados no manifesto.
- Node filho do helper brand usa `process.execPath`, preservando o executor verificado do pai.
- `expo-overview` referencia o arquivo iOS da skill irmã e declara explicitamente a indisponibilidade da rota expo-tailwind-setup, inexistente no commit. Não há substituto inventado.
- `agents-md` orienta cópia física de entrypoints em vez de symlink.
- Referências textuais de licença no frontmatter apontam para a licença real comum do pacote quando o arquivo local não existe; termos das licenças não foram alterados.

Arquivos de distribuição são regulares, sem modo executável; helpers devem ser invocados pelo runtime global explicitamente verificado, não por shebang. Testes e ferramentas auxiliares de manutenção que já estavam nos diretórios das skills foram preservados como material de origem; sua execução completa não é certificada nem é necessária aos fluxos de runtime testados. O contrato do pacote não autoriza instalações, publicação ou ações em serviços.

## Revisão das 28 menções

`revisao-recursos.json` classifica individualmente todas as ocorrências da Etapa 1: saída/exemplo do consumidor, referência resolvida de irmã, manutenção upstream, atribuição externa, exemplo/artefato gerado ou lacuna upstream que bloqueia distribuição. Não se tratou um caminho de exemplo como download ausente nem se descartou uma dependência real para aprovar a skill.

As duas referências a `quick_validate.py` em SPEC.md pertencem à validação de manutenção realizada a partir de skill-writer. Não são helpers de runtime de security-model/secret-serialization e não foram duplicadas com uma dependência PyYAML nova. A rotina de criação de skills e o scanner que obrigatoriamente dependem de PyYAML permanecem pendentes. A referência de SOURCES.md ao servidor de UI Sentry é atribuição de fonte externa; o fluxo organizacional correspondente também está pendente.

## Validação e limites

A validação padrão não consulta o cache. Confere revisões, entradas de política, hashes, proveniência original, recursos, caminhos de licença, links Markdown locais, dependências transitivas, ausência de skills não aprovadas, ausência de symlinks e preservação dos diretórios vazios de automação/agentes. `--origens` é uma verificação adicional explícita das sete origens e seus blobs Git.

Os testes de cópia usam um destino temporário novo para cada uma das 101 skills, copiam o fechamento e os arquivos comuns, comparam bytes e identidade física e revalidam referências. Buscas locais UI/UX previamente analisadas exercitam UX, Next.js e geração de recomendações sem persistência. Testes adversariais verificam rejeição de bytes adulterados, referência ausente e caminho com escape. Python é parseado por AST e JavaScript pelo parser Node, sem executar esses outros helpers.

O teste de clonagem usa um clone Git local real, com objetos independentes, sem alternates, submódulos, cache de aquisição ou remoto final configurado. A validação e as 101 cópias são repetidas nesse clone. Os relatórios informam a revisão testada e o fingerprint dos manifestos de pacotes, que não dependem do commit que apenas registra os próprios relatórios.

Isso não certifica a execução de todos os workflows de fornecedores, integração ou descoberta nos três agentes, SDKs Android/Expo, CLIs autenticadas, serviços, hardware, publicação ou instalações. Esses requisitos permanecem explícitos no catálogo e nos SKILL.md. O motor project-bootstrap e os testes de criação de aplicações continuam para etapas seguintes.
