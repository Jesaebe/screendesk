# Runbook de backup

Uma execução válida deve verificar configuração e espaço, impedir concorrência, gerar dump lógico, validar arquivo não vazio, compactar, publicar cópia criptografada, registrar relatório e aplicar retenção. Falhas não podem apagar o último backup válido nem expor credenciais.

O executor local atual cobre trava, dump, validação, promoção atômica, log sanitizado e relatório. As etapas de espaço prévio, upload criptografado, retenção, e-mail e agendamento ainda não estão conectadas ao executor.

O adaptador cloud constrói upload e retenção de 15 dias, mas ainda não está conectado ao executor. A ordem futura será: concluir e preservar dump local, enviar ao remote `crypt`, confirmar sucesso e somente então remover objetos cloud com idade superior à retenção.
