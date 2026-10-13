# Dashboard ScreenDeck

Dashboard web leve para data/hora, clima, Google Calendar, Google Tasks, ar-condicionado Samsung via SmartThings e situação dos backups.

O relógio inclui segundos. O calendário mensal permite navegar entre meses, destaca o dia atual, marca os dias que possuem eventos nas agendas Google conectadas e apresenta abaixo uma lista rolável com data, horário e título dos eventos do mês.

## Segredos

No servidor, crie `secrets/dashboard/` com arquivos `0600`:

- `dashboard-password`: senha de acesso ao painel;
- `google-client.json`: credencial OAuth 2.0 do tipo aplicação Web;
- `smartthings-token`: token pessoal do SmartThings.

Cadastre no Google Cloud o callback `${DASHBOARD_PUBLIC_URL}/oauth/google/callback` e habilite Google Calendar API e Google Tasks API. Nenhum desses arquivos deve entrar no Git.

O clima usa a geocodificação e previsão do Open-Meteo e não exige chave.

O dispositivo SmartThings é escolhido após consultar `/api/smartthings/devices`; seu ID é salvo em `/data/settings.json` como `smartthings_device_id`.

## Cadastro de bancos

O diálogo “Gerenciar bancos” cria, edita, pausa e remove origens de backup. Todos os cadastros usam obrigatoriamente `cyriusBackup` e `/run/secrets/maker-password`; a senha não é enviada ao navegador. O botão “Testar conexão” solicita ao serviço de backup uma consulta somente leitura, mostra versão e latência ou um erro sanitizado e é obrigatório antes de ativar uma origem nova ou alterada. O dashboard valida e grava o TOML compartilhado, e o backup o relê antes de cada rodada. Uma origem ativa precisa ser pausada antes da remoção; relatórios e arquivos existentes são preservados.

## Saúde do servidor

O painel exibe, em blocos com ícones grandes à esquerda dos dados, CPU e quantidade de processadores lógicos, carga, memória total, swap, capacidade total do disco raiz e do volume de backups, uptime e disponibilidade dos dois serviços. A leitura atual é renovada a cada segundo usando somente montagens específicas e somente leitura definidas no Compose. O histórico persistente continua gravando uma amostra por minuto e mantém até 1.440 amostras, equivalentes a 24 horas.

O card de backups consulta o estado a cada segundo. Durante uma execução, ele mostra a origem em processamento, o horário de início, a duração ao vivo e um indicador animado; ao finalizar, volta a apresentar o resultado mais recente.

Quando o resultado mais recente é uma falha, o campo de tamanho é substituído pelo motivo sanitizado registrado pelo serviço de backup, mantendo o card no mesmo tamanho.

Relatórios antigos que contenham apenas o código de saída são enriquecidos, em memória, com a primeira linha útil do log sanitizado. O caminho é validado dentro de `/host/backups/logs`, montado como somente leitura, e o arquivo de status original não é alterado.

O mesmo card mantém uma lista compacta dos cinco backups mais recentes, com origem, resultado, horário e detalhe em tooltip. Os acessos ao histórico completo e ao gerenciamento de bancos usam botões por ícone com rótulos acessíveis.

Agenda e tarefas mostram indicadores animados e acessíveis enquanto os dados Google estão sendo carregados, inclusive durante a navegação entre meses.

Em telas kiosk com pelo menos 900 pixels de largura, o layout ocupa exatamente a altura disponível e não cria rolagem na página. Cartões e listas são compactados conforme a altura para manter todas as áreas visíveis.
