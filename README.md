# ScreenDeck Home

Infraestrutura versionada para um painel web residencial customizado e um serviço independente de backups lógicos.

## Estado

O serviço de backup está implantado e operacional. O dashboard customizado que substituirá o Home Assistant está em preparação local e ainda não foi implantado. Nada adicional deve ser implantado no servidor sem autorização explícita. Consulte `MEMORY.md` e `STATUS.md`.

## Regras essenciais

- Não versionar segredos, dumps, logs ou configurações OAuth reais.
- Não executar o Compose na máquina de desenvolvimento.
- Novos acessos ou alterações no servidor exigem escopo e autorização explícitos.
- Revisar `docs/deployment.md` antes de substituir o Home Assistant pelo dashboard.

## Validação local permitida

Os testes usam apenas a biblioteca padrão do Python e não acessam rede, bancos ou Docker:

```sh
python3 -m unittest discover -s tests -v
bash scripts/validate-config.sh
```
