"""
Marketing Agent
Handles marketing campaigns, content creation, social media, and lead nurturing.
Integrates with Figma MCP for draft creation.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentConfig, AgentResult


class MarketingAgent(BaseAgent):
    """
    Marketing department agent responsible for:
    1. Campaign creation and management
    2. Content calendar management
    3. Social media post drafting
    4. Lead nurturing sequences
    5. Marketing material design (via Figma MCP)
    6. Performance analytics
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="MarketingAgent",
            description="Handles all marketing operations including campaigns, content, and design",
            config=config or AgentConfig(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                enable_tools=True,
                allowed_collections=[
                    "leads", "clients", "projects",
                    "communication_log", "documents"
                ]
            )
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Marketing Agent, responsible for all marketing operations.

## Your Responsibilities
1. Campaign Management: Plan, create, and track marketing campaigns
2. Content Creation: Draft social media posts, emails, blog content
3. Lead Nurturing: Design and execute lead follow-up sequences
4. Design Coordination: Create briefs for Figma designs
5. Analytics: Track and report on marketing performance

## Brand Guidelines
- Professional but approachable tone
- Focus on value proposition and outcomes
- Client-centric messaging
- Highlight expertise and quality

## Workflow Rules
1. ALL marketing content must be drafted first, never published directly
2. Campaign launches require human approval
3. Track all communications in communication_log
4. Create designs as drafts in Figma for review

## External Sites You Support
- Kerry's Art Shop: Art and creative products
- Hannah's Courses: Educational courses
- Client project sites: Various industries

## Output Format
Always provide structured output with:
- Action summary
- Content draft (if applicable)
- Next steps
- Items requiring approval

## Currency: GBP (£)"""

    def build_task_prompt(self, context: dict) -> str:
        task_type = context.get("task_type", "general_marketing")
        client_info = context.get("client", {})
        campaign_info = context.get("campaign", {})

        prompt = f"""## Marketing Task
- Type: {task_type}
- Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        if client_info:
            prompt += f"""## Client Context
{json.dumps(client_info, indent=2)}

"""

        if campaign_info:
            prompt += f"""## Campaign Context
{json.dumps(campaign_info, indent=2)}

"""

        prompt += f"""## Full Context
{json.dumps(context, indent=2)}

## Instructions
Based on the context above, execute the appropriate marketing action.
Provide your response with:
1. Analysis of what needs to be done
2. Content/action draft
3. Next steps
4. Any items requiring human approval"""

        return prompt

    def get_tools(self) -> List[Dict]:
        """Marketing-specific tools"""
        return [
            {
                "name": "create_campaign_draft",
                "description": "Create a draft marketing campaign",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_name": {"type": "string", "description": "Name of the campaign"},
                        "campaign_type": {
                            "type": "string",
                            "enum": ["email", "social", "content", "event", "multi_channel"],
                            "description": "Type of campaign"
                        },
                        "target_audience": {"type": "string", "description": "Target audience description"},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "budget_gbp": {"type": "number", "description": "Budget in GBP"},
                        "start_date": {"type": "string", "description": "Campaign start date"},
                        "end_date": {"type": "string", "description": "Campaign end date"}
                    },
                    "required": ["campaign_name", "campaign_type", "target_audience"]
                }
            },
            {
                "name": "draft_social_post",
                "description": "Draft a social media post",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "facebook", "linkedin", "twitter", "tiktok"],
                            "description": "Social media platform"
                        },
                        "post_type": {
                            "type": "string",
                            "enum": ["image", "video", "carousel", "story", "reel", "text"],
                            "description": "Type of post"
                        },
                        "content": {"type": "string", "description": "Post content/caption"},
                        "hashtags": {"type": "array", "items": {"type": "string"}},
                        "call_to_action": {"type": "string", "description": "CTA"},
                        "scheduled_time": {"type": "string", "description": "Scheduled publish time"}
                    },
                    "required": ["platform", "content"]
                }
            },
            {
                "name": "create_email_sequence",
                "description": "Create an email nurturing sequence",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sequence_name": {"type": "string", "description": "Name of the sequence"},
                        "trigger": {"type": "string", "description": "What triggers this sequence"},
                        "emails": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "subject": {"type": "string"},
                                    "body_summary": {"type": "string"},
                                    "delay_days": {"type": "integer"}
                                }
                            }
                        },
                        "target_segment": {"type": "string", "description": "Target audience segment"}
                    },
                    "required": ["sequence_name", "trigger", "emails"]
                }
            },
            {
                "name": "create_figma_design_brief",
                "description": "Create a brief for Figma design creation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "design_type": {
                            "type": "string",
                            "enum": ["social_post", "banner", "flyer", "presentation", "infographic", "ad"],
                            "description": "Type of design needed"
                        },
                        "dimensions": {
                            "type": "object",
                            "properties": {
                                "width": {"type": "integer"},
                                "height": {"type": "integer"}
                            }
                        },
                        "brand": {"type": "string", "description": "Which brand/site this is for"},
                        "headline": {"type": "string", "description": "Main headline text"},
                        "body_text": {"type": "string", "description": "Supporting body text"},
                        "call_to_action": {"type": "string", "description": "CTA button text"},
                        "style_notes": {"type": "string", "description": "Style and design notes"},
                        "images_needed": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["design_type", "brand"]
                }
            },
            {
                "name": "analyze_lead_for_nurturing",
                "description": "Analyze a lead and recommend nurturing approach",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string", "description": "Lead UUID"},
                        "lead_data": {"type": "object", "description": "Lead information"},
                        "source": {"type": "string", "description": "Where the lead came from"},
                        "interactions": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["lead_data"]
                }
            }
        ]

    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """Handle marketing-specific tool calls"""
        self.log(f"Tool: {tool_name}")

        if tool_name == "create_campaign_draft":
            return await self._create_campaign_draft(tool_input)

        elif tool_name == "draft_social_post":
            return await self._draft_social_post(tool_input)

        elif tool_name == "create_email_sequence":
            return await self._create_email_sequence(tool_input)

        elif tool_name == "create_figma_design_brief":
            return await self._create_figma_brief(tool_input)

        elif tool_name == "analyze_lead_for_nurturing":
            return await self._analyze_lead(tool_input)

        return {"error": f"Unknown tool: {tool_name}"}

    async def _create_campaign_draft(self, data: dict) -> dict:
        """Create a campaign draft in Directus"""
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": "draft",
            "requires_approval": True,
            "data": data,
            "message": f"Campaign '{data['campaign_name']}' created as draft"
        }

    async def _draft_social_post(self, data: dict) -> dict:
        """Create a social media post draft"""
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "post_id": post_id,
            "platform": data["platform"],
            "status": "draft",
            "requires_approval": True,
            "content": data["content"],
            "message": f"Social post draft created for {data['platform']}"
        }

    async def _create_email_sequence(self, data: dict) -> dict:
        """Create an email nurturing sequence"""
        sequence_id = f"sequence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "sequence_id": sequence_id,
            "status": "draft",
            "requires_approval": True,
            "email_count": len(data.get("emails", [])),
            "message": f"Email sequence '{data['sequence_name']}' created with {len(data.get('emails', []))} emails"
        }

    async def _create_figma_brief(self, data: dict) -> dict:
        """Create a Figma design brief for later execution"""
        brief_id = f"figma_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "brief_id": brief_id,
            "design_type": data["design_type"],
            "brand": data["brand"],
            "status": "pending_design",
            "requires_figma_execution": True,
            "message": f"Figma design brief created for {data['design_type']}",
            "brief_data": data
        }

    async def _analyze_lead(self, data: dict) -> dict:
        """Analyze a lead and provide nurturing recommendations"""
        lead_data = data.get("lead_data", {})
        source = data.get("source", "unknown")

        # Determine lead temperature
        interactions = data.get("interactions", [])
        interaction_count = len(interactions)

        if interaction_count == 0:
            temperature = "cold"
            recommended_sequence = "introduction"
        elif interaction_count < 3:
            temperature = "warm"
            recommended_sequence = "engagement"
        else:
            temperature = "hot"
            recommended_sequence = "conversion"

        return {
            "success": True,
            "lead_temperature": temperature,
            "recommended_sequence": recommended_sequence,
            "suggested_actions": [
                f"Add to {recommended_sequence} email sequence",
                "Schedule personalized follow-up",
                "Update CRM with analysis"
            ],
            "source_channel": source,
            "engagement_score": min(100, interaction_count * 15 + 25)
        }
