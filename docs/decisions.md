# Registro de decisões

## D-001 — Google Drive como destino cloud

Google Drive é o único destino cloud aprovado. A menção anterior à AWS foi removida do PRD.

## D-002 — Criptografia anterior ao upload

O remote usado pelo serviço deverá ser um remote `crypt` do rclone sobre um remote Google Drive. Arquivos legíveis não serão enviados ao Drive.

## D-003 — Configuração de origens em TOML

O serviço usa TOML porque Python moderno oferece leitura pela biblioteca padrão. Senhas são referenciadas por caminho de arquivo abaixo de `/run/secrets`, nunca gravadas no TOML versionado nem transportadas em variáveis de ambiente.

## D-004 — Estado do backup por volume compartilhado

O serviço publica JSON atômico em volume dedicado. O Home Assistant monta esse volume somente para leitura. O formato definitivo de histórico será validado durante a implementação funcional.

## D-005 — Monitoramento integrado e sem socket Docker

O dashboard coleta as métricas agregadas necessárias diretamente de arquivos específicos de `/proc` e de pontos de montagem somente leitura. A disponibilidade do backup usa heartbeat no volume de status compartilhado. Essa abordagem evita outro serviço, dependências externas, modo privilegiado e acesso ao socket Docker.

## Google Drive para backups

A conta aprovada é `jesaebe@gmail.com` e a pasta dedicada é `CyriusBackups`, diretamente na raiz do Drive. O remote `gdrive-crypt` tem essa pasta como raiz, mantendo nomes e conteúdo abaixo dela criptografados. OAuth, token e chaves do `crypt` ficam fora do repositório.
