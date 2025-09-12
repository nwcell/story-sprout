# Story Sprout MCP Server

A FastMCP server that provides Model Context Protocol tools and resources for the Story Sprout platform.

## Features

- **Story Management**: Create and manage stories through MCP tools
- **Statistics**: Get story and platform statistics
- **Configuration**: Access server configuration and health status
- **Resources**: Provide story configuration and health endpoints

## Development

### Setup

```bash
# From the root of the story-sprout project
cd services/mcp
uv sync
```

### Running the Server

```bash
# Development mode
uv run server.py

# Or with custom host/port
MCP_HOST=0.0.0.0 MCP_PORT=8081 uv run server.py
```

### Available Tools

- `create_story`: Create a new story with title, content, and user_id
- `get_story_stats`: Get statistics about stories in the system

### Available Resources

- `story://config`: Get server configuration information
- `story://health`: Get server health status

## Configuration

Environment variables:

- `MCP_HOST`: Server host (default: 127.0.0.1)
- `MCP_PORT`: Server port (default: 8080)
- `ENVIRONMENT`: Environment name (default: development)

## Testing

```bash
uv run python -m pytest
```
