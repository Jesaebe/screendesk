# Serviço de backup

O diretório contém o serviço de backup. O entrypoint carrega as origens, executa o agendador contínuo e encadeia dump, upload criptografado e retenção. As origens só executam quando possuem `enabled = true`; Maker permanece desabilitado até o teste controlado no servidor.

`sources.example.toml` contém a origem Maker desabilitada e um segundo bloco que serve de modelo. Em produção, todas as origens usam o usuário `cyriusBackup` e o segredo existente montado em `/run/secrets/maker-password`; nunca grave a senha diretamente no TOML ou em variável de ambiente.

O usuário exclusivo `cyriusBackup`, o segredo protegido, o pipeline e a restauração do Maker foram validados. Por conter maiúscula, o nome deve ser citado como `"cyriusBackup"` em comandos SQL. Para cada banco PostgreSQL adicional, aplique e valide as permissões com `scripts/grant-postgresql-backup-permissions.sh`, seguindo `docs/runbooks/grant-postgresql-backup-permissions.md`.

O script concede acesso aos objetos existentes e configura `ALTER DEFAULT PRIVILEGES` para os atuais proprietários. Ele deve ser reaplicado quando surgir um schema ou uma role criadora de objetos que ainda não existia na execução anterior.

As agendas são interpretadas no fuso definido em cada origem. Para Maker: 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.

Cada bloco `[[source]]` possui sua própria lista `schedule`, portanto não existe obrigação de quatro execuções diárias para todos os bancos. Exemplos válidos incluem `schedule = ["02:00"]` para uma execução diária ou `schedule = ["06:00", "18:00"]` para duas. O dashboard gerencia o cadastro e o agendador relê o arquivo protegido antes de cada rodada, sem exigir reinício.

## Executor local

`src/executor.py` implementa uma execução isolada com trava exclusiva por origem, arquivo `.partial`, validação de conteúdo não vazio, promoção atômica, log sanitizado e relatórios `latest.json` e `history.jsonl`. Os limites configurados em `BACKUP_LOCAL_HIGH_WATERMARK` e `BACKUP_LOCAL_LOW_WATERMARK` são repassados pelo entrypoint.

O executor real usa `subprocess` sem shell. Nos testes, essa dependência é substituída por um objeto simulado que cria arquivos temporários e nunca acessa banco ou rede.

## Google Drive criptografado

`src/cloud.py` constrói comandos `rclone copyto` e `rclone delete` sem shell. O remote configurado em `BACKUP_CLOUD_REMOTE` deverá ser obrigatoriamente um remote do tipo `crypt`, apoiado por um remote Google Drive. O prefixo `RCLONE_` é evitado porque o próprio rclone o interpreta como configuração de backend.

O diretório dedicado do `rclone.conf` é gravável pelo processo UID 1000 para permitir a substituição atômica usada na renovação do token OAuth. Ele contém somente esse arquivo, permanece fora do repositório e o arquivo usa modo `0600`.

A retenção usa `--min-age 15d` dentro do diretório exclusivo de cada origem. Os testes injetam um runner simulado e não executam o binário rclone.

## Pipeline

`src/pipeline.py` encadeia dump local, upload e retenção cloud. Ele publica exatamente um registro final no histórico, com estados distintos para `failed`, `cloud_failed` e `cloud_retention_failed`. Se a nuvem falhar, o caminho do dump local continua registrado e o arquivo é preservado.

## Agendamento e alertas

`src/scheduler.py` avalia cada agenda no fuso da origem, impede repetição dentro do mesmo minuto e lê a senha do arquivo protegido antes de chamar o pipeline. Arquivo ausente ou vazio gera `configuration_failed`, relatório e notificação.

`src/control.py` expõe somente na rede interna do Compose um endpoint para teste de conexão. Ele usa o segredo existente no próprio serviço, executa uma consulta de versão sem modificar o banco e retorna apenas versão, latência ou categoria sanitizada da falha; a porta não é publicada no host.

`src/notifications.py` oferece o contrato de notificação e adaptador SMTP com STARTTLS. Nos testes, pipeline, notificador e SMTP são falsos. O entrypoint chama `run_forever`; com todas as origens desabilitadas, o laço apenas avalia a agenda e não executa comandos externos. Enquanto SMTP não estiver completo, uma tentativa de alerta registra o canal como não configurado sem encerrar o agendador.

Os slots processados são persistidos atomicamente em `scheduler-state.json`, limitados aos 512 mais recentes, para evitar repetição após reinício. O resultado do canal de alerta fica separado em `notification-status.json`. Uma falha do SMTP não altera o resultado do backup nem encerra o agendador.

Enquanto o pipeline executa, `active-backup.json` publica atomicamente a origem e o horário de início no volume de status. O arquivo é removido ao concluir ou falhar e também durante a inicialização, evitando um indicador obsoleto após reinício.

Quando o comando de dump falha, o relatório usa a primeira linha útil e sanitizada de erro, limitada a 300 caracteres. Se não houver uma linha reconhecível, mantém o código de saída como fallback; a saída completa continua restrita ao log operacional.
