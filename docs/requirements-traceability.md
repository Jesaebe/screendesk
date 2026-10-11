# Rastreabilidade inicial

| Requisito | Artefato planejado | Estado |
|---|---|---|
| Dashboard touch | `home-assistant/dashboards/screendeck.yaml` | Base preparada; entidades dependem das integrações |
| Kiosk após boot | `tablet/` | Artefatos locais; não aplicado |
| Calendar e Tasks | Integrações oficiais + dashboard | Aguarda OAuth |
| Ar-condicionado | `packages/climate_control.yaml` | Aguarda modelo |
| Dumps lógicos | `backup/src/dump.py`, `executor.py` | Maker habilitado; execução automática aprovada |
| Criptografia/Drive | `backup/src/cloud.py` + rclone crypt | Upload criptografado e renovação OAuth aprovados |
| Pipeline completo | `backup/src/pipeline.py` | Produção e restauração aprovadas |
| Relatório/histórico | `backup/src/reporting.py` | Latest e JSONL implementados |
| Retenção local/cloud | `backup/src/retention.py` | Lógica local inicial |
| Alertas HA/e-mail | packages + `notifications.py` | Gmail real aprovado; alerta HA aguarda ativação |
| Agenda por origem | `scheduler.py` | Maker ativo em quatro horários; deduplicação persistente aprovada |
| Saúde do servidor | solução após inventário | Pendente |
| Restauração testada | `docs/runbooks/restore-test.md` | SHA-256 e catálogo `pg_restore` aprovados |
