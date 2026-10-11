# Segurança

- Home Assistant disponível somente na LAN, com administrador individual e MFA quando suportado.
- Conta exclusiva e de privilégio mínimo para cada banco copiado.
- OAuth do Google Drive restrito à finalidade de backup.
- `rclone crypt` configurado fora do repositório.
- Antes da implantação, executar diagnóstico do rclone e confirmar que `BACKUP_CLOUD_REMOTE` referencia um remote do tipo `crypt`, nunca o remote Google Drive legível diretamente. Variáveis da aplicação não devem usar `RCLONE_<BACKEND>_<OPTION>`, pois esse namespace é interpretado pelo próprio rclone.
- TLS para conexões remotas de banco, SMTP e Google Drive quando suportado.
- Erros publicados e enviados por e-mail devem passar por sanitização.
- Arquivos secretos no servidor devem pertencer ao usuário operacional e usar modo `0600`.
- O container de backup executa sem root como UID/GID `1000:1000`, alinhado ao usuário operacional `cyrius`, para ler diretamente o `rclone.conf` protegido por modo `0600`; o arquivo é montado somente para leitura.
- Cada senha de banco fica em arquivo próprio com modo `0600`, montado individualmente abaixo de `/run/secrets`; ela não passa pelo `.env`, pelo TOML versionável ou por argumentos de linha de comando.
- Nenhum `.env`, `sources.toml` real, `rclone.conf`, token, dump ou log entra no Git.
- O container monta somente o arquivo `rclone.conf` como leitura/escrita para o rclone persistir renovações do token OAuth. O arquivo permanece `0600`, pertence ao UID 1000 e não expõe o diretório de configuração inteiro; os demais segredos continuam somente leitura.

Antes do deploy, revisar imagens fixadas, portas, volumes, permissões e resultados do inventário.
