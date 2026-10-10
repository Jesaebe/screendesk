# Configurar Google Drive criptografado

Estado: remotes criados e validados pelo usuário em 10/10/2026, incluindo envio criptografado e restauração descriptografada de uma pasta de teste.

## Destino aprovado

- Conta Google: `jesaebe@gmail.com`.
- Pasta dedicada: `CyriusBackups`, diretamente na raiz do Drive.
- Remote base: `gdrive`.
- Remote criptografado: `gdrive-crypt`.
- Destino usado pela aplicação: `gdrive-crypt:screendeck-home`.

A pasta aprovada será a raiz visível do `crypt`. Abaixo dela, nomes de diretórios, nomes de arquivos e conteúdo serão criptografados pelo rclone.

## Regras de segurança

- Executar a autorização OAuth logado exclusivamente na conta aprovada.
- Não enviar token, `rclone.conf`, senha do `crypt` ou salt pelo chat.
- Gerar senhas longas e distintas para `password` e `password2` do remote `crypt`.
- Guardar essas senhas também em um gerenciador de senhas: perdê-las torna os backups irrecuperáveis.
- Manter `secrets/rclone.conf` com modo `0600` e fora do Git.
- Não usar `rclone sync`, `move`, `purge` ou `delete` durante a configuração e validação.

## Configuração interativa futura

No servidor, a partir do diretório do projeto:

```sh
mkdir -p secrets
rclone config --config ./secrets/rclone.conf
```

No assistente:

1. criar o remote `gdrive`, tipo `drive`;
2. autenticar por OAuth com `jesaebe@gmail.com`;
3. preferir o menor escopo compatível com criação e leitura dos arquivos do próprio rclone;
4. criar o remote `gdrive-crypt`, tipo `crypt`;
5. definir o remote de destino como `gdrive:CyriusBackups`;
6. habilitar criptografia dos nomes de arquivos (`standard`);
7. habilitar criptografia dos nomes de diretórios;
8. criar e guardar `password` e `password2` fora do repositório.

Depois:

```sh
chmod 0600 ./secrets/rclone.conf
rclone config show --config ./secrets/rclone.conf
rclone lsd --config ./secrets/rclone.conf gdrive-crypt:
```

O comando `config show` deve ser observado somente no terminal seguro do servidor; sua saída não deve ser copiada para documentação ou chat.

## Teste não destrutivo

Criar localmente um arquivo sem informação sensível e copiá-lo pelo remote criptografado:

```sh
printf 'ScreenDeck cloud test\n' > /tmp/screendeck-cloud-test.txt
rclone copyto --config ./secrets/rclone.conf \
  /tmp/screendeck-cloud-test.txt \
  gdrive-crypt:screendeck-home/validation/screendeck-cloud-test.txt
rclone cat --config ./secrets/rclone.conf \
  gdrive-crypt:screendeck-home/validation/screendeck-cloud-test.txt
```

Confirmar pela interface do Google Drive que o conteúdo armazenado sob `CyriusBackups` não possui nomes nem conteúdo legíveis. A exclusão do arquivo de teste deve ser uma ação separada e consciente depois da validação.

Referências oficiais: documentação dos remotes [Google Drive](https://rclone.org/drive/) e [Crypt](https://rclone.org/crypt/).
