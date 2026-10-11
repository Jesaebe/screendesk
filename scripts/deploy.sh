#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose=(docker compose --project-directory "$project_dir" --env-file "$project_dir/.env")

if [[ "${SCREENDECK_DEPLOY_AUTHORIZED:-}" != "YES" ]]; then
  echo "Implantação bloqueada: requer autorização explícita e SCREENDECK_DEPLOY_AUTHORIZED=YES." >&2
  exit 1
fi

"$project_dir/scripts/preflight-deploy.sh"

echo "Baixando a imagem fixada do Home Assistant..."
"${compose[@]}" pull home-assistant

echo "Validando a configuração do Home Assistant com a imagem fixada..."
"${compose[@]}" run --rm --no-deps home-assistant \
  python -m homeassistant --script check_config --config /config

echo "Iniciando somente o Home Assistant; o serviço de backup não será recriado..."
"${compose[@]}" up -d --no-deps home-assistant

ha_url="http://127.0.0.1:${HA_PORT:-8123}/"
for attempt in {1..60}; do
  if curl --fail --silent --show-error --output /dev/null "$ha_url"; then
    echo "Home Assistant respondeu em $ha_url"
    "${compose[@]}" ps home-assistant
    exit 0
  fi
  if (( attempt == 60 )); then
    break
  fi
  sleep 2
done

echo "Home Assistant não respondeu em até 120 segundos. O container foi preservado para diagnóstico." >&2
"${compose[@]}" ps home-assistant >&2 || true
"${compose[@]}" logs --tail 80 home-assistant >&2 || true
exit 1
