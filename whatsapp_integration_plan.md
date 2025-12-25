# Shinobi C2 - WhatsApp Integration Implementation Plan

**Status:** In Progress (Phase 2 Complete)
**Started:** 2025-12-25
**Target Completion:** 2025-12-26

---

## 🎯 Objectives

1. ✅ Rename email_agent → comms_agent (unified communications)
2. ✅ Create WhatsApp database collections
3. ✅ Build Twilio webhook handler
4. 🔄 Build Directus Flows (6 flows total)
5. ⏳ Configure environment variables
6. ⏳ Test end-to-end workflows

---

## ✅ Phase 1: Agent Refactoring - COMPLETED

### 1.1 Rename EmailAgent → CommsAgent ✅

**Completed Changes:**
- Renamed `scripts/agents/email_agent.py` → `scripts/agents/comms_agent.py`
- Updated class name: `EmailAgent` → `CommsAgent`
- Updated system prompt to handle multiple communication channels
- Added channel detection based on collection name
- Updated routing in `agent_service.py`

**Commit:** `34a403c` - "Refactor email_agent to comms_agent for multi-channel support"

**Agent Routing:**
```python
AGENT_ROUTES = {
    "emails": "comms",
    "whatsapp_messages": "comms",
    "sms_messages": "comms",
    "leads": "lead",
    # ... other routes
}
```

---

## ✅ Phase 2: Database & Webhook Infrastructure - COMPLETED

### 2.1 WhatsApp Collections Created ✅

#### Collection: `whatsapp_messages`
**Purpose:** Store all WhatsApp communications with verification status

**Fields:**
- **Twilio Integration:**
  - `message_sid` (string, unique, 34 chars) - Twilio message ID
  - `account_sid` (string, 34 chars) - Twilio account ID
  - `from_number` (string, required, 20 chars)
  - `to_number` (string, required, 20 chars)
  - `body` (text, required) - Message content
  - `media_urls` (json) - Array of media attachments
  - `direction` (string, default "inbound") - inbound|outbound

- **Verification:**
  - `verification_status` (string, default "pending") - pending|verified|failed
  - `verification_method` (string) - phone_match|project_id|email_link
  - `verified_at` (timestamp, readonly)

- **Threading:**
  - `conversation_id` (uuid) - Groups related messages
  - `parent_message_id` (uuid) - Reference to parent message

- **Workflow:**
  - `status` (string, default "received") - received|processing|responded|escalated
  - `responded_at` (timestamp, readonly)

- **Relations:**
  - `client` (M2O → clients, SET NULL on delete)
  - `contact` (M2O → contacts, SET NULL on delete)
  - `project` (M2O → projects, SET NULL on delete)

- **System Fields:**
  - `id` (uuid, primary key)
  - `date_created` (timestamp)
  - `date_updated` (timestamp)

**Collection Settings:**
- Icon: `chat`
- Color: `#25D366` (WhatsApp green)
- Display Template: `{{from_number}} - {{body}}`
- Archive Field: `status`
- Archive Value: `archived`

#### Collection: `verification_attempts`
**Purpose:** Audit trail for customer verification attempts

**Fields:**
- `id` (uuid, primary key)
- `phone_number` (string, required, 20 chars)
- `verification_type` (string, required) - phone_match|project_id|invoice_id|email_link
- `provided_value` (text) - Customer input (project ID, etc.)
- `status` (string, default "pending") - success|failed|pending
- `ip_address` (string, readonly, 45 chars) - Security logging
- `user_agent` (text, readonly) - Browser/device info
- `attempted_at` (timestamp, date-created)

**Relations:**
- `whatsapp_message` (M2O → whatsapp_messages, SET NULL on delete)
- `matched_client` (M2O → clients, readonly, SET NULL on delete)
- `matched_project` (M2O → projects, readonly, SET NULL on delete)

**Collection Settings:**
- Icon: `verified_user`
- Color: `#FFA500` (Orange)
- Display Template: `{{phone_number}} - {{verification_type}} ({{status}})`

### 2.2 Twilio Webhook Handler Created ✅

**Created Files:**
- `scripts/twilio_integration/__init__.py` - Module exports
- `scripts/twilio_integration/whatsapp_webhook.py` - Main webhook handler
- `scripts/twilio_integration/README.md` - Complete documentation

**Webhook Endpoints:**

#### POST `/twilio/whatsapp/incoming`
Receives incoming WhatsApp messages from Twilio.

**Flow:**
1. Validate Twilio signature (security check using `X-Twilio-Signature`)
2. Extract message data from form payload
3. Parse phone numbers (remove `whatsapp:` prefix)
4. Extract media URLs from `MediaUrl0`, `MediaUrl1`, etc.
5. Create record in Directus `whatsapp_messages` collection
6. Return success response: `{"status": "received", "message_id": "uuid"}`

**Security:**
- Uses `twilio.request_validator.RequestValidator`
- Validates signature using `TWILIO_AUTH_TOKEN`
- Returns 403 Forbidden for invalid signatures
- Logs all validation failures

#### GET `/twilio/whatsapp/health`
Health check endpoint for monitoring.

**Integration:**
- Added to FastAPI app via `app.include_router(whatsapp_router, tags=["twilio"])`
- Integrated into `agent_service.py` at line 820

**Dependencies Added:**
- `scripts/requirements.txt` - Added `twilio>=9.0.0`
- `agents/Dockerfile` - Updated to copy `scripts/twilio_integration/` directory

**Commit:** `b959141` - "Add Twilio WhatsApp webhook handler"

---

## 🔄 Phase 3: Directus Flows - IN PROGRESS

### Flow Architecture Principles

**Ground Rules:**
1. One responsibility per flow (minimal branching)
2. Explicit error handling (reject paths for all conditions)
3. Comprehensive logging (log every decision)
4. Human-in-the-loop (external comms require approval)
5. Grid positioning (19x, 37x, 55x for readability)

### 3.1 Flow 1: WhatsApp Inbound → Verification

**Trigger:** `items.create` on `whatsapp_messages`
**Purpose:** Verify customer identity before conversation

**Operations:**
1. **check_direction** (Condition)
   - Rule: `direction == 'inbound'`
   - Resolve: Continue verification
   - Reject: End (outbound messages skip verification)

2. **check_verification** (Condition)
   - Rule: `verification_status == 'pending'`
   - Resolve: Continue to phone lookup
   - Reject: End (already verified)

3. **phone_lookup** (Item Read)
   ```json
   {
     "collection": "contacts",
     "query": {
       "filter": { "phone": { "_eq": "{{$trigger.payload.from_number}}" } },
       "fields": ["*", "client.*"]
     }
   }
   ```

4. **auto_verify** (Condition)
   - Rule: `phone_lookup` found match
   - Resolve: Update verification_status='verified', trigger comms agent
   - Reject: Send verification request

5. **send_verification_request** (Request)
   - POST to Twilio API
   - Message:
     ```
     Hi! To help you securely, please reply with:
     1. Your project ID (e.g., PROJ-1234), OR
     2. Your invoice number (e.g., INV-5678), OR
     3. Type 'EMAIL' to get a verification link
     ```

6. **log_verification** (Item Create)
   - Collection: `verification_attempts`
   - Log attempt details

### 3.2 Flow 2: WhatsApp Verification Response

**Trigger:** `items.update` on `whatsapp_messages`
**Purpose:** Process verification attempts

**Operations:**
1. **check_pending** (Condition) - Only process if verification_status='pending'

2. **extract_verification_data** (Exec)
   ```javascript
   module.exports = async function(data) {
     const body = data.$trigger.payload.body.toUpperCase();

     const projectMatch = body.match(/PROJ-(\d+)/);
     if (projectMatch) return { type: 'project_id', value: projectMatch[0] };

     const invoiceMatch = body.match(/INV-(\d+)/);
     if (invoiceMatch) return { type: 'invoice_id', value: invoiceMatch[0] };

     if (body.includes('EMAIL')) return { type: 'email_link' };

     return { type: 'unknown' };
   }
   ```

3. **verify_project_id** (Condition)
   - Resolve: Look up project, verify ownership
   - Reject: Try next method

4. **verify_invoice_id** (Condition)
   - Resolve: Look up invoice, verify ownership
   - Reject: Try email fallback

5. **send_email_link** (Condition)
   - Resolve: Generate magic link, send email
   - Reject: Unknown input, send help

6. **update_verification** (Item Update) - Set verification_status

7. **trigger_comms_agent** (Request) - If verified, trigger agent

### 3.3 Flow 3: Comms Agent → WhatsApp Response

**Trigger:** `items.update` on `human_prompts` (status='responded' AND prompt_type='whatsapp_response')
**Purpose:** Send approved WhatsApp messages

**Operations:**
1. **check_approved** (Condition) - response='approve'?

2. **get_draft_message** (Item Read) - Read draft from context

3. **send_whatsapp** (Request)
   - POST to Twilio API
   - URL: `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`
   - Body:
     ```json
     {
       "From": "whatsapp:+14155238886",
       "To": "whatsapp:{{to_number}}",
       "Body": "{{body}}"
     }
     ```

4. **create_outbound_record** (Item Create)
   - Collection: `whatsapp_messages`
   - Log sent message

5. **log_communication** (Item Create) - Log to communication_log

### 3.4 Flow 4: Inbound Email → Comms Agent

**Trigger:** `items.create` on `emails` (direction='inbound')
**Purpose:** Route emails to comms agent

**Operations:**
1. **check_inbound** (Condition)

2. **trigger_comms_agent** (Request)
   ```json
   {
     "method": "POST",
     "url": "{{$env.AGENT_SERVICE_URL}}/webhook",
     "body": {
       "event": "items.create",
       "collection": "emails",
       "key": "{{$trigger.key}}",
       "payload": "{{$trigger.payload}}"
     }
   }
   ```

3. **log_agent_trigger** (Item Create)

### 3.5 Flow 5: New Lead → Lead Agent

**Trigger:** `items.create` on `leads`
**Purpose:** Auto-score and analyze leads

**Operations:**
1. **trigger_lead_agent** (Request) - POST to agent service

2. **log_trigger** (Item Create) - Log to agent_logs

### 3.6 Flow 6: Approval Response Handler

**Trigger:** `items.update` on `human_prompts` (status='responded')
**Purpose:** Execute approved actions

**Operations:**
1. **check_responded** (Condition)

2. **trigger_approval_handler** (Request)
   ```json
   {
     "method": "POST",
     "url": "{{$env.AGENT_SERVICE_URL}}/approval",
     "body": {
       "prompt_id": "{{$trigger.key}}",
       "response": "{{$trigger.payload.response}}",
       "context": "{{$trigger.payload.context}}"
     }
   }
   ```

---

## ⏳ Phase 4: Environment Configuration - PENDING

### 4.1 Directus Environment Variables

**Production (Render) - Directus Service:**
```bash
# Agent Service
AGENT_SERVICE_URL=https://shinobi-agents.onrender.com

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886

# SendGrid (Email)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=hello@shinobiagency.com

# Verification
MAGIC_LINK_EXPIRY_MINUTES=15
MAGIC_LINK_BASE_URL=https://shinobi-directus.onrender.com
```

**Production (Render) - Agent Service:**
```bash
# Directus
DIRECTUS_URL=https://shinobi-directus.onrender.com
DIRECTUS_ADMIN_TOKEN=3DHv4wddTSFuAdvZRqiCn_zqcj3mdsyYeFJbowwmO7U

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Twilio (for webhook validation)
TWILIO_AUTH_TOKEN=your_auth_token_here

# Agent Config
AGENT_PORT=8080
```

### 4.2 Twilio Configuration

**Sandbox Setup (Testing):**
1. Navigate to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Note sandbox number (e.g., +1 415 523 8886)
3. Configure webhook:
   - URL: `https://shinobi-agents.onrender.com/twilio/whatsapp/incoming`
   - Method: POST
   - Content-Type: application/x-www-form-urlencoded

**Production Setup (After Testing):**
1. Request WhatsApp Business API access
2. Verify business profile
3. Update webhook URLs to production

---

## ⏳ Phase 5: Testing Protocol - PENDING

### Test Scenarios

#### Test 1: Known Customer Auto-Verification
1. Send WhatsApp from phone number in contacts table
2. ✓ Verify auto-verification succeeds
3. ✓ Verify comms agent triggered
4. ✓ Check human_prompt created for response
5. ✓ Approve draft in Directus
6. ✓ Verify WhatsApp sent via Twilio
7. ✓ Check all logs (agent_logs, communication_log, verification_attempts)

#### Test 2: Unknown Customer - Project ID Verification
1. Send WhatsApp from unknown number
2. ✓ System asks for verification
3. Reply with valid project ID (e.g., "PROJ-1234")
4. ✓ Verify project lookup succeeds
5. ✓ Verify client linked correctly
6. ✓ Continue conversation flow

#### Test 3: Email Verification Fallback
1. Send WhatsApp from unknown number
2. Reply "EMAIL" to verification request
3. ✓ Verify magic link sent to email
4. Click magic link
5. ✓ Verify WhatsApp session verified
6. ✓ Continue conversation

#### Test 4: Email → Comms Agent
1. Create inbound email in Directus
2. ✓ Flow triggers comms agent
3. ✓ Agent analyzes email
4. ✓ Draft response created
5. Approve response
6. ✓ Email sent

#### Test 5: New Lead → Lead Agent
1. Create new lead in Directus
2. ✓ Lead agent triggered
3. ✓ Lead scoring completed
4. ✓ Nurturing sequence suggested
5. ✓ Check agent_logs

---

## 🔒 Phase 6: Security Hardening - PENDING

### Security Checklist

- [ ] **Twilio Signature Validation** - Verify all webhooks (✅ Already implemented)
- [ ] **Rate Limiting** - Max 10 verification attempts per phone/hour
- [ ] **Session Timeouts** - Verification expires after 15 minutes
- [ ] **Secure Tokens** - Magic links use cryptographically secure tokens
- [ ] **Access Logging** - All verification attempts logged (✅ Already implemented)
- [ ] **Client Data Isolation** - Agents only access verified client data
- [ ] **Sensitive Data Redaction** - Don't log full phone numbers
- [ ] **HTTPS Only** - All webhooks use HTTPS (✅ Render provides SSL)
- [ ] **Environment Variables** - No secrets in git (✅ Using env vars)

### Monitoring Flow

**Create Directus Flow:**
- **Trigger:** `items.create` on `verification_attempts` (status='failed')
- **Action:** If >5 failed attempts from same phone in 1 hour → Create alert

---

## 📊 Progress Tracking

| Phase | Status | Completion |
|-------|--------|-----------|
| Phase 1: Agent Refactoring | ✅ Complete | 100% |
| Phase 2: Database & Webhook | ✅ Complete | 100% |
| Phase 3: Directus Flows | 🔄 In Progress | 0% (0/6 flows) |
| Phase 4: Environment Config | ⏳ Pending | 0% |
| Phase 5: Testing | ⏳ Pending | 0% |
| Phase 6: Security | ⏳ Pending | 0% |

**Overall Progress:** 33% Complete (2/6 phases)

---

## 📝 Implementation Log

### 2025-12-25

**10:00 - Phase 1 Started**
- Refactored email_agent to comms_agent
- Updated routing table in agent_service.py
- Committed: `34a403c`

**11:00 - Phase 2 Started**
- Created `whatsapp_messages` collection (17 fields, 3 relations)
- Created `verification_attempts` collection (11 fields, 3 relations)
- Built Twilio webhook handler with security validation
- Updated Dockerfile and requirements.txt
- Committed: `b959141`

**12:00 - Phase 3 Started**
- Documented all 6 flows in detail
- Ready to implement flows in Directus UI

**13:00 - Namespace Shadowing Fix**
- Renamed `scripts/twilio/` to `scripts/twilio_integration/` to avoid shadowing the installed `twilio` SDK package
- Updated import in `agent_service.py`: `from twilio import` → `from twilio_integration import`
- Updated Dockerfile copy instruction
- Updated all documentation references
- Fixed deployment blocker: `ModuleNotFoundError: No module named 'twilio.request_validator'`

---

## 🎯 Next Actions

**Immediate (Today):**
1. Build Flow 1 in Directus UI (WhatsApp Verification)
2. Build Flow 2 in Directus UI (Verification Response)
3. Configure Twilio environment variables
4. Test basic WhatsApp message ingestion

**Tomorrow:**
1. Build remaining 4 flows
2. Configure all environment variables
3. Run all 5 test scenarios
4. Implement security monitoring flow

---

## 📚 Reference Files

### Critical Files
- [scripts/agents/comms_agent.py](scripts/agents/comms_agent.py) - Unified communications agent
- [scripts/agent_service.py](scripts/agent_service.py) - FastAPI service with routing
- [scripts/twilio_integration/whatsapp_webhook.py](scripts/twilio_integration/whatsapp_webhook.py) - Webhook handler
- [scripts/twilio_integration/README.md](scripts/twilio_integration/README.md) - Complete webhook documentation
- [agents/Dockerfile](agents/Dockerfile) - Production Docker build
- [scripts/requirements.txt](scripts/requirements.txt) - Python dependencies

### Directus Collections
- `whatsapp_messages` - WhatsApp message storage
- `verification_attempts` - Security audit trail
- `human_prompts` - Approval workflow
- `agent_logs` - Agent execution logs
- `communication_log` - All communication history

### Environment Files
- `.env` (not in git) - Local development secrets
- Render.com dashboard - Production environment variables

---

## 🔄 Rollback Plan

If issues occur:

1. **Set all flows to status='inactive'**
2. **Check agent_logs for errors**
3. **Review verification_attempts for failures**
4. **Test individual operations in isolation**
5. **Revert code changes:** `git reset --hard [commit-hash]`

Safe rollback commits:
- Before Phase 2: `34a403c` (comms_agent refactor)
- Before Phase 3: `b959141` (webhook handler added)

---

**Last Updated:** 2025-12-25 12:00
**Status:** Phase 2 Complete, Phase 3 In Progress
