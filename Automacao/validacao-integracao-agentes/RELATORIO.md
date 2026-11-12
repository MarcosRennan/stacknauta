# Etapa 2B — integração compartilhada, validação pelo Codex atual

Implementada uma skill `project-bootstrap` e uma camada aditiva de descoberta,
usando exclusivamente o Bootstrap 2A. A biblioteca permanece com as mesmas 101
skills aprovadas, 21 pendentes, duas excluídas e nove pacotes; não foi regenerada.
Não há instalação de runtimes/ferramentas, geradores, negócio ou publicação remota.

## Implementação

- `.agents/skills/project-bootstrap/SKILL.md`: procedimento único de interpretação,
  validação, dry-run, revisão/autorização, aplicação e operações pendentes.
- `AGENTS.md` e `GEMINI.md`: contexto mínimo; GEMINI importa o mesmo AGENTS.
- `Automacao/project-bootstrap/stacknauta_core/integration.py`: entradas rasas
  `stacknauta-*`, contexto do consumidor, manifesto adicional e verificação.
- `Automacao/project-bootstrap/bootstrap.py`: somente despacho da CLI para
  `agent-plan`, `agent-apply`, `agent-verify`. Comandos originais preservados.
- `Skills/validacao/validar_biblioteca.py`: substitui a exigência de pasta vazia
  pela conferência da skill real e dos artefatos da integração, mantendo suporte
  ao estado original 2A. Os pacotes e suas receitas não foram alterados.
- `Automacao/integracao-agentes/`: contrato, exemplos e testes manuais posteriores.
- `Automacao/validacao-integracao-agentes/`: suíte, teste de clone e evidências JSON.
- `README.md`: estado atual, comandos e links. `.agents/skills/.gitkeep` removido
  porque a pasta agora tem conteúdo real.

O plano da integração inclui o hash original 2A e os hashes dos arquivos novos.
A aplicação exige o hash revisado da integração e delega ao núcleo com seu hash
original. Hash não concede autorização. A conversa/permissões do agente continuam
responsáveis pela autorização; nos testes, ela foi concedida para temporários.

Os SKILL.md originais e recursos são copiados fisicamente pelo núcleo e mantidos
byte a byte. Os aliases não duplicam recursos: instruem a leitura integral do
original e a resolução de referências em seu diretório. GEMINI.md importa o
AGENTS.md original e o contexto adicional, sem mudar arquivos geridos pelo núcleo.
Conflitos bloqueiam; reexecução completa somente ausências. `agent-verify` confere
o estado inicial; alterações de desenvolvimento posteriores exigem verificações
próprias, não atualização silenciosa dos manifestos.

## Evidências e resultados

| Verificação | Resultado |
|---|---|
| Suíte original 2A | 65 testes passaram |
| Suíte 2B | 16 testes passaram, sem skips |
| Biblioteca | 958 arquivos conferidos, 101 planos de cópia física aprovados, sete JS parseados, zero erros |
| Aliases | Metadados/nomes e caminhos rasos conferidos para as 101 aprovadas, sem selecioná-las indiscriminadamente |
| Codex atual — Python/FastAPI | Plan/apply/verify, 25 arquivos do núcleo e quatro de integração |
| Codex atual — TypeScript/Next.js | Plan/apply/verify, 92 arquivos do núcleo e quatro de integração |
| Runtime real ausente | Java global ausente bloqueou antes de criar destino |
| Permissão real insuficiente | Pai temporário sem escrita bloqueou; permissão restaurada apenas nesse fixture |
| Hash incorreto | Bloqueio sem alterar arquivos |
| Idempotência | Bytes, inode e mtime preservados nas duas stacks |
| Falha parcial e links perigosos | Suíte 2B cobre retomada, symlink, hardlink e conflitos; testes anteriores preservados |
| Clone local limpo sem cache | Pendente de execução no commit candidato; será registrado em clone-local.json |

Evidências detalhadas: [automatizados.json](automatizados.json),
[nucleo-original.json](nucleo-original.json), [biblioteca.json](biblioteca.json),
[codex-fluxo.json](codex-fluxo.json) e [preservacao.json](preservacao.json).

Os algoritmos, launcher, exemplos e estado histórico 2A estão preservados por
hash; somente a interface CLI recebe os novos despachos. Os 4.259 registros de
metadados de App-Web foram confrontados com o pré-check sem mudança. Nenhum
consumidor anterior foi usado como destino. Não há remoto no Git principal.

## Descoberta versus utilização

Codex CLI 0.167.2: o comando nativo `codex debug prompt-input` renderizou
`project-bootstrap` no catálogo da raiz e os aliases `stacknauta-fastapi` e
`stacknauta-ui-ux-pro-max` nos respectivos consumidores temporários. O relatório
registra a linha nativa e hash do render completo; contextos pessoais completos
ficam fora do Git. A execução precisou de acesso ao estado pessoal do Codex,
autorizado pelo mecanismo de permissões; não houve alteração de configuração.

O Codex já ativo leu explicitamente a skill, seguiu o procedimento com os hashes
revisados, verificou os consumidores e leu a skill FastAPI copiada, seu contrato e
um recurso relativo real (`references/dependencies.md`). Essa utilização é real,
mas não equivale à ativação automática pelo catálogo de uma nova sessão.

Nenhuma nova conversa com modelo foi iniciada. **Ativação automática em nova
sessão permanece pendente**, conforme a instrução do usuário. Não se declara
compatibilidade integral a partir de inspeção estática ou renderização do prompt.

Os agent-plan.json foram interpretados: versões FastAPI/Next.js e compilador
TypeScript permanecem pendentes, sem arquitetura escolhida. Nenhuma operação
tecnológica adicional estava autorizada nesses fixtures, portanto não foi feita.

## Outros agentes e próximos testes

OpenCode/DeepSeek e Gemini CLI estão preparados estaticamente, **não testados nem
aprovados**. Após a correção de escopo, nenhum dos dois foi invocado ou teve suas
configurações/autenticação/modelos consultados. Inspeções da execução interrompida
não constituem aprovação nem fazem parte da evidência funcional desta entrega.

O roteiro curto está em
[TESTES-MANUAIS.md](../integracao-agentes/TESTES-MANUAIS.md): abrir cada agente na
raiz, confirmar a skill carregada, solicitar uma API temporária, revisar e
autorizar o hash, verificar arquivos e depois ativar a skill copiada no consumidor.
No OpenCode usar DeepSeek explicitamente; no Gemini respeitar confiança e
consentimento nativos. Registrar falhas sem contornar permissões.

Esta etapa comprova o fluxo do Codex atual e a integridade da camada comum;
confirmação em nova sessão e os dois outros agentes continuam separados. Não há
certificação de produção nem integração prática com SDKs, hardware ou serviços.

## Reexecução

Com Python global asdf válido, na raiz StackNauta:

```sh
asdf exec python -I -B Automacao/validacao-integracao-agentes/executar_testes.py
asdf exec python -I -B Automacao/validacao-project-bootstrap/executar_testes.py
asdf exec python -I -B Skills/validacao/validar_biblioteca.py --copias --sintaxe-node
# Exige árvore limpa e commit candidato; não inicia agentes ou modelos:
asdf exec python -I -B Automacao/validacao-integracao-agentes/testar_clone.py
```

O commit candidato conterá implementação e evidências atuais; um commit posterior
de evidência registrará o clone, com o hash exato do candidato testado. Temporários
e contextos de diagnóstico são preservados, sem exclusões recursivas.
