# Atualização manual das sete origens — Etapa 3A

A partir da raiz do StackNauta:

```sh
./Automacao/manutencao-skills/skills check
./Automacao/manutencao-skills/skills update expo
./Automacao/manutencao-skills/skills update --all
```

`check` consulta as branches **configuradas** no lock, informa também a branch
padrão remota e compara commits completos. Não escreve biblioteca, cache ou lock.
Erros de consulta retornam código 2 e `erro_consulta`, nunca sucesso presumido.
As origens aceitas são `ui-ux-pro-max`, `fastapi`, `remy`, `expo`, `chrisbanes`,
`android` e `sentry`. Não há descoberta de novas origens nesta etapa.

`update` é exclusivamente preparação/dry-run. Exige Git principal limpo e cria
`.stacknauta-updates/SESSION/` (ignorado pelo Git), com candidato, aquisições,
`plan.json`, `review.diff` e diário. Baixa somente origens com commits diferentes,
com profundidade 1, sem submódulos, checkout, filtros, smudge ou execução de hooks.
FastAPI preserva seus caminhos esparsos; cada origem mantém sua própria branch e
estrutura. O cache antigo `_repos/` não é consultado nem atualizado.

Revisar **todo** o `plan.json` e o `review.diff`: commits, alterações de conteúdo,
recursos, scripts, licenças, dependências, adaptações e novas skills pendentes.
Integridade e análise estática não tornam código de terceiros automaticamente
seguro. Depois de autorização humana explícita:

```sh
./Automacao/manutencao-skills/skills apply SESSION --plan-id HASH_REVISADO --approve
```

O hash vincula o candidato, os diffs, os metadados e o estado anterior do Git.
Mudança de HEAD, arquivo rastreado, modo, candidato ou hash impede a aplicação.
`--approve` registra a autorização do operador; não substitui a revisão nem concede
permissões ao agente. Não aplicar sem autorização do usuário. Não há instalação
de ferramentas, execução de fornecedores ou atualização automática em segundo plano.

## Política de promoção

- Atualiza incrementalmente apenas pacotes das origens selecionadas. Reutiliza
  inventário, fechamento de cópia, política, validação e adaptações existentes.
- Preserva aprovação, pendência e exclusão. Novas skills são registradas como
  pendentes, desabilitadas e sem distribuição; uma skill aninhada num diretório
  aprovado bloqueia a promoção para não ser incluída por acidente.
- Recursos novos dentro dos diretórios aprovados entram na proveniência e nos
  hashes. Recurso removido, skill removida/movida, licença desconhecida/alterada,
  nova dependência, referência não atendida ou contexto de adaptação incompatível
  bloqueiam o lote e geram `blocked.json`; nenhuma origem é promovida.
- Adaptações são reaplicadas somente com contexto exato e único, sem fuzzy patch.
  UI/UX mantém recursos canônicos `src/ui-ux-pro-max/{scripts,data}`; mudanças no
  renderer, templates ou entradas renderizadas exigem revisão manual, sem criar
  uma distribuição alternativa incompatível.
- Valida bytes de origem contra blobs Git, hashes distribuídos, licenças, links,
  proveniência e fechamento de todas as skills. Python passa por AST; alterações
  JS por `node --check` usando Node global asdf; imports literais novos externos
  ou recursos locais ausentes/fora da skill bloqueiam. Shell passa por `bash -n`. Não executa
  scripts de fornecedores. Alterações TS/TSX, Ruby e PowerShell exigem revisão
  específica. Análise de pré-requisitos é conservadora e não prova toda semântica.

Catálogo, lock, política, índices, adaptações e proveniência são preparados juntos.
A receita histórica `preparar_biblioteca.py` permanece intacta; não é um comando de
atualização. O catálogo promovido registra a receita incremental e seus hashes. Novos SKILL.md
fora do escopo esparso são relatados e bloqueiam o lote para aquisição/auditoria
posterior de seus recursos.
Relatórios históricos não são reescritos como se cobrissem as versões novas;
o plano, o diário e os validadores registram a operação atual.

## Consistência e recuperação

A atomicidade é **global por lote**, inclusive em `--all`: qualquer falha de
preparação bloqueia todas as origens selecionadas. A promoção troca a pasta
`Skills` inteira por renames no mesmo filesystem, com fsync e backup. Não publica
metadados e pacotes de revisões diferentes. Há uma breve janela sem `Skills` entre
as duas renomeações; evitar consumo concorrente. Não é uma troca POSIX única.

O diário registra `prepared`, `moving_old`, `old_moved`, `new_published` e
`committed`. Este último significa transação de filesystem concluída, **não** um
commit Git. Exceções tentam restaurar o backup. Para interrupção do processo:

```sh
./Automacao/manutencao-skills/skills recover SESSION --approve
```

O executável fica em `Automacao`, portanto funciona mesmo com `Skills` ausente.
Recuperação confere plano, diário, bytes/modos anteriores e estado publicado;
recusa sobrescrever um estado inesperado. Mantém candidato rejeitado e backup,
sem reset, clean ou exclusão de artefatos. Recuperação de transação interrompida
não é reversão de atualização já concluída: esta exige revisão separada a partir
do backup e da revisão Git anterior, preferencialmente em cópia isolada.

O cache antigo e arquivos ignorados anteriores acompanham `previous-Skills`; o
novo diretório ativo contém os artefatos versionados, sem precisar de `_repos/`.
Nenhum backup ou staging é removido automaticamente; planejar espaço em disco.
Arquivos não afetados mantêm bytes e modos, mas a troca da árvore altera inodes.

Depois de aplicar, conferir o diff e registrar **manualmente** um commit Git.
Sem isso, uma nova preparação é bloqueada pelo estado sujo. Repetir o mesmo apply
concluído retorna `ja_aplicado` se a árvore continuar idêntica. Uma nova consulta
após registrar a revisão não prepara nada quando os commits já coincidem.

## Runtimes, portabilidade e consumidores

O launcher compartilha `Automacao/python-global` com o bootstrap: somente Python
global instalado do asdf, sem fallback de sistema/local. Não instala runtime.
Os caminhos distribuídos são relativos à instalação. Não configura remotos Git.

Projetos consumidores nunca são visitados pela atualização: suas skills são
cópias físicas e permanecem na revisão original. **Limitação do verificador do
bootstrap existente:** ele recompõe o plano com a biblioteca local. Depois de uma
promoção real que mude seus hashes, verificar/reaplicar um consumidor antigo pode
exigir a revisão original do StackNauta em clone separado. Esta etapa não migra
consumidores nem altera suas proteções. Guardar o commit Git anterior e os planos.

## Testes

Usar o Python global asdf já resolvido (o launcher abaixo resolve e valida):

```sh
bash Automacao/python-global Automacao/validacao-atualizacoes/executar_testes.py
# Exige árvore limpa e commit local; clone temporário sem cache ou rede:
bash Automacao/python-global Automacao/validacao-atualizacoes/testar_clone.py
```

As fixtures usam repositórios Git temporários e não promovem origens reais. A
validação 3A não usa `--copias`, que executa buscas de fornecedor na suíte histórica;
confere estaticamente os fechamentos e reutiliza os testes de cópia do núcleo.
Limites/evidências: [relatório](../validacao-atualizacoes/RELATORIO.md).
