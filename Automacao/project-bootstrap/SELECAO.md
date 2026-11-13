# Seleção automática e explícita — extensão 4B

O catálogo pode declarar `compatibility.selection_mode` por skill:

- Ausente ou `"automatic"`: comportamento histórico, elegível para raízes automáticas.
- `"explicit"`: exige seu ID na lista de escolhas; compatibilidade técnica sozinha
  não autoriza sua distribuição, nem como dependência de outra raiz.
- Outros valores, inclusive null e tipos não textuais, são recusados pelo parser
  compartilhado de compatibilidade. Não há lista de especializações no núcleo.

O campo pertence à compatibilidade já versionada no catálogo e nas decisões de
inclusão. O review existente aceita essa extensão e a atualização preserva a
compatibilidade registrada. Não exige migração dos registros anteriores.

```json
{
  "languages_any": ["javascript", "typescript"],
  "frameworks_any": ["react", "nextjs", "vue", "nuxt", "svelte", "astro"],
  "frameworks_all": [],
  "features_all": ["ui", "animation"],
  "architecture": null,
  "tools": [],
  "runtimes": [],
  "selection_mode": "explicit"
}
```

O exemplo é uma política possível de especialista web, não aprovação de skill.
Não presume React, Motion, GSAP ou instalação. As linguagens continuam exigindo
os runtimes globais já previstos pelo núcleo. Frameworks da lista são alternativas;
não são escolhidos ou adicionados pelo seletor. Projetos sem framework exigem
outra política devidamente revisada; não declarar um framework fictício para
obter compatibilidade.

## Semântica de entrada preservada

| Entrada `skills` | Resultado |
|---|---|
| Ausente ou null | Raízes aprovadas, compatíveis e automáticas; especialistas omitidas com motivo no dry-run |
| Lista não vazia | Conjunto completo de raízes; não se soma à seleção automática |
| Lista vazia | Sem raízes e sem skills |
| IDs repetidos | Erro de configuração, sem deduplicação silenciosa |
| ID desconhecido, pendente ou excluído | Erro, mesmo quando solicitado explicitamente |
| Incompatibilidade ou pré-requisito ausente | Erro para pedido explícito; omissão justificada no automático |

Uma raiz explícita continua incluindo suas dependências automáticas obrigatórias,
sem transformá-las em raízes. Uma dependência também marcada explicit precisa
constar nominalmente na lista. Sem essa escolha, bloqueia-se o fechamento inteiro;
não se elimina uma dependência para tornar o conjunto distribuível. Compatibilidade,
classificação, ferramentas, runtimes, hashes e recursos físicos continuam exigidos.
Quando a UI/UX Pro Max também for desejada, seu ID precisa constar nas raízes.

## Planos, autorização e formatos históricos

Não foram alterados schemas de configuração, plano, lock ou manifesto. O catálogo
e seu hash já participam do lock e do hash do plano, vinculando o novo metadado
à revisão do dry-run; não é necessário inserir campos novos nos consumidores.
Omitir selection_mode preserva a forma normalizada histórica. Declarar automatic
é equivalente à omissão. Não foram modificadas as políticas das 101 skills legadas.

Em reexecuções com manifesto existente, o núcleo conserva a seleção fixada e as
evidências históricas, como antes. A verificação não volta ao automático do
catálogo atual, nem atualiza hashes silenciosamente. Schemas de consumidores 1
e 2 continuam suportados, incluindo seus limites de recuperação e evidência.
Arquivos evolutivos são preservados; protegidos adulterados continuam bloqueados.

Codex, OpenCode e Gemini usam esse mesmo núcleo e a mesma integração. O campo
não ativa agentes, não lê linguagem natural para decidir o especialista, não
autoriza instalar bibliotecas e não controla toda execução futura de um agente.
A lista e o hash são entradas técnicas; autorização do usuário continua separada.
