"""
Base Agent Class - Claude SDK Version
Foundation for all Shinobi agents with Claude API integration.
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any, List, Dict
from dataclasses import dataclass, field
import anthropic


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    agent_name: str
    task_id: str
    action_taken: str
    result_data: Optional[dict] = None
    error: Optional[str] = None
    requires_approval: bool = False
    approval_item_id: Optional[str] = None
    tokens_used: Optional[dict] = None


@dataclass
class AgentConfig:
    """Configuration for agent behavior"""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 120
    enable_tools: bool = True
    allowed_collections: List[str] = field(default_factory=list)
    allowed_uuids: set = field(default_factory=set)


class BaseAgent(ABC):
    """
    Base class for all Shinobi agents.
    Uses Claude SDK for direct API invocation with tool support.
    """

    def __init__(self, name: str, description: str, config: Optional[AgentConfig] = None):
        self.name = name
        self.description = description
        self.config = config or AgentConfig()
        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self._client: Optional[anthropic.Anthropic] = None
        self._async_client: Optional[anthropic.AsyncAnthropic] = None

    @property
    def client(self) -> anthropic.Anthropic:
        """Lazy-load synchronous client"""
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    @property
    def async_client(self) -> anthropic.AsyncAnthropic:
        """Lazy-load async client"""
        if self._async_client is None:
            self._async_client = anthropic.AsyncAnthropic()
        return self._async_client

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    @abstractmethod
    def build_task_prompt(self, context: dict) -> str:
        """Build the task-specific prompt from context"""
        pass

    def get_tools(self) -> List[Dict]:
        """
        Return tool definitions for this agent.
        Override in subclasses to define agent-specific tools.
        """
        return []

    def invoke_claude_sync(self, prompt: str, timeout: int = None) -> tuple[bool, str, dict]:
        """
        Invoke Claude API synchronously.
        Returns (success, output/error, token_usage)
        """
        timeout = timeout or self.config.timeout

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "system": self.system_prompt,
                "messages": messages,
            }

            if self.config.enable_tools and self.get_tools():
                kwargs["tools"] = self.get_tools()

            response = self.client.messages.create(**kwargs)

            output_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output_text += block.text

            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            return True, output_text, token_usage

        except anthropic.APITimeoutError:
            return False, f"Timeout after {timeout} seconds", {}
        except anthropic.APIConnectionError as e:
            return False, f"Connection error: {str(e)}", {}
        except anthropic.RateLimitError as e:
            return False, f"Rate limit exceeded: {str(e)}", {}
        except anthropic.APIStatusError as e:
            return False, f"API error: {str(e)}", {}
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", {}

    async def invoke_claude(self, prompt: str, timeout: int = None) -> tuple[bool, str, dict]:
        """
        Invoke Claude API asynchronously.
        Returns (success, output/error, token_usage)
        """
        timeout = timeout or self.config.timeout

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "system": self.system_prompt,
                "messages": messages,
            }

            if self.config.enable_tools and self.get_tools():
                kwargs["tools"] = self.get_tools()

            response = await asyncio.wait_for(
                self.async_client.messages.create(**kwargs),
                timeout=timeout
            )

            output_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output_text += block.text

            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            return True, output_text, token_usage

        except asyncio.TimeoutError:
            return False, f"Timeout after {timeout} seconds", {}
        except anthropic.APIConnectionError as e:
            return False, f"Connection error: {str(e)}", {}
        except anthropic.RateLimitError as e:
            return False, f"Rate limit exceeded: {str(e)}", {}
        except anthropic.APIStatusError as e:
            return False, f"API error: {str(e)}", {}
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", {}

    async def invoke_with_tools(self, prompt: str, max_turns: int = 10) -> tuple[bool, str, dict]:
        """
        Invoke Claude with tool use, handling multi-turn tool calls.
        Returns (success, final_output, token_usage)
        """
        messages = [{"role": "user", "content": prompt}]
        total_tokens = {"input_tokens": 0, "output_tokens": 0}

        for turn in range(max_turns):
            try:
                kwargs = {
                    "model": self.config.model,
                    "max_tokens": self.config.max_tokens,
                    "system": self.system_prompt,
                    "messages": messages,
                }

                if self.config.enable_tools and self.get_tools():
                    kwargs["tools"] = self.get_tools()

                response = await self.async_client.messages.create(**kwargs)

                total_tokens["input_tokens"] += response.usage.input_tokens
                total_tokens["output_tokens"] += response.usage.output_tokens

                if response.stop_reason == "end_turn":
                    output_text = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            output_text += block.text
                    return True, output_text, total_tokens

                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = await self.handle_tool_call(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result) if isinstance(result, dict) else str(result)
                            })

                    messages.append({"role": "user", "content": tool_results})
                    continue

                output_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        output_text += block.text
                return True, output_text, total_tokens

            except Exception as e:
                return False, f"Error during tool execution: {str(e)}", total_tokens

        return False, f"Exceeded maximum turns ({max_turns})", total_tokens

    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """
        Handle a tool call. Override in subclasses for custom tool handling.
        Default implementation logs the call and returns an error.
        """
        self.log(f"Tool call: {tool_name} with input: {json.dumps(tool_input)}")
        return {"error": f"Tool {tool_name} not implemented in {self.name}"}

    async def execute(self, task_id: str, context: dict) -> AgentResult:
        """
        Execute the agent task.
        Override in subclasses for custom behavior.
        """
        prompt = self.build_task_prompt(context)

        if self.config.enable_tools and self.get_tools():
            success, output, tokens = await self.invoke_with_tools(prompt)
        else:
            success, output, tokens = await self.invoke_claude(prompt)

        return AgentResult(
            success=success,
            agent_name=self.name,
            task_id=task_id,
            action_taken="claude_api_invocation",
            result_data={"output": output} if success else None,
            error=output if not success else None,
            tokens_used=tokens
        )

    def log(self, message: str):
        """Log with military time timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.name}] {message}")

    def validate_uuid_access(self, uuid: str) -> bool:
        """Check if the agent has access to this UUID"""
        if not self.config.allowed_uuids:
            return True
        return uuid in self.config.allowed_uuids

    def validate_collection_access(self, collection: str) -> bool:
        """Check if the agent has access to this collection"""
        if not self.config.allowed_collections:
            return True
        return collection in self.config.allowed_collections
