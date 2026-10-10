#!/usr/bin/env bash
set -euo pipefail

tablet_user="painel"
tablet_home="/home/painel"
backup_file="$tablet_home/.config/screendeck-home/session-settings.backup"

if [[ "${SCREENDECK_TABLET_ROLLBACK_AUTHORIZED:-}" != "YES" ]]; then
  echo "Rollback bloqueado: requer autorização explícita." >&2
  exit 1
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Execute com sudo após autorização." >&2
  exit 1
fi
if [[ ! -r "$backup_file" ]]; then
  echo "Backup das preferências não encontrado; rollback interrompido." >&2
  exit 1
fi

idle_delay="$(sed -n 's/^idle_delay=//p' "$backup_file")"
lock_enabled="$(sed -n 's/^lock_enabled=//p' "$backup_file")"
sleep_display_ac="$(sed -n 's/^sleep_display_ac=//p' "$backup_file")"
session_bus="unix:path=/run/user/$(id -u "$tablet_user")/bus"

sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.desktop.session idle-delay "$idle_delay"
sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.desktop.screensaver lock-enabled "$lock_enabled"
sudo -u "$tablet_user" env DBUS_SESSION_BUS_ADDRESS="$session_bus" \
  gsettings set org.cinnamon.settings-daemon.plugins.power sleep-display-ac "$sleep_display_ac"

rm -f \
  "$tablet_home/.config/autostart/screendeck-home.desktop" \
  "$tablet_home/.local/bin/screendeck-kiosk" \
  "$tablet_home/.config/screendeck-home/kiosk.env"

echo "Preferências restauradas. Chromium foi preservado."
