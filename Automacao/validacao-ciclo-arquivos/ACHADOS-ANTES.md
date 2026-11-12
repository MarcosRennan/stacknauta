# Investigação registrada antes da alteração do código — Etapa 2D

Base: commit 39d805d. Reproduzido no consumidor 2C por `agent-verify` com a
configuração declarativa original externa: código 2, `Arquivo inesperadamente
grande: pyproject.toml`. Nenhum comando de aplicação foi usado no consumidor.

1. `filesystem.read` compara fstat.st_size com o limite recebido. `Target.inspect`
   passa `len(data)` do arquivo original. O pyproject cresceu de 131 para 535
   bytes e é recusado antes da comparação de conteúdo. Reduzir ou manter o tamanho
   ainda produziria conflito, pois a comparação seguinte exige igualdade binária.
2. `core.Bootstrap.plan` regenera todos os bytes e um manifesto schema 1 com
   sha256/tamanho iniciais de todos os arquivos. O manifesto inteiro precisa
   corresponder ao plano regenerado. Não há classificação de ciclo de vida.
3. `Target.apply` repete a inspeção e compara todos os arquivos novamente antes
   de publicá-los exclusivamente. Reescritas são impedidas. Ausências são
   recriadas indistintamente para permitir retomada de falhas parciais.
4. `AgentIntegration.verify` chama o mesmo plan e exige nenhuma ausência.
   A integração compara todos os seus quatro arquivos de forma estrita, inclusive
   GEMINI.md. Seu manifesto adicional é publicado por último.
5. Arquivos adicionais são atualmente ignorados, incluindo código/testes legítimos.
   Eles não têm inventário de relatório. Arquivos especiais, symlinks e hardlinks
   nos caminhos geridos já são bloqueados por dirfd/O_NOFOLLOW e precisam continuar.
6. Os 65 testes 2A e 16 testes 2B cobrem publicação exclusiva, retomada, conflitos,
   cópia e caminhos perigosos. Um teste exige bloquear README modificado, que é
   precisamente o contrato a corrigir. Faltam evolução legítima, remoção sem
   restauração, classificação, relatório de adicionais e fixtures de manifestos
   anteriores independentes do gerador atual.
7. O config.json normalizado tem skills:null e não é aceito como entrada bruta
   pelo normalizador atual. A reprodução usa o pedido bruto preservado; esse
   contrato bruto será preservado. Para compatibilidade com a configuração que o
   próprio núcleo já grava, skills:null passará a equivaler à ausência de seleção
   explícita. Esse ajuste pontual não é a causa do conflito de integridade.

## Decisão de implementação

Manter gerador de conteúdo, versões de fontes e biblioteca. Introduzir política
por caminhos explícitos, com padrão protegido. Manifestos schema 1 permanecem
byte a byte e conservam hashes/IDs. Novos manifestos schema 2 registram a política
e um marcador de conclusão protegido, publicado por último. Esse marcador permite
retomar publicações parciais sem restaurar arquivos evolutivos removidos depois
da conclusão. Projetos schema 1 completos são interpretados conservadoramente
como concluídos, sem migração ou escrita automática; ausências protegidas bloqueiam.

Protegidos: manifestos, metadados .stacknauta, todos os recursos/índices/aliases
de skills e .tool-versions. Evolutivos: lista exata de arquivos de aplicação e
documentação gerados, inclusive pyproject/package/GEMINI/AGENTS. Desenvolvimento:
sementes src/lib.rs e placeholders gerados em src/tests, além de arquivos novos.

Modificações e remoções evolutivas após conclusão são relatadas e preservadas;
não há restauração automática. A validação não certifica sintaxe ou semântica da
aplicação: valida tipo físico e integridade do que é protegido. Conteúdo evolutivo
é identificado por hash em streaming, sem usar o tamanho original como limite.
Adicionais são inventariados sem seguir links; namespaces protegidos não aceitam
arquivos desconhecidos na verificação completa da integração.

Manter autorização pelo plano revisado, limites do destino, dirfd, publicação
exclusiva e hashes imutáveis. Não executar ou modificar o consumidor de referência,
App-Web, ferramentas de outros agentes, geradores ou instalações. Testes de escrita
usarão somente temporários; o consumidor será verificado novamente por leitura.
