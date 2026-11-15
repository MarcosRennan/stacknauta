# Testes posteriores — não executados nesta etapa

Atualização 2G: o fluxo Gemini suportado é Antigravity CLI (`agy`). Abra o novo
consumidor como workspace, confira `AGENTS.md` e `/skills`, e observe a leitura
explícita de `.stacknauta/AGENT-INTEGRATION.md` e dos originais pertinentes.
O consumidor não recebe GEMINI.md. O roteiro Gemini CLI convencional abaixo é
histórico, preservado para avaliação na 2H; não deve orientar o reteste 2G.
O prompt definitivo e as evidências da 2G ficam em
`../../.stacknauta-updates/padronizacao-agents-2g/` (artefatos locais ignorados).

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

## Gemini CLI

1. Abra o Gemini CLI na raiz StackNauta. Respeite a confiança de workspace
   (`/trust`, se necessário) e use `/skills list` ou `/skills reload`. Confirme
   `project-bootstrap`. Faça o pedido acima usando o nome simples da skill e
   confira `activate_skill`, com consentimento nativo, e `agent-plan` real.
2. Revise e autorize o plano concreto; confira aplicação e verificação usando os
   mesmos comandos Python, sem versões ou arquitetura escolhidas pelo agente.
3. Abra sessão no consumidor; confira importação de GEMINI.md, `/skills list` e
   ativação de `stacknauta-fastapi`. Leia original/recurso relativo, reexecute o
   mesmo plano e registre evidências. Não considerar a presença dos arquivos
   como prova de ativação.

## Codex — confirmação posterior em nova sessão

A etapa atual usa o Codex já ativo e o renderizador nativo de descoberta, sem
iniciar outra conversa com modelo. Para confirmar ativação automática posterior,
abra uma sessão no StackNauta e invoque `$project-bootstrap` com o pedido acima;
confira a skill carregada e a chamada do launcher. No consumidor, faça o mesmo
com `$stacknauta-fastapi`. Esse teste permanece separado da inspeção de catálogo.
