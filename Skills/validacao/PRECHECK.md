# Pré-check da Etapa 1

Verificações somente leitura concluídas antes de criar o destino:

- Destino ausente; diretório pai com permissão efetiva de escrita e travessia. Nenhum conteúdo existente precisou ser sobrescrito.
- Nenhum `AGENTS.md` encontrado no diretório de trabalho ou em seus ancestrais.
- Git disponível: 2.56.0.
- asdf disponível; `asdf current python` indicou Python **3.14.8**, instalado e selecionado pelo arquivo global `~/.tool-versions`; `asdf which python` e `asdf exec python` confirmaram o mesmo executor. Todos os scripts Python usados nesta etapa foram executados via asdf.
- Consultas iniciais ao GitHub falharam por resolução DNS no sandbox. A consulta foi repetida com acesso de rede autorizado e as sete origens responderam antes da criação. Não restou bloqueio de aquisição.
- Branches padrão e HEADs consultados com `git ls-remote --symref`; resultados fixados em `../fontes.lock.json`.

Antes da criação, foi capturado um baseline das duas árvores legadas: caminhos relativos, tipo/permissão, tamanho, mtime, destino de links e SHA-256 dos arquivos regulares, incluindo metadados Git presentes. O baseline temporário permanece fora desta instalação; `preservacao.json` registra a comparação final. A leitura não seguiu links simbólicos para escrever ou copiar seus alvos.

Durante a inspeção, Node.js global **24.21.0** foi identificado pelo asdf. Bun e `uipro` não estavam disponíveis. Nenhum deles foi instalado ou executado; a inspeção do mecanismo UI/UX foi por leitura de documentação e código. Não houve necessidade de consultar a implementação antiga para construir scripts ou catálogo.

Não foram executados geradores, scripts de fornecedores, instaladores, checkout de submódulos, operações remotas de escrita, `git push` ou instalação global. As escritas de entrega ficaram no novo StackNauta; evidências temporárias próprias foram gravadas em diretório temporário.
