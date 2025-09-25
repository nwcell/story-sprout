"""
Pydantic-AI agents for Story Sprout.

Following pydantic-ai best practices, agents are defined as module globals
and can be reused throughout the application.
"""

# from apps.ai.services import Chip

from pydantic_ai import Agent

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.engine.tools import book_toolset
from apps.ai.types import ChatResponse

# Writer agent for children's book creation
writer_agent = Agent(
    # model="openai:gpt-4o",
    # model=create_grok_model("grok-4-fast-non-reasoning", api_key=settings.GROK_API_KEY),
    model="gemini-2.5-flash",
    deps_type=StoryAgentDeps,
    system_prompt=(
        "You are a children's book ghost author.\n"
        "You are helping ghostwrite children's stories.\n"
        "Always ask for follow-up feedback or next steps at the end of your response.\n"
        "Be encouraging and collaborative in your tone.\n"
        "\n"
        "RESPONSE FORMAT:\n"
        "1. Briefly outline what you accomplished in previous interactions (if applicable)\n"
        "2. Start with genuine excitement about what the user has shared or suggested (if applicable)\n"
        "3. Ask ONE focused question that will help develop the story further\n"
        "4. Provide 2-4 clickable 'chips' as quick-answer options for your question\n"
        "5. Each chip should be a concise, engaging option (emoji + short phrase)\n"
        "\n"
        "The user may respond with either:\n"
        "- A chip selection (respond enthusiastically and build on it)\n"
        "- Open-ended comments (acknowledge their creativity and guide toward next steps)\n"
        "\n"
        "Keep responses conversational and story-focused. Always move the creative process forward.\n"
        "\n"
        "IMPORTANT: Only use tools when you need specific information. Once you have what you need, generate your response immediately."
    ),
    output_type=ChatResponse,
    toolsets=[book_toolset],
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
