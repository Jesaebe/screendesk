#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
expected_host="${SCREENDECK_EXPECTED_HOST:-192.168.25.249}"
backup_root="${BACKUP_ROOT:-/srv/backups}"
failed=0

pass() {
  printf 'OK: %s\n' "$1"
}

fail() {
  printf 'ERRO: %s\n' "$1" >&2
  failed=1
}

if [[ "$(hostname -I 2>/dev/null || true)" == *"$expected_host"* ]]; then
  pass "host esperado ($expected_host)"
else
  fail "este host não possui o endereço esperado $expected_host"
fi

if [[ -r /etc/os-release ]] && grep -q '^ID=ubuntu$' /etc/os-release; then
  pass "Ubuntu identificado"
else
  fail "Ubuntu não identificado"
fi

if command -v docker >/dev/null 2>&1 && docker version >/dev/null 2>&1; then
  pass "Docker acessível"
else
  fail "Docker não está instalado, ativo ou acessível ao usuário atual"
fi

if docker compose version >/dev/null 2>&1; then
  pass "Docker Compose acessível"
else
  fail "Docker Compose não está acessível"
fi

if ss -H -ltn 'sport = :8123' 2>/dev/null | grep -q .; then
  fail "porta TCP 8123 já está em uso"
else
  pass "porta TCP 8123 livre"
fi

if [[ -d "$backup_root" ]]; then
  pass "diretório de backups existe: $backup_root"
else
  fail "diretório de backups ausente: $backup_root"
fi

backup_owner="$(stat -c '%u' "$backup_root" 2>/dev/null || true)"
backup_mode="$(stat -c '%a' "$backup_root" 2>/dev/null || true)"
if [[ "$backup_owner" == "10001" ]] && (( (8#${backup_mode:-0} & 8#200) != 0 )); then
  pass "diretório de backups gravável pelo UID 10001 do container"
else
  fail "diretório de backups deve pertencer ao UID 10001 e permitir escrita ao proprietário"
fi

for required in compose.yaml .env secrets/sources.toml secrets/rclone.conf; do
  if [[ -f "$project_dir/$required" ]]; then
    pass "arquivo presente: $required"
  else
    fail "arquivo ausente: $required"
  fi
done

for secret in .env secrets/sources.toml secrets/rclone.conf; do
  path="$project_dir/$secret"
  [[ -e "$path" ]] || continue
  mode="$(stat -c '%a' "$path")"
  if (( (8#$mode & 8#077) == 0 )); then
    pass "permissões restritas: $secret ($mode)"
  else
    fail "permissões abertas em $secret ($mode); esperado 600 ou mais restritivo"
  fi
done

if [[ -f "$project_dir/.env" ]] && docker compose --project-directory "$project_dir" \
  --env-file "$project_dir/.env" config --quiet; then
  pass "configuração do Compose válida"
else
  fail "configuração do Compose não pôde ser validada"
fi

if [[ "$failed" -ne 0 ]]; then
  echo "Pré-checagem reprovada; nenhuma alteração foi feita." >&2
  exit 1
fi

echo "Pré-checagem aprovada; nenhuma alteração foi feita."
