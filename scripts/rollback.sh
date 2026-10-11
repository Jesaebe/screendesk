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

echo "Parando somente o Home Assistant; backup, volumes e configurações serão preservados..."
docker compose --project-directory "$project_dir" --env-file "$project_dir/.env" \
  stop --timeout 60 home-assistant
docker compose --project-directory "$project_dir" --env-file "$project_dir/.env" \
  ps home-assistant
