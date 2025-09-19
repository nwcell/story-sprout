"""
Pydantic-AI agents for Story Sprout.

Following pydantic-ai best practices, agents are defined as module globals
and can be reused throughout the application.
"""

from pydantic_ai import Agent

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.engine.tools import book_toolset, image_toolset

# Writer agent for children's book creation
writer_agent = Agent(
    model="openai:gpt-4o",
    deps_type=StoryAgentDeps,
    system_prompt=(
        "You are a children's book ghost author.\n"
        "You are helping ghostwrite children's stories.\n"
        "Always ask for follow-up feedback or next steps at the end of your response.\n"
        "Be encouraging and collaborative in your tone."
    ),
    toolsets=[book_toolset, image_toolset],
)

# Registry for accessing agents by name (type-safe)
AGENTS: dict[str, Agent[StoryAgentDeps, str]] = {
    "writer": writer_agent,
}


def get_agent(agent_type: str) -> Agent[StoryAgentDeps, str]:
    """Get an agent by type name."""
    if agent_type not in AGENTS:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AGENTS.keys())}")
    return AGENTS[agent_type]


def list_agent_types() -> list[str]:
    """List all available agent types."""
    return list(AGENTS.keys())
