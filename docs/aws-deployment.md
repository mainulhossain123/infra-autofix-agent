# AWS Deployment Guide (Free Tier)

This guide deploys the full `infra-autofix-agent` stack onto a **free-tier AWS t2.micro** instance in **ap-southeast-1 (Singapore)**.

- **AI Chat**: powered by [Groq](https://console.groq.com) (free API — `llama-3.3-70b-versatile`, better than a local 3B model)
- **No Ollama** needed — runs easily within the 1 GB t2.micro RAM limit + 4 GB swap
- **Cost**: $0.00 (AWS free tier + Groq free tier)
- **Total setup time**: ~25 minutes

---

## What You'll Need Before Starting

- An [AWS account](https://aws.amazon.com/) with free tier active
- A [Groq account](https://console.groq.com) — free signup, takes 2 minutes — for the AI chat feature
- A terminal on your machine (PowerShell or Windows Terminal)
- ~25 minutes

---

## Step 0 — Get a Free Groq API Key

This is quick and completely free.

1. Go to [console.groq.com](https://console.groq.com) and sign up with your Google or GitHub account
2. Click **API Keys** in the left sidebar
3. Click **Create API key**
4. Give it a name like `infra-autofix` and click **Submit**
5. **Copy the key** — it looks like `gsk_abc123...`. You'll paste it into `.env` in Step 7

> Groq's free tier gives you 14,400 requests/day and uses `llama-3.3-70b-versatile` — a 70B parameter model that is significantly smarter than the local `llama3.2:3b` used previously.

---

## Step 1 — Create a Key Pair (SSH Access)

You only do this once. This is how you'll SSH into your server.

1. Open the [AWS EC2 Console](https://console.aws.amazon.com/ec2)
2. In the left sidebar click **Key Pairs** (under "Network & Security")
3. Click **Create key pair**
   - Name: `infra-autofix-key`
   - Key pair type: `RSA`
   - Private key file format: `.pem` (Linux/Mac/Windows Terminal) or `.ppk` (PuTTY)
4. Click **Create key pair** — your browser downloads `infra-autofix-key.pem`
5. **Save this file somewhere safe** — you cannot download it again

On Windows (PowerShell), restrict permissions so SSH accepts it:
```powershell
icacls "C:\path\to\infra-autofix-key.pem" /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

---

## Step 2 — Create a Security Group

A Security Group is your firewall. This controls which ports are open to the internet.

1. In EC2 Console, click **Security Groups** (under "Network & Security")
2. Click **Create security group**
   - Name: `infra-autofix-sg`
   - Description: `Security group for infra-autofix-agent demo server`
   - VPC: leave as default
3. Under **Inbound rules**, click **Add rule** and add each of these:

| Type        | Protocol | Port  | Source            | Description        |
|-------------|----------|-------|-------------------|--------------------|
| SSH         | TCP      | 22    | My IP             | SSH access (you only) |
| Custom TCP  | TCP      | 3000  | Anywhere (0.0.0.0/0) | React Frontend  |
| Custom TCP  | TCP      | 5000  | Anywhere (0.0.0.0/0) | Flask API       |
| Custom TCP  | TCP      | 3001  | Anywhere (0.0.0.0/0) | Grafana         |
| Custom TCP  | TCP      | 9090  | Anywhere (0.0.0.0/0) | Prometheus      |

> **IMPORTANT**: Port 22 (SSH) should use "My IP" — this limits SSH to only your computer. Never set it to `0.0.0.0/0`.
>
> Ports 5432 (Postgres) and 3100 (Loki) are intentionally **NOT** opened — they're internal-only.

4. Click **Create security group**

---

## Step 3 — Launch the EC2 Instance

1. In EC2 Console, click **Launch Instance**

2. Fill in the details:
   - **Name**: `infra-autofix-agent`
   - **AMI**: Search for `Ubuntu Server 22.04 LTS` — choose the 64-bit (x86) version
   - **Instance type**: `t2.micro` — this is the AWS free tier instance (1 vCPU, 1 GB RAM, **free**)
   - **Key pair**: Select `infra-autofix-key` (the one you created in Step 1)
   - **Network settings**: Click "Edit" → select `infra-autofix-sg` (the security group from Step 2)
   - **Configure storage**: Change to **20 GB** gp3 (the default 8 GB is too small for Docker images)

3. Click **Launch instance**

4. Wait ~1–2 minutes for it to show "Running" in the Instances list

---

## Step 4 — Allocate an Elastic IP (Stable Public Address)

Without this, your server's IP changes every time it stops/starts.

1. In EC2 Console, click **Elastic IPs** (under "Network & Security")
2. Click **Allocate Elastic IP address** → click **Allocate**
3. Select the new IP → click **Actions** → **Associate Elastic IP address**
4. Instance: select your `infra-autofix-agent` instance → click **Associate**
5. **Note down this IP address** — this becomes your permanent public IP

---

## Step 5 — SSH Into the Server

From your local machine:

```powershell
# Replace <YOUR_ELASTIC_IP> with the IP from Step 4
# Replace the path with where you saved your .pem file
ssh -i "C:\path\to\infra-autofix-key.pem" ubuntu@<YOUR_ELASTIC_IP>
```

You should see a Ubuntu welcome message. You're now on the server.

---

## Step 6 — Run the Setup Script

Copy and paste this single command into your SSH session — it runs everything automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/mainulhossain123/infra-autofix-agent/main/scripts/aws-ec2-setup.sh | bash
```

This script (~2 minutes to run):
- Installs Docker via the official method
- Clones your public GitHub repository
- Creates `.env` from the production template
- Adds **4 GB swap** (critical — t2.micro only has 1 GB RAM; swap lets the 9 containers fit)
- Opens necessary firewall ports

---

## Step 7 — Set Your Passwords and Groq API Key

Edit the `.env` file with your secure passwords and the Groq key you copied in Step 0:

```bash
cd ~/infra-autofix-agent
nano .env
```

You must update these lines:
```
POSTGRES_PASSWORD=<pick a strong password>
DATABASE_URL=postgresql://remediation_user:<same password>@postgres:5432/remediation_db
GRAFANA_PASSWORD=<pick a strong password>
GROQ_API_KEY=gsk_<your key from Step 0>
```

To generate strong passwords:
```bash
openssl rand -base64 24
```

When done, press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 8 — Start All Services

Apply docker group permissions (so you don't need sudo), then start everything:

```bash
newgrp docker

cd ~/infra-autofix-agent

# Free-tier stack (no Ollama — uses Groq API for AI chat):
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

The first `--build` takes **8–12 minutes** on t2.micro (slow single-core CPU building images). Subsequent restarts are under a minute.

Check all containers started:
```bash
docker compose ps
```

You should see 8 containers with `Up` status: `postgres`, `app`, `bot`, `frontend`, `prometheus`, `grafana`, `loki`, `promtail`.

---

## Step 9 — Verify AI Chat Works

Test the AI chat endpoint from the server itself:

```bash
curl -s -X POST http://localhost:5000/api/ml/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "How many incidents are there?"}' | python3 -m json.tool
```

You should get a JSON response with an `"response"` field containing the AI's answer. If you see `"AI service not configured"`, check that `GROQ_API_KEY` is set correctly in `.env` and restart: `docker compose restart app`.

---

## Step 10 — Access the Application

Replace `<YOUR_ELASTIC_IP>` with your actual IP from Step 4:

| Service | URL | Login |
|---|---|---|
| **React Dashboard** | `http://<YOUR_ELASTIC_IP>:3000` | — |
| **Flask API** | `http://<YOUR_ELASTIC_IP>:5000` | — |
| **Grafana** | `http://<YOUR_ELASTIC_IP>:3001` | admin / your password |
| **Prometheus** | `http://<YOUR_ELASTIC_IP>:9090` | — |
| **Health Check** | `http://<YOUR_ELASTIC_IP>:5000/health` | — |

The main URL to share with people: **`http://<YOUR_ELASTIC_IP>:3000`**

---

## Managing Your Instance

### Stop (to save money when not demoing)
In AWS Console → EC2 → Instances → select your instance → **Instance state** → **Stop instance**

The Elastic IP stays, so your URL doesn't change.

### Start again
Same menu → **Start instance**. Wait ~1 minute, then everything is back up automatically (containers are set to `restart: unless-stopped`).

### View logs
```bash
ssh -i "infra-autofix-key.pem" ubuntu@<YOUR_ELASTIC_IP>
cd ~/infra-autofix-agent
docker compose logs -f app   # Flask app logs
docker compose logs -f bot   # Bot logs
```

### Restart a specific service
```bash
docker compose restart app
```

### Update to new code (after a git push)
```bash
cd ~/infra-autofix-agent
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Cost Summary

| Resource | Detail | Cost |
|---|---|---|
| EC2 t2.micro (running) | 750 free hrs/month | **$0** |
| EC2 t2.micro (stopped) | No compute charge | **$0** |
| EBS storage 20 GB gp3 | 30 GB free per month | **$0** |
| Elastic IP (attached) | Free while instance runs | **$0** |
| Elastic IP (detached) | ~$0.005/hr | ~$0.12/day |
| Groq API | 14,400 req/day free | **$0** |
| **Total** | | **$0** |

> The only way to incur charges: detach/release your Elastic IP without deleting it, or run more than 750 hours/month (impossible with one instance in a 31-day month).

---

## Troubleshooting

**Containers not starting:**
```bash
docker compose logs <service-name>
```

**Out of memory:**
```bash
free -h        # Check available RAM + swap
docker stats   # See per-container memory usage
```

If containers are OOM-killed, the 4 GB swap file (created by the setup script) should prevent this. Verify swap is active: `swapon --show`

**Can't connect to the app:**
- Check the Security Group inbound rules (Step 2) — most connectivity issues are security group misconfigurations
- Verify the instance is running and has the correct Elastic IP associated
- Run `docker compose ps` on the server to confirm containers are Up

**Frontend shows "API connection failed":**
The frontend connects to the API using the browser URL's hostname, so it should auto-resolve. If not, check that port 5000 is open in the Security Group.
