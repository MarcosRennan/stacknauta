# Pendências e exclusões — Etapa 1.5

Aprovação de empacotamento não ativa skills. Todas as entradas mantêm origem e revisão no catálogo.

## 21 pendentes

| Skill | Categoria | Justificativa |
|---|---|---|
| `ui-ux-pro-max:design-system` | Frontend | A revisão cita biblioteca assets/css/slide-animations.css e exemplo de slides não fornecidos; necessário esclarecer o contrato completo de slides. |
| `ui-ux-pro-max:design` | Frontend | Orquestrador inclui os fluxos design-system e slides ainda pendentes, além de provedores de imagem; a distribuição integral não está fechada. |
| `ui-ux-pro-max:slides` | Frontend | Depende do fluxo de design-system/slides com biblioteca de animação ausente na origem; não fabricar recurso. |
| `chrisbanes:deliver-spec` | Mobile | Contrato de orquestração com run-github-project e capacidades de revisão/delegação específicas dos agentes ainda precisa ser integrado. |
| `chrisbanes:implement-with-subagents` | Mobile | Modo de implementação exige a skill externa tdd (Matt Pocock), fora das sete fontes. |
| `chrisbanes:run-github-project` | Mobile | Modos triage/Wayfinder/research dependem de provedores externos não adquiridos; pacote completo de orquestração não fechado. |
| `chrisbanes:subagent-delegation` | Mobile | Playbooks por runtime e implementação com providers externos requerem adaptação aos agentes planejados. |
| `chrisbanes:to-plan` | Mobile | Planejamento integrado a orquestração/provedores externos ainda pendentes; não disponibilizar um fluxo parcial como completo. |
| `chrisbanes:using-chrisbanes-skills` | Mobile | Router da coleção encaminha a rotinas de orquestração ainda pendentes; skills Kotlin/Compose podem ser selecionadas diretamente. |
| `android:r8-analyzer` | Mobile | Helper obrigatório exige protobuf>=6.33.4, ausente no Python global. Não instalar nem apresentar execução do analisador como pronta. |
| `sentry:blog-writing-guide` | Frontend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:brand-guidelines` | Frontend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:browse-local-sentry` | Backend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:claude-settings-audit` | Seguranca | Gera permissões settings.json específicas de Claude Code, fora dos três agentes planejados; exige adaptação específica. |
| `sentry:document-api-endpoint` | Backend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:presentation-creator` | Frontend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:skill-scanner` | Seguranca | Script obrigatório depende de PyYAML e usa uv; PyYAML não está instalado no Python global. Não instalar dependência automaticamente. |
| `sentry:skill-writer` | Backend | Validação obrigatória depende de PyYAML, ausente no Python global; exige decisão posterior sobre dependência e escopo de autoria. |
| `sentry:sred-project-organizer` | Backend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:sred-work-summary` | Backend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |
| `sentry:triage-frontend-issues` | Frontend | Fluxo específico da organização Sentry (marca, repositório, serviços ou acesso interno); faltam contexto e adaptação para distribuição genérica. Não autenticar serviços nesta etapa. |

## 2 excluídas

| Skill | Categoria | Justificativa |
|---|---|---|
| `expo:expo-skill-eval` | Mobile | Ferramenta interna de avaliação do fornecedor; depende de eval-harness não adquirido e executa geradores/avaliações. Excluída da distribuição. |
| `expo:expo-migrate-module` | Mobile | Plugin expo-experiments, explicitamente experimental. Excluído desta distribuição estável, sem habilitação automática. |
