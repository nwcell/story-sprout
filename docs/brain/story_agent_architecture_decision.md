# Story Agent Architecture Decision

## Decision: Django-Hosted MCP Server

**Approach**: Extend existing django-mcp-server setup for story manipulation
**Rationale**: Industry standard protocol + direct ORM access + minimal architectural changes

## Key Benefits
- **Performance**: Direct database access, shared auth context
- **Future-proof**: MCP rapidly adopted by OpenAI, Google, Microsoft
- **Existing foundation**: django-mcp-server already installed and configured
- **Coexistence**: Keep Django Ninja API, add DRF for MCP (no migration needed)

## Implementation Path
1. Configure django-mcp-server in Django settings
2. Implement comprehensive story/page MCP tools
3. Integrate MCP toolset with pydantic-ai agent
4. Test and deploy story manipulation capabilities

See `mcp_implementation_plan.md` for detailed implementation strategy.