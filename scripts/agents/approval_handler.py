"""
Approval Handler
Creates and manages human approval requests in Directus.
"""

import httpx
import os
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_ADMIN_TOKEN", "")


@dataclass
class ApprovalRequest:
    """Request for human approval"""
    prompt_type: str  # approval_needed, clarification_needed, decision_required, review_output
    question: str
    context: dict
    options: Optional[list] = None
    deadline_hours: int = 24
    assigned_to: Optional[str] = None
    agent_log_id: Optional[str] = None


async def create_approval_request(request: ApprovalRequest) -> str:
    """
    Create a human_prompts record for approval.
    Returns the created prompt ID.
    """
    deadline = datetime.utcnow() + timedelta(hours=request.deadline_hours)

    payload = {
        "status": "pending",
        "prompt_type": request.prompt_type,
        "question": request.question,
        "context": request.context,
        "options": request.options,
        "deadline": deadline.isoformat(),
        "assigned_to": request.assigned_to,
        "agent_log": request.agent_log_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DIRECTUS_URL}/items/human_prompts",
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("id")


async def check_approval_status(prompt_id: str) -> dict:
    """Check if an approval has been responded to"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DIRECTUS_URL}/items/human_prompts/{prompt_id}",
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
        )
        response.raise_for_status()
        return response.json().get("data", {})


async def create_email_draft_approval(
    email_id: str,
    draft_subject: str,
    draft_body: str,
    original_email: dict,
    agent_log_id: str = None
) -> str:
    """
    Create an approval request for an email draft.
    """
    request = ApprovalRequest(
        prompt_type="approval_needed",
        question=f"Please review and approve this email response:\n\n**Subject:** {draft_subject}\n\n**Draft:**\n{draft_body}",
        context={
            "type": "email_draft",
            "email_id": email_id,
            "draft_subject": draft_subject,
            "draft_body": draft_body,
            "original_from": original_email.get("from_address"),
            "original_subject": original_email.get("subject"),
            "original_body": original_email.get("body", "")[:500]  # First 500 chars
        },
        options=[
            {"value": "approve", "label": "Approve and Send"},
            {"value": "edit", "label": "Edit Before Sending"},
            {"value": "reject", "label": "Don't Send"}
        ],
        deadline_hours=24,
        agent_log_id=agent_log_id
    )

    return await create_approval_request(request)
