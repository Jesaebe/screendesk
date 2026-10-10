#!/usr/bin/env bash
set -euo pipefail

if [[ "${SCREENDECK_RESTORE_TEST_AUTHORIZED:-}" != "YES" ]]; then
  echo "Teste bloqueado: requer ambiente descartável e autorização explícita." >&2
  exit 1
fi

echo "A restauração automatizada ainda não foi implementada; nenhuma alteração foi feita." >&2
exit 2
