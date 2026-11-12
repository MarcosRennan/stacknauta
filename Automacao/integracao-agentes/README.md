# Integração com agentes — Etapa 2B

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
`agent-verify` verifica o estado inicial byte a byte, não o desenvolvimento futuro.

## Descoberta comum

No StackNauta há uma skill real `project-bootstrap` em `.agents/skills/`.
`AGENTS.md` encaminha para ela. `GEMINI.md` importa AGENTS.md pelo mecanismo
oficial do Gemini. Não há configuração nova do OpenCode, provedor ou usuário.

No consumidor, o núcleo preserva o layout aprovado dos pacotes. A integração
acrescenta um SKILL.md por skill selecionada em
`.agents/skills/stacknauta-<nome>/`, sem copiar novamente seus recursos. A entrada
exige a leitura integral do original e o uso do diretório original como base.
Isso mantém licenças, scripts, dados e referências aprovados. Não há symlinks,
acesso ao cache ou caminhos pessoais nos arquivos distribuíveis. As entradas e
hashes são registrados em `.stacknauta/agent-integration.json`.

Os aliases têm nomes distintos dos originais. Codex/OpenCode podem listar também
os originais aninhados; isso não significa recursos duplicados nem nova seleção.
Gemini precisa do nível raso. Um novo GEMINI.md importa o AGENTS.md original e
`.stacknauta/AGENT-INTEGRATION.md`. Nenhum arquivo gerido pelo núcleo 2A é alterado.
Conflitos preexistentes, inclusive GEMINI.md, bloqueiam antes da criação. O
verificador usa as mesmas operações POSIX com dirfd/no-follow do núcleo. Não há
rollback destrutivo: uma interrupção deixa arquivos íntegros; reaplicar o mesmo
plano autorizado completa ausências e preserva conflitos para revisão manual.

Fontes oficiais consultadas durante a etapa:

- [Codex: instalação manual de skills](https://developers.openai.com/api/reference/cli)
- [OpenCode: descoberta, IDs e permissões](https://opencode.ai/docs/skills/)
- [Gemini CLI: descoberta e ativação](https://geminicli.com/docs/cli/tutorials/skills-getting-started/)
- [Gemini CLI: importação de contexto](https://geminicli.com/docs/cli/gemini-md/)

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
   no Gemini, `/skills list`, depois peça a preparação e confirme `activate_skill`
   quando solicitado. Respeite confiança do workspace e permissões nativas.
2. Use um prompt acima com destino temporário; confira invocação real do launcher
   e ausência do destino após dry-run. Revise os dois hashes e ambas as listas.
3. Autorize esse plano concreto e execute a aplicação. Confira agent-verify,
   cópias físicas, locks, `.tool-versions` e ausência de instalação/negócio.
4. Abra nova sessão no consumidor. Liste e ative um alias `stacknauta-*`, leia o
   original indicado e um recurso relativo real. Gemini: `/skills reload` seguido
   de `/skills list`; aceite somente consentimento pertinente. Confira o caminho
   e conteúdo reais, não apenas a descrição retornada pelo modelo.
5. Reaplique o mesmo hash e confira arquivos inalterados. Hash incorreto, runtime
   global ausente, destino sem permissão e symlink perigoso devem bloquear.
   Não aumente permissões automaticamente para ocultar um bloqueio esperado.
6. OpenCode deve usar um modelo DeepSeek autenticado explicitamente selecionado
   com `--model provedor/modelo`. Outro provedor/modelo não comprova esse requisito.
   Ausência de CLI, modelo, autenticação, rede ou permissão permanece pendência.
