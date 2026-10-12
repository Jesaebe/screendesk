# Monitoramento

O dashboard coleta, a cada minuto, métricas agregadas do host sem acesso ao socket Docker e sem privilégios adicionais:

- CPU, carga de 1/5/15 minutos e uptime por arquivos específicos de `/proc` montados somente para leitura;
- memória e swap por `/proc/meminfo`;
- ocupação do disco raiz pela montagem somente leitura de `/etc/hostname`, que pertence ao filesystem raiz;
- ocupação de `/srv/backups` por montagem somente leitura;
- disponibilidade do dashboard e heartbeat do agendador de backup.

As últimas 1.440 amostras (24 horas no intervalo padrão) ficam em `/data/host-metrics.jsonl`, no volume persistente do dashboard. A API autenticada `/api/host/metrics` entrega o estado atual e as 60 amostras mais recentes.

Nenhum conteúdo dos arquivos montados é exposto pela API. Os limiares em `alerts.example.yaml` continuam como valores iniciais até a definição operacional final.
