"""FastMCP Server for Story Sprout.

This server provides MCP tools and resources for the Story Sprout platform.
"""

import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Story Sprout MCP Server")


class StoryRequest(BaseModel):
    """Request model for story operations."""

    title: str
    content: str | None = None
    user_id: str | None = None


class StoryResponse(BaseModel):
    """Response model for story operations."""

    id: str
    title: str
    content: str
    status: str


@mcp.tool()
def create_story(request: StoryRequest) -> StoryResponse:
    """Create a new story.

    Args:
        request: Story creation request containing title, content, and user_id

    Returns:
        StoryResponse with the created story details
    """
    # TODO: Integrate with actual Story Sprout story creation logic
    story_id = f"story_{hash(request.title) % 10000:04d}"

    return StoryResponse(id=story_id, title=request.title, content=request.content or "", status="draft")


@mcp.tool()
def get_story_stats() -> dict[str, Any]:
    """Get statistics about stories in the system.

    Returns:
        Dictionary containing story statistics
    """
    # TODO: Integrate with actual Story Sprout database
    return {
        "total_stories": 42,
        "published_stories": 15,
        "draft_stories": 27,
        "total_words": 125000,
        "active_writers": 8,
    }


@mcp.resource("story://config")
def get_story_config() -> str:
    """Get Story Sprout configuration information.

    Returns:
        Configuration details as a string
    """
    config = {
        "server_name": "Story Sprout MCP Server",
        "version": "0.2.0",
        "features": ["Story creation", "Story statistics", "Configuration management"],
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

    return f"Story Sprout MCP Server Configuration:\n{config}"


@mcp.resource("story://health")
def get_health_status() -> str:
    """Get server health status.

    Returns:
        Health status information
    """
    return "Story Sprout MCP Server is healthy and running!"


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("MCP_PORT", "8080"))
    host = os.getenv("MCP_HOST", "127.0.0.1")

    print(f"Starting Story Sprout MCP Server on {host}:{port}")
    uvicorn.run(mcp, host=host, port=port, log_level="info")
