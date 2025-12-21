#!/usr/bin/env python3
"""
Setup Email Workflow System for Shinobi C2
Creates email_templates collection and populates with all templates
"""

import os
import json
import requests
from datetime import datetime

# Configuration
DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "i6DpdwdfQbWQ5_uQElOYuuZFWyOdK1uk")

headers = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json"
}


def create_email_templates_collection():
    """Create the email_templates collection if it doesn't exist"""

    collection_schema = {
        "collection": "email_templates",
        "meta": {
            "collection": "email_templates",
            "icon": "mail",
            "note": "Email templates for automated client communications",
            "display_template": "{{name}}",
            "hidden": False,
            "singleton": False,
            "sort_field": "sort",
            "archive_field": "is_active",
            "archive_value": "false",
            "unarchive_value": "true"
        },
        "schema": {
            "name": "email_templates"
        },
        "fields": [
            {
                "field": "id",
                "type": "uuid",
                "meta": {
                    "hidden": True,
                    "readonly": True,
                    "interface": "input",
                    "special": ["uuid"]
                },
                "schema": {
                    "is_primary_key": True
                }
            },
            {
                "field": "name",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "half",
                    "required": True
                },
                "schema": {
                    "is_nullable": False
                }
            },
            {
                "field": "slug",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "half",
                    "required": True,
                    "note": "Unique identifier for template lookup"
                },
                "schema": {
                    "is_unique": True
                }
            },
            {
                "field": "category",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "width": "half",
                    "options": {
                        "choices": [
                            {"text": "Welcome", "value": "welcome"},
                            {"text": "Booking", "value": "booking"},
                            {"text": "Follow Up", "value": "follow_up"},
                            {"text": "Re-engagement", "value": "re_engagement"},
                            {"text": "Proposal", "value": "proposal"},
                            {"text": "Onboarding", "value": "onboarding"},
                            {"text": "Milestone", "value": "milestone"},
                            {"text": "Invoice", "value": "invoice"},
                            {"text": "Payment Reminder", "value": "payment_reminder"},
                            {"text": "Completion", "value": "completion"},
                            {"text": "Referral", "value": "referral"},
                            {"text": "Nurture", "value": "nurture"}
                        ]
                    }
                }
            },
            {
                "field": "subject",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full",
                    "required": True,
                    "note": "Email subject line - supports {{variables}}"
                }
            },
            {
                "field": "body_html",
                "type": "text",
                "meta": {
                    "interface": "input-rich-text-html",
                    "width": "full",
                    "note": "HTML email body - supports {{variables}}"
                }
            },
            {
                "field": "body_text",
                "type": "text",
                "meta": {
                    "interface": "input-multiline",
                    "width": "full",
                    "note": "Plain text fallback"
                }
            },
            {
                "field": "variables",
                "type": "json",
                "meta": {
                    "interface": "input-code",
                    "width": "full",
                    "options": {
                        "language": "json"
                    },
                    "note": "Available merge fields and their sources"
                }
            },
            {
                "field": "trigger_collection",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "third",
                    "note": "Collection that triggers this email"
                }
            },
            {
                "field": "trigger_field",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "third",
                    "note": "Field to watch for changes"
                }
            },
            {
                "field": "trigger_value",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "third",
                    "note": "Value that triggers the email"
                }
            },
            {
                "field": "delay_hours",
                "type": "integer",
                "meta": {
                    "interface": "input",
                    "width": "half",
                    "note": "Hours to delay sending (negative for before event)",
                    "default": 0
                },
                "schema": {
                    "default_value": 0
                }
            },
            {
                "field": "is_active",
                "type": "boolean",
                "meta": {
                    "interface": "boolean",
                    "width": "half",
                    "default": True
                },
                "schema": {
                    "default_value": True
                }
            },
            {
                "field": "sort",
                "type": "integer",
                "meta": {
                    "hidden": True,
                    "interface": "input"
                }
            },
            {
                "field": "created_at",
                "type": "timestamp",
                "meta": {
                    "interface": "datetime",
                    "readonly": True,
                    "hidden": True,
                    "special": ["date-created"]
                }
            },
            {
                "field": "updated_at",
                "type": "timestamp",
                "meta": {
                    "interface": "datetime",
                    "readonly": True,
                    "hidden": True,
                    "special": ["date-updated"]
                }
            }
        ]
    }

    # Check if collection exists
    response = requests.get(
        f"{DIRECTUS_URL}/collections/email_templates",
        headers=headers
    )

    if response.status_code == 200:
        print("✓ email_templates collection already exists")
        return True

    # Create collection
    response = requests.post(
        f"{DIRECTUS_URL}/collections",
        headers=headers,
        json=collection_schema
    )

    if response.status_code in [200, 201]:
        print("✓ Created email_templates collection")
        return True
    else:
        print(f"✗ Failed to create collection: {response.status_code}")
        print(response.text)
        return False


def load_html_templates():
    """Load HTML templates from EMAIL_WORKFLOW.md or use defaults"""

    # Base HTML structure for all emails
    base_template = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{subject}}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #09090b; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #09090b;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #18181b; border: 1px solid #27272a; border-radius: 8px;">
          <!-- Header -->
          <tr>
            <td style="padding: 40px 40px 20px 40px; border-bottom: 1px solid #27272a;">
              <img src="{{logo_url}}" alt="The Shinobi Project" width="180" style="display: block;">
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              {{content}}
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding: 30px 40px; border-top: 1px solid #27272a; background-color: #09090b;">
              <p style="color: #71717a; font-size: 12px; margin: 0; text-transform: uppercase; letter-spacing: 1px;">
                The Shinobi Project
              </p>
              <p style="color: #52525b; font-size: 12px; margin: 8px 0 0 0;">
                {{company_address}}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>'''

    return base_template


def populate_templates():
    """Populate email_templates with all required templates"""

    # Load template definitions
    script_dir = os.path.dirname(os.path.abspath(__file__))
    seed_file = os.path.join(script_dir, "email_templates_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    templates = data["email_templates"]
    base_html = load_html_templates()

    # Template-specific content
    content_map = {
        "welcome": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0; letter-spacing: -0.5px;">
                Welcome, {{contact_first_name}}.
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                We understand you're interested in taking your business further. That's exactly what we do.
              </p>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                The Shinobi Project operates in the shadows so your business can shine in the light. We handle the complex infrastructure, digital presence, and technical operations that consume your time and energy.
              </p>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 32px 0;">
                <strong style="color: #e4e4e7;">The next step:</strong> A brief discovery call to understand your objectives and determine if we're the right fit.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{booking_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Schedule Discovery Call
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #71717a; font-size: 14px; line-height: 1.6; margin: 32px 0 0 0;">
                Select a time that works for you. The call takes 20-30 minutes.
              </p>''',

        "pre_meeting": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Ready for Tomorrow?
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Your discovery call is scheduled for <strong style="color: #e4e4e7;">{{meeting_date}} at {{meeting_time}}</strong>.
              </p>
              <div style="background-color: #09090b; border-left: 3px solid #b91c1c; padding: 20px; margin: 24px 0;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 1px;">
                  To Make the Most of Our Time
                </p>
                <ul style="color: #a1a1aa; font-size: 15px; line-height: 1.8; margin: 0; padding-left: 20px;">
                  <li>What's the primary challenge holding your business back?</li>
                  <li>What does success look like in 6-12 months?</li>
                  <li>Any specific projects or ideas you're considering?</li>
                </ul>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                No preparation required - just come as you are. These questions are simply food for thought.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{video_call_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Join Video Call
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #71717a; font-size: 14px; margin: 24px 0 0 0;">
                Need to reschedule? <a href="{{reschedule_url}}" style="color: #b91c1c;">Click here</a>
              </p>''',

        "follow_up": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Good Speaking With You, {{contact_first_name}}.
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Thank you for taking the time to discuss {{company_name}}'s objectives. Here's a summary of what we covered:
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  Key Points Discussed
                </p>
                <p style="color: #a1a1aa; font-size: 15px; line-height: 1.7; margin: 0;">
                  {{meeting_summary}}
                </p>
              </div>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  Next Steps
                </p>
                <p style="color: #a1a1aa; font-size: 15px; line-height: 1.7; margin: 0;">
                  {{next_steps}}
                </p>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 24px 0;">
                {{custom_message}}
              </p>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0;">
                If you have any questions in the meantime, reply to this email directly.
              </p>
              <p style="color: #e4e4e7; font-size: 16px; margin: 32px 0 0 0;">
                — {{assigned_team_member}}
              </p>''',

        "re_engagement": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Quick Check-In
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, we noticed we haven't connected recently.
              </p>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                No pressure - we understand timing is everything. If circumstances have changed or you're ready to continue the conversation, we're here.
              </p>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 32px 0;">
                If now isn't the right time, simply let us know and we'll check back in a few months.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{booking_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Reschedule Call
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #71717a; font-size: 14px; margin: 24px 0 0 0;">
                Or reply "not now" and we'll follow up in 3 months.
              </p>''',

        "proposal": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Your Proposal is Ready
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, following our discussions, we've prepared a detailed proposal for {{company_name}}.
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 8px;">Project</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 8px;">{{project_name}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 8px;">Investment</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 8px;">{{total_value}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Valid Until</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right;">{{expiration_date}}</td>
                  </tr>
                </table>
              </div>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{proposal_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      View Full Proposal
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 32px 0 0 0;">
                Review at your convenience. If you have questions or would like to discuss any aspect, reply to this email or schedule a follow-up call.
              </p>''',

        "onboarding": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Welcome to The Shinobi Project
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, we're honoured to have {{company_name}} on board. Your project is now officially in motion.
              </p>
              <div style="background-color: #09090b; border-left: 3px solid #b91c1c; padding: 20px; margin: 24px 0;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  Your Project Team
                </p>
                <p style="color: #a1a1aa; font-size: 15px; line-height: 1.7; margin: 0;">
                  <strong style="color: #e4e4e7;">Project Lead:</strong> {{project_manager}}<br>
                  <strong style="color: #e4e4e7;">Direct Email:</strong> {{project_email}}
                </p>
              </div>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  What Happens Next
                </p>
                <ol style="color: #a1a1aa; font-size: 15px; line-height: 1.8; margin: 0; padding-left: 20px;">
                  <li><strong style="color: #e4e4e7;">Kickoff Call</strong> - We'll schedule a brief call to align on priorities</li>
                  <li><strong style="color: #e4e4e7;">Access & Assets</strong> - We'll request any credentials or materials needed</li>
                  <li><strong style="color: #e4e4e7;">First Milestone</strong> - You'll receive updates as we progress</li>
                </ol>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                Your dedicated project email for all communications: <strong style="color: #e4e4e7;">{{project_email}}</strong>
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{kickoff_booking_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Schedule Kickoff Call
                    </a>
                  </td>
                </tr>
              </table>''',

        "milestone": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Milestone Achieved
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, we're pleased to report that <strong style="color: #e4e4e7;">{{milestone_name}}</strong> is now complete.
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 12px;">Project</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 12px;">{{project_name}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 12px;">Milestone</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 12px;">{{milestone_name}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Progress</td>
                    <td style="color: #b91c1c; font-size: 16px; font-weight: 600; text-align: right;">{{completion_percentage}}%</td>
                  </tr>
                </table>
              </div>
              <div style="background-color: #27272a; height: 8px; border-radius: 4px; margin: 24px 0;">
                <div style="background-color: #b91c1c; height: 8px; border-radius: 4px; width: {{completion_percentage}}%;"></div>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                {{milestone_description}}
              </p>
              <p style="color: #71717a; font-size: 14px; margin: 0;">
                <strong style="color: #a1a1aa;">Next milestone:</strong> {{next_milestone_name}}
              </p>''',

        "invoice": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Invoice {{invoice_number}}
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                Please find your invoice attached and detailed below.
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 12px;">Invoice Number</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 12px;">{{invoice_number}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 12px;">Amount Due</td>
                    <td style="color: #e4e4e7; font-size: 20px; font-weight: 700; text-align: right; padding-bottom: 12px;">{{total_amount}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 12px;">Due Date</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right; padding-bottom: 12px;">{{due_date}}</td>
                  </tr>
                  <tr>
                    <td style="color: #71717a; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Project</td>
                    <td style="color: #e4e4e7; font-size: 16px; text-align: right;">{{project_name}}</td>
                  </tr>
                </table>
              </div>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{stripe_payment_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Pay Now
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #71717a; font-size: 14px; margin: 24px 0 0 0;">
                Payment methods: Bank transfer or card via Stripe. Details in attached PDF.
              </p>''',

        "payment_reminder": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Payment Reminder
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, this is a friendly reminder that invoice <strong style="color: #e4e4e7;">{{invoice_number}}</strong> is now overdue.
              </p>
              <div style="background-color: #7f1d1d; border: 1px solid #b91c1c; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="color: #fca5a5; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 8px;">Amount Outstanding</td>
                    <td style="color: #ffffff; font-size: 20px; font-weight: 700; text-align: right; padding-bottom: 8px;">{{amount_remaining}}</td>
                  </tr>
                  <tr>
                    <td style="color: #fca5a5; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Days Overdue</td>
                    <td style="color: #ffffff; font-size: 16px; text-align: right;">{{days_overdue}}</td>
                  </tr>
                </table>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                If payment has already been sent, please disregard this notice. If you're experiencing difficulties, please get in touch so we can discuss options.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{stripe_payment_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Pay Now
                    </a>
                  </td>
                </tr>
              </table>''',

        "completion": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Mission Accomplished
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, we're pleased to confirm that <strong style="color: #e4e4e7;">{{project_name}}</strong> is now complete.
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  Deliverables
                </p>
                <p style="color: #a1a1aa; font-size: 15px; line-height: 1.7; margin: 0;">
                  {{deliverables_summary}}
                </p>
              </div>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  Your Assets
                </p>
                <ul style="color: #a1a1aa; font-size: 15px; line-height: 1.8; margin: 0; padding-left: 20px;">
                  <li><strong style="color: #e4e4e7;">Live Site:</strong> <a href="{{live_url}}" style="color: #b91c1c;">{{live_url}}</a></li>
                  <li><strong style="color: #e4e4e7;">Admin Access:</strong> <a href="{{admin_url}}" style="color: #b91c1c;">{{admin_url}}</a></li>
                  <li><strong style="color: #e4e4e7;">Documentation:</strong> <a href="{{docs_url}}" style="color: #b91c1c;">View Handover Pack</a></li>
                </ul>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                Your completion pack with all credentials, documentation, and assets will follow in a separate email.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{feedback_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Share Your Feedback
                    </a>
                  </td>
                </tr>
              </table>''',

        "completion_pack": '''<h1 style="color: #e4e4e7; font-size: 28px; font-weight: 700; margin: 0 0 24px 0;">
                Your Completion Pack
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{contact_first_name}}, thank you for working with The Shinobi Project. We've prepared a completion pack to help you share and celebrate your new digital presence.
              </p>
              <div style="background-color: #09090b; border: 1px solid #27272a; padding: 24px; margin: 24px 0; border-radius: 6px;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px;">
                  What's Included
                </p>
                <ul style="color: #a1a1aa; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px;">
                  <li><strong style="color: #e4e4e7;">Brand Assets</strong> - Logo files, color codes, typography</li>
                  <li><strong style="color: #e4e4e7;">Social Media Kit</strong> - Launch graphics ready to post</li>
                  <li><strong style="color: #e4e4e7;">Business Cards</strong> - Print-ready PDF designs</li>
                  <li><strong style="color: #e4e4e7;">Launch Announcement</strong> - Pre-written copy for your audience</li>
                  <li><strong style="color: #e4e4e7;">Referral Cards</strong> - Share with colleagues who need similar work</li>
                </ul>
              </div>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #b91c1c; border-radius: 6px;">
                    <a href="{{completion_pack_url}}" style="display: inline-block; padding: 16px 32px; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; text-transform: uppercase; letter-spacing: 1px;">
                      Download Completion Pack
                    </a>
                  </td>
                </tr>
              </table>
              <div style="background-color: #09090b; border-left: 3px solid #b91c1c; padding: 20px; margin: 32px 0;">
                <p style="color: #e4e4e7; font-size: 14px; font-weight: 600; margin: 0 0 12px 0;">
                  Enjoyed Working With Us?
                </p>
                <p style="color: #a1a1aa; font-size: 15px; line-height: 1.6; margin: 0;">
                  We grow through referrals. If you know someone who could benefit from similar work, we'd be grateful for an introduction. The referral cards in your pack make it easy.
                </p>
              </div>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0;">
                We'll stay in touch with occasional updates. If you ever need support or want to discuss future projects, you know where to find us.
              </p>''',

        "nurture": '''<h1 style="color: #e4e4e7; font-size: 24px; font-weight: 700; margin: 0 0 24px 0;">
                {{nurture_headline}}
              </h1>
              <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                {{nurture_body}}
              </p>
              <p style="color: #71717a; font-size: 14px; margin: 32px 0 0 0;">
                Questions? Just reply to this email.
              </p>'''
    }

    created_count = 0

    for template in templates:
        slug = template["slug"]
        content = content_map.get(slug, "<p>Template content to be added</p>")
        html_body = base_html.replace("{{content}}", content)

        template_data = {
            "name": template["name"],
            "slug": template["slug"],
            "category": template["category"],
            "subject": template["subject"],
            "body_html": html_body,
            "body_text": f"Plain text version of {template['name']}",
            "variables": json.dumps(template["variables"]),
            "trigger_collection": template["trigger_collection"],
            "trigger_field": template["trigger_field"],
            "trigger_value": template["trigger_value"],
            "delay_hours": template["delay_hours"],
            "is_active": template["is_active"]
        }

        # Check if template exists
        response = requests.get(
            f"{DIRECTUS_URL}/items/email_templates",
            headers=headers,
            params={"filter[slug][_eq]": slug}
        )

        if response.status_code == 200 and response.json().get("data"):
            print(f"  - {template['name']} already exists, skipping")
            continue

        # Create template
        response = requests.post(
            f"{DIRECTUS_URL}/items/email_templates",
            headers=headers,
            json=template_data
        )

        if response.status_code in [200, 201]:
            print(f"  ✓ Created: {template['name']}")
            created_count += 1
        else:
            print(f"  ✗ Failed: {template['name']} - {response.status_code}")

    print(f"\n  Created {created_count} templates")


def create_system_config_collection():
    """Create a system_config collection for storing booking URLs etc"""

    collection_schema = {
        "collection": "system_config",
        "meta": {
            "collection": "system_config",
            "icon": "settings",
            "note": "System-wide configuration values",
            "singleton": True,
            "hidden": False
        },
        "schema": {
            "name": "system_config"
        },
        "fields": [
            {
                "field": "id",
                "type": "integer",
                "meta": {
                    "hidden": True,
                    "interface": "input",
                    "readonly": True
                },
                "schema": {
                    "is_primary_key": True,
                    "has_auto_increment": True
                }
            },
            {
                "field": "booking_url",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full",
                    "note": "Google Calendar Appointment Scheduling URL"
                }
            },
            {
                "field": "kickoff_booking_url",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full",
                    "note": "URL for project kickoff call booking"
                }
            },
            {
                "field": "logo_url",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full",
                    "note": "URL to logo for email headers"
                }
            },
            {
                "field": "company_address",
                "type": "text",
                "meta": {
                    "interface": "input-multiline",
                    "width": "full",
                    "note": "Company address for email footers"
                }
            },
            {
                "field": "feedback_url",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full",
                    "note": "URL to feedback/review form"
                }
            },
            {
                "field": "from_email",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "half",
                    "note": "Default from email address"
                }
            },
            {
                "field": "from_name",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "half",
                    "note": "Default from name"
                }
            }
        ]
    }

    response = requests.get(
        f"{DIRECTUS_URL}/collections/system_config",
        headers=headers
    )

    if response.status_code == 200:
        print("✓ system_config collection already exists")
        return True

    response = requests.post(
        f"{DIRECTUS_URL}/collections",
        headers=headers,
        json=collection_schema
    )

    if response.status_code in [200, 201]:
        print("✓ Created system_config collection")
        return True
    else:
        print(f"✗ Failed to create system_config: {response.status_code}")
        return False


def main():
    print("\n" + "="*60)
    print("SHINOBI C2 - EMAIL WORKFLOW SETUP")
    print("="*60 + "\n")

    # Check Directus connection
    try:
        response = requests.get(f"{DIRECTUS_URL}/server/ping", timeout=5)
        if response.status_code != 200:
            print("✗ Cannot connect to Directus. Ensure containers are running:")
            print("  docker-compose up -d")
            return
    except Exception as e:
        print(f"✗ Cannot connect to Directus: {e}")
        print("  Ensure containers are running: docker-compose up -d")
        return

    print("✓ Connected to Directus\n")

    # Step 1: Create collections
    print("1. Creating collections...")
    create_email_templates_collection()
    create_system_config_collection()

    # Step 2: Populate templates
    print("\n2. Populating email templates...")
    populate_templates()

    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Set up Google Calendar Appointment Scheduling")
    print("2. Configure system_config with your booking URL")
    print("3. Create Directus Flows for email automation")
    print("4. Test email sending via Google Workspace MCP")
    print("\nSee EMAIL_WORKFLOW.md for full documentation.")


if __name__ == "__main__":
    main()
