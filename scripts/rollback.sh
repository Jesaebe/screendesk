#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${SCREENDECK_ROLLBACK_AUTHORIZED:-}" != "YES" ]]; then
  echo "Rollback bloqueado: requer autorização explícita e plano revisado." >&2
  exit 1
fi

if [[ ! -f "$project_dir/.env" ]]; then
  echo "Rollback bloqueado: arquivo .env ausente em $project_dir." >&2
  exit 1
fi

echo "Parando somente o dashboard novo; backup e volumes serão preservados..."
docker compose --project-directory "$project_dir" --env-file "$project_dir/.env" \
  stop --timeout 30 dashboard

if docker container inspect screendeck-home-home-assistant-1 >/dev/null 2>&1; then
  echo "Restaurando temporariamente o container anterior do Home Assistant..."
  docker start screendeck-home-home-assistant-1
fi
