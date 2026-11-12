# Inspeção das sete fontes

Inspeção estática realizada nas revisões de `../fontes.lock.json`. Fontes intactas, scripts não executados, nenhum instalador ou build de fornecedor executado. `arquivos.json` enumera todos os arquivos materializados, inclusive documentação, scripts, assets, templates, licenças, agentes auxiliares, exemplos e testes. Recursos não foram reduzidos ao SKILL.md.

| Origem | Caminho canônico | Conteúdo e peculiaridades |
|---|---|---|
| UI/UX Pro Max | `.claude/skills/*/SKILL.md` | Sete skills canônicas; seis cópias adicionais em `cli/assets/skills/`. CSVs, scripts Python/Node, referências, templates, assets e fontes preservados. Raiz MIT; `ui-styling/LICENSE.txt` Apache-2.0. |
| FastAPI | `fastapi/.agents/skills/fastapi/SKILL.md` | Uma skill, oito referências Markdown, licença MIT e documentação da raiz. Sparse-checkout conserva todo o diretório da skill; o pacote FastAPI não foi instalado. |
| Remy349 | `skills/*/SKILL.md` | Três skills de arquitetura hexagonal, Python, TypeScript e Go. Referências e exemplos completos; licença MIT. Scripts Node de manutenção na origem exigem Node >=20; não foram executados. |
| Expo | `plugins/expo/skills/*/SKILL.md` | 23 skills do plugin principal, uma experimental em `plugins/expo-experiments/skills/` e uma interna em `.claude/skills/expo-skill-eval/`. MIT, incluindo atribuição própria de `expo-animation`. Scripts JS/TS/Python/shell e references preservados. |
| Chris Banes | `skills/*/SKILL.md` | 21 skills, com Kotlin/Compose e também escrita, releases, Gradle e coordenação de trabalho. Referências, scripts Python, metadados de agentes e avaliações presentes. Apache-2.0. |
| Android | diretórios temáticos, inclusive níveis aninhados | 36 skills; referências locais extensas da documentação Android, recursos e scripts preservados. Apache-2.0. Caminhos não se limitam a `skills/`: incluem `device-ai/litert/`, `jetpack-compose/ink/`, `security/` e outros. |
| Sentry | `skills/*/SKILL.md` | 31 skills com referências, SPEC/SOURCES, scripts, agentes e recursos auxiliares. Apache-2.0 na raiz. O LICENSE de `security-review` identifica referências derivadas de OWASP sob CC-BY-SA-4.0; preservar as duas evidências e a atribuição. |

## Distribuição UI/UX Pro Max pendente

Foram lidos `README.md`, `cli/README.md`, `cli/package.json`, `cli/scripts/sync-assets.mjs`, `cli/src/utils/template.ts` e as configurações `codex.json`, `opencode.json` e `gemini.json` em `src/ui-ux-pro-max/templates/platforms/`.

O processo oficial usa uma CLI para renderizar `templates/base/skill-content.md` e a referência rápida, aplicar configuração e caminhos da plataforma, copiar `data/` e `scripts/` e instalar as seis subskills como irmãs. O SKILL.md do orquestrador em `.claude/skills/` é mantido separadamente, com caminhos e variável de plugin Claude. Não é um substituto universal dos templates. As seis cópias de SKILL.md em `cli/assets/skills/` são byte a byte idênticas às canônicas; arquivos adicionais de distribuição podem diferir por exclusões oficiais de assets binários.

A rotina oficial de sincronização exclui fontes de canvas e certos binários dos bundles de subskills. O clone completo foi preservado para não omitir esses recursos da inspeção. O catálogo usa os diretórios canônicos completos, não somente os assets empacotados.

`ui-styling/canvas-fonts/` também contém 27 arquivos de licença SIL Open Font License 1.1 para os assets de fontes. Foram identificados separadamente em `license.asset_licenses`; esses termos não são substituídos pela licença Apache da skill ou MIT da raiz. O inventário também registra `google-font-licenses.json` como metadado de licenciamento do fornecedor, sem baixar fontes externas.

A CLI declara dependências Node, tem build em Node e também fluxo de desenvolvimento Bun. Node global asdf está disponível, mas CLI compilada/dependências não foram preparadas ou executadas e Bun não está instalado. A leitura parcial do código **não constitui auditoria de segurança completa**. Não foi tentada uma renderização alternativa. A fonte está catalogada; preparar e validar a distribuição para os agentes permanece pendente. O mecanismo oficial inclui comandos de atualização global e remoção de layouts, incompatíveis com execução indiscriminada nesta etapa.

## Dependências e limites de seleção

- Expo conserva `.gitmodules` e o gitlink de `eval-harness` apontando para `expo/eval-experiments`. O submódulo serve ao avaliador interno e ficou sem checkout. Essa skill está explicitamente marcada `internal_evaluation_not_distributable`; as 23 skills do plugin principal e a experimental estão fisicamente presentes. A experimental não é promovida a distribuição estável.
- `expo-overview` faz roteamento para skills irmãs. Menciona `expo-tailwind-setup`, que não tem SKILL.md neste commit; nenhum arquivo foi inventado. Sua menção a `references/native-ios.md` se refere ao recurso de `eas-app-stores`, não a um arquivo no diretório de `expo-overview`.
- Subskills UI/UX referenciam irmãs e arquivos do futuro projeto consumidor. Gerar tokens, slides e imagens pertence a fases posteriores, não à aquisição da biblioteca.
- `chrisbanes:implement-with-subagents` declara dependência externa de `tdd`, de Matt Pocock, no modo de implementação. Essa oitava origem não foi adquirida. Skills de release e coordenação também têm pré-requisitos próprios; não autorizam ações nesta instalação.
- `android:r8-analyzer` exige Python e `protobuf>=6.33.4`; não foi instalado nem executado. Outras skills Android dependem de SDKs, Gradle, bibliotecas e, em alguns casos, hardware específico.
- Sentry contém rotinas específicas da organização, uso de `uv`, GitHub CLI autenticada, navegador, MCP Sentry, Notion e Linear. Nada foi autenticado, configurado ou executado. Dependências e pré-requisitos aparecem por skill em `dependency_evidence` e no frontmatter preservado.
- `sentry:django-access-review` declara `license: LICENSE`, mas não há LICENSE local na pasta. A licença Apache-2.0 da raiz foi preservada e o problema registrado; não foi criado arquivo substituto.
- A prioridade futura do asdf conflita com recomendações genéricas de fallback Python/Node ou instalação de ferramentas em algumas fontes. Essas fontes não foram modificadas. A seleção/adaptação deverá respeitar a política StackNauta antes de habilitar qualquer uma.

## Conferência de referências

O scanner verifica links Markdown fora de blocos de código e menções a arquivos de recursos em todos os documentos Markdown das skills. Registra resolução relativa ao documento, à skill e à raiz da origem; candidatos em outras pastas são evidência, não correção automática. Não segue URLs nem executa scripts, e não prova cobertura semântica completa de dependências, imports ou caminhos dinâmicos.

A execução encontrou 1.327 referências/menções presentes, quatro exemplos de URL/caminho e 28 menções que não resolvem nesses três contextos. Todas estão em `recursos.json`, com documento e possível correspondência quando existe. Elas permanecem conservadoramente marcadas para revisão antes da cópia:

- UI/UX: 13 menções a tokens/assets do consumidor, banners exemplificativos, biblioteca `assets/css/slide-animations.css` e exemplo de apresentação ausente. Nem todos são recursos que deveriam acompanhar a skill; a biblioteca de animação e o exemplo declarado precisam de esclarecimento antes de distribuição de slides.
- Expo: uma menção ao `native-ios.md` existente na skill irmã `eas-app-stores`.
- Sentry: duas chamadas de manutenção a `quick_validate.py` existente em `skill-writer`, uma referência de fonte ao `scripts/dev-ui-server.ts` do repositório separado `getsentry/sentry`, um exemplo de localização `scripts/tool.py` e dez menções exemplificativas/saídas de criação de skills em `skill-writer` (como working-set, holdout-set e `agents/openai.yaml`).

Essas 28 ocorrências não são tratadas como falha de download nem automaticamente como arquivos obrigatórios ausentes. O inventário mantém todo o conteúdo real das fontes e deixa `copy_plan_complete=false`. A certificação de um conjunto copiável, recursos transitivos, frontmatter completo e compatibilidade dos agentes pertence à próxima etapa.

## Integridade e isolamento

Todos os arquivos materializados são conferidos contra SHA-256 do inventário e seus blobs originais no Git. Commits, URL, branch, ausência de alterações, integridade `git fsck`, arquivos sparse e submódulos são conferidos. Os quatro links originais são relativos, internos e existentes; não há links absolutos ou links criados nas pastas de agentes.

`resultado.json` registra os resultados; `preservacao.json` compara o conteúdo e os metadados das duas árvores legadas com o baseline anterior à criação. Nenhuma alteração de fornecedores ou consumidores é necessária para executar a validação local.
