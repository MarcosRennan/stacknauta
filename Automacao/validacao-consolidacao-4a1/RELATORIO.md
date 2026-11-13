**StackNauta — Etapa 4A.1, Fase 3: consolidação final**

**Parecer: Não apto para iniciar a inclusão real da Etapa 4B nesta revisão.**
Uma regressão P2 foi confirmada no parsing de JavaScript da manutenção: um `.js`
válido para o Node global é recusado quando o tipo do pacote não está declarado.
É relevante para a próxima fase de frontend e deve ser tratada antes da aplicação
de novas inclusões. Nenhuma correção foi feita nesta consolidação.

A preparação da documentação de instalação pode começar. A publicação posterior
no GitHub deve aguardar essa correção e a revisão documental indicada abaixo.
A biblioteca atual permanece íntegra. A revisão também identificou um falso
positivo Python P3, sem evidência de dano ou modificação dos pacotes existentes.

**Base e rastreabilidade**

HEAD inicial: `c8252976af415f39efd08ca80be6fc94bc7fed04`. A árvore estava limpa.
Os arquivos alterados nas fases anteriores estão presentes e foram inspecionados.
Não foram encontradas alterações não documentadas entre o candidato testado da
Fase 2 e o HEAD inicial: a diferença contém somente seu relatório e JSON.

| Marco | Commit | Evidência |
|---|---|---|
| Implementação A01–A04 | `690b745` | [Fase 1](../validacao-correcoes-funcionais/RELATORIO.md) e seu JSON |
| Evidências da Fase 1 | `b50fda1` | 203 testes registrados |
| Implementação A05–A07 | `ee2bb5c` | [Fase 2](../validacao-seguranca-recuperacao/RELATORIO.md) e seu JSON |
| Evidências da Fase 2 / HEAD revisto | `c825297` | 242 testes registrados |

Os relatórios foram confrontados com os logs, os nomes dos testes no código
atual e os commits. Não foi localizada uma cópia separada da auditoria original
4A; os achados fornecidos no pedido e os registros das fases anteriores definiram
o escopo. Os resultados estruturados desta inspeção estão em
[resultado.json](resultado.json).

**Revisão individual de A01–A07**

| Achado | Estado | Confronto com código, testes e limites |
|---|---|---|
| A01 | **Resolvido** | A condição que recusava qualquer remoto foi removida de `Skills/validacao/validar_biblioteca.py`. O teste `test_origin_does_not_disable_integrity_validation` cobre clone com origin, ausência de remoto, SSH/HTTPS e adulteração. Os dois relatórios finais registram clone com origin preservado. O driver histórico de clone ainda tem uma restrição própria; ver D03. |
| A02 | **Resolvido com ressalvas** | O fallback indiscriminado para o inicializador foi substituído por `relative_python_resources`, em `atualizacao_receita.py:59`, chamado na inclusão e atualização. Os testes cobrem ausência, níveis, pacotes, homônimos e fluxos válidos sem executar módulos. Exports dinâmicos e existência de símbolos não têm certificação semântica completa. Foi confirmado o falso positivo adicional R02. |
| A03 | **Resolvido com ressalvas** | `core.py:138` lê a seleção e o lock fixados; `filesystem.py:247` verifica a vinculação ao manifesto. A reexportação confronta recursos e origens, preservando os hashes globais históricos. Testes cobrem deriva do catálogo, inclusão compatível, outra origem, schemas 1/2 e adulterações. Se os recursos/proveniência históricos não forem reproduzíveis, o bloqueio conservador permanece, sem reescrever manifestos. |
| A04 | **Resolvido** | `atualizacoes.py:566` diferencia `incluida`, `atualizada` e ausência de mudança; recusas e falhas de promoção têm resultados distintos na CLI. Testes de inclusão, atualização, JSON da CLI, rollback e idempotência estão nos logs. `falha_aplicacao` é uma extensão documentada do contrato. |
| A05 | **Resolvido com ressalvas** | `finish`, `apply`, `sync_tree` e `_recover` persistem dados/diretórios antes dos respectivos registros finais. Backups e árvores recusadas são preservados. Testes verificam a ordem, falhas de escrita/sincronização, diários antigos e recuperação conservadora. O diário não oferece atomicidade global nem garantia absoluta contra falhas de hardware. |
| A06 | **Resolvido com ressalvas** | `filesystem.py:191` usa `O_TMPFILE`, fsync e publicação do descritor com um único nome final. Os 11 testes cobrem interrupções e preservação de finais. Temporários legados sem prova não são apagados. Linux/procfs/filesystem compatíveis são requisitos; indisponibilidade bloqueia sem fallback inseguro. |
| A07 | **Resolvido com ressalvas** | As proteções contra caminhos inseguros foram implementadas com descritores, no-follow/nonblock, fstat e rename sem substituição. Os testes incluem symlinks, hardlinks, FIFO e substituições concorrentes. Concorrência hostil irrestrita do mesmo usuário continua fora da garantia. A mudança do parsing por stdin introduziu R01, uma regressão funcional que bloqueia o parecer global de avanço. |

Referências de implementação: [manutenção](../manutencao-skills/atualizacoes.py),
[imports](../manutencao-skills/atualizacao_receita.py),
[inclusões](../manutencao-skills/inclusoes.py),
[núcleo](../project-bootstrap/stacknauta_core/core.py) e
[filesystem](../project-bootstrap/stacknauta_core/filesystem.py).
Os limites principais estão documentados em
[INCLUSAO.md](../manutencao-skills/INCLUSAO.md),
[manutenção](../manutencao-skills/README.md) e
[ciclo de vida](../project-bootstrap/CICLO-DE-VIDA.md).

**Pendências confirmadas nesta revisão — sem correção automática**

**R01 — P2, regressão no parsing de `.js` sem tipo declarado; bloqueador da 4B.**
Em `atualizacoes.py:433–442`, o tipo inicial é CommonJS e permanece assim quando
não existe `package.json`. O Node global instalado foi usado apenas como parser:

```javascript
export const value = 1;
throw new Error("must never execute");
```

Em um diretório temporário sem declaração de tipo, inclusive nos ancestrais
externos, `node --check arquivo.js` retornou **0**. Para os mesmos bytes,
`Updates.check_changed_scripts` lançou `ValueError` com `Unexpected token 'export'`
ao usar `--input-type=commonjs` por stdin. Nenhum script foi executado.
O caso reproduz a diferença em relação à forma anterior de parsing; o Git atribui
essa mudança ao commit `ee2bb5c`. O fluxo de preparação chama esse método e pode
bloquear inclusões/atualizações válidas. Não foi realizada uma inclusão real.

O teste existente cobre `.js` com `type: module` e `.cjs`; não cobre a ausência de
tipo. O tratamento posterior deve preservar a leitura segura e a semântica de
parsing dos formatos suportados, com teste específico; não deve voltar a abrir
caminhos inseguros para contornar a recusa.

**R02 — P3, export estático por desempacotamento não reconhecido.**
Com `helper, other = 1, 2` em `pkg/__init__.py`, o import válido
`from . import helper` em `pkg/main.py` é recusado como dependência ausente/ambígua.
`explicit_export` (`atualizacao_receita.py:93`) só reconhece alvo `ast.Name` para
atribuições; o alvo desse exemplo é `ast.Tuple`. A reprodução chamou somente o
analisador com bytes em memória, sem executar módulos. É uma limitação conservadora
adicional a registrar no contrato e considerar em futura manutenção. Não foi
comprovado impacto em uma skill real; não é o bloqueador principal desta entrega.

**A08 — P3, mantido pendente.** O driver de regressão ainda usa `assert` em
checagens de clone (`executar_testes.py:35`). A execução registrada utiliza os
launchers isolados e comandos sem `-O`. O achado não foi implementado nem usado
para descartar os resultados existentes.

**Arquitetura e contratos**

A separação permanece reconhecível: biblioteca versionada fornece seleção e
recursos; bootstrap cria/verifica consumidores; manutenção prepara candidatos e
promove somente a biblioteca. A integração delega ao núcleo e usa entradas rasas
para as três famílias de agentes. Não há um segundo motor de bootstrap.

A manutenção reutiliza primitivas de diretórios do núcleo; os helpers locais
tratam staging, sincronização e registros. Não foi encontrada dependência Python
externa nova: ctypes é parte da biblioteca padrão, com dependência operacional
da libc/renameat2. Os launchers continuam escolhendo exclusivamente o Python
global instalado do asdf, sem instalação automática.

Os comandos documentados de plan/apply/agent-plan/agent-apply/agent-verify e
check/update/add/review/apply/recover correspondem ao despacho atual. Revisão de
dry-run, hash, autorização e revalidação continuam presentes. Schemas 1/2 e a
política de arquivos evolutivos permanecem cobertos. A exceção de compatibilidade
funcional identificada é R01; não há motivo para uma refatoração geral nesta fase.

**Biblioteca e cobertura comprovada**

A conferência somente de leitura confirmou **101 aprovadas, 21 pendentes, duas
excluídas, sete origens e nove pacotes**. Foram verificados hashes, tamanhos e modos
dos 958 arquivos de pacote, mais os nove manifestos PROVENANCE: 967 artefatos
físicos. Os contadores históricos de 958 excluem esses nove manifestos; não há
divergência de inventário. Também foram confrontados 950 registros de entrada e
102 hashes de adaptações. Há 13 arquivos com nomes iniciados por LICENSE,
COPYING ou NOTICE nos pacotes; esse filtro de nomes não pretende contar todas
as formas de licença incorporadas aos recursos verificados.

Catálogo e lock concordam em URLs/commits. Hashes de receita, política e lock
conferem. Toda a árvore Skills é idêntica à base da Fase 2; desde antes da Fase 1,
a única alteração sob Skills é o validador de A01. Não se consultou `_repos`.
As evidências anteriores de clones sem cache e cópias físicas permanecem
aplicáveis ao mesmo código/recursos. Não há atualização automática de consumidores.

| Evidência versionada | Núcleo | Integração | Atualizações | Inclusões | Total |
|---|---:|---:|---:|---:|---:|
| Fase 1 | 99 | 16 | 42 | 46 | 203 |
| Fase 2 | 110 | 16 | 69 | 47 | 242 |

Os totais coincidem com as linhas `ok` dos logs; todas as suítes registram zero
falhas, erros e skips. Não se somam 203 e 242. As duas evidências registram 101
casos de cópia física, 958 arquivos verificados e origin preservado no clone.
O probe Btrfs da Fase 2 comprova sucesso nominal das primitivas e sincronizações,
sem teste de queda de energia. Seu registro foi conferido, não reexecutado.

**Nenhuma suíte completa foi repetida nesta fase.** Houve apenas inspeção de Git,
AST, registros/hashes e os dois casos direcionados acima. Eles identificaram
falhas de cobertura/comportamento e não representam duas novas aprovações para
somar aos 242 testes. Os logs verdes comprovam os casos executados; R01 e R02 são
casos adicionais fora daquela cobertura.

**Evidências dos agentes**

| Agente | Implementação e descoberta estática | Descoberta nativa | Ativação/uso efetivo | Bootstrap |
|---|---|---|---|---|
| Codex CLI | Implementados; arquivos de descoberta inalterados | Renderizador nativo comprovado no registro 2B, versão 0.167.2 | Leitura/uso explícito na sessão ativa documentados; ativação automática em sessão nova não comprovada nesse registro | Plan/apply/verify de Python/FastAPI e TypeScript/Next.js comprovados nos temporários históricos |
| OpenCode com DeepSeek | Implementados pelo procedimento e aliases compartilhados | Marcos do teste posterior não verificáveis nos artefatos locais | Testes posteriores relatados pelo usuário; sem relatório acessível para separar os marcos | Não se atribui sucesso/fracasso documental sem o artefato posterior |
| Gemini CLI / Antigravity | Integração Gemini e descoberta estática implementadas | Ambiente e descoberta do teste posterior não verificáveis localmente | Testes posteriores relatados pelo usuário; separar CLI/Antigravity quando incorporar a evidência | Não se infere o resultado específico de cada ambiente sem registro |

Fonte local: [relatório 2B](../validacao-integracao-agentes/RELATORIO.md) e
[codex-fluxo.json](../validacao-integracao-agentes/codex-fluxo.json).
Para OpenCode/DeepSeek e Gemini, o estado consolidado é **evidências externas
relatadas pelo usuário, pendentes de incorporação documental**. A informação
posterior do usuário não é negada pelos registros antigos que dizem “não testado”.
Também não autoriza atribuir descoberta, ativação e bootstrap a cada ambiente
sem evidência acessível. `agent-verify` comprova estado físico, não ativação nativa.
Nenhum agente foi executado nesta fase.

**Pendências documentais antes da publicação**

| ID | Local observado | Ação documental necessária |
|---|---|---|
| D01 | README:3, 17 e 173 | Atualizar o estado 3B para 4A.1, separar o parecer atual dos resultados históricos e reconhecer os testes externos posteriores relatados. |
| D02 | README do bootstrap:97, 103 e 107; README da manutenção:160 | Atualizar referências futuras à 2B, publicação temporária nomeada e limitação histórica genérica. Remeter às regras atuais de O_TMPFILE e verificação fixada, incluindo seus limites. |
| D03 | README:147; `Skills/validacao/testar_clone.py:21` | O driver antigo exige ausência de remoto e remove origin no clone. Isso não é o comportamento do validador atual. Documentar o runner recente que preserva origin; tratar eventual atualização do driver em escopo próprio. Não remover remotos para satisfazê-lo. |
| D04 | README principal / instalação | Explicitar Linux/Fedora testado, asdf global e runtimes necessários, libc/procfs/O_TMPFILE/renameat2, permissões, fluxo por hash e ausência de instalação automática. Não anunciar portabilidade Windows/macOS ou resistência absoluta a quedas/concorrência. |
| D05 | Raiz do repositório | Não foi localizado arquivo de licença próprio na raiz. Definir/documentar os termos do código próprio; as licenças dos fornecedores não substituem essa decisão do mantenedor. |
| D06 | Relatórios de agentes | Incorporar os artefatos externos com data, versão, ambiente/modelo DeepSeek, commit, comandos, hashes e resultados separados de descoberta, ativação e bootstrap. Preservar o contexto temporal dos relatórios 2B. |

`STATUS.json` continua com estágio 2A e flags conservadoras. Não deve ser promovido
a certificação universal de agentes/produção com base apenas nos testes do motor.
Os documentos históricos não foram reescritos nesta consolidação; as divergências
acima ficam explícitas para a preparação da documentação pública.

**Decisão e preservação desta fase**

- **Etapa 4B, inclusão real:** bloqueada por R01/P2. Depois do tratamento específico,
  revisar novamente o critério de parsing antes de aplicar inclusões reais.
- **Documentação de instalação/portabilidade:** pode ser preparada agora, com D01–D06
  e os limites documentados; sem instalar ou configurar ambientes nesta fase.
- **Publicação posterior no GitHub:** adiar até tratar R01 e as pendências públicas
  pertinentes. Este parecer não certifica produção nem publica o repositório.
- **R02/P3 e A08/P3:** pendências menores registradas, sem implementação automática.

Nenhum núcleo, sistema de manutenção, catálogo, lock, pacote ou consumidor foi
modificado. App-Web não foi acessado. Os testes específicos usaram memória e
fixtures próprias em `/tmp`; não executaram scripts analisados. Não houve agente
como subprocesso, aquisição de origem, instalação, alteração global, configuração
de remoto ou push. Os únicos arquivos acrescentados ao repositório são este
relatório e `resultado.json`, em commit exclusivamente documental. O identificador
do commit desta consolidação é informado na entrega.
