**StackNauta — Etapa 4A.1, Fase 1: correções funcionais A01–A04**

Concluída em 12/11/2026. Commit inicial:
`0d2355e6fbe3bfea771481fc9257f8a93843e1b5`. O estado inicial de
`git status --porcelain=v1 --untracked-files=all` estava vazio. Não havia
alterações locais a preservar ou sobrescrever. O relatório da Etapa 4A não foi
encontrado no repositório; as referências fornecidas no pedido foram conferidas
no código desse commit e usadas para reproduzir os quatro achados.

As reproduções foram feitas antes das correções, em fixtures e consumidores
temporários sob `/tmp`. Os quatro testes falharam pelos motivos esperados.
Nenhum consumidor existente foi usado para aplicação, reprodução ou migração.

**A01 — compatibilidade com remoto Git (corrigido)**

Causa confirmada: `Skills/validacao/validar_biblioteca.py` acrescentava erro
sempre que `git remote` retornava qualquer nome, independentemente da integridade
da biblioteca. Isso também rejeitava o origin criado por uma clonagem local.

Correção: removida exclusivamente essa condição. Hashes, arquivos, licenças,
catálogo, lock, proveniência, links e fechamento continuam com os mesmos controles.
Não foi acrescentada nenhuma operação de publicação, configuração de remoto ou
push. As URLs SSH/HTTPS foram testadas como configuração local de fixtures;
o validador permanece offline e não precisa autenticar nessas URLs.

Teste direcionado `test_origin_does_not_disable_integrity_validation`: passou
com clone mantendo origin, clone temporário sem remoto e URLs local, SSH e HTTPS.
Biblioteca íntegra com remoto passou; licença adulterada continuou rejeitada.
O teste inicialmente falhava com `Remoto configurado no Git principal`.
Na regressão, o clone completo também manteve origin durante todos os testes.

Arquivos: `Skills/validacao/validar_biblioteca.py` e
`Automacao/validacao-atualizacoes/test_updates.py`.

**A02 — resolução de imports relativos Python (corrigido)**

Causas confirmadas: a inclusão aceitava o `__init__.py` do diretório pai como
alternativa para qualquer módulo relativo ausente. A atualização analisava
dependências absolutas novas, ignorando a existência dos módulos relativos.

Correção: um resolvedor estático compartilhado em `atualizacao_receita.py`
verifica os caminhos e níveis relativos, diferencia módulo, pacote regular e
namespace físico e respeita a precedência de pacote sobre módulo homônimo.
Inclusões fecham os recursos sobre esses resultados; atualizações verificam os
arquivos efetivamente empacotados. Inicializadores necessários também entram
no fechamento. Nenhum módulo analisado é importado ou executado.

`from . import helper` exige módulo/pacote físico ou export explícito verificável
no inicializador. `from .helper import função` e `from ..utils import ferramenta`
exigem os módulos correspondentes no nível correto. A política de imports
absolutos permanece a anterior, inclusive dependências externas já declaradas
no script anterior versus dependências novas que exigem revisão.

Testes direcionados aprovados: cinco testes unitários em `RelativePythonTests`
e quatro testes de fluxo de inclusão/atualização. Cobrem módulo existente e
ausente com inicializador presente, pacotes aninhados, níveis relativos, pacote
na raiz, escape acima do escopo, arquivos homônimos no nível errado, pacote e
módulo com mesmo nome, namespace físico, alias de export, sintaxe inválida,
import absoluto local e externo previamente declarado. Inclusão e atualização
válidas passaram com scripts que lançariam erro se fossem executados; as duas
operações rejeitaram o módulo ausente e preservaram a biblioteca ativa.

Limites: verifica-se a existência do módulo de `from .helper import símbolo`,
sem certificar semanticamente o símbolo. Imports dinâmicos, `__getattr__`, exports
condicionais, `*` e mudanças de `sys.path` não têm resolução completa. Nomes sem
evidência em `from . import nome` bloqueiam para revisão; alguns exports válidos
que só existem em execução podem, conservadoramente, exigir análise manual.
A semântica completa dos imports absolutos não foi ampliada nesta fase.

Arquivos: `Automacao/manutencao-skills/atualizacao_receita.py`, `inclusoes.py`,
`INCLUSAO.md`, `Automacao/validacao-atualizacoes/test_updates.py` e
`Automacao/validacao-inclusoes/test_additions.py`.

**A03 — verificação de consumidores antigos (corrigido com limites conservadores)**

Causa confirmada: `Bootstrap.plan` selecionava novamente as skills pelo catálogo
atual e gerava um novo skills-lock contendo os hashes globais atuais. Mesmo uma
mudança sem relação com os recursos copiados alterava o manifesto reconstruído,
que era rejeitado por `Target.inspect`.

Correção: para um destino existente, a seleção vem do manifesto original.
O skills-lock copiado precisa corresponder a seu hash/tamanho protegido nesse
manifesto. A exportação da seleção fixada precisa reproduzir todos os registros
de arquivos, origens, commits e pré-requisitos. Somente os hashes globais do
catálogo e lock de fontes deixam de depender dos valores atuais; seus bytes
históricos são conservados, sem renovação silenciosa. O manifesto inteiro continua
sendo reconstruído e comparado, com os controles físicos anteriores.

Schemas 1 e 2 mantêm IDs, conteúdo e comportamento de conclusão anteriores.
Não há migração, regravação ou atualização automática de arquivos evolutivos.
Reaplicar continua exigindo o hash original autorizado. Skills novas compatíveis
não passam a integrar uma inicialização existente.

Testes direcionados aprovados: consumidor íntegro original; catálogo com nova
skill; lock global com outra origem atualizada; inclusão real de fixture
compatível seguida de atualização de outra origem; schema 1 após divergência
do catálogo; schema 2; adulterações em manifesto, lock, marcador, aliases e
recursos protegidos; evidência histórica ausente; arquivo protegido removido;
publicação parcial retomável e evolução legítima. As verificações e reaplicações
preservaram bytes, IDs, inode e timestamps nos casos instrumentados.

Limite conservador: ainda é necessário reproduzir os recursos e a proveniência
da seleção histórica com uma biblioteca confiável. Alteração no próprio pacote
selecionado, inclusive README/PROVENANCE renovados por outra inclusão na mesma
origem, pode exigir a revisão original num clone separado. Registros ausentes,
divergentes ou insuficientes bloqueiam; não se inventam hashes históricos nem se
certifica integridade sem evidência. Runtimes e gerador compatíveis continuam
necessários. Os manifestos continuam sem assinatura contra controle total pelo
mesmo usuário, conforme o contrato anterior.

Arquivos: `Automacao/project-bootstrap/stacknauta_core/core.py`, `filesystem.py`,
`Automacao/project-bootstrap/CICLO-DE-VIDA.md`,
`Automacao/validacao-project-bootstrap/test_lifecycle.py`,
`Automacao/validacao-inclusoes/test_additions.py` e `INCLUSAO.md`.

**A04 — resultado de inclusão e atualização (corrigido)**

Causa confirmada: a promoção só classificava como modificada uma origem com
`estado: atualizacao_disponivel`. Uma inclusão chega como `inclusao_revisada`
e, depois de aplicada, caía no fallback `nao_modificada`.

Correção: inclusão aplicada passa a informar `resultado: incluida`; atualização
aplicada continua `atualizada`. Mantidos os contratos de `aplicado`,
`sem_alteracoes`, `sem_novas_candidatas` e `ja_aplicado`. A CLI distingue
`bloqueado` antes das escritas de `falha_aplicacao` durante promoção/recuperação,
mantendo código de saída 2. A API preserva os tipos de exceção existentes.
Após rollback bem-sucedido, `application-failed.json` registra a falha, a
recuperação e a ausência de origens promovidas. Falha na recuperação permanece
erro para revisão manual; não é relatada como sucesso.

Testes direcionados aprovados: inclusão aplicada com resultado correto,
atualização aplicada, consulta sem alterações, falta de autorização, hash
incorreto, falha após publicação com rollback, JSON da CLI para recusa e falha,
fluxo completo de CLI e reexecução idempotente. A reprodução inicial demonstrou
`nao_modificada` apesar da inclusão efetivada.

Arquivos: `Automacao/manutencao-skills/atualizacoes.py`, `skills_cli.py`,
`INCLUSAO.md`, `Automacao/validacao-atualizacoes/test_updates.py` e
`Automacao/validacao-inclusoes/test_additions.py`.

**Regressão final e preservação**

A regressão completa foi executada uma única vez no commit
`690b745df39354f0fc5515e62a277ad13f7d09c7`, entre 23:41:51 e 23:43:09 UTC,
em clone local sem `_repos`, sem alternates e com origin preservado. O clone
terminou com árvore limpa e origin inalterado. Os logs completos e resultados
estruturados estão em [resultado.json](resultado.json).

| Suíte | Resultado |
|---|---|
| Núcleo e ciclo de vida | 99 testes aprovados |
| Integração dos agentes | 16 testes aprovados |
| Atualizações | 42 testes aprovados |
| Inclusões | 46 testes aprovados |
| Total automatizado | **203; zero falhas, erros ou skips** |
| Biblioteca | 958 arquivos verificados; zero erros |
| Cópias físicas | 101 casos aprovados, 4.114 arquivos copiados |
| JavaScript | 7 arquivos com sintaxe aprovada |
| Smoke tests já existentes da biblioteca | 3 aprovados |

O status da biblioteca continua `passed_with_documented_pending`: preserva as
pendências históricas de distribuição, sem erros novos. Não houve bloqueio
ambiental ou teste pendente nesta fase. Testes nativos de OpenCode e Gemini
ficaram fora do escopo por restrição explícita; nenhum deles foi executado.
Os módulos das fixtures de imports relativos permaneceram estritamente estáticos;
os três smoke tests da biblioteca são os já existentes no validador.

Runner: `Automacao/validacao-correcoes-funcionais/executar_testes.py`. Ele executa
cada suíte uma vez e valida a biblioteca com `--copias --sintaxe-node`, sem
invocar a cadeia antiga que repetia suítes em clones sucessivos. Com candidato
limpo, a reprodução usa:

```sh
Automacao/python-global Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4a1.json
```

`git diff --exit-code` contra o commit inicial confirmou que todos os pacotes
Frontend, Backend, Mobile e Seguranca, catálogo, lock de fontes e
`Skills/manutencao` permaneceram idênticos. Os nove pacotes e 101 conjuntos
aprovados, licenças, revisões e recursos não foram atualizados. A única alteração
sob `Skills` foi a remoção da condição de remoto no validador.

Não houve escrita em App-Web ou consumidores existentes, instalação de runtimes
ou dependências, mudança global de configuração, alteração de remoto real,
push ou publicação. Somente Python/Node globais já instalados no asdf foram usados;
as simulações de outros runtimes existentes nas suítes foram mantidas. Dry-run,
aprovação explícita por hash, path traversal, symlinks/hardlinks, integridade,
cópia física, recuperação e idempotência continuam cobertos. A05–A08 não foram
implementados. O novo valor de status de falha da CLI é uma extensão intencional
do contrato; clientes que enumeram status devem reconhecer `falha_aplicacao`.

**Commits locais**

Implementação, testes e documentação dos contratos: `690b745` —
`fix: corrigir achados funcionais A01–A04 do StackNauta`.
O commit posterior de evidências acrescenta somente este relatório e
`resultado.json`; seu hash é informado na entrega. Não houve alteração de código
após a regressão nem repetição da suíte completa.
