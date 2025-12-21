#!/usr/bin/env python3
"""
Gmail to Directus Email Sync Script
Fetches emails from Gmail and syncs to Directus emails collection.
Matches emails to clients based on domain.
"""

import os
import json
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parseaddr

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
DIRECTUS_URL = os.getenv('DIRECTUS_URL', 'http://localhost:8055')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN')
GMAIL_USER = os.getenv('GMAIL_USER', 'jonin@theshinobiproject.com')

# Your own domains - emails from/to these are "internal", match to external party
OWN_DOMAINS = {
    'theshinobiproject.com',
    'hortuscognitor.com',
    'hortuscognitor.co.uk',
    'aaronisaac.co.uk',
}

# Paths
SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_DIR = Path.home() / '.google_workspace_mcp' / 'credentials'
TOKEN_FILE = CREDENTIALS_DIR / f'{GMAIL_USER}.json'

# Client secrets from environment or file
CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use workspace-mcp's saved credentials
            if not TOKEN_FILE.exists():
                print(f"Error: No credentials found at {TOKEN_FILE}")
                print("Run the Google Workspace MCP first to authenticate.")
                return None

    return build('gmail', 'v1', credentials=creds)


def get_directus_clients():
    """Fetch all clients from Directus with their email domains."""
    headers = {'Authorization': f'Bearer {DIRECTUS_TOKEN}'}

    # Get clients
    resp = requests.get(
        f'{DIRECTUS_URL}/items/clients',
        headers=headers,
        params={'fields': 'id,company_name,email,website_url'}
    )
    resp.raise_for_status()
    clients = resp.json().get('data', [])

    # Get contacts
    resp = requests.get(
        f'{DIRECTUS_URL}/items/contacts',
        headers=headers,
        params={'fields': 'id,email,client'}
    )
    resp.raise_for_status()
    contacts = resp.json().get('data', [])

    # Build domain -> client mapping
    domain_map = {}
    email_map = {}

    for client in clients:
        client_id = client['id']

        # Map client email
        if client.get('email'):
            email = client['email'].lower()
            email_map[email] = {'client_id': client_id, 'contact_id': None}
            domain = email.split('@')[-1]
            domain_map[domain] = client_id

        # Map website domain
        if client.get('website_url'):
            url = client['website_url'].lower()
            domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            domain_map[domain] = client_id

    # Map contact emails
    for contact in contacts:
        if contact.get('email') and contact.get('client'):
            email = contact['email'].lower()
            email_map[email] = {
                'client_id': contact['client'],
                'contact_id': contact['id']
            }
            domain = email.split('@')[-1]
            if domain not in domain_map:
                domain_map[domain] = contact['client']

    return domain_map, email_map


def get_existing_gmail_ids():
    """Get set of gmail_ids already in Directus."""
    headers = {'Authorization': f'Bearer {DIRECTUS_TOKEN}'}

    resp = requests.get(
        f'{DIRECTUS_URL}/items/emails',
        headers=headers,
        params={'fields': 'gmail_id', 'limit': -1}
    )
    resp.raise_for_status()
    emails = resp.json().get('data', [])

    return {e['gmail_id'] for e in emails if e.get('gmail_id')}


def parse_email_address(addr_string):
    """Extract email address from 'Name <email>' format."""
    name, email = parseaddr(addr_string)
    return email.lower() if email else addr_string.lower()


def match_email_to_client(from_addr, to_addr, domain_map, email_map, own_domains):
    """Match email addresses to client and contact.

    Prioritises the EXTERNAL party - skips own domains to find the client.
    """
    from_email = parse_email_address(from_addr)
    to_email = parse_email_address(to_addr)

    # Determine which is external (not our domain)
    from_domain = from_email.split('@')[-1]
    to_domain = to_email.split('@')[-1]

    # Order: external first, then internal
    if from_domain in own_domains:
        # We sent this - match to recipient
        emails_to_check = [to_email, from_email]
    else:
        # We received this - match to sender
        emails_to_check = [from_email, to_email]

    # Check exact email matches first (skip own domains)
    for email in emails_to_check:
        domain = email.split('@')[-1]
        if domain not in own_domains and email in email_map:
            return email_map[email]

    # Check domain matches (skip own domains)
    for email in emails_to_check:
        domain = email.split('@')[-1]
        if domain not in own_domains and domain in domain_map:
            return {'client_id': domain_map[domain], 'contact_id': None}

    return {'client_id': None, 'contact_id': None}


def fetch_new_emails(service, max_results=50, after_date=None):
    """Fetch emails from Gmail."""
    query = ''
    if after_date:
        query = f'after:{after_date.strftime("%Y/%m/%d")}'

    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        q=query
    ).execute()

    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = {h['name'].lower(): h['value'] for h in full_msg['payload'].get('headers', [])}

        # Get body
        body = ''
        payload = full_msg['payload']
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
                elif part['mimeType'] == 'text/html' and part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')

        # Determine direction
        from_addr = headers.get('from', '')
        direction = 'inbound'
        if GMAIL_USER.lower() in from_addr.lower():
            direction = 'outbound'

        # Parse labels
        labels = full_msg.get('labelIds', [])

        emails.append({
            'gmail_id': msg['id'],
            'thread_id': full_msg.get('threadId'),
            'message_id': headers.get('message-id'),
            'from_address': from_addr,
            'to_address': headers.get('to', ''),
            'cc': headers.get('cc', ''),
            'subject': headers.get('subject', '(no subject)'),
            'body': body[:50000],  # Limit body size
            'direction': direction,
            'email_date': datetime.fromtimestamp(int(full_msg['internalDate']) / 1000).isoformat(),
            'is_read': 'UNREAD' not in labels,
            'is_important': 'IMPORTANT' in labels,
            'is_starred': 'STARRED' in labels,
            'labels': labels
        })

    return emails


def save_email_to_directus(email_data, client_id, contact_id):
    """Save email to Directus."""
    headers = {
        'Authorization': f'Bearer {DIRECTUS_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        'gmail_id': email_data['gmail_id'],
        'thread_id': email_data['thread_id'],
        'message_id': email_data['message_id'],
        'from_address': email_data['from_address'],
        'to_address': email_data['to_address'],
        'cc': email_data['cc'],
        'subject': email_data['subject'],
        'body': email_data['body'],
        'direction': email_data['direction'],
        'email_date': email_data['email_date'],
        'is_read': email_data['is_read'],
        'is_important': email_data['is_important'],
        'is_starred': email_data['is_starred'],
        'labels': email_data['labels'],
        'client': client_id,
        'contact': contact_id
    }

    resp = requests.post(
        f'{DIRECTUS_URL}/items/emails',
        headers=headers,
        json=payload
    )
    resp.raise_for_status()
    return resp.json()


def sync_emails(days_back=7, max_results=100):
    """Main sync function."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Gmail sync...")

    # Initialize
    service = get_gmail_service()
    if not service:
        return

    domain_map, email_map = get_directus_clients()
    existing_ids = get_existing_gmail_ids()

    print(f"  - Found {len(domain_map)} client domains")
    print(f"  - Found {len(email_map)} contact emails")
    print(f"  - {len(existing_ids)} emails already synced")

    # Fetch emails
    after_date = datetime.now() - timedelta(days=days_back)
    emails = fetch_new_emails(service, max_results=max_results, after_date=after_date)

    print(f"  - Fetched {len(emails)} emails from Gmail")

    # Process and save
    new_count = 0
    matched_count = 0

    for email in emails:
        if email['gmail_id'] in existing_ids:
            continue

        match = match_email_to_client(
            email['from_address'],
            email['to_address'],
            domain_map,
            email_map,
            OWN_DOMAINS
        )

        try:
            save_email_to_directus(email, match['client_id'], match['contact_id'])
            new_count += 1
            if match['client_id']:
                matched_count += 1
        except Exception as e:
            print(f"  - Error saving email {email['gmail_id']}: {e}")

    print(f"  - Saved {new_count} new emails ({matched_count} matched to clients)")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync complete.")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Sync Gmail to Directus')
    parser.add_argument('--days', type=int, default=7, help='Days back to sync')
    parser.add_argument('--max', type=int, default=100, help='Max emails to fetch')
    args = parser.parse_args()

    sync_emails(days_back=args.days, max_results=args.max)
