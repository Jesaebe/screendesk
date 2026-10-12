# Rastreabilidade inicial

| Requisito | Artefato planejado | Estado |
|---|---|---|
| Dashboard touch | `dashboard/static/` | Base responsiva preparada |
| Kiosk após boot | `tablet/` | Artefatos locais; não aplicado |
| Calendar e Tasks | Google APIs + dashboard | Implementado; aguarda credencial OAuth |
| Ar-condicionado | SmartThings API | Samsung WindFree identificado; aguarda token e seleção |
| Dumps lógicos | `backup/src/dump.py`, `executor.py` | Maker habilitado; execução automática aprovada |
| Criptografia/Drive | `backup/src/cloud.py` + rclone crypt | Upload criptografado e renovação OAuth aprovados |
| Pipeline completo | `backup/src/pipeline.py` | Produção e restauração aprovadas |
| Relatório/histórico | `backup/src/reporting.py` | Latest e JSONL implementados |
| Retenção local/cloud | `backup/src/retention.py` | Lógica local inicial |
| Alertas/e-mail | dashboard + `notifications.py` | Gmail real aprovado; status visual implementado |
| Agenda por origem | `scheduler.py` | Maker ativo em quatro horários; deduplicação persistente aprovada |
| Saúde do servidor | `dashboard/src/host_metrics.py` + heartbeat do backup | Implementado localmente; aguarda implantação controlada |
| Restauração testada | `docs/runbooks/restore-test.md` | SHA-256 e catálogo `pg_restore` aprovados |
