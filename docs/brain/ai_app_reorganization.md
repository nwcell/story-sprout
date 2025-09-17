# AI App Reorganization Implementation Plan

## Executive Summary

**Goal**: Reorganize the AI app to have cleaner architecture with fewer files while maintaining all existing functionality. Focus on consolidating modules and integrating pydantic-ai-stash with proper UI patterns.

**Key Constraint**: Net decrease in files/directories in `src/apps/ai/`

## Current State Analysis

### Files in AI App (Before)
```
src/apps/ai/
├── __init__.py
├── admin.py              # Django admin
├── agents.py             # Agent definitions (existing)
├── api.py                # Django Ninja API endpoints
├── apps.py               # Django app config
├── models.py             # DB models (Conversation, Message, Job, etc.)
├── schemas.py            # Pydantic schemas
├── signals.py            # Django signals
├── tasks.py              # Celery tasks
├── tests.py              # Tests
├── tools.py              # Agent tools (existing)
├── types.py              # Type definitions (existing)
├── views.py              # Django views
├── migrations/           # Django migrations (keep as-is)
├── prompt_templates/     # AI prompt templates (keep as-is)
└── util/                 # Utility modules (keep as-is)
```

**Total**: ~16 files + 2 directories + migrations + util

## Target Architecture

### Desired Module Structure
```
src/apps/ai/
├── __init__.py
├── admin.py              # Keep existing
├── api.py                # Keep existing API endpoints
├── apps.py               # Keep existing
├── models.py             # Keep existing DB models
├── views.py              # Keep existing views
├── tests.py              # Keep existing tests
├── signals.py            # Keep existing signals
├── core.py               # NEW: Reusable AI/agent utilities
├── stash.py              # NEW: Pydantic-ai-stash integration
├── domain.py             # NEW: Domain-specific agents & deps
├── services.py           # NEW: Cross-app story services
├── chat.py               # NEW: AI chat with SSE/HTMX
├── legacy.py             # OLD: Migrate agents.py, tools.py, types.py, tasks.py here
├── migrations/           # Keep as-is
├── prompt_templates/     # Keep as-is
└── util/                 # Keep as-is
```

**Target**: ~13 files + 2 directories (3 fewer files)

## Implementation Plan

### Phase 1: Foundation and Core Utilities _**(⏳ In Progress)**_

#### Core Module Setup
- [ ] Create `core.py` with reusable AI/agent patterns
  - [ ] Base agent configuration classes
  - [ ] Common dependency injection patterns
  - [ ] Agent registry system
  - [ ] Error handling utilities
  - [ ] Validation helpers

#### Stash Integration Module
- [ ] Create `stash.py` for pydantic-ai-stash Django integration
  - [ ] Artifact model integration
  - [ ] Binary content to URL conversion
  - [ ] File storage integration
  - [ ] Cleanup utilities

### Phase 2: Domain-Specific Components

#### Domain Module
- [ ] Create `domain.py` for use-case specific AI components
  - [ ] Writer agent configuration
  - [ ] Story-specific dependencies
  - [ ] Domain-specific prompts
  - [ ] Agent initialization functions

#### Story Services Module
- [ ] Create `services.py` for cross-app story operations
  - [ ] Story CRUD service functions
  - [ ] Page CRUD service functions
  - [ ] Integration with existing `stories.services`
  - [ ] Permission validation
  - [ ] SSE notification integration

### Phase 3: Chat and UI Integration

#### Chat Module with SSE/HTMX
- [ ] Create `chat.py` for AI chat controls
  - [ ] Response shape enforcement (message + chips + freetext)
  - [ ] SSE event publishing
  - [ ] HTMX integration helpers
  - [ ] Out-of-band (OOB) updates
  - [ ] AI panel state management

#### Required Response Shape Implementation
- [ ] Enforce agent response structure:
  ```python
  {
      "message": "AI response text",
      "chips": [
          {"emoji": "✍️", "color": "emerald", "text": "Action 1"},
          {"emoji": "🗞", "color": "amber", "text": "Action 2"}
      ],
      "freetext": True  # Allow custom input
  }
  ```

### Phase 4: Migration and Consolidation

#### Legacy Module Creation
- [ ] Create `legacy.py` consolidating existing modules
  - [ ] Move content from `agents.py` → `legacy.py`
  - [ ] Move content from `tools.py` → `legacy.py`
  - [ ] Move content from `types.py` → `legacy.py`
  - [ ] Move content from `tasks.py` → `legacy.py`
  - [ ] Update imports throughout codebase
  - [ ] Preserve all existing functionality

#### Cleanup
- [ ] Remove original files after migration:
  - [ ] Delete `agents.py`
  - [ ] Delete `tools.py`
  - [ ] Delete `types.py`
  - [ ] Delete `tasks.py`

### Phase 5: Integration and Flow Implementation

#### Agent Flow Integration
- [ ] Implement desired agent workflow:
  1. [ ] Agent receives prompt
  2. [ ] Agent pulls current story with tools
  3. [ ] Agent updates story via services
  4. [ ] Services trigger UI updates via SSE
  5. [ ] Agent generates follow-up response with required shape
  6. [ ] Response sent to UI via SSE+HTMX

#### Testing and Validation
- [ ] Test agent response shapes
- [ ] Validate SSE/HTMX integration
- [ ] Ensure existing features work
- [ ] Performance testing
- [ ] Error handling validation

### Phase 6: Documentation and Cleanup

#### Documentation Updates
- [ ] Update `CLAUDE.md` with new patterns
- [ ] Document response shape requirements
- [ ] Add agent flow documentation
- [ ] Create integration examples

#### Final Cleanup
- [ ] Remove any unused imports
- [ ] Run linting and formatting
- [ ] Update any remaining references
- [ ] Verify file count reduction

## Technical Specifications

### Artifact/Stash Integration

#### Problem
Currently using `BinaryContent` in pydantic-ai responses, need to integrate with Django's artifact system.

#### Solution
```python
# In stash.py
class ArtifactStash:
    def store_binary_content(self, content: BinaryContent) -> str:
        """Store binary content and return URL."""
        # Save to Artifact model
        # Return URL for frontend access

    def replace_binary_with_urls(self, tool_response: ToolReturn) -> ToolReturn:
        """Replace BinaryContent with URL references."""
        # Process tool response
        # Replace binary data with URLs
```

### Response Shape Enforcement

#### Required Structure
Every agent response must conform to:
```python
@dataclass
class AgentResponse:
    message: str
    chips: list[ChipData]
    freetext: bool = True

@dataclass
class ChipData:
    emoji: str
    color: str  # emerald, amber, neutral, etc.
    text: str
```

#### Integration with UI Templates
Responses must work with existing AI panel templates:
- `cotton/ai/panel/content/index.html`
- `cotton/ai/panel/content/chip_row.html`

### SSE/HTMX Integration

#### Event Publishing
```python
# In chat.py
def publish_agent_response(channel: str, response: AgentResponse):
    """Publish agent response via SSE for HTMX consumption."""
    send_event(channel, "ai_response", {
        "message": response.message,
        "chips": response.chips,
        "freetext": response.freetext
    })
```

#### HTMX Integration
- Use existing SSE patterns from stories app
- Leverage out-of-band (OOB) updates
- Maintain compatibility with current UI

## Success Criteria

### Functional Requirements
- ✅ All existing agent functionality preserved
- ✅ Story services properly integrated
- ✅ Pydantic-ai-stash working with artifacts
- ✅ Agent responses follow required shape
- ✅ SSE/HTMX integration functional
- ✅ No breaking changes to existing features

### Non-Functional Requirements
- ✅ Net reduction in AI app files/directories
- ✅ Clean module separation
- ✅ Maintainable code organization
- ✅ Performance equivalent or better
- ✅ Type safety maintained

### File Count Validation
- **Before**: ~16 files + 2 dirs
- **After**: ~13 files + 2 dirs
- **Reduction**: 3 fewer files minimum

## Implementation Guidelines

### Working with Checkboxes
- ✅ **Completed**: `- [x] Task description`
- ⏳ **In Progress**: `- [ ] Task description _**(⏳ In Progress)**_`
- 📋 **Pending**: `- [ ] Task description`
- 🔍 **Review Needed**: `- [ ] Task description _**(🔍 Review)**_`
- ⚠️ **Blocked**: `- [ ] Task description _**(⚠️ Blocked: reason)**_`
- 🧪 **Testing**: `- [ ] Task description _**(🧪 Testing)**_`

### Implementation Rules
1. **Focus Limit**: Work on 3-5 tasks maximum at any time
2. **Status Updates**: Mark tasks as in progress when starting
3. **Sequential Completion**: Complete tasks fully before moving to next phase
4. **Preserve Functionality**: No breaking changes to existing features
5. **File Count**: Ensure net reduction in files/directories

## Notes

- **Backward Compatibility**: All existing task functions and API endpoints must continue working
- **Migration Strategy**: Gradual migration to avoid breaking changes
- **Testing**: Comprehensive testing at each phase
- **Documentation**: Keep documentation updated as changes are made