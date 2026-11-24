#!/usr/bin/env bash
# Jalankan UI Streamlit agar bisa diakses dari laptop (mis. via Tailscale/LAN).
# PYTHONPATH di-unset supaya paket ROS 2 tidak bentrok dengan venv.
set -e
cd "$(dirname "$0")"

PORT="${1:-8501}"

# IP yang bisa dipakai laptop untuk mengakses (Tailscale 100.x diprioritaskan)
TS_IP="$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^100\.' | head -n1 || true)"
LAN_IP="$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^192\.168\.|^10\.' | head -n1 || true)"

echo "Buka di browser laptop:"
[ -n "$TS_IP" ]  && echo "  Tailscale : http://$TS_IP:$PORT"
[ -n "$LAN_IP" ] && echo "  LAN       : http://$LAN_IP:$PORT"
echo "  (atau pakai SSH tunnel: ssh -L $PORT:localhost:$PORT <user>@<remote>, lalu http://localhost:$PORT)"
echo

exec env -u PYTHONPATH .venv/bin/streamlit run app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true
