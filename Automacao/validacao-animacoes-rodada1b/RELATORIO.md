# Etapa 4B — Rodada 1B: seleção e preparação

## Estado e escopo

Iniciada em 13/11/2026 no HEAD
`a035f50c3d890668b4817c3b32edad6274c6a344`. Havia somente os dois relatórios não
rastreados da [Rodada 1A](../validacao-animacoes-rodada1/RELATORIO.md); nenhum arquivo
rastreado estava modificado. Ambos foram preservados byte a byte e foram
versionados com esta rodada para permitir o driver de regressão em árvore limpa.

Hashes iniciais preservados:

- 1A/RELATORIO.md: `b2cb924e72aced7fc581b15eeec11f3e3b5472e27e358f7f4600368c2b3b21f7`.
- 1A/resultado.json: `225e2d446a3bb6d4adf335f1930c7af2e4bc37cfae549f70f05b91345e6bf408`.

Validação inicial: 101 aprovadas, 21 pendentes, duas excluídas, sete origens,
nove pacotes; zero erros, com pendências históricas documentadas. Nenhum pacote,
catálogo, lock, classificação ou projeto consumidor foi alterado. O executor
permanece Python global asdf 3.14.8, sem instalação ou configuração global.

## Código implementado e contratos

A causa era a seleção de todas as raízes aprovadas compatíveis em Library.select
quando skills era null, sem metadado para uma especialização opcional. Uma
fixture com duas skills tecnicamente equivalentes reproduziu esse resultado
usando o método do commit anterior. O primeiro teste com o novo campo, antes da
correção, falhou porque selection_mode ainda era desconhecido.

A extensão mínima está em **compatibility.selection_mode**, com valores:

- Ausente ou automatic: seleção histórica, sem migração ou mudança das 101 skills.
- explicit: requer ID solicitado; no automático gera omissão justificada.
- Outros valores: erro controlado, inclusive null, booleanos, listas e objetos.

A guarda vale também no fechamento. Uma raiz automática não consegue levar uma
dependência explicit por tabela; o conjunto é omitido com motivo. Em uma lista
explícita essa dependência também precisa constar nominalmente. Dependências
automáticas continuam transitivas. Não se elimina dependência nem se ignora
compatibilidade para completar uma seleção.

O código executável mudou somente em compatibility.py e library.py. O parser
compartilhado já usado pelo review/validador aceita o campo; a manutenção já
preserva compatibility nas atualizações. Não foi criado mecanismo separado de
aprovação, aquisição ou seleção por agente, nem lista de IDs no núcleo.

Semântica preservada: ausente/null usa automático; lista é o conjunto completo
de raízes; [] não seleciona skills; duplicatas são erro. UI/UX Pro Max não é
acrescentada a uma lista explícita que não a cite. IDs inexistentes, pendentes,
excluídos, dependências ou recursos ausentes/adulterados continuam bloqueados.
Seleção não dispensa ferramentas/runtimes, revisão do plano ou autorização.

Não foram alterados schemas de configuração, plano, lock ou manifesto, nem os
bytes iniciais históricos. O hash do catálogo já está no lock e no plano. Schemas
de consumidores 1 e 2 continuam usando evidências/seleção fixadas, preservando
hashes e arquivos evolutivos. A lista fixada é evidência histórica, não um novo
pedido de inclusão. Codex/OpenCode/Gemini recebem os mesmos resultados pelo motor
e integração existentes; nenhum agente foi executado ou teve seu adapter alterado.

Contrato detalhado: [SELECAO.md](../project-bootstrap/SELECAO.md).

## Testes específicos e regressão

**Executados e aprovados:** 22 testes novos do seletor, zero falhas/erros/skips,
mais dois testes novos da inclusão/atualização, também aprovados. Usam somente
catálogos, origens Git e consumidores sintéticos temporários. Os testes históricos
que aplicam inclusões usam autorização exclusivamente dentro dessas fixtures;
não aprovam qualquer candidata iart ou origem real.

Cobertura: legado sem campo; automatic; explicit não solicitado apesar de ui e
animation coincidirem; explicit solicitado/incompatível; pendente/excluído;
IDs ausentes/repetidos; lista mista e lista completa; ausente/null/[]; frontend
genérico e backend; fechamento automático e explícito; ferramentas/runtimes;
recurso ausente/adulterado; metadado inválido; dry-run determinístico e vinculado
ao catálogo; integração comum; idempotência; schemas 1/2, locks e evolutivos;
manifesto/lock/skill protegidos adulterados. A manutenção foi exercitada com
metadado válido, preservação após update e bloqueio de valor inválido.

**Regressão completa executada uma única vez e aprovada**, entre 13:58:28 e
14:00:08 UTC de 13/11/2026 (aproximadamente 100 segundos), no commit
`a2744bbaf48b5e56bdaad9ff6e45c5083e312389`:

```sh
Automacao/python-global Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4b1b-regressao-final.json --sem-smoke-fornecedor
```

| Grupo | Testes | Falhas / erros / skips |
|---|---:|---|
| Núcleo e ciclo de vida | 132 | 0 / 0 / 0 |
| Integração compartilhada | 16 | 0 / 0 / 0 |
| Atualizações, analisadores e segurança | 99 | 0 / 0 / 0 |
| Inclusões | 50 | 0 / 0 / 0 |
| **Total** | **297** | **0 / 0 / 0** |

São 273 históricos mais 24 novos; os testes direcionados já fazem parte desse
total e não são somados novamente. Nenhum teste automatizado ficou pendente.
Os testes visuais/nativos e smoke tests de fornecedor não foram solicitados.

O driver existente (cujo campo histórico stage ainda é 4A.1) criou
`/tmp/stacknauta-4a1-regression-88140gut/StackNauta`, sem _repos ou alternates,
com origin apontando para o repositório local e preservado até o fim. A árvore
do clone permaneceu limpa. A biblioteca passou: 101/21/2, sete origens, nove
pacotes, 958 arquivos de pacotes íntegros e sete JS parseados, sem executar vendor.
**101 casos de cópia física**, 4.114 arquivos copiados, incluindo verificações
adversariais de conteúdo adulterado, referência ausente e escape de caminho.
O modo sem-smoke-fornecedor foi respeitado: smoke tests não solicitados,
vendor_code_executed false. Não há alegação de validação visual de animações.
Logs e resultados completos estão em [resultado.json](resultado.json).

## Revisão das quatro candidatas

Origem fixa `https://github.com/iart-ai/web-animation-skills`, commit
`ed3a045192679b24d32090ee7a983871311ababd`. A sessão
`52b822d7ca934018abaa284e709e51e3` permanece disponível e seu review_id
`bfa0b1b8f3fb96ca230f783cd9f6ab9e0022c61e36ef027dd351abd872eb0541` foi revalidado.
Os 42 arquivos físicos da inspeção foram conferidos pelos índices Git e
source_bytes existentes, sem executar fornecedor. O fechamento das quatro
contém 18 arquivos únicos, com hashes individuais em [propostas.json](propostas.json).
Todas continuam pending, disabled e fora do catálogo ativo.

| Skill | Revisão e preparação | Situação para próxima decisão |
|---|---|---|
| micro-interaction | CSS é alternativa básica; React/Motion só para exemplos de gestos, spring e layout em stack já escolhida. Referências CSS/Framer intactas, sem dependência obrigatória em outra skill | Elegível para futura revisão individual com condições de execução documentadas; nenhuma aprovação |
| svg-animation | Referência svg-techniques íntegra. CSS/SMIL não exigem GSAP; MorphSVG/MotionPath/Flubber/SVGO são opções condicionais. Revisar browser, paths, filtros, custo de pintura e estado final estático | Elegível para futura revisão individual com condições documentadas; nenhuma dependência GSAP presumida |
| accessible-animation | Receita inconsistente confirmada: reset !important vence shorthand normal posterior. Orientação corrigida, diff e hashes preparados sem modificar origem | **Bloqueada para aprovação**: proposta ainda não é uma correção distribuível pelo fluxo de inclusão atual |
| 60fps-animation | Layout/paint/composite, batching, FLIP, profiling real e limites de will-change presentes. Texto contém simplificações de GPU/grid e “smooth at any frame rate”; não foram tratadas como garantias | Elegível para decisão de diagnóstico/otimização com ressalvas expressas; não certificada para FPS e sem correção silenciosa da prose |

Licença: MIT física da raiz, copyright iart.ai preservado, incluindo recursos
compartilhados; sem nova licença de asset no fechamento. Isso não licencia
bibliotecas/assets futuros nem autoriza instalá-los. Compatibilidade nativa e
ativação destas skills nos três agentes não foram exercitadas.

### accessible-animation e scripts compartilhados

[ORIENTACOES-PROPOSTAS.md](ORIENTACOES-PROPOSTAS.md) documenta a correção da
cascata, preferência de movimento, distinção de feedback essencial e controles
de pausa, sem promessa WCAG. [accessible-animation.proposta.diff](accessible-animation.proposta.diff)
tem antes `29d5fec1be9fa5e978738c313678974f61c06443e02ffce1bdc20434dfb0a767`
e depois `121c74e0c6deea14922f026bd2e95e61fa9450154f4c559180b2ef041ae713d4`.
O replay foi validado em memória pela primitiva existente. Não houve aplicação
na inspeção, distribuição, navegador ou teste de fornecedor.

A manutenção registra hashes/diffs e reaplica adaptações anteriores, mas a
inclusão nova só adapta contrato e caminhos de README/licença. Não oferece entrada
de patch arbitrário. Não foi contornado esse limite por edição de manifesto ou
por alteração da origem. É necessário um caminho rastreável autorizado para a
correção, ou upstream corrigido com revisão explicitamente autorizada, antes de
aprovar accessible-animation. Seu status não foi transformado em pronta.

LICENSE, scripts/README.md e os três .sh permanecem no fechamento. O contrato de
distribuição existente já proíbe instalação implícita e execução de shebangs.
O original seek-shot usa npx -y playwright e nomes previsíveis; contact-sheet
usa ffmpeg -y/cp e pode sobrescrever saídas; probe-mp4 depende de ffprobe/awk/head.
Pré-requisitos e efeitos estão documentados, sem inventar comandos substitutos.
Playwright/Chromium continuam não validados; nada foi instalado ou executado.
Distribuir arquivos não é autorização para executar, e a política não controla
toda execução futura de um agente. A rechecagem sintática dos mesmos scripts não
foi repetida: bytes preservados e evidências de parsing disponíveis na 1A.

## Metadados e operações não autorizadas

propostas.json contém as quatro políticas validadas por declared_policy e um
documento de decisões **pending**, validado em memória pelo validador existente.
Nenhuma decisão de aprovação foi criada ou enviada à CLI. Todas usam explicit;
linguagens JS/TS; frameworks web suportados alternativos; ui e animation.
accessible exige também accessibility; 60fps exige performance. Não se inferem
SVG ou intenção de diagnóstico de texto livre: a escolha nominal é necessária.
CSS não exige React/Motion. A lista conservadora de frameworks permite Vue,
Nuxt, Svelte e Astro, mas não presume projetos vanilla sem framework compatíveis;
estes precisam de política específica revisada, sem stack fictícia. Bibliotecas
de aplicação não aparecem como runtimes asdf.

gsap-web, lottie-animation, ascii-animation, page-transition-animation,
animations de mthines e glassmorphism não receberam propostas de aprovação,
mudanças de classificação, promoção ou nova aquisição.

Não há plan_id de incorporação. A CLI exige status approved nas decisões para
incluir arquivos num plano. Isso não foi simulado. Além disso, a sessão antiga
tem HEAD/baseline anteriores às alterações desta rodada: continua evidência
íntegra, mas não é válida para preparar/prometer uma promoção no código atual.
Não foi reescrito review_id, baseline ou hashes dessa sessão.

Somente após autorização individual futura, em árvore limpa:

```sh
Automacao/manutencao-skills/skills add https://github.com/iart-ai/web-animation-skills --ref ed3a045192679b24d32090ee7a983871311ababd
Automacao/manutencao-skills/skills review NOVA_SESSAO
```

Conferir novamente commit/fechamento/bloqueios e obter o novo review_id. Preparar
um JSON fora da candidata com schema_version 1 e skills por ID: para IDs realmente
autorizados e sem impedimentos, usar category Frontend, reason, compatibility,
requires_skills e prerequisites_review revisados a partir das propostas. Alterar
status para approved **somente após essa autorização**, sem liberar accessible
enquanto bloqueada. Então emitir apenas o dry-run:

```sh
Automacao/manutencao-skills/skills review NOVA_SESSAO --decisions /caminho/decisoes-autorizadas.json --review-id NOVO_REVIEW_ID
```

Esses comandos futuros não foram executados. O diff final deve ser lido também
quanto aos registros pendentes das demais descobertas da mesma origem. Hashes e
decisões técnicas não concedem autorização de promoção; esta continua separada.

## Preservação, arquivos, commits e limites

Nenhuma escrita em App-Web ou consumidores reais. Testes de aplicação ficaram
em destinos sintéticos temporários. Nenhum script de fornecedor, agente externo,
instalador ou atualização real foi executado. Não houve mudança de remotos reais,
configuração asdf, fontes, pacotes, licenças, catálogo ou locks ativos.

Arquivos de implementação: compatibility.py e library.py. Testes:
validacao-project-bootstrap/test_selection.py e validacao-inclusoes/test_additions.py.
Documentação técnica: project-bootstrap/SELECAO.md, README.md do núcleo e
manutencao-skills/INCLUSAO.md. Relatórios e propostas desta pasta; relatórios 1A
versionados sem alteração de bytes. Nenhum diretório ignorado, cópia de fornecedor
ou staging deve ser incluído no commit.

Commit de implementação/testes/documentação:
`a2744bbaf48b5e56bdaad9ff6e45c5083e312389` — feat: exigir seleção explícita para
skills especializadas. Inclui os relatórios 1A intactos. O commit documental
subsequente registra exclusivamente o resultado final desta rodada; seu hash
está no Git e na resposta de entrega. Nenhum commit de inclusão ou promoção.

A comparação final dos **1.004 arquivos rastreados de Skills/** com a baseline
inicial preservou todos os hashes e modos; git diff do diretório também ficou
vazio. Os relatórios 1A conservam os hashes acima. A árvore foi limpa antes da
regressão e será novamente limpa após registrar as evidências finais. Staging
ignorado permaneceu fora dos commits. Os arquivos executáveis do commit testado
não foram alterados depois da regressão; não há justificativa para repeti-la.

**Resultado: política implementada e validada; três candidatas preparadas para
futura revisão individual com as condições documentadas; accessible-animation
formalmente bloqueada. Nenhuma candidata aprovada ou promovida.**

Permanecem as limitações de análise estática, falta de execução visual/nativa,
escopo conservador dos frameworks propostos, receita acessível bloqueada e
dependências opcionais nunca automaticamente disponíveis. A extensão de seleção
não resolve problemas de execução, autorização ou qualidade dos fornecedores.
