#!/usr/bin/env bash
# =============================================================================
# update_duckdns.sh — Keep your DuckDNS subdomain pointing to this EC2 instance
# =============================================================================
#
# AWS EC2 instances get a NEW public IP on every stop/start cycle.
# This script calls the DuckDNS API to update your subdomain automatically.
#
# SETUP (run once on your EC2 instance):
# ──────────────────────────────────────
#   1. Copy this file to the EC2 instance (it's already in the repo):
#         /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh
#
#   2. Make it executable:
#         chmod +x /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh
#
#   3. Open crontab:
#         crontab -e
#
#   4. Add this line (runs every 5 minutes, logs to ~/duckdns.log):
#         */5 * * * * DUCKDNS_DOMAIN=your-subdomain DUCKDNS_TOKEN=your-token /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh >> /home/ubuntu/duckdns.log 2>&1
#
#      Replace:
#        your-subdomain  →  the subdomain you created at duckdns.org (NOT the full hostname, just the part before .duckdns.org)
#        your-token      →  the token shown on your duckdns.org dashboard
#
# TESTING:
#   DUCKDNS_DOMAIN=your-subdomain DUCKDNS_TOKEN=your-token ./update_duckdns.sh
#
# =============================================================================

set -euo pipefail

DUCKDNS_DOMAIN="${DUCKDNS_DOMAIN:-}"
DUCKDNS_TOKEN="${DUCKDNS_TOKEN:-}"

if [[ -z "$DUCKDNS_DOMAIN" ]] || [[ -z "$DUCKDNS_TOKEN" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: DUCKDNS_DOMAIN and DUCKDNS_TOKEN must be set."
    echo "  Usage: DUCKDNS_DOMAIN=mysubdomain DUCKDNS_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx $0"
    exit 1
fi

# When ip= is left empty, DuckDNS auto-detects the calling server's public IP.
RESPONSE=$(curl -fsSL "https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=")

if [[ "$RESPONSE" == "OK" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] OK — ${DUCKDNS_DOMAIN}.duckdns.org updated successfully."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED — DuckDNS returned: ${RESPONSE}"
    exit 1
fi
