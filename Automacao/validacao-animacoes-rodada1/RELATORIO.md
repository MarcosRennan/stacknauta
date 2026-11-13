# Etapa 4B — Rodada 1: candidatas de animação

Análise realizada em 13/11/2026. **Aquisição e descoberta concluídas; nenhuma
aprovação, promoção ou inclusão na biblioteca ativa.** Dez candidatas permanecem
`pending`, `enabled: false`, em duas sessões isoladas. As classificações abaixo
são recomendações técnicas deste relatório, não decisões gravadas no catálogo.

## Estado inicial e procedimento

HEAD inicial e final: `a035f50c3d890668b4817c3b32edad6274c6a344`.
Árvore inicialmente limpa, incluindo arquivos não rastreados. Foram consultados
AGENTS.md, a [documentação de inclusão](../manutencao-skills/INCLUSAO.md), a CLI,
os módulos compartilhados de análise e o [relatório R01/R02](../validacao-r01-r02/RELATORIO.md).
A regressão histórica de 273 testes pertence à etapa anterior; não foi repetida.

Comandos disponíveis: `check`, `update`, `add`, `review`, `apply`, `recover`.
Nesta rodada foram usados apenas `add` e `review SESSION`, sem decisões.
Não foram usados `update`, `apply`, `recover`, `--approve` ou equivalentes.

```sh
Automacao/python-global Skills/validacao/validar_biblioteca.py
Automacao/manutencao-skills/skills add https://github.com/iart-ai/web-animation-skills
Automacao/manutencao-skills/skills add https://github.com/mthines/agent-skills/tree/main/skills/design/animations
Automacao/manutencao-skills/skills review 52b822d7ca934018abaa284e709e51e3
Automacao/manutencao-skills/skills review f1e5ec90d12343f9989afa5c1f23fa82
```

A primeira consulta HTTPS falhou por DNS no sandbox, antes de criar sessão.
As aquisições seguintes usaram a permissão de rede solicitada, pelo mesmo fluxo
existente. Não houve transporte alternativo, execução de instaladores ou checkout
com scripts/hooks do fornecedor. A aquisição usa Git raso, verificação de objetos
e materialização controlada; não configura remotos do repositório principal.

A biblioteca passou na validação com pendências já documentadas e **zero erros**:
101 aprovadas, 21 pendentes, duas excluídas, sete origens, nove pacotes;
958 arquivos de pacotes verificados, 41 Python analisados e 1.095 links locais
conferidos. Locks, licenças, hashes e proveniência foram confrontados pelo
validador existente. Não foram solicitados smoke tests ou cópias nesta rodada.

## Origem e identificação das sessões

| Origem | Revisão fixada na inspeção | Escopo | Candidatas |
|---|---|---|---:|
| [iart-ai/web-animation-skills](https://github.com/iart-ai/web-animation-skills/tree/ed3a045192679b24d32090ee7a983871311ababd) | `ed3a045192679b24d32090ee7a983871311ababd` | Repositório completo, branch main | 9 |
| [mthines/agent-skills](https://github.com/mthines/agent-skills/tree/3f78b3bad165f10955230e3811661d6af21467b0/skills/design/animations) | `3f78b3bad165f10955230e3811661d6af21467b0` | `skills/design/animations`, branch main | 1 |

**iart-ai**

- Origem candidata: `gh-iart-ai-web-animation-skills`.
- Sessão: `52b822d7ca934018abaa284e709e51e3`.
- `review_id`: `bfa0b1b8f3fb96ca230f783cd9f6ab9e0022c61e36ef027dd351abd872eb0541`.
- Inspeção: `.stacknauta-updates/52b822d7ca934018abaa284e709e51e3/inspection/Skills/_repos/gh-iart-ai-web-animation-skills/`.

**mthines**

- Origem candidata: `gh-mthines-agent-skills`.
- Sessão: `f1e5ec90d12343f9989afa5c1f23fa82`.
- `review_id`: `b7986f21daf3ec8356c251c1352c6d7adcd2d60763d43c74d46d3dd743cc6130`.
- Inspeção: `.stacknauta-updates/f1e5ec90d12343f9989afa5c1f23fa82/inspection/Skills/_repos/gh-mthines-agent-skills/`.

`analysis.json`, índices, evidências de licença e bytes adquiridos permanecem
nessas sessões, ignoradas pelo Git. O [resultado.json](resultado.json) preserva
as respostas completas de descoberta/revisão, os hashes dos recursos e os
resultados estáticos. **Não existe plan_id promovível desta rodada:** não foram
enviadas decisões individuais, nem preparado dry-run de incorporação. O review_id
identifica a inspeção e não autoriza distribuição ou execução de ferramentas.

## Avaliação individual

Todos os caminhos iart abaixo são relativos à sua revisão fixada; o ID completo
é `gh-iart-ai-web-animation-skills:<nome>`. Cada diretório contém SKILL.md e README.
Todas têm licença MIT da raiz, referências resolvidas e nenhum conflito nominal
ou duplicata exata com o catálogo atual. Sobreposição funcional é avaliada
separadamente de igualdade de bytes.

| Nome e caminho do SKILL.md | Finalidade e stack | Recursos específicos e dependências | Classificação e recomendação |
|---|---|---|---|
| `60fps-animation` — `skills/60fps-animation/SKILL.md` | Diagnóstico de jank, FLIP, leituras/escritas em lote, sombras e expansão; CSS/JS, WAAPI, independente de framework | `references/patterns-and-profiling.md`; sem biblioteca de animação obrigatória; DevTools para medição | **Recomendada.** Complementa a UI/UX com procedimentos de investigação e receitas. Ressalva: o exemplo de grid não comprova ausência de layout; 60/120fps é alvo medido, não garantia. |
| `accessible-animation` — `skills/accessible-animation/SKILL.md` | Movimento reduzido por intensidade, mudanças de preferência em tempo real, controles de pausa; CSS/JS e exemplos React/GSAP/Motion/Lenis | `references/patterns.md`; APIs do navegador bastam no caminho básico; bibliotecas são condicionais ao exemplo escolhido | **Recomendada.** Amplia a orientação geral de acessibilidade com teardown e padrões práticos. Não constitui certificação WCAG; revisar a cascata dos resets e os casos classificados como essenciais. |
| `micro-interaction` — `skills/micro-interaction/SKILL.md` | Hover, press, toggle, toast, drawer, modal, reorder e feedback de estado; CSS e React | `references/css-recipes.md`, `references/framer-motion-recipes.md`; CSS não exige pacote; caminho React exige React e Motion (`motion/react`) ou compatibilidade explícita do projeto | **Recomendada.** Melhor ganho direto para componentes cotidianos. Começar por CSS; spring/layout/gestos apenas quando pedidos. Não copiar JSX para Vue/Svelte/vanilla. |
| `svg-animation` — `skills/svg-animation/SKILL.md` | Draw-on, morph, caminhos, ícones, gradientes e filtros; SVG/CSS/SMIL/JS | `references/svg-techniques.md`; CSS/SMIL básicos sem biblioteca; GSAP/MorphSVG/MotionPath ou Flubber opcionais; SVGO é ferramenta opcional de autoria | **Recomendada.** Especialização vetorial distinta de paletas/layout da UI/UX. Escolher um controlador; verificar suporte do navegador, custo de filtros e estado estático final. |
| `gsap-web` — `skills/gsap-web/SKILL.md` | Timelines, ScrollTrigger, pin/scrub, SplitText, Flip, integração de rolagem; JS/TS, vanilla ou frameworks web | Dois cookbooks; `examples/hero-timeline.js`, `examples/standalone-template.html`; GSAP obrigatório nesse caminho; Lenis/Locomotive e `@gsap/react` condicionais | **Condicional.** Agrega profundidade além dos 17 presets existentes. Descoberta mantém bloqueios por imports `gsap` e `gsap/SplitText`. Revisão específica de dependências e versão/licença antes de incorporar; nunca instalar por selecionar a skill. |
| `lottie-animation` — `skills/lottie-animation/SKILL.md` | Integração de assets de designer, segmentos, playback, tema e exportação AE; web/React e notas mobile | `references/integration-and-export.md`; player dotLottie ou lottie-web obrigatório para playback; wrapper React/interactivity opcionais; After Effects/Bodymovin apenas para autoria/exportação | **Condicional.** Útil quando houver asset .lottie/.json autorizado. Não entrega o asset nem licença sobre animações futuras. Paridade mobile/formatos e versões dos players não foram testadas. |
| `ascii-animation` — `skills/ascii-animation/SKILL.md` | Arte generativa ASCII, conversão de imagem/vídeo, terminal e Three.js | `references/rendering.md`, `scripts/img-to-ascii.mjs`; conversor Node depende de `sharp`; Three.js apenas no caminho 3D; canvas/pre básicos sem pacote | **Pendente.** Nicho de pedido explícito, sem prioridade para UI usual. Import `sharp` bloqueado pelo fluxo; não instalado. Avaliar a necessidade do conversor e sua dependência antes de eventual inclusão. |
| `glassmorphism` — `skills/glassmorphism/SKILL.md` | Vidro fosco/líquido, blur, highlights, refração e hover; CSS/SVG | `references/glass-recipes.md`; sem pacote obrigatório; backdrop-filter/SVG dependem de suporte e orçamento gráfico | **Redundante.** UI/UX já contém Glassmorphism e diretrizes de contraste. As receitas têm valor específico, mas animam blur/sombra e conflitam com orientações de performance das outras candidatas. Não incorporar nesta rodada. |
| `page-transition-animation` — `skills/page-transition-animation/SKILL.md` | Transições de páginas, App Router, AnimatePresence/FrozenRouter e View Transitions | `references/full-examples.md`; Next.js/React/Motion no caminho FrozenRouter; `next-view-transitions` opcional; API nativa em alternativas | **Pendente.** Usa `next/dist/...LayoutRouterContext` e coloca AnimatePresence em template que pode remontar. A orientação de persistência é internamente contraditória. Exige comprovação por versão/router e revisão do conteúdo antes de recomendar distribuição. Demo HTML não comprova integração Next.js. |

**mthines — `gh-mthines-agent-skills:animations`**

- Caminho: `skills/design/animations/SKILL.md`, revisão acima, licença MIT.
- Descrição funcional: análise da interação antes da escolha do efeito, CSS-first,
  View Transitions, scroll timelines, Motion para React, coreografia de estados,
  performance percebida, skeletons/otimismo, R3F e engines de assets.
- Recursos: `lens.md`, `references/recipes.md`, 17 documentos em `rules/`, três
  templates HTML e `scripts/is-motion-diff.mjs`; 25 arquivos no fechamento,
  incluindo a licença. Núcleo web CSS/JS; exemplos React/TSX não são universais.
- Dependências condicionais: React/Motion; R3F/Three/Drei para 3D; Lottie ou Rive
  para assets; Node e Git no classificador; `gh` só em integrações de PR.
  Não se exigem todos os motores para usar orientações CSS.
- **Classificação: Pendente.** Bom catálogo semântico de verbos/feedback e esperas,
  mas não incorporar no estado adquirido. Há oito referências não resolvidas
  no escopo (screencast, video-analyser, animations-native, ux e create-skill);
  os fluxos opcionais não tornam esses links fisicamente distribuíveis.
  Não foram adquiridas/aprovadas essas outras skills para satisfazer o fechamento.
- `Skill(...)`, `${CLAUDE_SKILL_DIR}` e slash commands de ferramentas próprias
  dependem de capacidades não portáveis por si só. `confidence`, visual-design,
  pr-reviewer e ui-verify são ainda referências operacionais em prose, não
  dependências automaticamente garantidas pelo inventário.
- A regra que exclui GSAP da implementação e exige Motion conflita diretamente
  com o domínio GSAP da UI/UX e com `gsap-web`. O próprio lens admite revisar GSAP:
  a diferença entre revisar e implementar precisa ser mantida explícita.
- O classificador importa efetivamente apenas `node:fs`, `node:child_process` e
  `node:url`. O coletor textual também encontrou `motion/react` em fixture string
  e `", "` ao cruzar aspas. Esses dois bloqueios são falsos positivos identificados
  por leitura do arquivo, **não foram removidos, dispensados ou contornados**.
  A sintaxe passou; isso não remove a pendência do fluxo. Uma rodada própria pode
  tratar o analisador ou a adaptação autorizada, sem alterar esta inspeção.

## Licenças, segurança e condições de uso

As dez candidatas têm evidência MIT física adquirida: copyright 2026 iart.ai e
copyright 2026 Mads Thines, respectivamente. A redistribuição deve preservar
copyright, aviso de permissão e exclusão de garantia, inclusive recursos comuns.
Não foi encontrada licença de asset divergente pelo inventário. Isso não licencia
automaticamente pacotes npm, players, fontes, imagens ou animações carregados no
projeto futuro. Nenhum runtime/asset remoto foi incluído ou executado nesta análise.

**Kit comum iart:** todas as nove skills incluem no fechamento `scripts/README.md`,
`contact-sheet.sh`, `seek-shot.sh`, `probe-mp4.sh` e LICENSE. Os auxiliares usam
ffmpeg/ffprobe, cp, awk e, para screenshots, npx/Playwright/Chromium. ffmpeg e ffprobe
foram localizados; a disponibilidade de Playwright/Chromium não foi exercitada.
O caminho npx localizado é um shim asdf, não prova de dependências prontas.
Os exemplos aceitam ferramenta de navegador alternativa, mas o kit traz
`npx -y playwright`, que pode baixar/executar pacote sem nova pergunta. Isso
não é autorização do StackNauta. Antes de futura promoção, registrar como o fluxo
de verificação usará ferramentas já disponíveis ou uma adaptação explicitamente
revisada; não permitir instalação implícita.

`contact-sheet.sh` usa `ffmpeg -y` e pode sobrescrever o arquivo de saída;
`seek-shot.sh` grava nomes previsíveis no diretório corrente. Não tratar esses
helpers como leitura pura. `img-to-ascii.mjs` lê uma imagem e usa sharp;
`hero-timeline.js` contém autoexecução ao ser importado em uma página com .hero.
Nenhum foi importado ou executado. O classificador mthines pode ler arquivos e
invocar `git diff` via execFileSync se executado; só recebeu parsing nesta rodada.

Não foram identificadas instruções para exfiltrar credenciais, ignorar permissões
ou executar instalação remota por pipe no material inspecionado. Essa conclusão
é limitada à leitura estática da revisão adquirida, não certificação de segurança
de dependências/CDNs ou versões futuras. Exemplos CDN produzem dependência de
rede e precisam da política do projeto; não se tornam offline por estarem num HTML.

Outras ressalvas técnicas a preservar na decisão:

- iart exige frequentemente entrega standalone HTML/CDN. É útil como demonstração,
  mas não deve substituir arquivos/componentes/roteamento da stack explicitamente
  escolhida. O bootstrap prepara o esqueleto; não implementa essas animações.
- O texto GSAP/SVG atribui a gratuidade de plugins a 3.12, mas o anúncio oficial
  é da [3.13](https://gsap.com/blog/3-13/). Usar versão/API concretas, não assumir
  equivalência. A [licença GSAP](https://gsap.com/community/standard-license/)
  tem termos próprios e restrições para determinados construtores visuais;
  MIT da skill não a substitui.
- `page-transition-animation` importa API interna e faz afirmações amplas sobre
  remontagem. A [documentação Next.js](https://nextjs.org/docs/app/api-reference/file-conventions/template)
  descreve remontagem por segmento e reset de estado; portanto a persistência
  necessária ao exit não está provada pela receita. Nenhum app foi criado para
  testá-la nesta rodada.
- `accessible-animation` usa um reset global `!important`, seguido por overrides
  sem `!important`: estes não restauram as durações como a prose sugere. O padrão
  positivo no-preference e exemplos por biblioteca são alternativas presentes;
  copiar a combinação literalmente exige revisão. Loading spinner não deve ser
  considerado essencial em qualquer contexto apenas pelo nome.
- Há simplificações sobre composição GPU, filtros e grid em ambos os repositórios.
  Não aceitar promessa de compositor-only/60fps sem medir o caso concreto. O
  [guia web.dev](https://web.dev/articles/animations-guide) recomenda verificar o
  impacto das propriedades além de transform/opacity e evitar promoção excessiva.
- O [guia Motion](https://motion.dev/docs/react-upgrade-guide) documenta migração
  de imports, mas não sustenta a inferência de que todo projeto deva migrar para
  atender uma skill. A afirmação mthines de abandono de framer-motion não foi
  adotada como política. Mudança de dependência exige decisão do projeto.
- Movimento reduzido e pausa têm finalidades distintas. A referência
  [WCAG 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)
  é nível AAA; a leitura de uma skill ou um reset não comprova conformidade global,
  nem cobre sozinho foco, leitores de tela, flashes ou controles de pausa.

## Complementaridade e compatibilidade com agentes

A UI/UX Pro Max permanece responsável pelo sistema visual, adequação ao produto,
paleta, tipografia, layout, prioridades de UX e acessibilidade. Foi inspecionada
exclusivamente a cópia distribuída: `SKILL.md`, `data/styles.csv`,
`data/ux-guidelines.csv`, `data/motion.csv` e o mapeamento estático em `scripts/core.py`.
Nenhum search.py do fornecedor foi executado. Confirmados **17 presets GSAP**, com
hover, scroll reveal, stagger, page transition, parallax, loaders e carousel;
Glassmorphism também já é um estilo explícito.

| Situação | Combinação sugerida |
|---|---|
| Decisão de estilo/layout sem pedido de movimento | Só UI/UX Pro Max; não acrescentar animações por padrão |
| Feedback em componentes | UI/UX + micro-interaction; accessible-animation se houver desenho/auditoria da redução |
| Jank ou custo de animação | UI/UX quando houver decisão visual + 60fps-animation para diagnóstico; só 60fps se o design estiver fixado |
| SVG animado | UI/UX para direção visual + svg-animation para mecânica; não ativar GSAP apenas por haver SVG |
| Timeline/scroll complexo explicitamente GSAP | UI/UX + gsap-web, com accessible-animation conforme necessidade; não usar mthines como regra concorrente |
| Asset Lottie fornecido e licenciado | lottie-animation; UI/UX só para integrar o asset à experiência; dispensa GSAP se não houver outra demanda |
| Hover simples/preset já adequado | UI/UX ou uma especialista específica; evitar carregar várias receitas equivalentes |
| Transição Next.js/FrozenRouter ou mthines genérico | Manter pendente até resolver as ressalvas; não transferir autoridade de stack a essas skills |

Os Markdown e exemplos iart são estruturalmente utilizáveis por Codex, OpenCode
e Gemini após o empacotamento e adaptações previstas pelo contrato; não exigem
plugin Claude como requisito para ler instruções. Descoberta nativa, ativação e
execução dessas candidatas nos três agentes **não foram testadas**. Em mthines,
o núcleo conceitual é legível, mas ferramentas/comandos Claude e skills externas
impedem afirmar portabilidade funcional do workflow completo. Não executar
agentes nem incorporar seus manifests/plugins upstream para contornar isso.

## Seleção sugerida pelo bootstrap — sem implementação

Condições abaixo são propostas para uma futura decisão; nada foi gravado em
configuração, catálogo ou seletor. Usar o vocabulário existente, sem inventar
frameworks `gsap`, `lottie` ou `motion`: são bibliotecas de aplicação, não runtimes
ou executáveis para o campo tools.

Base das candidatas recomendadas/condicionais: linguagem explicitamente declarada
`javascript` ou `typescript`, `features_all: ["ui", "animation"]`; frameworks
obrigatórios vazios para os caminhos CSS/DOM gerais. Para stacks web já declaradas,
conferir react/nextjs/vue/nuxt/svelte/astro conforme o exemplo. Não estender essas
receitas DOM automaticamente a Expo/React Native/Compose.

| Candidata | Condição adicional de seleção explícita |
|---|---|
| 60fps-animation | Pedido de diagnóstico/otimização; acrescentar `performance` às features exigidas |
| accessible-animation | Pedido de acessibilidade/reduced-motion/auditoria de animações; acrescentar `accessibility` |
| micro-interaction | Pedido de hover/press/toggle/modal/listas/feedback; CSS por padrão; React/Motion só se React/Next.js declarados e biblioteca autorizada |
| svg-animation | Pedido explícito de ícone/ilustração/path SVG animado; CSS/SMIL ou engine já escolhida, sem inferir GSAP |
| gsap-web | Pedido explícito de GSAP/timeline/ScrollTrigger avançado e escolha de biblioteca autorizada; confirmar versão e licença; Lenis/Locomotive somente se solicitados |
| lottie-animation | Pedido explícito de playback Lottie e asset licenciado disponível; escolha de player/renderer aprovada; não selecionar pelo simples requisito ui |

**Limite concreto do seletor atual:** `Library.select` seleciona todas as aprovadas
compatíveis quando `skills` é null. O contrato não possui opt-in por biblioteca,
SVG/Lottie nem uma condição “somente seleção explícita”. `enabled: false` não é
essa barreira. Portanto ui+animation isoladamente não discrimina as especialistas.
Para a próxima rodada, usar a lista existente `skills: [...]`, com os IDs desejados
e `ui-ux-pro-max:ui-ux-pro-max` se necessário (a lista é o conjunto de raízes,
não acréscimo ao automático), e revisar o dry-run. **Não aprovar em lote regras
genéricas que façam todas combinarem automaticamente.** Se a intenção futura
for garantir esse opt-in em todo bootstrap automático, falta uma política
expressável para essa garantia; exige decisão de escopo antes da promoção,
não foi implementada nesta análise.

A seleção de uma skill nunca concede autorização para instalar sua biblioteca,
baixar navegador, trocar framework, usar CDN ou desenvolver funcionalidade de
negócio no bootstrap. Dependências de exemplos e ferramentas de verificação devem
ser analisadas individualmente no futuro fluxo de review.

## Verificações executadas e preservação

| Verificação | Resultado verificável |
|---|---|
| Biblioteca ativa, validador existente | Passou com pendências antigas documentadas; 101/21/2, 7 origens, 9 pacotes; zero erros |
| Duas aquisições add + reviews sem decisões | 10 descobertas pendentes; respostas review iguais às respostas add; `active_library_modified: false` |
| Integridade das inspeções e recursos | review_id revalidado pela API existente; 42 arquivos físicos iart e 39 mthines confrontados com índices/hashes Git usando source_bytes |
| Fechamento de recursos iart | 37 arquivos únicos; 66 verificações de referência, nenhuma não resolvida |
| Fechamento mthines | 25 arquivos; 91 verificações de referência, oito não resolvidas; bloqueios mantidos |
| Sintaxe JS em arquivo | 3 arquivos passaram no helper compartilhado check_javascript com Node global asdf 24.21.0, apenas --check |
| Sintaxe Shell | 3 arquivos passaram no helper compartilhado check_changed_scripts, bash -n; nenhum comando do corpo executado |
| Templates HTML | 4 inspecionados; 3 scripts inline passaram no parsing Node, um template sem script; scripts CDN não carregados |
| Baseline versionada | Todos os 1.110 arquivos rastreados mantêm hash e modo iguais às duas baselines de descoberta |
| Código, catálogo, locks, pacotes e consumidores | Nenhuma alteração executada; nenhuma cópia/promocão para Skills ativa |

Fingerprint das baselines (JSON canônico de caminhos, hashes e modos):
`74f29904e6809df80c738ff9ccd6c59e8b8cc7cacca7407c5b1408289b4bf87a`.
Os hashes individuais do fechamento e fingerprints de índices constam em resultado.json.
O Python executor foi o global asdf 3.14.8; não houve instalação ou alteração
da configuração. O parser sintático não resolve imports externos nem certifica
semântica, CSS, layout, comportamento de navegador ou performance. O fato de JS
parsear não elimina os bloqueios de distribuição da descoberta.

Não foram executados scripts, self-tests ou demos de fornecedores, builds,
playwright, bibliotecas de animação, agentes ou renderizações. A suíte de 273
testes não foi repetida: não houve modificação de código executável ou pacote ativo.
Também não se repetiram os 101 casos de cópia física já registrados na etapa anterior.
App-Web e consumidores não foram usados como ambientes de teste nem receberam
escritas; esta afirmação deriva do escopo das operações, não de uma auditoria
nova sobre seus diretórios.

## Decisão proposta e estado final

Priorizar para futura análise de incorporação **micro-interaction, svg-animation,
accessible-animation e 60fps-animation**. Considerar **gsap-web** para demandas
avançadas e **lottie-animation** para assets específicos. Manter ASCII, transições
Next.js e mthines pendentes; dispensar Glassmorphism nesta rodada por sobreposição.
As ressalvas de ferramentas, conteúdo e seleção precisam constar da futura revisão;
esta recomendação não afirma que exista plano aprovado ou pronto para aplicar.

Arquivos criados no repositório: este RELATORIO.md e resultado.json, somente
documentação/evidências. Duas sessões ignoradas foram criadas em .stacknauta-updates.
Arquivos auxiliares em /tmp: stacknauta-4b-library-before.json,
stacknauta-4b-{iart,mthines}-{add,review}.json, stacknauta-4b-static-checks.py e
stacknauta-4b-static-results.json. O script temporário apenas reuniu evidências
usando primitivas existentes e parsing; não introduziu mecanismo na aplicação.

Estado final do Git: HEAD inalterado; nenhum arquivo rastreado modificado;
somente os dois relatórios novos não rastreados neste diretório. Catálogo,
locks, nove pacotes e as classificações existentes permanecem intactos.
**Zero commits criados; nenhuma incorporação ou publicação.** O trabalho encerra
na descoberta para a decisão explícita do usuário sobre candidatas e pendências.
