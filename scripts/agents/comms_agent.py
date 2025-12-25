"""
Communications Agent
Handles all inbound/outbound communications across multiple channels (email, WhatsApp, SMS).

Key behaviors:
- NEVER sends messages directly
- Creates drafts in service_workflows for human approval
- Logs all activity to agent_logs
- Channel-agnostic processing
"""

import json
from typing import Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentResult


class CommsAgent(BaseAgent):
    """
    Agent for handling all communications across multiple channels.
    All outbound messages require human approval.
    """

    def __init__(self):
        super().__init__(
            name="comms_agent",
            description="Handles inbound communications and drafts responses across all channels"
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Communications Agent, an AI assistant for a web design agency.

## Your Capabilities
- Read communications from multiple collections (emails, whatsapp_messages, sms_messages)
- Analyze message content, sentiment, and intent
- Draft professional responses appropriate for the channel
- Create workflow items for human approval

## Your Constraints
- NEVER send messages directly (no Gmail send, no Twilio send, etc.)
- ALWAYS create drafts that require human approval
- Log all your actions to agent_logs collection

## Your Process
1. Read the communication context provided (identify channel from collection)
2. Analyze the sender, subject/content, and channel
3. Determine the appropriate response type:
   - inquiry → draft informative response
   - complaint → draft empathetic response, escalate if needed
   - request → draft acknowledgment with next steps
   - spam → mark as spam, no response needed
4. Create a draft in service_workflows with:
   - status: 'pending_approval'
   - workflow_type: '[channel]_response' (email_response, whatsapp_response, sms_response)
   - related_collection: the source collection
   - related_item_id: the original message ID
   - draft_content: the response you've written
   - notes: your reasoning for the response
   - metadata: channel-specific data (to_number for WhatsApp/SMS, to_email for email)
5. Log your action to agent_logs

## Response Style by Channel
### Email:
- Professional but friendly
- Clear subject lines
- Proper formatting with paragraphs
- Sign off as "The Shinobi Team"

### WhatsApp/SMS:
- Concise and direct
- Friendly, conversational tone
- Use line breaks sparingly
- No formal sign-off needed
- Emoji acceptable if appropriate to context

## Available MCP Tools
- mcp__directus__items: Read/write Directus collections
- mcp__directus__schema: Check collection structure
- mcp__google-workspace__get_gmail_message_content: Read email details (read-only)
"""

    def build_task_prompt(self, context: dict) -> str:
        """Build prompt for communication processing task"""

        item_id = context.get("item_id", "unknown")
        collection = context.get("collection", "unknown")
        event_type = context.get("event", "items.create")
        message_data = context.get("payload", {})

        # Determine channel
        channel_map = {
            "emails": "email",
            "whatsapp_messages": "whatsapp",
            "sms_messages": "sms"
        }
        channel = channel_map.get(collection, "unknown")

        prompt = f"""## Communication Processing Task

### Event Details
- Event Type: {event_type}
- Channel: {channel}
- Collection: {collection}
- Message ID: {item_id}
- Timestamp: {datetime.utcnow().isoformat()}

### Message Data
{json.dumps(message_data, indent=2)}

### Instructions
1. First, use mcp__directus__items to read the full message record:
   ```
   action: read
   collection: {collection}
   query:
     filter:
       id:
         _eq: "{item_id}"
   ```

2. Analyze the message and determine appropriate response

3. Create a workflow item for the draft response:
   ```
   action: create
   collection: service_workflows
   data:
     status: pending_approval
     workflow_type: {channel}_response
     title: "Response to: [subject/sender]"
     description: [your draft response]
     related_collection: {collection}
     related_item_id: "{item_id}"
     metadata:
       original_subject: [subject if email]
       original_sender: [sender]
       to_recipient: [recipient address/number]
       channel: {channel}
       response_reasoning: [why you chose this response]
   ```

4. Log your action:
   ```
   action: create
   collection: agent_logs
   data:
     agent_type: comms
     action: draft_response
     collection: {collection}
     item_id: "{item_id}"
     status: completed
     result: "Created draft {channel} response for approval"
   ```

Process this {channel} message now.
"""
        return prompt

    async def execute(self, task_id: str, context: dict) -> AgentResult:
        """Execute communication processing with approval workflow"""

        self.log(f"Processing communication task: {task_id}")

        # Build and execute prompt
        prompt = self.build_task_prompt({
            "item_id": task_id,
            "collection": context.get("collection", "emails"),
            "event": context.get("trigger_event", "items.create"),
            "payload": context
        })

        success, output = self.invoke_claude(prompt)

        if not success:
            self.log(f"Failed: {output}")
            return AgentResult(
                success=False,
                agent_name=self.name,
                task_id=task_id,
                action_taken="process_communication",
                error=output
            )

        self.log(f"Completed: Draft created for approval")

        return AgentResult(
            success=True,
            agent_name=self.name,
            task_id=task_id,
            action_taken="draft_response",
            result_data={"output": output},
            requires_approval=True,
            approval_item_id=task_id
        )


# Convenience function for direct invocation
async def process_communication(message_id: str, message_data: dict) -> AgentResult:
    """Process a single communication message"""
    agent = CommsAgent()
    return await agent.execute(message_id, message_data)
