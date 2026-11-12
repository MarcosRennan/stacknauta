# Etapa 3B — inclusão controlada de skills e origens

## Base e arquitetura

Base: `3932c84`, árvore inicialmente limpa. A [análise anterior à implementação](../manutencao-skills/ANALISE-3B.md)
registra os componentes reaproveitados e os pontos fixos da Etapa 3A.
A biblioteca real continua com **sete origens, nove pacotes, 101 aprovadas,
21 pendentes e duas excluídas**. Não se adicionou ou atualizou conteúdo real.

O motor de publicação não foi duplicado. `Updates.begin/copy_snapshot/finish`
extraem os passos comuns do código 3A; `apply` e `recover` continuam únicos, com
o mesmo schema de plano, hash revisado, backup, diário e troca global de Skills.

- `origens.py`: HTTPS/SSH GitHub, identidade canônica, refs, branches com barras,
  tags/commits e escopos. URLs inválidas ou ambíguas são recusadas.
- `inclusoes.py`: descoberta, relatório, decisões individuais, fechamento de
  recursos e preparação incremental dos novos pacotes/metadados.
- `skills_cli.py`: novos `add`/`review`, preservando `check/update/apply/recover`.
  Origens de update/check agora vêm do lock, não de uma lista fixa de sete.
- `atualizacoes.py`: aquisição esparsa ampliável sem estreitar escopo anterior,
  transporte SSH sem aceite de host key, credenciais existentes somente para
  consultas HTTPS/SSH, TLS/fsck obrigatórios e validação estática reaproveitada.
- `atualizacao_receita.py`: inventário, leitura confrontada com blobs, contagens,
  índices de categoria e análise de imports compartilhados com a inclusão.
  Atualizações preservam a compatibilidade e a revisão de inclusão registradas.
- `compatibility.py`/`library.py`: leitura estrita e aditiva de condições explícitas
  do catálogo, com o matcher existente; nenhuma política legada é substituída.
  Não houve reconstrução do núcleo ou alteração da integração dos agentes.
- `inventariar.py`: corrige prefixo de SKILL.md na raiz, para não omitir seus recursos.
- `validar_biblioteca.py`: registro extensível, IDs únicos, licença compartilhada
  em caminho relativo e conferência das regras declarativas. As verificações de
  hashes, arquivos, referências, origem e adaptações continuam obrigatórias.
- README principal, manutenção e [guia de inclusão](../manutencao-skills/INCLUSAO.md)
  documentam comandos, decisões, limites e recuperação. Esta pasta contém testes,
  demonstração reproduzível, wrapper de clone e evidências.

O empacotador histórico fixado por hash permaneceu intacto. Os nove pacotes atuais
não foram renderizados ou regenerados. Novas distribuições usam layout relativo
`vendor/<caminho-original>`, com fechamento explícito e licença compartilhada.
Inclusão em origem com pacote legado usa `-adicionais`, preservando seu layout.

## Procedimento e segurança

```sh
./Automacao/manutencao-skills/skills add URL [--ref REF] [--path CAMINHO]
./Automacao/manutencao-skills/skills review SESSION
./Automacao/manutencao-skills/skills review SESSION --decisions decisoes.json --review-id HASH_DESCOBERTA
# Revisar plan.json e review.diff; somente após autorização explícita:
./Automacao/manutencao-skills/skills apply SESSION --plan-id HASH_PLANO --approve
```

Descoberta escreve apenas inspeção/cache isolados e não produz aprovação.
Decisões por ID preparam outro dry-run; somente apply promove. Novas candidatas
não mencionadas ficam pendentes. Entradas anteriores não revistas mantêm suas
classificações. Não se habilitam skills globalmente; cópia para projeto depende
da seleção e das escolhas declaradas pelo usuário.

O review mostra descrição, recursos/scripts, referências, licença, dependências,
conflitos e estados. Categoria incerta permanece nula; aprovação exige categoria
permitida e compatibilidade verificável. Condições incluem linguagens, frameworks,
funcionalidades, arquitetura, versões concretas de frameworks, ferramentas e
runtimes globais. Não são inferidas tecnologias pelo nome. Incompatível automática
é omitida com motivo; pedido explícito incompatível bloqueia.

Licenças desconhecidas/incompatíveis, dependências não atendidas, recursos ausentes,
IDs duplicados, conteúdo já catalogado, renderer não suportado e conflitos de alias
aprovado impedem aprovação. Companheiras exigem aprovação própria e fechamento
no mesmo pacote. Pré-requisitos textuais exigem revisão/mapeamento explícitos,
com disponibilidade de ferramentas e runtimes verificada, sem instalação.

URLs HTTPS/SSH da mesma origem não geram dois cadastros. Origem já registrada
permanece no commit fixado; revisão diferente exige update separado. Branches
novas seguem o mecanismo 3A; tags/commits explícitos não seguem branches nem
recebem alegação de disponibilidade remota sem consulta.

Aquisição nunca executa README/SKILL.md, hooks, checkout/filtros ou submódulos.
O conteúdo adquirido é tratado como dado não confiável e confrontado com blobs
Git e hashes. A preparação revalida a inspeção; a aplicação recusa alterações em
Git, candidato, metadados, código de validação ou hash. SSH exige chaves/host key
existentes e é não interativo. Credenciais/configuração global não são gravadas.

Consistência e recuperação mantêm a semântica 3A: global por lote, dois renames
com fsync e breve janela sem Skills; backup e diário recuperam interrupções sem
reset, clean ou exclusões destrutivas. Não consumir concorrentemente à promoção.
Planos 3A continuam reconhecidos; mudança do HEAD exige nova preparação, como antes.

## Demonstração prática isolada

[demonstracao.json](demonstracao.json) registra o cenário de uma origem Git local:

| Candidata | Resultado |
|---|---|
| `good-helper` | explicitamente aprovada e distribuída em Backend |
| `missing-helper` | pendente; referência obrigatória ausente |
| `fastapi` | pendente; conflito com nome aprovado e alias existente |

A tentativa de aprovar a conflitante foi recusada mesmo com acknowledgment.
Somente a válida entrou no pacote da biblioteca de teste. Todas mantiveram
`enabled: false`. A biblioteca mínima da fixture passou de quatro para cinco
aprovadas; isso não é a contagem da biblioteca principal.

O mesmo núcleo inicializou um projeto temporário Python/FastAPI a partir dessa
biblioteca, copiou recursos/licença/proveniência e produziu o alias de descoberta.
Plan/apply/verify passaram e reapply retornou `unchanged`. Não houve dependências
instaladas, gerador externo ou execução da aplicação/fornecedor. As referências
temporárias ficam no JSON para inspeção. Isso comprova arquivos e integração
compartilhada, não ativação nativa numa nova sessão de agente.

## Testes e evidências

Python executor: global asdf **3.14.8**. Suites de execução:

| Conjunto | Resultado |
|---|---:|
| Núcleo/ciclo de vida | 96 passaram |
| Integração compartilhada | 16 passaram |
| Atualizações 3A | 34 passaram |
| Inclusões 3B | 42 passaram |
| Total | **188**, zero falhas/erros/skips |

Os novos testes cobrem os 20 cenários solicitados: origem válida/múltiplas skills,
subdiretório e raiz com recursos, origem existente sem duplicação, bytes duplicados,
conflitos de nome/ID, licenças raiz/assets ausentes ou incompatíveis, recursos e
dependências não atendidos, aprovação/exclusão individual, pendências, hashes,
symlinks/escapes, rede/repo indisponível, recuperação antes/depois da publicação,
idempotência, classificações preservadas, seletor, cópia física, bootstrap
plan/apply/verify, CLI anterior e transporte SSH simulado. Também há branches
locais com barras, tags anotadas, versões de framework e ausência de migração implícita.

Biblioteca completa: 958 arquivos, 101 fechamentos estáticos e sete JS parseados;
zero erros. Não se usou o modo histórico `--copias`, pois ele executa buscas de
fornecedor. As cópias são cobertas pelos testes do núcleo e pelos novos casos,
sem executar fornecedores. O wrapper de clone reutiliza os testes 3A e acrescenta
a suíte e demonstração 3B; validação final de clone será registrada após o commit.

```sh
bash Automacao/python-global Automacao/validacao-inclusoes/executar_testes.py
bash Automacao/python-global Automacao/validacao-inclusoes/demonstrar.py
bash Automacao/python-global Automacao/validacao-atualizacoes/executar_testes.py
bash Automacao/python-global Automacao/validacao-project-bootstrap/executar_testes.py
bash Automacao/python-global Automacao/validacao-integracao-agentes/executar_testes.py
bash Automacao/python-global Skills/validacao/validar_biblioteca.py --sintaxe-node
# Com árvore limpa e commit candidato:
bash Automacao/python-global Automacao/validacao-inclusoes/testar_clone.py
```

Relatórios: [inclusoes.json](inclusoes.json), [atualizacoes.json](atualizacoes.json),
[nucleo.json](nucleo.json), [integracao.json](integracao.json),
[biblioteca.json](biblioteca.json), [fechamentos.json](fechamentos.json),
[catalogo.json](catalogo.json).

## Compatibilidade e limitações

- Schema dos projetos 1/2, regras antigas e comandos 3A preservados. O catálogo
  schema 2 e o lock schema 1 recebem campos opcionais, sem migração/regravação dos
  dados reais. A biblioteca antiga continua aceita sem compatibility declarativo.
- Análise estática não é auditoria semântica completa nem certificação jurídica
  ou de workflows. Imports dinâmicos, serviços autenticados, SDKs e hardware
  precisam de revisão humana; não foram provisionados.
- Novas stacks/condições fora do vocabulário, intervalos semver, renderers especiais,
  recursos fora do escopo esparso e dependências entre pacotes exigem preparação
  posterior. Não se enfraquecem validadores para acomodá-los.
- Aliases existentes dependem de nomes únicos e até 64 caracteres incluindo o
  prefixo. Colisões aprovadas/nomes longos ficam pendentes; não se mudou a integração
  para tentar acomodar esses casos.
- SSH e HTTPS privado não tiveram autenticação real testada: parsing, flags e
  isolamento foram testados; aquisição efetiva usou Git local. Nenhuma origem real
  foi incorporada e nenhuma das 21 pendentes reais foi aprovada.
- Cache/backup/inspeções acumulam até revisão manual; candidatos parciais não são
  sobrescritos. Reversão deliberada de operação concluída é revisão separada,
  não recover automático. Limites POSIX/Fedora e concorrência do mesmo usuário
  permanecem os documentados na 3A.
- Após futura incorporação real, o hash do catálogo muda e a verificação de
  consumidores antigos pode exigir seu commit original do StackNauta em clone
  separado. Nenhum consumidor é migrado ou tem hashes atualizados nesta etapa.
- OpenCode/Gemini não foram executados; nenhuma nova ativação nativa do Codex foi
  alegada. Não há certificação de produção ou publicação remota.

O próximo passo é revisar esta implementação antes de escolher uma origem real;
descoberta, decisões e promoção deverão seguir as autorizações separadas descritas.
