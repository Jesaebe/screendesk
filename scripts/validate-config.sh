#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

python3 -m unittest discover -s tests -v

if git ls-files | grep -E '(^|/)(\.env|secrets\.yaml|rclone\.conf)$|credentials.*\.json$' >/dev/null; then
  echo "Erro: arquivo secreto potencial está versionado." >&2
  exit 1
fi

echo "Validação local concluída sem executar infraestrutura."
