#!/usr/bin/env python3
"""
Gmail Helper Module
Provides Gmail send functionality using Google API directly.
Used by agent_service.py for sending approved emails.
"""

import os
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# Configuration
GMAIL_USER = os.getenv('GMAIL_USER', 'jonin@theshinobiproject.com')

# Paths - uses same credentials as Google Workspace MCP
CREDENTIALS_DIR = Path.home() / '.google_workspace_mcp' / 'credentials'
TOKEN_FILE = CREDENTIALS_DIR / f'{GMAIL_USER}.json'

# Scopes needed for sending - readonly was used for sync, we need send
# The token should have been generated with full gmail access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly'
]


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed token
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            return None

    if not creds or not creds.valid:
        print(f"No valid credentials found at {TOKEN_FILE}")
        print("Ensure Google Workspace MCP has been authenticated with gmail.send scope.")
        return None

    return build('gmail', 'v1', credentials=creds)


def create_message(
    to: str,
    subject: str,
    body: str,
    from_addr: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    reply_to_message_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    is_html: bool = False
) -> Dict[str, Any]:
    """
    Create a message for the Gmail API.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        from_addr: Sender address (optional, uses default)
        cc: CC recipients
        bcc: BCC recipients
        reply_to_message_id: Message-ID header for threading
        thread_id: Gmail thread ID for threading
        is_html: Whether body is HTML

    Returns:
        Message dict ready for Gmail API
    """
    if is_html:
        message = MIMEMultipart('alternative')
        message.attach(MIMEText(body, 'html'))
    else:
        message = MIMEText(body, 'plain')

    message['to'] = to
    message['subject'] = subject

    if from_addr:
        message['from'] = from_addr

    if cc:
        message['cc'] = cc

    if bcc:
        message['bcc'] = bcc

    # Threading headers
    if reply_to_message_id:
        message['In-Reply-To'] = reply_to_message_id
        message['References'] = reply_to_message_id

    # Encode the message
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    result = {'raw': raw}
    if thread_id:
        result['threadId'] = thread_id

    return result


async def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    thread_id: Optional[str] = None,
    reply_to_message_id: Optional[str] = None,
    is_html: bool = False
) -> Dict[str, Any]:
    """
    Send an email via Gmail API.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        thread_id: Gmail thread ID for replies (optional)
        reply_to_message_id: Message-ID for threading (optional)
        is_html: Whether body is HTML (default False)

    Returns:
        Dict with success status and message details
    """
    try:
        service = get_gmail_service()
        if not service:
            return {
                'success': False,
                'error': 'Gmail service not available - check credentials'
            }

        message = create_message(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            thread_id=thread_id,
            reply_to_message_id=reply_to_message_id,
            is_html=is_html
        )

        # Send the message
        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        return {
            'success': True,
            'message_id': result.get('id'),
            'thread_id': result.get('threadId'),
            'label_ids': result.get('labelIds', [])
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_email_sync(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    thread_id: Optional[str] = None,
    reply_to_message_id: Optional[str] = None,
    is_html: bool = False
) -> Dict[str, Any]:
    """
    Synchronous version of send_email for non-async contexts.
    """
    try:
        service = get_gmail_service()
        if not service:
            return {
                'success': False,
                'error': 'Gmail service not available - check credentials'
            }

        message = create_message(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            thread_id=thread_id,
            reply_to_message_id=reply_to_message_id,
            is_html=is_html
        )

        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        return {
            'success': True,
            'message_id': result.get('id'),
            'thread_id': result.get('threadId'),
            'label_ids': result.get('labelIds', [])
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    # Test the helper
    import asyncio

    async def test():
        result = await send_email(
            to='test@example.com',
            subject='Test Email from Gmail Helper',
            body='This is a test email sent via Gmail API.'
        )
        print(f"Result: {result}")

    print("Gmail Helper Test")
    print(f"Token file: {TOKEN_FILE}")
    print(f"Token exists: {TOKEN_FILE.exists()}")

    # Only run test if explicitly requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--send-test':
        asyncio.run(test())
