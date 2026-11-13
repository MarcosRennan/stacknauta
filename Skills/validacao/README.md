# validacao

Biblioteca preparada na Etapa 1.5. Nenhuma skill ativada.

| Skill | Status | Pacote ou impedimento |
|---|---|---|

Diretório reservado às ferramentas e evidências da biblioteca; os pacotes de consumo estão nas quatro categorias de domínio.

Para conferir todas as cópias físicas e a sintaxe JS sem executar os scripts de
busca do fornecedor:

```sh
Automacao/python-global Skills/validacao/validar_biblioteca.py --copias --sintaxe-node --sem-smoke-fornecedor
```

`--sem-smoke-fornecedor` conserva as verificações de hashes, referências, licenças,
cópia e casos adversariais. Só omite os três smoke tests executáveis UI/UX; o JSON
registra `ui_smoke_tests_status: not_requested` e `vendor_code_executed: false`.
Sem a opção, o comportamento histórico de `--copias` é preservado.
O runner `Automacao/validacao-correcoes-funcionais/executar_testes.py` aceita a
mesma opção para sua validação final em clone com origin preservado.
