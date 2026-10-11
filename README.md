# ScreenDeck Home

Infraestrutura versionada para um painel residencial baseado em Home Assistant e um serviço independente de backups lógicos.

## Estado

O serviço de backup da Fase 1 está implantado e operacional. O Home Assistant ainda aguarda ativação controlada. Nada adicional deste repositório deve ser implantado ou executado no servidor de produção sem autorização explícita. Consulte `MEMORY.md` para o ponto de retomada e `STATUS.md` para o histórico.

## Regras essenciais

- Não versionar segredos, dumps, logs ou configurações OAuth reais.
- Não executar o Compose na máquina de desenvolvimento.
- Novos acessos ou alterações no servidor exigem escopo e autorização explícitos.
- Revisar `docs/deployment.md` antes de ativar o Home Assistant.

## Validação local permitida

Os testes usam apenas a biblioteca padrão do Python e não acessam rede, bancos ou Docker:

```sh
python3 -m unittest discover -s tests -v
bash scripts/validate-config.sh
```
