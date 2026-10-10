#!/usr/bin/env bash
set -euo pipefail

tablet_user="painel"
tablet_home="/home/painel"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backup_file="$tablet_home/.config/screendeck-home/session-settings.backup"

if [[ "${SCREENDECK_TABLET_AUTHORIZED:-}" != "YES" ]]; then
  echo "Configuração bloqueada: requer autorização explícita." >&2
  exit 1
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Execute com sudo após autorização." >&2
  exit 1
fi
if [[ "$(dpkg --print-architecture)" != "i386" ]]; then
  echo "Host recusado: arquitetura diferente de i386." >&2
  exit 1
fi
if ! id "$tablet_user" >/dev/null 2>&1; then
  echo "Host recusado: usuário painel ausente." >&2
  exit 1
fi
if [[ "${SCREENDECK_HA_URL:-}" != http://* && "${SCREENDECK_HA_URL:-}" != https://* ]]; then
  echo "Defina SCREENDECK_HA_URL com http:// ou https://." >&2
  exit 1
fi

apt-get update
apt-get install --no-install-recommends -y chromium

install -d -o "$tablet_user" -g "$tablet_user" -m 0755 \
  "$tablet_home/.local/bin" \
  "$tablet_home/.config/autostart" \
  "$tablet_home/.config/screendeck-home"
install -o "$tablet_user" -g "$tablet_user" -m 0755 \
  "$script_dir/screendeck-kiosk" "$tablet_home/.local/bin/screendeck-kiosk"
install -o "$tablet_user" -g "$tablet_user" -m 0644 \
  "$script_dir/screendeck-home.desktop" "$tablet_home/.config/autostart/screendeck-home.desktop"
printf 'SCREENDECK_HA_URL=%q\n' "$SCREENDECK_HA_URL" > "$tablet_home/.config/screendeck-home/kiosk.env"
chown "$tablet_user:$tablet_user" "$tablet_home/.config/screendeck-home/kiosk.env"
chmod 0600 "$tablet_home/.config/screendeck-home/kiosk.env"

session_bus="unix:path=/run/user/$(id -u "$tablet_user")/bus"
if [[ ! -f "$backup_file" ]]; then
  {
    printf 'idle_delay=%s\n' "$(sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" gsettings get org.cinnamon.desktop.session idle-delay)"
    printf 'lock_enabled=%s\n' "$(sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" gsettings get org.cinnamon.desktop.screensaver lock-enabled)"
    printf 'sleep_display_ac=%s\n' "$(sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" gsettings get org.cinnamon.settings-daemon.plugins.power sleep-display-ac)"
  } > "$backup_file"
  chown "$tablet_user:$tablet_user" "$backup_file"
  chmod 0600 "$backup_file"
fi

sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.desktop.session idle-delay 0
sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.desktop.screensaver lock-enabled false
sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.settings-daemon.plugins.power sleep-display-ac 0

echo "Configuração preparada. Reinicie somente após validar a URL e com autorização."
