"""
Shinobi Email Module
Email handling, Gmail sync, and email service functionality.
"""

from .gmail_helper import send_email, send_email_sync, create_message, get_gmail_service
from .gmail_sync import sync_emails
from .email_service import ShinobiEmailService

__all__ = [
    'send_email',
    'send_email_sync',
    'create_message',
    'get_gmail_service',
    'sync_emails',
    'ShinobiEmailService',
]
