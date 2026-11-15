# Validação após preparar o ambiente

[README](../README.md) · [Linux](INSTALACAO-LINUX.md) · [Uso](PRIMEIROS-PASSOS.md) · [Problemas](SOLUCAO-DE-PROBLEMAS.md)

Execute da raiz de uma cópia confiável, com Python/Node globais asdf instalados.
Não requer rede, instalação de dependências, login de agente ou cache de origens.
Guarde os resultados fora do consumidor e dos arquivos versionados.

## 1. Ambiente, revisão e arquivos

```bash
pwd -P
git rev-parse HEAD
git status --short
git diff --check
asdf --version
asdf current
test -f AGENTS.md
test -f .agents/skills/project-bootstrap/SKILL.md
test -f Skills/catalogo.json
test -f Skills/fontes.lock.json
test -x Automacao/project-bootstrap/project-bootstrap
test -x Automacao/python-global
test -x Automacao/manutencao-skills/skills
./Automacao/project-bootstrap/project-bootstrap --help
./Automacao/project-bootstrap/project-bootstrap agent-plan --help
./Automacao/project-bootstrap/project-bootstrap agent-apply --help
./Automacao/project-bootstrap/project-bootstrap agent-verify --help
```

A instalação deve ser acessível ao usuário. Git preserva o bit de execução, não
todos os bits de permissão: launchers 0744 no checkout original apareceram como
0755 no clone local. Confira permissões efetivas e propriedade; não se certifica
compartilhamento de um checkout por vários usuários. Os testes verificam o filesystem
real; testes/ajudas isoladas não provam todos os pré-requisitos de um consumidor.

## 2. Biblioteca e catálogo offline

```bash
STACKNAUTA_VALIDACAO="$(mktemp -d -t stacknauta-validacao-XXXXXX)"
bash Automacao/python-global Skills/validacao/validar_biblioteca.py --copias --sintaxe-node --sem-smoke-fornecedor > "$STACKNAUTA_VALIDACAO/biblioteca.json"
cat "$STACKNAUTA_VALIDACAO/biblioteca.json"
# Confira primeiro que asdf current python resolve HOME/.tool-versions.
asdf exec python -B Skills/validacao/validar_catalogo.py > "$STACKNAUTA_VALIDACAO/catalogo.json"
cat "$STACKNAUTA_VALIDACAO/catalogo.json"
```

O catálogo delega ao validador atual. Sua invocação preserva o diretório do script
para um import local; o launcher isolado -I não resolve esse import entre scripts.
`asdf exec` só é válido aqui com a resolução global confirmada, sem fallback.
Não é necessário pip, PyYAML ou outra biblioteca adicional.

Esperado para esta revisão: `passed_with_documented_pending`, erros vazios e
105 aprovadas/27 pendentes/duas excluídas/nove origens/onze pacotes. Esse status
mantém as pendências de workflows; não é certificação de produção. A opção
sem-smoke-fornecedor confere cópias sem executar buscas/scripts do fornecedor;
`node --check` faz parsing, não executa a aplicação ou resolve todos os imports.
Não use --origens para consumo: essa opção consulta caches de aquisição.

## 3. Regressão automatizada

As quatro suítes usam unittest e fixtures temporárias; não instalam runtimes ou
executam outros agentes. Go/JVM/Rust têm casos sintéticos, não uma validação de
seus SDKs nesta máquina. A baseline da 2H tem **303 casos**:

```bash
bash Automacao/python-global Automacao/validacao-project-bootstrap/executar_testes.py --report "$STACKNAUTA_VALIDACAO/nucleo.json"
bash Automacao/python-global Automacao/validacao-integracao-agentes/executar_testes.py --report "$STACKNAUTA_VALIDACAO/integracao.json"
bash Automacao/python-global Automacao/validacao-atualizacoes/executar_testes.py --report "$STACKNAUTA_VALIDACAO/atualizacoes.json"
bash Automacao/python-global Automacao/validacao-inclusoes/executar_testes.py --report "$STACKNAUTA_VALIDACAO/inclusoes.json"
```

Verifique status, tests_run, failures, errors e skipped em cada relatório; não
conte testes como aprovados somente porque começaram. Estes testes cobrem o
mesmo código compartilhado para os três ambientes, sem iniciar suas sessões.

O runner agregado abaixo cria seu próprio clone e **exige commit e árvore limpa**:

```bash
bash Automacao/python-global Automacao/validacao-correcoes-funcionais/executar_testes.py --report "$STACKNAUTA_VALIDACAO/regressao-clone.json" --sem-smoke-fornecedor
```

Se há alterações em revisão, não faça commit nem limpeza só para satisfazê-lo.
Use as suítes componentes sobre um snapshot isolado claramente identificado.
O runner não é um instalador, e seu clone local não testa acesso ao GitHub.

## 4. Consumidor e descoberta

Execute o [exemplo completo](PRIMEIROS-PASSOS.md) para planejar, inspecionar,
autorizar, aplicar e verificar um destino novo. Confirme verified/intact,
AGENTS, contrato, duas skills, recursos físicos/links relativos, manifests e locks.
Não deve haver GEMINI.md, dependências instaladas ou implementação frontend.

Só uma sessão manual do cliente comprova catálogo, seleção e leitura de skills.
Se não foi autorizada/executada, registre descoberta comportamental como não
verificada nessa instalação. Os resultados aceitos da 4B não substituem esse teste
em outra máquina. Não execute agentes recursivamente durante a regressão.

## 5. O que foi e o que não pode ser comprovado localmente

| Procedimento | Evidência possível nesta 4C |
|---|---|
| CLI, contratos e requisitos | Inspeção do código e ajuda real |
| Pacotes, recursos e permissões | Clone local limpo, hashes e validadores |
| Uso sem _repos ou relatórios ignorados | Bootstrap oficial no clone sem esses diretórios |
| Novos documentos ainda não commitados | Overlay documental exato no clone; links e shell revisados nesse estado |
| Regressão dos agentes | Suítes compartilhadas; nenhuma sessão nova |
| Destino e publicação segura | Consumidor sintético e verificador no filesystem local |
| Instalação Fedora/asdf/agentes | Documentação oficial; provisionamento real não executado |
| GitHub SSH, modelos e autenticação | Dependem de rede, publicação, contas e acesso; pendentes |
| Outro Linux/CPU/filesystem | Requer instalação real; não certificado por esta simulação |

Uma instalação apta exige resultados reais, runtimes acessíveis também no sandbox
e decisões do usuário sobre pendências da aplicação. Falhas devem ser preservadas
e diagnosticadas; não modifique o código ou a biblioteca para validar a documentação.
