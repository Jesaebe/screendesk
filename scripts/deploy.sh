#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SCREENDECK_GIT_COMMIT="${SCREENDECK_GIT_COMMIT:-$(git -C "$project_dir" rev-parse --short HEAD 2>/dev/null || printf unknown)}"
export SCREENDECK_BUILD_TIME="${SCREENDECK_BUILD_TIME:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
compose=(docker compose --project-directory "$project_dir" --env-file "$project_dir/.env")

if [[ "${SCREENDECK_DEPLOY_AUTHORIZED:-}" != "YES" ]]; then
  echo "Implantação bloqueada: requer autorização explícita e SCREENDECK_DEPLOY_AUTHORIZED=YES." >&2
  exit 1
fi

"$project_dir/scripts/preflight-deploy.sh"

echo "Construindo o dashboard customizado..."
"${compose[@]}" build dashboard

echo "Validando o dashboard..."
"${compose[@]}" run --rm --no-deps --entrypoint python3 dashboard \
  -m py_compile /app/src/server.py

echo "Parando o Home Assistant antigo de forma recuperável..."
if docker container inspect screendeck-home-home-assistant-1 >/dev/null 2>&1; then
  docker stop --timeout 60 screendeck-home-home-assistant-1
fi

echo "Iniciando somente o dashboard; o serviço de backup não será recriado..."
"${compose[@]}" up -d --no-deps dashboard

dashboard_url="http://127.0.0.1:${DASHBOARD_PORT:-8123}/healthz"
for attempt in {1..60}; do
  if curl --fail --silent --show-error --output /dev/null "$dashboard_url"; then
    echo "Dashboard respondeu em $dashboard_url"
    "${compose[@]}" ps dashboard
    exit 0
  fi
  if (( attempt == 60 )); then
    break
  fi
  sleep 2
done

echo "Dashboard não respondeu em até 120 segundos. O container foi preservado para diagnóstico." >&2
"${compose[@]}" ps dashboard >&2 || true
"${compose[@]}" logs --tail 80 dashboard >&2 || true
exit 1
