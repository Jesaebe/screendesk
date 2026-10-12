# Implantação controlada

Estado atual: o backup está implantado e operacional; o Home Assistant está ativo temporariamente e será substituído pelo dashboard customizado.

Pré-condições: Fase 1 validada, inventário concluído, segredos preparados fora do Git, backups dos arquivos que serão afetados e autorização explícita do usuário.

Destino: servidor `192.168.25.249`. A porta 8123 permanece a mesma durante a troca.

Aplicações Docker existentes só poderão ser desativadas ou removidas após inventário e confirmação explícita por recurso. A implantação do ScreenDeck não autoriza implicitamente remoção de containers, volumes, redes ou dados anteriores.

As aplicações Docker antigas foram removidas pelo usuário conforme o plano aprovado. Depois da limpeza, não restaram containers, imagens, volumes locais ou cache de build; a raiz passou a 10% de uso, com 84 GB disponíveis. Nginx, Zabbix Agent 2 e as redes padrão do Docker foram preservados.

Antes de qualquer alteração, executar `scripts/preflight-deploy.sh` no diretório transferido. A pré-checagem é somente leitura e confirma host, Ubuntu, Docker/Compose, porta 8123, armazenamento, arquivos secretos, permissões e validade declarativa do Compose. Ela não cria diretórios, não corrige permissões e não inicia containers.

O `rclone.conf` já validado permanece em `/home/cyrius/.config/rclone/rclone.conf` no servidor. O Compose monta seu diretório dedicado em `/run/rclone` com escrita, necessária para a renovação OAuth atômica; o arquivo continua protegido com modo `0600` e não é copiado para o repositório.

O serviço de backup executa como UID/GID `1000:1000`, correspondente ao usuário `cyrius` no servidor. Isso mantém o processo sem privilégios de root e permite ler o `rclone.conf` com modo `0600`. Antes da implantação, `/srv/backups` deverá pertencer ao UID `1000` e permitir escrita ao proprietário.

A senha do Maker deve ficar em `/home/cyrius/.config/screendeck-home/maker-password`, pertencente a `cyrius:cyrius`, modo `0600`, sem quebra de linha obrigatória. O Compose monta somente esse arquivo em `/run/secrets/maker-password`, somente leitura. O procedimento interativo está em `docs/runbooks/install-maker-secret.md`.

## Substituição controlada pelo dashboard

Depois de publicar e atualizar o checkout do servidor, executar somente mediante autorização explícita:

```sh
SCREENDECK_DEPLOY_AUTHORIZED=YES ./scripts/deploy.sh
```

O script executa novamente a pré-checagem, constrói e valida o dashboard, para o Home Assistant sem removê-lo, inicia somente `dashboard` com `--no-deps` e aguarda o endpoint de saúde. O container de backup não é recriado.

Antes da execução, instalar `secrets/dashboard/dashboard-password` com modo `0600`. OAuth Google exige HTTPS no endereço público; `google-client.json` e `smartthings-token` são opcionais durante o primeiro boot.

## Reversão da substituição

Mediante autorização específica:

```sh
SCREENDECK_ROLLBACK_AUTHORIZED=YES ./scripts/rollback.sh
```

O rollback para somente o dashboard e volta a iniciar o container preservado do Home Assistant. O serviço de backup não é alterado.
