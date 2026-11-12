# Etapa 2D — correção do ciclo de vida dos arquivos

## Causa raiz reproduzida

Antes de editar o núcleo, `agent-verify` no consumidor FastAPI retornou código 2:
`Arquivo inesperadamente grande: pyproject.toml`. O arquivo original tinha 131
bytes; o autorizado posteriormente tinha 535. `Target.inspect` passava len do
conteúdo inicial para `filesystem.read`, que recusava crescimento antes de
comparar hashes. Mesmo sem crescer, o arquivo diferente seria recusado, pois não
havia política que distinguisse configuração evolutiva de metadados protegidos.

[ACHADOS-ANTES.md](ACHADOS-ANTES.md) registra geração, comparação, ausências,
falhas parciais, integração, cobertura e decisão antes da alteração do código.
[reproducao-antes.json](reproducao-antes.json) preserva a reprodução por leitura.

## Solução e arquivos

O gerador de conteúdo e a biblioteca não foram reconstruídos. A política explícita
fica em `stacknauta_core/lifecycle.py`; o filesystem reutiliza dirfd, O_NOFOLLOW e
publicação exclusiva existentes. Hashes evolutivos são calculados em streaming
limitado ao tamanho observado no início da leitura, detectando alteração concorrente.
Conteúdo protegido de tamanho incompatível é recusado antes de ler o payload.

- `filesystem.py`: inspeção por classe, streaming, inventário sem seguir links,
  conclusão/retomada e preservação de modificações/remoções após conclusão.
- `core.py`: schema 2 para novos projetos e marcador protegido final; reconstrução
  exata de schema 1 para existentes; relatórios de ciclo de vida.
- `integration.py`: mesma política para GEMINI.md e proteção de aliases/metadados;
  inventário completo rejeita adicionais em namespaces protegidos.
- `config.py`: skills:null do JSON já gravado equivale à ausência de seleção
  explícita, permitindo reutilizar a configuração existente sem mudar os IDs.
- `test_bootstrap.py`: um contrato anterior mudou de bloquear README legítimo
  para preservá-lo; a proteção estrita é coberta por testes específicos.
- `test_lifecycle.py`: 31 regressões novas, com subcasos adicionais.
- README principal, README do núcleo, guia de integração e skill: orientação atualizada.
- `CICLO-DE-VIDA.md`: política, esquema, compatibilidade e limites completos.
- Esta pasta: investigação, reprodução, resultados e teste de clone.

## Política

| Classe | Caminhos | Comportamento concluído |
|---|---|---|
| Protegido | `.stacknauta/**`, `.agents/skills/**`, `.tool-versions`, gerados desconhecidos | Diferença/ausência bloqueia; nunca recalcular origem para aceitar alteração. |
| Evolutivo | Lista exata de configs/documentação: pyproject, package, tsconfig, go.mod, Cargo.toml, gitignore, README, AGENTS, GEMINI, BUILD-PLAN e docs/REQUIREMENTS.json | Relatar hash/tamanho original e atual ou remoção; preservar sem sobrescrever/restaurar. |
| Desenvolvimento inicial | src/lib.rs e placeholders gerados em src/tests | Preservar edição e remoção. |
| Adicional | Arquivos/diretórios fora do conjunto gerado | Inventariar e preservar; não executar nem seguir links. |

As regras são por caminho, não extensão. Um README nas referências de skill
continua protegido. Novos arquivos desconhecidos em áreas protegidas são proibidos
na verificação completa de integração. Um link adicional fora delas é relatado
como não seguido, não como alvo certificado. A validação não é lint de aplicação.

## Contratos e compatibilidade

Sucesso mantém `status: verified`, com `verification_state: intact` ou
`verified_with_evolution`; lifecycle diferencia modified, removed e unmanaged.
Erros continuam código 2. Dry-run e hash revisado continuam obrigatórios. Alterar
um arquivo evolutivo não altera a origem nem o ID inicial; isso não autoriza
operações tecnológicas ou regravação de hashes.

Novos manifestos schema 2 incluem a política na identidade e um marcador
bootstrap-complete.json publicado no final. Antes da conclusão, o mesmo plano
pode completar ausências; depois, arquivos evolutivos removidos não voltam.

Schema 1 completo (2A/2B/2C) é aceito sem migração, reescrita ou novo marcador.
Gerador 2A.1 foi mantido para reproduzir seus bytes e IDs exatamente. Por não ter
marcador histórico, esse formato é tratado como concluído: ausência protegida
antiga bloqueia em vez de inferir recuperação. Incompletos antigos exigem análise
manual em cópia isolada. Nenhuma migração foi necessária no caso real.

## Problema original: antes e depois

| Item | Antes | Depois |
|---|---|---|
| Verificação do consumidor 2C | código 2, tamanho inesperado | código 0, verified_with_evolution |
| pyproject 535 bytes | rejeitado | modificação evolutiva, hash original e atual informados |
| Outros 28 arquivos | íntegros | íntegros e preservados |
| Adicionais do desenvolvimento/venv | ignorados | 2.226 entradas inventariadas sem adoção/execução |
| ID de integração | aee4b748... | mesmo ID completo |
| Migração/escrita no consumidor | nenhuma | nenhuma |

O consumidor foi usado somente com plan/verify, nunca apply. Uma comparação de
2.266 entradas confirmou bytes, inode, permissões e timestamps preservados.
App-Web teve 4.259 entradas conferidas, sem alteração. Os 1.004 arquivos já
rastreados sob Skills permanecem idênticos. Configuração global asdf preservada.
Os IDs completos e hashes estão em [referencia-depois.json](referencia-depois.json).

## Testes

- **96 testes do núcleo passaram**: 65 anteriores (um contrato ajustado) e 31
  novos de ciclo de vida, sem falhas/skips.
- **16 testes de integração passaram**, sem falhas/skips.
- Biblioteca: 958 arquivos de pacote, 101 casos de cópia física, sete arquivos
  JavaScript apenas parseados; zero erros. Fontes/101 skills não regeneradas.
- Fixtures schema 1 de núcleo e integração, IDs/bytes imutáveis, config normalizado,
  alterações pyproject/package/docs/GEMINI, remoções evolutivas, código/testes
  adicionais, adulterações em dez caminhos protegidos, ausência protegida,
  troca por diretório, symlink/hardlink, escapes, política/schema adulterados,
  falhas parciais antes do pyproject e do marcador, concorrência de leitura e
  rejeição de payload protegido sem lê-lo.
- Reexecuções temporárias preservaram bytes, inode, mode, mtime e ctime. Durante
  recuperação parcial, diretórios que recebem novos arquivos mudam naturalmente;
  os arquivos já completos permanecem idênticos.
- Clone local limpo sem `_repos/`: **passou**, repetindo os 112 testes e os 101
  casos de cópia. A CLI real aceitou crescimento de pyproject e arquivos novos,
  verificou evolução e reaplicou sem alterar bytes, inode, mode, mtime ou ctime.
  A árvore do clone permaneceu limpa. [clone-local.json](clone-local.json).

Evidências: [nucleo.json](nucleo.json), [integracao.json](integracao.json),
[biblioteca.json](biblioteca.json). Os runners antigos mantêm seus rótulos históricos
2A/2B; os resultados aqui correspondem ao código testado nesta etapa 2D.

```sh
asdf exec python -I -B Automacao/validacao-project-bootstrap/executar_testes.py
asdf exec python -I -B Automacao/validacao-integracao-agentes/executar_testes.py
asdf exec python -I -B Skills/validacao/validar_biblioteca.py --copias --sintaxe-node
# Com commit candidato e árvore limpa; nenhum agente ou gerador é iniciado:
asdf exec python -I -B Automacao/validacao-ciclo-arquivos/testar_clone.py
```

## Limitações e riscos restantes

- Valida integridade/estrutura do bootstrap, não sintaxe, correção ou execução da
  aplicação. Remover configuração evolutiva pode tornar a aplicação inválida.
- Projetos schema 1 incompletos não são reconstruídos automaticamente.
- Perda do marcador final com conteúdo inicial intacto é indistinguível de falha
  antes de sua publicação; verify recusa incompletude e apply autorizado pode
  concluir esse estado. Evolução sem marcador exige revisão.
- Inventário inacessível ou muito profundo bloqueia; não certifica links adicionais.
- Limites POSIX/Fedora e ataques concorrentes do mesmo usuário renomeando ancestrais
  permanecem. Manifestos não são assinaturas contra controle total do mesmo usuário.
- Verificação ainda exige runtimes globais e biblioteca compatíveis; não implementa
  atualização de stacks, dependências, origens ou migração automática.
- OpenCode/Gemini não foram executados. Os testes de aplicação da 2C não foram
  repetidos no consumidor, preservado integralmente. Nenhuma instalação ou gerador.
- A ocorrência histórica dos horários Git não é atribuída a um ator nesta etapa;
  não houve limpeza, reset, restauração ou publicação remota.

O commit de implementação validado no clone é
`aa3fecae0ff38649ffb9713f8a259a2deff1954f`. O commit de evidências posterior
acrescenta somente os relatórios e esta atualização, sem mudança de código após
os testes. A conferência final está em [preservacao.json](preservacao.json) e o
resultado consolidado em [resultado.json](resultado.json).
