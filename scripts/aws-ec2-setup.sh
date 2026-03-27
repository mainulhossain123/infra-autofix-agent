#!/bin/bash
# =============================================================================
# AWS EC2 Setup Script for infra-autofix-agent
# Free-tier deployment: Ubuntu 22.04 + t2.micro + Groq API (no Ollama)
# Region: ap-southeast-1 (Singapore)
# =============================================================================
# Run this on a FRESH Ubuntu 22.04 LTS t2.micro EC2 instance after SSH-ing in.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/mainulhossain123/infra-autofix-agent/main/scripts/aws-ec2-setup.sh | bash
#
# After running, follow the NEXT STEPS printed at the end.
# =============================================================================

set -e  # Exit immediately on any error

REPO_URL="https://github.com/mainulhossain123/infra-autofix-agent.git"
REPO_DIR="$HOME/infra-autofix-agent"

echo ""
echo "============================================================"
echo "  infra-autofix-agent — Free Tier EC2 Setup"
echo "  Instance: t2.micro | Region: ap-southeast-1"
echo "  AI: Groq API (llama-3.3-70b) — no Ollama needed"
echo "============================================================"
echo ""

# --- Step 1: System Update ---
echo "[1/6] Updating system packages..."
sudo apt-get update -y -q
sudo apt-get upgrade -y -q
sudo apt-get install -y -q ca-certificates curl gnupg git nano

# --- Step 2: Install Docker (official method) ---
echo "[2/6] Installing Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y -q
sudo apt-get install -y -q \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker "$USER"
echo "    Docker installed: $(docker --version)"

# --- Step 3: Clone the repository ---
echo "[3/6] Cloning repository..."
if [ -d "$REPO_DIR" ]; then
  echo "    Repository exists — pulling latest..."
  cd "$REPO_DIR" && git pull
else
  git clone "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

# --- Step 4: Configure environment ---
echo "[4/6] Creating .env from production template..."
if [ ! -f "$REPO_DIR/.env" ]; then
  cp "$REPO_DIR/.env.production.example" "$REPO_DIR/.env"
  echo "    Created .env — you must edit it before starting containers"
else
  echo "    .env already exists — not overwriting"
fi

# --- Step 5: Open OS firewall ports ---
echo "[5/6] Configuring UFW firewall..."
sudo ufw allow 22/tcp   comment 'SSH'        > /dev/null 2>&1 || true
sudo ufw allow 3000/tcp comment 'Frontend'   > /dev/null 2>&1 || true
sudo ufw allow 5000/tcp comment 'API'        > /dev/null 2>&1 || true
sudo ufw allow 3001/tcp comment 'Grafana'    > /dev/null 2>&1 || true
sudo ufw allow 9090/tcp comment 'Prometheus' > /dev/null 2>&1 || true
# Postgres (5432) is internal only — never exposed

# --- Step 6: Create swap space (CRITICAL for t2.micro with 1GB RAM) ---
echo "[6/6] Creating 4GB swap file (required for t2.micro)..."
if [ ! -f /swapfile ]; then
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
  echo "    4GB swap created and enabled"
else
  echo "    Swap already exists — skipping"
fi

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_IP')

echo ""
echo "============================================================"
echo "  SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "  1. Apply docker group membership (avoids logout/login):"
echo "     newgrp docker"
echo ""
echo "  2. Edit .env — set your passwords AND your Groq API key:"
echo "     nano $REPO_DIR/.env"
echo "     (Get a free Groq key at https://console.groq.com)"
echo ""
echo "  3. Start all services:"
echo "     cd $REPO_DIR"
echo "     docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
echo ""
echo "  4. Check all containers are running:"
echo "     docker compose ps"
echo ""
echo "  5. Access the app:"
echo "     Dashboard  -> http://$PUBLIC_IP:3000"
echo "     API        -> http://$PUBLIC_IP:5000"
echo "     Grafana    -> http://$PUBLIC_IP:3001"
echo "     Prometheus -> http://$PUBLIC_IP:9090"
echo ""
