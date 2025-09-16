# Django-Hosted MCP Implementation Plan

## Executive Summary

**Decision**: Django-hosted MCP server for story manipulation
**Rationale**: Direct ORM access, shared auth context, reduced complexity, optimal performance

## Architecture Overview

```
Agent (pydantic-ai) → MCP Client → Django MCP Server → Django ORM → Database
```

### Key Benefits
- **Performance**: Direct database access, no API overhead
- **Consistency**: Shared transaction context and authentication
- **Simplicity**: Single service deployment, unified error handling
- **Future-proof**: Industry-standard MCP protocol

## Current State Analysis

### ✅ Already Configured
- `django-mcp-server>=0.5.6` installed
- URL routing: `path("mcp/", include("mcp_server.urls"))`
- Basic `StoryTool(ModelQueryToolset)` started
- ASGI support with Daphne

### ❌ Missing Implementation
- `mcp_server` not in `INSTALLED_APPS`
- Story manipulation tools not implemented
- Agent integration with MCP toolset
- Comprehensive story/page operations

## Implementation Architecture

### Phase 1: Class-Based API Refactor

**Current Issue**: Function-based views in `src/apps/stories/api.py` lack organization
**Solution**: Refactor to class-based ViewSets for better maintainability

```python
# apps/stories/api.py - Class-Based Implementation
class StoryViewSet(ViewSet):
    """Single class handling all story operations"""
    def list(self, request) -> List[StoryOut]           # GET /stories/
    def create(self, request, payload: StoryIn) -> StoryOut   # POST /stories/
    def retrieve(self, request, story_uuid: UUID) -> StoryOut # GET /stories/{uuid}
    def update(self, request, story_uuid: UUID, payload: StoryIn) -> StoryOut # PATCH /stories/{uuid}
    def destroy(self, request, story_uuid: UUID)        # DELETE /stories/{uuid}

class PageViewSet(ViewSet):
    """Single class handling all page operations with nested routing"""
    def list(self, request, story_uuid: UUID) -> List[PageOut]  # GET /stories/{uuid}/pages/
    def create(self, request, story_uuid: UUID, payload: PageIn) -> PageOut # POST /stories/{uuid}/pages/
    # ... full CRUD + specialized endpoints
```

### Phase 2: MCP Integration (API-First Approach)

```python
# apps/stories/mcp.py - MCP Toolset calling Class-Based API
class StoryMCPToolset(MCPToolset):
    """AI agent tools that call the class-based API internally"""

    # Story Operations (call StoryViewSet methods)
    async def get_story_by_id(self, story_uuid: str) -> dict
    async def create_story(self, title: str, description: str = "") -> dict
    async def update_story(self, story_uuid: str, **kwargs) -> dict
    async def delete_story(self, story_uuid: str) -> dict
    async def list_user_stories(self, limit: int = 10) -> list

    # Page Operations (call PageViewSet methods)
    async def get_page(self, story_uuid: str, page_uuid: str) -> dict
    async def create_page(self, story_uuid: str, content: str = "", image_text: str = "") -> dict
    async def update_page_content(self, story_uuid: str, page_uuid: str, content: str) -> dict
    async def delete_page(self, story_uuid: str, page_uuid: str) -> dict
    async def move_page_up(self, story_uuid: str, page_uuid: str) -> dict
    async def move_page_down(self, story_uuid: str, page_uuid: str) -> dict

    # Advanced Operations
    async def get_story_outline(self, story_uuid: str) -> dict
    async def get_page_by_number(self, story_uuid: str, page_number: int) -> dict
```

### Agent Integration

```python
# apps/ai/agents.py - Enhanced with MCP
from pydantic_ai.toolsets import MCPToolset

# Configure MCP client to connect to Django MCP server
mcp_toolset = MCPToolset(
    server_url="http://localhost:8000/mcp/",
    server_name="story_operations"
)

writer_agent = Agent(
    model="openai:gpt-4o",
    deps_type=AgentDependencies,
    system_prompt="""You are a children's book ghost author with access to story manipulation tools.
    You can create, read, update, and delete stories and pages.
    Always maintain story coherence and age-appropriate content.""",
    toolsets=[mcp_toolset]  # Use MCP instead of direct tools
)
```

## Task Implementation Plan

### Phase 1: Foundation Setup
1. **Configure Django MCP Server**
   - Add `mcp_server` to `INSTALLED_APPS`
   - Verify URL routing and ASGI configuration
   - Test basic MCP endpoint accessibility

2. **Implement Core Story Tools**
   - Extend `StoryMCPToolset` with essential operations
   - Add proper error handling and validation
   - Implement user authorization checks

### Phase 2: Story Operations
3. **Story CRUD Operations**
   - `get_story_by_id`, `create_story`, `update_story`, `delete_story`
   - `list_user_stories` with pagination
   - User-scoped queries with proper authorization

4. **Page CRUD Operations**
   - `get_page`, `add_page`, `update_page_content`, `delete_page`
   - `update_page_image_text` for AI image generation
   - `reorder_pages` for story structure changes

### Phase 3: Advanced Features
5. **Navigation and Structure Tools**
   - `get_story_outline` for story overview
   - `get_next_page`, `get_previous_page` navigation
   - Story structure analysis tools

6. **Agent Integration**
   - Configure pydantic-ai agent with MCP toolset
   - Replace existing tool stubs with MCP calls
   - Test agent story manipulation capabilities

### Phase 4: Testing and Optimization
7. **Comprehensive Testing**
   - Unit tests for each MCP tool
   - Integration tests with agent system
   - Performance testing and optimization

8. **Documentation and Deployment**
   - API documentation for MCP endpoints
   - Deployment configuration updates
   - Monitoring and logging setup

## Quality Assurance Framework

### Testing Strategy
- **Unit Tests**: Each MCP tool in isolation
- **Integration Tests**: Agent + MCP + Database
- **End-to-End Tests**: Full conversation workflows
- **Performance Tests**: Response time and throughput

### Code Quality Standards
- Type hints for all function signatures
- Comprehensive docstrings
- Error handling with proper HTTP status codes
- Async/await best practices
- Database transaction management

## Next Steps

1. Begin with Phase 1: Foundation Setup
2. Iterative development with testing at each step
3. Regular integration testing with existing agent system
4. Performance monitoring and optimization
5. Documentation and deployment preparation

This plan provides a structured approach to implementing Django-hosted MCP for story manipulation while maintaining system reliability and performance.
