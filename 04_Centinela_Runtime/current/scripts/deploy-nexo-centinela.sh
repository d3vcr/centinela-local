#!/usr/bin/env bash
set -euo pipefail

mode=check
confirm=
source_dir=
frontend_archive=
frontend_sha=
release_dir=
backup_dir=
expected_frontend=

protected_units=(
  mosquitto.service
  ecu-remote-relay.service
  nexo-ingest.service
  nexo-normalizer.timer
  nexo-api.service
  nexo-cockpit.service
  nexo-orbital-guardian-temp.service
  tailscaled.service
)

legacy_units=(
  motoguarana-funnel.timer
  motoguarana-funnel.service
  motoguarana-portal-publico.service
  motoguarana-startup.service
)

while (($#)); do
  case "$1" in
    --apply) mode=apply ;;
    --confirm) shift; confirm="${1:-}" ;;
    --source-dir) shift; source_dir="${1:-}" ;;
    --frontend-archive) shift; frontend_archive="${1:-}" ;;
    --frontend-sha) shift; frontend_sha="${1:-}" ;;
    --release-dir) shift; release_dir="${1:-}" ;;
    --backup-dir) shift; backup_dir="${1:-}" ;;
    --expected-frontend) shift; expected_frontend="${1:-}" ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[[ "$source_dir" == /tmp/nexo-centinela-* && -d "$source_dir/apps/centinela" ]] || {
  echo "Explicit staged Centinela source directory is required" >&2
  exit 2
}
[[ -f "$source_dir/deploy/systemd/nexo-centinela.service" ]] || {
  echo "Repo-managed unit is missing" >&2
  exit 2
}
[[ -f "$frontend_archive" ]] || { echo "Frontend archive is missing" >&2; exit 2; }
[[ "$frontend_sha" =~ ^[A-Fa-f0-9]{64}$ ]] || {
  echo "Valid frontend SHA-256 is required" >&2
  exit 2
}
[[ "$release_dir" == /opt/nexo/releases/orbital-guardian-* ]] || {
  echo "Explicit immutable release directory is required" >&2
  exit 2
}
[[ "$backup_dir" == /var/lib/nexo/backups/centinela-* ]] || {
  echo "Explicit Centinela backup directory is required" >&2
  exit 2
}
[[ "$expected_frontend" == /opt/nexo/releases/orbital-guardian-* ]] || {
  echo "Explicit expected frontend baseline is required" >&2
  exit 2
}

actual_sha="$(sha256sum "$frontend_archive" | awk '{print $1}')"
[[ "${actual_sha,,}" == "${frontend_sha,,}" ]] || {
  echo "Frontend SHA-256 mismatch" >&2
  exit 3
}
if unzip -Z1 "$frontend_archive" |
  grep -Eq '(^/|(^|/)\.\.(/|$)|(^|/)(node_modules|\.env|venv|\.venv)(/|$)|\.(sqlite3?|db)$)'; then
  echo "Frontend archive contains a blocked path" >&2
  exit 3
fi

current_frontend="$(readlink -f /opt/nexo/current-frontend)"
[[ "$current_frontend" == "$expected_frontend" ]] || {
  echo "Frontend baseline mismatch: $current_frontend" >&2
  exit 3
}
for unit in "${protected_units[@]}"; do
  [[ "$(systemctl is-enabled "$unit")" == enabled ]] || {
    echo "Protected unit is not enabled: $unit" >&2
    exit 3
  }
  [[ "$(systemctl is-active "$unit")" == active ]] || {
    echo "Protected unit is not active: $unit" >&2
    exit 3
  }
done
for unit in "${legacy_units[@]}"; do
  [[ "$(systemctl is-enabled "$unit" 2>/dev/null || true)" == disabled ]] || {
    echo "Legacy unit is not disabled: $unit" >&2
    exit 3
  }
  [[ "$(systemctl is-active "$unit" 2>/dev/null || true)" == inactive ]] || {
    echo "Legacy unit is not inactive: $unit" >&2
    exit 3
  }
done

health="$(curl -fsS --max-time 5 http://127.0.0.1:8080/health)"
live="$(curl -fsS --max-time 5 http://127.0.0.1:8080/live)"
python3 - "$health" "$live" <<'PY'
import json
import sys

health, live = map(json.loads, sys.argv[1:])
assert health["safety"]["physical_outputs_enabled"] is False
assert health["safety"]["remote_start_locked"] is True
assert health["database"]["readonly"] is True
assert health["database"].get("query_only") == 1
sample = (live.get("ecu") or {}).get("sample")
if sample is not None:
    assert sample.get("relay_outputs_enabled") in (0, False)
PY

echo "source_dir=$source_dir"
echo "frontend_archive=$frontend_archive"
echo "frontend_sha=$actual_sha"
echo "release_dir=$release_dir"
echo "backup_dir=$backup_dir"
echo "current_frontend=$current_frontend"

if [[ "$mode" == check ]]; then
  echo "CHECK ONLY: add --apply --confirm DEPLOY_NEXO_CENTINELA."
  exit 0
fi
[[ "$confirm" == DEPLOY_NEXO_CENTINELA ]] || {
  echo "Missing literal confirmation DEPLOY_NEXO_CENTINELA" >&2
  exit 2
}
[[ ! -e "$backup_dir" ]] || { echo "Backup directory already exists" >&2; exit 3; }
[[ ! -e "$release_dir" ]] || { echo "Release directory already exists" >&2; exit 3; }

mkdir -m 0750 "$backup_dir"
printf '%s\n' "$current_frontend" >"$backup_dir/previous_frontend"
if [[ -d /opt/nexo/apps/centinela ]]; then
  cp -a /opt/nexo/apps/centinela "$backup_dir/app"
  touch "$backup_dir/app_existed"
fi
if [[ -f /etc/systemd/system/nexo-centinela.service ]]; then
  cp -a /etc/systemd/system/nexo-centinela.service "$backup_dir/unit"
  touch "$backup_dir/unit_existed"
fi

rollback_on_error() {
  trap - ERR
  systemctl disable --now nexo-centinela.service 2>/dev/null || true
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
  ln -sfn "$current_frontend" /opt/nexo/current-frontend
  systemctl daemon-reload
  systemctl restart nexo-orbital-guardian-temp.service
  echo "Deployment failed; automatic rollback applied" >&2
}
trap rollback_on_error ERR

install -d -m 0755 /opt/nexo/apps/centinela
cp -a "$source_dir/apps/centinela/." /opt/nexo/apps/centinela/
chown -R root:root /opt/nexo/apps/centinela
find /opt/nexo/apps/centinela -type d -exec chmod 0755 {} +
find /opt/nexo/apps/centinela -type f -exec chmod 0644 {} +
install -m 0644 "$source_dir/deploy/systemd/nexo-centinela.service" \
  /etc/systemd/system/nexo-centinela.service

mkdir "$release_dir"
unzip -q "$frontend_archive" -d "$release_dir"
chmod -R a-w "$release_dir"
ln -sfn "$release_dir" /opt/nexo/current-frontend

systemctl daemon-reload
systemctl enable --now nexo-centinela.service
systemctl restart nexo-orbital-guardian-temp.service

for _ in $(seq 1 20); do
  if curl -fsS --max-time 3 http://127.0.0.1:8090/health >/dev/null &&
    curl -fsS --max-time 3 http://127.0.0.1:8181/api/centinela/state >/dev/null; then
    break
  fi
  sleep 1
done
curl -fsS --max-time 5 http://127.0.0.1:8090/health >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:8181/api/centinela/state >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:8081/ >/dev/null
tailscale serve status | grep -F '|-- / proxy http://127.0.0.1:8181' >/dev/null
[[ "$(systemctl is-enabled nexo-centinela.service)" == enabled ]]
[[ "$(systemctl is-active nexo-centinela.service)" == active ]]

cat >"$backup_dir/deployment.txt" <<EOF
release_dir=$release_dir
previous_frontend=$current_frontend
frontend_sha=$actual_sha
deployed_at=$(date --iso-8601=seconds)
EOF
chmod 0640 "$backup_dir/deployment.txt"
trap - ERR
echo "NEXO Centinela deployed successfully."

