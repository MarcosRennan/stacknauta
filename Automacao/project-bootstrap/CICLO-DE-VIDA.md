# Ciclo de vida — política 2D.1

O bootstrap registra o conteúdo que criou. Isso não autoriza restaurá-lo sobre
desenvolvimento posterior. Os comandos `agent-*` usam uma só política, sem force,
atualização silenciosa de hashes ou aceitação de alterações protegidas.

| Classe | Regra sobre caminhos gerados | Após conclusão |
|---|---|---|
| Protegido | `.stacknauta/**`, `.agents/skills/**`, `.tool-versions`; outros caminhos gerados não listados abaixo | Hash/tamanho originais e estrutura física rigorosos. Alteração ou ausência bloqueia. |
| Evolutivo | `pyproject.toml`, `package.json`, `tsconfig.json`, `go.mod`, `Cargo.toml`, `.gitignore`, `README.md`, `AGENTS.md`, `GEMINI.md`, `BUILD-PLAN.md`, `docs/REQUIREMENTS.json` | Modificações e remoções relatadas e preservadas; nunca sobrescrever ou recriar automaticamente. |
| Desenvolvimento inicial | `src/lib.rs` e placeholders gerados `src/**/.gitkeep`, `tests/**/.gitkeep` | Mesma preservação; código e testes posteriores pertencem ao desenvolvimento. |
| Adicional não gerenciado | Caminhos fora do conjunto gerado | Inventariar caminho/tipo sem alterar, remover ou executar. |

A classificação é por caminho, não extensão. README/JSON dentro das skills são
protegidos. O índice `.agents/skills/README.md` e o documento interno
`.stacknauta/AGENT-INTEGRATION.md` também são protegidos. A lista está em
`stacknauta_core/lifecycle.py`, com padrão fechado para caminhos desconhecidos.

O inventário completo da integração recusa adicionais em `.stacknauta/` e
`.agents/skills/`; não aceita skills novas só por aparecerem no destino. O núcleo
simples `plan/apply` valida seu próprio conjunto. A validação das adições de
integração pertence aos comandos `agent-*`; no núcleo simples podem aparecer
como arquivos não geridos por ele.

## Relatórios e estrutura física

Sucesso mantém `status: verified`; `verification_state` distingue `intact` de
`verified_with_evolution`. `lifecycle` contém `modified` com hash/tamanho original
e atual, `removed` e `unmanaged`. Existe `integration_lifecycle` separado.
No dry-run, action é `create`, `unchanged`, `preserve_modified` ou
`preserve_removed`; sha256/size de files continuam descrevendo a origem inicial.

Arquivos evolutivos precisam continuar regulares e físicos, com nlink=1.
Diretório ou arquivo especial substituindo arquivo gerido, symlinks em componentes
geridos e hardlinks são erros estruturais. Hashes são calculados em streaming,
sem usar tamanho original como limite para crescimento. Não se certifica sintaxe
ou semântica da aplicação: TOML/JSON alterado precisa das validações da stack.
Remoção permitida não significa que a aplicação continuará executável.

Links adicionais são inventariados como `symlink_not_followed`, nunca percorridos,
copiados ou usados pelo bootstrap; isso não certifica o alvo. Inventário
inacessível ou acima de 128 níveis bloqueia. Erros mantêm código 2; conflito de
conteúdo informa classe, hashes e tamanhos esperados/atuais. Não regravar hashes.
Tamanho protegido diferente é recusado antes de ler o conteúdo; o hash atual é
marcado como não calculado nesse caso. A proteção contra payload incompatível
permanece, enquanto o tamanho original não limita conteúdo evolutivo concluído.

## Conclusão e retomada

Novos projetos usam manifesto **schema 2**, com hashes/tamanhos iniciais, política
2D.1 e classificação por arquivo. O caminho do marcador
`.stacknauta/bootstrap-complete.json` faz parte da identidade. O marcador guarda
ID do plano e hash do manifesto e é publicado **por último** no núcleo, depois de
todos os recursos. Seu conteúdo determinístico aparece no dry-run e é protegido.
A integração conserva schema 1 e seu marcador final `agent-integration.json`.

Antes do marcador, arquivos presentes precisam corresponder ao plano; a mesma
aplicação autorizada pode completar ausências. Depois dele, ausências evolutivas
não são restauradas e ausências protegidas bloqueiam. Remover/adulterar o marcador
nunca produz verificação bem-sucedida. Somente sua ausência com conteúdo inicial
intacto é indistinguível de interrupção antes da última publicação: uma reaplicação
explícita conclui esse estado. Havendo evolução sem marcador, o conflito exige
revisão. Não se infere intenção nem se oferece recuperação destrutiva.

Sem arquivos a criar, idempotência preserva bytes, inode, permissões, mtime e ctime
de arquivos e diretórios. Na retomada parcial, diretórios que recebem novas
entradas necessariamente mudam; arquivos já completos são preservados.

## Compatibilidade

Manifestos **schema 1** das etapas 2A/2B/2C são aceitos sem reescrita, migração ou
novo marcador automático. Gerador de conteúdo `2A.1` foi mantido para reproduzir
exatamente bytes, hashes e IDs anteriores. A leitura usa a política explícita
2D.1. O config normalizado com `skills: null` passa a equivaler à ausência de
seleção explícita, sem troca de stack ou mudança do plano original.

Sem marcador histórico, schema 1 é conservadoramente considerado concluído:
remoções evolutivas são preservadas e ausência protegida bloqueia, sem reconstrução.
Um projeto antigo incompleto exige diagnóstico numa cópia isolada. Não há
migração ou reparo automático. Projetos 2A sem integração podem usar `plan/apply`;
`agent-plan/apply` propõem as adições 2B, e agent-verify exige integração concluída.
Schema desconhecido ou política adulterada bloqueia; não fazer downgrade silencioso.

Hashes vinculam conteúdo inicial/configuração/recursos e, no schema 2, a política.
Evoluções não viram novas origens nem silenciosamente alteram IDs. A reaplicação
continua exigindo hash revisado e autorização; não concede autorização tecnológica.
Confiança na biblioteca e no executável local continua necessária. Manifestos não
são assinaturas contra invasor com controle do mesmo usuário. Renomeação concorrente
de ancestrais pelo mesmo usuário permanece fora da garantia anterior; dirfd,
O_NOFOLLOW e publicação exclusiva são mantidos.
