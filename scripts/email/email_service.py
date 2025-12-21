#!/usr/bin/env python3
"""
Shinobi C2 - Email Service
SendGrid integration for automated email workflows
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Email, To, Content, Attachment, FileContent,
    FileName, FileType, Disposition, ContentId,
    TrackingSettings, ClickTracking, OpenTracking
)
import base64

# Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "i6DpdwdfQbWQ5_uQElOYuuZFWyOdK1uk")

FROM_EMAIL = os.getenv("FROM_EMAIL", "jonin@theshinobiproject.com")
FROM_NAME = os.getenv("FROM_NAME", "The Shinobi Project")

directus_headers = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json"
}


class ShinobiEmailService:
    """Email service for Shinobi C2 automated workflows"""

    def __init__(self):
        if not SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY environment variable not set")
        self.sg = SendGridAPIClient(SENDGRID_API_KEY)
        self.system_config = self._load_system_config()

    def _load_system_config(self) -> Dict[str, Any]:
        """Load system configuration from Directus"""
        try:
            response = requests.get(
                f"{DIRECTUS_URL}/items/system_config/1",
                headers=directus_headers
            )
            if response.status_code == 200:
                return response.json().get("data", {})
        except Exception as e:
            print(f"Warning: Could not load system config: {e}")

        # Defaults
        return {
            "booking_url": "",
            "kickoff_booking_url": "",
            "logo_url": "",
            "company_address": "The Shinobi Project",
            "feedback_url": "",
            "from_email": FROM_EMAIL,
            "from_name": FROM_NAME
        }

    def _get_template(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch email template from Directus by slug"""
        try:
            response = requests.get(
                f"{DIRECTUS_URL}/items/email_templates",
                headers=directus_headers,
                params={"filter[slug][_eq]": slug}
            )
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    return data[0]
        except Exception as e:
            print(f"Error fetching template {slug}: {e}")
        return None

    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace {{variable}} placeholders with actual values"""
        if not text:
            return ""

        # Add system config variables
        all_vars = {
            **self.system_config,
            **variables
        }

        def replace_match(match):
            var_name = match.group(1).strip()
            value = all_vars.get(var_name, match.group(0))
            return str(value) if value is not None else ""

        return re.sub(r'\{\{([^}]+)\}\}', replace_match, text)

    def _format_currency(self, amount: float, currency: str = "GBP") -> str:
        """Format amount as currency"""
        symbols = {"GBP": "£", "USD": "$", "EUR": "€"}
        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"

    def _format_date(self, date_str: str, format_type: str = "long") -> str:
        """Format date string for display"""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if format_type == "long":
                return dt.strftime("%A, %d %B %Y")
            elif format_type == "short":
                return dt.strftime("%d/%m/%Y")
            elif format_type == "time":
                return dt.strftime("%H:%M")
            elif format_type == "datetime":
                return dt.strftime("%A, %d %B at %H:%M")
        except:
            return date_str
        return date_str

    def _log_email(self,
                   template_slug: str,
                   to_email: str,
                   subject: str,
                   client_id: Optional[str] = None,
                   contact_id: Optional[str] = None,
                   project_id: Optional[str] = None,
                   success: bool = True,
                   error_message: Optional[str] = None):
        """Log sent email to communication_log"""
        try:
            payload = {
                "communication_type": "email",
                "direction": "outbound",
                "subject": subject,
                "summary": f"Automated email: {template_slug}",
                "timestamp": datetime.utcnow().isoformat(),
                "full_content": f"Template: {template_slug}, To: {to_email}"
            }

            if client_id:
                payload["client"] = client_id
            if contact_id:
                payload["contact"] = contact_id
            if project_id:
                payload["project"] = project_id

            requests.post(
                f"{DIRECTUS_URL}/items/communication_log",
                headers=directus_headers,
                json=payload
            )
        except Exception as e:
            print(f"Warning: Could not log email: {e}")

    def send_template_email(self,
                            template_slug: str,
                            to_email: str,
                            to_name: Optional[str] = None,
                            variables: Optional[Dict[str, Any]] = None,
                            attachments: Optional[List[Dict]] = None,
                            client_id: Optional[str] = None,
                            contact_id: Optional[str] = None,
                            project_id: Optional[str] = None) -> bool:
        """
        Send an email using a template from Directus

        Args:
            template_slug: The slug of the template to use
            to_email: Recipient email address
            to_name: Recipient name (optional)
            variables: Dictionary of variables to replace in template
            attachments: List of attachment dicts with 'content', 'filename', 'type'
            client_id: Associated client ID for logging
            contact_id: Associated contact ID for logging
            project_id: Associated project ID for logging

        Returns:
            bool: True if email sent successfully
        """
        variables = variables or {}

        # Get template
        template = self._get_template(template_slug)
        if not template:
            print(f"Template not found: {template_slug}")
            return False

        # Process variables
        subject = self._replace_variables(template.get("subject", ""), variables)
        html_content = self._replace_variables(template.get("body_html", ""), variables)
        text_content = self._replace_variables(template.get("body_text", ""), variables)

        # Build email
        message = Mail(
            from_email=Email(
                self.system_config.get("from_email", FROM_EMAIL),
                self.system_config.get("from_name", FROM_NAME)
            ),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        # Add plain text version
        if text_content:
            message.add_content(Content("text/plain", text_content))

        # Add attachments
        if attachments:
            for att in attachments:
                attachment = Attachment(
                    FileContent(att.get("content", "")),
                    FileName(att.get("filename", "attachment")),
                    FileType(att.get("type", "application/octet-stream")),
                    Disposition("attachment")
                )
                message.add_attachment(attachment)

        # Enable tracking
        message.tracking_settings = TrackingSettings(
            click_tracking=ClickTracking(True, True),
            open_tracking=OpenTracking(True)
        )

        # Send email
        try:
            response = self.sg.send(message)
            success = response.status_code in [200, 201, 202]

            if success:
                print(f"✓ Email sent: {template_slug} -> {to_email}")
                self._log_email(
                    template_slug, to_email, subject,
                    client_id, contact_id, project_id,
                    success=True
                )
            else:
                print(f"✗ Email failed: {response.status_code}")
                self._log_email(
                    template_slug, to_email, subject,
                    client_id, contact_id, project_id,
                    success=False,
                    error_message=str(response.body)
                )

            return success

        except Exception as e:
            print(f"✗ Email error: {e}")
            self._log_email(
                template_slug, to_email, subject,
                client_id, contact_id, project_id,
                success=False,
                error_message=str(e)
            )
            return False

    def send_welcome_email(self, lead_id: str) -> bool:
        """Send welcome email to new lead"""
        # Get lead with contact
        response = requests.get(
            f"{DIRECTUS_URL}/items/leads/{lead_id}",
            headers=directus_headers,
            params={"fields": "*,contact.*,company.*"}
        )

        if response.status_code != 200:
            print(f"Could not fetch lead: {lead_id}")
            return False

        lead = response.json().get("data", {})
        contact = lead.get("contact", {})
        company = lead.get("company", {})

        if not contact or not contact.get("email"):
            print(f"No contact email for lead: {lead_id}")
            return False

        return self.send_template_email(
            template_slug="welcome",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "company_name": company.get("company_name", "")
            },
            client_id=company.get("id") if company else None,
            contact_id=contact.get("id")
        )

    def send_pre_meeting_reminder(self, event_id: str) -> bool:
        """Send pre-meeting reminder"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/calendar_events/{event_id}",
            headers=directus_headers,
            params={"fields": "*,attendees_contacts.*,client.*"}
        )

        if response.status_code != 200:
            return False

        event = response.json().get("data", {})
        contacts = event.get("attendees_contacts", [])

        if not contacts:
            return False

        contact = contacts[0] if isinstance(contacts, list) else contacts

        return self.send_template_email(
            template_slug="pre_meeting",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "meeting_date": self._format_date(event.get("start_datetime", ""), "long"),
                "meeting_time": self._format_date(event.get("start_datetime", ""), "time"),
                "video_call_url": event.get("video_call_url", ""),
                "reschedule_url": self.system_config.get("booking_url", "")
            },
            client_id=event.get("client"),
            contact_id=contact.get("id")
        )

    def send_proposal_notification(self, proposal_id: str) -> bool:
        """Send proposal notification"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/proposals/{proposal_id}",
            headers=directus_headers,
            params={"fields": "*,contact.*,client.*"}
        )

        if response.status_code != 200:
            return False

        proposal = response.json().get("data", {})
        contact = proposal.get("contact", {})
        client = proposal.get("client", {})

        if not contact or not contact.get("email"):
            return False

        return self.send_template_email(
            template_slug="proposal",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "company_name": client.get("company_name", ""),
                "project_name": proposal.get("opportunity_name", "Your Project"),
                "total_value": self._format_currency(proposal.get("total_value", 0)),
                "expiration_date": self._format_date(proposal.get("expiration_date", ""), "long"),
                "proposal_url": proposal.get("proposal_document", "")
            },
            client_id=client.get("id") if client else None,
            contact_id=contact.get("id")
        )

    def send_onboarding_email(self, contract_id: str) -> bool:
        """Send onboarding email when contract activated"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/contracts/{contract_id}",
            headers=directus_headers,
            params={"fields": "*,client.*,project.*,project.project_manager.*"}
        )

        if response.status_code != 200:
            return False

        contract = response.json().get("data", {})
        client = contract.get("client", {})
        project = contract.get("project", {})

        # Get primary contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_primary_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            return False

        contact = contacts[0]
        pm = project.get("project_manager", {})

        return self.send_template_email(
            template_slug="onboarding",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "company_name": client.get("company_name", ""),
                "project_manager": f"{pm.get('first_name', '')} {pm.get('last_name', '')}".strip() if pm else "Your Project Lead",
                "project_email": project.get("project_email", FROM_EMAIL)
            },
            client_id=client.get("id"),
            contact_id=contact.get("id"),
            project_id=project.get("id") if project else None
        )

    def send_milestone_update(self, milestone_id: str) -> bool:
        """Send milestone completion notification"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/milestones/{milestone_id}",
            headers=directus_headers,
            params={"fields": "*,project.*,project.client.*"}
        )

        if response.status_code != 200:
            return False

        milestone = response.json().get("data", {})
        project = milestone.get("project", {})
        client = project.get("client", {})

        # Get primary contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_primary_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            return False

        contact = contacts[0]

        # Get next milestone
        next_milestone_response = requests.get(
            f"{DIRECTUS_URL}/items/milestones",
            headers=directus_headers,
            params={
                "filter[project][_eq]": project.get("id"),
                "filter[status][_neq]": "completed",
                "sort": "sort",
                "limit": 1
            }
        )
        next_milestones = next_milestone_response.json().get("data", [])
        next_milestone_name = next_milestones[0].get("name", "Final Review") if next_milestones else "Final Review"

        return self.send_template_email(
            template_slug="milestone",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "milestone_name": milestone.get("name", ""),
                "milestone_description": milestone.get("description", ""),
                "project_name": project.get("name", ""),
                "completion_percentage": project.get("completion_percentage", 0),
                "next_milestone_name": next_milestone_name
            },
            client_id=client.get("id"),
            contact_id=contact.get("id"),
            project_id=project.get("id")
        )

    def send_invoice_notification(self, invoice_id: str) -> bool:
        """Send invoice notification"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/invoices/{invoice_id}",
            headers=directus_headers,
            params={"fields": "*,client.*,project.*"}
        )

        if response.status_code != 200:
            return False

        invoice = response.json().get("data", {})
        client = invoice.get("client", {})
        project = invoice.get("project", {})

        # Get billing contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_billing_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            # Fall back to primary contact
            contact_response = requests.get(
                f"{DIRECTUS_URL}/items/contacts",
                headers=directus_headers,
                params={
                    "filter[client][_eq]": client.get("id"),
                    "filter[is_primary_contact][_eq]": True
                }
            )
            contacts = contact_response.json().get("data", [])

        if not contacts:
            return False

        contact = contacts[0]

        # Build Stripe payment URL if available
        stripe_id = invoice.get("stripe_invoice_id")
        payment_url = f"https://invoice.stripe.com/i/{stripe_id}" if stripe_id else ""

        return self.send_template_email(
            template_slug="invoice",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "company_name": client.get("company_name", ""),
                "invoice_number": invoice.get("invoice_number", ""),
                "total_amount": self._format_currency(invoice.get("total_amount", 0)),
                "due_date": self._format_date(invoice.get("due_date", ""), "long"),
                "project_name": project.get("name", "") if project else "",
                "stripe_payment_url": payment_url
            },
            client_id=client.get("id"),
            contact_id=contact.get("id"),
            project_id=project.get("id") if project else None
        )

    def send_payment_reminder(self, invoice_id: str) -> bool:
        """Send payment reminder for overdue invoice"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/invoices/{invoice_id}",
            headers=directus_headers,
            params={"fields": "*,client.*"}
        )

        if response.status_code != 200:
            return False

        invoice = response.json().get("data", {})
        client = invoice.get("client", {})

        # Calculate days overdue
        due_date = datetime.fromisoformat(invoice.get("due_date", "").replace("Z", "+00:00"))
        days_overdue = (datetime.now(due_date.tzinfo) - due_date).days

        # Get billing contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_billing_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            contact_response = requests.get(
                f"{DIRECTUS_URL}/items/contacts",
                headers=directus_headers,
                params={
                    "filter[client][_eq]": client.get("id"),
                    "filter[is_primary_contact][_eq]": True
                }
            )
            contacts = contact_response.json().get("data", [])

        if not contacts:
            return False

        contact = contacts[0]

        stripe_id = invoice.get("stripe_invoice_id")
        payment_url = f"https://invoice.stripe.com/i/{stripe_id}" if stripe_id else ""

        return self.send_template_email(
            template_slug="payment_reminder",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "invoice_number": invoice.get("invoice_number", ""),
                "amount_remaining": self._format_currency(invoice.get("amount_remaining", invoice.get("total_amount", 0))),
                "days_overdue": days_overdue,
                "stripe_payment_url": payment_url
            },
            client_id=client.get("id"),
            contact_id=contact.get("id")
        )

    def send_project_completion(self, project_id: str) -> bool:
        """Send project completion email"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/projects/{project_id}",
            headers=directus_headers,
            params={"fields": "*,client.*"}
        )

        if response.status_code != 200:
            return False

        project = response.json().get("data", {})
        client = project.get("client", {})

        # Get primary contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_primary_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            return False

        contact = contacts[0]

        return self.send_template_email(
            template_slug="completion",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "project_name": project.get("name", ""),
                "deliverables_summary": project.get("requirements", "All deliverables completed as specified."),
                "live_url": project.get("live_url", ""),
                "admin_url": project.get("admin_url", ""),
                "docs_url": ""  # Link to handover docs
            },
            client_id=client.get("id"),
            contact_id=contact.get("id"),
            project_id=project.get("id")
        )

    def send_completion_pack(self, project_id: str) -> bool:
        """Send completion pack email (3 days after project completion)"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/projects/{project_id}",
            headers=directus_headers,
            params={"fields": "*,client.*"}
        )

        if response.status_code != 200:
            return False

        project = response.json().get("data", {})
        client = project.get("client", {})

        # Get primary contact
        contact_response = requests.get(
            f"{DIRECTUS_URL}/items/contacts",
            headers=directus_headers,
            params={
                "filter[client][_eq]": client.get("id"),
                "filter[is_primary_contact][_eq]": True
            }
        )

        contacts = contact_response.json().get("data", [])
        if not contacts:
            return False

        contact = contacts[0]

        return self.send_template_email(
            template_slug="completion_pack",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", ""),
                "company_name": client.get("company_name", ""),
                "completion_pack_url": ""  # Link to Google Drive folder
            },
            client_id=client.get("id"),
            contact_id=contact.get("id"),
            project_id=project.get("id")
        )

    def send_re_engagement(self, lead_id: str) -> bool:
        """Send re-engagement email to inactive lead"""
        response = requests.get(
            f"{DIRECTUS_URL}/items/leads/{lead_id}",
            headers=directus_headers,
            params={"fields": "*,contact.*"}
        )

        if response.status_code != 200:
            return False

        lead = response.json().get("data", {})
        contact = lead.get("contact", {})

        if not contact or not contact.get("email"):
            return False

        return self.send_template_email(
            template_slug="re_engagement",
            to_email=contact.get("email"),
            to_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            variables={
                "contact_first_name": contact.get("first_name", "")
            },
            contact_id=contact.get("id")
        )


# Scheduled job functions
def process_pre_meeting_reminders():
    """Find meetings tomorrow and send reminders"""
    service = ShinobiEmailService()

    tomorrow_start = (datetime.utcnow() + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    tomorrow_end = tomorrow_start + timedelta(days=1)

    response = requests.get(
        f"{DIRECTUS_URL}/items/calendar_events",
        headers=directus_headers,
        params={
            "filter[event_type][_eq]": "client_meeting",
            "filter[start_datetime][_gte]": tomorrow_start.isoformat(),
            "filter[start_datetime][_lt]": tomorrow_end.isoformat()
        }
    )

    if response.status_code != 200:
        return

    events = response.json().get("data", [])
    print(f"Found {len(events)} meetings tomorrow")

    for event in events:
        service.send_pre_meeting_reminder(event.get("id"))


def process_overdue_invoices():
    """Find overdue invoices and send reminders"""
    service = ShinobiEmailService()

    response = requests.get(
        f"{DIRECTUS_URL}/items/invoices",
        headers=directus_headers,
        params={
            "filter[status][_nin]": "paid,cancelled",
            "filter[due_date][_lt]": datetime.utcnow().date().isoformat()
        }
    )

    if response.status_code != 200:
        return

    invoices = response.json().get("data", [])
    print(f"Found {len(invoices)} overdue invoices")

    for invoice in invoices:
        service.send_payment_reminder(invoice.get("id"))

        # Update status to overdue if still 'sent'
        if invoice.get("status") == "sent":
            requests.patch(
                f"{DIRECTUS_URL}/items/invoices/{invoice.get('id')}",
                headers=directus_headers,
                json={"status": "overdue"}
            )


def process_inactive_leads():
    """Find leads inactive for 14+ days and send re-engagement"""
    service = ShinobiEmailService()

    cutoff_date = (datetime.utcnow() - timedelta(days=14)).isoformat()

    response = requests.get(
        f"{DIRECTUS_URL}/items/leads",
        headers=directus_headers,
        params={
            "filter[lead_status][_nin]": "won,lost",
            "filter[last_activity_date][_lt]": cutoff_date
        }
    )

    if response.status_code != 200:
        return

    leads = response.json().get("data", [])
    print(f"Found {len(leads)} inactive leads")

    for lead in leads:
        service.send_re_engagement(lead.get("id"))

        # Update last activity date
        requests.patch(
            f"{DIRECTUS_URL}/items/leads/{lead.get('id')}",
            headers=directus_headers,
            json={"last_activity_date": datetime.utcnow().isoformat()}
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python email_service.py <command> [args]")
        print("\nCommands:")
        print("  test                    - Test email configuration")
        print("  send <template> <email> - Send test email")
        print("  reminders               - Process pre-meeting reminders")
        print("  overdue                 - Process overdue invoices")
        print("  reengagement            - Process inactive leads")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        service = ShinobiEmailService()
        print("✓ Email service configured successfully")
        print(f"  From: {service.system_config.get('from_email', FROM_EMAIL)}")
        print(f"  SendGrid API: {'Configured' if SENDGRID_API_KEY else 'NOT SET'}")

    elif command == "send":
        if len(sys.argv) < 4:
            print("Usage: python email_service.py send <template_slug> <email>")
            sys.exit(1)

        template_slug = sys.argv[2]
        to_email = sys.argv[3]

        service = ShinobiEmailService()
        success = service.send_template_email(
            template_slug=template_slug,
            to_email=to_email,
            variables={
                "contact_first_name": "Test",
                "company_name": "Test Company"
            }
        )

        if success:
            print(f"✓ Test email sent to {to_email}")
        else:
            print(f"✗ Failed to send email")

    elif command == "reminders":
        process_pre_meeting_reminders()

    elif command == "overdue":
        process_overdue_invoices()

    elif command == "reengagement":
        process_inactive_leads()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
