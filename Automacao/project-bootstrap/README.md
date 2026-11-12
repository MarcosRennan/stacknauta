# project-bootstrap — núcleo 2A

Prepara somente um esqueleto inicial. Não desenvolve regras de negócio, não executa geradores, não instala dependências/runtimes, não inicia serviços e não faz operações Git nos consumidores. A integração com Codex, OpenCode/DeepSeek e Gemini CLI permanece para a Etapa 2B. **Não certificado para produção.**

## Interface

Da raiz do StackNauta:

```bash
./Automacao/project-bootstrap/project-bootstrap plan --config Automacao/project-bootstrap/examples/python-fastapi.json
./Automacao/project-bootstrap/project-bootstrap apply --config Automacao/project-bootstrap/examples/python-fastapi.json --plan-id HASH_RETORNADO_PELO_PLAN
```

`plan` é o dry-run: imprime JSON com entradas normalizadas, versões globais verificadas, skills/fechamentos, omissões justificadas, arquivos/hashes e plano pendente para o agente. Não cria o destino. `apply` exige esse `plan_id`, refaz os pré-checks e recusa um plano desatualizado. Saída bem-sucedida em stdout, erros claros em stderr, exit code 2 para bloqueio. Não há opção force, atualização, instalador, comando arbitrário ou adaptação por agente.

O launcher Bash resolve o Python global diretamente pelo asdf antes de executar Python. Usa o executável real dentro da instalação, com `-I -S -B`, sem shim/local/system fallback, PYTHONPATH, site-packages ou bytecode. Não iniciar pela versão Python do sistema. O executor exige Python global instalado >=3.11.

## Entrada JSON

```json
{
  "schema_version": 1,
  "name": "minha-api",
  "destination": "~/Projetos/minha-api",
  "stack": {
    "languages": ["python"],
    "frameworks": [{"name": "fastapi", "version": "0.123.4"}],
    "architecture": "hexagonal-ddd"
  },
  "requirements": {
    "features": ["api"],
    "description": "Requisitos iniciais definidos pelo usuário.",
    "constraints": ["Desenvolver a aplicação em prompts posteriores."]
  }
}
```

A versão de framework acima ilustra a sintaxe; não é recomendação de versão. Para uma versão real, informar a versão escolhida pelo usuário. Se omitida, fica pendente no plano do agente: não se usa latest nem se inventa uma versão. Dependências são apenas declaradas em pyproject/package.json quando o usuário informou uma versão concreta; nenhum comando de instalação é executado.

- `name`: slug minúsculo, até 64 caracteres, sem barras.
- `destination`: opcional. Padrão `$HOME/Projetos/<name>`. Aceita absoluto ou `~/...`; recusa travessia, caminhos reservados e symlinks. Um pai explícito fora da raiz padrão precisa existir. O núcleo pode criar a própria raiz padrão `Projetos/` em HOME depois dos pré-checks.
- `stack.languages`: obrigatório e não vazio. Python, JavaScript, TypeScript, Go, Java, Kotlin e Rust, usando nomes canônicos minúsculos.
- `stack.frameworks`: lista opcional de nomes ou objetos `{name, version}`. Cada framework precisa de uma linguagem explicitamente declarada. A lista suportada está em `stacknauta_core/config.py`; entradas desconhecidas são recusadas. Lista vazia não escolhe framework.
- `stack.architecture`: opcional; `flat`, `hexagonal` ou `hexagonal-ddd`. Ausência não define arquitetura. As duas variantes hexagonais criam apenas diretórios vazios de domínio/aplicação/adapters/bootstrap. Somente `hexagonal-ddd` com funcionalidade `api` permite as skills Remy que prescrevem DDD para APIs; não se impõe DDD ou backend a uma interface.
- `stack.go_module`: obrigatório para Go; origem de módulo fornecida pelo usuário, sem endereço GitHub inventado.
- `requirements.features`: tags explícitas da política em `config.py`, por exemplo `api`, `ui`, `testing`, `security-review`, `gradle`, `networking`. Texto livre em `description` e `constraints` é preservado sem inferir tecnologias ou funcionalidades.
- `skills`: opcional. Ausência usa seleção automática determinística pelas declarações. Uma lista fornece raízes explícitas; lista vazia desabilita a seleção. Seleção explícita nunca ignora compatibilidade ou dependências.
- `runtime_versions`: restrições opcionais por plugin (`python`, `nodejs`, `golang`, `java`, `rust`). Precisam coincidir com a configuração global e ser exigidas pelo projeto/executor/helpers. Não selecionam outra versão ou instalam nada.

Chaves desconhecidas, duplicadas, tipos incorretos, configurações especiais/links/FIFO e JSON acima de 1 MB são recusados antes de escrever no projeto. Arquivos de configuração são somente lidos.

## Responsabilidades e arquivos

| Arquivo | Responsabilidade |
|---|---|
| `project-bootstrap` | Iniciar com Python global asdf sem depender do cwd |
| `bootstrap.py` | CLI JSON `plan`/`apply` |
| `stacknauta_core/config.py` | Contrato e normalização das escolhas explícitas |
| `stacknauta_core/runtimes.py` | Configuração global, instalação física, executáveis e probes de versão |
| `stacknauta_core/compatibility.py` | Política explícita para as 101 skills aprovadas; padrão fechado |
| `stacknauta_core/library.py` | Reutilizar planos da biblioteca 1.5 e conferir hashes/proveniência |
| `stacknauta_core/core.py` | Esqueleto, plano determinístico, identidade e coordenação |
| `stacknauta_core/filesystem.py` | Inspeção, publicação exclusiva e retomada segura com dirfd |
| `STATUS.json` | Núcleo 2A implementado; integração e produção ainda falsas |

No consumidor são preparados README, AGENTS genérico, `.gitignore`, requisitos, diretórios de fonte/testes, `.tool-versions` e metadados em `.stacknauta/`. Python recebe metadados PEP 621; Node recebe package.json; TypeScript recebe tsconfig mínimo; Go recebe go.mod; Rust recebe Cargo.toml e arquivo de biblioteca vazio. A versão 0.0.0 é apenas marcador inicial. Não há build backend Python, bundler, compilador TypeScript, edição Rust, build tool/DSL JVM ou versões de plugins escolhidos automaticamente. JVM recebe um plano de build e diretórios vazios; wrappers/SDKs/configuração específica ficam para o agente após escolhas explícitas.

O Python cuida das operações de arquivo e validação. `.stacknauta/agent-plan.json` registra tarefas tecnológicas ainda não executadas, inclusive versões ausentes, revisão de geradores e pré-requisitos de SDKs/serviços. Ele não autoriza executar comandos. Não há código de negócio, servidor FastAPI, páginas Next, serviços, virtualenv, node_modules ou repositório Git criado pelo núcleo.

## asdf e estabilidade

O núcleo lê literalmente `$HOME/.tool-versions` e exige uma única versão explícita por runtime obrigatório. Recusa system, path/ref, fallback em lista e configurações ausentes. Consulta `asdf where <plugin> <versão>` e `asdf which <executável>` com a versão global forçada e cwd HOME. O relatório declara que overrides locais/ambiente foram ignorados explicitamente. Nunca assume que `python`, `node`, `java` ou outro binário encontrado no PATH é o runtime correto.

Executáveis precisam pertencer à instalação gerenciada e responder aos probes de versão. Python atual precisa ser o executor global verificado; JVM precisa ter java/javac consistentes. Variáveis de autoload/wrappers são isoladas. Probes Go usam `GOTOOLCHAIN=local`; Rust usa `RUSTUP_AUTO_INSTALL=0`, sem instalar toolchains. Kotlin utiliza o runtime JVM Java; compilador/plugin Kotlin e TypeScript são decisões de dependências posteriores, não runtimes do sistema usados como fallback.

Versões e funções (`application`, `executor`, `skill-helper`) são registradas. Python executor também entra em `.tool-versions`. Caminhos absolutos de instalação e informações do PATH aparecem apenas no diagnóstico do dry-run, nunca na identidade dos arquivos. O manifesto não contém timestamp variável; repetir o mesmo estado preserva bytes, inode e mtime, mesmo com mudanças de PATH que não alterem os pré-requisitos reais.

## Seleção e cópia de skills

Somente o catálogo/pacotes versionados são consumidos; nenhum acesso a `_repos/` ou atualização GitHub. A seleção verifica a compatibilidade de **todo** o fechamento. Skills pendentes, excluídas, desconhecidas, arquiteturas não declaradas, requisitos incompatíveis ou workflows cuja autenticação ainda exige agente não são incluídos.

Em seleção automática, um fechamento incompatível é omitido com motivo em `skills.skipped`; em seleção explícita, é erro antes de criar arquivos. Funcionalidades sem skill adequada continuam registradas como requisitos, sem substituir tecnologias ou desenvolver a aplicação.

Casos conservadores da biblioteca 1.5:

- Expo tem fechamento de 23 skills via router. Um pedido simples Expo não autoriza implicitamente deploy, OTA, App Clip e demais funcionalidades: esse fechamento é omitido se as tags faltarem. Uma seleção explícita incompleta é bloqueada. A biblioteca não foi refeita para relaxar esse contrato.
- security-review Sentry exige companheiras Django e GitHub Actions. Não é copiada para FastAPI ou outro projeto incompatível só por pedir revisão de segurança.
- Referências Kotlin podem puxar Compose/Gradle/testes; o conjunto só é incluído se esses pré-requisitos estiverem declarados.
- Skills de PR autenticado ficam para validação do agente na 2B; não se consulta autenticação ou serviços nesta etapa.

As cópias são byte a byte, com recursos comuns e licenças, em `.agents/skills/<categoria-origem>/skills/<nome>/`. O namespace preserva caminhos relativos e evita colisão de licenças ou alterações nas skills aprovadas. `.agents/skills/README.md` indexa os SKILL.md reais; `.stacknauta/skills-lock.json` registra seleção, versões, commits, hashes e origens por arquivo. Não há SKILL.md fictício, symlink, hardlink para a biblioteca ou cache necessário. Descoberta desse layout por cada agente será testada na 2B; não há adapter específico nesta etapa.

## Segurança, reexecução e falhas

O destino precisa ser novo/vazio ou conter exatamente o manifesto esperado. Uma árvore estrangeira não é adotada. A instalação StackNauta e a árvore legada irmã são áreas protegidas. Caminhos de destino/componentes são abertos por descritores de diretório POSIX com `O_NOFOLLOW`; arquivos especiais, symlinks e hardlinks preexistentes são recusados.

O manifesto imutável `.stacknauta/manifest.json` é a reserva do conjunto esperado. Publicação usa temporário exclusivo, fsync e link atômico interno sem sobrescrita; o temporário próprio é removido e o resultado tem nlink=1. Não existe rename/replace sobre um arquivo existente. Diretórios e arquivos de terceiros não são removidos ou substituídos. Estado final é verificado antes do sucesso.

Em falha após a reserva, os arquivos completos já publicados permanecem. A reexecução do mesmo plano completa apenas arquivos ausentes, preservando os existentes. Conteúdo diferente, manifesto alterado ou links perigosos bloqueiam a operação para revisão manual. Arquivos extras do usuário são preservados. Mudanças de stack, requisitos ou versões não são tratadas como atualização/migração de projeto existente.

Limites: implementação POSIX/Fedora; não certifica Windows, filesystems sem publicação por link atômico, ataques de processos com controle do mesmo usuário renomeando ancestrais continuamente, nem recuperação automática de SIGKILL antes da primeira reserva se restarem temporários sem proprietário demonstrável. Nesses estados ambíguos, preserva arquivos e para. Não há rollback destrutivo, exclusão recursiva ou limpeza automática de evidências.

## Exemplos e testes

```bash
./Automacao/project-bootstrap/project-bootstrap plan --config Automacao/project-bootstrap/examples/python-fastapi.json
./Automacao/project-bootstrap/project-bootstrap plan --config Automacao/project-bootstrap/examples/typescript-nextjs.json
./Automacao/project-bootstrap/project-bootstrap plan --config Automacao/project-bootstrap/examples/go-api.json
asdf exec python -I -B Automacao/validacao-project-bootstrap/executar_testes.py
asdf exec python -B Skills/validacao/validar_catalogo.py
```

Go será bloqueado se não houver versão global instalada; o comando não instala runtime nem cria destino nesse caso. Python/Node foram testados com runtimes reais já instalados; Go/JVM/Rust têm testes de resolução e esqueleto com runtimes sintéticos não executados. Todos os projetos de teste ficam em diretórios temporários novos.

Resultados e limites estão em `../validacao-project-bootstrap/resultado.json`, `biblioteca.json`, `clone-local.json` e `preservacao.json`. A Etapa 2B deverá verificar descoberta/uso das skills nos agentes e as operações específicas de cada stack antes de qualquer alegação de uso em produção.
