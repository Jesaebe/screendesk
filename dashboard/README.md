# Dashboard ScreenDeck

Dashboard web leve para data/hora, clima, Google Calendar, Google Tasks, ar-condicionado Samsung via SmartThings e situação dos backups.

O relógio inclui segundos. O calendário mensal permite navegar entre meses, destaca o dia atual e marca os dias que possuem eventos nas agendas Google conectadas.

## Segredos

No servidor, crie `secrets/dashboard/` com arquivos `0600`:

- `dashboard-password`: senha de acesso ao painel;
- `google-client.json`: credencial OAuth 2.0 do tipo aplicação Web;
- `smartthings-token`: token pessoal do SmartThings.

Cadastre no Google Cloud o callback `${DASHBOARD_PUBLIC_URL}/oauth/google/callback` e habilite Google Calendar API e Google Tasks API. Nenhum desses arquivos deve entrar no Git.

O clima usa a geocodificação e previsão do Open-Meteo e não exige chave.

O dispositivo SmartThings é escolhido após consultar `/api/smartthings/devices`; seu ID é salvo em `/data/settings.json` como `smartthings_device_id`.

## Saúde do servidor

O painel exibe CPU e quantidade de processadores lógicos, carga, memória total, swap, capacidade total do disco raiz e do volume de backups, uptime e disponibilidade dos dois serviços. A leitura atual é renovada a cada segundo usando somente montagens específicas e somente leitura definidas no Compose. O histórico persistente continua gravando uma amostra por minuto e mantém até 1.440 amostras, equivalentes a 24 horas.

Em telas kiosk com pelo menos 900 pixels de largura, o layout ocupa exatamente a altura disponível e não cria rolagem na página. Cartões e listas são compactados conforme a altura para manter todas as áreas visíveis.
