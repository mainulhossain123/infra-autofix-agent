#!/bin/bash
# =============================================================================
# EC2 First-Boot Bootstrap Script
# =============================================================================
# This file is a Terraform templatefile(). It runs automatically the first
# time the EC2 instance boots (via EC2 user_data / cloud-init).
#
# Terraform substitutes these placeholders before sending to the instance:
#   ${groq_api_key}       — your Groq API key
#   ${postgres_password}  — generated database password
#   ${grafana_password}   — generated Grafana password
#
# NOTE: All other $ signs (bash variables, subshells) are left unchanged
#       by Terraform. Only ${...} matching a declared variable is replaced.
# =============================================================================

set -e

# Log everything to a file so you can watch progress via SSH:
#   tail -f /var/log/infra-autofix-setup.log
exec > /var/log/infra-autofix-setup.log 2>&1

echo "=== infra-autofix-agent: EC2 bootstrap started at $(date) ==="
echo "Instance: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)"

# ── Step 1: System update ─────────────────────────────────────────────────────
echo ""
echo "[1/6] Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y -q
apt-get upgrade -y -q
apt-get install -y -q ca-certificates curl gnupg git

# ── Step 2: Install Docker (official method) ──────────────────────────────────
echo ""
echo "[2/6] Installing Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Note: using $ARCH and $VERSION_CODENAME (no braces) so Terraform doesn't
# try to substitute them as template variables.
ARCH=$(dpkg --print-architecture)
. /etc/os-release
echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y -q
apt-get install -y -q \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu
echo "    Docker $(docker --version) installed"

# ── Step 3: Swap space (CRITICAL for t2.micro — only 1 GB RAM) ───────────────
echo ""
echo "[3/6] Creating 4 GB swap file (required for t2.micro)..."
if [ ! -f /swapfile ]; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo "    Swap created. Total memory: $(free -h | grep Mem | awk '{print $2}') RAM + $(free -h | grep Swap | awk '{print $2}') swap"
fi

# ── Step 4: Clone the repository ─────────────────────────────────────────────
echo ""
echo "[4/6] Cloning infra-autofix-agent repository..."
git clone https://github.com/mainulhossain123/infra-autofix-agent.git /home/ubuntu/infra-autofix-agent
chown -R ubuntu:ubuntu /home/ubuntu/infra-autofix-agent

# ── Step 5: Write .env with injected secrets ──────────────────────────────────
# Terraform has already replaced ${groq_api_key}, ${postgres_password},
# ${grafana_password} with real values before this script reaches the instance.
# The single-quoted EOF prevents bash from expanding any remaining $ signs.
echo ""
echo "[5/6] Writing .env with production secrets..."
cat > /home/ubuntu/infra-autofix-agent/.env << 'ENVEOF'
FLASK_ENV=production
APP_PORT=5000
POSTGRES_USER=remediation_user
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=remediation_db
DATABASE_URL=postgresql://remediation_user:${postgres_password}@postgres:5432/remediation_db
GRAFANA_USER=admin
GRAFANA_PASSWORD=${grafana_password}
GRAFANA_PORT=3001
BOT_POLL_SECONDS=5
CPU_THRESHOLD=80
ERROR_RATE_THRESHOLD=0.2
RESPONSE_TIME_THRESHOLD_MS=500
MAX_RESTARTS_PER_5MIN=3
COOLDOWN_SECONDS=120
ENABLE_AUTO_SCALE=true
DATA_RETENTION_DAYS=180
CLEANUP_INTERVAL_HOURS=24
PROMETHEUS_PORT=9090
SLACK_WEBHOOK_URL=
GROQ_API_KEY=${groq_api_key}
GROQ_MODEL=llama-3.3-70b-versatile
ML_ENABLED=true
ENVEOF

chmod 600 /home/ubuntu/infra-autofix-agent/.env
chown ubuntu:ubuntu /home/ubuntu/infra-autofix-agent/.env
echo "    .env written (permissions: 600)"

# ── Step 6: Start all services ────────────────────────────────────────────────
# IMPORTANT: This step takes 8-12 minutes on t2.micro (slow CPU building images).
# terraform apply finishes immediately — the app becomes available ~12 min later.
echo ""
echo "[6/6] Starting Docker Compose services (this takes 8-12 minutes on t2.micro)..."
cd /home/ubuntu/infra-autofix-agent

# Run as ubuntu user (not root) because docker group membership is on ubuntu
sudo -u ubuntu docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d --build

echo ""
echo "=== Bootstrap COMPLETE at $(date) ==="
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Dashboard  -> http://$PUBLIC_IP:3000"
echo "API        -> http://$PUBLIC_IP:5000"
echo "Grafana    -> http://$PUBLIC_IP:3001"
echo "Prometheus -> http://$PUBLIC_IP:9090"

# Write a completion marker so you can check from outside:
#   curl http://<IP>:5000/health
touch /home/ubuntu/infra-autofix-setup-complete
