# Serviço de backup

O diretório contém o contrato inicial do serviço. Nesta fase ele não agenda nem executa dumps reais; comandos externos permanecem separados e testáveis. A implementação funcional será feita após definir origens, janelas e credenciais.

`sources.example.toml` contém a origem Maker desabilitada e um segundo bloco que serve de modelo para novas origens. Cada bloco referencia uma variável de ambiente exclusiva; nunca grave a senha diretamente no TOML.

Maker permanece com `enabled = false`. O usuário exclusivo `cyriusBackup` e um `pg_dump` de validação foram confirmados pelo usuário em 10/10/2026. Por conter maiúscula, o nome deve ser citado como `"cyriusBackup"` em comandos SQL. O procedimento sem senha versionada está em `docs/runbooks/create-maker-backup-role.sql`. A origem só será habilitada após instalar a senha como segredo no servidor e validar o remote `crypt`.

O runbook concede acesso aos objetos existentes. Se a aplicação criar tabelas ou sequências no futuro, os proprietários desses objetos também deverão configurar `ALTER DEFAULT PRIVILEGES` para o usuário de backup ou o procedimento precisará ser reaplicado antes do próximo dump.

As agendas são interpretadas no fuso definido em cada origem. Para Maker: 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.

## Executor local

`src/executor.py` implementa uma execução isolada com trava exclusiva por origem, arquivo `.partial`, validação de conteúdo não vazio, promoção atômica, log sanitizado e relatórios `latest.json` e `history.jsonl`. Upload, retenção, notificações e agendamento são etapas separadas e ainda não estão habilitadas.

O executor real usa `subprocess` sem shell. Nos testes, essa dependência é substituída por um objeto simulado que cria arquivos temporários e nunca acessa banco ou rede.

## Google Drive criptografado

`src/cloud.py` constrói comandos `rclone copyto` e `rclone delete` sem shell. O remote configurado em `RCLONE_CRYPT_REMOTE` deverá ser obrigatoriamente um remote do tipo `crypt`, apoiado por um remote Google Drive; essa propriedade será confirmada no checklist de implantação porque não é seguro inferi-la apenas pelo nome.

A retenção usa `--min-age 15d` dentro do diretório exclusivo de cada origem. Os testes injetam um runner simulado e não executam o binário rclone.

## Pipeline

`src/pipeline.py` encadeia dump local, upload e retenção cloud. Ele publica exatamente um registro final no histórico, com estados distintos para `failed`, `cloud_failed` e `cloud_retention_failed`. Se a nuvem falhar, o caminho do dump local continua registrado e o arquivo é preservado.

## Agendamento e alertas

`src/scheduler.py` avalia cada agenda no fuso da origem, impede repetição dentro do mesmo minuto e exige a variável de senha antes de chamar o pipeline. Configuração ausente gera `configuration_failed`, relatório e notificação.

`src/notifications.py` oferece o contrato de notificação e adaptador SMTP com STARTTLS. Nos testes, pipeline, notificador e SMTP são falsos. O método contínuo `run_forever` existe, mas o entrypoint não o chama enquanto as origens reais estiverem desabilitadas e a implantação não estiver autorizada.

Os slots processados são persistidos atomicamente em `scheduler-state.json`, limitados aos 512 mais recentes, para evitar repetição após reinício. O resultado do canal de alerta fica separado em `notification-status.json`. Uma falha do SMTP não altera o resultado do backup nem encerra o agendador.
