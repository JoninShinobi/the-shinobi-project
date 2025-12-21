"""
Webhook Endpoints for External Sites
Standardized API endpoints for Kerry's Art Shop, Hannah's Courses, and client sites.
All webhooks route through the Orchestrator Agent.
"""

import os
import json
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================================
# Models
# ============================================================================

class WebhookSource(str, Enum):
    """Registered external sites"""
    KERRY_ART = "kerry_art_shop"
    HANNAH_COURSES = "hannah_courses"
    CLIENT_SITE = "client_site"
    STRIPE = "stripe"
    WOOCOMMERCE = "woocommerce"
    SHOPIFY = "shopify"
    CUSTOM = "custom"


class TransactionEvent(BaseModel):
    """E-commerce transaction from external site"""
    event_type: str = Field(..., description="purchase, refund, subscription, etc.")
    source: WebhookSource
    transaction_id: str
    customer_email: str
    customer_name: Optional[str] = None
    amount_gbp: float
    currency: str = "GBP"
    products: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    timestamp: Optional[str] = None


class ContactFormEvent(BaseModel):
    """Contact form submission from external site"""
    source: WebhookSource
    form_type: str = Field(default="contact", description="contact, quote_request, support, etc.")
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    page_url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class SupportTicketEvent(BaseModel):
    """Support request from external site"""
    source: WebhookSource
    client_site: Optional[str] = None
    customer_email: str
    customer_name: Optional[str] = None
    subject: str
    description: str
    category: str = Field(default="general")
    priority: str = Field(default="medium")
    attachments: list[str] = Field(default_factory=list)


class AnalyticsEvent(BaseModel):
    """Analytics/tracking event from external site"""
    source: WebhookSource
    event_name: str
    page_url: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: dict = Field(default_factory=dict)


class CustomEvent(BaseModel):
    """Generic webhook for custom integrations"""
    source: WebhookSource
    event_type: str
    payload: dict


# ============================================================================
# Webhook Configuration
# ============================================================================

SITE_CONFIGS: Dict[str, dict] = {
    "kerry_art_shop": {
        "name": "Kerry's Art Shop",
        "webhook_secret": os.getenv("KERRY_ART_WEBHOOK_SECRET", ""),
        "default_client_id": os.getenv("KERRY_ART_CLIENT_ID"),
        "commission_type": "standard",
        "site_url": "https://kerrysart.com",
    },
    "hannah_courses": {
        "name": "Hannah's Courses",
        "webhook_secret": os.getenv("HANNAH_COURSES_WEBHOOK_SECRET", ""),
        "default_client_id": os.getenv("HANNAH_COURSES_CLIENT_ID"),
        "commission_type": "standard",
        "site_url": "https://hannahcourses.com",
    },
    "client_site": {
        "name": "Client Site",
        "webhook_secret": os.getenv("CLIENT_WEBHOOK_SECRET", ""),
        "default_client_id": None,
        "commission_type": "standard",
    },
}


# ============================================================================
# Webhook Router
# ============================================================================

def create_webhook_app() -> FastAPI:
    """Create the webhook FastAPI application"""

    app = FastAPI(
        title="Shinobi C2 Webhooks",
        description="Standardized webhook endpoints for external sites",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately in production
        allow_credentials=True,
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Utility Functions
    # -------------------------------------------------------------------------

    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        if not secret:
            return True  # No secret configured, skip verification
        expected = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    def get_site_config(source: WebhookSource) -> dict:
        """Get configuration for a webhook source"""
        return SITE_CONFIGS.get(source.value, SITE_CONFIGS["client_site"])

    async def route_to_orchestrator(event_type: str, source: str, payload: dict):
        """Route event to the orchestrator agent"""
        # Import here to avoid circular imports
        from agents import OrchestratorAgent, AgentConfig

        orchestrator = OrchestratorAgent(
            config=AgentConfig(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
            )
        )

        result = await orchestrator.classify_and_route({
            "event_type": event_type,
            "source": source,
            "payload": payload,
            "received_at": datetime.now(timezone.utc).isoformat()
        })

        return result

    # -------------------------------------------------------------------------
    # Transaction Endpoints
    # -------------------------------------------------------------------------

    @app.post("/webhooks/transaction")
    async def handle_transaction(
        event: TransactionEvent,
        background_tasks: BackgroundTasks,
        x_webhook_signature: Optional[str] = Header(None)
    ):
        """
        Handle e-commerce transactions from external sites.
        Routes to Finance Agent for invoicing and revenue tracking.
        Routes to Client Services for customer follow-up.
        Routes to Marketing for post-purchase nurturing.
        """
        site_config = get_site_config(event.source)

        # Add site context to event
        enriched_payload = {
            **event.model_dump(),
            "site_config": site_config,
            "workflow_type": "transaction_processing"
        }

        # Queue for async processing
        background_tasks.add_task(
            route_to_orchestrator,
            "transaction",
            event.source.value,
            enriched_payload
        )

        return {
            "success": True,
            "message": "Transaction received and queued for processing",
            "transaction_id": event.transaction_id,
            "source": event.source.value
        }

    @app.post("/webhooks/transaction/{site_name}")
    async def handle_site_transaction(
        site_name: str,
        request: Request,
        background_tasks: BackgroundTasks,
        x_webhook_signature: Optional[str] = Header(None)
    ):
        """Site-specific transaction endpoint with custom payload handling"""
        body = await request.body()
        payload = json.loads(body)

        # Map site name to source
        source_map = {
            "kerry": WebhookSource.KERRY_ART,
            "kerry-art": WebhookSource.KERRY_ART,
            "hannah": WebhookSource.HANNAH_COURSES,
            "hannah-courses": WebhookSource.HANNAH_COURSES,
        }
        source = source_map.get(site_name.lower(), WebhookSource.CLIENT_SITE)

        # Normalize payload to our format
        normalized = {
            "event_type": payload.get("type", payload.get("event_type", "purchase")),
            "source": source.value,
            "transaction_id": payload.get("id", payload.get("transaction_id", "")),
            "customer_email": payload.get("email", payload.get("customer_email", "")),
            "customer_name": payload.get("name", payload.get("customer_name")),
            "amount_gbp": float(payload.get("total", payload.get("amount", 0))),
            "products": payload.get("items", payload.get("products", [])),
            "raw_payload": payload
        }

        background_tasks.add_task(
            route_to_orchestrator,
            "transaction",
            source.value,
            normalized
        )

        return {"success": True, "message": "Transaction queued", "source": source.value}

    # -------------------------------------------------------------------------
    # Contact Form Endpoints
    # -------------------------------------------------------------------------

    @app.post("/webhooks/contact")
    async def handle_contact_form(
        event: ContactFormEvent,
        background_tasks: BackgroundTasks
    ):
        """
        Handle contact form submissions.
        Routes to Sales for lead qualification.
        Routes to Client Services for response drafting.
        """
        site_config = get_site_config(event.source)

        enriched_payload = {
            **event.model_dump(),
            "site_config": site_config,
            "workflow_type": "lead_intake"
        }

        background_tasks.add_task(
            route_to_orchestrator,
            "contact_form",
            event.source.value,
            enriched_payload
        )

        return {
            "success": True,
            "message": "Contact form received",
            "source": event.source.value
        }

    # -------------------------------------------------------------------------
    # Support Endpoints
    # -------------------------------------------------------------------------

    @app.post("/webhooks/support")
    async def handle_support_request(
        event: SupportTicketEvent,
        background_tasks: BackgroundTasks
    ):
        """
        Handle support requests from external sites.
        Routes to Client Services for ticket creation and response.
        """
        site_config = get_site_config(event.source)

        enriched_payload = {
            **event.model_dump(),
            "site_config": site_config,
            "workflow_type": "support_ticket"
        }

        background_tasks.add_task(
            route_to_orchestrator,
            "support_request",
            event.source.value,
            enriched_payload
        )

        return {
            "success": True,
            "message": "Support request received",
            "source": event.source.value
        }

    # -------------------------------------------------------------------------
    # Analytics Endpoints
    # -------------------------------------------------------------------------

    @app.post("/webhooks/analytics")
    async def handle_analytics_event(
        event: AnalyticsEvent,
        background_tasks: BackgroundTasks
    ):
        """
        Handle analytics events for tracking and reporting.
        Routes to Marketing for campaign attribution.
        """
        enriched_payload = {
            **event.model_dump(),
            "workflow_type": "analytics_tracking"
        }

        background_tasks.add_task(
            route_to_orchestrator,
            "analytics",
            event.source.value,
            enriched_payload
        )

        return {"success": True, "message": "Event tracked"}

    # -------------------------------------------------------------------------
    # Custom/Generic Endpoints
    # -------------------------------------------------------------------------

    @app.post("/webhooks/custom")
    async def handle_custom_event(
        event: CustomEvent,
        background_tasks: BackgroundTasks
    ):
        """
        Handle custom webhook events.
        Orchestrator will classify and route appropriately.
        """
        enriched_payload = {
            "event_type": event.event_type,
            "source": event.source.value,
            "payload": event.payload,
            "workflow_type": "custom"
        }

        background_tasks.add_task(
            route_to_orchestrator,
            event.event_type,
            event.source.value,
            enriched_payload
        )

        return {"success": True, "message": f"Custom event '{event.event_type}' queued"}

    # -------------------------------------------------------------------------
    # Stripe Webhook Handler
    # -------------------------------------------------------------------------

    @app.post("/webhooks/stripe")
    async def handle_stripe_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature")
    ):
        """
        Handle Stripe webhook events.
        Routes to Finance for payment processing.
        """
        body = await request.body()
        payload = json.loads(body)

        event_type = payload.get("type", "unknown")
        data = payload.get("data", {}).get("object", {})

        enriched_payload = {
            "stripe_event_type": event_type,
            "stripe_event_id": payload.get("id"),
            "data": data,
            "workflow_type": "stripe_event"
        }

        background_tasks.add_task(
            route_to_orchestrator,
            f"stripe_{event_type}",
            "stripe",
            enriched_payload
        )

        return {"success": True}

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------

    @app.get("/webhooks/health")
    async def health_check():
        """Webhook service health check"""
        return {
            "status": "healthy",
            "service": "shinobi-webhooks",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "registered_sources": list(SITE_CONFIGS.keys())
        }

    return app


# ============================================================================
# Application Instance
# ============================================================================

webhook_app = create_webhook_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "webhook_endpoints:webhook_app",
        host="0.0.0.0",
        port=5003,
        reload=True
    )
