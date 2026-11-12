# Inclusão controlada — Etapa 3B

A inclusão usa a mesma CLI, Python global asdf, snapshot, hash, publicação e
recuperação da Etapa 3A. Não instala ferramentas nem executa código do fornecedor.
Nenhuma skill ou origem real foi incorporada na validação desta etapa.

## Descoberta sem incorporação

Com Git principal limpo e um commit local que preserve o estado atual:

```sh
./Automacao/manutencao-skills/skills add https://github.com/usuario/repositorio
./Automacao/manutencao-skills/skills add https://github.com/usuario/repositorio/tree/main/skills/exemplo
./Automacao/manutencao-skills/skills add git@github.com:usuario/repositorio.git --ref main --path skills/exemplo
```

Também aceita `ssh://git@github.com/usuario/repositorio.git` e links `blob` para
SKILL.md. `--ref` aceita branch, tag ou commit completo. Branches com barras são
resolvidas pelo maior prefixo remoto válido; ambiguidades branch/tag são recusadas.
`--path` é relativo à raiz Git e não aceita travessia ou caminhos reservados.
Pode usar `--source-id identificador` quando o ID gerado colidir.

URL canônica identifica a mesma origem entre HTTPS/SSH e diferenças de caixa;
não se duplica seu cadastro. Uma origem existente permanece no commit registrado:
se a revisão solicitada diferir, usar `update` em operação separada. Uma inspeção
não atualiza silenciosamente a biblioteca. Escopo de aquisição existente não é
reduzido; quando necessário, a descoberta amplia os caminhos de skills esparsos.

`add` retorna `session_id`, `review_id` e candidatas. Grava somente inspeção/cache
em `.stacknauta-updates/SESSION/inspection`, nunca no catálogo ou pacotes ativos.
Licenças ancestrais do subdiretório também são adquiridas. Fontes sem SKILL.md,
indisponíveis ou inseguras são bloqueadas com motivo. Escopo incompleto mantém
recursos ausentes como pendência; inspecionar a raiz do repositório quando necessário.

```sh
./Automacao/manutencao-skills/skills review
./Automacao/manutencao-skills/skills review SESSION
```

O primeiro lista catálogo e sessões de descoberta. O segundo apresenta nome, ID,
origem/commit, categoria proposta, descrição, recursos, scripts, licença,
dependências, conflitos, pendências e estado. `discovery_status` preserva o estado
original; `current_status` mostra a classificação atual no catálogo. A revisão não
executa as instruções das skills e não ativa agentes.

## Decisões individuais e dry-run

Criar um JSON **fora do candidato**. Exemplo para uma skill analisada que tenha
finalidade Python/FastAPI; adaptar às condições reais, sem inventar tecnologias:

```json
{
  "schema_version": 1,
  "skills": {
    "gh-usuario-repositorio:api-guidelines": {
      "status": "approved",
      "category": "Backend",
      "reason": "Recursos, licença e aplicabilidade analisados individualmente.",
      "compatibility": {
        "languages_any": ["python"],
        "frameworks_any": ["fastapi"],
        "frameworks_all": [],
        "features_all": ["api"],
        "architecture": null,
        "tools": [],
        "runtimes": ["python"]
      },
      "requires_skills": [],
      "prerequisites_review": {}
    }
  }
}
```

Somente os IDs desejados entram como `approved`. Os demais novos permanecem
pendentes; candidatos antigos não mencionados conservam suas decisões. Também
pode declarar `pending` ou `excluded`, com justificativa. Aprovar uma origem não
aprova suas skills. Aprovação de distribuição mantém `enabled: false`: a seleção
para cada projeto e a ativação no agente são passos posteriores.

```sh
./Automacao/manutencao-skills/skills review SESSION --decisions decisoes.json --review-id HASH_DA_DESCOBERTA
```

Esse comando prepara **outro dry-run**, sem promover. Confere novamente Git,
inspeção, hashes, recursos e metadados. Gera `plan.json`, `review.diff` e `plan_id`.
Leia os arquivos completos, inclusive adaptações de contrato e licença. Somente
depois da autorização explícita do usuário:

```sh
./Automacao/manutencao-skills/skills apply SESSION --plan-id HASH_DO_PLANO --approve
```

É o mesmo apply/recover da Etapa 3A: promoção global por troca de Skills, diário,
backup e validação final. Há uma breve janela sem Skills; não consumir durante a
promoção. Não é uma troca POSIX única. Não sobrescreve consumidores e não cria
commit Git automático. Depois de conferir, registrar manualmente o commit local.

Uma sessão selada aceita repetir as mesmas decisões, mantendo o plano. Mudanças
de decisão exigem nova descoberta. Se houver falha depois de escrever o candidato,
os dados parciais ficam preservados: repetir `add`, sem apagar ou sobrescrever o
candidato anterior. Recuperação de publicação interrompida continua disponível:

```sh
./Automacao/manutencao-skills/skills recover SESSION --approve
```

## Classificação, compatibilidade e impedimentos

- Categorias aprovadas: `Frontend`, `Backend`, `Mobile`, `Seguranca` (aceita
  `Segurança` nas decisões). Categoria incerta fica nula, sem criar categoria nova.
- As condições de compatibilidade usam os vocabulários atuais do bootstrap.
  Listas vazias significam ausência daquela restrição, não tecnologia presumida.
  Exige ao menos uma condição de aplicabilidade. Suporta `languages_all` opcional,
  frameworks obrigatórios/alternativos, funcionalidades, arquitetura, ferramentas,
  runtimes e `framework_versions` com listas de versões concretas. Versão omitida
  no projeto não satisfaz restrição de versão explícita. Intervalos/versionamento
  semântico, novas stacks e condições não expressáveis exigem análise posterior.
- Não substitui as políticas das 101 skills legadas. Novas regras são declarativas
  no catálogo, verificadas pelo mesmo seletor e pelo validador da biblioteca.
  Incompatíveis são omitidas com motivo; solicitação explícita incompatível bloqueia.
  A stack do usuário nunca é ajustada automaticamente.
- `tools` contém nomes de executáveis, não comandos/caminhos. Runtimes devem estar
  em `runtimes`, não em tools: sua resolução exige instalação global do asdf.
  Ferramenta/runtime ausente bloqueia aprovação, sem instalação automática.
- Cada texto de `dependency_evidence` exige entrada em `prerequisites_review`:
  `"texto exato": {"tools": [], "runtimes": ["python"], "reason": "..."}`.
  Mapeamentos precisam estar na política e disponíveis. Justificativas para
  evidências de exemplo ou contexto são decisões humanas auditáveis; não são prova
  automática de disponibilidade de todos os serviços/SDKs ou da semântica do texto.
- Dependências entre skills exigem `requires_skills` exato, aprovação individual
  das companheiras e mesmo pacote. Não aprova dependências implicitamente.
- Licença ausente, não identificada ou incompatível, referência não resolvida,
  conteúdo interno/experimental, scripts com novas dependências não atendidas,
  instalações remotas por pipe e layout incompatível permanecem pendentes.
- IDs duplicados na origem impedem registro ambíguo. Conteúdo já catalogado não é
  distribuído novamente. Nomes que colidem com skills **aprovadas** são bloqueados,
  porque a integração existente produz aliases por nome. Não foi alterada a lógica
  dos agentes. Conflitos só com entradas não distribuídas exigem lista exata em
  `conflicts_acknowledged`. Nomes longos demais para o alias também ficam pendentes.

## Pacotes e rastreabilidade

Novos pacotes usam `Skills/Categoria/origem/vendor/<caminho-original>`. Preservam
a organização relativa dos recursos, com arquivos comuns/licenças uma vez por
pacote. `skill_extra_files` registra recursos externos ao diretório da skill.
Adaptações de SKILL.md limitam-se ao contrato explícito e aos caminhos de
README/licença, com hashes antes/depois e unified diff. Conteúdo de terceiros não
é alterado silenciosamente.

Arquivos distribuídos recebem modo 0644, conforme o contrato existente: scripts
não são executados implicitamente por shebang. O modo original permanece no
índice Git da aquisição e o modo distribuído na proveniência; os bytes dos
recursos permanecem intactos, salvo adaptações explicitamente registradas.

Se a origem já tem um pacote legado, uma inclusão usa um pacote `-adicionais`
da mesma origem/categoria; não mistura layouts nem reempacota skills antigas.
Inclusões posteriores reutilizam esse pacote. `_repos/` continua cache opcional;
pacotes e cópias físicas não dependem dele. A atualização 3A reconhece as novas
origens e preserva suas decisões e regras de compatibilidade. Tags/commits explícitos
ficam fixados: `check` informa `revisao_fixada`, sem consulta de atualização ou
afirmação de disponibilidade atual do commit. Branches continuam acompanhadas.

HTTPS pode usar credenciais/proxy já configurados no Git; SSH usa chaves/agente
existentes e exige host key conhecida. Não inicia login interativo, não aceita
host keys automaticamente nem grava credenciais/configuração. Hooks/fsmonitor
ficam desativados e não há checkout, filtros, smudge ou submódulos. Nesta etapa,
SSH foi validado por parsing/invocação simulada, sem conexão/autenticação real.
TLS continua obrigatório nas consultas HTTPS; configuração local não desliga sua
verificação. Objetos recebidos passam também pelo fsck de fetch do Git.

Análise estática cobre referências Markdown, imports literais JS, imports Python,
AST e parsing de scripts suportados. Não é um resolvedor semântico completo de
imports dinâmicos, comandos em prose, SDKs ou serviços. TypeScript/Ruby/PowerShell,
renderers especiais e mudanças manuais podem exigir preparação posterior. Licença
é identificada por evidência textual para revisão, sem certificação jurídica.

**Consumidores:** permanecem intocados. O verificador atual recompõe planos com o
catálogo presente; depois de incorporação real, mesmo adicionar só pendentes muda
seu hash. Para verificar/reaplicar consumidores antigos, guardar a revisão original
do StackNauta em clone separado. Não se migram manifestos nem se aceitam hashes
novos silenciosamente.

Testes, demonstração e limites: [relatório 3B](../validacao-inclusoes/RELATORIO.md).
