# Implantação futura

Estado atual: **não autorizada**.

Pré-condições: Fase 1 validada, inventário concluído, segredos preparados fora do Git, backups dos arquivos que serão afetados e autorização explícita do usuário.

Destino planejado: servidor `192.168.25.249`; o inventário e a validação posterior à limpeza confirmaram a porta 8123 disponível.

Aplicações Docker existentes só poderão ser desativadas ou removidas após inventário e confirmação explícita por recurso. A implantação do ScreenDeck não autoriza implicitamente remoção de containers, volumes, redes ou dados anteriores.

As aplicações Docker antigas foram removidas pelo usuário conforme o plano aprovado. Depois da limpeza, não restaram containers, imagens, volumes locais ou cache de build; a raiz passou a 10% de uso, com 84 GB disponíveis. Nginx, Zabbix Agent 2 e as redes padrão do Docker foram preservados.

Antes de qualquer alteração, executar `scripts/preflight-deploy.sh` no diretório transferido. A pré-checagem é somente leitura e confirma host, Ubuntu, Docker/Compose, porta 8123, armazenamento, arquivos secretos, permissões e validade declarativa do Compose. Ela não cria diretórios, não corrige permissões e não inicia containers.

O `rclone.conf` já validado permanece em `/home/cyrius/.config/rclone/rclone.conf` no servidor. O Compose o monta como `/run/secrets/rclone.conf`, somente leitura; não é necessário refazer a autorização OAuth nem copiar o arquivo para o repositório.

O serviço de backup executa como UID/GID `1000:1000`, correspondente ao usuário `cyrius` no servidor. Isso mantém o processo sem privilégios de root e permite ler o `rclone.conf` com modo `0600`. Antes da implantação, `/srv/backups` deverá pertencer ao UID `1000` e permitir escrita ao proprietário.

A senha do Maker deve ficar em `/home/cyrius/.config/screendeck-home/maker-password`, pertencente a `cyrius:cyrius`, modo `0600`, sem quebra de linha obrigatória. O Compose monta somente esse arquivo em `/run/secrets/maker-password`, somente leitura. O procedimento interativo está em `docs/runbooks/install-maker-secret.md`.

Ordem planejada:

1. revisar diff e imagens fixadas;
2. transferir somente artefatos versionados;
3. criar configuração secreta com permissões restritas;
4. validar a configuração do Compose;
5. construir a imagem de backup;
6. iniciar os serviços;
7. validar health checks, LAN e persistência;
8. executar backup controlado e restauração de teste;
9. documentar comandos e resultados em `STATUS.md`.

O script `scripts/deploy.sh` permanece bloqueado e ainda não executa a implantação. Ele só será implementado quando as origens, o remote `crypt`, SMTP e o entrypoint funcional do backup estiverem fechados; sua execução futura continuará exigindo autorização explícita por variável de ambiente.
