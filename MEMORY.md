# Memória operacional — ScreenDeck Home

## Finalidade

Este arquivo é o ponto de retomada do projeto. Antes de continuar o trabalho, consulte-o para conhecer o estado atual, as decisões vigentes e a próxima etapa. O PRD continua sendo a fonte completa dos requisitos e deve ser relido quando uma tarefa exigir detalhes não registrados aqui, houver dúvida, conflito ou mudança relevante de escopo.

## Estado atual

- O `PRD_ScreenDeck_Home.md` foi lido integralmente.
- A fundação local da Fase 1 foi implementada em 09/10/2026.
- Foram criados os arquivos raiz de governança, exemplo de ambiente e Compose declarativo.
- Foram adicionados documentação, runbooks, esqueleto do Home Assistant, contrato inicial do serviço de backup, monitoramento pendente de decisão, scripts protegidos e testes locais.
- O entrypoint funcional do backup carrega as origens, monta o pipeline real e executa o agendador contínuo. Maker continua deliberadamente com `enabled = false`, portanto nenhum dump é executado antes do teste controlado.
- A imagem de backup foi construída no servidor e somente o container `screendeck-home-backup-1` está em execução, saudável, como UID/GID `1000:1000`. Todas as origens permanecem desabilitadas; não houve dump, upload ou criação de relatórios. O Home Assistant continua desligado.
- O primeiro pipeline real completo do Maker foi aprovado: dump de 12.433.797 bytes, upload pelo remote criptografado, retenção cloud, download de validação, SHA-256 idêntico e catálogo `pg_restore` válido. Maker retornou para `enabled = false`.
- A renovação OAuth foi validada após montar o diretório dedicado `/home/cyrius/.config/rclone` em `/run/rclone`: a listagem cloud terminou sem stderr, o diretório contém somente `rclone.conf` e o arquivo permanece em modo `0600`. Os demais segredos continuam somente leitura.
- Maker está permanentemente habilitado desde 10/10/2026, com agenda às 00:00, 06:00, 12:00 e 18:00 em `America/Bahia` e retenção cloud de 15 dias. O container permaneceu saudável após a ativação.
- A agenda é definida por origem no campo `schedule`; bancos futuros podem usar frequências diferentes. Após editar o TOML real, deve-se validá-lo e reiniciar somente o serviço `backup`.
- O canal SMTP Gmail foi ativado e testado em 10/10/2026, usando provisoriamente `jesaebe@gmail.com` como remetente e destinatário: senha de app em arquivo `0600`, STARTTLS e autenticação aprovados, e-mail sintético recebido na caixa de entrada e container saudável. Nenhuma senha foi exibida ou colocada no `.env`.
- Cinquenta e oito testes unitários passaram, cobrindo configuração, entrypoint, comandos de dump sem senha, relatórios, retenção, agendamento, notificações e sanitização.
- `scripts/validate-config.sh` passou, incluindo a verificação de nomes de arquivos secretos versionados.
- A primeira origem foi modelada: `Maker`, PostgreSQL 14, host `151.243.236.61`, porta 5433, banco `janus`, aproximadamente 15 MB, sem SSL e agenda diária às 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.
- Maker permanece com `enabled = false`. O usuário exclusivo `cyriusBackup` foi criado e um `pg_dump` de validação funcionou, conforme confirmação do usuário em 10/10/2026. A senha foi instalada no servidor como arquivo protegido, e o `sources.toml` real e o remote `crypt` estão preparados; a habilitação ainda depende do entrypoint funcional e de um teste controlado.
- Google Drive definido para backups: conta `jesaebe@gmail.com`, pasta `CyriusBackups` diretamente na raiz do Drive, remote base `gdrive` e remote criptografado `gdrive-crypt`. Ambos foram criados e testados pelo usuário no servidor definitivo em 10/10/2026; o `crypt` grava dentro de `CyriusBackups` com nomes ilegíveis. O `rclone.conf` permanece somente em `/home/cyrius/.config/rclone/rclone.conf` nesse servidor e será montado no container como somente leitura. O teste de ida e volta foi concluído nele: uma pasta foi enviada criptografada e restaurada com nomes e conteúdo legíveis pelo `gdrive-crypt`.
- O executor local foi implementado com trava por origem, arquivo parcial, validação não vazia, promoção atômica, logs sanitizados e relatórios `latest.json`/`history.jsonl`.
- O executor externo é injetável; todos os testes usam simulação. Agendamento, upload cloud e notificações estão conectados pelo entrypoint, mas nenhuma origem real está habilitada.
- A retenção local foi integrada ao executor: inicia em 85%, busca retornar a 75%, preserva o último backup de cada origem e recusa o dump se a margem não puder ser restaurada.
- A reserva prévia inicial é o maior valor entre duas vezes o tamanho estimado e 64 MiB.
- Travas com mais de seis horas e PID inexistente são apenas classificadas como candidatas a obsoletas; não há remoção automática.
- O adaptador cloud simulado constrói upload por `rclone copyto` e retenção por `rclone delete --min-age 15d`, sempre limitado ao diretório da origem.
- O remote real `gdrive-crypt` foi validado pelo usuário no servidor definitivo: envio, listagem e restauração funcionaram, e nomes/conteúdo permanecem criptografados dentro de `CyriusBackups` quando vistos pelo remote base. O arquivo está em `/home/cyrius/.config/rclone/rclone.conf`, pertence a `cyrius:cyrius`, tem modo `0600` e será montado no container como somente leitura; não é necessário copiá-lo para a máquina de desenvolvimento.
- O pipeline simulado integra dump, upload e retenção cloud, preserva o dump local em falhas cloud e publica um único relatório final com duração total.
- O agendador interpreta o fuso de cada origem, evita repetição no mesmo minuto enquanto o processo está ativo e transforma senha ausente ou exceção inesperada em relatório e alerta.
- O adaptador SMTP usa STARTTLS e foi validado apenas com cliente falso. Nenhum e-mail foi enviado.
- O laço contínuo existe, porém não está conectado ao entrypoint e não foi iniciado.
- A deduplicação do agendador persiste atomicamente entre reinícios e mantém somente os 512 slots mais recentes.
- Falhas do canal SMTP são registradas em estado separado, sem substituir o resultado do backup ou interromper o ciclo.
- Senhas de bancos são referenciadas por `password_file` abaixo de `/run/secrets`, não por variáveis de ambiente. Para Maker, o host deverá manter `/home/cyrius/.config/screendeck-home/maker-password` com modo `0600`; o Compose o monta somente para leitura e o agendador trata arquivo ausente ou vazio como falha de configuração.
- Tablet inventariado por SSH somente leitura: Debian 12 i386, Cinnamon/X11, `1920x1200` horizontal, usuário `painel` com autologin, Chromium ausente e aproximadamente 19 GiB livres.
- Não há autostart persistente do kiosk. A sessão bloqueia após 900 segundos e desliga a tela em AC após 1800 segundos.
- A configuração desejada é Chromium após o autologin, tela sempre ativa e recuperação automática do navegador. Nenhuma mudança foi aplicada ao tablet.
- Artefatos locais do kiosk foram preparados em `tablet/`: launcher resiliente, autostart Cinnamon, instalador protegido, captura de preferências e rollback direcionado.
- A URL do Home Assistant é obrigatória em tempo de instalação e não está fixada no launcher.
- Servidor Ubuntu: `192.168.25.249`. URL LAN planejada do Home Assistant: `http://192.168.25.249:8123`, pendente de confirmar a porta.
- Endpoint SSH externo confirmado em 10/10/2026: `45.225.13.12`, porta `1522`, usuário `cyrius`; o host se identifica como `cyrius`. O endereço LAN `192.168.25.249` continua sendo o destino local do Home Assistant.
- Repositório Git configurado em `https://github.com/Jesaebe/screendesk.git`; o projeto foi clonado em `/home/cyrius/screendeck-home` no servidor, inicialmente no commit `d539366`, sem segredos e sem iniciar infraestrutura.
- A desativação das aplicações Docker antigas foi executada pelo usuário em 10/10/2026 conforme o plano documentado.
- A validação posterior mostrou zero containers, imagens, volumes locais e cache de build; restaram somente as redes padrão `bridge`, `host` e `none`.
- Porta 8123 está livre. Docker, Nginx/80 e Zabbix/10050 permaneceram ativos; SSH/22 também permaneceu disponível.
- A raiz caiu de 84% para 10% de uso, com 84 GB disponíveis após a limpeza.
- `/srv/backups` tem aproximadamente 93 GB disponíveis e foi atribuído a `cyrius:cyrius` (UID/GID `1000:1000`), modo `0755`, atendendo ao contrato de escrita do container não-root.
- Maker foi confirmado como banco externo em outro servidor; não corresponde ao PostgreSQL 11 local do Cartório.
- Foram descartados os dados de Rifa, Cartório, HML, PRD FEJJB e Jiu-Jitsu System, além de imagens, volumes anônimos, diretórios antigos e cache de build.
- Nenhum pacote foi instalado.
- Nenhum serviço ou container do ScreenDeck foi iniciado.
- Não houve acesso SSH nem alteração no servidor Ubuntu de produção.
- Não houve alteração fora desta pasta do projeto.
- A referência isolada à AWS na seção de segurança do PRD foi removida. O destino cloud aprovado é Google Drive, com criptografia via rclone ou solução equivalente.
- A pré-checagem de implantação `scripts/preflight-deploy.sh` foi aprovada integralmente no servidor em 10/10/2026. O usuário `cyrius` foi adicionado ao grupo `docker` após autorização explícita; host, Docker/Compose, porta 8123, segredos, `/srv/backups` e Compose foram validados sem iniciar containers.
- Os documentos de inventário e implantação foram atualizados para refletir a desativação Docker já concluída. `deploy.sh` e `rollback.sh` continuam deliberadamente bloqueados e sem ações de infraestrutura.

## Restrições permanentes desta etapa

- Desenvolver e preparar todos os artefatos somente nesta máquina e dentro deste repositório.
- Não instalar pacotes globais nem modificar configurações do sistema local.
- Não executar Docker, containers ou serviços do projeto na máquina local.
- Tratar o servidor Ubuntu como produção.
- Antes de autorização explícita para implantação, qualquer SSH deve ser somente leitura e para diagnóstico não destrutivo.
- Não criar, editar ou excluir arquivos, serviços, containers, credenciais, agendamentos ou regras de firewall no servidor sem autorização explícita.
- Nunca versionar senhas, tokens, chaves, arquivos `.env`, dumps ou outros segredos.
- Ao finalizar uma etapa ou precisar de interação do usuário, executar `scripts/notify-user.sh`. O aviso usa o bell do terminal e pode ser silencioso se o cliente desabilitar sons.

## Decisões vigentes

- Interface e automação: Home Assistant Container.
- Orquestração futura no servidor: Docker Compose.
- Cliente: Chromium em modo kiosk no tablet Debian 12 i686.
- Calendário e tarefas: integrações Google Calendar e Google Tasks por OAuth.
- Backup: dumps lógicos com ferramentas nativas de PostgreSQL e MySQL/MariaDB.
- Armazenamento local futuro: `/srv/backups`.
- Nuvem: Google Drive com conteúdo criptografado antes do envio.
- Retenção cloud inicial: 15 dias.
- Limpeza local inicial: iniciar com 85% de uso e limpar até 75%, preservando espaço para o próximo dump.
- Segredos: arquivos locais ignorados pelo Git e um `.env.example` sem valores reais.
- O monitoramento deve representar o host real, não apenas métricas internas dos containers; a solução exata ainda será definida.

## Estrutura local planejada

A Fase 1 deverá preparar, sem executar a infraestrutura:

- arquivos raiz: `README.md`, `STATUS.md`, `.gitignore`, `.editorconfig`, `.env.example` e `compose.yaml`;
- `docs/` para arquitetura, decisões, segurança, inventário, implantação, rollback, tablet e runbooks;
- `home-assistant/` para configuração, dashboard, temas, automações e packages;
- `backup/` para Dockerfile, configuração de exemplo, código do serviço e modelos de notificação;
- `monitoring/` para desenho das métricas e alertas;
- `scripts/` para validação, inventário somente leitura, implantação, rollback e restauração;
- `tests/` para testes unitários, retenção, relatórios, erros e proteção de segredos.

## Próxima etapa autorizável

Fechar o desenho funcional antes de habilitar o serviço de backup:

1. confirmar SMTP, destinatários, calendários/listas Google e marca/modelo do ar-condicionado;
2. definir a solução de monitoramento do host e seus limiares;
3. acompanhar a primeira execução automática do Maker e confirmar o novo objeto cloud;
4. acompanhar a primeira execução automática do Maker;
5. preparar a implantação controlada do restante da solução agora que a pré-checagem e o pipeline de backup estão aprovados;
6. instalar/configurar o tablet somente com autorização explícita posterior.

Não há autorização para SSH, implantação ou execução de containers.

## Pendências de levantamento

- Bancos a copiar: tipos, hosts, portas, tamanhos e janelas permitidas.
- Conta e pasta do Google Drive.
- Marca, modelo e método de controle do ar-condicionado.
- Resolução, orientação e comportamento de tela do tablet.
- Calendários e listas do Google Tasks que aparecerão.
- Frequência final dos backups.
- Conta SMTP e destinatários dos alertas.
- Limiares finais de CPU, memória e armazenamento.
- Portas e serviços já existentes no servidor, a levantar futuramente por diagnóstico somente leitura.

## Regra de atualização

Ao concluir cada etapa, atualizar este arquivo com o que mudou, validações feitas, decisões novas, pendências e a próxima ação concreta. Se a memória divergir do PRD, uma decisão explícita mais recente deve ser registrada nos dois arquivos; caso contrário, prevalece o PRD.

## Última validação

- Data: 10/10/2026.
- Comando: `python3 -m unittest discover -s tests -v`.
- Resultado: 58 testes aprovados; entrypoint funcional, pipeline, scripts de implantação e tablet validados.
- Comando: `bash scripts/validate-config.sh`.
- Resultado: aprovado.
- Infraestrutura do ScreenDeck executada: nenhuma. Ambiente Docker antigo removido pelo usuário em 10/10/2026 e validado vazio.
