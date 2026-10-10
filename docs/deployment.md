# Implantação futura

Estado atual: **não autorizada**.

Pré-condições: Fase 1 validada, inventário concluído, segredos preparados fora do Git, backups dos arquivos que serão afetados e autorização explícita do usuário.

Destino planejado: servidor `192.168.25.249`; o inventário e a validação posterior à limpeza confirmaram a porta 8123 disponível.

Aplicações Docker existentes só poderão ser desativadas ou removidas após inventário e confirmação explícita por recurso. A implantação do ScreenDeck não autoriza implicitamente remoção de containers, volumes, redes ou dados anteriores.

As aplicações Docker antigas foram removidas pelo usuário conforme o plano aprovado. Depois da limpeza, não restaram containers, imagens, volumes locais ou cache de build; a raiz passou a 10% de uso, com 84 GB disponíveis. Nginx, Zabbix Agent 2 e as redes padrão do Docker foram preservados.

Antes de qualquer alteração, executar `scripts/preflight-deploy.sh` no diretório transferido. A pré-checagem é somente leitura e confirma host, Ubuntu, Docker/Compose, porta 8123, armazenamento, arquivos secretos, permissões e validade declarativa do Compose. Ela não cria diretórios, não corrige permissões e não inicia containers.

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
