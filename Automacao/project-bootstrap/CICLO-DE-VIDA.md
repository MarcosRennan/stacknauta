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

`GEMINI.md` permanece na política para preservar a classificação de manifestos
históricos. Novos consumidores usam AGENTS.md e não geram esse arquivo.

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

### Catálogos posteriores (4A.1)

Em destinos existentes, a seleção original vem do manifesto, e o lock copiado
precisa corresponder ao hash/tamanho protegido naquele manifesto. O núcleo
reexporta exatamente essa seleção e confronta todos os registros de recursos,
origens, commits e pré-requisitos com o lock fixado. Só os dois hashes globais
históricos de catálogo/lock deixam de ser comparados aos arquivos globais atuais;
seus valores e bytes originais são preservados. O restante do manifesto é
reconstruído e comparado integralmente, inclusive política e conclusão.

Isso permite adicionar skills (até compatíveis) e atualizar outras origens sem
mudar o plano do consumidor. Nenhuma skill nova é selecionada numa reaplicação.
Schemas 1 e 2 mantêm os mesmos IDs e não recebem migração ou regravação de hashes.
Arquivos evolutivos continuam preservados; recursos protegidos adulterados ou
ausentes continuam bloqueados.

O tratamento é conservador: se a biblioteca atual não reproduz os recursos e a
proveniência da seleção histórica, ou se faltam registros verificáveis, não se
certifica integridade a partir de um hash inventado. É necessário usar uma revisão
original confiável do StackNauta num clone separado e fazer revisão manual.
Isso inclui alterações no pacote selecionado (por exemplo README/PROVENANCE
renovados por outra inclusão na mesma origem), mesmo se o SKILL.md não mudou.
Runtimes globais e gerador compatíveis continuam necessários. Não há independência
completa da biblioteca histórica nem assinatura criptográfica dos manifestos.

**Publicação e interrupções (4A.1, Fase 2, A06).** O bootstrap agora cria um
inode anônimo com `O_TMPFILE` no diretório final. Grava os bytes, aplica modo e
sincroniza o arquivo antes de criar o único nome final, exclusivamente. O link
usa `/proc/self/fd` para o descritor próprio, conforme a interface Linux; não
segue um symlink fornecido pelo projeto. Diretórios recém-criados e a entrada
final recebem sincronização. Nunca há dois nomes temporário/final para esse
inode. Antes do link, o kernel descarta o anônimo ao terminar o processo; depois,
o final já tem `nlink=1`. Reaplicar o plano autorizado pode completar ausências
sem alterar finais existentes. Schemas, hashes e classificações não mudaram.

A operação exige filesystem com `O_TMPFILE` e procfs utilizável. Falta de suporte
ou de permissão bloqueia sem fallback para publicação nomeada menos segura.
Arquivos finais continuam passando por tipo, hash/tamanho e contagem de links.
Reexecuções preservam bytes, inode, permissões, mtime e ctime dos finais intactos;
não se promete preservar atime de leituras.

Temporários nomeados de versões anteriores não contêm registro que vincule o nome
a um plano/operação. Mesmo com prefixo, inode e bytes coincidentes, não se prova
automaticamente a propriedade de todos os nomes do inode. Por isso esses nomes
não são apagados: hardlinks antigos continuam bloqueados para revisão manual.
Nomes desconhecidos em áreas protegidas também continuam rejeitados pela
integração. A correção elimina a janela nas novas publicações, sem reduzir as
verificações nem criar um procedimento de exclusão baseado em padrões.

Os testes interrompem processos filhos em `/tmp` antes e depois do link; não
simulam uma queda física de energia. A garantia continua condicionada ao sistema
operacional/filesystem, não cobre controle hostil total pelo mesmo usuário e
não constitui promessa de tolerância absoluta a falhas de hardware.
Referência: [O_TMPFILE e publicação por descritor](https://man7.org/linux/man-pages/man2/open.2.html).
