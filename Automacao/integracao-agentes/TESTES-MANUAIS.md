# Testes posteriores — não executados nesta etapa

O fluxo Gemini suportado é Antigravity CLI (`agy`), com a mesma entrada AGENTS.md
usada por Codex CLI e OpenCode. O roteiro atual substitui o cliente convencional;
as versões anteriores permanecem no histórico Git. O reteste comportamental 2G
foi confirmado pelo usuário. As verificações desta 2H não iniciam outros agentes.

Abra os agentes diretamente em seus ambientes habituais. Não é necessário mudar
configurações globais ou instalar nada pelo StackNauta. Use somente um modelo
DeepSeek já disponível no OpenCode. Se faltar CLI, modelo, autenticação, runtime
global asdf ou permissão, registre o bloqueio; não substitua silenciosamente.

## OpenCode com DeepSeek

1. Abra o OpenCode na raiz do StackNauta, selecione seu DeepSeek e peça:
   “Use @project-bootstrap para planejar api-teste com Python e FastAPI,
   funcionalidade API, em um diretório temporário novo. Não escolher arquitetura
   ou versões de framework. Não instalar, executar geradores ou serviços.”
   Confirme o carregamento real da skill e a execução de `agent-plan`.
2. Revise destino, runtimes, skills, arquivos e hashes. Autorize exatamente esse
   plano; confira `agent-apply` e `agent-verify`, sem código de negócio.
3. Abra sessão no consumidor e ative `@stacknauta-fastapi`. Confirme a leitura do
   original e de `references/dependencies.md` no diretório original. Reaplique o
   mesmo hash e confirme ausência de alterações. Registre versão do agente,
   modelo DeepSeek, comandos e resultados; erros permanecem pendências.

## Gemini via Antigravity CLI (`agy`)

1. Em uma validação manual autorizada, abra o Antigravity CLI na raiz StackNauta,
   selecione Gemini e respeite a confiança do workspace e as permissões nativas.
   Confira AGENTS.md e a skill `project-bootstrap` em `/skills`. Faça o pedido
   acima e confirme a leitura da skill e a execução real de `agent-plan`.
2. Revise e autorize o plano concreto; confira aplicação e verificação usando os
   mesmos comandos Python, sem versões ou arquitetura escolhidas pelo agente.
3. Abra uma nova sessão na raiz do consumidor; confira AGENTS.md, o catálogo em
   `/skills` e a leitura de `.stacknauta/AGENT-INTEGRATION.md`. Verifique a seleção
   contextual, leitura do encaminhador, SKILL.md original e recursos pertinentes.
   Reexecute o mesmo plano e registre evidências. A presença de arquivos e hashes
   não comprova ativação. Nenhum import de contexto é necessário.

## Codex — confirmação posterior em nova sessão

A etapa atual usa o Codex já ativo e o renderizador nativo de descoberta, sem
iniciar outra conversa com modelo. Para confirmar ativação automática posterior,
abra uma sessão no StackNauta e invoque `$project-bootstrap` com o pedido acima;
confira a skill carregada e a chamada do launcher. No consumidor, faça o mesmo
com `$stacknauta-fastapi`. Esse teste permanece separado da inspeção de catálogo.
