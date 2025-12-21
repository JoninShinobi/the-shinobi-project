"""
Email Agent
Handles inbound email processing and response drafting.

Key behaviors:
- NEVER sends emails directly
- Creates drafts in service_workflows for human approval
- Logs all activity to agent_logs
"""

import json
from typing import Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentResult


class EmailAgent(BaseAgent):
    """
    Agent for handling email-related automation.
    All email sends require human approval.
    """

    def __init__(self):
        super().__init__(
            name="email_agent",
            description="Handles inbound emails and drafts responses"
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Email Agent, an AI assistant for a web design agency.

## Your Capabilities
- Read emails from the emails collection
- Analyze email content, sentiment, and intent
- Draft professional responses
- Create workflow items for human approval

## Your Constraints
- NEVER send emails directly using Gmail MCP send functions
- ALWAYS create drafts that require human approval
- Log all your actions to agent_logs collection

## Your Process
1. Read the email context provided
2. Analyze the sender, subject, and content
3. Determine the appropriate response type:
   - inquiry → draft informative response
   - complaint → draft empathetic response, escalate if needed
   - request → draft acknowledgment with next steps
   - spam → mark as spam, no response needed
4. Create a draft in service_workflows with:
   - status: 'pending_approval'
   - workflow_type: 'email_response'
   - related_email_id: the original email ID
   - draft_content: the response you've written
   - notes: your reasoning for the response
5. Log your action to agent_logs

## Response Style
- Professional but friendly
- Acknowledge the sender's query clearly
- Provide helpful next steps when appropriate
- Sign off as "The Shinobi Team"

## Available MCP Tools
- mcp__directus__items: Read/write Directus collections
- mcp__directus__schema: Check collection structure
- mcp__google-workspace__get_gmail_message_content: Read email details
"""

    def build_task_prompt(self, context: dict) -> str:
        """Build prompt for email processing task"""

        email_id = context.get("item_id", "unknown")
        event_type = context.get("event", "items.create")
        email_data = context.get("payload", {})

        prompt = f"""## Email Processing Task

### Event Details
- Event Type: {event_type}
- Email ID: {email_id}
- Timestamp: {datetime.utcnow().isoformat()}

### Email Data
{json.dumps(email_data, indent=2)}

### Instructions
1. First, use mcp__directus__items to read the full email record:
   ```
   action: read
   collection: emails
   query:
     filter:
       id:
         _eq: "{email_id}"
   ```

2. Analyze the email and determine appropriate response

3. Create a workflow item for the draft response:
   ```
   action: create
   collection: service_workflows
   data:
     status: pending_approval
     workflow_type: email_response
     title: "Response to: [subject]"
     description: [your draft response]
     related_collection: emails
     related_item_id: "{email_id}"
     metadata:
       original_subject: [subject]
       original_sender: [sender]
       response_reasoning: [why you chose this response]
   ```

4. Log your action:
   ```
   action: create
   collection: agent_logs
   data:
     agent_type: email
     action: draft_response
     collection: emails
     item_id: "{email_id}"
     status: completed
     result: "Created draft response for approval"
   ```

Process this email now.
"""
        return prompt

    async def execute(self, task_id: str, context: dict) -> AgentResult:
        """Execute email processing with approval workflow"""

        self.log(f"Processing email task: {task_id}")

        # Build and execute prompt
        prompt = self.build_task_prompt({
            "item_id": task_id,
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
                action_taken="process_email",
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
async def process_email(email_id: str, email_data: dict) -> AgentResult:
    """Process a single email"""
    agent = EmailAgent()
    return await agent.execute(email_id, email_data)
