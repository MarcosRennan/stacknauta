# Orientações para revisão — não distribuídas

Estas orientações são documentação da Rodada 1B. Não alteram os originais,
o staging ou pacotes. Seleção explícita restringe distribuição; não impede que
um agente ou pessoa execute comandos fora do StackNauta em outra ocasião.

## Condições comuns às quatro candidatas

Preservar LICENSE e o fechamento completo, incluindo scripts/README.md,
contact-sheet.sh, seek-shot.sh e probe-mp4.sh. O contrato existente que a inclusão
insere no SKILL.md e no README proíbe instalação implícita, fallback de runtime
e execução de shebangs. Esse contrato é necessário, mas não é um sandbox para
execuções futuras. Nenhum auxiliar é chamado pela preparação/bootstrap.

Antes de eventual execução separada:

- seek-shot exige Node/npx, Playwright e navegador compatível disponíveis.
  O comando original usa `npx -y playwright` e pode baixar/executar código; não
  seguir esse caminho se depender de aquisição implícita. Não foi validada uma
  alternativa de comando e não se propõe uma substituição não testada.
- contact-sheet usa ffmpeg e, no caso de uma imagem, cp. O caminho ffmpeg usa
  `-y`; saídas preexistentes podem ser sobrescritas. Confirmar diretório/nomes de
  saída e autorização de sobrescrita antes de uma execução futura.
- probe-mp4 usa ffprobe, head e awk; ele inspeciona mídia e não certifica a
  qualidade de uma animação web. Não é requisito para usar exemplos CSS.
- seek-shot produz `frame-<t>.png` no diretório corrente, com nomes previsíveis;
  contact-sheet recebe um destino. Planejar a área de saída sem tocar projetos
  alheios. Ter os arquivos distribuídos não autoriza executá-los.
- Resolver runtimes exclusivamente nas instalações globais asdf. Bibliotecas
  de aplicação (Motion, GSAP, Flubber) não são runtimes ou ferramentas CLI.
  Disponibilidade de ffmpeg/ffprobe foi observada na 1A; não garante que estejam
  presentes em outro ambiente. Playwright/Chromium continuam não validados.

## micro-interaction

CSS nativo é alternativa básica, sem React ou Motion. Escolher CSS conforme os
navegadores-alvo e manter fallback para recursos modernos. Os exemplos React,
spring, AnimatePresence, layout/layoutId e gestos exigem contexto React/Motion
compatível e previamente escolhido. Não adicionar framework, trocar stack,
instalar Motion ou converter UI inteira para React pela presença desta skill.
Um pedido explícito de microinterações não equivale a autorizar toda essa stack.
Um demo HTML/CDN não substitui componentes, build ou integração já declarados.

## svg-animation

CSS e SMIL são alternativas para SVG independente de framework. Não presumir
GSAP: MotionPath/MorphSVG/Flubber são opções com dependências a revisar conforme
o efeito solicitado, licença e versões. SVGO é ferramenta opcional de autoria;
não executar otimização que remova IDs, paths ou viewBox necessários ao exemplo.
Rever interpolação de paths, suporte de navegador e filtros; custo de pintura,
área e complexidade impedem uma promessa genérica de composição por GPU.
Em movimento reduzido, manter o estado final estático visível e semanticamente
apropriado, sem deixar um stroke invisível ou controles sem feedback.

## accessible-animation — inconsistência confirmada e proposta

No SKILL.md original, o reset global declara transition-duration com
`!important`. A regra .card posterior usa transition shorthand sem essa prioridade.
A ordem posterior não vence a declaração importante: o fade de 150ms descrito
na explicação não restaura a duração quando as receitas são combinadas.

Correção mínima proposta, limitada ao exemplo reduzido posterior ao reset:

```css
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: opacity 150ms ease, background-color 150ms ease;
    transition-duration: 150ms, 150ms !important;
  }
  .parallax-layer { transform: none !important; }
  .hero-zoom { animation: none !important; }
}
```

O seletor de classe com duração importante restaura essas duas durações frente
ao reset universal importante apresentado. Isso não certifica outras camadas,
seletores ou animações de um aplicativo. Preferir conteúdo estático legível por
padrão e opt-in de movimento não essencial em no-preference quando adequado.
Reduzir movimento não é remover feedback; um spinner não se torna essencial
apenas pelo nome. Tratar separadamente controles de pausa/parada para movimento
automático, foco/teclado/leitores de tela e necessidades funcionais reais.
Nem a skill nem esse exemplo conferem conformidade WCAG.

O arquivo accessible-animation.proposta.diff contém essa correção e a explicação
de prioridade, com hashes em propostas.json. A aplicação do diff foi conferida
somente em bytes temporários pela função replay_patch existente; não houve
execução de CSS, navegador ou código de fornecedor. Os arquivos originais não
foram modificados.

**Bloqueio:** a infraestrutura registra/reaplica adaptações com hashes e diff,
mas a inclusão nova só gera automaticamente contrato e caminhos README/licença.
A CLI não recebe uma correção arbitrária de receita. Não inserir o diff no
manifesto manualmente nem dispensar a inspeção. A proposta não entra no futuro
pacote sem um caminho de incorporação rastreável explicitamente revisado, ou
uma revisão upstream corrigida autorizada pelo usuário. Não trocar silenciosamente
o commit fixado. accessible-animation permanece bloqueada para aprovação.

## 60fps-animation

Usar para diagnóstico e otimização, não para adicionar efeitos por iniciativa do
bootstrap. O original distingue layout, paint e composite, mostra batching/FLIP
e exige gravação de Performance, paint flashing, frames e verificação real.
Também limita will-change à proximidade da animação e exige sua remoção; proíbe
aplicação indiscriminada e reconhece o custo dos filtros.

Há simplificações no original: “smooth at any frame rate”, execução de transform
sempre no compositor e grid dito compositor-friendly. Não é possível confirmar
essas frases como garantias. Grid pode envolver layout; composição depende de
navegador, conteúdo, área, camadas e hardware. 60/120 FPS são alvos a medir, não
efeito automático de copiar a skill. Não afirmar que este relatório corrigiu
essas frases no fornecedor. Sua aceitação futura exige reconhecer essas ressalvas
e medir o caso real, mantendo a referência ao orçamento do dispositivo-alvo.
