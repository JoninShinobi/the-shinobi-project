"""
Twilio WhatsApp Webhook Handler
Receives incoming WhatsApp messages and creates records in Directus
"""

import os
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from twilio.request_validator import RequestValidator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_directus_client():
    """Get configured Directus client"""
    # Import here to avoid circular dependencies
    import httpx

    directus_url = os.getenv("DIRECTUS_URL", "http://localhost:8055")
    directus_token = os.getenv("DIRECTUS_ADMIN_TOKEN")

    if not directus_token:
        raise ValueError("DIRECTUS_ADMIN_TOKEN environment variable not set")

    return {
        "url": directus_url,
        "token": directus_token
    }


async def create_whatsapp_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create WhatsApp message record in Directus"""
    import httpx

    client_config = await get_directus_client()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{client_config['url']}/items/whatsapp_messages",
            json=data,
            headers={
                "Authorization": f"Bearer {client_config['token']}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()["data"]


@router.post("/twilio/whatsapp/incoming")
async def handle_incoming_whatsapp(request: Request):
    """
    Twilio webhook for incoming WhatsApp messages

    Endpoint: POST /twilio/whatsapp/incoming
    Content-Type: application/x-www-form-urlencoded

    Twilio Documentation:
    https://www.twilio.com/docs/whatsapp/tutorial/send-and-receive-media-messages-whatsapp-python
    """

    # 1. Validate Twilio signature (security)
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not twilio_auth_token:
        logger.error("TWILIO_AUTH_TOKEN not set")
        raise HTTPException(status_code=500, detail="Server configuration error")

    validator = RequestValidator(twilio_auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    # Get form data for validation
    form_data = await request.form()
    form_dict = dict(form_data)

    # Validate signature
    if not validator.validate(url, form_dict, signature):
        logger.warning(f"Invalid Twilio signature from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid signature")

    logger.info(f"Valid Twilio webhook received from {form_dict.get('From', 'unknown')}")

    # 2. Extract message data
    from_number = form_dict.get("From", "").replace("whatsapp:", "")
    to_number = form_dict.get("To", "").replace("whatsapp:", "")
    body = form_dict.get("Body", "")
    num_media = int(form_dict.get("NumMedia", "0"))

    # Extract media URLs if present
    media_urls = []
    for i in range(num_media):
        media_url = form_dict.get(f"MediaUrl{i}")
        if media_url:
            media_urls.append(media_url)

    message_data = {
        "message_sid": form_dict.get("MessageSid"),
        "account_sid": form_dict.get("AccountSid"),
        "from_number": from_number,
        "to_number": to_number,
        "body": body,
        "media_urls": media_urls if media_urls else None,
        "direction": "inbound",
        "status": "received",
        "verification_status": "pending"
    }

    # 3. Create record in Directus
    try:
        whatsapp_record = await create_whatsapp_message(message_data)
        logger.info(f"Created WhatsApp message record: {whatsapp_record['id']}")

        # 4. Return success response to Twilio
        return {
            "status": "received",
            "message_id": whatsapp_record["id"]
        }

    except Exception as e:
        logger.error(f"Failed to create WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get("/twilio/whatsapp/health")
async def health_check():
    """Health check endpoint for webhook"""
    return {"status": "ok", "service": "whatsapp_webhook"}
