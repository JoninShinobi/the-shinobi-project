#!/bin/bash
# Gmail Sync Cron Script
cd /Users/aarondudfield/the-shinobi-project

export DIRECTUS_TOKEN=i6DpdwdfQbWQ5_uQElOYuuZFWyOdK1uk
export GMAIL_USER=jonin@theshinobiproject.com

/usr/bin/python3 scripts/gmail_sync.py --days 1 --max 50 >> /tmp/gmail_sync.log 2>&1
