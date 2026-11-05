# ScreenDeck Home

Sistema residencial composto por um dashboard web leve, um serviço independente de backups lógicos e um tablet em modo kiosk. O servidor de produção é Ubuntu, executa os serviços em Docker Compose e mantém os backups tanto no disco local quanto no Google Drive com criptografia do `rclone crypt`.

## Estado atual

- Servidor: `192.168.25.249`.
- Dashboard: implantado na porta `8123` e publicado pelo Nginx em `https://hml.cyrius.com.br`.
- Tablet kiosk: Debian, usuário `painel`, Firefox ESR iniciado automaticamente.
- Backup: implantado, com agendamento por origem, histórico no dashboard, alerta por e-mail, cópia local e cópia criptografada no Google Drive.
- Usuário de banco adotado: `cyriusBackup`.
- Google Drive: conta `jesaebe@gmail.com`, pasta `CyriusBackups`, remote base `gdrive` e remote criptografado `gdrive-crypt`.

O histórico detalhado das entregas está em [STATUS.md](STATUS.md), as decisões permanentes em [MEMORY.md](MEMORY.md) e a arquitetura em [docs/architecture.md](docs/architecture.md).

## Arquitetura e tecnologias

| Componente | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Dashboard | Python 3.12, HTML, CSS e JavaScript, sem framework externo | Relógio, clima Open-Meteo, Google Calendar/Tasks, SmartThings, métricas do host e operação dos backups |
| Backup | Python 3.12 | Agenda, trava por origem, dump, retenção, relatórios e alertas |
| Banco PostgreSQL | `pg_dump` em formato custom | Backup lógico consistente e restaurável por `pg_restore` |
| MySQL/MariaDB | `mariadb-dump` | Backup lógico com `--single-transaction` e `--quick` |
| Nuvem | `rclone`, Google Drive e `rclone crypt` | Upload, criptografia de conteúdo e nomes e retenção remota |
| Execução | Docker Engine e Docker Compose | Isolamento, reinício automático, volumes e rede interna |
| Alertas | SMTP com STARTTLS | E-mail para qualquer resultado de falha |
| Tablet | Debian, Cinnamon/X11 e Firefox ESR kiosk | Cliente dedicado do dashboard |
| Testes | `unittest` da biblioteca padrão | Validação local sem acessar bancos, rede ou Docker |

O Compose cria dois serviços:

- `dashboard`: publica `8123:8080`, lê o status do backup e métricas específicas do host em modo somente leitura;
- `backup`: não publica porta no host, executa como UID/GID `1000:1000` e expõe a porta `8090` apenas na rede interna para testes de conexão e disparo manual.

Os dados persistentes ficam em:

- `/srv/backups`: dumps, arquivos parciais, logs e travas;
- volume `backup-status`: último resultado, histórico, heartbeat e estado do agendador;
- volume `dashboard-data`: preferências, sessão e histórico de métricas;
- `/home/cyrius/.config/rclone/rclone.conf`: OAuth e configuração dos remotes;
- `/home/cyrius/.config/screendeck-home/`: senhas de banco e SMTP;
- `secrets/`: configuração de origens e segredos do dashboard no servidor.

Nenhum desses segredos, dumps ou logs deve entrar no Git.

## Estrutura do repositório

```text
backup/       serviço de backup e configuração de exemplo
dashboard/    aplicação web e arquivos estáticos
docs/         arquitetura, segurança e runbooks operacionais
monitoring/   limites e documentação de monitoramento
scripts/      validação, implantação, rollback e permissões
tablet/       launcher, instalação e rollback do kiosk
tests/        testes automatizados locais
compose.yaml  definição dos serviços, volumes e rede
```

## Configuração inicial do servidor

Pré-requisitos:

- Ubuntu com Docker Engine e o plugin Docker Compose;
- usuário operacional `cyrius`, UID/GID `1000:1000`, com acesso ao Docker;
- `/srv/backups` pertencente ao UID `1000` e gravável pelo proprietário;
- Nginx/HTTPS configurado quando Google OAuth for usado;
- acesso de rede do servidor aos bancos, ao Google Drive e ao SMTP.

No checkout do servidor:

```sh
cp .env.example .env
chmod 600 .env
mkdir -p secrets/dashboard
cp backup/config/sources.example.toml secrets/sources.toml
chmod 600 secrets/sources.toml
```

Revise `.env`. Os valores mais importantes são:

```dotenv
TZ=America/Bahia
DASHBOARD_PORT=8123
DASHBOARD_PUBLIC_URL=https://hml.cyrius.com.br
BACKUP_ROOT=/srv/backups
BACKUP_UID=1000
BACKUP_GID=1000
BACKUP_CONFIG_HOST=./secrets/sources.toml
RCLONE_CONFIG_DIR_HOST=/home/cyrius/.config/rclone
BACKUP_CLOUD_REMOTE=gdrive-crypt:screendeck-home
BACKUP_CLOUD_RETENTION_DAYS=15
```

`BACKUP_SCHEDULE` permanece por compatibilidade, mas a agenda efetiva é definida por origem no campo `schedule` de `sources.toml`.

### Segredos obrigatórios

Todos os arquivos devem pertencer a `cyrius:cyrius`, ter modo `0600` e nunca ser exibidos em logs ou enviados por chat:

| Arquivo no host | Uso |
| --- | --- |
| `/home/cyrius/.config/screendeck-home/maker-password` | Senha de `cyriusBackup`, atualmente compartilhada pelas origens cadastradas |
| `/home/cyrius/.config/rclone/rclone.conf` | OAuth do Drive e parâmetros/segredos do `crypt` |
| `secrets/sources.toml` | Hosts, bancos, agendas e origens ativas |
| `secrets/dashboard/dashboard-password` | Autenticação do dashboard |
| `secrets/dashboard/google-client.json` | OAuth Web do Google Calendar/Tasks; opcional |
| `secrets/dashboard/smartthings-token` | Token SmartThings; opcional |
| `/home/cyrius/.config/screendeck-home/smtp-password` | Senha de app SMTP; obrigatória quando alertas por e-mail estiverem habilitados |

Os procedimentos seguros estão em [instalação da senha de banco](docs/runbooks/install-maker-secret.md) e [instalação da senha SMTP](docs/runbooks/install-gmail-smtp-secret.md).

## Usuário de backup dos bancos

Use uma conta exclusiva, sem privilégios administrativos. Em PostgreSQL o nome adotado é `"cyriusBackup"`; as maiúsculas exigem aspas duplas em SQL.

Exemplo de criação, executado por um administrador do PostgreSQL e com uma senha forte informada de forma segura:

```sql
CREATE ROLE "cyriusBackup" LOGIN PASSWORD 'defina-interativamente-e-nao-versione';
```

Depois aplique as permissões em cada banco PostgreSQL:

```sh
chmod u+x scripts/grant-postgresql-backup-permissions.sh
scripts/grant-postgresql-backup-permissions.sh \
  --host banco.exemplo.local \
  --port 5432 \
  --database nome_do_banco \
  --admin-user postgres
```

O script não aceita a senha administrativa como argumento. Ele concede `CONNECT`, `USAGE` nos schemas, `SELECT` nas tabelas e sequências existentes e privilégios padrão para objetos futuros criados pelos proprietários atuais. Ao final, `objetos_sem_select` deve ser `0`.

Reexecute o script quando surgir um schema, proprietário ou role criadora de objetos. O roteiro completo está em [docs/runbooks/grant-postgresql-backup-permissions.md](docs/runbooks/grant-postgresql-backup-permissions.md).

Para MySQL/MariaDB, crie uma conta restrita ao banco necessário, conceda ao menos os privilégios de leitura compatíveis com `mariadb-dump` e valide um dump antes de ativar a origem.

## Cadastro e agenda dos bancos

O modo recomendado é **Dashboard → Gerenciar bancos**. Uma origem nova ou alterada precisa passar por **Testar conexão** antes de ser ativada. O teste consulta somente a versão do banco; um dump real ainda deve ser acompanhado para validar acesso a todas as tabelas.

Também é possível editar `secrets/sources.toml` no servidor:

```toml
[[source]]
id = "sistema-exemplo"
display_name = "Sistema Exemplo"
engine = "postgresql"
version = "14"
host = "banco.exemplo.local"
port = 5432
database = "aplicacao"
username = "cyriusBackup"
password_file = "/run/secrets/maker-password"
sslmode = "require"
schedule = ["00:00", "06:00", "12:00", "18:00"]
timezone = "America/Bahia"
estimated_size_mb = 100
enabled = true
readiness_note = "Permissoes e dump validados."
```

Cada origem possui sua própria agenda e fuso. O serviço relê o TOML antes de cada rodada; alterações feitas pelo dashboard não exigem reinício. Identificadores aceitam apenas letras minúsculas, números e hífens.

## Como o backup funciona

Para cada origem ativa e devida, o serviço executa estas etapas em sequência:

1. reserva o slot da agenda para impedir repetição após reinício;
2. cria `/srv/backups/.locks/<origem>.lock`, impedindo duas execuções simultâneas da mesma origem;
3. verifica o espaço e, quando o uso atinge 85%, remove backups locais antigos até projetar 75%, preservando o mais recente de cada origem;
4. grava o dump como `.partial` em `/srv/backups/.incoming`;
5. PostgreSQL usa `pg_dump --format=custom`; MySQL/MariaDB usa `mariadb-dump --single-transaction --quick`;
6. valida que o arquivo não está vazio e o promove atomicamente para `/srv/backups/<origem>/`;
7. envia o arquivo com checksum para `gdrive-crypt:screendeck-home/<origem>/`;
8. remove da nuvem arquivos da mesma origem com mais de `BACKUP_CLOUD_RETENTION_DAYS`, atualmente 15 dias;
9. registra um único resultado final e, se houver falha, envia e-mail SMTP.

Formato dos arquivos:

```text
/srv/backups/<origem>/<origem>-AAAAMMDDTHHMMSSZ.dump  # PostgreSQL
/srv/backups/<origem>/<origem>-AAAAMMDDTHHMMSSZ.sql   # MySQL/MariaDB
/srv/backups/logs/<origem>/<execucao>.log              # log sanitizado
```

Se o upload falhar, o dump local válido é preservado. Os estados principais são `success`, `failed`, `cloud_failed`, `cloud_retention_failed`, `configuration_failed` e `internal_failed`.

O botão do dashboard para executar todos os backups inicia uma rodada manual em segundo plano. Disparos manuais duplicados e sobreposição com a agenda são serializados pelo serviço.

## Configuração do Google Drive criptografado

Topologia usada em produção:

```text
gdrive:CyriusBackups                   remote Google Drive base
└── gdrive-crypt:                      camada que criptografa nomes e conteúdo
    └── screendeck-home/<origem>/      destino lógico visto pelo serviço
```

Configure diretamente no servidor:

```sh
install -d -m 700 /home/cyrius/.config/rclone
rclone config --config /home/cyrius/.config/rclone/rclone.conf
chmod 600 /home/cyrius/.config/rclone/rclone.conf
```

No assistente:

1. crie `gdrive`, tipo `drive`, apontando para a conta e pasta desejadas;
2. crie `gdrive-crypt`, tipo `crypt`, com destino `gdrive:CyriusBackups`;
3. use criptografia `standard` para nomes de arquivos e habilite nomes de diretórios criptografados;
4. gere `password` e `password2` longas e diferentes;
5. guarde as duas credenciais e uma cópia protegida do `rclone.conf` fora do servidor.

Valide sem revelar a configuração:

```sh
rclone listremotes --config /home/cyrius/.config/rclone/rclone.conf
rclone lsd --config /home/cyrius/.config/rclone/rclone.conf gdrive-crypt:
```

Não copie a saída de `rclone config show` para documentação ou chat. O procedimento completo e o teste não destrutivo estão em [docs/runbooks/configure-rclone-google-drive.md](docs/runbooks/configure-rclone-google-drive.md).

## Listar backups existentes

### Histórico registrado pelo serviço

Pelo dashboard, use o botão de histórico no cartão de backups. No servidor:

```sh
docker compose exec -T backup sh -c 'tail -n 30 /status/history.jsonl'
docker compose exec -T backup sh -c 'cat /status/latest.json'
```

### Arquivos locais

```sh
find /srv/backups -mindepth 2 -maxdepth 2 -type f \
  \( -name '*.dump' -o -name '*.sql' \) -printf '%TY-%Tm-%Td %TH:%TM  %10s  %p\n' \
  | sort -r
```

### Arquivos no Google Drive

Liste sempre pelo remote `crypt`; ele apresenta nomes descriptografados:

```sh
docker compose exec -T backup rclone lsf \
  --config /run/rclone/rclone.conf \
  --recursive --files-only --format 'tsp' \
  gdrive-crypt:screendeck-home
```

Usar o remote base `gdrive:CyriusBackups` mostrará somente nomes cifrados e não deve ser usado para restauração.

## Restaurar um backup

Restauração altera dados. Primeiro restaure em um banco descartável e isolado; nunca aponte diretamente para produção sem validação e autorização específicas.

### 1. Obter o arquivo

Se o dump local existir, use-o diretamente. Para baixar da nuvem para uma área separada:

```sh
docker compose exec -T backup mkdir -p /backups/restore/netus
docker compose exec -T backup rclone copyto \
  --config /run/rclone/rclone.conf \
  gdrive-crypt:screendeck-home/netus/ARQUIVO.dump \
  /backups/restore/netus/ARQUIVO.dump
```

Confirme que o arquivo existe e registre seu checksum:

```sh
sha256sum /srv/backups/restore/netus/ARQUIVO.dump
```

### 2. PostgreSQL

Inspecione o catálogo antes de restaurar:

```sh
pg_restore --list /srv/backups/restore/netus/ARQUIVO.dump | less
```

Crie um banco vazio e descartável e restaure sem reaplicar proprietários ou privilégios do ambiente original:

```sh
createdb --host HOST --port PORTA --username ADMIN BANCO_RESTAURADO
pg_restore --exit-on-error --no-owner --no-privileges \
  --host HOST --port PORTA --username ADMIN \
  --dbname BANCO_RESTAURADO \
  /srv/backups/restore/netus/ARQUIVO.dump
```

### 3. MySQL/MariaDB

```sh
mariadb --host HOST --port PORTA --user ADMIN --password \
  -e 'CREATE DATABASE banco_restaurado'
mariadb --host HOST --port PORTA --user ADMIN --password \
  banco_restaurado < /srv/backups/restore/origem/ARQUIVO.sql
```

Forneça senhas pelo prompt ou por arquivo de credenciais `0600`, nunca por argumento. Depois valide contagens, objetos críticos, versão da aplicação e consultas funcionais. Registre arquivo, checksum, ferramenta, duração e resultado antes de considerar o backup restaurável.

O script [scripts/restore-test.sh](scripts/restore-test.sh) é apenas uma proteção/placeholder e ainda **não automatiza** a restauração.

## Perda da chave de criptografia

O `rclone crypt` não possui chave mestra de recuperação. O acesso ao Google Drive ou a renovação do OAuth não descriptografa os backups por si só.

Há três cenários:

1. **Perdeu apenas o token OAuth do Drive:** reconecte o remote base `gdrive`, preservando integralmente o remote `gdrive-crypt`, suas senhas, o caminho de destino e as opções de nomes. Os backups continuam recuperáveis.
2. **Perdeu `rclone.conf`, mas guardou `password` e `password2`:** recrie `gdrive` e `gdrive-crypt` com o mesmo destino, as mesmas duas credenciais e exatamente as mesmas opções de criptografia. Valide com `rclone lsf gdrive-crypt:screendeck-home` antes de alterar o serviço.
3. **Perdeu `rclone.conf`, `password` e `password2`:** os objetos cifrados existentes são irrecuperáveis. Não há procedimento técnico para reconstruir essas credenciais a partir do Drive. Preserve os objetos para uma eventual localização de uma cópia da configuração, crie novas credenciais e use outro diretório remoto para os backups futuros.

Prevenção obrigatória:

- manter uma cópia criptografada e offline do arquivo completo `/home/cyrius/.config/rclone/rclone.conf`;
- guardar `password` e `password2` separadamente em um gerenciador de senhas;
- registrar o remote base, caminho, criptografia de nomes e criptografia de diretórios;
- testar periodicamente a listagem e uma restauração em ambiente descartável;
- nunca substituir ou reconfigurar `gdrive-crypt` sobre dados existentes sem validar primeiro uma cópia da configuração.

Ao trocar definitivamente de chave, crie um novo remote/path, atualize `BACKUP_CLOUD_REMOTE` no `.env`, recrie somente o serviço `backup` e faça um backup/restauração controlados. Backups antigos continuam exigindo a chave anterior.

## Implantação e atualização

### Validação local

Estes comandos não acessam bancos, rede ou Docker:

```sh
python3 -m unittest discover -s tests -v
bash scripts/validate-config.sh
```

`validate-config.sh` já executa a suíte e verifica se arquivos secretos conhecidos entraram no Git; executar ambos é útil apenas quando se deseja a saída detalhada antes da validação consolidada.

### Pré-checagem no servidor

```sh
./scripts/preflight-deploy.sh
```

Ela é somente leitura e valida host, Ubuntu, Docker, Compose, porta, armazenamento, segredos, permissões e sintaxe do Compose.

### Atualizar o dashboard

```sh
SCREENDECK_DEPLOY_AUTHORIZED=YES ./scripts/deploy.sh
```

O script executa a pré-checagem, constrói e valida a imagem, inicia somente o dashboard e aguarda o `/healthz`. Ele não recria o serviço de backup.

### Atualizar o serviço de backup

Faça isso somente após confirmar no dashboard e no servidor que não existe backup ativo nem arquivo `.lock` válido:

```sh
docker compose --env-file .env build backup
docker compose --env-file .env up -d --no-deps backup
docker compose --env-file .env ps backup
```

Recriar o backup interrompe qualquer dump em andamento. Nunca faça isso durante uma execução.

### Rollback do dashboard

```sh
SCREENDECK_ROLLBACK_AUTHORIZED=YES ./scripts/rollback.sh
```

O rollback para somente o dashboard e preserva o backup, os volumes e `/srv/backups`. Nunca use `docker compose down -v`, limpeza global do Docker ou exclusão de `/srv/backups` como rollback.

## Scripts operacionais

| Script | Quando executar | Efeito |
| --- | --- | --- |
| `scripts/validate-config.sh` | Antes de commit/deploy | Testes e verificação local; não acessa infraestrutura |
| `scripts/preflight-deploy.sh` | Antes de implantar | Diagnóstico somente leitura do servidor |
| `scripts/deploy.sh` | Atualização autorizada do dashboard | Build, validação, troca e healthcheck do dashboard |
| `scripts/rollback.sh` | Reversão autorizada do dashboard | Para o dashboard e restaura o Home Assistant preservado, se existir |
| `scripts/grant-postgresql-backup-permissions.sh` | Banco/schema/role novos ou erro de permissão | Concede leitura e privilégios padrão a `cyriusBackup` |
| `scripts/inventory-server.sh` | Diagnóstico de host | Coleta inventário somente leitura |
| `scripts/restore-test.sh` | Não usar como restauração automática | Placeholder bloqueado; ainda não restaura dados |
| `tablet/install.sh` | Instalação autorizada do kiosk | Configura autostart e energia do usuário `painel` |
| `tablet/rollback.sh` | Reversão do kiosk | Restaura preferências capturadas |

## Operação e diagnóstico

```sh
# Estado dos serviços
docker compose --env-file .env ps

# Logs recentes
docker compose --env-file .env logs --tail 100 dashboard
docker compose --env-file .env logs --tail 100 backup

# Estado ativo e último resultado
docker compose exec -T backup sh -c \
  'test ! -f /status/active-backup.json || cat /status/active-backup.json; cat /status/latest.json'

# Travas existentes — apenas listar, não remover automaticamente
find /srv/backups/.locks -maxdepth 1 -type f -print -exec sed -n '1,3p' {} \;
```

Uma trava só deve ser removida depois de confirmar simultaneamente que não há backup indicado como ativo e que não há `pg_dump`, `mariadb-dump` ou `mysqldump` em execução. Consulte [docs/runbooks/disk-pressure.md](docs/runbooks/disk-pressure.md) e [docs/runbooks/backup-failure.md](docs/runbooks/backup-failure.md).

## Regras de segurança

- Não versionar `.env`, `sources.toml` real, `rclone.conf`, tokens, credenciais, dumps ou logs.
- Não colocar senhas em argumentos, URLs, TOML, `.env`, capturas de tela ou chat.
- Usar TLS para bancos, SMTP e acesso público sempre que o ambiente suportar.
- Manter arquivos secretos em modo `0600` e diretórios privados em `0700`.
- Usar sempre o remote `gdrive-crypt` para listar, copiar ou restaurar; o remote base contém ciphertext.
- Não usar `rclone sync`, `move`, `purge` ou `delete` manualmente sem revisão exata do destino.
- Não executar o Compose de produção na máquina de desenvolvimento.
- Antes de qualquer ação destrutiva, identificar o arquivo, banco, container ou volume exato e preservar o último backup válido.

Consulte também [docs/security.md](docs/security.md), [docs/deployment.md](docs/deployment.md) e os demais [runbooks](docs/runbooks/).
