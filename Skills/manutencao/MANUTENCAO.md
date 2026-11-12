# Manutenção da biblioteca

Disponível nesta etapa: inventário estático de fontes locais e validação offline. A rotina de atualização e a distribuição para consumidores ainda serão implementadas.

Para recalcular o catálogo das revisões já fixadas, a partir da raiz do StackNauta:

```bash
asdf exec python Skills/manutencao/inventariar.py
asdf exec python Skills/validacao/validar_catalogo.py
```

O inventariador verifica o Python global asdf, as revisões e a limpeza das sete fontes antes de escrever `catalogo.json`, os dois índices de evidências e os seis índices de categoria. Não baixa dependências, não executa fornecedores, não altera origens, não faz fetch e não habilita skills. Sua classificação é explícita no código; novos SKILL.md em revisões diferentes não entram pelo fluxo acima porque o lock precisa coincidir antes da geração.

Política para uma futura atualização manual:

1. Registrar intenção e escopo; guardar catálogo, evidências e os clones nas revisões anteriores para permitir reversão, especialmente porque clones rasos não preservam histórico remoto completo.
2. Conferir novamente URL, branch padrão e commit candidato, sem substituir silenciosamente a revisão instalada. Não inicializar submódulos por padrão.
3. Inspecionar diferenças de conteúdo, novas skills e nomes removidos, resources, scripts, licenças e processo oficial de distribuição. Classificar entradas novas antes de disponibilizá-las; não habilitar por mera presença.
4. Revisar o lock e a classificação explicitamente. Só então regenerar o inventário, validar e comparar o diff do Git principal. Fontes modificadas localmente devem interromper o processo.
5. Registrar a decisão e o relatório. Em caso de falha, retornar aos clones e catálogos anteriores preservados, sem exclusões ou sobrescritas automáticas. A estratégia operacional de reversão ainda depende de implementação.

Os fornecedores não recebem mudanças silenciosas. Qualquer adaptação futura de conteúdo, inclusive substituição de comandos Python por execução controlada via asdf, deverá existir em uma camada separada com origem, patch e validação documentados.

O bootstrap futuro não atualizará fontes durante a criação de projetos. Não se deve executar os instaladores oficiais nesta instalação para atualizar o catálogo: eles podem gravar configurações de agentes, instalar pacotes globais, remover layouts antigos ou habilitar skills.

Os diretórios de categoria são índices, e `_repos/` mantém o conteúdo. Não criar uma segunda cópia da biblioteca para cada agente. Em consumidores novos, a operação futura deverá selecionar o conjunto compatível e copiar fisicamente somente esse conjunto e os recursos necessários.
