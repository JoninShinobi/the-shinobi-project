"""
Orchestrator Agent - Central Brain
Routes tasks to specialized department agents and coordinates cross-department workflows.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, AgentConfig, AgentResult


class Department(Enum):
    """Available departments for task routing"""
    FINANCE = "finance"
    MARKETING = "marketing"
    CLIENT_SERVICES = "client_services"
    PRODUCTION = "production"
    SALES = "sales"
    OPERATIONS = "operations"
    UNKNOWN = "unknown"


@dataclass
class TaskClassification:
    """Classification result for incoming task"""
    department: Department
    priority: str  # critical, high, medium, low
    task_type: str
    requires_human_approval: bool
    estimated_complexity: str  # simple, moderate, complex
    context_summary: str


class OrchestratorAgent(BaseAgent):
    """
    Central orchestration agent that:
    1. Receives all incoming events from external sites and internal flows
    2. Classifies and routes tasks to appropriate department agents
    3. Coordinates multi-department workflows
    4. Manages handoffs between agents
    5. Tracks overall workflow progress
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="Orchestrator",
            description="Central brain that routes and coordinates all agent tasks",
            config=config or AgentConfig(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                enable_tools=True,
                allowed_collections=[
                    "clients", "projects", "invoices", "leads",
                    "tasks", "communication_log", "audit_log"
                ]
            )
        )
        self._department_agents: Dict[Department, BaseAgent] = {}

    def register_agent(self, department: Department, agent: BaseAgent):
        """Register a department agent for task delegation"""
        self._department_agents[department] = agent
        self.log(f"Registered {agent.name} for {department.value}")

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi C2 Orchestrator - the central brain coordinating all business operations.

## Your Role
You receive incoming events, classify them, and route to the appropriate department agent.

## Available Departments
- FINANCE: Invoicing, payments, revenue tracking, expenses
- MARKETING: Campaign creation, social media, content, lead nurturing
- CLIENT_SERVICES: Client communications, support, feedback, relationships
- PRODUCTION: Project management, task tracking, deliverables
- SALES: Lead qualification, proposals, contracts
- OPERATIONS: Team scheduling, resource allocation, internal processes

## Classification Rules
1. Analyze the incoming event/task context
2. Determine the primary department responsible
3. Identify if multiple departments need coordination
4. Assess priority based on urgency and business impact
5. Flag items requiring human approval

## Human Approval Required For
- Financial transactions over £1000
- New client contracts
- Marketing campaigns going live
- Any action affecting external customers
- Escalated support issues
- Changes to production systems

## Response Format
Always respond with valid JSON containing your classification and routing decision.

## Currency
All financial values are in GBP (£)."""

    def build_task_prompt(self, context: dict) -> str:
        event_type = context.get("event_type", "unknown")
        source = context.get("source", "unknown")
        payload = context.get("payload", {})

        return f"""Classify and route this incoming event:

## Event Details
- Type: {event_type}
- Source: {source}
- Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Payload
{json.dumps(payload, indent=2)}

## Instructions
1. Classify this event to a department
2. Determine priority level
3. Identify if human approval is needed
4. Provide routing instructions

Respond with JSON:
{{
    "department": "finance|marketing|client_services|production|sales|operations",
    "priority": "critical|high|medium|low",
    "task_type": "brief description of the task type",
    "requires_human_approval": true|false,
    "estimated_complexity": "simple|moderate|complex",
    "context_summary": "brief summary of what needs to be done",
    "multi_department": ["list", "of", "other", "departments"] or null,
    "suggested_actions": ["action 1", "action 2"],
    "notes": "any additional context"
}}"""

    def get_tools(self) -> List[Dict]:
        """Define tools for the orchestrator"""
        return [
            {
                "name": "route_to_department",
                "description": "Route a task to a specific department agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "enum": ["finance", "marketing", "client_services", "production", "sales", "operations"],
                            "description": "Target department"
                        },
                        "task_context": {
                            "type": "object",
                            "description": "Context to pass to the department agent"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "Task priority"
                        }
                    },
                    "required": ["department", "task_context"]
                }
            },
            {
                "name": "request_human_approval",
                "description": "Create a human approval request in Directus",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_type": {
                            "type": "string",
                            "enum": ["decision_required", "review_output", "approval_needed"],
                            "description": "Type of approval needed"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Brief summary for the human reviewer"
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Options for the human to choose from"
                        },
                        "context": {
                            "type": "object",
                            "description": "Full context for the decision"
                        }
                    },
                    "required": ["approval_type", "summary"]
                }
            },
            {
                "name": "log_audit_event",
                "description": "Log an event to the audit log",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_type": {
                            "type": "string",
                            "description": "Type of event being logged"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the event"
                        },
                        "related_collection": {
                            "type": "string",
                            "description": "Collection this event relates to"
                        },
                        "related_item_id": {
                            "type": "string",
                            "description": "ID of the related item"
                        }
                    },
                    "required": ["event_type", "description"]
                }
            }
        ]

    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """Handle orchestrator tool calls"""
        self.log(f"Tool: {tool_name}")

        if tool_name == "route_to_department":
            return await self._route_to_department(
                tool_input["department"],
                tool_input["task_context"],
                tool_input.get("priority", "medium")
            )

        elif tool_name == "request_human_approval":
            return await self._request_human_approval(
                tool_input["approval_type"],
                tool_input["summary"],
                tool_input.get("options", []),
                tool_input.get("context", {})
            )

        elif tool_name == "log_audit_event":
            return await self._log_audit_event(
                tool_input["event_type"],
                tool_input["description"],
                tool_input.get("related_collection"),
                tool_input.get("related_item_id")
            )

        return {"error": f"Unknown tool: {tool_name}"}

    async def _route_to_department(self, department: str, context: dict, priority: str) -> dict:
        """Route task to the appropriate department agent"""
        dept = Department(department)

        if dept not in self._department_agents:
            return {
                "success": False,
                "error": f"No agent registered for {department}",
                "available_departments": [d.value for d in self._department_agents.keys()]
            }

        agent = self._department_agents[dept]
        task_id = f"{department}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.log(f"Routing to {agent.name} with priority {priority}")

        try:
            result = await agent.execute(task_id, context)
            return {
                "success": result.success,
                "agent": agent.name,
                "task_id": task_id,
                "result": result.result_data,
                "requires_approval": result.requires_approval,
                "approval_id": result.approval_item_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent.name,
                "task_id": task_id
            }

    async def _request_human_approval(
        self,
        approval_type: str,
        summary: str,
        options: List[str],
        context: dict
    ) -> dict:
        """Create human approval request in Directus"""
        # This will be implemented to create a human_prompts record
        approval_id = f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "approval_id": approval_id,
            "type": approval_type,
            "status": "pending",
            "message": "Human approval request created"
        }

    async def _log_audit_event(
        self,
        event_type: str,
        description: str,
        related_collection: Optional[str],
        related_item_id: Optional[str]
    ) -> dict:
        """Log event to audit log"""
        # This will be implemented to create an audit_log record
        return {
            "success": True,
            "logged": True,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        }

    async def classify_and_route(self, event: dict) -> AgentResult:
        """
        Main entry point: classify incoming event and route appropriately.
        """
        task_id = f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # First, classify the event
        result = await self.execute(task_id, event)

        if not result.success:
            return result

        # Parse the classification
        try:
            output = result.result_data.get("output", "")
            # Extract JSON from the output
            if "```json" in output:
                json_str = output.split("```json")[1].split("```")[0]
            elif "{" in output:
                start = output.index("{")
                end = output.rindex("}") + 1
                json_str = output[start:end]
            else:
                json_str = output

            classification = json.loads(json_str)

            # Update result with classification
            result.result_data["classification"] = classification

            # If we have a registered agent for this department, route automatically
            dept = Department(classification.get("department", "unknown"))
            if dept in self._department_agents and not classification.get("requires_human_approval"):
                routing_result = await self._route_to_department(
                    classification["department"],
                    event,
                    classification.get("priority", "medium")
                )
                result.result_data["routing"] = routing_result

        except (json.JSONDecodeError, ValueError) as e:
            self.log(f"Classification parse error: {e}")
            result.result_data["parse_error"] = str(e)

        return result

    async def execute_workflow(self, workflow_steps: List[dict]) -> List[AgentResult]:
        """
        Execute a multi-step workflow across departments.
        Each step is executed in sequence with results passed forward.
        """
        results = []
        context = {}

        for i, step in enumerate(workflow_steps):
            self.log(f"Executing workflow step {i+1}/{len(workflow_steps)}: {step.get('name', 'unnamed')}")

            # Merge previous results into context
            step_context = {**context, **step.get("context", {})}
            step_context["previous_results"] = [r.result_data for r in results if r.success]

            result = await self.classify_and_route({
                "event_type": step.get("type", "workflow_step"),
                "source": "orchestrator_workflow",
                "payload": step_context,
                "workflow_step": i + 1,
                "workflow_total": len(workflow_steps)
            })

            results.append(result)

            # Check if we need to stop
            if not result.success and step.get("stop_on_failure", True):
                self.log(f"Workflow stopped at step {i+1} due to failure")
                break

            if result.requires_approval:
                self.log(f"Workflow paused at step {i+1} pending human approval")
                break

            # Update context with this step's results
            if result.result_data:
                context[f"step_{i+1}"] = result.result_data

        return results
