#!/bin/bash
# Shinobi Security Scanner Runner
# Runs the autonomous security scanner agent
#
# Usage:
#   ./run_security_scan.sh              # Full scan of all projects
#   ./run_security_scan.sh --project X  # Scan specific project
#   ./run_security_scan.sh --dry-run    # Scan without updating Directus

set -e

# Configuration
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(dirname "$BIN_DIR")"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/security_scan_$(date +%Y%m%d_%H%M%S).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Load environment variables
if [ -f "$SCRIPTS_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPTS_DIR/.env" | xargs)
fi

# Check required environment variables
if [ -z "$DIRECTUS_URL" ]; then
    export DIRECTUS_URL="http://localhost:8055"
    echo "[WARN] DIRECTUS_URL not set, using default: $DIRECTUS_URL"
fi

if [ -z "$DIRECTUS_ADMIN_TOKEN" ]; then
    echo "[ERROR] DIRECTUS_ADMIN_TOKEN not set"
    exit 1
fi

# Check for required tools
if ! command -v gh &> /dev/null; then
    echo "[ERROR] GitHub CLI (gh) not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not installed"
    exit 1
fi

# Check gh authentication
if ! gh auth status &> /dev/null; then
    echo "[ERROR] GitHub CLI not authenticated. Run 'gh auth login'"
    exit 1
fi

echo "=========================================="
echo "Shinobi Security Scanner"
echo "Started: $(date)"
echo "=========================================="
echo ""

# Run the scanner
cd "$SCRIPTS_DIR"

python3 -m agents.security_scanner "$@" 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=========================================="
echo "Completed: $(date)"
echo "Log file: $LOG_FILE"
echo "=========================================="

exit $EXIT_CODE
