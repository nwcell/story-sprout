# Django MCP Implementation Tasks

## Task Management Rules

### Working with Checkboxes
- ✅ **Completed**: `- [x] Task description`
- ⏳ **In Progress**: `- [ ] Task description _**(⏳ In Progress)**_`
- 📋 **Pending**: `- [ ] Task description`
- 🔍 **Review Needed**: `- [ ] Task description _**(🔍 Review)**_`
- ⚠️ **Blocked**: `- [ ] Task description _**(⚠️ Blocked: reason)**_`
- 🧪 **Testing**: `- [ ] Task description _**(🧪 Testing)**_`

### Implementation Guidelines
1. **Work on 3-5 tasks maximum at any time** to maintain focus
2. **Mark tasks as _**(⏳ In Progress)**_ when starting work**
3. **Complete tasks fully before moving to next phase**
4. **Use nesting for subtasks and dependencies**
5. **Add _**(🔍 Review)**_ tag when task needs verification**
6. **Include specific file paths and line numbers for clarity**

---

## Phase 1: Foundation Setup

### Django MCP Server Configuration
- [ ] Add `mcp_server` to `INSTALLED_APPS` in `src/config/settings/base.py`
- [ ] Add `rest_framework` to `INSTALLED_APPS` (MCP dependency)
- [ ] Verify MCP URL routing in `src/config/urls.py`
- [ ] Test basic MCP endpoint accessibility at `/mcp/`
  - [ ] Test with curl/browser access
  - [ ] Verify proper JSON-RPC response format
  - [ ] Check authentication requirements

### Basic MCP Tool Setup
- [ ] Extend `StoryTool` class in `src/apps/stories/mcp.py`
- [ ] Implement basic tool discovery endpoint
- [ ] Add proper error handling and logging
- [ ] Test tool registration and discovery

---

## Phase 2: Django Class-Based API Refactor

### Refactor Stories API to Class-Based Views
- [ ] Create `StoryViewSet` class in `src/apps/stories/api.py` _**(🔍 Review)**_
  - [ ] Replace function-based story endpoints with single class
  - [ ] Implement `list()`, `create()`, `retrieve()`, `update()`, `destroy()` methods
  - [ ] Maintain existing JSON and HTMX response logic
  - [ ] Add proper user authorization and filtering

- [ ] Create `PageViewSet` class in `src/apps/stories/api.py`
  - [ ] Replace function-based page endpoints with single class
  - [ ] Implement full CRUD operations with nested routing
  - [ ] Handle page ordering operations (`move_up`, `move_down`)
  - [ ] Implement image upload/delete functionality
  - [ ] Add special endpoints for content/image_text field access

### Enhanced API Features (Based on Current Implementation)
- [ ] Ensure full JSON API compatibility (remove HTMX-only logic)
  - [ ] Story endpoints: `GET /stories/`, `POST /stories/`, `GET /stories/{uuid}`, `PATCH /stories/{uuid}`, `DELETE /stories/{uuid}`
  - [ ] Page endpoints: `GET /stories/{uuid}/pages/`, `POST /stories/{uuid}/pages/`, `GET /stories/{uuid}/pages/{uuid}`, etc.
  - [ ] Special endpoints: `/stories/{uuid}/pages/{uuid}/move/up`, `/stories/{uuid}/pages/{uuid}/image`

## Phase 2B: Core MCP Story Tools

### Story CRUD Tools (MCP Implementation)
- [ ] Implement `StoryMCPToolset` class in `src/apps/stories/mcp.py`
  - [ ] `get_story_by_id(story_uuid: str) -> dict` - calls API endpoint
  - [ ] `create_story(title: str, description: str = "") -> dict` - calls API endpoint
  - [ ] `update_story(story_uuid: str, **kwargs) -> dict` - calls API endpoint
  - [ ] `delete_story(story_uuid: str) -> dict` - calls API endpoint
  - [ ] `list_user_stories(limit: int = 10, offset: int = 0) -> list` - calls API endpoint

### Story Operation Testing
- [ ] Unit tests for each story CRUD operation
  - [ ] Test authorization enforcement
  - [ ] Test error handling
  - [ ] Test data validation
  - [ ] Test transaction rollback

---

## Phase 3: MCP Page Operations

### Page CRUD Tools (MCP Implementation)
- [ ] Extend `StoryMCPToolset` with page operations in `src/apps/stories/mcp.py`
  - [ ] `get_page(story_uuid: str, page_uuid: str) -> dict` - calls API endpoint
  - [ ] `list_pages(story_uuid: str) -> list` - calls API endpoint
  - [ ] `create_page(story_uuid: str, content: str = "", image_text: str = "") -> dict` - calls API endpoint
  - [ ] `update_page_content(story_uuid: str, page_uuid: str, content: str) -> dict` - calls API endpoint
  - [ ] `update_page_image_text(story_uuid: str, page_uuid: str, image_text: str) -> dict` - calls API endpoint
  - [ ] `delete_page(story_uuid: str, page_uuid: str) -> dict` - calls API endpoint
  - [ ] `move_page_up(story_uuid: str, page_uuid: str) -> dict` - calls API endpoint
  - [ ] `move_page_down(story_uuid: str, page_uuid: str) -> dict` - calls API endpoint

### Advanced Page Operations
- [ ] Add specialized MCP tools for page management
  - [ ] `get_page_by_number(story_uuid: str, page_number: int) -> dict`
  - [ ] `get_story_outline(story_uuid: str) -> dict` - returns story with all pages summary
  - [ ] `insert_page_at_position(story_uuid: str, position: int, content: str = "") -> dict`
  - [ ] `duplicate_page(story_uuid: str, page_uuid: str) -> dict`

### Page Operation Testing
- [ ] Unit tests for page CRUD operations
  - [ ] Test page ordering logic
  - [ ] Test cascade operations
  - [ ] Test permission validation
  - [ ] Test transaction handling

---

## Phase 4: Navigation & Structure Tools

### Navigation Tools
- [ ] Implement `get_story_outline(story_uuid: str) -> dict`
  - [ ] Return story metadata
  - [ ] Include all pages with summaries
  - [ ] Show page order and numbers
  - [ ] Include content snippets

- [ ] Implement `get_next_page(page_uuid: str) -> dict`
  - [ ] Find next page in story order
  - [ ] Handle last page case
  - [ ] Return page data or null

- [ ] Implement `get_previous_page(page_uuid: str) -> dict`
  - [ ] Find previous page in story order
  - [ ] Handle first page case
  - [ ] Return page data or null

### Advanced Story Tools
- [ ] Implement `get_page_count(story_uuid: str) -> int`
- [ ] Implement `search_story_content(story_uuid: str, query: str) -> list`
- [ ] Implement `duplicate_story(story_uuid: str, new_title: str) -> dict`
- [ ] Implement `export_story_data(story_uuid: str, format: str = "json") -> dict`

---

## Phase 5: Agent Integration

### MCP Client Setup
- [ ] Research MCP client integration for pydantic-ai
- [ ] Configure MCP toolset in `src/apps/ai/agents.py`
- [ ] Update `writer_agent` to use MCP tools instead of direct tools
- [ ] Test MCP client connection to Django server

### Agent Tool Integration
- [ ] Replace tool stubs in `src/apps/ai/tools.py` with MCP calls
  - [ ] Update `get_story()` to use MCP
  - [ ] Update `get_page()` to use MCP
  - [ ] Remove direct database access from tools
  - [ ] Add MCP error handling

- [ ] Update agent system prompt in `src/apps/ai/agents.py`
  - [ ] Include story manipulation capabilities
  - [ ] Add guidance for tool usage
  - [ ] Specify output formats

### Agent Dependency Updates
- [ ] Update `AgentDependencies` in `src/apps/ai/types.py`
  - [ ] Add MCP client configuration
  - [ ] Include user context for MCP calls
  - [ ] Add story context tracking

---

## Phase 6: Testing & Integration

### End-to-End Testing
- [ ] Test complete agent conversation workflow
  - [ ] Agent creates new story
  - [ ] Agent adds pages with content
  - [ ] Agent modifies existing story
  - [ ] Agent navigates story structure

- [ ] Test error scenarios
  - [ ] Invalid story UUID
  - [ ] Permission denied cases
  - [ ] Network connectivity issues
  - [ ] Malformed MCP requests

### Performance Testing
- [ ] Measure MCP call latency
- [ ] Test concurrent agent requests
- [ ] Monitor database query efficiency
- [ ] Profile memory usage

### Integration Testing
- [ ] Test with existing Celery task system
- [ ] Verify SSE streaming still works
- [ ] Test with existing Ninja API endpoints
- [ ] Confirm no regression in current functionality

---

## Phase 7: Documentation & Deployment

### Documentation
- [ ] Document MCP endpoints in API docs
- [ ] Create agent usage examples
- [ ] Update development setup instructions
- [ ] Add troubleshooting guide

### Production Readiness
- [ ] Add monitoring and logging
- [ ] Configure production MCP settings
- [ ] Test deployment process
- [ ] Create rollback plan

### Code Quality
- [ ] Run full test suite
- [ ] Check type safety with mypy
- [ ] Run linting with ruff
- [ ] Code review and approval

---

## Success Criteria

### Functional Requirements
- ✅ Agent can create, read, update, delete stories
- ✅ Agent can manipulate page content and ordering
- ✅ All operations respect user permissions
- ✅ MCP tools integrate seamlessly with pydantic-ai
- ✅ No regression in existing functionality

### Non-Functional Requirements
- ✅ MCP calls complete within 500ms
- ✅ All database operations use transactions
- ✅ Comprehensive error handling and logging
- ✅ Type safety maintained throughout
- ✅ Test coverage above 90%

---

## Notes

- **Focus Area**: Work on one phase at a time, completing all tasks before moving forward
- **Testing Strategy**: Test each tool individually before integration
- **Error Handling**: Every MCP tool should handle errors gracefully
- **Performance**: Monitor database queries and optimize as needed
- **Documentation**: Keep inline documentation updated as code evolves