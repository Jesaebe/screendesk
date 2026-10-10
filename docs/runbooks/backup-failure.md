# Falha de backup

1. identificar origem e execução pelo relatório;
2. consultar o log sanitizado;
3. verificar conectividade, credenciais, espaço e ferramenta cliente sem registrar segredos;
4. preservar o último backup válido;
5. repetir somente após corrigir a causa;
6. confirmar alerta persistente e e-mail;
7. documentar causa e recuperação.

Estados monitorados: `failed`, `cloud_failed`, `cloud_retention_failed`, `configuration_failed` e `internal_failed`. Todos devem gerar notificação persistente no Home Assistant; quando o SMTP estiver configurado, o agendador também solicita e-mail.
