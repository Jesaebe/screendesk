#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
expected_host="${SCREENDECK_EXPECTED_HOST:-192.168.25.249}"
backup_root="${BACKUP_ROOT:-/srv/backups}"
backup_uid="${BACKUP_UID:-1000}"
backup_config_host="${BACKUP_CONFIG_HOST:-$project_dir/secrets/sources.toml}"
maker_password_host="${BACKUP_MAKER_PASSWORD_HOST:-/home/cyrius/.config/screendeck-home/maker-password}"
rclone_config_dir_host="${RCLONE_CONFIG_DIR_HOST:-/home/cyrius/.config/rclone}"
rclone_config_host="$rclone_config_dir_host/rclone.conf"
dashboard_password_host="$project_dir/secrets/dashboard/dashboard-password"
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
  if docker container inspect screendeck-home-home-assistant-1 >/dev/null 2>&1; then
    pass "porta TCP 8123 ocupada pelo Home Assistant que será substituído"
  else
    fail "porta TCP 8123 já está em uso por serviço desconhecido"
  fi
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
if [[ "$backup_owner" == "$backup_uid" ]] && (( (8#${backup_mode:-0} & 8#200) != 0 )); then
  pass "diretório de backups gravável pelo UID $backup_uid do container"
else
  fail "diretório de backups deve pertencer ao UID $backup_uid e permitir escrita ao proprietário"
fi

for required in compose.yaml .env; do
  if [[ -f "$project_dir/$required" ]]; then
    pass "arquivo presente: $required"
  else
    fail "arquivo ausente: $required"
  fi
done

for secret_path in "$project_dir/.env" "$backup_config_host" "$maker_password_host" "$rclone_config_host" "$dashboard_password_host"; do
  path="$secret_path"
  if [[ -f "$path" ]]; then
    pass "arquivo secreto presente: $path"
  else
    fail "arquivo secreto ausente: $path"
    continue
  fi
  [[ -e "$path" ]] || continue
  mode="$(stat -c '%a' "$path")"
  if (( (8#$mode & 8#077) == 0 )); then
    pass "permissões restritas: $path ($mode)"
  else
    fail "permissões abertas em $path ($mode); esperado 600 ou mais restritivo"
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
