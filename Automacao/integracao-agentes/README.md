# Integração com agentes — Etapa 2B

Atualização 2G: `AGENTS.md` é a base compartilhada de Codex, OpenCode e
Gemini executado no Antigravity CLI (`agy`). Novos consumidores não recebem
`GEMINI.md`. O núcleo instrui a leitura explícita do contrato complementar
`.stacknauta/AGENT-INTEGRATION.md`, quando presente, antes de usar descoberta
de skills ou realizar configuração tecnológica. Um caminho Markdown não comprova
carregamento automático. Requisitos e decisões aprovadas prevalecem sobre sugestões
das skills. Seleção explícita, cópias físicas, recursos e aliases são preservados.

Atualização 2H: o procedimento da skill de bootstrap e o roteiro operacional
utilizam Gemini via Antigravity CLI (`agy`), sem imports de contexto específicos
do cliente convencional. O reteste comportamental 2G foi confirmado pelo usuário;
as verificações automatizadas continuam distinguindo estrutura de ativação nativa.
Não há migração automática de consumidores antigos: os manifestos recompostos
incluem os templates originais; use a revisão do gerador que criou o consumidor
para verificar/reaplicar planos anteriores. Não substitua hashes históricos.

Atualização 2D: [ciclo de vida](../project-bootstrap/CICLO-DE-VIDA.md) distingue
conteúdo protegido, evolutivo, sementes de desenvolvimento e adicionais.
`agent-verify` agora relata evolução permitida, mantendo status verified;
verification_state e lifecycle detalham alterações/remoções. A classificação
evolutiva de GEMINI.md permanece apenas para contratos históricos; novos planos
não o emitem. Os manifestos e aliases permanecem protegidos.
Os relatórios históricos 2B descrevem o contrato anterior de igualdade total.

O procedimento está em `../../.agents/skills/project-bootstrap/SKILL.md`.
O launcher `../project-bootstrap/project-bootstrap` continua resolvendo o Python
global do asdf. `stacknauta_core/integration.py` delega ao Bootstrap 2A; não há
implementações de bootstrap específicas de agente. Os comandos originais `plan`
e `apply` continuam disponíveis e com o mesmo contrato.

## Interface

Execute a partir da raiz StackNauta; a configuração fica fora do destino:

```sh
Automacao/project-bootstrap/project-bootstrap agent-plan --config /tmp/pedido.json
# Revisar files + integration_files, core_plan_id e plan_id; obter autorização aplicável.
Automacao/project-bootstrap/project-bootstrap agent-apply --config /tmp/pedido.json --plan-id HASH_REVISADO
Automacao/project-bootstrap/project-bootstrap agent-verify --config /tmp/pedido.json
```

`agent-plan` é somente leitura. O hash da integração inclui o hash do plano 2A,
as entradas de descoberta e todos os arquivos adicionais. O hash original 2A
continua verificando esqueleto, runtimes, seleção e recursos. `agent-apply`
recalcula e confere ambos antes da criação. Hash não é autorização: essa decisão
pertence à conversa e às permissões do ambiente, como no núcleo original.

As tarefas tecnológicas em `.stacknauta/agent-plan.json` exigem análise e
autorização próprias. O código não executa geradores, dependências ou serviços.
`agent-verify` verifica hashes protegidos e estrutura física e relata evolução;
não certifica sintaxe, semântica, testes ou dependências da aplicação.

## Descoberta comum

No StackNauta há uma skill real `project-bootstrap` em `.agents/skills/`.
`AGENTS.md` encaminha para ela. Os três ambientes usam essa entrada compartilhada.
Não há configuração nova do OpenCode, provedor ou usuário.

No consumidor, o núcleo preserva o layout aprovado dos pacotes. A integração
acrescenta um SKILL.md por skill selecionada em
`.agents/skills/stacknauta-<nome>/`, sem copiar novamente seus recursos. A entrada
exige a leitura integral do original e o uso do diretório original como base.
Isso mantém licenças, scripts, dados e referências aprovados. Não há symlinks,
acesso ao cache ou caminhos pessoais nos arquivos distribuíveis. As entradas e
hashes são registrados em `.stacknauta/agent-integration.json`.

Os aliases têm nomes distintos dos originais. Codex/OpenCode podem listar também
os originais aninhados; isso não significa recursos duplicados nem nova seleção.
O Antigravity descobre o nível raso e o AGENTS.md diretamente, sem imports.
O contrato complementar permanece consultável e protegido. Um GEMINI.md do usuário
não é gerado, gerenciado nem sobrescrito pela integração nova. Conflitos em arquivos
gerenciados bloqueiam antes da criação. O
verificador usa as mesmas operações POSIX com dirfd/no-follow do núcleo. Não há
rollback destrutivo: uma interrupção deixa arquivos íntegros; reaplicar o mesmo
plano autorizado completa ausências e preserva conflitos para revisão manual.

Fontes oficiais consultadas durante a etapa:

- [Codex: instalação manual de skills](https://developers.openai.com/api/reference/cli)
- [OpenCode: descoberta, IDs e permissões](https://opencode.ai/docs/skills/)
- [Antigravity: regras compartilhadas e includes](https://antigravity.google/docs/rules)
- [Antigravity: skills no CLI](https://antigravity.google/docs/skills)
- [Antigravity: descoberta e precedência](https://antigravity.google/docs/customization-discovery)

## Primeiro prompt

Python/FastAPI, mantendo versão de framework pendente:

> Use project-bootstrap para preparar api-estudo em $HOME/Projetos/api-estudo.
> Linguagem Python; framework FastAPI; funcionalidade API; arquitetura hexagonal-ddd.
> Não instalar dependências, executar geradores ou serviços. Mostre o dry-run,
> hashes e pendências. Aplicação ainda não autorizada.

TypeScript/Next.js, arquitetura omitida:

> Prepare web-estudo usando project-bootstrap. Destino $HOME/Projetos/web-estudo;
> TypeScript, Next.js, interface e acessibilidade. Não escolha arquitetura ou
> versões de frameworks. Apresente o plano para autorização, sem iniciar negócio.

O agente deve converter apenas as escolhas declaradas para o JSON suportado.
Framework sem versão fica pendente para operações tecnológicas. Feature/stack
não suportada exige esclarecimento, nunca substituição silenciosa.

## Validação manual por agente

Use clone local limpo sem o cache e destinos temporários novos com pai existente.
Consulte os resultados reais em `../validacao-integracao-agentes/RELATORIO.md`;
esta lista é um roteiro, não evidência de aprovação.

1. Abra sessão no clone e confirme `project-bootstrap` na lista nativa.
   No Codex, invoque `$project-bootstrap`; no OpenCode, `@project-bootstrap`;
   no Gemini/Antigravity, `/skills`, depois peça a preparação e confirme leitura
   real. Respeite confiança do workspace e permissões nativas.
2. Use um prompt acima com destino temporário; confira invocação real do launcher
   e ausência do destino após dry-run. Revise os dois hashes e ambas as listas.
3. Autorize esse plano concreto e execute a aplicação. Confira agent-verify,
   cópias físicas, locks, `.tool-versions` e ausência de instalação/negócio.
4. Abra nova sessão no consumidor. Liste e ative um alias `stacknauta-*`, leia o
   original indicado e um recurso relativo real. Antigravity: `/skills`;
   aceite somente consentimento pertinente. Confira o caminho
   e conteúdo reais, não apenas a descrição retornada pelo modelo.
5. Reaplique o mesmo hash e confira arquivos inalterados. Hash incorreto, runtime
   global ausente, destino sem permissão e symlink perigoso devem bloquear.
   Não aumente permissões automaticamente para ocultar um bloqueio esperado.
6. OpenCode deve usar um modelo DeepSeek autenticado explicitamente selecionado
   com `--model provedor/modelo`. Outro provedor/modelo não comprova esse requisito.
   Ausência de CLI, modelo, autenticação, rede ou permissão permanece pendência.
