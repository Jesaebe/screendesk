# Registro de decisões

## D-001 — Google Drive como destino cloud

Google Drive é o único destino cloud aprovado. A menção anterior à AWS foi removida do PRD.

## D-002 — Criptografia anterior ao upload

O remote usado pelo serviço deverá ser um remote `crypt` do rclone sobre um remote Google Drive. Arquivos legíveis não serão enviados ao Drive.

## D-003 — Configuração de origens em TOML

O serviço usa TOML porque Python moderno oferece leitura pela biblioteca padrão. Senhas são referenciadas por nome de variável de ambiente, nunca gravadas no TOML versionado.

## D-004 — Estado do backup por volume compartilhado

O serviço publica JSON atômico em volume dedicado. O Home Assistant monta esse volume somente para leitura. O formato definitivo de histórico será validado durante a implementação funcional.

## D-005 — Monitoramento do host pendente

Não será escolhida uma imagem de monitoramento antes do inventário. A solução deverá expor CPU, memória, carga, disco raiz e `/srv/backups` sem privilégios desnecessários.

## Google Drive para backups

A conta aprovada é `jesaebe@gmail.com` e a pasta dedicada é `CyriusBackups`, diretamente na raiz do Drive. O remote `gdrive-crypt` tem essa pasta como raiz, mantendo nomes e conteúdo abaixo dela criptografados. OAuth, token e chaves do `crypt` ficam fora do repositório.
