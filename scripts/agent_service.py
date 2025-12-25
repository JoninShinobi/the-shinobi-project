#!/usr/bin/env python3
"""
Shinobi C2 Agent Service
FastAPI webhook receiver that invokes Claude Agent SDK for autonomous business operations.

Trigger Flow:
1. Directus Flow fires (items.create on leads, emails, etc.)
2. Webhook POST to this service (localhost:5002)
3. This service invokes Claude Agent SDK with context
4. Claude uses Directus MCP to read/write data
5. Response logged to agent_logs collection
6. If email send needed → requires human approval

Architecture:
- OrchestratorAgent: Central brain that routes to department agents
- FinanceAgent: Invoicing, payments, revenue tracking
- MarketingAgent: Campaigns, content, lead nurturing
- ClientServicesAgent: Support, communications, relationships
- EmailAgent: Email drafting and response handling
"""

import asyncio
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

# Import SDK-based agents
from agents import (
    BaseAgent,
    AgentConfig,
    AgentResult,
    OrchestratorAgent,
    Department,
    MarketingAgent,
    FinanceAgent,
    ClientServicesAgent,
    EmailAgent
)

# Import Gmail helper for direct email sending
# TODO: Restore email functionality after restructuring
# from email.gmail_helper import send_email as gmail_send_email

# Configuration
DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_ADMIN_TOKEN", "")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5002"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ==========================================
# Department Agents (Initialized on startup)
# ==========================================
_orchestrator: Optional[OrchestratorAgent] = None
_finance_agent: Optional[FinanceAgent] = None
_marketing_agent: Optional[MarketingAgent] = None
_client_services_agent: Optional[ClientServicesAgent] = None
_email_agent: Optional[EmailAgent] = None

# ==========================================
# Agent Status Controls (Enable/Disable)
# ==========================================
# Each agent can be toggled on/off at runtime
# Disabled agents will reject tasks with a clear message
_agent_status: dict[str, bool] = {
    "orchestrator": True,
    "email": True,
    "lead": True,
    "tracker": True,
    "finance": True,
    "marketing": True,
    "client_services": True,
}

def is_agent_enabled(agent_type: str) -> bool:
    """Check if an agent type is currently enabled."""
    return _agent_status.get(agent_type, False)

def set_agent_status(agent_type: str, enabled: bool) -> bool:
    """Set an agent's enabled status. Returns True if agent exists."""
    if agent_type not in _agent_status:
        return False
    _agent_status[agent_type] = enabled
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent '{agent_type}' {'ENABLED' if enabled else 'DISABLED'}")
    return True

def get_all_agent_status() -> dict[str, bool]:
    """Get status of all agents."""
    return _agent_status.copy()


async def load_agent_status_from_directus():
    """
    Load agent status from Directus agent_settings collection.
    Falls back to defaults if collection doesn't exist or is empty.
    """
    global _agent_status
    try:
        result = await directus_request(
            "GET",
            "/items/agent_settings?filter[setting_type][_eq]=agent_status"
        )
        settings = result.get("data", [])
        if settings and len(settings) > 0:
            saved_status = settings[0].get("value", {})
            if isinstance(saved_status, dict):
                for agent_type, enabled in saved_status.items():
                    if agent_type in _agent_status:
                        _agent_status[agent_type] = bool(enabled)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded agent status from Directus")
                return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Could not load agent status from Directus: {e}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Using default status (all enabled)")
    return False


async def save_agent_status_to_directus():
    """
    Save agent status to Directus agent_settings collection.
    Creates or updates the agent_status setting.
    """
    try:
        # Check if setting exists
        result = await directus_request(
            "GET",
            "/items/agent_settings?filter[setting_type][_eq]=agent_status"
        )
        settings = result.get("data", [])

        setting_data = {
            "setting_type": "agent_status",
            "value": _agent_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if settings and len(settings) > 0:
            # Update existing
            setting_id = settings[0]["id"]
            await directus_request("PATCH", f"/items/agent_settings/{setting_id}", setting_data)
        else:
            # Create new
            await directus_request("POST", "/items/agent_settings", setting_data)

        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Could not save agent status to Directus: {e}")
        return False


# ==========================================
# Session Security - UUID Access Control
# ==========================================
# Each agent session gets a unique session_id
# Sessions track which UUIDs the agent is allowed to access
# PreToolUse hooks validate all Directus calls against this

_active_sessions: dict[str, dict] = {}
# Structure: {
#   "session-uuid": {
#       "allowed_uuids": {"uuid1", "uuid2"},  # Set of allowed item IDs
#       "allowed_collections": {"leads", "emails"},  # Allowed collections
#       "created_at": datetime,
#       "agent_type": "email",
#       "violation_count": 0
#   }
# }

# Prompt cache (refreshed on startup and every 5 minutes)
_prompt_cache = {}
_cache_timestamp = None
CACHE_TTL_SECONDS = 300  # 5 minutes

# Fallback prompts (used if Directus fetch fails)
FALLBACK_PROMPTS = {
    "email": """You are the Shinobi Email Agent. Your job is to:
1. Analyze the inbound email context provided
2. Draft an appropriate professional response
3. Store the draft in the service_workflows collection with status 'pending_approval'
4. NEVER send emails directly - always create drafts for human approval

Use the Directus MCP tools to read context and write drafts.
Use Gmail MCP tools ONLY to read emails, never to send.
""",

    "lead": """You are the Shinobi Lead Agent. Your job is to:
1. Analyze new leads and qualify them
2. Score leads based on company size, urgency, and fit
3. Update the lead record with score and notes
4. If high-priority, create a task for immediate follow-up

Use the Directus MCP tools to read/write lead data.
""",

    "tracker": """You are the Shinobi Tracker Agent. Your job is to:
1. Scan project_trackers for overdue items
2. Flag any issues and update status
3. Create alerts for items needing attention

Use the Directus MCP tools to read/update tracker data.
"""
}


async def fetch_prompts_from_directus() -> dict:
    """
    Fetch prompts from service_prompts collection.
    Returns dict keyed by prompt_name with prompt_content as value.
    """
    global _prompt_cache, _cache_timestamp

    # Check cache validity
    now = datetime.now(timezone.utc)
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
        return _prompt_cache

    try:
        result = await directus_request(
            "GET",
            "/items/service_prompts?filter[status][_eq]=active&fields=prompt_name,prompt_type,prompt_content,variables"
        )

        prompts = {}
        for item in result.get("data", []):
            name = item.get("prompt_name", "")
            content = item.get("prompt_content", "")
            if name and content:
                prompts[name] = {
                    "content": content,
                    "type": item.get("prompt_type"),
                    "variables": item.get("variables", [])
                }

        # Update cache
        _prompt_cache = prompts
        _cache_timestamp = now
        print(f"[{now.strftime('%H:%M:%S')}] Loaded {len(prompts)} prompts from Directus")

        return prompts

    except Exception as e:
        print(f"[ERROR] Failed to fetch prompts from Directus: {e}")
        return {}


def get_agent_prompt(agent_type: str, prompts_dict: dict) -> str:
    """
    Get prompt for agent type.
    Checks Directus prompts first, falls back to hardcoded.

    Prompt naming convention: {agent_type}_agent_system
    Example: email_agent_system, lead_agent_system
    """
    # Try Directus prompt first
    prompt_key = f"{agent_type}_agent_system"
    if prompt_key in prompts_dict:
        return prompts_dict[prompt_key]["content"]

    # Also try just the agent_type as key
    if agent_type in prompts_dict:
        return prompts_dict[agent_type]["content"]

    # Fall back to hardcoded
    return FALLBACK_PROMPTS.get(agent_type, "")


def substitute_variables(prompt: str, context: dict) -> str:
    """
    Replace {{variable}} placeholders with values from context.
    """
    import re

    def replace_var(match):
        var_name = match.group(1)
        # Support nested keys like payload.email
        value = context
        for key in var_name.split('.'):
            if isinstance(value, dict):
                value = value.get(key, f"{{{{MISSING:{var_name}}}}}")
            else:
                return f"{{{{MISSING:{var_name}}}}}"
        return str(value)

    return re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_var, prompt)


# ==========================================
# Session Security Functions
# ==========================================

def create_session(
    agent_type: str,
    primary_uuid: str,
    collection: str,
    additional_uuids: Set[str] = None
) -> str:
    """
    Create a new secure session for an agent task.
    Returns session_id that must be passed to Claude.
    """
    session_id = str(uuid.uuid4())

    allowed_uuids = {primary_uuid}
    if additional_uuids:
        allowed_uuids.update(additional_uuids)

    _active_sessions[session_id] = {
        "allowed_uuids": allowed_uuids,
        "allowed_collections": {collection},
        "created_at": datetime.now(timezone.utc),
        "agent_type": agent_type,
        "primary_uuid": primary_uuid,
        "violation_count": 0
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Session created: {session_id[:8]}... "
          f"(agent={agent_type}, primary={primary_uuid[:8]}...)")

    return session_id


def validate_access(session_id: str, tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """
    Validate if a tool call is allowed for this session.
    Returns (allowed: bool, reason: str)

    Called by PreToolUse hook via /hook/validate endpoint.
    """
    # Check session exists
    if session_id not in _active_sessions:
        return False, "Invalid session ID - session expired or never existed"

    session = _active_sessions[session_id]

    # Only check Directus MCP tools
    if not tool_name.startswith("mcp__directus__"):
        return True, "Non-Directus tool - allowed"

    # Extract UUIDs from tool input
    requested_uuids = set()

    # Check 'keys' parameter (used in items read/update/delete)
    if "keys" in tool_input and tool_input["keys"]:
        for key in tool_input["keys"]:
            if key:
                requested_uuids.add(str(key))

    # Check 'key' parameter (singular)
    if "key" in tool_input and tool_input["key"]:
        requested_uuids.add(str(tool_input["key"]))

    # Check nested data for IDs
    if "data" in tool_input:
        data = tool_input["data"]
        if isinstance(data, dict):
            if "id" in data:
                requested_uuids.add(str(data["id"]))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "id" in item:
                    requested_uuids.add(str(item["id"]))

    # Check collection access
    if "collection" in tool_input:
        collection = tool_input["collection"]
        # Allow reads from certain collections always (for context gathering)
        read_always_allowed = {"service_prompts", "agent_logs", "service_workflows"}
        if collection in read_always_allowed and tool_input.get("action") == "read":
            return True, f"Read from {collection} always allowed"

        # For strict mode, check collection is in allowed set
        # (Currently permissive - agent can read from any collection for context)

    # If we found UUIDs being accessed, check they're allowed
    if requested_uuids:
        unauthorized = requested_uuids - session["allowed_uuids"]
        if unauthorized:
            session["violation_count"] += 1
            violation_msg = (
                f"ACCESS DENIED: Attempted to access unauthorized records. "
                f"Requested: {list(unauthorized)[:3]}... "  # Show max 3
                f"Session allows: {list(session['allowed_uuids'])[:3]}... "
                f"Violation #{session['violation_count']}"
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] SECURITY: {violation_msg}")
            return False, violation_msg

    return True, "Access validated"


def end_session(session_id: str) -> dict:
    """
    End a session and return summary.
    """
    if session_id not in _active_sessions:
        return {"error": "Session not found"}

    session = _active_sessions.pop(session_id)
    duration = (datetime.now(timezone.utc) - session["created_at"]).total_seconds()

    summary = {
        "session_id": session_id,
        "agent_type": session["agent_type"],
        "duration_seconds": duration,
        "violation_count": session["violation_count"],
        "primary_uuid": session["primary_uuid"]
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Session ended: {session_id[:8]}... "
          f"(violations={session['violation_count']}, duration={duration:.1f}s)")

    return summary


async def log_security_violation(
    session_id: str,
    tool_name: str,
    tool_input: dict,
    reason: str
):
    """Log security violation to agent_logs and potentially terminate session."""
    session = _active_sessions.get(session_id, {})

    try:
        log_data = {
            "agent_type": session.get("agent_type", "unknown"),
            "trigger_event": "security_violation",
            "collection": tool_input.get("collection", "unknown"),
            "item_id": session.get("primary_uuid", "unknown"),
            "status": "blocked",
            "error": f"Tool: {tool_name} | Reason: {reason} | Input: {json.dumps(tool_input)[:500]}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await directus_request("POST", "/items/agent_logs", log_data)
    except Exception as e:
        print(f"[ERROR] Failed to log security violation: {e}")


class WebhookPayload(BaseModel):
    """Incoming webhook from Directus"""
    event: str  # items.create, items.update, etc.
    collection: str
    key: Optional[str] = None
    keys: Optional[list] = None
    payload: Optional[dict] = None


class AgentTask(BaseModel):
    """Task to be processed by an agent"""
    agent_type: str  # email, lead, tracker
    trigger_event: str
    collection: str
    item_id: str
    context: dict


class AgentResponse(BaseModel):
    """Response from agent execution"""
    success: bool
    agent_type: str
    task_id: str
    result: Optional[str] = None
    error: Optional[str] = None
    logs: list = []


# Async HTTP client for Directus API
async def directus_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make authenticated request to Directus API"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
        url = f"{DIRECTUS_URL}{endpoint}"

        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()


async def log_agent_activity(
    agent_type: str,
    trigger_event: str,
    collection: str,
    item_id: str,
    status: str,
    result: str = None,
    error: str = None
):
    """Log agent activity to agent_logs collection"""
    try:
        log_data = {
            "agent_type": agent_type,
            "trigger_event": trigger_event,
            "collection": collection,
            "item_id": item_id,
            "status": status,
            "result": result,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await directus_request("POST", "/items/agent_logs", log_data)
    except Exception as e:
        print(f"[ERROR] Failed to log agent activity: {e}")


def get_agent_for_type(agent_type: str) -> Optional[BaseAgent]:
    """Get the appropriate SDK-based agent for a given type."""
    agent_map = {
        "email": _email_agent,
        "lead": _marketing_agent,  # Marketing handles lead nurturing
        "tracker": _client_services_agent,  # Client services handles project tracking
        "finance": _finance_agent,
        "marketing": _marketing_agent,
        "client_services": _client_services_agent,
    }
    return agent_map.get(agent_type)


async def invoke_claude_agent(task: AgentTask) -> AgentResponse:
    """
    Invoke Claude Agent SDK with the appropriate department agent.
    Routes tasks to specialized agents based on agent_type.
    Falls back to OrchestratorAgent for classification if needed.

    Security: Creates a session that restricts access to only
    the specific record(s) related to this task.
    """
    # ==========================================
    # Check Agent Status (Enable/Disable)
    # ==========================================
    if not is_agent_enabled(task.agent_type):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent '{task.agent_type}' is DISABLED - rejecting task {task.item_id[:8]}...")
        return AgentResponse(
            success=False,
            agent_type=task.agent_type,
            task_id=task.item_id,
            error=f"Agent '{task.agent_type}' is currently disabled",
            logs=[f"Task rejected: agent disabled at {datetime.now().strftime('%H:%M:%S')}"]
        )

    # ==========================================
    # Create Secure Session
    # ==========================================
    session_id = create_session(
        agent_type=task.agent_type,
        primary_uuid=task.item_id,
        collection=task.collection
    )

    try:
        # Get the appropriate agent for this task type
        agent = get_agent_for_type(task.agent_type)

        if not agent:
            # Use orchestrator to classify and route
            if _orchestrator:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No direct agent for '{task.agent_type}', routing through orchestrator")
                routing_result = await _orchestrator.classify_and_route({
                    "event": task.trigger_event,
                    "collection": task.collection,
                    "item_id": task.item_id,
                    "context": task.context
                })

                # Get the recommended department's agent
                department = routing_result.get("department")
                if department:
                    department_to_type = {
                        "finance": "finance",
                        "marketing": "marketing",
                        "client_services": "client_services",
                        "sales": "marketing",  # Sales handled by marketing
                        "production": "client_services",  # Production handled by client services
                        "operations": "client_services",
                    }
                    agent_type_mapped = department_to_type.get(department, "client_services")
                    agent = get_agent_for_type(agent_type_mapped)

        if not agent:
            end_session(session_id)
            return AgentResponse(
                success=False,
                agent_type=task.agent_type,
                task_id=task.item_id,
                error=f"No agent available for type: {task.agent_type}"
            )

        # Build context for the agent with security session info
        agent_context = {
            "session_id": session_id,
            "authorized_record": task.item_id,
            "authorized_collection": task.collection,
            "task_type": task.trigger_event,
            "trigger_event": task.trigger_event,
            "collection": task.collection,
            "item_id": task.item_id,
            **task.context
        }

        # Run the SDK-based agent
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Invoking {agent.name} for task {task.item_id[:8]}...")

        result = await agent.run(agent_context)

        # End session and get summary
        session_summary = end_session(session_id)

        if result.success:
            return AgentResponse(
                success=True,
                agent_type=task.agent_type,
                task_id=task.item_id,
                result=json.dumps(result.data) if result.data else result.message,
                logs=[
                    f"Agent: {agent.name}",
                    f"Session duration: {session_summary.get('duration_seconds', 0):.1f}s",
                    f"Security violations blocked: {session_summary.get('violation_count', 0)}"
                ]
            )
        else:
            return AgentResponse(
                success=False,
                agent_type=task.agent_type,
                task_id=task.item_id,
                error=result.error or "Agent execution failed",
                logs=[f"Session violations: {session_summary.get('violation_count', 0)}"]
            )

    except asyncio.TimeoutError:
        end_session(session_id)
        return AgentResponse(
            success=False,
            agent_type=task.agent_type,
            task_id=task.item_id,
            error="Agent execution timed out"
        )
    except Exception as e:
        end_session(session_id)
        return AgentResponse(
            success=False,
            agent_type=task.agent_type,
            task_id=task.item_id,
            error=str(e)
        )


async def process_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Process incoming Directus webhook and route to appropriate agent"""

    # Determine which agent should handle this
    agent_type = None

    if payload.collection == "emails":
        agent_type = "email"
    elif payload.collection == "leads":
        agent_type = "lead"
    elif payload.collection in ["project_trackers", "tasks", "milestones"]:
        agent_type = "tracker"

    if not agent_type:
        return {"status": "ignored", "reason": f"No agent for collection: {payload.collection}"}

    # Get item ID
    item_id = payload.key or (payload.keys[0] if payload.keys else None)
    if not item_id:
        return {"status": "error", "reason": "No item ID in webhook payload"}

    # Create agent task
    task = AgentTask(
        agent_type=agent_type,
        trigger_event=payload.event,
        collection=payload.collection,
        item_id=str(item_id),
        context=payload.payload or {}
    )

    # Log the incoming task
    await log_agent_activity(
        agent_type=agent_type,
        trigger_event=payload.event,
        collection=payload.collection,
        item_id=str(item_id),
        status="received"
    )

    # Run agent in background
    background_tasks.add_task(run_agent_task, task)

    return {
        "status": "accepted",
        "agent_type": agent_type,
        "item_id": item_id,
        "message": f"Task queued for {agent_type} agent"
    }


async def run_agent_task(task: AgentTask):
    """Background task to run agent and log results"""
    try:
        # Log start
        await log_agent_activity(
            agent_type=task.agent_type,
            trigger_event=task.trigger_event,
            collection=task.collection,
            item_id=task.item_id,
            status="processing"
        )

        # Invoke agent
        response = await invoke_claude_agent(task)

        # Log completion
        await log_agent_activity(
            agent_type=task.agent_type,
            trigger_event=task.trigger_event,
            collection=task.collection,
            item_id=task.item_id,
            status="completed" if response.success else "failed",
            result=response.result,
            error=response.error
        )

    except Exception as e:
        await log_agent_activity(
            agent_type=task.agent_type,
            trigger_event=task.trigger_event,
            collection=task.collection,
            item_id=task.item_id,
            status="error",
            error=str(e)
        )


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global _orchestrator, _finance_agent, _marketing_agent, _client_services_agent, _email_agent

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Shinobi Agent Service starting on port {AGENT_PORT}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Directus URL: {DIRECTUS_URL}")

    # Validate API key
    if not ANTHROPIC_API_KEY:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARNING: ANTHROPIC_API_KEY not set - agents will fail")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Anthropic API key configured")

    # Initialize SDK-based agents
    agent_config = AgentConfig(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        enable_tools=True
    )

    _orchestrator = OrchestratorAgent(config=agent_config)
    _finance_agent = FinanceAgent(config=agent_config)
    _marketing_agent = MarketingAgent(config=agent_config)
    _client_services_agent = ClientServicesAgent(config=agent_config)
    _email_agent = EmailAgent()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Initialized 5 SDK-based agents:")
    print(f"  - OrchestratorAgent (central routing)")
    print(f"  - FinanceAgent (invoicing, payments)")
    print(f"  - MarketingAgent (campaigns, content)")
    print(f"  - ClientServicesAgent (support, relationships)")
    print(f"  - EmailAgent (email drafting)")

    # Preload prompts from Directus on startup
    prompts = await fetch_prompts_from_directus()
    if prompts:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Available prompts: {list(prompts.keys())}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Using fallback prompts: {list(FALLBACK_PROMPTS.keys())}")

    # Load agent status from Directus (persisted enable/disable states)
    await load_agent_status_from_directus()
    enabled_count = sum(1 for v in _agent_status.values() if v)
    disabled_count = sum(1 for v in _agent_status.values() if not v)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent status: {enabled_count} enabled, {disabled_count} disabled")
    if disabled_count > 0:
        disabled_agents = [k for k, v in _agent_status.items() if not v]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Disabled agents: {', '.join(disabled_agents)}")

    yield

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Shinobi Agent Service shutting down")
    # Clear agent references
    _orchestrator = None
    _finance_agent = None
    _marketing_agent = None
    _client_services_agent = None
    _email_agent = None


app = FastAPI(
    title="Shinobi Agent Service",
    description="AI Agent webhook receiver for Directus CRM automation",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "shinobi-agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_sessions": len(_active_sessions),
        "agents_enabled": sum(1 for v in _agent_status.values() if v),
        "agents_disabled": sum(1 for v in _agent_status.values() if not v)
    }


# ==========================================
# Agent Control Endpoints (Enable/Disable)
# ==========================================

@app.get("/agents/status")
async def get_agents_status():
    """
    Get the current enabled/disabled status of all agents.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": get_all_agent_status(),
        "summary": {
            "total": len(_agent_status),
            "enabled": sum(1 for v in _agent_status.values() if v),
            "disabled": sum(1 for v in _agent_status.values() if not v)
        }
    }


@app.post("/agents/{agent_type}/enable")
async def enable_agent(agent_type: str, background_tasks: BackgroundTasks):
    """
    Enable a specific agent.
    """
    if agent_type not in _agent_status:
        raise HTTPException(status_code=404, detail=f"Unknown agent type: {agent_type}")

    set_agent_status(agent_type, True)
    background_tasks.add_task(save_agent_status_to_directus)

    return {
        "status": "enabled",
        "agent_type": agent_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/agents/{agent_type}/disable")
async def disable_agent(agent_type: str, background_tasks: BackgroundTasks):
    """
    Disable a specific agent.
    Disabled agents will reject all incoming tasks.
    """
    if agent_type not in _agent_status:
        raise HTTPException(status_code=404, detail=f"Unknown agent type: {agent_type}")

    set_agent_status(agent_type, False)
    background_tasks.add_task(save_agent_status_to_directus)

    return {
        "status": "disabled",
        "agent_type": agent_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/agents/{agent_type}/toggle")
async def toggle_agent(agent_type: str, background_tasks: BackgroundTasks):
    """
    Toggle a specific agent's status.
    """
    if agent_type not in _agent_status:
        raise HTTPException(status_code=404, detail=f"Unknown agent type: {agent_type}")

    new_status = not _agent_status[agent_type]
    set_agent_status(agent_type, new_status)
    background_tasks.add_task(save_agent_status_to_directus)

    return {
        "status": "enabled" if new_status else "disabled",
        "agent_type": agent_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/agents/disable-all")
async def disable_all_agents(background_tasks: BackgroundTasks):
    """
    Emergency: Disable all agents at once.
    """
    for agent_type in _agent_status:
        _agent_status[agent_type] = False

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ALL AGENTS DISABLED (emergency shutdown)")
    background_tasks.add_task(save_agent_status_to_directus)

    return {
        "status": "all_disabled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "All agents have been disabled"
    }


@app.post("/agents/enable-all")
async def enable_all_agents(background_tasks: BackgroundTasks):
    """
    Enable all agents at once.
    """
    for agent_type in _agent_status:
        _agent_status[agent_type] = True

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ALL AGENTS ENABLED")
    background_tasks.add_task(save_agent_status_to_directus)

    return {
        "status": "all_enabled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "All agents have been enabled"
    }


# ==========================================
# Hook Validation Endpoints
# ==========================================

class HookValidateRequest(BaseModel):
    """Request from PreToolUse hook script"""
    session_id: str
    tool_name: str
    tool_input: dict


class HookValidateResponse(BaseModel):
    """Response to PreToolUse hook script"""
    allowed: bool
    reason: str


@app.post("/hook/validate", response_model=HookValidateResponse)
async def validate_hook(request: HookValidateRequest, background_tasks: BackgroundTasks):
    """
    Validate a tool call from the PreToolUse hook.

    This endpoint is called by the hook script BEFORE Claude executes any tool.
    It checks if the session is authorized to access the requested records.

    Returns:
        allowed: True if the tool call should proceed
        reason: Explanation for the decision
    """
    allowed, reason = validate_access(
        session_id=request.session_id,
        tool_name=request.tool_name,
        tool_input=request.tool_input
    )

    # Log security violations asynchronously
    if not allowed:
        background_tasks.add_task(
            log_security_violation,
            request.session_id,
            request.tool_name,
            request.tool_input,
            reason
        )

    return HookValidateResponse(allowed=allowed, reason=reason)


@app.get("/sessions")
async def list_sessions():
    """
    List active sessions (for debugging/monitoring).
    """
    sessions = []
    for session_id, data in _active_sessions.items():
        sessions.append({
            "session_id": session_id[:8] + "...",  # Truncate for display
            "agent_type": data["agent_type"],
            "primary_uuid": data["primary_uuid"][:8] + "...",
            "violation_count": data["violation_count"],
            "age_seconds": (datetime.now(timezone.utc) - data["created_at"]).total_seconds()
        })

    return {
        "active_count": len(_active_sessions),
        "sessions": sessions
    }


@app.post("/sessions/{session_id}/end")
async def force_end_session(session_id: str):
    """
    Force end a session (for admin/emergency use).
    """
    if session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    summary = end_session(session_id)
    return {"status": "ended", "summary": summary}


@app.get("/prompts")
async def list_prompts():
    """
    List all available prompts.
    Shows Directus prompts + fallback prompts.
    """
    prompts_dict = await fetch_prompts_from_directus()

    return {
        "directus_prompts": list(prompts_dict.keys()),
        "fallback_prompts": list(FALLBACK_PROMPTS.keys()),
        "cache_age_seconds": (datetime.now(timezone.utc) - _cache_timestamp).total_seconds() if _cache_timestamp else None,
        "cache_ttl_seconds": CACHE_TTL_SECONDS
    }


@app.post("/prompts/reload")
async def reload_prompts():
    """
    Force reload prompts from Directus.
    Clears cache and fetches fresh.
    """
    global _prompt_cache, _cache_timestamp
    _prompt_cache = {}
    _cache_timestamp = None

    prompts = await fetch_prompts_from_directus()

    return {
        "status": "reloaded",
        "prompts_loaded": list(prompts.keys()),
        "count": len(prompts)
    }


@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Receive webhook from Directus Flow.
    Routes to appropriate agent based on collection.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Webhook received: {payload.event} on {payload.collection}")
    return await process_webhook(payload, background_tasks)


@app.post("/trigger/{agent_type}")
async def manual_trigger(agent_type: str, task: AgentTask, background_tasks: BackgroundTasks):
    """
    Manually trigger an agent for testing.
    """
    # Check if prompt exists (in Directus or fallback)
    prompts_dict = await fetch_prompts_from_directus()
    prompt = get_agent_prompt(agent_type, prompts_dict)

    if not prompt:
        raise HTTPException(status_code=400, detail=f"No prompt found for agent type: {agent_type}")

    task.agent_type = agent_type

    await log_agent_activity(
        agent_type=agent_type,
        trigger_event="manual_trigger",
        collection=task.collection,
        item_id=task.item_id,
        status="received"
    )

    background_tasks.add_task(run_agent_task, task)

    return {
        "status": "accepted",
        "agent_type": agent_type,
        "item_id": task.item_id,
        "message": f"Manual trigger queued for {agent_type} agent"
    }


class ApprovalPayload(BaseModel):
    """Incoming approval response from Directus"""
    prompt_id: str
    response: str
    context: Optional[dict] = None


@app.post("/approval")
async def handle_approval(payload: ApprovalPayload, background_tasks: BackgroundTasks):
    """
    Handle human approval responses from Directus.
    When a human responds to a prompt, this processes the response
    and takes the appropriate action (e.g., send email if approved).
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Approval received for prompt: {payload.prompt_id}")

    # Check what type of approval this is
    context = payload.context or {}
    approval_type = context.get("type", "unknown")
    response = payload.response.lower()

    if approval_type == "email_draft":
        if response == "approve":
            # User approved - trigger email send
            background_tasks.add_task(
                send_approved_email,
                payload.prompt_id,
                context
            )
            return {"status": "processing", "action": "sending_email"}
        elif response == "reject":
            # User rejected - log and do nothing
            await log_agent_activity(
                agent_type="email",
                trigger_event="approval_rejected",
                collection="human_prompts",
                item_id=payload.prompt_id,
                status="completed",
                result="Email draft rejected by user"
            )
            return {"status": "rejected", "action": "none"}
        else:
            # Edit requested - create new prompt with edit capability
            return {"status": "edit_requested", "action": "await_edit"}

    return {"status": "processed", "approval_type": approval_type}


async def send_approved_email(prompt_id: str, context: dict):
    """Send an email that was approved by human using Gmail API directly."""
    try:
        email_id = context.get("email_id")
        draft_subject = context.get("draft_subject")
        draft_body = context.get("draft_body")
        original_from = context.get("original_from")
        thread_id = context.get("thread_id")
        reply_to_message_id = context.get("reply_to_message_id")

        if not all([email_id, draft_subject, draft_body, original_from]):
            raise ValueError("Missing required email context")

        # Send email using Gmail API directly (no subprocess/CLI needed)
        result = await gmail_send_email(
            to=original_from,
            subject=draft_subject,
            body=draft_body,
            thread_id=thread_id,
            reply_to_message_id=reply_to_message_id
        )

        if result.get("success"):
            await log_agent_activity(
                agent_type="email",
                trigger_event="email_sent",
                collection="emails",
                item_id=email_id,
                status="completed",
                result=f"Email sent successfully. Message ID: {result.get('message_id')}"
            )

            # Update email record in Directus with sent status
            try:
                async with httpx.AsyncClient() as client:
                    await client.patch(
                        f"{DIRECTUS_URL}/items/emails/{email_id}",
                        headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
                        json={
                            "status": "sent",
                            "sent_at": datetime.now(timezone.utc).isoformat(),
                            "gmail_message_id": result.get("message_id"),
                            "gmail_thread_id": result.get("thread_id")
                        }
                    )
            except Exception as update_error:
                print(f"Warning: Failed to update email record: {update_error}")

        else:
            await log_agent_activity(
                agent_type="email",
                trigger_event="email_send_failed",
                collection="emails",
                item_id=email_id,
                status="failed",
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        await log_agent_activity(
            agent_type="email",
            trigger_event="email_send_error",
            collection="human_prompts",
            item_id=prompt_id,
            status="failed",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
