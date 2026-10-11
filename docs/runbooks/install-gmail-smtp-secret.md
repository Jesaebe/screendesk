# Instalar a senha de app do Gmail

Use inicialmente `jesaebe@gmail.com` como remetente e destinatário. A senha deve ser uma senha de app do Google, não a senha normal da conta, e nunca deve ser enviada por chat ou gravada no `.env`.

No servidor, autenticado como `cyrius`, capture a senha sem eco:

```bash
install -d -m 700 /home/cyrius/.config/screendeck-home
umask 077
IFS= read -r -s -p 'Senha de app do Gmail: ' smtp_password
printf '\n'
printf '%s' "$smtp_password" > /home/cyrius/.config/screendeck-home/smtp-password
unset smtp_password
chmod 600 /home/cyrius/.config/screendeck-home/smtp-password
stat -c 'owner=%U group=%G mode=%a size=%s' /home/cyrius/.config/screendeck-home/smtp-password
```

O resultado esperado é proprietário `cyrius:cyrius`, modo `600` e tamanho maior que zero. Depois configure no `.env`:

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=jesaebe@gmail.com
SMTP_PASSWORD_FILE=/run/secrets/smtp-password
SMTP_PASSWORD_HOST=/home/cyrius/.config/screendeck-home/smtp-password
ALERT_EMAIL_FROM=jesaebe@gmail.com
ALERT_EMAIL_TO=jesaebe@gmail.com
```

Recrie somente o serviço `backup` e envie uma mensagem de teste controlada antes de depender dos alertas em produção.
