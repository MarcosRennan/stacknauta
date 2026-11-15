# Componentes de terceiros

A licença MIT da autoria própria do StackNauta não substitui as
licenças dos componentes incorporados. Os textos de licença, copyrights e avisos
originais permanecem nos caminhos abaixo. A identificação de uma organização de
origem não presume titularidade sobre todos os componentes daquele repositório.

As revisões e os arquivos distribuídos estão registrados em
[fontes.lock.json](Skills/fontes.lock.json), [catalogo.json](Skills/catalogo.json)
e nos PROVENANCE.json de cada pacote. Esta tabela reutiliza esse inventário.

| Pacote | Autor/organização identificada | Licença | Texto preservado | Origem | Atribuição/escopo |
|---|---|---|---|---|---|
| Frontend/ui-ux-pro-max | Next Level Builder; ui-styling identifica claudekit | MIT geral; Apache-2.0 no LICENSE de ui-styling, com divergência MIT no frontmatter; fontes OFL-1.1 | [MIT](Skills/Frontend/ui-ux-pro-max/LICENSE), [Apache](Skills/Frontend/ui-ux-pro-max/skills/ui-styling/LICENSE.txt), [fontes e avisos OFL](Skills/Frontend/ui-ux-pro-max/skills/ui-styling/canvas-fonts/) | [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Preservar os escopos separados; ver pendência abaixo. |
| Backend/fastapi | Sebastián Ramírez / FastAPI | MIT | [LICENSE](Skills/Backend/fastapi/LICENSE) | [FastAPI](https://github.com/fastapi/fastapi) | Copyright e permissão MIT mantidos. |
| Backend/remy | Santiago Moraga Caldera / Remy349 | MIT | [LICENSE](Skills/Backend/remy/LICENSE) | [Remy349](https://github.com/Remy349/skills) | Copyright e permissão MIT mantidos. |
| Mobile/expo | 650 Industries, Inc. (Expo); Emil Kowalski em expo-animation | MIT | [LICENSE](Skills/Mobile/expo/LICENSE), [expo-animation/LICENSE](Skills/Mobile/expo/skills/expo-animation/LICENSE) | [Expo](https://github.com/expo/skills) | Aviso específico de expo-animation também preservado. |
| Mobile/chrisbanes | Chris Banes / projeto de origem | Apache-2.0 | [LICENSE](Skills/Mobile/chrisbanes/LICENSE) | [Chris Banes](https://github.com/chrisbanes/skills) | Avisos originais e indicação das adaptações preservados. |
| Mobile/android | Projeto Android / Google | Apache-2.0 | [LICENSE.txt](Skills/Mobile/android/LICENSE.txt) | [Android](https://github.com/android/skills) | Avisos originais e indicação das adaptações preservados. |
| Seguranca/android | Projeto Android / Google | Apache-2.0 | [LICENSE.txt](Skills/Seguranca/android/LICENSE.txt) | [Android](https://github.com/android/skills) | Mesmo licenciamento da origem, sem relicenciamento pelo StackNauta. |
| Backend/sentry | Sentry / projeto de origem | Apache-2.0 | [LICENSE](Skills/Backend/sentry/LICENSE), [django-perf-review/LICENSE](Skills/Backend/sentry/skills/django-perf-review/LICENSE) | [Sentry](https://github.com/getsentry/skills) | Aviso específico da skill e licença completa do pacote mantidos. |
| Seguranca/sentry | Sentry; OWASP Foundation e contribuidores nas referências derivadas | Apache-2.0; CC-BY-SA-4.0 no material derivado de OWASP | [LICENSE](Skills/Seguranca/sentry/LICENSE), [security-review/LICENSE](Skills/Seguranca/sentry/skills/security-review/LICENSE) | [Sentry](https://github.com/getsentry/skills), [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) | Atribuição, link CC e indicação de alterações preservados; ver escopo abaixo. |
| Frontend/gh-iart-ai-web-animation-skills | iart.ai | MIT | [vendor/LICENSE](Skills/Frontend/gh-iart-ai-web-animation-skills/vendor/LICENSE) | [iart.ai](https://github.com/iart-ai/web-animation-skills) | Copyright e permissão MIT mantidos. |
| Frontend/gh-anthropics-skills | Anthropic / projeto de origem | Apache-2.0 específica de frontend-design | [frontend-design/LICENSE.txt](Skills/Frontend/gh-anthropics-skills/vendor/skills/frontend-design/LICENSE.txt) | [Anthropic](https://github.com/anthropics/skills) | Subconjunto frontend-design; não inclui todas as dependências da origem. |

Os templates de manutenção da origem UI/UX também preservam seu
[LICENSE MIT](Skills/manutencao/ui-ux-pro-max-templates/LICENSE).
Os avisos de adaptação StackNauta nos SKILL.md e os PROVENANCE.json identificam as
alterações de distribuição/execução. Não se substituem os textos de licença por
esta tabela ou pelos links externos.

## ui-styling: escopo ainda pendente

Na revisão incorporada `6ae86f61f520d6ca229d2f40e070410638c908c5`, o
[SKILL original](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/6ae86f61f520d6ca229d2f40e070410638c908c5/.claude/skills/ui-styling/SKILL.md)
declara MIT, enquanto o
[LICENSE original do mesmo diretório](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/6ae86f61f520d6ca229d2f40e070410638c908c5/.claude/skills/ui-styling/LICENSE.txt)
contém Apache-2.0. O MIT da raiz da origem não explica essa diferença nem estabelece
dual licensing. Os arquivos foram preservados; o StackNauta não escolhe uma licença
substituta nem considera a divergência resolvida por ambas serem permissivas.

O escopo MIT/Apache dessa revisão continua sem esclarecimento da origem. Na
distribuição, preservam-se ambos os textos e os avisos de copyright e adaptação
identificados; não foi encontrada proibição concreta de redistribuição nos termos
examinados. Esse registro não resolve juridicamente a divergência nem afirma dual
licensing. A licença própria do StackNauta não substitui nenhum dos dois textos.

## Fontes OFL

Os 54 TTF em canvas-fonts mantêm os copyrights e a declaração OFL embutidos;
os 27 textos OFL completos do pacote foram preservados. Não houve alteração de
fontes, nomes reservados ou avisos. Para explicitar as duas famílias discutidas na
auditoria:

- IBM Plex Serif mantém o copyright 2020 IBM Corp. All rights reserved nos TTF.
  O aviso compartilhado [IBM Plex](Skills/Frontend/ui-ux-pro-max/skills/ui-styling/canvas-fonts/IBMPlexMono-OFL.txt)
  preserva Copyright © 2017 IBM Corp. e Reserved Font Name "Plex".
- Instrument Serif mantém Copyright 2022 The Instrument Serif Project Authors
  (https://github.com/Instrument/instrument-serif), também registrado nos TTF.
  Sua licença é SIL OFL-1.1; o texto integral comum da OFL está preservado, por
  exemplo, em [InstrumentSans-OFL.txt](Skills/Frontend/ui-ux-pro-max/skills/ui-styling/canvas-fonts/InstrumentSans-OFL.txt).
  O copyright de Instrument Sans nesse arquivo não substitui o de Instrument Serif,
  explicitado aqui e nos metadados das fontes.

Esses avisos e textos devem acompanhar a redistribuição correspondente. Ausência
de um nome de arquivo OFL por família não equivale, sozinha, a ausência de licença.
A OFL permite avisos em metadados apropriados, preserva o licenciamento das fontes
e restringe o uso de Reserved Font Names em versões modificadas. Ver
[condições oficiais](https://openfontlicense.org/open-font-license-official-text/).

## Referências OWASP — CC-BY-SA

O material de referência de security-review deriva da OWASP Cheat Sheet Series,
da OWASP Foundation e seus contribuidores, sob
[CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/).
O aviso local, a origem e o link da licença estão preservados. As adaptações de
distribuição/execução StackNauta estão identificadas nos arquivos e na proveniência.
O material adaptado correspondente mantém atribuição e ShareAlike; isso não
relicencia automaticamente o código próprio nem toda a coleção do StackNauta.
