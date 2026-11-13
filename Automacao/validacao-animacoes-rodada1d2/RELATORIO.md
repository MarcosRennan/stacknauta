# Etapa 4B — Rodada 1D.2: promoção concluída, regressão bloqueada

Executada em 13/11/2026. **O plano autorizado foi aplicado integralmente e a
biblioteca está íntegra com 104 skills aprovadas. A rodada não atingiu todos os
critérios de aceitação: a regressão completa apresentou seis falhas.** Nenhuma
correção fora do plano ou commit no repositório principal foi realizado. Os
arquivos publicados, o backup e as evidências foram preservados para diagnóstico.

## Estado inicial, autorização e plano

HEAD inicial e final: `f26e7256afe0c85c801b8d57622d70bd4513c54f`. Árvore inicialmente
limpa. Foram consultados AGENTS.md, a documentação da manutenção, os relatórios
1A/1B/1C/1D.1, o plano completo e seu diff. A autorização desta rodada permitia
aplicar exclusivamente o plano abaixo, condicionada à sua integridade.

| Identificador | Valor |
|---|---|
| Sessão | `55d27dfc7feb4ee6848c2fcdd1974295` |
| Review ID | `41a429d06233cee3111ebce8e5bc2c17d3a8406cd22748c3bc20c9f7dd35d94f` |
| Plan ID / hash oficial utilizado | `605ebf71270d2936dc4c13284d2a0c1f8389334aafe0062b449d9bac5d49a494` |
| Origem | `gh-iart-ai-web-animation-skills` |
| Upstream | `https://github.com/iart-ai/web-animation-skills.git` |
| Revisão fixada | `ed3a045192679b24d32090ee7a983871311ababd` |

A validação inicial confirmou 101 aprovadas, 21 pendentes, duas excluídas, sete
origens e nove pacotes, zero erros de integridade. A revalidação prévia executou
os seis testes de auditoria da 1D.1 sobre o estado atual: todos passaram, incluindo
51 cenários de seleção. Foram conferidos o review_id, a identidade oficial do
plano, HEAD e hashes/modos da baseline, árvore completa do candidato, diário
prepared, 42 arquivos adquiridos por SHA-256/Git blob, permissões, MIT e os 15
recursos únicos das três skills. O diff completo foi reconstruído e confrontado
com todos os bytes das 24 operações. Não houve divergência de escopo.

Os hashes upstream dos três SKILL.md coincidiram com os autorizados; os hashes
distribuídos coincidem com as adaptações contratuais já aprovadas:

| Skill | SHA-256 upstream | SHA-256 distribuído |
|---|---|---|
| micro-interaction | `f8ae0fc6137448bce51f689a13513a0a8742b1cbffa1b9f32ac723b46309e6e0` | `92b5976aef42d779b0fbd0214026fad1108b92d5dd724e17ecee997444bb264f` |
| svg-animation | `90e37f8f3d8c662515952de7a50c9130f5695d1a0cae1501115bd5d253c712c4` | `1d0c9520d23b9bb211c829b7775c6423321a2b9bb48c1b20b403f1be5f717cee` |
| 60fps-animation | `deb5d78aabae2289cbe161733be81aca6c3b4cd0940c0df3acf10196efdfe962` | `d54e95b0e5483f7a80866ef9914df683c72839ddbde70303c54be24e399e81b7` |

## Aplicação e estado transacional

Foi executado uma única vez, após a revalidação:

```sh
Automacao/manutencao-skills/skills apply 55d27dfc7feb4ee6848c2fcdd1974295 --plan-id 605ebf71270d2936dc4c13284d2a0c1f8389334aafe0062b449d9bac5d49a494 --approve
```

Retorno: status aplicado, resultado da origem incluida, mesmo plan_id. Diário
final **committed**; árvore ativa idêntica a candidate_tree. O backup
`.stacknauta-updates/55d27dfc7feb4ee6848c2fcdd1974295/previous-Skills/` permanece
preservado. Não houve falha transacional, recuperação ou reaplicação da promoção.
Não se tentou reverter uma transação committed em resposta a falhas dos testes.

Na conferência final, o backup também contém
`manutencao/__pycache__/biblioteca.cpython-314.pyc`, ignorado pelo Git e fora da
baseline rastreada, SHA-256
`5528002f2695efbd10807980a21f7dafda908178dec192aa14995eafc7b4afcf`.
Todos os 1.004 arquivos rastreados do backup coincidem com a baseline; não há
ausências ou alterações nesses arquivos. O cache estava na árvore antiga movida
pelo apply; sua origem e instante de criação não foram certificados nesta rodada.
Não foi removido. A comparação estrita de recuperação existente exclui _repos,
mas não esse cache, portanto um rollback automático que use esse backup exigiria
revisão manual. No estado committed atual, recover já recusa reversão deliberada.
Essa limitação adicional foi registrada, sem relaxar verificações ou modificar
o mecanismo. O cache não está na biblioteca ativa nem nas cópias verificadas.

Somente estes IDs passaram de ausentes para aprovados:

- gh-iart-ai-web-animation-skills:micro-interaction;
- gh-iart-ai-web-animation-skills:svg-animation;
- gh-iart-ai-web-animation-skills:60fps-animation.

**17 arquivos criados**, todos em `Skills/Frontend/gh-iart-ai-web-animation-skills/`:
15 recursos sob vendor/, README gerado e PROVENANCE.json. Os 15 recursos são
LICENSE; quatro arquivos em vendor/scripts/ (README e três .sh); README/SKILL.md
e patterns-and-profiling para 60fps; README/SKILL.md e duas referências CSS/Motion
para micro; README/SKILL.md e svg-techniques para SVG. Não há arquivos de outras
skills nesse pacote. Os três SKILL.md recebem somente contrato e caminho README
da adaptação existente, rastreados em hashes/diffs/proveniência. Recursos restantes
mantêm os bytes upstream; modos distribuídos 0644, inclusive Shell.

**Sete metadados alterados**, exatamente como no plano:

- Skills/Frontend/README.md;
- Skills/catalogo.json;
- Skills/fontes.lock.json;
- Skills/manutencao/distribuicao-politica.json;
- Skills/validacao/adaptacoes.json;
- Skills/validacao/arquivos.json;
- Skills/validacao/recursos.json.

O diff textual dos JSONs é amplo por serialização canônica. A comparação
semântica confirmou os **124 registros históricos intactos**, incluindo as 101
aprovadas, 21 pendentes e duas excluídas. Os **997 arquivos históricos fora dos
sete metadados autorizados** mantêm hashes/modos, incluindo UI/UX Pro Max. Nenhum
código de produto, seletor, integração, contrato de manifesto ou licença histórica
foi alterado. Fonte iart adicionada ao lock por commit, sem avanço implícito de branch.

## Biblioteca e cópias físicas

Validação ativa após a promoção: passou com pendências documentadas e zero erros.

| Item | Resultado real |
|---|---:|
| Skills aprovadas | 104 |
| Pendentes | 27 |
| Excluídas | 2 |
| Origens | 8 |
| Pacotes distribuíveis | 10 |
| Arquivos de pacotes verificados, sem contar manifestos | 974 |

As seis novas pendentes iart são accessible-animation, ascii-animation,
glassmorphism, gsap-web, lottie-animation e page-transition-animation. Permanecem
sem distribuição. A receita de accessible-animation não foi corrigida/aplicada;
mthines não foi incorporada. Nenhuma origem histórica foi atualizada.

Na execução final do validador em clone sem _repos/staging:

- **104 casos de cópia física aprovados**, cobrindo as 101 históricas e três novas;
- **4.145 arquivos copiados**;
- novas: 60fps 10 arquivos, micro 11, SVG 10; cada fechamento contém somente uma skill;
- MIT, recursos, hashes, referências locais e cópias físicas conferidos;
- testes adversariais de adulteração, referência ausente e escape passaram;
- sete JS históricos parseados, sem execução;
- smoke tests de fornecedor não solicitados; vendor_code_executed false.

Os auxiliares contact-sheet, seek-shot, probe-mp4 e README foram preservados;
não foram executados. Npx/Playwright/Chromium, Motion, GSAP e instalações npm não
foram utilizados. Seus riscos de download, nomes previsíveis e sobrescrita
ffmpeg -y continuam documentados nas rodadas anteriores. Cópia não autoriza execução.

## Bootstrap sintético e agentes

**Nove testes direcionados pós-promoção aprovados, zero falhas/erros/skips**, com
runtimes reais globais asdf Python 3.14.8/Node 24.21.0, apenas consultas/probes de
versão permitidos pelo harness. Os consumidores foram criados exclusivamente em
`/tmp/stacknauta-1d2-consumers-9cz3es4o/`, usando a biblioteca de um clone sem
staging/cache, com origin preservado. Não foram instaladas dependências.

| Cenário | Resultado executado |
|---|---|
| A — automático com ui/animation/performance e skills null | Somente UI/UX Pro Max; nenhuma das três especialistas |
| B — micro explícita | Skill isolada, recursos/licença/manifestos íntegros; arquivo evolutivo modificado legitimamente foi preservado |
| C — SVG explícita | Skill isolada e cópia completa |
| D — performance explícita | Skill isolada, requisitos presentes e cópia completa |
| E — quatro raízes explícitas (UI/UX + três novas) | Exatamente as quatro raízes e selecionadas; sem acréscimos automáticos |
| F — backend/incompatibilidade e ausência de performance | Rejeição controlada antes de criar destino |
| G — vanilla sem framework | Bloqueio conhecido confirmado; sem alteração de compatibilidade |
| H — React + React Native | Plano nominal aceito pelo seletor, alvo não discriminado; publicação **não executada** pelo procedimento de validação |
| Proteção adicional | Adulteração deliberada de skill no consumidor sintético bloqueou verify e foi preservada para diagnóstico |

Nos seis consumidores efetivamente criados (A–E e o caso de adulteração), a
reaplicação foi unchanged e preservou bytes, inode, permissões e mtime. Não houve
duplicação. Hashes dos locks e cópias, nlink 1, inodes independentes da biblioteca,
aliases portáveis e caminhos relativos foram verificados. O cenário H não criou
destino: o bloqueio foi do procedimento, **não uma garantia fornecida pelo núcleo**.
O contrato atual não permite distinguir com segurança o alvo nativo do web numa
entrada mista. Não se afirma integração segura para esse alvo ambíguo nem se
alterou o seletor. Vanilla e accessible-animation continuam fora da solução.

Integração **estrutural** validada para Codex CLI, OpenCode e Gemini: mesma seleção
do núcleo, entradas .agents/skills/stacknauta-*, cópias reais apontadas pelos aliases,
AGENTS, GEMINI.md e AGENT-INTEGRATION coerentes. **Descoberta nativa não executada;
ativação efetiva não testada.** Nenhum agente foi iniciado como subprocesso.

## Regressão completa — resultado bloqueante

O driver existente exige uma árvore Git limpa. Para não criar commits no
repositório principal antes das validações, foi preparado um clone temporário
com os 24 arquivos publicados e árvore Skills idêntica ao plano. Um commit de
fixture somente nesse clone (`b3da089d3c9d95edfd98865ebceb52d469c8d58b`) permitiu
usar o driver intacto. Árvore Git da fixture:
`e25b9ce7a25ec438f2805b1cc0dd2c56e168d0b5`.

O clone inicial preservou origin para o repositório principal. O driver criou
outro clone de verificação, `/tmp/stacknauta-4a1-regression-2iglxo6b/StackNauta`,
preservando seu origin para a fixture; sem _repos, alternates ou staging. Ao fim,
origin estava inalterado e a árvore desse clone limpa. A biblioteca testada é a
publicada; o HEAD principal continua f26e725 por ausência de commit após as falhas.

Na preparação estrita da fixture, Git recriou dois lançadores com 0755 enquanto
a baseline local registrava 0744, com bytes idênticos. Somente os modos da fixture
foram alinhados; Git conserva o bit executável, não todos os bits POSIX. A primeira
invocação do driver recusou a fixture ainda suja antes de executar qualquer teste.
Após o preparo, a **suíte completa executou uma única vez**, de 15:26:06 a 15:27:48
UTC (aproximadamente 102 segundos):

```sh
Automacao/python-global /tmp/stacknauta-1d2-validation-sbjbh6ao/StackNauta/Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4b1d2-regressao-final.json --sem-smoke-fornecedor
```

| Grupo | Executados | Aprovados | Falhas | Erros / skips |
|---|---:|---:|---:|---|
| Núcleo/ciclo de vida | 132 | 131 | 1 | 0 / 0 |
| Integração | 16 | 16 | 0 | 0 / 0 |
| Atualizações/analisadores/segurança | 99 | 97 | 2 | 0 / 0 |
| Inclusões | 50 | 47 | 3 | 0 / 0 |
| **Total** | **297** | **291** | **6** | **0 / 0** |

As cópias físicas e os nove testes direcionados são verificações separadas;
não foram somados para disfarçar a regressão. Não há teste pendente por bloqueio
ambiental na execução completa. Testes de fornecedor/nativos não foram solicitados.

### Seis falhas confirmadas

| Teste | Evidência e causa da expectativa incompatível |
|---|---|
| test_bootstrap.SelectionTests.test_every_approved_skill_has_an_explicit_policy — test_bootstrap.py:296 | Compara aprovadas a set(policies()), a lista legada. As três novas estão declaradas no catálogo, consumidas por catalog_policies/Library.rules, e não são adicionadas à lista hardcoded por projeto. O teste aponta exatamente os três IDs novos. |
| test_updates.UpdateTests.test_check_unchanged_is_read_only — test_updates.py:177 | Exige sete origens; a fixture agora possui oito. A origem nova é fixada por commit, portanto também tem estado revisao_fixada. |
| test_updates.UpdateTests.test_network_failure_is_not_reported_as_update — test_updates.py:245 | Exige erro_consulta para todas. A origem fixada não consulta rede por contrato. Diagnóstico somente leitura confirmou sete erro_consulta simulados e uma revisao_fixada. |
| test_additions.AdditionTests.test_existing_origin_reuses_identity_and_pending_metadata — test_additions.py:237 | Exige sete origens; observadas oito. |
| test_additions.AdditionTests.test_existing_full_acquisition_is_never_narrowed — test_additions.py:246 | Exige sete origens; observadas oito. |
| test_additions.AdditionTests.test_update_new_registered_origin_preserves_compatibility — test_additions.py:432 | Após acrescentar uma origem sintética, exige oito; observadas nove. |

O diagnóstico confirmou que **todas as 104 aprovadas têm política no catálogo
carregado pelo núcleo**. Os testes acima contêm expectativas históricas que não
cobrem essa extensão e a oitava origem fixada. **Eles não foram editados, excluídos,
ignorados ou reinterpretados como aprovados.** A regressão permanece failed.
Asserções posteriores ao primeiro assert falho de cada teste não são apresentadas
como verificadas. Nenhuma nova execução completa foi feita após as falhas.

## Preservação, Git e pendências

A publicação permanece committed, a árvore Skills coincide com o plano e o
backup está preservado. App-Web e consumidores existentes não receberam escrita;
nenhum foi usado como fixture. Os destinos sintéticos constam das evidências.
Essa afirmação decorre do escopo das operações, não de uma nova auditoria de
conteúdo dos diretórios externos. Configurações asdf, remotos reais, agentes,
licenças históricas e código do StackNauta não foram modificados.

**Nenhum commit no repositório principal**, conforme a seção 17 da autorização,
que proíbe commits de conclusão quando testes obrigatórios falham. O commit da
fixture temporária não publica nem registra a incorporação no repositório principal.
Não houve push, rebase, reset ou rollback deliberado.

Git final **não está limpo**: preserva as sete modificações de metadados e 17
arquivos novos exatamente da promoção, mais este RELATORIO.md e resultado.json
não rastreados. Isso é registrado como limitação da conclusão; não se criou um
commit ou desfez a promoção para ocultar o estado. Não há arquivos de staging ou
_repos adicionados ao índice. Não foi alterado o plano oficial.

Evidência consolidada: [resultado.json](resultado.json), com retorno CLI,
preflight, pós-publicação, cenários sintéticos, logs completos da regressão,
cópias físicas e diagnóstico. Os originais estão preservados em
`.stacknauta-updates/55d27dfc7feb4ee6848c2fcdd1974295/rodada1d2/` e /tmp; relatórios
1A/1B/1C/1D.1 não foram sobrescritos. Nenhum arquivo de fornecedor foi executado.

**Pendência bloqueante:** etapa específica autorizada para adequar os testes e
fixtures à política declarativa, à quantidade variável de origens e às revisões
fixadas; depois, nova regressão justificada pelas correções. Não modificar o
plano já aplicado para satisfazer asserções antigas. Discriminação web/nativo,
vanilla, accessible-animation, GSAP/Lottie e descoberta nativa continuam exigindo
decisões próprias. Esta rodada registra a promoção comprovada e a validação final
incompleta; não declara o trabalho integralmente aprovado.
