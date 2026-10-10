# Pressão de disco

Ao atingir 85%, suspender novas execuções que não caibam com margem e selecionar backups locais mais antigos até a projeção voltar a 75%. Nunca remover arquivos fora da árvore administrada nem o último backup válido de cada origem. A exclusão será registrada no relatório.

Se os arquivos removíveis não forem suficientes para voltar a 75%, a execução nova deve falhar antes de chamar a ferramenta de dump. A preservação do último backup válido tem precedência sobre uma nova tentativa.

## Trava persistente

Uma trava existente bloqueia a origem. O diagnóstico considera candidata a obsoleta apenas uma trava com mais de seis horas cujo PID comprovadamente não exista. Trava malformada, processo vivo ou falta de permissão para verificar o PID nunca autoriza remoção automática.

Antes de remover uma trava candidata no servidor, confirmar que o container de backup não está executando e que não há `pg_dump`, `mariadb-dump` ou `mysqldump` associado à origem. A remoção deverá citar o caminho exato e ser registrada no relatório operacional; não usar curingas nem limpeza recursiva.
