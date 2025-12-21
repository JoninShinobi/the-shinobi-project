#!/usr/bin/env python3
"""
Shinobi C2 - Email Webhook Handler
Flask server to receive Directus Flow webhooks and send emails via SendGrid

Run with: python email_webhook.py
Or use gunicorn: gunicorn -w 2 -b 0.0.0.0:5001 email_webhook:app
"""

import os
import json
from flask import Flask, request, jsonify
from .email_service import ShinobiEmailService

app = Flask(__name__)

# Initialize email service
email_service = None

def get_email_service():
    global email_service
    if email_service is None:
        email_service = ShinobiEmailService()
    return email_service


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "shinobi-email"})


@app.route('/webhook/email', methods=['POST'])
def handle_email_webhook():
    """
    Generic email webhook handler
    Expects JSON body with:
    - template: template slug
    - to_email: recipient email
    - to_name: recipient name (optional)
    - variables: dict of template variables
    - client_id, contact_id, project_id (optional for logging)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        template = data.get("template")
        to_email = data.get("to_email")

        if not template or not to_email:
            return jsonify({"error": "Missing required fields: template, to_email"}), 400

        service = get_email_service()
        success = service.send_template_email(
            template_slug=template,
            to_email=to_email,
            to_name=data.get("to_name"),
            variables=data.get("variables", {}),
            client_id=data.get("client_id"),
            contact_id=data.get("contact_id"),
            project_id=data.get("project_id")
        )

        if success:
            return jsonify({"status": "sent", "template": template, "to": to_email})
        else:
            return jsonify({"status": "failed", "template": template, "to": to_email}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/lead/welcome', methods=['POST'])
def handle_welcome_email():
    """Webhook for new lead welcome email"""
    try:
        data = request.get_json()
        lead_id = data.get("lead_id") or data.get("key") or data.get("keys", [None])[0]

        if not lead_id:
            return jsonify({"error": "No lead_id provided"}), 400

        service = get_email_service()
        success = service.send_welcome_email(lead_id)

        return jsonify({"status": "sent" if success else "failed", "lead_id": lead_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/meeting/reminder', methods=['POST'])
def handle_meeting_reminder():
    """Webhook for pre-meeting reminder"""
    try:
        data = request.get_json()
        event_id = data.get("event_id") or data.get("key")

        if not event_id:
            return jsonify({"error": "No event_id provided"}), 400

        service = get_email_service()
        success = service.send_pre_meeting_reminder(event_id)

        return jsonify({"status": "sent" if success else "failed", "event_id": event_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/proposal/sent', methods=['POST'])
def handle_proposal_sent():
    """Webhook for proposal sent notification"""
    try:
        data = request.get_json()
        proposal_id = data.get("proposal_id") or data.get("key")

        if not proposal_id:
            return jsonify({"error": "No proposal_id provided"}), 400

        service = get_email_service()
        success = service.send_proposal_notification(proposal_id)

        return jsonify({"status": "sent" if success else "failed", "proposal_id": proposal_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/contract/active', methods=['POST'])
def handle_contract_active():
    """Webhook for contract activated - sends onboarding email"""
    try:
        data = request.get_json()
        contract_id = data.get("contract_id") or data.get("key")

        if not contract_id:
            return jsonify({"error": "No contract_id provided"}), 400

        service = get_email_service()
        success = service.send_onboarding_email(contract_id)

        return jsonify({"status": "sent" if success else "failed", "contract_id": contract_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/milestone/completed', methods=['POST'])
def handle_milestone_completed():
    """Webhook for milestone completion notification"""
    try:
        data = request.get_json()
        milestone_id = data.get("milestone_id") or data.get("key")

        if not milestone_id:
            return jsonify({"error": "No milestone_id provided"}), 400

        service = get_email_service()
        success = service.send_milestone_update(milestone_id)

        return jsonify({"status": "sent" if success else "failed", "milestone_id": milestone_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/invoice/sent', methods=['POST'])
def handle_invoice_sent():
    """Webhook for invoice sent notification"""
    try:
        data = request.get_json()
        invoice_id = data.get("invoice_id") or data.get("key")

        if not invoice_id:
            return jsonify({"error": "No invoice_id provided"}), 400

        service = get_email_service()
        success = service.send_invoice_notification(invoice_id)

        return jsonify({"status": "sent" if success else "failed", "invoice_id": invoice_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/invoice/overdue', methods=['POST'])
def handle_invoice_overdue():
    """Webhook for overdue invoice reminder"""
    try:
        data = request.get_json()
        invoice_id = data.get("invoice_id") or data.get("key")

        if not invoice_id:
            return jsonify({"error": "No invoice_id provided"}), 400

        service = get_email_service()
        success = service.send_payment_reminder(invoice_id)

        return jsonify({"status": "sent" if success else "failed", "invoice_id": invoice_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/project/completed', methods=['POST'])
def handle_project_completed():
    """Webhook for project completion notification"""
    try:
        data = request.get_json()
        project_id = data.get("project_id") or data.get("key")

        if not project_id:
            return jsonify({"error": "No project_id provided"}), 400

        service = get_email_service()

        # Send completion email immediately
        success = service.send_project_completion(project_id)

        # Note: completion_pack should be sent 72h later via scheduled job
        # or use a task queue like Celery

        return jsonify({
            "status": "sent" if success else "failed",
            "project_id": project_id,
            "note": "Completion pack scheduled for 72h"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/lead/reengagement', methods=['POST'])
def handle_lead_reengagement():
    """Webhook for lead re-engagement"""
    try:
        data = request.get_json()
        lead_id = data.get("lead_id") or data.get("key")

        if not lead_id:
            return jsonify({"error": "No lead_id provided"}), 400

        service = get_email_service()
        success = service.send_re_engagement(lead_id)

        return jsonify({"status": "sent" if success else "failed", "lead_id": lead_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/batch', methods=['POST'])
def handle_batch_emails():
    """
    Batch email sending for scheduled jobs
    Expects JSON body with:
    - template: template slug
    - items: list of dicts with 'id', 'email', 'name', 'variables'
    """
    try:
        data = request.get_json()
        template = data.get("template")
        items = data.get("items", [])

        if not template or not items:
            return jsonify({"error": "Missing template or items"}), 400

        service = get_email_service()
        results = {"sent": 0, "failed": 0, "errors": []}

        for item in items:
            try:
                success = service.send_template_email(
                    template_slug=template,
                    to_email=item.get("email"),
                    to_name=item.get("name"),
                    variables=item.get("variables", {}),
                    client_id=item.get("client_id"),
                    contact_id=item.get("contact_id")
                )

                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"id": item.get("id"), "error": str(e)})

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('EMAIL_WEBHOOK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    print(f"\n{'='*50}")
    print("SHINOBI C2 - EMAIL WEBHOOK SERVICE")
    print(f"{'='*50}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"\nEndpoints:")
    print(f"  POST /webhook/email           - Generic template email")
    print(f"  POST /webhook/lead/welcome    - Welcome email")
    print(f"  POST /webhook/meeting/reminder - Pre-meeting reminder")
    print(f"  POST /webhook/proposal/sent   - Proposal notification")
    print(f"  POST /webhook/contract/active - Onboarding email")
    print(f"  POST /webhook/milestone/completed - Milestone update")
    print(f"  POST /webhook/invoice/sent    - Invoice notification")
    print(f"  POST /webhook/invoice/overdue - Payment reminder")
    print(f"  POST /webhook/project/completed - Project completion")
    print(f"  POST /webhook/lead/reengagement - Re-engagement")
    print(f"  POST /webhook/batch           - Batch emails")
    print(f"{'='*50}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
