# StackNauta

Base independente para um futuro bootstrap de projetos. **Etapa 1: aquisição e catálogo de skills. O project-bootstrap ainda não está implementado nem funcional.**

As sete fontes foram adquiridas novamente do GitHub. Nenhum script, skill ou arquivo da implementação anterior foi usado como base. Os diretórios antigos e os projetos consumidores ficaram fora das escritas desta instalação. A conferência de preservação está em [Skills/validacao/preservacao.json](Skills/validacao/preservacao.json).

## Estrutura

```text
StackNauta/
├── Automacao/
│   ├── project-bootstrap/.gitkeep
│   └── validacao-project-bootstrap/.gitkeep
├── Skills/
│   ├── Frontend/README.md
│   ├── Backend/README.md
│   ├── Mobile/README.md
│   ├── Seguranca/README.md
│   ├── manutencao/
│   │   ├── README.md
│   │   ├── MANUTENCAO.md
│   │   └── inventariar.py
│   ├── validacao/
│   │   ├── README.md
│   │   ├── PRECHECK.md
│   │   ├── INSPECAO.md
│   │   ├── arquivos.json
│   │   ├── recursos.json
│   │   ├── resultado.json
│   │   ├── preservacao.json
│   │   └── validar_catalogo.py
│   ├── _repos/                 # sete clones independentes, sem alterações
│   ├── fontes.lock.json
│   └── catalogo.json
├── .agents/skills/.gitkeep      # nenhuma skill habilitada
├── .gitignore
└── README.md
```

Os índices por categoria apontam para os arquivos originais; não existem cópias locais adicionais nem links simbólicos criados para distribuição. Os quatro links relativos já presentes nos fornecedores foram preservados e conferidos. Os `.gitkeep` mantêm apenas os três diretórios reservados sem implementação.

## Fontes e revisões adquiridas

Branch padrão conferida com `git ls-remote --symref URL HEAD` antes da aquisição. Todos os clones são rasos (`depth=1`, uma branch), sem checkout de submódulos. FastAPI também usa filtro `blob:none` e sparse-checkout de `fastapi/.agents/skills/fastapi`, mantendo a skill inteira, suas oito referências e a licença da raiz.

| Origem | Branch padrão/adquirida | Commit completo | Skills distintas |
|---|---|---|---:|
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | main | `6ae86f61f520d6ca229d2f40e070410638c908c5` | 7 |
| [FastAPI](https://github.com/fastapi/fastapi) | master | `5add7a458d629b07311d48261f696b5ac2bb9a5f` | 1 |
| [Remy349](https://github.com/Remy349/skills) | main | `5d9eae132afea72518ba0f1f41919f9e37964362` | 3 |
| [Expo](https://github.com/expo/skills) | main | `a9e5bd3fa00b4e61f632e43f85da73aee1942582` | 25 |
| [Chris Banes](https://github.com/chrisbanes/skills) | main | `50d54366e577460b769ce05b50da007de9939783` | 21 |
| [Android](https://github.com/android/skills) | main | `5815d27fda564aa9f07ebdcb5e57ed3e8d904e0d` | 36 |
| [Sentry](https://github.com/getsentry/skills) | main | `e94f22214528d69899d09c627b3315ddc3544816` | 31 |

São **124 skills distintas, 130 arquivos físicos SKILL.md**: seis são cópias de distribuição de subskills UI/UX já representadas por seus caminhos canônicos. Entre as 124 há uma skill interna de avaliação Expo, excluída de distribuição, e uma experimental. As demais 122 estão catalogadas como fontes; isso não significa distribuição preparada ou compatibilidade confirmada. **Zero skills habilitadas e zero distribuições preparadas.**

Classificação individual: Frontend 8, Backend 6, Mobile 65, Seguranca 9, manutencao 29 e validacao 7. Categoria da origem e categoria efetiva da skill são registradas separadamente; Sentry inclui várias rotinas de manutenção e Android inclui segurança.

## Catálogo e evidências

- [catalogo.json](Skills/catalogo.json): identificação de cada skill, URL, commit completo, caminho original, categoria, arquivos necessários, evidências de licença e dependências, menções a skills irmãs, status e pendências. Todos os caminhos de armazenamento são relativos ao StackNauta.
- [fontes.lock.json](Skills/fontes.lock.json): sete URLs, branches, revisões e modalidade de aquisição. Nenhuma atualização automática.
- [arquivos.json](Skills/validacao/arquivos.json): tamanho, SHA-256, modo e blob Git de cada arquivo materializado; links e omissões do sparse-checkout explicitados.
- [recursos.json](Skills/validacao/recursos.json): conferência estática de links Markdown e menções a references, scripts, assets, templates, data e agents.
- [INSPECAO.md](Skills/validacao/INSPECAO.md): peculiaridades de distribuição, licenças e dependências; interpretação dos limites da conferência.
- [resultado.json](Skills/validacao/resultado.json): resultado da validação local; [preservacao.json](Skills/validacao/preservacao.json): comparação das duas árvores legadas com o baseline anterior à criação.

`required_files` preserva o diretório completo de cada skill, recursos resolvidos e licenças ancestrais. É um inventário conservador, **não um plano de cópia validado**. Dependências condicionais, exemplos e referências externas ainda exigem interpretação. Nenhum arquivo do fornecedor foi corrigido, renderizado ou executado.

## Verificação local

Execute a partir desta pasta, com o Python global do asdf instalado:

```bash
asdf current python
asdf which python
asdf exec python Skills/validacao/validar_catalogo.py
```

O validador usa apenas a biblioteca padrão, não acessa rede, não instala nada, não escreve no projeto e não executa scripts de terceiros. Compara o catálogo regenerado em memória, commits, URLs, branches, recursos, licenças, hashes e blobs originais; também executa `git fsck` nas origens. A checagem de frontmatter cobre delimitadores, nome e descrição; não é validação YAML completa. Links externos não são testados. O relatório salvo registra a execução desta etapa; uma nova execução imprime um novo resultado em JSON.

O resultado `passed_with_documented_pending` significa integridade e inventário aprovados, com pendências documentadas. Não certifica scripts, comportamento das skills, renderização nem compatibilidade com agentes.

## Manutenção e próximos passos

O Git principal é local, sem remoto. `Skills/_repos/` é ignorado para evitar repositórios aninhados como gitlinks acidentais; cada origem conserva seu próprio Git. **Copiar apenas o Git principal não transporta a biblioteca**: preserve também os sete clones. O lock e os hashes permitem conferir revisões e conteúdo. Não existe comando de restauração/aquisição automatizada nesta etapa.

[MANUTENCAO.md](Skills/manutencao/MANUTENCAO.md) descreve a política ainda planejada de atualização manual, comparação de commits, validação e reversão. O inventariador local disponível apenas registra fontes já adquiridas; não atualiza nem habilita skills.

Para a Etapa 2, implementar uma única lógica de bootstrap com adaptações para Codex, OpenCode com DeepSeek e Gemini CLI. Ela deverá preparar somente o esqueleto inicial a partir da stack informada. Desenvolvimento da aplicação, geradores e integrações não fazem parte desta entrega.

A operação futura deverá validar antes de qualquer escrita no destino que os runtimes e o executor Python vêm das versões globais válidas e instaladas do asdf. Ausência deve interromper a operação, sem fallback para runtimes do sistema e sem instalação automática. Skills selecionadas e todos os seus recursos deverão ser copiados fisicamente para novos consumidores, sem links simbólicos. Não haverá atualização silenciosa durante o bootstrap. A lógica usará caminhos relativos à própria instalação.
