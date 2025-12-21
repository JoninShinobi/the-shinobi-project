#!/bin/bash
# Shinobi C2 - Scheduled Email Jobs
# Add to crontab: crontab -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPTS_DIR"

# Load environment variables
export SENDGRID_API_KEY="your_sendgrid_api_key_here"
export DIRECTUS_URL="http://localhost:8055"
export DIRECTUS_TOKEN="i6DpdwdfQbWQ5_uQElOYuuZFWyOdK1uk"
export FROM_EMAIL="jonin@theshinobiproject.com"
export FROM_NAME="The Shinobi Project"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the specified job
case "$1" in
    "reminders")
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running pre-meeting reminders..."
        python -m email.email_service reminders
        ;;
    "overdue")
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking overdue invoices..."
        python -m email.email_service overdue
        ;;
    "reengagement")
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing inactive leads..."
        python -m email.email_service reengagement
        ;;
    "all")
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running all scheduled jobs..."
        python -m email.email_service reminders
        python -m email.email_service overdue
        python -m email.email_service reengagement
        ;;
    *)
        echo "Usage: $0 {reminders|overdue|reengagement|all}"
        exit 1
        ;;
esac

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Job completed."
