# Rastreabilidade inicial

| Requisito | Artefato planejado | Estado |
|---|---|---|
| Dashboard touch | `home-assistant/dashboards/screendeck.yaml` | Esqueleto |
| Kiosk após boot | `tablet/` | Artefatos locais; não aplicado |
| Calendar e Tasks | Integrações oficiais + dashboard | Aguarda OAuth |
| Ar-condicionado | `packages/climate_control.yaml` | Aguarda modelo |
| Dumps lógicos | `backup/src/dump.py`, `executor.py` | Executor testado; Maker desabilitado |
| Criptografia/Drive | `backup/src/cloud.py` + rclone crypt | Adaptador simulado; configuração real pendente |
| Pipeline completo | `backup/src/pipeline.py` | Simulado; origens reais desabilitadas |
| Relatório/histórico | `backup/src/reporting.py` | Latest e JSONL implementados |
| Retenção local/cloud | `backup/src/retention.py` | Lógica local inicial |
| Alertas HA/e-mail | packages + `notifications.py` | SMTP simulado; credenciais pendentes |
| Agenda por origem | `scheduler.py` | Estado persistente testado; entrada contínua desabilitada |
| Saúde do servidor | solução após inventário | Pendente |
| Restauração testada | `docs/runbooks/restore-test.md` | Procedimento inicial |
