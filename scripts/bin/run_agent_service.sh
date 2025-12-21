#!/bin/bash
# Shinobi Agent Service Startup Script
# Runs the AI agent webhook service for Directus automation

set -e

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(dirname "$BIN_DIR")"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

# Load environment variables if .env exists
if [ -f "$SCRIPTS_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPTS_DIR/.env" | xargs)
fi

# Default values
export DIRECTUS_URL="${DIRECTUS_URL:-http://localhost:8055}"
export AGENT_PORT="${AGENT_PORT:-5002}"

echo "========================================="
echo "  Shinobi Agent Service"
echo "========================================="
echo "Starting at: $(date '+%H:%M:%S')"
echo "Directus URL: $DIRECTUS_URL"
echo "Agent Port: $AGENT_PORT"
echo "Project Root: $PROJECT_ROOT"
echo "========================================="

# Check if Claude CLI is available
if ! command -v claude &> /dev/null; then
    echo "[ERROR] Claude CLI not found. Install with: npm install -g @anthropic/claude-code"
    exit 1
fi

# Check if required Python packages are installed
python3 -c "import fastapi, uvicorn, httpx, pydantic, anthropic" 2>/dev/null || {
    echo "[INFO] Installing required Python packages..."
    pip install -r "$SCRIPTS_DIR/requirements.txt"
}

# Run the service
echo "[INFO] Starting agent service on port $AGENT_PORT..."
cd "$SCRIPTS_DIR"
python3 agent_service.py
