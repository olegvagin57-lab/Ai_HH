#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   sudo bash scripts/prepare_remote_server.sh
#
# Optional env overrides:
#   DEPLOY_USER=deploy APP_DIR=/opt/ai_hh bash scripts/prepare_remote_server.sh

DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_DIR="${APP_DIR:-/opt/ai_hh}"

echo "[1/5] Installing Docker prerequisites..."
apt-get update
apt-get install -y ca-certificates curl gnupg git

echo "[2/5] Installing Docker engine and compose plugin..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker

echo "[3/5] Creating deploy user..."
if ! id -u "${DEPLOY_USER}" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "${DEPLOY_USER}"
fi
usermod -aG docker "${DEPLOY_USER}"

echo "[4/5] Creating app directory..."
mkdir -p "${APP_DIR}"
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}"

echo "[5/5] Creating SSH folder for deploy user..."
install -d -m 700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"

echo "Done."
echo "Next steps:"
echo "1) Add CI public key to /home/${DEPLOY_USER}/.ssh/authorized_keys"
echo "2) Add GitHub Secrets: SERVER_HOST, SERVER_USER, SERVER_PORT, SSH_PRIVATE_KEY"
