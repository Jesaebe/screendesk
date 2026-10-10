# Segurança

- Home Assistant disponível somente na LAN, com administrador individual e MFA quando suportado.
- Conta exclusiva e de privilégio mínimo para cada banco copiado.
- OAuth do Google Drive restrito à finalidade de backup.
- `rclone crypt` configurado fora do repositório.
- Antes da implantação, executar diagnóstico do rclone e confirmar que `RCLONE_CRYPT_REMOTE` referencia um remote do tipo `crypt`, nunca o remote Google Drive legível diretamente.
- TLS para conexões remotas de banco, SMTP e Google Drive quando suportado.
- Erros publicados e enviados por e-mail devem passar por sanitização.
- Arquivos secretos no servidor devem pertencer ao usuário operacional e usar modo `0600`.
- Nenhum `.env`, `sources.toml` real, `rclone.conf`, token, dump ou log entra no Git.

Antes do deploy, revisar imagens fixadas, portas, volumes, permissões e resultados do inventário.
