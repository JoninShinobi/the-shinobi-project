"""
Twilio Integration Module
Handles WhatsApp messaging via Twilio API
"""

from .whatsapp_webhook import router as whatsapp_router

__all__ = ["whatsapp_router"]
