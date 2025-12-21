"""
Shinobi C2 Agent Modules
Specialized AI agents for business automation powered by Claude SDK.
"""

from .base_agent import BaseAgent, AgentConfig, AgentResult
from .email_agent import EmailAgent
from .orchestrator_agent import OrchestratorAgent, Department, TaskClassification
from .marketing_agent import MarketingAgent
from .finance_agent import FinanceAgent
from .client_services_agent import ClientServicesAgent

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
    # Core
    "OrchestratorAgent",
    "Department",
    "TaskClassification",
    # Specialized Agents
    "EmailAgent",
    "MarketingAgent",
    "FinanceAgent",
    "ClientServicesAgent",
]
