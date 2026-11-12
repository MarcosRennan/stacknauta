# Análise anterior à implementação — Etapa 3B

Base: `3932c84`, árvore limpa; 101 aprovadas, 21 pendentes, duas excluídas,
sete origens e nove pacotes. Nenhuma incorporação real está autorizada nesta etapa.

`Updates` já resolve aquisição sem checkout/hooks/submódulos, snapshot, revisão
por hash, validação, troca global de Skills e recuperação. Serão extraídos apenas
os passos comuns de início/selagem do candidato; apply/recover continuam únicos.
`SOURCES`, choices da CLI e o validador fixam sete origens e precisam passar a
consultar o registro. HTTPS já existe; SSH requer transporte restrito ao GitHub,
sem gravação de configuração ou aceite automático de host keys.

`inventariar.build` e `biblioteca` fornecem frontmatter, referências, licenças,
blobs, contrato e fechamento. A receita histórica está fixada por hash e não será
alterada. O incremento deve preservar todos os pacotes antigos e usar proveniência
e diffs no mesmo formato. A análise de SKILL.md na raiz precisa corrigir o prefixo
`./`, que atualmente não corresponde aos caminhos do índice Git.

O seletor usa políticas explícitas por identificador. Será acrescentada leitura
estrita de regras declarativas para novas entradas, sem substituir políticas
legadas nem inventar stack. Vocabulários existentes de tecnologias serão mantidos;
casos não expressáveis continuarão pendentes. Categorias incertas permanecem nulas
até classificação explícita, sem criar nova categoria.

Descoberta e aprovação serão separadas: add só analisa; review com decisões
individuais prepara plano selado; apply continua exigindo hash e --approve.
Licenças desconhecidas, referências incompletas, conflitos não resolvidos e
dependências sem revisão impedem aprovação. Novas skills não são habilitadas.
Validação estática não certifica todos os workflows ou conteúdo de terceiros.

Fixtures Git locais testarão incorporação, seletor, recuperação e portabilidade.
Biblioteca real, consumidores, App-Web, credenciais e configuração asdf devem
permanecer preservados. OpenCode/Gemini não serão executados.
