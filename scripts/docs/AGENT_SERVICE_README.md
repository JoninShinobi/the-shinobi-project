# Shinobi C2 Agent Service

AI-powered automation layer for the Shinobi business management system.

## Architecture

```
Directus Flow → Webhook POST → FastAPI (port 5001) → Claude CLI → Directus MCP
                                    ↓
                              agent_logs (audit)
                                    ↓
                         human_prompts (approval gate)
```

## Quick Start

```bash
# 1. Configure environment
cp scripts/.env.example scripts/.env
# Edit scripts/.env with your tokens

# 2. Install dependencies
pip install -r scripts/requirements.txt

# 3. Start the service
./scripts/run_agent_service.sh
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_PORT` | Port for the agent service | `5002` |
| `DIRECTUS_URL` | Directus instance URL | `http://localhost:8055` |
| `DIRECTUS_ADMIN_TOKEN` | Directus API token with admin access | Required |

## Endpoints

### `GET /health`
Health check endpoint.

### `GET /prompts`
List all available prompts (Directus + fallback).

### `POST /prompts/reload`
Force reload prompts from Directus, clearing the cache.

### `POST /webhook`
Receives webhooks from Directus flows. Automatically routes to the appropriate agent based on collection:

| Collection | Agent |
|------------|-------|
| `emails` | Email Agent |
| `leads` | Lead Agent |
| `project_trackers`, `tasks`, `milestones` | Tracker Agent |

**Payload format:**
```json
{
  "event": "items.create",
  "collection": "emails",
  "key": "uuid-here",
  "payload": { ... }
}
```

### `POST /trigger/{agent_type}`
Manually trigger an agent for testing.

### `POST /approval`
Handle human approval responses from Directus.

## Agents

### Email Agent
- Analyzes inbound emails
- Drafts professional responses
- **Never sends directly** - creates drafts for human approval
- Uses Gmail MCP for reading only

### Lead Agent
- Scores new leads
- Qualifies based on company size, urgency, fit
- Creates follow-up tasks for high-priority leads

### Tracker Agent
- Scans for overdue items
- Updates project health status
- Creates alerts for attention items

## Prompt Management

Prompts are stored in the `service_prompts` Directus collection. The agent service:
1. Fetches prompts from Directus on startup
2. Caches prompts for 5 minutes
3. Falls back to hardcoded prompts if Directus fetch fails

### Prompt Naming Convention
- `{agent_type}_agent_system` - e.g., `email_agent_system`, `lead_agent_system`

### Creating a Prompt in Directus

Navigate to **Content → service_prompts** and create:

| Field | Example |
|-------|---------|
| `prompt_name` | `email_agent_system` |
| `prompt_type` | `system` |
| `status` | `active` |
| `prompt_content` | See below |
| `variables` | `["sender_email", "subject", "body"]` |

**Example prompt_content:**
```
You are the Shinobi Email Agent. Analyze inbound emails and draft professional responses.

Context:
- Email from: {{sender_email}}
- Subject: {{subject}}
- Body: {{body}}

Tasks:
1. Determine intent (inquiry, support, complaint, sales)
2. Check if sender exists in clients/leads collections
3. Draft appropriate response
4. Store draft in service_workflows for approval

Never send directly. All responses require human approval.
```

### Variable Substitution
Prompts support `{{variable}}` placeholders that get replaced with values from the webhook context:
- `{{sender_email}}` → replaced with `context.sender_email`
- `{{payload.status}}` → replaced with `context.payload.status` (nested access)

### Reloading Prompts
After editing prompts in Directus, either:
- Wait 5 minutes for cache to expire
- Call `POST /prompts/reload` to force refresh

## Human Approval Workflow

1. Agent drafts a response (e.g., email reply)
2. Draft stored in `service_workflows` with status `pending_approval`
3. Approval request created in `human_prompts`
4. Human reviews in Directus UI
5. On approval → agent sends via Gmail MCP
6. On rejection → logged and no action taken

## Directus Flows Setup

Import the flows from `scripts/directus_flows_config.json`:

1. **AI Agent - Inbound Email**
   - Trigger: `emails` collection, `items.create`
   - Filter: `direction = 'inbound'`
   - Action: Webhook to `http://localhost:5002/webhook`

2. **AI Agent - New Lead**
   - Trigger: `leads` collection, `items.create`
   - Action: Webhook to `http://localhost:5002/webhook`

3. **AI Agent - Approval Response**
   - Trigger: `human_prompts` collection, `items.update`
   - Filter: `status = 'responded'`
   - Action: Webhook to `http://localhost:5002/approval`

## Logging

All agent activity is logged to the `agent_logs` collection:

| Field | Description |
|-------|-------------|
| `agent_type` | email, lead, or tracker |
| `trigger_event` | The event that triggered the agent |
| `collection` | Source collection |
| `item_id` | ID of the item being processed |
| `status` | received, processing, completed, failed, error |
| `result` | Agent output on success |
| `error` | Error message on failure |
| `timestamp` | When the action occurred |

## Development

### Testing locally

```bash
# Start the service
./scripts/run_agent_service.sh

# Send a test webhook
curl -X POST http://localhost:5002/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "items.create",
    "collection": "leads",
    "key": "test-123",
    "payload": {
      "company_name": "Test Corp",
      "contact_name": "John Doe",
      "email": "john@test.com"
    }
  }'
```

### Adding a new agent

1. Create `scripts/agents/new_agent.py` extending `BaseAgent`
2. Add prompt to `AGENT_PROMPTS` in `agent_service.py`
3. Add collection routing in `process_webhook()`
4. Create Directus flow to trigger on relevant events

## Security

- Agent service requires `DIRECTUS_ADMIN_TOKEN` for full access
- Email sending requires human approval (no autonomous sends)
- All actions logged for audit trail
- Claude CLI runs in project directory with configured MCP servers

### Session-Based Access Control

**Every agent session is restricted to specific records:**

```
1. Webhook triggers with item UUID (e.g., lead "abc-123")
2. Python creates session: allowed_uuids = {"abc-123"}
3. Session ID passed to Claude via environment variable
4. PreToolUse hook fires BEFORE every Directus MCP call
5. Hook calls /hook/validate endpoint with tool + session_id
6. Python checks if requested UUID is in allowed_uuids
7. If mismatch → BLOCK (tool never executes)
8. If match → ALLOW (tool proceeds)
```

**This prevents:**
- Claude accidentally accessing wrong profiles
- Data leakage between unrelated records
- Confused agents mixing up user data

### Security Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hook/validate` | POST | Called by PreToolUse hook to validate tool calls |
| `/sessions` | GET | List active sessions (monitoring) |
| `/sessions/{id}/end` | POST | Force-terminate a session |

### Security Violations

All blocked attempts are logged to `agent_logs` with:
- `trigger_event`: "security_violation"
- `status`: "blocked"
- `error`: Details of what was attempted

### Hook Configuration

The PreToolUse hook is configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__directus__*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/security_guard.py"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

**Claude CLI not found:**
```bash
npm install -g @anthropic/claude-code
```

**Directus connection refused:**
- Ensure Directus is running on the configured URL
- Check the admin token is valid

**Agent timeout:**
- Default timeout is 120 seconds
- Complex tasks may need longer timeout in `invoke_claude_agent()`
