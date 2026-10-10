# ScreenDeck Home

Infraestrutura versionada para um painel residencial baseado em Home Assistant e um serviço independente de backups lógicos.

## Estado

A Fase 1 prepara artefatos locais e testes de lógica. Nada deste repositório deve ser implantado ou executado no servidor de produção sem autorização explícita. Consulte `MEMORY.md` para o ponto de retomada e `STATUS.md` para o histórico.

## Regras essenciais

- Não versionar segredos, dumps, logs ou configurações OAuth reais.
- Não executar o Compose na máquina de desenvolvimento.
- SSH no servidor é somente leitura até autorização de implantação.
- Revisar `docs/deployment.md` e concluir `docs/server-inventory.md` antes de implantar.

## Validação local permitida

Os testes usam apenas a biblioteca padrão do Python e não acessam rede, bancos ou Docker:

```sh
python3 -m unittest discover -s tests -v
bash scripts/validate-config.sh
```
