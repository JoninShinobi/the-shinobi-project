#!/bin/bash
# Shinobi Security Scanner - Run Script
# Schedule this via cron or systemd timer on VPS
#
# Example cron (run daily at 3 AM):
#   0 3 * * * /path/to/run_security_scanner.sh >> /var/log/shinobi-scanner.log 2>&1

set -e

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(dirname "$BIN_DIR")"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"
LOG_FILE="/tmp/shinobi-security-scan.log"

# Configuration - set these via environment or modify here
export DIRECTUS_URL="${DIRECTUS_URL:-http://localhost:8055}"
export DIRECTUS_ADMIN_TOKEN="${DIRECTUS_ADMIN_TOKEN}"
export GITHUB_ORG="${GITHUB_ORG:-JoninShinobi}"

echo "=========================================="
echo "Shinobi Security Scanner"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo "ERROR: GitHub CLI (gh) not installed"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "ERROR: GitHub CLI not authenticated"
    exit 1
fi

if [ -z "$DIRECTUS_ADMIN_TOKEN" ]; then
    echo "WARNING: DIRECTUS_ADMIN_TOKEN not set - Directus updates will be skipped"
fi

# Ensure httpx is installed
python3 -c "import httpx" 2>/dev/null || pip3 install httpx -q

# Run the scanner
cd "$SCRIPTS_DIR"
python3 -m agents.security_scanner "$@"

echo "=========================================="
echo "Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
