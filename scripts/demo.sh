#!/bin/bash
# Demo script to simulate various failure scenarios

set -e

echo "=========================================="
echo "Auto-Remediation Bot - Demo Scenarios"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

APP_URL="http://localhost:5000"

# Function to wait for user
wait_for_user() {
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Function to check service health
check_health() {
    echo -e "${GREEN}Current health status:${NC}"
    curl -s ${APP_URL}/api/health | jq '.'
    echo ""
}

# Scenario 1: Application crash
echo -e "${YELLOW}=== Scenario 1: Application Crash ===${NC}"
echo "This will crash the main application container."
echo "Watch the bot detect the failure and restart the container."
wait_for_user

echo -e "${RED}Triggering crash...${NC}"
curl -X POST ${APP_URL}/crash
echo ""
echo "Application crashed! Watch bot logs for remediation..."
echo ""
echo "Run: docker logs -f ar_bot"
wait_for_user

# Scenario 2: CPU spike
echo -e "${YELLOW}=== Scenario 2: CPU Spike ===${NC}"
echo "This will simulate a CPU spike for 15 seconds."
echo "Watch the bot detect high CPU and start a replica."
wait_for_user

check_health

echo -e "${RED}Triggering CPU spike (15 seconds)...${NC}"
curl -X POST "${APP_URL}/spike/cpu?duration=15"
echo ""
echo "CPU spike triggered! Monitor with: docker stats"
echo "Watch bot start replica container."
wait_for_user

# Scenario 3: Error rate spike
echo -e "${YELLOW}=== Scenario 3: High Error Rate ===${NC}"
echo "This will simulate increased error rate for 20 seconds."
echo "Watch the bot detect high errors and take action."
wait_for_user

check_health

echo -e "${RED}Triggering error spike (20 seconds)...${NC}"
curl -X POST "${APP_URL}/spike/errors?duration=20"
echo ""
echo "Error spike triggered! Sending requests to accumulate errors..."

# Send some requests to trigger errors
for i in {1..50}; do
    curl -s ${APP_URL}/ > /dev/null &
done
wait

echo "Requests sent. Watch bot logs for remediation."
wait_for_user

# Scenario 4: Manual health check
echo -e "${YELLOW}=== Scenario 4: Current System State ===${NC}"
echo "Checking current health and incidents..."
echo ""

check_health

echo -e "${GREEN}Recent incidents:${NC}"
curl -s "${APP_URL}/api/incidents?limit=5" | jq '.incidents'
echo ""

echo -e "${GREEN}Remediation history:${NC}"
curl -s "${APP_URL}/api/remediation/history?limit=5" | jq '.actions'
echo ""

# Scenario 5: Container status
echo -e "${YELLOW}=== Scenario 5: Container Status ===${NC}"
echo "Checking Docker container status..."
echo ""

docker ps -a --filter "name=ar_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${GREEN}Demo complete!${NC}"
echo ""
echo "Useful commands:"
echo "  - View bot logs:    docker logs -f ar_bot"
echo "  - View app logs:    docker logs -f ar_app"
echo "  - Check health:     curl http://localhost:5000/api/health | jq"
echo "  - View incidents:   curl http://localhost:5000/api/incidents | jq"
echo "  - Container stats:  docker stats"
echo "  - Stop all:         docker compose down"
echo ""
