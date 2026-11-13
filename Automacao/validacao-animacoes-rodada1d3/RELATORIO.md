# Etapa 4B — Rodada 1D.3: regressão pós-promoção concluída

Executada em 13/11/2026. **298 testes automatizados aprovados, zero falhas,
erros ou skips; 104 conjuntos de cópia física aprovados.** As seis falhas da
1D.2 foram corrigidas exclusivamente nos testes. Não houve reaplicação da
promoção, alteração de código de produção ou edição da biblioteca nesta rodada.

## Estado inicial e preservação

HEAD inicial: `f26e7256afe0c85c801b8d57622d70bd4513c54f`.
A árvore estava legitimamente suja: sete metadados modificados, 17 arquivos
novos da promoção e dois relatórios não rastreados da 1D.2. Nenhuma diferença
inesperada foi encontrada. Essas alterações foram preservadas; os relatórios
1D.2 conservam seus hashes iniciais e o resultado histórico de seis falhas.

Referências: [relatório 1D.2](../validacao-animacoes-rodada1d2/RELATORIO.md),
[evidência 1D.2](../validacao-animacoes-rodada1d2/resultado.json), relatórios 1A/1B
versionados e artefatos 1C/1D.1 da sessão. Também foram consultados os contratos
e testes de manutenção, seleção, revisões fixadas e recuperação.

| Identificador | Valor confirmado |
|---|---|
| Sessão | `55d27dfc7feb4ee6848c2fcdd1974295` |
| Review | `41a429d06233cee3111ebce8e5bc2c17d3a8406cd22748c3bc20c9f7dd35d94f` |
| Plano já aplicado | `605ebf71270d2936dc4c13284d2a0c1f8389334aafe0062b449d9bac5d49a494` |
| Upstream iart-ai | `ed3a045192679b24d32090ee7a983871311ababd` |
| Diário real | `committed`, mesmo plan_id |

O hash oficial foi reconferido pela identidade e serialização utilizadas pela
manutenção, somente em leitura. A árvore ativa coincide com `candidate_tree`.
Não se executou `skills apply`, recuperação real, nova aquisição ou atualização.
Plano, diário, backup e conteúdo das skills não foram alterados.

## Diagnóstico individual das seis falhas

Os resultados anteriores abaixo são evidências da 1D.2 confrontadas com o código,
não uma nova execução completa antes das correções. Os nomes incluem módulo,
classe e função; os arquivos correspondentes estão listados depois da tabela.

| Teste completo | Esperado antes / obtido | Categoria e causa | Correção e contrato protegido |
|---|---|---|---|
| `test_bootstrap.SelectionTests.test_every_approved_skill_has_an_explicit_policy` | Aprovadas iguais aos 101 IDs de `policies()` / três IDs declarativos adicionais, total 104 | **A**: tabela legada confundida com regras efetivas do catálogo | Confere união das políticas legadas/declaradas, cobertura das aprovadas e equivalência das regras normalizadas; cada política histórica continua igual. |
| `test_updates.UpdateTests.test_check_unchanged_is_read_only` | Sete origens, todas `sem_alteracoes` / oito, sendo uma `revisao_fixada` | **A**: quantidade histórica e estado inadequado para origem fixada | Confere quantidade/IDs do registro, commit exato e revisão disponível conforme branch ou commit/tag; mantém igualdade da árvore e ausência de staging. |
| `test_updates.UpdateTests.test_network_failure_is_not_reported_as_update` | Todas `erro_consulta` / sete erros simulados e uma `revisao_fixada` | **C**: fixture inclui origem que não consulta rede | Simula falha nas branches; confere bloqueio, commits exatos, nenhuma revisão disponível e conjunto exato de origens consultadas. Pins não consultam rede nem viram atualização. |
| `test_additions.AdditionTests.test_existing_origin_reuses_identity_and_pending_metadata` | Sete origens / oito | **A**: contagem histórica | Compara registros completos de origens antes/depois; mantém preservação das skills não envolvidas e proveniência. |
| `test_additions.AdditionTests.test_existing_full_acquisition_is_never_narrowed` | Sete origens / oito | **A**: contagem histórica sem relação com aquisição esparsa | Compara registro completo antes/depois e mantém `sparse_paths == []`; aquisição completa não pode ser estreitada. |
| `test_additions.AdditionTests.test_update_new_registered_origin_preserves_compatibility` | Oito após adicionar uma sintética / nove | **A**: base histórica de sete | Confere quantidade inicial + 1 e conjunto exato de IDs com a nova origem; mantém igualdade da compatibilidade e validador integral. |

Arquivos alterados nesta rodada:

- `Automacao/validacao-project-bootstrap/test_bootstrap.py`;
- `Automacao/validacao-atualizacoes/test_updates.py`;
- `Automacao/validacao-inclusoes/test_additions.py`.

**Cinco casos A, um C; nenhum B ou D identificado.** Nenhum teste foi removido,
ignorado ou convertido para xfail. Não se trocaram simplesmente números por
oito/nove: os testes conferem identidade, conteúdo e contratos. Revisões, hashes,
proveniência e bloqueios continuam verificados. Não houve migração indiscriminada
das fixtures históricas ou alteração do seletor para satisfazer expectativas.

Adicionado `test_bootstrap.SelectionTests.test_new_approved_skill_without_declarative_policy_is_rejected`:
exige rejeição de nova aprovada sem compatibilidade declarada. Isso explica o
total de 298 e preserva o fechamento conservador.

## Verificações executadas nesta rodada

| Execução | Resultado |
|---|---|
| Direcionados: seis afetados, novo negativo, revisões fixadas e seleção explícita | **30 aprovados**, zero falhas/erros/skips; 6,333 s |
| Integração com catálogo publicado e consumidores temporários | **3 aprovados**, zero falhas/erros/skips; 1,710 s |
| Recuperação em duas árvores sintéticas independentes | Com cache: bloqueio conservador; sem extra: rollback verificado |
| Biblioteca ativa, leitura e sintaxe Node | `passed_with_documented_pending`, zero erros |
| Regressão completa | **298 aprovados**, zero falhas/erros/skips; uma execução |
| Cópias físicas no clone da regressão | **104 conjuntos aprovados**, 4.145 arquivos copiados |

Os grupos se sobrepõem e não são somados aos 298. Os nove testes de bootstrap
1D.2 são **históricos**; não se afirma que todos foram reexecutados nesta rodada.

### Seleção, distribuição e idempotência

Dois consumidores foram efetivamente criados somente em
`/tmp/stacknauta-1d3-consumers-idmvu4xb/`:

- Automático com `ui`, `animation`, `performance` e `skills: null`: somente
  `ui-ux-pro-max:ui-ux-pro-max`, nenhuma especialista.
- Combinado, UI/UX Pro Max e as três novas nominalmente: exatamente as quatro
  raízes e skills, sem acréscimos automáticos.

Criação, verificação e reaplicação passaram, com recursos, licenças, aliases,
locks e manifests íntegros. Reaplicação sem mudanças preservou bytes, inode,
modo e mtime; cópias físicas independentes foram conferidas.

O terceiro teste conferiu separadamente planos nominais de micro-interaction,
svg-animation e 60fps-animation: cada um selecionou somente sua raiz. Conferiu
bloqueio de accessible-animation pendente, de uma excluída histórica e de
performance sem a feature obrigatória. Esses casos individuais foram de
planejamento/exportação; cada fechamento físico foi validado nos 104 casos,
além da distribuição combinada.

As três políticas continuam `selection_mode: explicit`, JavaScript/TypeScript
e React/Next.js/Vue/Nuxt/Svelte/Astro. Micro/SVG exigem `ui` e `animation`;
performance exige também `performance`. Sem novas dependências obrigatórias de
skills, instalação automática ou relaxamento de compatibilidade. Sem alteração
das regras históricas ou da semântica das listas explícitas.

Codex CLI, OpenCode e Gemini receberam a mesma seleção nos testes estruturais.
**Estrutura e cópia física verificadas; descoberta nativa não executada e
ativação efetiva não testada.** Nenhum agente foi iniciado.

### Regressão completa e árvore testada

O driver exige Git limpo. Para preservar o working tree e adiar os commits
principais até a aprovação, utilizou-se um clone temporário com os 24 arquivos
do plano e os três testes corrigidos. O driver e o núcleo permaneceram intactos.

Fixture temporária: `d6d82f82eb7072ed2182f5561cf81d6cf89568e5`.
Árvore testada: `ba983dac1bfae89554915f036b0c1bcf0867bf73`.
Após os dois primeiros commits principais, **a árvore Git foi confrontada e é
idêntica à testada**. Somente na fixture foram alinhados dois modos de lançadores
0755 para 0744, como na baseline POSIX; bytes e bit executável Git não mudaram.

Comando executado uma vez:

```sh
Automacao/python-global /tmp/stacknauta-1d3-validation-9t936a6v/StackNauta/Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4b1d3-regressao-final.json --sem-smoke-fornecedor
```

| Grupo | Executados/aprovados | Falhas | Erros | Skips |
|---|---:|---:|---:|---:|
| Núcleo/ciclo de vida, incluindo schemas históricos | 133 | 0 | 0 | 0 |
| Integração | 16 | 0 | 0 | 0 |
| Atualizações/analisadores/segurança | 99 | 0 | 0 | 0 |
| Inclusões | 50 | 0 | 0 | 0 |
| **Total** | **298** | **0** | **0** | **0** |

De 16:18:48,382 a 16:20:28,441 UTC: **100,06 segundos**. O clone final
`/tmp/stacknauta-4a1-regression-6su8rk8g/StackNauta` preservou `origin` para a
fixture e terminou limpo; sem `_repos/`, staging ou alternates. A fixture preservou
`origin` para o principal. Remotos reais não foram alterados. Python 3.14.8 e
Node 24.21.0 globais do asdf, sem instalações.

As cópias cobrem as 101 históricas e três novas, com 974 arquivos de pacotes
verificados. Testes adversariais detectaram adulteração, referência ausente e
escape. Sete JavaScript foram somente parseados. Smoke tests do fornecedor não
foram solicitados; nenhum script de fornecedor foi executado.

## Biblioteca e integridade

| Estado confirmado | Quantidade |
|---|---:|
| Aprovadas | 104 |
| Pendentes | 27 |
| Excluídas | 2 |
| Origens | 8 |
| Pacotes distribuíveis | 10 |

Os **124 registros históricos** permanecem iguais: 101 aprovadas, 21 pendentes
e duas excluídas. Os **997 arquivos históricos fora dos sete metadados do plano**
mantêm hashes/modos. Locks, licenças, proveniência e fechamentos correspondem
integralmente ao plano; nenhuma outra origem foi atualizada.

Somente micro-interaction, svg-animation e 60fps-animation estão aprovadas na
origem nova. Accessible-animation, ascii-animation, glassmorphism, gsap-web,
lottie-animation e page-transition-animation continuam pendentes, sem distribuição.
A receita CSS bloqueada não foi adaptada/aplicada.

O pacote novo mantém 17 arquivos: 15 recursos únicos sob `vendor/`, README gerado
e PROVENANCE.json. Os sete metadados e seus diffs amplos por serialização canônica
são exatamente os já aplicados, não alterações desta correção. Inventário e hashes
upstream/distribuídos constam da evidência 1D.2 preservada; a igualdade completa
com `candidate_tree` foi reconferida nesta rodada.

## Parecer sobre o cache no backup

**Risco controlado — recuperação desse backup exige revisão manual.** Arquivo:

```text
/home/marcosrennan/Projetos/StackNauta/.stacknauta-updates/55d27dfc7feb4ee6848c2fcdd1974295/previous-Skills/manutencao/__pycache__/biblioteca.cpython-314.pyc
```

SHA-256: `5528002f2695efbd10807980a21f7dafda908178dec192aa14995eafc7b4afcf`.
Regular 0644, 9.459 bytes. Birth time: 12/11/2026 00:09:59,041999169 -03;
mtime: 12/11/2026 03:09:59,042846 UTC. Já existia antes da promoção de 13/11
e acompanhou a árvore antiga movida para backup.

O cabeçalho indica cache Python 3.14 por timestamp, fonte de 5.843 bytes e mtime
03:08:31 UTC de 12/11. A fonte efetiva do backup tem 5.945 bytes e mtime
03:22:29,968540 UTC; seus bytes coincidem com a fonte ativa. O cache está
desatualizado. Não foi carregado nem executado. Origem provável: importação ou
compilação Python anterior; comando/processo originais não determinados. Não há
evidência de criação pela promoção ou pelo processo desta rodada.

O lançador global usa `-I -S -B`; os pontos de entrada também inibem bytecode.
Uma importação de módulo próprio mínimo sintético pelo Python global com esses
flags não criou cache. Isso não identifica retrospectivamente seu autor nem
prova ausência de outros caminhos históricos de execução.

Todos os 1.004 arquivos rastreados do backup são íntegros, mas esse extra não
integra a baseline. A recuperação estrita exclui somente `_repos`; não aceita
qualquer ignorado como seguro. Em duas árvores sintéticas independentes:

1. Uma **cópia** do cache provocou `Backup alterado; recuperação manual necessária`;
   árvore e diário sintéticos permaneceram intactos.
2. Outro backup sintético íntegro, construído sem extra, permitiu recuperação,
   terminando `rolled_back`, restaurando bytes anteriores e preservando a árvore
   candidata recusada.

Nenhuma recuperação real foi executada. Arquivo, backup e diário reais permanecem
inalterados; `committed` não autoriza rollback deliberado. Não se classifica o cache
como inofensivo nem se confirma defeito de produção a corrigir nesta rodada.
Se recuperação automática desse estado for necessária, uma etapa própria deverá
definir tratamento comprovável de caches ignorados sem aceitar arquivos desconhecidos.
Não realizar limpeza ampla ou relaxar o validador. Persistência continua sujeita
às limitações documentadas de filesystem, fsync e hardware; sem atomicidade global.

## Limitações e consumidores

- Vanilla continua fora dos metadados por ausência de framework permitido.
- O seletor não discrimina com segurança web/nativo em React + React Native.
  Seleção explícita não resolve isso. Exigir alvo web inequívoco e não publicar
  em cenário misto ambíguo; não há garantia de bloqueio nativo pelo núcleo.
  A 1D.2 registrou plano aceito nesse cenário, sem publicação.
- Auxiliares Shell permanecem íntegros e não executados. Downloads via `npx -y`,
  Playwright/Chromium, nomes previsíveis e `ffmpeg -y` exigem revisão/autorização
  antes do uso. Distribuir não autoriza executar.
- Accessible-animation, GSAP/Lottie, vanilla e descoberta nativa continuam fora
  desta rodada.

App-Web e consumidores existentes não receberam escrita nem foram fixtures.
Essa evidência decorre das operações restritas aos testes, relatórios, Git e
diretórios temporários, não de auditoria forense dos diretórios externos. Nenhum
manifesto, skill, configuração ou aplicação de consumidor real foi alterado.
Sem instalações, execução de agentes, mudanças globais asdf ou push.

## Commits e fechamento

Somente após todas as validações, com staging explícito e revisão de diff:

1. `e3b6fdf4d5c9f51bbdf2aa32c5da6759547c473f`: incorporação, exatamente os 24
   arquivos do plano (17 novos e sete metadados), sem testes ou relatórios.
2. `de6c96a0aaf3d929de2191058afe9c7daed2d0eb`: somente os três arquivos de
   testes, seis adequações e um novo negativo; nenhuma biblioteca.
3. Commit documental deste relatório: somente os dois arquivos 1D.2 preservados
   e os dois arquivos 1D.3. Seu hash próprio é consultável sem autorreferência:

```sh
git log -1 --format=%H -- Automacao/validacao-animacoes-rodada1d3/RELATORIO.md
git status --porcelain --untracked-files=all
```

Após os commits 1/2, restavam apenas relatórios não rastreados. O fechamento
pós-commit documental confere árvore limpa e os três commits; o registro local
fica em `.stacknauta-updates/55d27dfc7feb4ee6848c2fcdd1974295/rodada1d3/fechamento-git.json`,
sem alterar novamente HEAD. Staging, backups e `_repos/` não integram commits.

Evidência persistente: [resultado.json](resultado.json), com logs completos da
regressão atual, testes direcionados, inventários, hashes e parecer do cache.
Artefatos adicionais permanecem na sessão; relatórios anteriores não sobrescritos.

**Parecer: Rodada 1D concluída, com ressalvas documentadas.** As expectativas
históricas foram adequadas sem reduzir controles; a biblioteca promovida está
íntegra e não há bloqueador de regressão remanescente identificado neste escopo.
As limitações acima exigem decisões próprias, não alterações silenciosas.
