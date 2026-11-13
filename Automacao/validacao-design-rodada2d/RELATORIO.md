# Etapa 4B — Rodada 2D: Frontend Design incorporada e validada

Executada em 13/11/2026. **Promoção transacional concluída, 298 testes da suíte
completa aprovados, dez testes direcionados de bootstrap aprovados e 105 conjuntos
de cópia física aprovados. Zero falhas, erros ou skips.** Somente Frontend Design
foi incorporada, como especialista de seleção nominal. As ressalvas de uso
permanecem documentadas; não houve validação comportamental dos agentes.

## Estado inicial e revalidação antes da aplicação

HEAD inicial: `63670f5a30a0960a56e9e88c51521aaec6ff981c`, branch `main`, Git limpo,
índice vazio e nenhuma operação Git incompleta. Nenhum commit posterior ao plano.
Foram consultados AGENTS.md, documentação real da manutenção, sintaxe de apply,
relatórios 2A/2B/2C e plano, diff e evidências 2C.1.

| Identificador | Valor confirmado e utilizado |
|---|---|
| Sessão | `1ec4c3395b1d4a97b108d8c471d98544` |
| Review ID | `481544cc5f580a2f90950309bacedb34bdad8034937c1b00c8d87c2d7f048e78` |
| Plan ID / hash oficial | `1c73b3b106c35ee9819f68357a87dad9c77af3fab6fcd3dde0c17fe19c2b0156` |
| Skill | `gh-anthropics-skills:frontend-design` |
| Origem | `https://github.com/anthropics/skills.git` |
| Revisão fixada por commit | `2c5958ecac7cee2b583967a2c4981d0f4a75c579` |

O preflight integral reconferiu identidade oficial e hash do plano, HEAD, hashes
e modos da baseline, review, commit Git adquirido, cinco arquivos materializados,
licença e fechamento de recursos. O JSON completo e todas as operações foram
revisados; o diff completo foi reconstruído com os bytes antes/depois e coincidiu
integralmente com o oficial. Nenhuma divergência de escopo foi encontrada.

O validador inicial passou, zero erros, com pendências históricas documentadas:
104 aprovadas, 27 pendentes, duas excluídas, oito origens e dez pacotes.
A autorização desta rodada foi vinculada ao hash acima; não se gerou plano
substituto, mudou decisão ou adquiriu outra revisão.

## Recursos, licença e transformação contratual

| Arquivo | SHA-256 |
|---|---|
| SKILL.md upstream | `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3` |
| SKILL.md distribuído | `771c8727f834a627e79eb134ae9d2ff2b684e9e24a64e45ff6b8c01c502540cd` |
| LICENSE.txt upstream/distribuído | `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` |

Os dois recursos adquiridos são `skills/frontend-design/SKILL.md` e
`skills/frontend-design/LICENSE.txt`, respectivamente 9.390 e 10.174 bytes,
modo Git 100644. Apache-2.0 confirmada no diretório da skill; licença e avisos
aplicáveis preservados. O original adquirido não foi alterado.

A diferença da cópia distribuída é somente o contrato padrão StackNauta de
execução/asdf e o link relativo ao README, já presente no plano autorizado e
rastreado por hashes, diff e proveniência. Nenhuma instrução criativa, regra de
precedência visual ou correção de conteúdo foi inserida no fornecedor. O pacote
contém os dois recursos, README gerado e PROVENANCE.json, todos físicos 0644.
Não há script, instalação ou dependência obrigatória de outra skill.

## Aplicação e estado transacional

Após todas as verificações, foi executada **uma única tentativa**:

```sh
Automacao/manutencao-skills/skills apply 1ec4c3395b1d4a97b108d8c471d98544 --plan-id 1c73b3b106c35ee9819f68357a87dad9c77af3fab6fcd3dde0c17fe19c2b0156 --approve
```

Retorno CLI **0**, `status: aplicado`, origem com `resultado: incluida` e mesmo
plan_id. Diário final **committed**. A árvore ativa corresponde integralmente a
`candidate_tree`. Não houve recuperação, reaplicação da promoção ou sucesso parcial.
O estado committed significa conclusão transacional de filesystem; os commits
Git foram criados somente depois das validações obrigatórias.

Backup desta promoção:
`.stacknauta-updates/1ec4c3395b1d4a97b108d8c471d98544/previous-Skills/`.
Seus 1.021 arquivos coincidem exatamente com a árvore ativa inicial, sem extras.
Nenhum backup ou artefato transacional foi apagado.

## Arquivos efetivamente incorporados e preservação histórica

**Quatro arquivos criados**, sob `Skills/Frontend/gh-anthropics-skills/`:

```text
PROVENANCE.json
README.md
vendor/skills/frontend-design/LICENSE.txt
vendor/skills/frontend-design/SKILL.md
```

**Sete metadados alterados**, exatamente os previstos:

```text
Skills/Frontend/README.md
Skills/catalogo.json
Skills/fontes.lock.json
Skills/manutencao/distribuicao-politica.json
Skills/validacao/adaptacoes.json
Skills/validacao/arquivos.json
Skills/validacao/recursos.json
```

Catálogo acrescenta somente Frontend Design, origem e pacote. Lock registra a
origem `gh-anthropics-skills` fixada no commit autorizado. Política, índices,
adaptação e proveniência refletem esse conjunto; os hashes de geração são coerentes.
Nenhum arquivo foi removido. Nenhuma origem histórica foi atualizada.

Comparação semântica e de bytes confirmou **133 registros históricos intactos**,
incluindo 104 aprovadas, 27 pendentes e duas excluídas. Os **1.014 arquivos
históricos fora dos sete metadados** mantêm hashes e modos. UI/UX Pro Max e as
três especialistas de animação permanecem intactas. Nenhum núcleo, teste de
produção, integração ou contrato de manifesto foi editado.

| Indicador confirmado pelo validador ativo | Resultado |
|---|---:|
| Aprovadas | 105 |
| Pendentes | 27 |
| Excluídas | 2 |
| Origens | 9 |
| Pacotes distribuíveis | 11 |
| Arquivos de pacotes verificados, sem manifestos | 977 |

As demais candidatas Anthropic não foram incorporadas. Vercel, Impeccable e as
animações pendentes não receberam decisões novas. Accessible-animation continua
pendente e sem distribuição. Os números acima foram observados após a aplicação,
não impostos manualmente para alcançar a projeção.

## Seleção, compatibilidade e precedência visual

Metadados publicados: categoria `Frontend`, JavaScript ou TypeScript, alternativas
React/Next.js/Vue/Nuxt/Svelte/Astro, feature obrigatória `ui`, `selection_mode:
explicit`, sem `requires_skills`. Ferramentas/runtimes extras vazios; as linguagens
continuam sujeitas aos runtimes globais do núcleo. Nenhuma dependência é instalada.

No automático, Frontend Design não é acrescentada por frontend, ui ou animation.
Na lista explícita, apenas as raízes solicitadas e suas dependências reais são
consideradas. UI/UX não se torna dependência de Frontend Design, nem vice-versa.
Foram ainda verificadas em leitura as 12 combinações JS/TS × seis frameworks na
biblioteca ativa: seleção nominal correta, sem criar consumidores adicionais.

A precedência foi transportada no cenário I em `requirements.constraints`:
requisitos explícitos; decisões/Design System aprovados; UI/UX e convenções
aplicáveis; exploração criativa complementar. Identidade sintética Portal Orion
Estudos, paleta `#1F3D5B/#FFFFFF/#18212B`, tipografia system-ui e componentes
AppHeader/PrimaryButton/FormField foram declarados como aprovados, sem implementar
uma interface de aplicação. As strings foram preservadas em requisitos, config,
agent-plan e manifesto do consumidor.

Esse resultado comprova **transporte estrutural**, não obediência do agente.
A orientação deve integrar o contexto autorizado; não é injetada automaticamente
por selection_mode nem concede permissão de redesenhar identidade aprovada.
Nenhum agente foi executado ou avaliado esteticamente.

Vanilla permanece bloqueado pelos metadados conservadores. React Native isolado
também é rejeitado. A configuração mista React + React Native é aceita pelo
predicado sem discriminação segura de alvo: **nenhum consumidor desse caso foi
publicado**. O bloqueio foi do procedimento de validação, não uma garantia do
núcleo. Exigir alvo web inequívoco; não se ampliou compatibilidade nesta rodada.

## Testes direcionados A–J

**Dez testes aprovados**, zero falhas, erros ou skips, 3,259 s. Consumidores
somente em `/tmp/stacknauta-2d-consumers-3c1opnl7/`, utilizando a biblioteca de
um clone local sem staging/cache. Nenhum consumidor real foi usado como fixture.

| Cenário | Resultado efetivamente executado |
|---|---|
| A — automático | Somente UI/UX Pro Max; Frontend Design e animações explícitas ausentes |
| B — Frontend Design nominal | Somente a solicitada; quatro arquivos do pacote, licença, lock, alias e hashes íntegros |
| C — UI/UX isolada | Somente UI/UX, sem Frontend Design implícita |
| D — combinação | Exatamente as duas raízes, 82 arquivos de recursos; sem duplicação/dependência implícita |
| E — incompatível | Backend Express e ausência de ui rejeitados antes de criar destino |
| F — vanilla | Bloqueio conhecido confirmado, sem alteração de metadados |
| G — mobile nativo | React Native isolado rejeitado |
| H — misto | Plano aceito pelo predicado, alvo não discriminado; consumidor não criado |
| I — identidade aprovada | Requisitos e decisões visuais preservados nos documentos e manifesto; sem teste comportamental |
| J — idempotência/evolução | Reaplicação preserva arquivos; package.json evoluído não é sobrescrito; adulteração de skill protegida bloqueia verify e é preservada |

Nos seis consumidores criados (A/B/C/D/I/J), criação, verify e reaplicação passaram.
Reaplicação unchanged preservou bytes, inode, modo e mtime. Não houve duplicação.
O caso J mantém a adulteração deliberada somente no consumidor temporário como
evidência negativa. A promoção da biblioteca não foi repetida para testar idempotência.

Recursos foram conferidos por hash, nlink 1 e inodes/dispositivos distintos da
biblioteca; sem symlinks ou caminhos operacionais de staging/cache. Runtimes
consultados pelo harness: apenas probes permitidos do asdf global, Python 3.14.8
e Node 24.21.0. Nenhum fornecedor, npx, pip, build ou serviço foi executado.

## Distribuição física e agentes

Validador existente executado no clone com `--copias --sintaxe-node
--sem-smoke-fornecedor`: **105 conjuntos físicos aprovados**, cobrindo as 104
históricas e Frontend Design; **4.149 arquivos copiados**. Os testes adversariais
detectaram adulteração de conteúdo, referência ausente e escape de caminho.
Os sete JavaScript históricos foram somente parseados. Smoke tests de fornecedor
não solicitados; `vendor_code_executed: false`.

O clone `/tmp/stacknauta-2d-validation-zjq16ruf/StackNauta` preservou `origin`
para o repositório principal; sem `_repos/`, staging ou alternates. Seus arquivos
correspondem aos publicados. Git recriou dois lançadores como 0755; somente no
clone foram alinhados a 0744, como na fonte. Nenhum arquivo/modo do produto foi
alterado por esse preparo. Não houve mudança de remoto real.

Integração **estrutural** validada para Codex CLI, OpenCode e Gemini: aliases
`.agents/skills/stacknauta-*`, links relativos corretos para os SKILL.md completos,
licenças/recursos físicos e locks, AGENTS, GEMINI.md e AGENT-INTEGRATION coerentes.
Os três usam o núcleo compartilhado. **Descoberta nativa não executada; ativação
e obediência criativa não testadas.** Cópia de Markdown não comprova esses resultados.

## Regressão completa, uma execução

Depois dos testes direcionados e da cópia física, foram executados uma vez os
quatro executores de unittest da definição canônica
`Automacao/validacao-correcoes-funcionais/executar_testes.py`. A lista foi extraída
do próprio driver, sem editar código de produção. A etapa biblioteca já concluída
foi registrada com seu resultado real, sem repetir as 105 cópias. Todos os nove
módulos `test_*.py` canônicos pertencem a esses quatro executores.

| Grupo | Executados/aprovados | Falhas | Erros | Skips |
|---|---:|---:|---:|---:|
| Núcleo e ciclo de vida, incluindo schemas históricos | 133 | 0 | 0 | 0 |
| Integração comum | 16 | 0 | 0 | 0 |
| Atualizações, analisadores e segurança/recuperação | 99 | 0 | 0 | 0 |
| Inclusões | 50 | 0 | 0 | 0 |
| **Total** | **298** | **0** | **0** | **0** |

De 19:37:37,369 a 19:39:13,500 UTC: **96,131 s**. Os dez testes direcionados e
105 casos de cópia são verificações separadas; não foram somados aos 298.
Nenhum teste foi alterado, removido, ignorado ou convertido em xfail.

Comandos e logs completos constam de [resultado.json](resultado.json). A
orquestração própria ficou apenas em staging e usou os executores existentes:

```sh
Automacao/python-global .stacknauta-updates/1ec4c3395b1d4a97b108d8c471d98544/rodada2d/test_bootstrap_temporario.py
Automacao/python-global /tmp/stacknauta-2d-validation-zjq16ruf/StackNauta/Skills/validacao/validar_biblioteca.py --copias --sintaxe-node --sem-smoke-fornecedor
Automacao/python-global .stacknauta-updates/1ec4c3395b1d4a97b108d8c471d98544/rodada2d/executar_regressao.py
```

A regressão utilizou commit de **fixture temporária**, exclusivamente no clone,
`dc6b93b8923af89147c06680fb147ffc8b0cddfd`, sem antecipar commit de conclusão no
repositório principal. Sua árvore `178369fa7e48c82e87b14d39303247b685f2ef36` é
**idêntica à árvore do commit real de incorporação**, conferida após todos os
testes. O clone terminou limpo e com origin inalterado. Nenhum teste foi repetido
para aumentar contagem de aprovações.

## Commits e fechamento do Git

Após transação, integridade, bootstrap, cópias e regressão aprovados, o diff e
índice foram conferidos com staging explícito:

1. `30498580ac22e0a4cf119b74eaefd1ce6c835131` — incorporação, somente os 11
   arquivos do plano, 1.028 inserções e 11 remoções textuais de metadados;
   sem relatório, código de produção ou teste modificado.
2. Commit de evidências — somente este RELATORIO.md e resultado.json. Seu hash
   é informado na resposta final, sem referência circular no próprio commit.

Após o primeiro commit, Git estava limpo e a árvore igual à testada. O segundo
versiona exclusivamente os dois relatórios. A conferência final do Git e os dois
hashes ficam no registro local
`.stacknauta-updates/1ec4c3395b1d4a97b108d8c471d98544/rodada2d/fechamento-git.json`,
sem outro commit para inserir o próprio hash. A consulta do commit documental é:

```sh
git log -1 --format=%H -- Automacao/validacao-design-rodada2d/RELATORIO.md
git status --porcelain --untracked-files=all
```

Staging, backups, caches, _repos e consumidores sintéticos não integram commits.
Não houve push ou alteração de configurações globais/remotos.

## Preservação e limitações remanescentes

App-Web e consumidores existentes não foram destinos de escrita. Nenhum
manifesto, lock, configuração, skill ou decisão visual de projeto antigo recebeu
atualização retroativa. Essa evidência decorre do escopo das operações e dos
destinos temporários, não de uma auditoria forense dos diretórios externos.

O backup legado da sessão `55d27dfc7feb4ee6848c2fcdd1974295` continua preservado,
inclusive `biblioteca.cpython-314.pyc`, SHA-256
`5528002f2695efbd10807980a21f7dafda908178dec192aa14995eafc7b4afcf`.
Sua eventual recuperação estrita exige revisão manual, como documentado antes.
Ele é distinto do novo backup exato, sem extras, desta promoção. Nenhuma
recuperação real foi executada ou mecanismo de recuperação alterado.

Vanilla, discriminação web/nativo e avaliação comportamental dos agentes continuam
pendências separadas. A documentação/seleção explícita não controla toda ação
futura de um agente. Não há promessa de atomicidade global ou tolerância absoluta
a falhas de hardware/energia além das garantias documentadas de filesystem,
fsync e diário.

**Parecer: Rodada 2D concluída com ressalvas documentadas.** A skill está
incorporada como especialista opcional; integridade, seleção, distribuição e
regressão passaram. Uma avaliação criativa real dos agentes poderá ser planejada
em etapa própria. Nenhuma nova funcionalidade ou ampliação de compatibilidade
foi implementada.
