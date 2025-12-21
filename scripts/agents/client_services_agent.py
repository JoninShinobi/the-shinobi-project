"""
Client Services Agent
Handles client communications, support, relationships, and satisfaction.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentConfig, AgentResult


class ClientServicesAgent(BaseAgent):
    """
    Client Services department agent responsible for:
    1. Client communications and follow-ups
    2. Support ticket management
    3. Client relationship nurturing
    4. Feedback collection and analysis
    5. Onboarding coordination
    6. Account health monitoring
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="ClientServicesAgent",
            description="Handles client relationships, communications, and support",
            config=config or AgentConfig(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                enable_tools=True,
                allowed_collections=[
                    "clients", "contacts", "communication_log",
                    "support_tickets", "reviews_feedback", "projects"
                ]
            )
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Client Services Agent, responsible for client relationships and satisfaction.

## Your Responsibilities
1. Client Communications: Manage all client touchpoints
2. Support Management: Handle support tickets and escalations
3. Relationship Building: Maintain strong client relationships
4. Feedback Management: Collect and analyze client feedback
5. Onboarding: Coordinate new client onboarding
6. Account Health: Monitor client health scores

## Communication Guidelines
- Professional yet warm and personable
- Respond within 24 hours (business days)
- Always acknowledge concerns before resolving
- Proactive communication on project updates
- Personalized approach based on client history

## Escalation Triggers
1. Client expresses strong dissatisfaction
2. Potential contract cancellation mentioned
3. Unresolved issue after 48 hours
4. Request for senior management contact
5. Legal or compliance concerns

## Health Score Factors
- Recent communication frequency
- Project milestone completion
- Payment history
- Support ticket volume
- Feedback sentiment

## Workflow Rules
1. ALL outbound communications must be drafted first
2. Escalated issues require human approval
3. Log all interactions in communication_log
4. Update client health score after significant interactions

## Response Timeframes
- Critical: 2 hours
- High: 4 hours
- Medium: 24 hours
- Low: 48 hours

## Output Format
Always provide:
- Communication summary
- Draft content (if applicable)
- Recommended actions
- Items requiring escalation"""

    def build_task_prompt(self, context: dict) -> str:
        task_type = context.get("task_type", "general_client_service")
        client_info = context.get("client", {})
        ticket_info = context.get("ticket", {})
        communication = context.get("communication", {})

        prompt = f"""## Client Services Task
- Type: {task_type}
- Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        if client_info:
            prompt += f"""## Client Context
{json.dumps(client_info, indent=2)}

"""

        if ticket_info:
            prompt += f"""## Support Ticket
{json.dumps(ticket_info, indent=2)}

"""

        if communication:
            prompt += f"""## Communication Context
{json.dumps(communication, indent=2)}

"""

        prompt += f"""## Full Context
{json.dumps(context, indent=2)}

## Instructions
Execute the appropriate client service action.
Provide:
1. Analysis of the situation
2. Recommended approach
3. Draft communication (if needed)
4. Follow-up actions
5. Escalation needs"""

        return prompt

    def get_tools(self) -> List[Dict]:
        """Client services-specific tools"""
        return [
            {
                "name": "draft_client_communication",
                "description": "Draft a communication to send to a client",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "contact_id": {"type": "string", "description": "Specific contact UUID (optional)"},
                        "communication_type": {
                            "type": "string",
                            "enum": ["email", "phone_script", "meeting_agenda", "follow_up"],
                            "description": "Type of communication"
                        },
                        "subject": {"type": "string", "description": "Subject/topic"},
                        "content": {"type": "string", "description": "Communication content"},
                        "purpose": {
                            "type": "string",
                            "enum": ["update", "request", "response", "introduction", "follow_up", "escalation"],
                            "description": "Purpose of communication"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "Priority level"
                        }
                    },
                    "required": ["client_id", "communication_type", "subject", "content"]
                }
            },
            {
                "name": "create_support_ticket",
                "description": "Create a new support ticket",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "contact_id": {"type": "string", "description": "Contact who reported"},
                        "title": {"type": "string", "description": "Ticket title"},
                        "description": {"type": "string", "description": "Issue description"},
                        "category": {
                            "type": "string",
                            "enum": ["bug", "feature_request", "question", "complaint", "billing", "other"],
                            "description": "Ticket category"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "Priority level"
                        },
                        "project_id": {"type": "string", "description": "Related project (optional)"}
                    },
                    "required": ["client_id", "title", "description", "category"]
                }
            },
            {
                "name": "update_ticket_status",
                "description": "Update a support ticket status",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "Ticket UUID"},
                        "status": {
                            "type": "string",
                            "enum": ["open", "in_progress", "waiting_on_client", "waiting_on_internal", "resolved", "closed"],
                            "description": "New status"
                        },
                        "resolution_notes": {"type": "string", "description": "Notes about resolution"},
                        "internal_notes": {"type": "string", "description": "Internal team notes"}
                    },
                    "required": ["ticket_id", "status"]
                }
            },
            {
                "name": "calculate_client_health",
                "description": "Calculate and update client health score",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "factors": {
                            "type": "object",
                            "properties": {
                                "communication_score": {"type": "integer", "minimum": 0, "maximum": 100},
                                "payment_score": {"type": "integer", "minimum": 0, "maximum": 100},
                                "project_score": {"type": "integer", "minimum": 0, "maximum": 100},
                                "support_score": {"type": "integer", "minimum": 0, "maximum": 100},
                                "feedback_score": {"type": "integer", "minimum": 0, "maximum": 100}
                            }
                        }
                    },
                    "required": ["client_id"]
                }
            },
            {
                "name": "request_feedback",
                "description": "Create a feedback request for a client",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "project_id": {"type": "string", "description": "Project UUID (optional)"},
                        "feedback_type": {
                            "type": "string",
                            "enum": ["project_completion", "quarterly_review", "nps", "general"],
                            "description": "Type of feedback request"
                        },
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific questions to ask"
                        }
                    },
                    "required": ["client_id", "feedback_type"]
                }
            },
            {
                "name": "escalate_to_human",
                "description": "Escalate an issue to a human team member",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "issue_summary": {"type": "string", "description": "Summary of the issue"},
                        "reason": {
                            "type": "string",
                            "enum": ["client_dissatisfied", "complex_issue", "contract_risk", "legal_concern", "request_management"],
                            "description": "Reason for escalation"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["immediate", "today", "this_week"],
                            "description": "How urgent is this"
                        },
                        "context": {"type": "object", "description": "Additional context"}
                    },
                    "required": ["client_id", "issue_summary", "reason"]
                }
            },
            {
                "name": "schedule_follow_up",
                "description": "Schedule a follow-up action for a client",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "follow_up_type": {
                            "type": "string",
                            "enum": ["call", "email", "meeting", "check_in"],
                            "description": "Type of follow-up"
                        },
                        "scheduled_date": {"type": "string", "description": "When to follow up"},
                        "purpose": {"type": "string", "description": "Purpose of follow-up"},
                        "notes": {"type": "string", "description": "Notes for follow-up"}
                    },
                    "required": ["client_id", "follow_up_type", "scheduled_date", "purpose"]
                }
            }
        ]

    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """Handle client services-specific tool calls"""
        self.log(f"Tool: {tool_name}")

        if tool_name == "draft_client_communication":
            return await self._draft_communication(tool_input)

        elif tool_name == "create_support_ticket":
            return await self._create_ticket(tool_input)

        elif tool_name == "update_ticket_status":
            return await self._update_ticket(tool_input)

        elif tool_name == "calculate_client_health":
            return await self._calculate_health(tool_input)

        elif tool_name == "request_feedback":
            return await self._request_feedback(tool_input)

        elif tool_name == "escalate_to_human":
            return await self._escalate(tool_input)

        elif tool_name == "schedule_follow_up":
            return await self._schedule_follow_up(tool_input)

        return {"error": f"Unknown tool: {tool_name}"}

    async def _draft_communication(self, data: dict) -> dict:
        """Draft a client communication"""
        draft_id = f"comm_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "draft_id": draft_id,
            "client_id": data["client_id"],
            "type": data["communication_type"],
            "subject": data["subject"],
            "status": "draft",
            "requires_approval": True,
            "message": f"Communication draft created for review"
        }

    async def _create_ticket(self, data: dict) -> dict:
        """Create a support ticket"""
        ticket_id = f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        priority = data.get("priority", "medium")

        response_times = {
            "critical": "2 hours",
            "high": "4 hours",
            "medium": "24 hours",
            "low": "48 hours"
        }

        return {
            "success": True,
            "ticket_id": ticket_id,
            "client_id": data["client_id"],
            "title": data["title"],
            "category": data["category"],
            "priority": priority,
            "status": "open",
            "target_response_time": response_times[priority],
            "message": f"Support ticket {ticket_id} created with {priority} priority"
        }

    async def _update_ticket(self, data: dict) -> dict:
        """Update a support ticket"""
        return {
            "success": True,
            "ticket_id": data["ticket_id"],
            "new_status": data["status"],
            "updated_at": datetime.now().isoformat(),
            "message": f"Ticket updated to {data['status']}"
        }

    async def _calculate_health(self, data: dict) -> dict:
        """Calculate client health score"""
        factors = data.get("factors", {})

        # Default scores if not provided
        scores = {
            "communication": factors.get("communication_score", 70),
            "payment": factors.get("payment_score", 80),
            "project": factors.get("project_score", 75),
            "support": factors.get("support_score", 85),
            "feedback": factors.get("feedback_score", 70)
        }

        # Weighted average
        weights = {
            "communication": 0.20,
            "payment": 0.25,
            "project": 0.25,
            "support": 0.15,
            "feedback": 0.15
        }

        overall = sum(scores[k] * weights[k] for k in scores)

        if overall >= 80:
            status = "healthy"
            recommendation = "Continue current engagement"
        elif overall >= 60:
            status = "needs_attention"
            recommendation = "Schedule check-in call"
        else:
            status = "at_risk"
            recommendation = "Immediate intervention required"

        return {
            "success": True,
            "client_id": data["client_id"],
            "overall_score": round(overall, 1),
            "status": status,
            "factors": scores,
            "recommendation": recommendation,
            "requires_escalation": status == "at_risk"
        }

    async def _request_feedback(self, data: dict) -> dict:
        """Create a feedback request"""
        request_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "request_id": request_id,
            "client_id": data["client_id"],
            "feedback_type": data["feedback_type"],
            "status": "pending",
            "requires_approval": True,
            "message": f"Feedback request draft created for {data['feedback_type']}"
        }

    async def _escalate(self, data: dict) -> dict:
        """Escalate issue to human"""
        escalation_id = f"esc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "escalation_id": escalation_id,
            "client_id": data["client_id"],
            "reason": data["reason"],
            "urgency": data.get("urgency", "today"),
            "status": "pending_human_review",
            "requires_immediate_attention": data.get("urgency") == "immediate",
            "message": f"Issue escalated to human team - {data['reason']}"
        }

    async def _schedule_follow_up(self, data: dict) -> dict:
        """Schedule a follow-up"""
        follow_up_id = f"followup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "follow_up_id": follow_up_id,
            "client_id": data["client_id"],
            "type": data["follow_up_type"],
            "scheduled_date": data["scheduled_date"],
            "purpose": data["purpose"],
            "status": "scheduled",
            "message": f"Follow-up {data['follow_up_type']} scheduled for {data['scheduled_date']}"
        }
