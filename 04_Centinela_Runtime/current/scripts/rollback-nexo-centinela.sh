#!/usr/bin/env bash
set -euo pipefail

mode=check
confirm=
backup_dir=

while (($#)); do
  case "$1" in
    --apply) mode=apply ;;
    --confirm) shift; confirm="${1:-}" ;;
    --backup-dir) shift; backup_dir="${1:-}" ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[[ "$backup_dir" == /var/lib/nexo/backups/centinela-* && -d "$backup_dir" ]] || {
  echo "Explicit Centinela backup directory is required" >&2
  exit 2
}
[[ -f "$backup_dir/previous_frontend" ]] || {
  echo "Backup lacks previous_frontend" >&2
  exit 2
}
previous_frontend="$(cat "$backup_dir/previous_frontend")"
[[ "$previous_frontend" == /opt/nexo/releases/orbital-guardian-* &&
  -d "$previous_frontend" ]] || {
  echo "Invalid previous frontend in backup" >&2
  exit 3
}

echo "backup_dir=$backup_dir"
echo "previous_frontend=$previous_frontend"
echo "centinela_enabled=$(systemctl is-enabled nexo-centinela.service 2>/dev/null || true)"
echo "centinela_active=$(systemctl is-active nexo-centinela.service 2>/dev/null || true)"

if [[ "$mode" == check ]]; then
  echo "CHECK ONLY: add --apply --confirm ROLLBACK_NEXO_CENTINELA."
  exit 0
fi
[[ "$confirm" == ROLLBACK_NEXO_CENTINELA ]] || {
  echo "Missing literal confirmation ROLLBACK_NEXO_CENTINELA" >&2
  exit 2
}

systemctl disable --now nexo-centinela.service
if [[ -f "$backup_dir/unit_existed" ]]; then
  cp -a "$backup_dir/unit" /etc/systemd/system/nexo-centinela.service
else
  rm -f -- /etc/systemd/system/nexo-centinela.service
fi
if [[ -f "$backup_dir/app_existed" ]]; then
  rm -rf -- /opt/nexo/apps/centinela
  cp -a "$backup_dir/app" /opt/nexo/apps/centinela
else
  rm -rf -- /opt/nexo/apps/centinela
fi
ln -sfn "$previous_frontend" /opt/nexo/current-frontend
systemctl daemon-reload
systemctl restart nexo-orbital-guardian-temp.service

for _ in $(seq 1 10); do
  curl -fsS --max-time 3 http://127.0.0.1:8181/ >/dev/null && break
  sleep 1
done
curl -fsS --max-time 5 http://127.0.0.1:8181/ >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:8080/health >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:8081/ >/dev/null
echo "NEXO Centinela rollback completed."

