#!/usr/bin/env bash
set -euo pipefail

if [[ "${SCREENDECK_DEPLOY_AUTHORIZED:-}" != "YES" ]]; then
  echo "Implantação bloqueada: requer autorização explícita e SCREENDECK_DEPLOY_AUTHORIZED=YES." >&2
  exit 1
fi

echo "A rotina de implantação ainda não foi implementada; nenhuma alteração foi feita." >&2
exit 2
