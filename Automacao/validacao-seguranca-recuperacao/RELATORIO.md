**StackNauta — Etapa 4A.1, Fase 2: segurança e recuperação (A05–A07)**

Concluída em 12/11/2026, horário de Fortaleza. Commit inicial:
`b50fda14386af31e9e18598117d78797d549e3b6`. O estado Git inicial estava limpo,
sem alterações preexistentes. Foram lidos o relatório da Fase 1, os módulos
indicados no pedido e os testes relacionados. Não foi encontrado um relatório
separado da auditoria 4A nessa revisão; as referências do pedido foram conferidas
no código atual. Os três cenários foram reproduzidos antes de alterar produção.

**A05 — persistência das inclusões e atualizações**

Causa confirmada: o diário recebia sincronização de arquivo e diretório, mas os
arquivos copiados/escritos na árvore candidata não tinham uma barreira equivalente
antes dos renames ou de `committed`. A reprodução instrumentou os inodes dos
arquivos candidatos: a primeira promoção ocorria sem que todos recebessem fsync.

Correção: o mesmo diário e os mesmos backups foram mantidos. A preparação agora
confere hashes/modos, sincroniza os arquivos e os diretórios candidatos de baixo
para cima e persiste plano/diff antes de `prepared`. A entrada do diretório da
sessão também é sincronizada. Apply reconfere e sincroniza o candidato e a árvore
anterior antes da primeira promoção. Cada rename sincroniza os dois diretórios
pais. Depois da publicação, o conjunto ativo precisa coincidir com o candidato e
ser sincronizado antes de gravar `committed`. Não há exclusão automática de backup.

Recuperação verifica a identidade do plano, a fase conhecida do diário e a árvore
anterior completa, com hashes e modos. O cache `_repos` é preservado sem ser usado
como evidência. Backup adulterado, destino inesperado ou fase desconhecida bloqueia
para revisão. Sem backup, só se conclui rollback se a biblioteca ativa já for
exatamente a anterior; ativo e backup ausentes têm diagnóstico explícito. A árvore
rejeitada após promoção é preservada em `failed-Skills-*`. `rolled_back` só é
registrado depois da sincronização da árvore restaurada.

O formato do diário não mudou: fases antigas conhecidas continuam aceitas e passam
pelas novas verificações. Uma reaplicação de diário `committed`, inclusive antigo,
confere e sincroniza os arquivos antes de retornar `ja_aplicado`. Isso verifica o
estado disponível agora, sem afirmar como um diário antigo persistiu no passado.
Estados ambíguos não são promovidos nem reparados por suposição.

Testes direcionados: **13 novos casos aprovados** para A05, distribuídos entre
`MaintenanceRecoveryTests` e o caso de inclusão. Cobrem arquivos sincronizados antes
do primeiro rename; falha de escrita na preparação; falha de sincronização antes
e depois da promoção; conclusão após a barreira; interrupção antes e depois da
publicação; diário antigo; backup íntegro, ausente e adulterado; fase desconhecida;
falha após gravação de `committed`; recuperação idempotente; nova preparação e
aplicação após rollback. Os testes existentes de promoção normal, autorização,
inclusão e preservação da árvore ativa também passaram.

Arquivos: `Automacao/manutencao-skills/atualizacoes.py`, `README.md`,
`Automacao/validacao-atualizacoes/test_security_recovery.py` e
`Automacao/validacao-inclusoes/test_additions.py`.

**A06 — hardlinks temporários no bootstrap**

Causa confirmada: o bootstrap escrevia um temporário nomeado, criava o hardlink
final e depois removia o temporário. Encerrar um processo filho logo após o link
deixou `nlink=2`; o verificador recusou a retomada. Interromper antes do link também
deixou um nome temporário. Ambas as reproduções usaram somente arquivos sintéticos.

Correção escolhida: eliminar a janela nas novas publicações. O arquivo é criado
com `O_TMPFILE` no diretório de destino, sem nome. Depois de gravar bytes, aplicar
modo e fsync, o próprio descritor é publicado exclusivamente por `/proc/self/fd`.
Antes disso há zero nomes; depois, um nome e `nlink=1`. Ao terminar o processo,
o kernel descarta o inode ainda anônimo. Não há busca ou remoção de nomes por
prefixo, formato ou coincidência de conteúdo. Diretórios recém-criados também
recebem sincronização de sua entrada no pai.

Finais existentes nunca são substituídos. Tipo, hardlinks, hash/tamanho e estado
do plano continuam verificados pelo núcleo. Reaplicar o plano autorizado completa
ausências e preserva arquivos intactos. Schemas 1 e 2, classificações, hashes e
comandos não mudaram; não foi necessário criar metadados persistidos adicionais.

**Limite para versões antigas:** temporários nomeados legados não têm registro
que vincule todos os nomes a uma operação. Mesmo prefixo, inode e bytes iguais
não provam propriedade suficiente para apagar um nome desconhecido. Por isso um
hardlink legado continua bloqueado para revisão manual e nenhum nome é apagado.
A solução recupera as novas interrupções pela eliminação da janela, sem diminuir
a proteção contra temporários de outra operação, symlinks ou finais adulterados.

Testes direcionados: **11 novos casos aprovados**, incluindo publicação normal,
processo filho interrompido antes/depois do link, inode anônimo e conteúdo
correspondentes ao final, repetição preservando bytes/inode/modo/mtime/ctime,
temporário de mesmo prefixo com bytes diferentes, outra operação, temporário
symlink, final adulterado, hardlink legado sem prova e falta de suporte a
O_TMPFILE. A falta de suporte bloqueia sem fallback nomeado. Não se promete
preservar atime de leituras. Os testes de integração que recusam arquivos
desconhecidos em áreas protegidas permaneceram aprovados.

Arquivos: `Automacao/project-bootstrap/stacknauta_core/filesystem.py`,
`Automacao/project-bootstrap/CICLO-DE-VIDA.md` e
`Automacao/validacao-project-bootstrap/test_publication.py`.

**A07 — operações de filesystem da manutenção**

Causa confirmada: `safe` verificava caminhos e chamadas posteriores de pathlib/os
voltavam a abri-los pelo texto. A reprodução trocou um arquivo por symlink após
a inspeção; a leitura antiga não recusou o alvo substituído.

Correção: reutilizadas as primitivas de diretórios físicos do núcleo. Leituras,
escritas, cópias, locks, varredura da árvore e metadados usam operações relativas
a descritores, `O_NOFOLLOW`, `O_NONBLOCK` e fstat. Truncamento só ocorre após
validar arquivo regular com um link. Hash e modo são obtidos do mesmo descritor;
tamanho, timestamps e identidade observáveis são conferidos. A varredura não segue
symlinks nem abre arquivos especiais. Metadados confirmam o inode do temporário
e do resultado publicado; um nome temporário substituído não é apagado.

Renames usam a primitiva Linux `renameat2(RENAME_NOREPLACE)` por ctypes da stdlib,
com pais abertos e conferência de inode; não sobrescrevem um destino que apareceu
concorrentemente. Ausência de suporte bloqueia. O subprocesso Git recebe a base
aberta por descritor e o validador recebe seu script aberto. Os parsers Bash/Node
recebem bytes seguros por stdin, sem executar os scripts analisados; o tipo de
módulo JS declarado é preservado. O lock filtrado da aquisição e as escritas das
inclusões usam as mesmas operações seguras. Não foi criada uma camada de objetos
de filesystem, banco de dados ou dependência externa.

Testes direcionados: **15 novos casos aprovados** para A07: 13 em
`MaintenanceFilesystemTests`, mais troca após inspeção e parsing seguro nos testes
de manutenção. Cobrem arquivo regular, symlink final e intermediário, hardlink,
FIFO com prazo controlado, diretório no lugar de arquivo, substituição entre
inspeção/abertura, escape, EACCES injetado, destino criado durante rename,
temporário de metadados substituído por symlink e parsing de JS module/CommonJS.
Os sentinelas externos sintéticos permaneceram intactos. Os fluxos normais de
inclusão e atualização e seus testes de CLI passaram após a correção.

Arquivos: `Automacao/manutencao-skills/atualizacoes.py`, `inclusoes.py`,
`atualizacao_receita.py`, `README.md`,
`Automacao/project-bootstrap/stacknauta_core/filesystem.py` e
`Automacao/validacao-atualizacoes/test_security_recovery.py`.

**Garantias e limites reais**

A ordem implementada é dados verificados/sincronizados, diretórios sincronizados,
renames com pais sincronizados, verificação/sincronização ativa e, por último,
conclusão do diário. Isso não transforma dois renames e um arquivo de diário em
uma única transação atômica. Existe uma janela sem `Skills`. Falhas detectadas
retornam erro e tentam recuperação conservadora; falha no rollback exige revisão,
sem presumir sucesso nem descartar a evidência.

fsync depende do kernel, filesystem, montagem e dispositivo honrarem a operação.
Não foram simuladas quedas físicas de energia ou falhas de hardware; tmpfs não
constitui evidência de persistência após desligamento. Não há garantia universal
para NFS, hardware defeituoso, corrupção ou ambientes sem procfs/O_TMPFILE/
renameat2. Em caso de suporte/permissão insuficiente, a operação bloqueia.

Descritores reduzem a substituição por symlinks e evitam truncar alvos inseguros.
Não congelam o namespace ou o conteúdo contra outro processo do mesmo usuário.
Renomeação de ancestrais inteiros, escrita no inode já aberto e alteração hostil
de código, módulos importados, executáveis ou configuração interna dos
subprocessos permanecem fora de uma garantia irrestrita. O flock é cooperativo.
Metadados locais continuam sem assinatura contra controle total do mesmo usuário.
Temporários legados sem propriedade verificável permanecem manuais.

Referências técnicas consultadas: [fsync e diretórios](https://man7.org/linux/man-pages/man2/fsync.2.html),
[O_TMPFILE](https://man7.org/linux/man-pages/man2/open.2.html),
[renameat2](https://man7.org/linux/man-pages/man2/rename.2.html) e
[parsing do Node](https://nodejs.org/docs/latest-v24.x/api/cli.html#-c---check).

**Integração e regressão final**

Antes da regressão, os testes direcionados foram executados por achado, seguidos
dos fluxos de integração: CLI de inclusão, atualização, autorização/hash,
reaplicação idempotente, retomada parcial, schema 1 e consumidor temporário
verificado depois de inclusão e atualização de outra origem.

A regressão completa foi executada **uma única vez**, sem repetir a cadeia de
clones antigos, no commit `ee2bb5c6656187f992a0c1d0fb86bb39c9e2d489`.
Intervalo: 13/11/2026, 00:09:12–00:10:44 UTC (12/11 em Fortaleza), cerca de
93 segundos. Foi reutilizado o runner existente:

```sh
Automacao/python-global Automacao/validacao-correcoes-funcionais/executar_testes.py --report /tmp/stacknauta-4a1-fase2-regressao.json
```

| Verificação | Resultado |
|---|---|
| Núcleo/ciclo de vida/publicação | 110 aprovados |
| Integração dos agentes | 16 aprovados |
| Atualizações/filesystem/recuperação | 69 aprovados |
| Inclusões | 47 aprovados |
| Total | **242; zero falhas, erros ou skips** |
| Biblioteca | 958 arquivos verificados; zero erros |
| Cópias físicas | 101 casos; 4.114 arquivos copiados |
| Sintaxe JavaScript da biblioteca | 7 arquivos aprovados |
| Smoke tests já existentes | 3 aprovados |
| Origin do clone | preservado e inalterado |
| Árvore do clone após testes | limpa; sem cache nem alternates |

Os 203 testes anteriores e 39 novos passaram. A biblioteca mantém o status
histórico `passed_with_documented_pending`, referente às classificações
anteriores; não há teste desta fase pendente ou bloqueio ambiental.

Ambiente observado: Linux `7.2.15-200.fc44.x86_64`, workspace Btrfs e `/tmp` tmpfs.
Como a suíte usa `/tmp`, foi feito adicionalmente um único probe curto no Btrfs,
em diretório temporário novo sob `/home/marcosrennan/Projetos`, separado do
repositório e dos consumidores. Publicação anônima, nlink=1, preservação de
metadados, fsync de arquivos/diretórios, rename sem substituição e metadados JSON
passaram. Somente esse diretório sintético foi limpo. Isso confirma suporte às
primitivas e retorno de sincronização, sem validar um desligamento real.

Os resultados completos, logs por teste e probe estão em
[resultado.json](resultado.json). Não houve alteração no código de implementação
após a regressão nem segunda execução da suíte completa.

**Preservação, compatibilidade e commits**

`git diff --exit-code b50fda14386af31e9e18598117d78797d549e3b6 HEAD -- Skills`
retornou zero. **Toda a árvore Skills permaneceu idêntica**, incluindo nove
pacotes de distribuição, 101 skills aprovadas, 21 pendentes e duas excluídas,
licenças, revisões, catálogo e locks. Os arquivos de descoberta dos agentes e suas
instruções também permaneceram idênticos. Não foi aplicada atualização real.

Não houve escrita em App-Web ou consumidores existentes, instalação de runtimes
ou dependências, configuração de remotos reais, push ou alteração global do asdf.
Os testes de falha usaram somente diretórios temporários e dados sintéticos.
A preservação dos consumidores reais resulta do escopo das operações; eles não
foram usados como fixtures nem receberam inventário ou migração nesta fase.
Somente Python/Node globais existentes do asdf foram usados para os fluxos reais;
simulações de outros runtimes presentes nas suítes foram mantidas. Codex,
OpenCode e Gemini não foram executados como subprocessos.

Schemas 1/2, dry-run, autorização explícita por hash, cópia física, seleção,
classificações e política de ciclo de vida continuam cobertos. Novos nomes
desconhecidos não são aceitos nem removidos automaticamente. O escopo foi A05,
A06 e A07; não houve implementação de A08 ou refatoração geral.

Commit de implementação/testes/documentação técnica: **`ee2bb5c`** —
`fix: reforçar persistência e filesystem nos achados A05–A07`.
O commit posterior de evidências adiciona apenas este relatório e `resultado.json`;
seu identificador é informado na entrega. Nenhum commit foi publicado remotamente.
