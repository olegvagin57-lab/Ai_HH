# Remote deployment (local edit -> server run)

This setup is for the workflow where you edit code on your local PC, push to GitHub, and the app is automatically redeployed on your remote server.

## 1) One-time server preparation (run from your own terminal)

Server: `172.24.191.52`

```bash
# connect
ssh root@172.24.191.52

# install Docker + Compose plugin (Ubuntu/Debian example)
apt update
apt install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# create deploy user
useradd -m -s /bin/bash deploy || true
usermod -aG docker deploy
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chown -R deploy:deploy /home/deploy/.ssh

# app directory
mkdir -p /opt/ai_hh
chown -R deploy:deploy /opt/ai_hh
```

## 2) Add deploy SSH key

Generate key pair locally (without passphrase for CI key):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ai_hh_deploy_key -N ""
```

Add public key to server:

```bash
ssh-copy-id -i ~/.ssh/ai_hh_deploy_key.pub deploy@172.24.191.52
```

## 3) Configure GitHub Actions secrets

Repository -> Settings -> Secrets and variables -> Actions:

- `SERVER_HOST`: `172.24.191.52`
- `SERVER_USER`: `deploy`
- `SERVER_PORT`: `22`
- `SSH_PRIVATE_KEY`: content of `~/.ssh/ai_hh_deploy_key`

## 4) Configure `.env` on server once

```bash
ssh deploy@172.24.191.52
cd /opt/ai_hh
cp -n env.production.template .env
nano .env
```

Required minimum:
- `SECRET_KEY` (strong random value)
- `CORS_ORIGINS` (include your host/IP where frontend is opened)

## 5) Deploy flow

1. Edit locally
2. `git add` / `git commit` / `git push`
3. Workflow `.github/workflows/deploy.yml` runs automatically
4. App is restarted on server with `docker compose -f docker-compose.prod.yml up -d --build`

## 6) Management commands from local machine

```bash
ssh deploy@172.24.191.52
cd /opt/ai_hh
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```
