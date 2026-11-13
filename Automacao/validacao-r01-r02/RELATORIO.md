**StackNauta — Etapa 4A.2: correções R01 e R02**

Concluída em 13/11/2026. R01 e R02 foram corrigidos e os respectivos casos de
regressão passaram. A suíte completa foi executada uma única vez, com **273
testes aprovados**, zero falhas, erros ou skips, e 101 casos de cópia física.
O impedimento técnico R01 identificado na consolidação foi removido para o
escopo validado. As demais pendências documentais de publicação e A08 permanecem
fora desta etapa; não houve inclusão real nem publicação.

HEAD inicial: `fee34669c0628ecb24635d1da8dae0fa4ac0c075`, com árvore limpa.
Foram consultados os relatórios das fases anteriores e a
[consolidação 4A.1](../validacao-consolidacao-4a1/RELATORIO.md). O fluxo efetivo
foi confirmado em `check_changed_scripts`, usado por inclusão e atualização,
e em `relative_python_resources`, também compartilhado pelos dois fluxos.

**R01 — interpretação de módulos JavaScript**

Causa confirmada: a manutenção passava os bytes por stdin com
`--input-type=commonjs` quando não encontrava tipo explícito. Isso substituía a
detecção aplicável ao arquivo `.js` na versão global do Node. A busca existente
do JSON mais próximo não bastava para preservar a semântica de arquivo sem tipo.

Reprodução antes da correção, em fixture temporário sem declaração de tipo:

```javascript
export const value = 1;
throw new Error("never execute");
```

O teste que exigia aceitação falhou com `Unexpected token 'export'`. Esse caso
e o de R02 foram registrados antes das mudanças: dois testes, dois erros
esperados. Nenhum dos módulos analisados foi executado.

Correção: o Node global do asdf recebe `--check` sobre uma cópia privada dos bytes
lidos com as primitivas seguras existentes. A extensão e a posição relativa são
preservadas; o package.json mais próximo é copiado sem modificar seus bytes.
Um JSON vazio na raiz sintética delimita o contexto e impede herança acidental
da máquina de validação. Não se injeta `type: module` nem se modifica fornecedor
ou candidato para obter aprovação. A busca respeita a raiz candidata e a fronteira
`node_modules`. O JSON mais próximo encerra a busca mesmo sem `type`.

Assim, `.mjs`, `.cjs`, `.js`, tipos explícitos e ausência de tipo são analisados
pelo próprio Node instalado. JSON malformado/inacessível tem diagnóstico de
contexto. Falha de parser que não seja erro de sintaxe é inconclusiva e bloqueia
para revisão, em vez de classificar o script como inválido.

A inspeção do fluxo também confirmou a necessidade de reconferir scripts
JavaScript intactos nos outputs de atualização: mudar somente package.json
pode mudar o formato aplicável. A validação agora cobre esse caso. As regras
anteriores de dependências externas e fechamento de recursos foram preservadas.

Após a correção, **17 testes direcionados JavaScript passaram**, cobrindo:
extensões `.mjs`/`.cjs`; ESM e CommonJS explícitos; `.js` sem tipo; JSON sem campo
type; herança ancestral; sobrescrita aninhada em ambos os sentidos; JSON aninhado
sem tipo interrompendo herança; script intacto com contexto alterado; sintaxe
realmente inválida nos três formatos; ESM recusado em CommonJS explícito;
JSON malformado; contexto por symlink; falha inconclusiva do parser. Os testes
também conferem a preservação dos bytes do script e dos JSONs de origem.

**R02 — nomes definidos por atribuição estruturada Python**

Causa confirmada: `explicit_export` só reconhecia `ast.Name` diretamente nos
targets de Assign/AnnAssign. Um target Tuple/List não era percorrido, embora
contivesse identificadores definidos pela atribuição.

Reprodução antes da correção:

```python
# pkg/__init__.py
helper, other = 1, 2
# pkg/main.py
from . import helper
```

O teste falhou como dependência local ausente/ambígua. A correção acrescenta uma
extração recursiva pequena dos targets Name, Tuple, List e Starred. Assign mantém
todos os seus alvos, inclusive encadeados; AnnAssign continua exigindo valor.
Atributos/subscritos não definem seu objeto-base e AugAssign isolado não é
tratado como criação de export. Não foi adicionada execução ou inferência de
valores do lado direito.

Depois da correção, **13 testes direcionados Python passaram**: atribuição simples,
tupla, lista, aninhamento, alvos estrelados/encadeados, anotação com valor,
anotação sem valor recusada, atributos/subscritos/augassign sem definição,
export diferente de módulo físico, símbolo ausente, sintaxe inválida, import
relativo com export estruturado e módulo relativo obrigatório ausente.

O símbolo encontrado no inicializador não passa a representar um arquivo `.py`.
Por exemplo, `from .helper import tool` continua bloqueado quando helper.py/pacote
helper está ausente, mesmo se existir uma variável helper no inicializador.

**Integração com inclusão e atualização**

O novo teste de fluxo usa repositório Git local sintético com `.js` ESM sem tipo,
inicializador com `from .utils import helper` e `primeiro, segundo = helper, None`,
e import relativo desses símbolos. Discovery deixou a candidata pendente, sem
modificar a biblioteca ativa da fixture. Review preparou o plano, aplicação sem
approve foi recusada, e a aplicação explicitamente autorizada relatou `incluida`.

Uma nova revisão sintética alterou o JS e usou desestruturação Python aninhada.
Prepare manteve a biblioteca ativa intacta e apply autorizado relatou
`atualizada`. Revisões posteriores com JS inválido e módulo Python ausente foram
bloqueadas, preservando a biblioteca ativa. O sentinela que o JS criaria se fosse
executado permaneceu ausente; o consumidor sintético permaneceu intacto.

O grupo final de testes direcionados executou os 17 casos JS mais esse fluxo:
**18 aprovados**. Os 13 casos Python foram executados separadamente. Essas contagens
se sobrepõem à regressão completa e não devem ser somadas ao total final.

**Regressão final**

Commit testado: `61a8e64910684f8a0b8932465ca4693bee650178`.
Execução única entre 12:28:17 e 12:29:55 UTC de 13/11/2026, cerca de 98 segundos:

```sh
Automacao/python-global Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4a2-regressao-final.json --sem-smoke-fornecedor
```

| Verificação | Resultado |
|---|---|
| Núcleo/ciclo de vida | 110 aprovados |
| Integração dos agentes | 16 aprovados |
| Atualizações/analisadores/segurança | 99 aprovados |
| Inclusões | 48 aprovados |
| Total | **273; zero falhas, erros ou skips** |
| Biblioteca | 958 arquivos verificados, zero erros |
| Cópias físicas | 101 casos, 4.114 arquivos copiados |
| Sintaxe JS da biblioteca | 7 arquivos aprovados; somente parsing |
| Smoke tests executáveis de fornecedor | Não solicitados; zero executados |
| Clone | Limpo ao final, sem `_repos`/alternates, origin preservado e inalterado |

Os 242 testes anteriores e 31 novos passaram. O status histórico da biblioteca
continua `passed_with_documented_pending`, referente às classificações existentes.
Não houve bloqueio ambiental nem teste automatizado pendente nesta etapa.

Para cumprir a proibição de executar scripts de fornecedores, foi acrescentada
a opção `--sem-smoke-fornecedor` ao validador e encaminhada pelo runner. Ela
omite apenas os três smokes UI/UX e mantém cópias, hashes, referências, licenças,
casos adversariais e parsing. O comportamento padrão anterior de `--copias` é
preservado. A evidência registra `ui_smoke_tests_status: not_requested`, lista de
smokes vazia e `vendor_code_executed: false`. Não se atribui aprovação aos três
smokes não executados nesta etapa.

**Arquivos modificados e limites**

- `Automacao/manutencao-skills/atualizacoes.py`: contexto/parsing JS seguro e
  reconferência dos scripts nos outputs.
- `Automacao/manutencao-skills/atualizacao_receita.py`: targets estruturados Python.
- `Automacao/validacao-atualizacoes/test_analyzers.py`: 30 casos direcionados.
- `Automacao/validacao-inclusoes/test_additions.py`: fluxo real sintético conjunto.
- `Skills/validacao/validar_biblioteca.py` e runner de regressão: omissão explícita
  dos smokes de fornecedor, exigida para esta execução.
- `Automacao/manutencao-skills/README.md`, `INCLUSAO.md` e
  `Skills/validacao/README.md`: documentação técnica diretamente relacionada.
- Este diretório: relatório e evidências, adicionados depois da regressão.

Runtimes reais: Python 3.14.8 e Node 24.21.0, globais do asdf já instalados.
Detecção JS acompanha a versão global usada; não certifica sintaxe de versões
futuras, comportamento em browser, resolução de imports ou efeitos em execução.
Só se considera contexto materializado no candidato, sem presumir metadados de
origem que não foram copiados. O diretório privado usa as mesmas restrições de
descritores/Linux documentadas em A07; não amplia a garantia contra controle
hostil total do mesmo usuário.

Python continua estático: não avalia o RHS, aridade de valores, controle de fluxo,
exports dinâmicos ou existência semântica de símbolos de módulos. Anotações sem
valor não criam nomes em execução. As verificações anteriores de imports relativos
permanecem; não foram reconstruídos os analisadores nem alteradas as regras de
aprovação/seleção. Casos fora da cobertura estática podem exigir revisão manual.

Referências consultadas: [formatos e package.json do Node 24.21.0](https://nodejs.org/download/release/v24.21.0/docs/api/packages.html)
e [opção --check](https://nodejs.org/download/release/v24.21.0/docs/api/cli.html#-c---check).

**Preservação e commits**

O diff contra o HEAD inicial confirmou que todos os pacotes Frontend, Backend,
Mobile e Seguranca, catálogo, lock de fontes e Skills/manutencao permaneceram
idênticos. Mantidos **101 aprovadas, 21 pendentes, duas excluídas, sete origens e
nove pacotes**. As únicas alterações sob Skills foram ferramenta e documentação
de validação, sem mudança de skill ou licença.

O núcleo/contratos do bootstrap, arquivos de descoberta, README principal e
instruções dos agentes permaneceram idênticos. Dry-run, hash, aprovação explícita,
candidatos isolados, proveniência, diário, recuperação e proteções de filesystem
continuaram cobertos pelos testes existentes.

Não houve escrita em App-Web ou consumidores existentes, inclusão/atualização
real, execução de fornecedores/agentes, instalação, configuração global ou de
remotos reais, nem push. As escritas dos testes ocorreram em fixtures temporárias.
Os consumidores reais não foram usados para inventário ou teste; sua preservação
é sustentada pelo escopo das operações e pelos controles de destino.

Implementação, testes e documentação técnica: **`61a8e64`** —
`fix: corrigir contexto JavaScript e exports Python em R01–R02`.
O commit posterior de evidências acrescenta somente este relatório e
`resultado.json`; seu identificador é informado na entrega. Nenhum código foi
alterado após a regressão, e a suíte completa não foi repetida.

Resultados e logs: [resultado.json](resultado.json).
