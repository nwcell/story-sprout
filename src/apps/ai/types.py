"""
Common types for AI agents.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AgentDependencies:
    """Dependencies injected into all agents."""

    conversation_uuid: UUID
