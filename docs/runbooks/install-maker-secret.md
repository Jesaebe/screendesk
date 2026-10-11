# Instalar o segredo do Maker

Estado: procedimento preparado, ainda não executado. Ele altera o servidor e exige autorização explícita.

O objetivo é gravar a senha de `cyriusBackup` sem colocá-la no repositório, no histórico do shell, em argumento de processo ou no arquivo `.env`.

No servidor, autenticado como `cyrius`, crie o diretório privado:

```bash
install -d -m 700 /home/cyrius/.config/screendeck-home
```

Capture a senha sem eco e grave o arquivo com permissão restrita:

```bash
umask 077
IFS= read -r -s -p 'Senha de cyriusBackup: ' maker_password
printf '\n'
printf '%s' "$maker_password" > /home/cyrius/.config/screendeck-home/maker-password
unset maker_password
chmod 600 /home/cyrius/.config/screendeck-home/maker-password
```

Valide somente metadados; não use comandos que exibam o conteúdo:

```bash
stat -c 'owner=%U group=%G mode=%a size=%s' /home/cyrius/.config/screendeck-home/maker-password
```

O resultado esperado é proprietário e grupo `cyrius`, modo `600` e tamanho maior que zero.

Depois, no diretório do projeto no servidor, crie `secrets/sources.toml` a partir de `backup/config/sources.example.toml`, mantenha somente as origens reais e deixe Maker com `enabled = false`. Esse arquivo também deve pertencer a `cyrius:cyrius` e usar modo `0600`. A habilitação ocorrerá apenas junto do entrypoint funcional e de um teste controlado de backup e restauração.

Por fim, execute a pré-checagem somente leitura:

```bash
scripts/preflight-deploy.sh
```

Não informe a senha no chat e não a inclua em comandos, `.env`, `sources.toml`, logs ou capturas de tela.
