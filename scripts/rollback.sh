#!/usr/bin/env bash
set -euo pipefail

if [[ "${SCREENDECK_ROLLBACK_AUTHORIZED:-}" != "YES" ]]; then
  echo "Rollback bloqueado: requer autorização explícita e plano revisado." >&2
  exit 1
fi

echo "A rotina de rollback ainda não foi implementada; nenhuma alteração foi feita." >&2
exit 2
