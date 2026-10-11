# Serviço de backup

O diretório contém o serviço de backup. O entrypoint carrega as origens, executa o agendador contínuo e encadeia dump, upload criptografado e retenção. As origens só executam quando possuem `enabled = true`; Maker permanece desabilitado até o teste controlado no servidor.

`sources.example.toml` contém a origem Maker desabilitada e um segundo bloco que serve de modelo para novas origens. Cada bloco referencia um arquivo de segredo exclusivo montado somente para leitura; nunca grave a senha diretamente no TOML ou em variável de ambiente.

Maker permanece com `enabled = false`. O usuário exclusivo `cyriusBackup`, o segredo protegido, um `pg_dump` de validação e o remote `crypt` foram confirmados em 10/10/2026. Por conter maiúscula, o nome deve ser citado como `"cyriusBackup"` em comandos SQL. O procedimento sem senha versionada está em `docs/runbooks/create-maker-backup-role.sql`. A origem só será habilitada durante o teste controlado.

O runbook concede acesso aos objetos existentes. Se a aplicação criar tabelas ou sequências no futuro, os proprietários desses objetos também deverão configurar `ALTER DEFAULT PRIVILEGES` para o usuário de backup ou o procedimento precisará ser reaplicado antes do próximo dump.

As agendas são interpretadas no fuso definido em cada origem. Para Maker: 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.

Cada bloco `[[source]]` possui sua própria lista `schedule`, portanto não existe obrigação de quatro execuções diárias para todos os bancos. Exemplos válidos incluem `schedule = ["02:00"]` para uma execução diária ou `schedule = ["06:00", "18:00"]` para duas. Depois de alterar o arquivo real no servidor, valide o TOML e reinicie somente o serviço `backup`; não é necessário reconstruir a imagem.

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

`src/notifications.py` oferece o contrato de notificação e adaptador SMTP com STARTTLS. Nos testes, pipeline, notificador e SMTP são falsos. O entrypoint chama `run_forever`; com todas as origens desabilitadas, o laço apenas avalia a agenda e não executa comandos externos. Enquanto SMTP não estiver completo, uma tentativa de alerta registra o canal como não configurado sem encerrar o agendador.

Os slots processados são persistidos atomicamente em `scheduler-state.json`, limitados aos 512 mais recentes, para evitar repetição após reinício. O resultado do canal de alerta fica separado em `notification-status.json`. Uma falha do SMTP não altera o resultado do backup nem encerra o agendador.
