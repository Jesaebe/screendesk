# Tablet em modo kiosk

## Inventário somente leitura — 09/10/2026

- Endereço LAN: `192.168.25.47/24` em `wlan0`.
- Hostname atual: `jesaweb`.
- Sistema: Debian 12 Bookworm, kernel `6.1.0-52-686-pae`.
- Arquitetura de pacotes: `i386`.
- Ambiente gráfico: Cinnamon sobre X11, inicializado por `graphical.target`.
- Usuário da sessão: `painel`, UID 1001.
- LightDM já possui login automático de `painel`, sem espera.
- Tela interna: `DSI-1`, resolução ativa `1920x1200` a 60 Hz.
- Orientação: horizontal normal.
- Memória: 1,9 GiB; aproximadamente 702 MiB disponíveis durante o levantamento.
- Swap: 975 MiB; 257 MiB em uso durante o levantamento.
- Raiz: 28 GiB, 7,3 GiB usados e 19 GiB disponíveis.
- Chromium: não instalado; pacote i386 disponível nos repositórios Debian configurados.
- Diretório `~/.config/autostart`: sem lançador local encontrado.
- Crontab do usuário: vazio.
- Nenhum serviço systemd de usuário específico para kiosk foi encontrado.
- Firefox ESR estava em modo kiosk, mas foi iniciado manualmente por outra sessão SSH e não representa autostart persistente.
- Bloqueio de tela Cinnamon: habilitado.
- Inatividade da sessão: 900 segundos.
- Desligamento da tela em alimentação AC: 1800 segundos.
- `xinput` não está instalado; a validação touch deverá ser presencial ou usar outra interface já disponível.

Nenhuma configuração foi alterada durante o levantamento.

## Estado desejado

- Instalar Chromium pelo repositório oficial do Debian.
- Iniciar o Chromium após o login automático do usuário `painel`.
- Usar modo kiosk apontando para a URL LAN do Home Assistant.
- Manter resolução `1920x1200` e orientação horizontal.
- Desabilitar bloqueio, suspensão e desligamento automático da tela somente para a sessão dedicada `painel`.
- Reiniciar o navegador automaticamente se ele encerrar inesperadamente.
- Não armazenar credenciais do Home Assistant na linha de comando ou no arquivo `.desktop`.
- URL LAN planejada: `http://192.168.25.249:8123`, condicionada à confirmação de que a porta está livre no servidor.

## Implantação futura

A instalação e as mudanças de sessão exigem autorização explícita. Antes de aplicar:

1. definir URL ou hostname LAN definitivo do Home Assistant;
2. registrar os valores atuais do Cinnamon para rollback;
3. instalar Chromium sem pacotes externos ou globais;
4. criar launcher versionado e específico do usuário;
5. alterar energia/bloqueio somente na sessão `painel`;
6. reiniciar a sessão de forma controlada;
7. validar touch, kiosk, recuperação do navegador e permanência da tela;
8. documentar comandos e resultados no `STATUS.md`.

Os artefatos locais estão em `tablet/`. `install.sh` exige confirmação literal, arquitetura i386, usuário `painel` e URL HTTP(S). O launcher reinicia o Chromium cinco segundos após uma saída inesperada. `rollback.sh` restaura as preferências capturadas e não desinstala Chromium.
