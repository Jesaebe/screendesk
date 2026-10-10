# Rollback futuro

Antes de qualquer deploy, registrar a versão anterior dos artefatos e preservar dados persistentes. Um rollback deverá parar apenas os serviços deste projeto, restaurar a configuração anterior e confirmar a integridade dos volumes sem excluir dumps ou configurações.

Nunca usar remoção de volumes, limpeza global do Docker ou exclusão de `/srv/backups` como parte do rollback.
