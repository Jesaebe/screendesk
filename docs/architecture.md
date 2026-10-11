# Arquitetura

O tablet Debian atua somente como cliente Chromium em modo kiosk. O servidor Ubuntu já executa o serviço independente de backup descrito por `compose.yaml`; o Home Assistant é a próxima ativação controlada.

## Fluxos

1. O tablet acessa o Home Assistant exclusivamente pela LAN.
2. O Home Assistant consome o resumo somente leitura publicado no volume `backup-status`.
3. O serviço de backup gera dumps lógicos em `/srv/backups`, registra o resultado e envia uma cópia criptografada ao Google Drive.
4. Falhas produzem estado para alerta persistente no Home Assistant e, quando configurado, e-mail SMTP.

## Limites

- Credenciais ficam fora do Git e são montadas como arquivos somente leitura ou fornecidas pelo ambiente.
- Bancos remotos não são expostos pelo Compose.
- O monitoramento correto do host ainda será decidido após inventário; métricas internas de containers não substituem métricas do Ubuntu.
- Não haverá publicação direta na internet nem abertura de portas no roteador nesta fase.

## Endereçamento planejado

- Servidor Ubuntu: `192.168.25.249`.
- Home Assistant: `http://192.168.25.249:8123`.
- Tablet: `192.168.25.47`.

A porta 8123 foi confirmada livre pelo inventário e pela pré-checagem do servidor.
