# Status — ScreenDeck Home

## 2026-10-10 — Acesso SSH externo confirmado

- Confirmado acesso ao servidor por `cyrius@45.225.13.12`, porta `1522`, usando autenticação não interativa já configurada.
- O host remoto se identifica como `cyrius`; o usuário operacional permanece UID/GID `1000:1000`.
- O `rclone.conf` continua presente com proprietário `cyrius:cyrius` e modo `0600`.
- `/srv/backups` continua `root:root` modo `0755` e ainda não atende ao contrato de escrita do container.
- O diretório novo `/home/cyrius/screendeck-home` não existia antes da tentativa de transferência; a estratégia foi alterada pelo usuário para distribuição via Git.
- Nenhum container ou serviço foi iniciado.

## 2026-10-10 — Segredo do Maker preparado como arquivo protegido

- O contrato deixou de transportar a senha do banco por variável de ambiente e passou a usar um arquivo exclusivo abaixo de `/run/secrets`.
- O Compose monta `/home/cyrius/.config/screendeck-home/maker-password` como `/run/secrets/maker-password`, somente leitura, sem incluir o valor no `.env`, no `sources.toml` ou nos argumentos do processo.
- O agendador lê o segredo somente no momento da execução, remove apenas a quebra de linha final e mantém sanitização de erros; arquivo ausente ou vazio resulta em `configuration_failed`.
- A pré-checagem passou a exigir o arquivo real e permissão `0600` ou mais restritiva, sem ler seu conteúdo.
- Foi adicionado um runbook de captura interativa sem eco nem histórico do shell; `secrets/` inteiro passou a ser ignorado pelo Git.
- Maker continua desabilitado e nenhum arquivo, segredo ou serviço foi alterado no servidor.
- Validação local: 52 testes aprovados, sintaxe Bash aprovada, validação de configuração aprovada e diff sem erros de whitespace.
- Próximo passo: mediante autorização explícita, instalar interativamente o segredo no servidor, preparar `secrets/sources.toml` ainda com Maker desabilitado e executar a pré-checagem somente leitura.

## 2026-10-10 — rclone.conf do servidor integrado ao Compose

- Confirmado por inspeção SSH somente leitura o arquivo já validado em `/home/cyrius/.config/rclone/rclone.conf`, pertencente a `cyrius:cyrius` e com modo `0600` no servidor definitivo.
- Confirmados sem revelar a configuração os remotes `gdrive` e `gdrive-crypt` no arquivo definitivo.
- O Compose passou a montar esse arquivo diretamente em `/run/secrets/rclone.conf`, somente leitura, sem refazer OAuth, recriar remotes ou copiar o segredo para o repositório.
- Como o arquivo `0600` pertence ao UID/GID `1000:1000`, o serviço de backup foi alinhado a esse mesmo usuário não-root; o servidor não possui ferramentas ACL instaladas e nenhuma permissão do segredo foi afrouxada.
- A configuração versionável das origens passou a ter montagem separada, evitando expor todo um diretório de segredos ao container.
- A pré-checagem valida existência e permissões do arquivo real no servidor sem ler seu conteúdo.
- Validação local: sintaxe Bash aprovada, 51 testes aprovados e `scripts/validate-config.sh` aprovado; nenhum acesso ou alteração foi feito no servidor.
- Próximo passo: instalar a senha de `cyriusBackup` como segredo protegido e preparar `sources.toml` no servidor antes de habilitar Maker.

## 2026-10-10 — Remotes rclone validados

- Os remotes `gdrive` e `gdrive-crypt` foram criados e testados pelo usuário.
- A configuração e os testes foram realizados no servidor definitivo; o `rclone.conf` permanece em `/home/cyrius/.config/rclone/rclone.conf` e não precisa ser copiado para a máquina de desenvolvimento.
- A pasta correta é `CyriusBackups`, com maiúsculas, diretamente na raiz do Google Drive.
- O remote criptografado grava dentro dessa pasta com nomes ilegíveis, conforme esperado.
- O usuário concluiu um teste de restauração: enviou uma pasta pelo remote criptografado e recuperou nomes e conteúdo originais por meio do `gdrive-crypt`.
- O remote base `gdrive` representa a raiz do Drive; portanto, caminhos informados depois de `gdrive:` são relativos à raiz e podem criar novas pastas.
- Nenhum token, senha ou conteúdo do `rclone.conf` foi registrado no repositório.
- Próximo passo: confirmar no servidor apenas o caminho e as permissões do `rclone.conf` já validado e instalar a senha de `cyriusBackup` como segredo protegido.

## 2026-10-10 — Destino Google Drive definido

- Conta aprovada: `jesaebe@gmail.com`.
- Pasta dedicada: `CyriusBackups`, diretamente na raiz do Drive.
- Planejados os remotes `gdrive` e `gdrive-crypt`, com a pasta aprovada como raiz visível e nomes/conteúdo abaixo dela criptografados.
- Adicionado runbook de OAuth, proteção do `rclone.conf` e teste de ida e volta sem dados sensíveis.
- Esta entrada registrava o planejamento inicial; a criação e a validação posteriores estão documentadas acima.

## 2026-10-10 — Conta de backup do Maker validada

- O usuário confirmou a criação bem-sucedida de `cyriusBackup` no PostgreSQL Maker.
- A autenticação e o `pg_dump` de validação também funcionaram.
- A origem permanece desabilitada até a senha ser instalada como segredo protegido no servidor e o remote `crypt` do Google Drive ser validado.
- Nenhuma senha foi recebida ou registrada no repositório.
- Próximo passo: definir a conta e a pasta do Google Drive para preparar a configuração criptografada do rclone.

## 2026-10-10 — Usuário de backup do Maker definido

- Nome escolhido: `cyriusBackup`, preservando maiúsculas e portanto citado em SQL como `"cyriusBackup"`.
- A configuração de exemplo deixou de usar o superusuário `postgres`, mas a origem continua desabilitada até criação e teste reais.
- Adicionado runbook SQL com `LOGIN`, sem privilégios administrativos, acesso ao banco `janus` e leitura dos schemas, tabelas e sequências existentes.
- Nenhuma senha foi criada ou registrada; o runbook orienta definição interativa pelo `psql`.
- Próximo passo: executar o runbook com acesso administrativo ao PostgreSQL Maker e validar `pg_dump`, mediante autorização e disponibilidade do acesso.

## 2026-10-10 — Pré-checagem de implantação preparada

- Adicionado `scripts/preflight-deploy.sh`, estritamente somente leitura, para validar o host esperado, Ubuntu, Docker/Compose, porta 8123, armazenamento, segredos, permissões e Compose antes do deploy.
- A escrita em `/srv/backups` é validada pelo contrato real do container: proprietário UID 10001 e permissão de escrita para o dono.
- Inventário e documentação de implantação foram sincronizados com a desativação Docker já concluída pelo usuário.
- `deploy.sh` e `rollback.sh` permanecem bloqueados e não executam mudanças; implantação continua sem autorização.
- Validação local: sintaxe Bash aprovada, 50 testes aprovados e `scripts/validate-config.sh` aprovado.
- Próximo passo: obter as definições funcionais e credenciais pendentes (usuário exclusivo de Maker, remote `crypt`, SMTP e integrações) antes de ligar o entrypoint real e preparar o deploy executável.

## 2026-10-10 — Desativação Docker concluída pelo usuário

- O usuário executou a remoção planejada das aplicações Docker antigas, seus dados, imagens, redes, volumes, diretórios e cache de build.
- Validação informada após a remoção: zero containers, imagens, volumes locais e cache de build.
- Permaneceram somente as redes padrão `bridge`, `host` e `none`.
- A raiz passou de 84% para 10% de uso, com 84 GB disponíveis.
- `/srv/backups` permanece com 1% de uso e 93 GB disponíveis.
- Docker, Nginx e Zabbix Agent 2 foram confirmados como ativos.
- SSH/22, Nginx/80 e Zabbix/10050 continuam escutando; a porta 8123 permanece livre.
- Próximo passo: fechar credenciais e parâmetros pendentes e preparar a implantação controlada do ScreenDeck.

## 2026-10-09 — Decisão preliminar de desativação Docker

- Maker confirmado como banco externo, sem relação com o PostgreSQL local do Cartório.
- Usuário confirmou descarte dos dados de Rifa, Cartório, HML, PRD FEJJB e Jiu-Jitsu System.
- Limpeza do cache de build autorizada em princípio.
- Plano exato documentado em `docs/docker-decommission.md`.
- Imagens, volumes anônimos e diretórios de código ainda exigem confirmação final.
- Nenhuma remoção foi executada.

## 2026-10-09 — Inventário somente leitura do servidor

- Acesso SSH autorizado e encerrado sem alterações.
- Confirmados Ubuntu 24.04.4, Docker 29.4.0, Compose 5.1.3 e porta 8123 livre.
- Encontrados 9 containers: 4 ativos e 5 parados, distribuídos entre Rifa, Cartório, HML e hello-world.
- Encontrados 21 volumes; bancos e uploads foram identificados como dados que exigem decisão específica.
- Raiz está em 84%; cache de build possui 60,13 GB, com 55,04 GB estimados como recuperáveis.
- `/srv/backups` possui 93 GB disponíveis, mas permissões atuais não permitem escrita pelo usuário não-root planejado.
- Nginx e Zabbix rodam fora do Docker e não estão incluídos em qualquer remoção implícita.
- Nenhum container, imagem, volume, cache, serviço ou arquivo foi alterado.

## 2026-10-09 — Endereço do servidor definido

- Servidor Ubuntu informado: `192.168.25.249`.
- URL LAN planejada do Home Assistant: `http://192.168.25.249:8123`.
- Disponibilidade da porta 8123 ainda precisa ser confirmada por inventário somente leitura.
- Usuário informou intenção de remover aplicações Docker existentes.
- Nenhum container ou dado foi alterado; remoção exige inventário e confirmação explícita dos recursos exatos.

## 2026-10-09 — Artefatos locais do kiosk

- Preparados launcher Chromium, autostart Cinnamon, instalador protegido e rollback direcionado.
- URL do Home Assistant é obrigatória por variável e não foi fixada no código.
- Launcher mantém DPMS/saver desativados durante a sessão e reinicia o Chromium após saída inesperada.
- Instalador captura preferências atuais antes de alterar bloqueio, inatividade e desligamento da tela.
- Nenhum artefato foi transferido ou executado no tablet.
- Validação local: sintaxe aprovada e 48 testes aprovados.

## 2026-10-09 — Inventário somente leitura do tablet

- Acesso SSH ao tablet autorizado pelo usuário e limitado a consultas.
- Confirmados Debian 12 i386, Cinnamon/X11, usuário `painel` com autologin e tela `1920x1200` horizontal.
- Chromium não está instalado, mas há pacote i386 nos repositórios Debian configurados.
- Não há autostart persistente do kiosk; o Firefox observado foi iniciado manualmente por SSH.
- A sessão atualmente bloqueia após 15 minutos e desliga a tela em AC após 30 minutos.
- Tablet possui aproximadamente 2 GiB de RAM e 19 GiB livres na raiz.
- Nenhum arquivo, pacote, serviço ou configuração do tablet foi alterado.
- Sessão SSH encerrada após o diagnóstico.

## 2026-10-09 — Agendador resiliente a reinício e falha SMTP

- Slots processados persistem atomicamente e impedem repetição após reinício.
- Estado é limitado aos 512 slots mais recentes.
- Resultado do canal de notificação é armazenado separadamente do backup.
- Falha SMTP é sanitizada e não interrompe o ciclo do agendador.
- Nenhum e-mail ou processo contínuo foi iniciado.
- Validação local: 44 testes aprovados.

## 2026-10-09 — Agendamento e notificações simuladas

- Agenda avaliada no fuso de cada origem e deduplicada por minuto durante a execução do processo.
- Origem desabilitada nunca chama o pipeline.
- Senha ausente gera `configuration_failed`; exceção inesperada gera `internal_failed` com sanitização.
- Falhas solicitam notificação por interface injetável.
- Adaptador SMTP com STARTTLS foi testado somente com cliente falso.
- Laço contínuo existe no código, mas não foi conectado ao entrypoint nem iniciado.
- Validação local: 40 testes aprovados.

## 2026-10-09 — Pipeline transacional simulado

- Dump local, upload criptografado e retenção cloud encadeados.
- Uma execução gera exatamente um registro final de histórico.
- Falhas locais, de upload e de retenção cloud possuem estados distintos.
- Falhas cloud preservam e continuam referenciando o dump local válido.
- Todos os comandos externos permanecem simulados nos testes.
- O relatório final mede a duração do pipeline completo.
- Validação local: 34 testes aprovados.

## 2026-10-09 — Adaptador cloud simulado

- Adaptador rclone criado sem uso de shell e sem execução real nos testes.
- Upload é destinado ao diretório exclusivo da origem no remote configurado.
- Retenção cloud usa 15 dias e permanece limitada ao diretório da origem.
- Saídas de erro passam por sanitização de segredos conhecidos.
- Remote real deverá ser confirmado como tipo `crypt` antes da implantação.
- Aviso sonoro por bell do terminal adicionado para final de etapa ou interação necessária.
- Validação local: 30 testes aprovados.

## 2026-10-09 — Proteção de espaço e retenção local

- Reserva prévia definida como duas vezes o tamanho estimado, com mínimo inicial de 64 MiB.
- Ao alcançar 85% de uso, a seleção remove apenas backups administrados e antigos até projetar 75%.
- O backup mais recente de cada origem é protegido.
- Se 75% não puder ser alcançado sem remover arquivos protegidos, o novo dump é recusado.
- Travas antigas são diagnosticadas, mas nunca removidas automaticamente.
- Validação local: 25 testes aprovados.

## 2026-10-09 — Executor local de dump

- Implementados bloqueio exclusivo por origem, arquivo parcial, validação não vazia e promoção atômica.
- Logs passam por sanitização antes de persistir.
- Cada tentativa publica relatório atual e acrescenta histórico JSONL.
- Execução externa é injetável; os testes usam simulação e não acessam banco ou rede.
- Agendamento, upload, retenção integrada e notificações continuam desabilitados.
- Maker continua com `enabled = false` até substituir o usuário administrativo.
- Validação local: 18 testes aprovados.

## 2026-10-09 — Primeira origem modelada

- Origem `Maker` registrada como PostgreSQL 14, banco `janus`, porta 5433 e tamanho estimado de 15 MB.
- Agenda definida para 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.
- SSL foi registrado como desabilitado conforme o ambiente informado.
- Senha permanece fora do repositório, referenciada por `BACKUP_MAKER_PASSWORD`.
- Origem mantida com `enabled = false`: o usuário atual `postgres` deve ser substituído por usuário exclusivo de backup antes do uso real.
- Modelo para inclusão de novas origens e validação TOML adicionados.
- Nenhuma conexão com o IP, banco ou servidor foi realizada.

## 2026-10-09 — Fundação local da Fase 1

- Estrutura inicial do repositório criada.
- Proteção de segredos e exemplo de variáveis adicionados.
- Compose declarativo preparado, sem execução.
- Esqueletos versionáveis do Home Assistant e do serviço de backup adicionados.
- Documentação inicial de arquitetura, segurança, inventário, implantação, rollback e operação criada.
- Testes locais de lógica adicionados sem dependências externas.
- Nenhum serviço, container ou acesso SSH foi realizado.

### Próxima etapa

Validar os artefatos locais, corrigir eventuais falhas e fechar a Fase 1. Depois, coletar as pendências funcionais e, mediante autorização específica, executar inventário somente leitura do servidor.
