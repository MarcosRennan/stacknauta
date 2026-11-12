# Manutenção da biblioteca

## Inclusão controlada — Etapa 3B

O [guia de inclusão](../../Automacao/manutencao-skills/INCLUSAO.md) documenta
`skills add URL`, `skills review`, decisões individuais e o apply por hash.
Descoberta não altera catálogo/pacotes ativos. Nada é aprovado automaticamente;
origens existentes são reconhecidas sem duplicação. A biblioteca real permanece
nas sete origens e 101 skills aprovadas durante a validação 3B.

## Atualização incremental — Etapa 3A

Usar a [CLI de manutenção](../../Automacao/manutencao-skills/README.md):

```sh
./Automacao/manutencao-skills/skills check
./Automacao/manutencao-skills/skills update expo
./Automacao/manutencao-skills/skills update --all
# Somente depois da revisão e autorização explícita:
./Automacao/manutencao-skills/skills apply SESSION --plan-id HASH_REVISADO --approve
```

A preparação é isolada e a promoção é global por lote, com diário e backup.
Não há atualização automática do cache, de consumidores ou de aprovações.
Conflitos, mudanças de licença, novas dependências e mudanças na distribuição
UI/UX bloqueiam a promoção para revisão manual. Recuperação, limites, exemplos
e testes estão no guia acima. Nenhuma origem real foi promovida na Etapa 3A.

## Preparação histórica — Etapa 1.5

O Git principal versiona os nove pacotes de distribuição, política, catálogo, templates necessários ao renderer próprio e ferramentas de validação. `_repos/` é apenas cache opcional de aquisição/atualização; a validação padrão e o consumo dos pacotes não precisam dele. Nenhuma origem foi atualizada nesta etapa.

## Conferência e preparação

A partir da raiz, com o Python global asdf instalado:

```bash
asdf exec python Skills/validacao/validar_biblioteca.py
asdf exec python Skills/validacao/validar_biblioteca.py --origens
asdf exec python Skills/manutencao/preparar_biblioteca.py
```

O primeiro comando é independente de cache. O segundo confere explicitamente as origens locais. O terceiro regenera em memória e compara os artefatos, sem escrever. Para preparar novamente as revisões fixadas e a política revisada:

```bash
asdf exec python Skills/manutencao/preparar_biblioteca.py --write
```

O empacotador lê somente as sete revisões locais do lock e verifica arquivos contra seus blobs originais antes de qualquer escrita. Não acessa rede, executa fornecedores, instala dependências ou habilita skills. Recusa pacotes com conteúdo local alterado, arquivos estranhos, colisões ou arquivos que ficariam obsoletos; não exclui nem usa força para resolver esses estados. Os destinos são relativos ao próprio StackNauta. `inventariar.py` conserva a função de aquisição histórica e recusa sobrescrever um catálogo de distribuição.

O renderer UI/UX é Python da biblioteca padrão e usa os templates oficiais preservados em `ui-ux-pro-max-templates/`. Seu resultado antes das adaptações foi comparado ao renderer oficial para quatro plataformas. A geração do pacote usa o perfil universal e registra adaptações de portabilidade/asdf. Não há necessidade de instalar CLI, Bun ou pacotes npm.

## Procedimento histórico para revisões que exigem adaptação manual

1. Preservar os clones anteriores, o Git principal e os relatórios para reversão. Clones rasos não constituem histórico remoto completo.
2. Conferir novamente URL, branch padrão e commit candidato. Adquirir para área nova sem alterar silenciosamente o cache aprovado. Não inicializar submódulos por padrão.
3. Inspecionar mudanças de SKILL.md, recursos, licenças, scripts, processos de distribuição, novas dependências e entradas removidas. Reclassificar explicitamente todas as skills na política; não aprovar pelo simples aparecimento de um arquivo.
4. Revisar lock, inventário de aquisição, templates e decisões em conjunto. A receita histórica não faz atualização, fetch ou resolução de conflitos. A CLI 3A prepara revisões compatíveis; alterações nos próprios arquivos de empacotamento exigem revisão.
5. Preparar artefatos e validar integridade, fechamento de cópia, renderização quando aplicável e clone local sem cache. Registrar diffs, relatórios e commit somente depois da revisão.
6. Em falha, consultar diário e backup da CLI 3A. Para adaptações manuais ou reversão deliberada, usar snapshot Git e clones anteriores em área de restauração separada. Não sobrescrever consumidores ou apagar estados para aparentar sucesso.

Os índices de aquisição da Etapa 1 mantêm as fontes originais rastreáveis. Arquivos empacotados modificados têm hash original, hash distribuído, motivo e diff. Licenças específicas e atribuições continuam junto dos recursos. A biblioteca não atualiza fontes durante consumo e não instala ferramentas para satisfazer pré-requisitos.

O núcleo e a integração compartilhada foram implementados nas etapas 2A–2D.
O bootstrap valida runtimes globais antes de escrever e copia fisicamente os
conjuntos selecionados. Não consulta atualizações durante a criação de projetos.
OpenCode e Gemini continuam pendentes de validação prática separada.
