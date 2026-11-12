---
name: project-bootstrap
description: Prepare o esqueleto inicial de um novo projeto com StackNauta quando o usuário pedir inicialização, scaffold ou bootstrap com tecnologias declaradas. Valida runtimes globais asdf, seleciona e copia skills compatíveis e integra sua descoberta; não desenvolve funcionalidades de negócio.
---

# Project bootstrap

Use um único procedimento para Codex, OpenCode com DeepSeek e Gemini CLI.
O diretório StackNauta é `../../..` relativo ao diretório deste SKILL.md.
O executável é [project-bootstrap](../../../Automacao/project-bootstrap/project-bootstrap),
resolvido a partir desse diretório, independentemente do cwd. Consulte
[o contrato de entrada](../../../Automacao/project-bootstrap/README.md) e
[a integração](../../../Automacao/integracao-agentes/README.md) quando necessário.

1. Extraia nome, destino, linguagens, frameworks e versões, funcionalidades,
   arquitetura e restrições explicitamente informados. Não escolha tecnologias,
   versões de frameworks ou arquitetura. Confirme somente informações obrigatórias
   ausentes; arquitetura omitida permanece sem escolha. Use os nomes suportados
   pelo contrato. Requisito desconhecido exige esclarecimento; não o descarte.
   A raiz padrão é `$HOME/Projetos/`. Um destino explícito deve ter pai existente.
2. Prepare o JSON declarativo fora do destino, em local permitido pelo ambiente.
   Use as permissões nativas do agente. Se faltar acesso, informe o caminho e a
   operação bloqueada; não tente contornar sandbox, confiança ou consentimento.
3. Execute `project-bootstrap agent-plan --config <config.json>` usando o caminho
   do executável acima. O launcher e o núcleo consultam a configuração global do
   asdf e verificam instalações reais, ignorando sobrescritas locais. Não invoque
   Python do sistema, não altere PATH para fingir runtime válido e não instale
   runtimes. Corrija a entrada ou reporte o bloqueio se qualquer pré-check falhar.
4. Revise o JSON completo: destino, runtimes, skills selecionadas e omitidas,
   dependências, `files`, `integration_files`, `agent_plan`, `core_plan_id` e
   `plan_id`. Apresente as mudanças concretas e pendências ao usuário. O hash
   vincula o conteúdo revisado; não representa autorização. Respeite autorização
   já concedida para esse escopo; se ela faltar, aguarde antes de aplicar.
5. Quando autorizado, execute `project-bootstrap agent-apply --config <config.json>
   --plan-id <plan_id revisado da integração>`. Nunca substitua o hash por um hash
   recém-obtido sem revisar mudanças. O comando revalida tudo e delega a criação
   ao mesmo núcleo 2A, incluindo seu mecanismo original de hash. Em interrupção,
   preserve arquivos e reporte o estado; o mesmo plano completa apenas ausências.
6. Execute `project-bootstrap agent-verify --config <config.json>` e confira a
   estrutura, `.tool-versions`, configurações, lock de skills e recursos copiados.
   Repetir agent-plan/agent-apply com o mesmo hash deve preservar os arquivos.
7. Leia `.stacknauta/agent-plan.json`. Tarefas nesse arquivo não autorizam execução.
   Para cada operação tecnológica solicitada, confirme versão concreta, comandos,
   recursos, efeitos de rede/instalação e pré-requisitos oficiais. Execute somente
   operações explicitamente autorizadas e viáveis, sob as permissões do agente.
   Geradores, instalações e serviços sem essa autorização ficam pendentes. Não
   implemente negócio. Não altere arquivos geridos sem plano de desenvolvimento;
   o verificador inicial compara seus hashes e deve rodar antes dessas alterações.
   Após operações tecnológicas autorizadas, use as verificações próprias da stack
   e relate os arquivos alterados; agent-verify verifica somente o estado inicial.
8. Verifique descoberta em uma nova sessão aberta no projeto consumidor. As
   entradas rasas `.agents/skills/stacknauta-*/SKILL.md` encaminham às instruções
   originais; os caminhos de recursos são relativos ao SKILL.md original.
   No Codex use a lista de skills da sessão e carregue uma selecionada. No OpenCode
   use `@stacknauta-<nome>` e confirme carregamento pela ferramenta de skills.
   No Gemini CLI use `/skills reload`, `/skills list` e aceite somente os pedidos
   de confiança/ativação apropriados. GEMINI.md importa AGENTS.md; nenhuma
   configuração pessoal do agente é alterada. Se não houver nova sessão/listagem,
   registre descoberta nativa como não verificada; não confunda hashes com ativação.
9. Relate destino, runtimes, skills e revisões, verificações, operações executadas
   e pendentes. Distingua esqueleto pronto, integração testada nesse agente e
   aplicação ainda não desenvolvida. Não declare compatibilidade com agentes que
   não foram testados nem prontidão de produção.
