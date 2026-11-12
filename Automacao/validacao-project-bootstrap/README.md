# Validação do núcleo — Etapa 2A

Testes com biblioteca padrão `unittest`, sem instalar dependências, gerar aplicações completas ou tocar em consumidores existentes:

```bash
asdf exec python -I -B Automacao/validacao-project-bootstrap/executar_testes.py
asdf exec python -I -B Automacao/validacao-project-bootstrap/executar_testes.py --report Automacao/validacao-project-bootstrap/resultado.json
asdf exec python -B Skills/validacao/validar_catalogo.py
```

Com commit candidato e árvore limpa, repetir clone local e ambas as suítes:

```bash
asdf exec python -I -B Automacao/validacao-project-bootstrap/testar_clone.py
```

Esse comando reutiliza o teste de clone anterior, imprime JSON e não grava relatórios na árvore principal. Não configura remotos no StackNauta original nem acessa rede.

O runner verifica primeiro que está no Python global asdf. Os testes reais de CLI precisam de Python e Node globais já instalados; não os instalam quando faltarem. Go, Java/Kotlin e Rust usam estruturas/runners sintéticos somente para testar resolução, falhas, compatibilidade e esqueleto. Nenhum binário sintético é executado. As versões sintéticas e versões de framework nos casos de teste são dados de teste, não recomendações.

## Cobertura

- Configuração válida/inválida, chaves duplicadas/desconhecidas, tipos, escolhas explícitas de linguagem/framework/arquitetura, versões e origem de módulo Go.
- Configuração global asdf ausente, versões ausentes/duplicadas/fallback/system, runtime não instalado/executável, versão real divergente, executor errado e aliases para executáveis externos.
- Isolamento explícito de overrides locais/ambiente e variáveis de autoload; bloqueio de instalação automática de toolchains em probes Go/Rust.
- Política para todas as 101 skills aprovadas; diferentes stacks, ausência de inferência, pendentes/excluídas/incompatíveis e dependências transitivas.
- Exportação byte a byte, arquivos comuns, recursos de irmãs, licenças, commits/hashes e ausência de symlink/hardlink para a biblioteca.
- Dry-run sem criação de destino/raiz padrão, hash revisado, idempotência com bytes/inode/mtime preservados e mudanças de PATH somente diagnósticas.
- Arquivos preexistentes, alterações do usuário, falhas parciais e retomada de arquivos ausentes sem reescrever os publicados.
- Travessia, áreas protegidas, `//`, arquivos especiais/FIFO, symlinks de ancestrais/folhas, hardlinks e injeção de symlink durante publicação.
- Biblioteca mínima em outra localização, sem `_repos/`, e HOME sintético. CLI real usa os runtimes globais já instalados e cria somente projetos temporários Python/FastAPI e TypeScript/Next.js, sem geradores ou instalações.

Diretórios temporários são preservados como evidência; não há exclusão recursiva. Falhas são injetadas por callbacks Python internos aos testes, nunca por comandos de configuração do usuário. O JSON de entrada não oferece hooks ou execução arbitrária.

## Evidências

- [resultado.json](resultado.json): execução completa dos testes, contagem e log.
- [biblioteca.json](biblioteca.json): validadores anteriores com sete origens, 101 planos físicos, sintaxe e buscas UI/UX previamente analisadas na 1.5; nenhum pacote foi reconstruído ou atualizado.
- [preservacao.json](preservacao.json): comparação das duas árvores legadas e hashes/estado da biblioteca aprovada.
- [clone-local.json](clone-local.json): testes do núcleo e validação da biblioteca em clone Git local limpo, sem cache ou dependência de objetos externos; footprint dos arquivos testados.

Os validadores e testes anteriores foram preservados. O validador da biblioteca recebeu somente uma transição explícita de estado: aceita o núcleo 2A declarado em STATUS.json, exige os arquivos correspondentes e mantém `.agents/skills` global vazio. O catálogo, lock, inventário, pacotes e origens da 1.5 permanecem inalterados.

Não estão certificados: descoberta/integração nos três agentes, builds reais Go/JVM/Rust, SDKs Android/Expo, autenticação, implantação, geradores, dependências de aplicação ou serviços. Essas fronteiras permanecem para etapas posteriores, incluindo a integração 2B.
