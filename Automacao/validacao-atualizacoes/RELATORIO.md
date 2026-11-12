# Etapa 3A — sistema de atualização das skills

## Estado e análise reaproveitada

Base inspecionada: commit `7b680c4` (Etapa 2D), árvore inicialmente limpa, sem
remotos. O inventário contém sete origens, nove pacotes, 101 skills aprovadas,
21 pendentes e duas excluídas. Não se reconstruiu ou atualizou a biblioteca real.

O sistema existente já fornecia os componentes necessários:

- `inventariar.build`: branches/caminhos distintos, descoberta de SKILL.md,
  referências, evidências de pré-requisitos, inventário e blobs de origem.
- `biblioteca`: serialização, hashes, fechamento transitivo e arquivos de cópia.
- `distribuicao-politica.json`: decisões individuais de distribuição.
- `PROVENANCE.json` e `adaptacoes.json`: inputs, licenças, hashes e diffs explícitos.
- `validar_biblioteca.py`: inventários, proveniência, licenças e links locais.
- `AsdfResolver` e launcher existente: Python exclusivamente global do asdf.

O empacotador histórico gera toda a biblioteca e recusa substituições. Sua receita
é fixada por hash no catálogo e precisa permanecer reproduzível. Por isso ficou
intacto: a atualização incremental reaproveita seus registros e os helpers de
inventário/validação, preservando bytes de pacotes não afetados e classificações.
O cache `_repos/` é opcional, não fonte de verdade para atualização ou consumo.

## Arquitetura e arquivos

- `Automacao/manutencao-skills/skills`: interface estável independente da pasta
  `Skills`, inclusive para recuperar sua ausência após interrupção.
- `skills_cli.py`: `check`, `update ORIGEM`, `update --all`, `apply` e `recover`.
- `atualizacoes.py`: Git restrito, snapshots, isolamento, hash revisado, validação,
  exclusão mútua, promoção global por diretório e recuperação com diário/backup.
- `atualizacao_receita.py`: atualização incremental de pacotes e metadados;
  reaplicação exata de adaptações, novas skills pendentes e bloqueios conservadores.
- `Automacao/python-global`: extração mecânica da resolução asdf do launcher do
  bootstrap; ambos usam o mesmo contrato. Nenhum algoritmo do núcleo foi alterado.
- `Skills/validacao/validar_biblioteca.py`: extensão opcional de `check_links` para
  conferir se o alvo está no fechamento selecionado, além de existir no pacote.
  O comportamento padrão anterior permanece; não se enfraqueceu um validador.
- `.gitignore`: staging de atualização ignorado. README principal e guias de
  manutenção atualizados. Esta pasta contém testes, clone e evidências.

O [guia de utilização](../manutencao-skills/README.md) descreve os comandos,
autorização, bloqueios, recuperação e limites operacionais.

## Fluxo e segurança

`check` usa `ls-remote` das branches cadastradas, somente leitura. Uma falha nunca
é apresentada como atualização disponível ou origem em dia. `update` exige Git
limpo, consulta as revisões e adquire apenas as alteradas em candidato isolado,
com profundidade 1, sem checkout, submódulos, filtros ou hooks. Os blobs são
materializados e confrontados com seus hashes. Não executa fornecedores.

Preserva as decisões anteriores e registra descobertas novas como pendentes,
sem distribuir ou habilitar. Recursos, licenças, catálogo, política, lock, hashes,
índices e proveniência são preparados juntos. Mudanças incompatíveis de licença,
adaptação, renderer UI/UX, dependências ou referências bloqueiam todo o lote.

O plano inclui revisão Git inicial, commits anteriores/propostos, diff de origem,
diff distribuído, novos pendentes, hashes/modos anteriores e árvore candidata.
`apply` exige autorização explícita e hash revisado, reconfere tudo e revalida.
Novas verificações acontecem depois da publicação. Uma origem previamente
cadastrada não recebe confiança automática: o operador precisa revisar conteúdo.

A consistência é **global por lote**. Duas renomeações com fsync substituem a
árvore inteira; há uma janela curta sem `Skills`, não uma troca POSIX única.
Falha tenta restaurar o snapshot anterior; interrupções podem usar `recover`.
Backup, candidato e diário são preservados, sem exclusão, reset ou clean.
Mudanças inesperadas no destino/backup interrompem a recuperação automática.
O diário `committed` significa publicação concluída, não commit Git automático.

## Testes executados

Python executor global asdf: **3.14.8**. Nenhum runtime ou pacote instalado.

| Conjunto | Resultado |
|---|---|
| Núcleo e ciclo de vida | 96 passaram; zero falhas/erros/skips |
| Integração compartilhada | 16 passaram; zero falhas/erros/skips |
| Atualizações com Git local | 30 passaram; zero falhas/erros/skips |
| Biblioteca completa | 958 arquivos verificados; zero erros |
| Fechamento estático | 101 skills conferidas, incluindo referências selecionadas |
| Sintaxe de recursos | 41 Python parseados; sete JavaScript com `--check` |
| Catálogo offline | passou sem cache |
| Consumidor FastAPI 2C por leitura | `verified_with_evolution`, mesmo plan ID |

As 30 fixtures cobrem: origem sem alteração, novo commit, promoção individual e
múltipla, fetch somente das alteradas, conexão/branch/repositório indisponíveis,
nova skill pendente, nova skill fora do escopo esparso, alteração de licença,
adaptação reaplicada, ambiente Git redirecionado, recursos ausentes e novos, blob
adulterado, novas dependências e referências não atendidas, licença/proveniência,
falhas antes/depois da publicação e na validação final, recuperação com `Skills`
ausente, reexecução sem escrita, inode/modos/timestamps preservados no no-op,
autorização/hash/diário e módulos candidatos adulterados, Git sujo, escape e symlinks inseguros.

As fixtures são mínimas (quatro skills reais em dois pacotes, sete origens Git
locais); toda a biblioteca real passa adicionalmente pelos validadores e pelos
101 fechamentos. Isso evita copiar centenas de MB em cada caso e mantém testes
determinísticos sem atualização GitHub. Testes de cópia do núcleo continuam
incluídos. `--copias` histórico não foi executado nesta etapa porque executa
buscas do fornecedor; não se alega nova execução de seus workflows.

Comandos, a partir da raiz:

```sh
bash Automacao/python-global Automacao/validacao-atualizacoes/executar_testes.py
bash Automacao/python-global Automacao/validacao-project-bootstrap/executar_testes.py
bash Automacao/python-global Automacao/validacao-integracao-agentes/executar_testes.py
bash Automacao/python-global Skills/validacao/validar_biblioteca.py --sintaxe-node
# O wrapper histórico importa módulos irmãos; executar sem -I:
asdf exec python -B Skills/validacao/validar_catalogo.py
# Com commit candidato e árvore limpa:
bash Automacao/python-global Automacao/validacao-atualizacoes/testar_clone.py
```

Evidências: [atualizacoes.json](atualizacoes.json), [nucleo.json](nucleo.json),
[integracao.json](integracao.json), [biblioteca.json](biblioteca.json),
[catalogo.json](catalogo.json), [fechamentos.json](fechamentos.json).
Clonagem local limpa e verificações finais serão registradas após o commit candidato.

Uma execução intermediária com fixtures completas esgotou a cota de `/tmp`.
Somente fixtures desta etapa, com marcadores de propriedade e origens locais
confirmados, foram removidas após autorização específica da ferramenta. A suíte
foi reduzida e passou integralmente. Nenhum cache real, projeto anterior ou
artefato de recuperação da biblioteca foi removido. Staging real requer espaço
para candidato e backup; limpeza automática de estados não foi implementada.

## Consulta real somente leitura

Consulta às sete origens via GitHub em 12/11/2026, sem fetch no StackNauta,
sem mudar `_repos/`, locks, catálogo, pacotes ou remotos. A primeira tentativa
no sandbox não resolveu DNS; a consulta externa somente leitura foi autorizada
e concluída. [consulta-real.json](consulta-real.json) conserva os commits completos.

| Origem | Branch | Resultado | Revisão disponível (prefixo) |
|---|---|---|---|
| UI/UX Pro Max | main | sem alterações | `6ae86f61f520` |
| FastAPI | master | sem alterações | `5add7a458d62` |
| Remy349 | main | sem alterações | `5d9eae132afe` |
| Expo | main | atualização disponível | `2a326eb51ddd` (atual `a9e5bd3fa00b`) |
| Chris Banes | main | atualização disponível | `b684174b626c` (atual `50d54366e577`) |
| Android | main | sem alterações | `5815d27fda56` |
| Sentry | main | sem alterações | `e94f22214528` |

Nenhum `update` ou `apply` foi executado contra origens reais. Disponibilidade
não equivale a conteúdo aprovado ou distribuição preparada. A biblioteca real
continua com **101 aprovadas, 21 pendentes, duas excluídas e nove pacotes**.

## Limitações e pendências

- Mudanças estruturais, remoções, novos pré-requisitos ou adaptações incompatíveis
  precisam de análise manual; não há resolução automática de conflitos.
- UI/UX com mudança em renderer/template exige revisão própria; não se executou
  fornecedor para validar uma nova distribuição. TypeScript/Ruby/PowerShell
  alterados também exigem validação específica.
- A análise estática de dependências/referências não certifica todos os efeitos
  de scripts ou instruções. A revisão humana do diff continua obrigatória.
- Promoção global tem janela de indisponibilidade; não consumir concorrentemente.
  Requer POSIX/Fedora e espaço no mesmo filesystem. Backups acumulam até revisão
  manual; reversão de uma promoção já concluída não é automática.
- Hashes e defesas de caminhos não são assinaturas contra controle total do
  mesmo usuário ou garantia contra todas as renomeações concorrentes externas.
- Consumidores permanecem intocados. O verificador atual do bootstrap recompõe
  o plano com a biblioteca presente; após futura atualização real, verificar um
  consumidor antigo pode exigir o commit original do StackNauta em clone separado.
  Nenhuma migração ou mudança de contrato do núcleo foi introduzida nesta etapa.
- Só as sete origens cadastradas são aceitas. Novas origens são Etapa 3B.
- OpenCode e Gemini não foram executados; não há aprovação prática desses agentes.
  Nenhum gerador, serviço, publicação ou atualização real foi executado.

Próximo passo: revisar o mecanismo e, em autorização separada, preparar uma das
atualizações reais disponíveis; revisar o plano/diff antes de autorizar promoção.
