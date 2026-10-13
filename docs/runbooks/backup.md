# Runbook de backup

Uma execução válida deve verificar configuração e espaço, impedir concorrência, gerar dump lógico, validar arquivo não vazio, compactar, publicar cópia criptografada, registrar relatório e aplicar retenção. Falhas não podem apagar o último backup válido nem expor credenciais.

Antes de ativar uma nova origem PostgreSQL, conceda e valide as permissões de leitura com `scripts/grant-postgresql-backup-permissions.sh`. O passo a passo, incluindo privilégios para objetos futuros e a verificação após a concessão, está em `docs/runbooks/grant-postgresql-backup-permissions.md`.

O executor local atual cobre trava, dump, validação, promoção atômica, log sanitizado e relatório. As etapas de espaço prévio, upload criptografado, retenção, e-mail e agendamento ainda não estão conectadas ao executor.

O adaptador cloud constrói upload e retenção de 15 dias, mas ainda não está conectado ao executor. A ordem futura será: concluir e preservar dump local, enviar ao remote `crypt`, confirmar sucesso e somente então remover objetos cloud com idade superior à retenção.
