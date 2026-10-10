#!/usr/bin/env bash
set -euo pipefail

# Somente leitura. Revisar e obter autorização antes de enviar ou executar no servidor.
uname -a
cat /etc/os-release
command -v docker || true
docker version 2>/dev/null || true
docker compose version 2>/dev/null || true
docker ps --all 2>/dev/null || true
docker network ls 2>/dev/null || true
docker volume ls 2>/dev/null || true
df -hT
lsblk -f
free -h
uptime
nproc
ss -lnt
stat -c '%A %U %G %n' /srv/backups 2>/dev/null || true
