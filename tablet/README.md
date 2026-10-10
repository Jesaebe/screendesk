# Configuração do tablet ScreenDeck

Artefatos destinados ao tablet Debian 12 i386. Eles são preparados localmente e não devem ser executados sem autorização explícita.

## Instalação futura

No tablet, a partir deste diretório e após revisar o script:

```sh
sudo SCREENDECK_TABLET_AUTHORIZED=YES \
  SCREENDECK_HA_URL=http://IP-DO-SERVIDOR:8123 \
  ./install.sh
```

O instalador exige host i386, usuário `painel`, URL HTTP(S) e confirmação literal. Ele instala Chromium pelo APT do Debian, cria arquivos somente no perfil dedicado e ajusta energia/bloqueio dessa sessão.

## Rollback futuro

```sh
sudo SCREENDECK_TABLET_ROLLBACK_AUTHORIZED=YES ./rollback.sh
```

O rollback remove somente os arquivos ScreenDeck conhecidos e restaura os valores de sessão registrados pelo instalador. Chromium não é removido automaticamente, evitando afetar outros usos.
