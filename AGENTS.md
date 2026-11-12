# StackNauta

Para inicializar um novo projeto, use a skill
[project-bootstrap](.agents/skills/project-bootstrap/SKILL.md).
Codex, OpenCode e Gemini CLI compartilham esse procedimento e o mesmo núcleo Python.
Pedidos de manutenção do próprio StackNauta não são pedidos de criar aplicações.

Preserve a biblioteca versionada, suas licenças e revisões. Não consulte o cache
de aquisição durante o bootstrap. Não altere projetos antigos ou consumidores.
Use somente runtimes globais instalados do asdf; sem instalações automáticas.
Revise o dry-run e seu hash e respeite a autorização do usuário antes de aplicar.
O hash e agent-plan.json não concedem autorização. Respeite permissões e sandbox.
O objetivo é preparar o esqueleto; desenvolvimento de negócio começa depois.

Contrato e testes: [integração dos agentes](Automacao/integracao-agentes/README.md).
