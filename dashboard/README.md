# Dashboard ScreenDeck

Dashboard web leve para data/hora, clima, Google Calendar, Google Tasks, ar-condicionado Samsung via SmartThings e situação dos backups.

## Segredos

No servidor, crie `secrets/dashboard/` com arquivos `0600`:

- `dashboard-password`: senha de acesso ao painel;
- `google-client.json`: credencial OAuth 2.0 do tipo aplicação Web;
- `smartthings-token`: token pessoal do SmartThings.

Cadastre no Google Cloud o callback `${DASHBOARD_PUBLIC_URL}/oauth/google/callback` e habilite Google Calendar API e Google Tasks API. Nenhum desses arquivos deve entrar no Git.

O clima usa a geocodificação e previsão do Open-Meteo e não exige chave.

O dispositivo SmartThings é escolhido após consultar `/api/smartthings/devices`; seu ID é salvo em `/data/settings.json` como `smartthings_device_id`.
