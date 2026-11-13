# Etapa 4B — Rodada 2B: preparação da Frontend Design

Executada em 13/11/2026. **Parecer: pronta com ressalvas para futura revisão
individual**, no escopo web conservador proposto e com precedência visual levada
explicitamente ao contexto de consumo autorizado. Não é aprovação. Não houve
nova aquisição, decisão, plano, promoção ou criação de consumidor.

## Estado inicial e referência operacional

HEAD inicial/final: `56b33bdfaac4a5e06c16418fface2611a52b7b24`.
Não havia arquivo rastreado modificado. Existiam somente os dois relatórios
esperados, não rastreados, da [Rodada 2A](../validacao-design-rodada2a/RELATORIO.md).
Foram preservados byte a byte; seus hashes constam de [propostas.json](propostas.json).
Não se tentou limpar o Git ou criar commit para viabilizar planejamento.

Consultados: AGENTS.md, documentação de manutenção/inclusão, CLI real,
[contrato de seleção](../project-bootstrap/SELECAO.md), configuração, catálogo,
núcleo de seleção, geração de requisitos, integração comum, relatórios 1B/1C
e evidências 1D.3. Não se prosseguiu na análise das demais candidatas da 2A.

As validações existentes, inicial e final, passaram com pendências documentadas
e **zero erros**: **104 aprovadas, 27 pendentes, duas excluídas, oito origens e
dez pacotes**. Nenhum catálogo, lock, pacote ou classificação mudou. A candidata
não possui registro no catálogo ativo; seu estado de descoberta é `pending`
somente no staging, sem aumentar a contagem ativa de pendentes.

## Origem, sessão e integridade

| Campo | Valor confirmado |
|---|---|
| ID completo | `gh-anthropics-skills:frontend-design` |
| Nome | `frontend-design` |
| Origem | `gh-anthropics-skills` |
| Repositório | `https://github.com/anthropics/skills.git` |
| Commit adquirido na 2A | `2c5958ecac7cee2b583967a2c4981d0f4a75c579` |
| Caminho | `skills/frontend-design/SKILL.md` |
| Sessão reutilizada | `78ab56b987824743915bca34f29e1090` |
| Review oficial | `693c6aa1be23fc91c05b9c4ae988055965392dc343f775487cf8fa0812be1b3a` |
| Plan ID | **Ausente** — nenhuma decisão de aprovação enviada |

Foi executado somente o review oficial, sem decisões:

```sh
Automacao/manutencao-skills/skills review 78ab56b987824743915bca34f29e1090
```

A identidade do review foi revalidada pelo módulo existente. Os cinco arquivos
regulares materializados na aquisição foram confrontados por SHA-256, blob Git,
modo e árvore do commit. O analisador existente foi executado novamente em
leitura; seu resultado coincide com a análise original. HEAD e arquivos rastreados
da baseline coincidem. Os dois registros de recursos coincidem integralmente
com a evidência 2A, sem divergências, links, hardlinks ou arquivos ausentes.

| Recurso | Bytes / modo Git | SHA-256 |
|---|---|---|
| `skills/frontend-design/SKILL.md` | 9.390 / 100644 | `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3` |
| `skills/frontend-design/LICENSE.txt` | 10.174 / 100644 | `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` |

Não há colisão de origem, ID ou nome no catálogo. A sessão foi adquirida de
`main` com `revision_type: branch`; **o commit e os bytes materializados estão
fixados e verificados**, mas isso não equivale a um cadastro por commit. Não
se consultou nem substituiu pelo HEAD remoto atual. Em uma eventual redescoberta,
preferir fixação formal pelo commit acima, sem editar a sessão antiga.

## Leitura funcional integral e limites

O [SKILL.md original fixado](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/frontend-design/SKILL.md)
foi lido integralmente, como dado de fornecedor, não como instrução para esta
execução. As referências abaixo usam suas linhas originais, anteriores a qualquer
adaptação contratual de distribuição.

| Responsabilidade | Procedimento concreto | Limite ou preferência subjetiva |
|---|---|---|
| Direção contextual, linhas 9–13 | Identificar assunto, público, trabalho principal e confirmar contexto ausente | A narrativa de cliente insatisfeito e disposição a risco não pode ser presumida |
| Composição, 17–30 e 47–51 | Plano de cores, tipos, layout/alinhamento e wireframes ASCII; relacionar elementos ao conteúdo | Hero, escala, número de famílias e tratamentos preferidos não são universais |
| Originalidade, 38–53 | Comparar plano ao briefing, rever padrões repetidos e justificar escolhas antes de implementar | A própria avaliação do agente não é aprovação visual do usuário |
| Execução, 32, 55 e 59 | Cuidar de especificidade CSS, foco, responsividade, reduced motion e crítica visual quando possível | Não contém auditoria completa de acessibilidade, testes de performance ou garantia estética |
| Conteúdo, 34 e 63–71 | Vocabulário consistente, CTAs claros e mensagens úteis | Criar placeholders não autoriza substituir fatos, textos ou tom aprovados |

Não é um catálogo adicional de estilos e não fornece um resolvedor de stack.
Não obriga assimetria, maximalismo ou um framework específico. A contenção e o
combate a determinados padrões são preferências a aplicar segundo o contexto,
não proibições de estilos legítimos. A linha 45 reconhece expressamente que a
direção definida no briefing prevalece, inclusive quando pede esses estilos.

Pode melhorar exploração criativa, mas não há evidência nesta rodada de melhora
visual efetiva: nenhuma interface foi construída, renderizada ou avaliada por
usuários. Screenshot é opcional, não requisito garantido pelo ambiente.

## Complementaridade com UI/UX Pro Max

A UI/UX Pro Max permanece intacta e central: pesquisa de estilos, paletas,
tipografia, UX/acessibilidade, componentes e recomendações por stack. Seu texto
já diferencia consultas de projeto novo, correção pontual e stack; documenta
Master e overrides de páginas. Não é necessário regenerar um sistema visual
para qualquer tarefa de revisão.

Frontend Design acrescenta um procedimento de exploração contextual e crítica
de repetição estética. Há redundância em cores, tipos, layout, movimento e
clareza de conteúdo. Seu uso agrega mais valor quando existe um eixo criativo
livre ou uma solicitação de alternativa; agrega menos numa correção rotineira
já atendida pela UI/UX existente.

Ordem operacional proposta:

1. Ler briefing, restrições e artefatos aprovados, identificando seus caminhos reais.
2. Usar as orientações aplicáveis da UI/UX e convenções existentes como referência.
3. Explorar com Frontend Design somente eixos livres ou mudanças solicitadas.
4. Apresentar alternativas e impactos; implementar somente mudanças autorizadas
   e validar resultado contra requisitos e artefatos.

Não é uma ordem obrigatória de carregamento imposta pelo núcleo. Ambas podem
ser distribuídas independentemente: não há recurso compartilhado obrigatório ou
dependência técnica entre elas. **`requires_skills: []`** permanece na proposta.
Quando ambas forem desejadas, solicitar os dois IDs nas raízes explícitas.

Em interface aprovada, continuam úteis crítica de legibilidade, especificidade
CSS, foco, espaçamento, conteúdo e coerência, dentro da tarefa autorizada. Não
se infere permissão para substituir paleta, tipos, componentes ou layout.

## Conflitos criativos e mitigação

São riscos contextuais, não comportamentos que foram executados. O JSON contém
referência, requisito afetado, gravidade, mitigação e efeito sobre a recomendação
para cada item.

| ID / linhas | Incentivo e risco | Gravidade/contexto | Mitigação e efeito |
|---|---|---|---|
| V01 — 9, 13 | Assumir insatisfação do cliente, risco estético ou assunto/público a partir de memória | Alta em redesign não solicitado; moderada em exploração nova | Confirmar lacunas; tratar a narrativa como hipótese, não briefing real |
| V02 — 17, 50, 59 | Novo hero, alinhamento/composição e contenção podem contrariar layout aprovado ou dashboard sem hero | Moderada; alta se substituir decisão aprovada | Restringir aos eixos livres; não impor hero, assimetria ou contenção a qualquer interface |
| V03 — 19–28 | Escolher novas famílias/escalas ou rejeitar tratamentos pode substituir tipografia da marca | Alta com tipografia aprovada | Preservar tokens; mudanças são propostas separadas, sujeitas a confirmação |
| V04 — 38–51 | Aversão a estéticas recorrentes e novo plano de tokens podem tratar sistema existente como projeto em branco | Alta em Design System consolidado | Inventariar e reaproveitar artefatos; linha 45 já subordina preferências ao briefing |
| V05 — 53, 55 | Autocrítica seguida de implementação pode ser confundida com autorização humana | Alta se mudar decisões consolidadas | Separar proposta, crítica e aprovação; originalidade autoavaliada não aprova execução |
| V06 — 34, 63–71 | Placeholder/copy pode alterar conteúdo factual, CTAs e voz aprovada | Alta ao publicar invenção como fato; moderada em rascunho | Identificar conteúdo provisório; confirmar alterações antes de substituir textos reais |
| V07 — 17, 32, 59 | Um momento coreografado ou ferramenta de screenshot pode gerar efeitos/dependências não solicitados | Moderada; potencialmente alta para acessibilidade | Não adicionar movimento por iniciativa; preservar reduced motion e permissões; nenhuma especialista de animação é dependência automática |
| V08 — 13, 59 | Memória e juízo de harmonia/originalidade podem prevalecer sobre requisitos atuais ou simular validação objetiva | Moderada | Conferir artefatos atuais; não declarar WCAG, performance ou eficácia visual sem testes próprios |

A orientação externa é viável porque esclarece o briefing e seus artefatos sem
contradizer a primazia já prevista na linha 45. Não se recomenda reescrever o
upstream para remover toda preferência subjetiva. Também não se presume que a
mera seleção explícita elimine esses riscos.

## Precedência visual proposta

Esta hierarquia está formalizada **como proposta de consumo**, não como instrução
já distribuída ou garantia técnica:

1. **Requisitos e restrições do projeto:** briefing, função, marca, público,
   conteúdo, acessibilidade, performance, tecnologias e restrições do usuário.
2. **Decisões e artefatos aprovados:** identidade, Design System, tokens,
   componentes, layouts, tipografia, cores, proporções, responsividade e interação.
3. **Diretrizes existentes aplicáveis:** UI/UX Pro Max e convenções do projeto,
   subordinadas aos itens anteriores.
4. **Exploração complementar:** sugestões Frontend Design e refinamentos opcionais,
   somente no escopo solicitado e nos aspectos livres.

Sem identidade aprovada, apresentar alternativas para revisão. Com identidade
aprovada, preservar os artefatos e limitar mudanças à tarefa autorizada. Se um
novo requisito conflitar com decisão anterior, registrar a divergência para
decisão do usuário. Mudança de decisão aprovada exige proposta com motivo,
impacto e confirmação antes da aplicação. Não inventar aprovações ou conteúdo
factual nem trocar stack, instalar assets/bibliotecas ou adicionar movimento
por associação à skill.

### Canal existente, rastreabilidade e limite

O fluxo aceita `requirements.constraints`; `normalize` preserva essas strings.
`core.agent_tasks` e `core.skeleton` as levam a `.stacknauta/config.json`,
`docs/REQUIREMENTS.json` e `.stacknauta/agent-plan.json`. O AGENTS.md gerado orienta
ler esses documentos; a integração comum também encaminha para esse contexto.
O teste E verificou o transporte em memória, sem plano ou escrita de consumidor.

Foi preparado texto próprio StackNauta de precedência, versão **2B.1**, completo
em `propostas.json` e no staging `rodada2b/precedencia-proposta.md`. SHA-256 UTF-8:
`9d30d69fb070ccda56abe1ee8b2e3084fad3989047bc119ee32f8beafd120a16`.
É hash documental, **não hash de autorização ou plan_id**. Sua utilização futura
deve constar do pedido/configuração autorizados e do prompt de consumo, com os
caminhos reais dos artefatos aprovados. Não foi injetado automaticamente.

Não é necessário patch visual no fornecedor para esse escopo operacional.
O empacotamento existente somente acrescenta contrato de execução e ajusta
caminhos; não contém precedência visual automática e não oferece entrada de
patch arbitrário rastreável para nova inclusão. Se a decisão exigir uma guarda
adicional embutida em toda cópia, **essa modalidade fica bloqueada** até etapa
própria. Não editar manualmente inspeção, catálogo ou contrato para obtê-la.
Prompts e restrições carregam orientação, mas não comprovam obediência futura
do agente. O original, o contexto e a proposta devem ser avaliados conjuntamente.

## Metadados completos propostos

Categoria: `Frontend`. Nenhum campo abaixo foi gravado no catálogo:

```json
{
  "category": "Frontend",
  "compatibility": {
    "languages_any": ["javascript", "typescript"],
    "frameworks_any": ["react", "nextjs", "vue", "nuxt", "svelte", "astro"],
    "frameworks_all": [],
    "features_all": ["ui"],
    "architecture": null,
    "tools": [],
    "runtimes": [],
    "selection_mode": "explicit"
  },
  "requires_skills": [],
  "prerequisites_review": {},
  "conflicts_acknowledged": []
}
```

| Campo | Justificativa / alcance |
|---|---|
| category | Frontend é uma das quatro categorias aceitas |
| languages_any | JS ou TS são valores existentes; não exige ambas; HTML/CSS não são identificadores suportados |
| frameworks_any | Seis alternativas web já registradas; JS isolado não identifica frontend |
| frameworks_all | Vazio: não exige combinação de frameworks |
| features_all | `ui` existe; intenção criativa vem da escolha nominal e briefing, não de feature inventada |
| architecture | null não impõe arquitetura nem autoriza alterá-la |
| tools | Nenhuma ferramenta proprietária obrigatória; screenshot é opcional |
| runtimes | Skill textual sem runtime próprio; executor e runtimes do projeto seguem o núcleo/asdf, inclusive Node para JS/TS |
| selection_mode | `explicit` é aceito pelo parser compartilhado e exige pedido nominal, inclusive como dependência |
| requires_skills | Nenhuma; complementaridade não é dependência técnica |
| prerequisites_review / conflicts_acknowledged | Vazios: sem evidências obrigatórias ou colisões extraídas |

`skills: null` mantém seleção automática histórica. Lista explícita é o conjunto
completo de raízes; UI/UX Pro Max não se soma por associação. O metadado não
aprova a skill, não interpreta linguagem natural e não seleciona especialistas
de animação apenas pela presença de `animation`.

### Vanilla, mobile e extensão futura

HTML/CSS são conceitualmente pertinentes à skill, mas não linguagens do contrato.
JS sem framework normaliza, porém não satisfaz a política conservadora. Não se
criou framework `vanilla` nem se abriu compatibilidade a qualquer backend JS.

React Native/Expo isolados não satisfazem a lista web. React + React Native
satisfaz o predicado pela presença de React: **o núcleo não distingue o alvo**.
Exigir alvo web inequívoco e suspender consumo no cenário ambíguo; não afirmar
que há um bloqueio técnico inexistente. Seleção explícita não resolve isso.

Alternativa futura: estudar, em etapa separada, um discriminador de alvo web/nativo
e declaração explícita de frontend sem framework. Nenhum nome de campo novo foi
tratado como aceito ou implementado. Também não há campo que imponha aprovação
visual ou precedência comportamental ao agente.

## Licença, recursos, segurança e agentes

Apache-2.0 foi confirmada no `LICENSE.txt` do próprio diretório e no apontamento
do frontmatter. Não se inferiu licença da raiz para toda a origem. No diretório
e ancestrais pertinentes não há NOTICE específico adicional. O arquivo global
THIRD_PARTY_NOTICES.md contém avisos de outros componentes/fontes, não inclui
referência à frontend-design e não acrescenta binários/assets a este fechamento.
Nenhum titular/ano de copyright específico foi encontrado nos dois recursos;
não se fabricou atribuição. Preservar a origem e revisão na proveniência.

Para cópias, acompanhar a licença integral e conservar avisos aplicáveis. Para
versões modificadas, observar a identificação destacada das alterações da seção
4(b), preservar avisos e eventuais atribuições NOTICE aplicáveis conforme 4(d),
além dos hashes/diffs/proveniência existentes. O texto não apresenta proibição
de uso comercial, mas não concede licença irrestrita de marcas ou de assets
futuros. Não transforma ausência de restrição técnica em certificação jurídica.

Uma futura distribuição padrão acrescentaria o contrato de execução já suportado,
com rastreabilidade. O hash distribuído ainda **não existe**: não confundir com
o hash original acima, nem inventá-lo antes de um plano autorizado.

Fechamento completo: dois arquivos regulares 0644, sem scripts, imports, comandos
Shell/Python/JavaScript, URLs no SKILL.md, referências locais ausentes, serviços,
downloads ou instalações obrigatórias. O livro citado é referência textual,
não material adquirido/redistribuído. Fontes e imagens que venham a ser escolhidas
requerem revisão própria. A prose orienta construir/revisar código e conteúdo;
isso pode ter efeitos no uso futuro, mas nada foi executado nesta análise.

| Evidência | Resultado |
|---|---|
| Frontmatter e estrutura | name, description e license reconhecidos pelo inventário; alias esperado cabe no limite portátil |
| Recursos físicos | Completos; nenhum script ou ferramenta específica de Claude exigido |
| Conversão por agente | Não identificada para leitura; somente contrato/caminhos padrão em futura inclusão autorizada |
| Codex, OpenCode e Gemini | Portabilidade textual provável pelo núcleo comum; não certifica workflow completo |
| Descoberta nativa / ativação | Não executadas / não testada |
| Screenshot/avaliação visual | Condicionais às ferramentas/permissões do ambiente; não executados |

## Cenários e verificações efetivamente executados

**Oito testes direcionados aprovados**, zero falhas, erros ou skips; 0,034 s.
Harness próprio de inspeção somente no staging, executado pelo Python global
asdf. Não registra candidata como aprovada, altera Library ou cria plano/aplicação.

| Cenário | Resultado observado e limite |
|---|---|
| A — automático | Catálogo ativo seleciona somente UI/UX no perfil web ui/animation/performance; nenhuma especialista de animação. Modo proposto normaliza como explicit; candidata está ausente, sem simular disponibilidade |
| B — Frontend Design nominal | Predicado proposto aceita os seis frameworks. Library real rejeita o ID não catalogado; sem distribuição fictícia |
| C — UI/UX isolada | Raízes e selecionadas somente UI/UX; regra histórica sem selection_mode adicional preservada |
| D — combinação | Configuração preserva os dois IDs e ambos os predicados são compatíveis; seleção real bloqueia a candidata ausente. Combinação física não executada |
| E — identidade aprovada | Orientação preservada em config, requisitos e agent-plan gerados somente em memória. Não testa interpretação/obediência do agente; conflitos analisados acima |
| F — vanilla | JS sem framework rejeitado pelo predicado; HTML/CSS e framework vanilla recusados pelo vocabulário |
| G — mobile | Expo/React Native isolados rejeitados; combinação React + React Native aceita pelo predicado, risco exposto e não distribuído |
| H — incompatível | Backend Express, Python/FastAPI e ausência de ui rejeitados pelo predicado. Guarda nominal real de uma especialista já ativa também rejeitou stack incompatível; valores inválidos de selection_mode recusados |

Foi verificado somente transporte de artefatos em memória, não um plano
real de distribuição da candidata. O caminho temporário de destino continuou
inexistente. As consultas de runtime do teste E identificaram Python 3.14.8 e
Node 24.21.0 globais asdf, sem instalar ou executar fornecedores.

Comando do harness:

```sh
Automacao/python-global .stacknauta-updates/78ab56b987824743915bca34f29e1090/rodada2b/test_scenarios.py
```

Duas validações da biblioteca foram executadas com
`Skills/validacao/validar_biblioteca.py --sintaxe-node --sem-smoke-fornecedor`,
via `Automacao/python-global`. As mesmas contagens e zero erros foram confirmados;
os sete JavaScript ativos foram somente parseados. As 298 aprovações e 104 cópias
físicas da 1D.3 são **históricas**, não reexecutadas: nenhum código de produção ou
pacote ativo mudou. Não se considera eficácia visual ou integração nativa testada.

## Prontidão, impedimentos operacionais e Rodada 2C

**Pronta com ressalvas** significa elegível para revisão individual sob seleção
explícita, escopo web conservador e orientação de precedência adotada no consumo.
Não há bloqueador técnico automático de licença, fechamento, nome ou integridade.
Os conflitos visuais não foram ocultados; sua mitigação operacional deve ser
aceita como condição. Se for exigida guarda adicional intrínseca/automática,
essa modalidade ainda não está pronta, conforme o limite de adaptação acima.

Não é possível gerar plano nesta execução: falta autorização individual e o
planejador exige árvore Git limpa. Os relatórios não rastreados são esperados,
não adulteração de origem; o review somente leitura funciona com eles. Não se
submeteu `pending` como artifício nem se chamou uma revisão com decisões.

Para a 2C:

1. Revisar os metadados, o escopo e a proposta de precedência; decidir sobre
   eventual autorização individual, sem confundi-la com autorização de promoção.
2. Organizar documentação/baseline por autorização própria; não apagar relatórios
   para passar `clean()`. Se HEAD mudar, renovar descoberta oficial fixada no
   commit original e gerar novos identificadores, sem editar a sessão antiga.
3. Se necessária essa renovação, usar o comando existente abaixo, somente na
   etapa autorizada e em baseline apropriada — **não foi executado na 2B**:

```sh
Automacao/manutencao-skills/skills add https://github.com/anthropics/skills --ref 2c5958ecac7cee2b583967a2c4981d0f4a75c579 --path skills/frontend-design
```

Depois de autorização específica, o review com decisões poderá produzir dry-run;
inspecionar licença, contrato acrescentado, caminhos, hashes e diff antes de
qualquer decisão posterior de aplicação. Não há plan_id artificial neste relatório.

## Artefatos e estado final

Criados fora do staging: este RELATORIO.md e [propostas.json](propostas.json).
Na sessão reutilizada, `rodada2b/` contém inspeção, retorno CLI, orientação
versionada, proposta-base e harness/log/JSON de cenários. São artefatos próprios
de análise, sem cópia modificada do fornecedor, decisão ou plano. Registros
anteriores da sessão e relatórios 2A foram preservados.

Git final: mesmo HEAD, nenhum rastreado modificado, quatro relatórios não
rastreados esperados — os dois da 2A e os dois da 2B. **Zero commits e zero push.**
A biblioteca continua 104/27/2, oito origens e dez pacotes. App-Web e consumidores
existentes não foram destinos de escrita; não se fez auditoria forense de seus
diretórios. Nenhum backup histórico foi limpo/alterado. Não se executaram agentes,
instalações, builds, scripts de fornecedores ou novas aquisições.

**Parado antes de aprovação ou promoção.** A proposta é suficiente para decidir
sobre uma revisão individual condicionada na próxima rodada, não para declarar
distribuição efetuada ou precedência automaticamente imposta aos agentes.
