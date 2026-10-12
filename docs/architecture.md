# Arquitetura

O tablet Debian atua somente como cliente Chromium em modo kiosk. O servidor Ubuntu executa o serviço independente de backup e hospedará um dashboard web customizado e pequeno.

## Fluxos

1. O tablet acessa o dashboard pelo Nginx.
2. O dashboard consome o resumo somente leitura publicado no volume `backup-status`.
3. O serviço de backup gera dumps lógicos em `/srv/backups`, registra o resultado e envia uma cópia criptografada ao Google Drive.
4. O dashboard consulta Open-Meteo, Google Calendar, Google Tasks e SmartThings sem armazenar senhas das contas.
5. Falhas de backup aparecem no painel e geram e-mail SMTP.
6. O dashboard coleta métricas agregadas do Ubuntu por arquivos específicos de `/proc` e pontos de montagem somente leitura; o backup publica um heartbeat no volume de status.

## Limites

- Credenciais ficam fora do Git e são montadas como arquivos somente leitura ou fornecidas pelo ambiente.
- Bancos remotos não são expostos pelo Compose.
- O monitoramento lê métricas do host, não métricas internas do container, e não recebe acesso ao socket Docker.
- Não haverá publicação direta na internet nem abertura de portas no roteador nesta fase.

## Endereçamento planejado

- Servidor Ubuntu: `192.168.25.249`.
- Dashboard: `http://192.168.25.249:8123` internamente, publicado pelo Nginx.
- Tablet: `192.168.25.47`.

A porta 8123 é preservada durante a substituição para evitar mudanças no Nginx.
