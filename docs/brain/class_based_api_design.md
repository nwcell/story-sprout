# Class-Based API Design for Stories

## Current vs. Proposed Architecture

### Current State Analysis (Function-Based Views)
The existing `src/apps/stories/api.py` contains:

**Story Operations (Functions):**
- `list_stories()` - GET `/stories/`
- `create_story()` - POST `/stories/`
- `get_story()` - GET `/stories/{uuid}`
- `update_story()` - PATCH `/stories/{uuid}`
- `delete_story()` - DELETE `/stories/{uuid}`
- `get_story_title()` - GET `/stories/{uuid}/title`
- `get_story_description()` - GET `/stories/{uuid}/description`

**Page Operations (Functions):**
- `list_pages()` - GET `/stories/{uuid}/pages/`
- `get_page()` - GET `/stories/{uuid}/pages/{uuid}`
- `create_page()` - POST `/stories/{uuid}/pages/`
- `update_page()` - PATCH `/stories/{uuid}/pages/{uuid}`
- `delete_page()` - DELETE `/stories/{uuid}/pages/{uuid}`
- `move_page()` - POST `/stories/{uuid}/pages/{uuid}/move/{direction}`
- `get_page_content()` - GET `/stories/{uuid}/pages/{uuid}/content`
- `get_page_image_text()` - GET `/stories/{uuid}/pages/{uuid}/image_text`
- `get_page_image()` - GET `/stories/{uuid}/pages/{uuid}/image`
- `upload_page_image()` - POST `/stories/{uuid}/pages/{uuid}/image`
- `delete_page_image()` - DELETE `/stories/{uuid}/pages/{uuid}/image`

## Proposed Class-Based Design

### StoryViewSet Class Structure

```python
from ninja import Router
from ninja.pagination import paginate
from ninja.viewsets import ViewSet
from typing import List, Optional
from uuid import UUID

router = Router()

class StoryViewSet(ViewSet):
    """
    Comprehensive Story CRUD operations.
    Handles both JSON API and HTMX responses.
    """

    def get_queryset(self):
        """Filter stories by authenticated user."""
        return Story.objects.filter(user=self.request.user)

    def list(self, request) -> List[StoryOut]:
        """GET /stories/ - List user's stories"""
        # JSON: Return paginated story list
        # HTMX: Return stories/index.html template

    def create(self, request, payload: StoryIn) -> StoryOut:
        """POST /stories/ - Create new story"""
        # JSON: Return created story
        # HTMX: Redirect to story detail view

    def retrieve(self, request, story_uuid: UUID) -> StoryOut:
        """GET /stories/{uuid} - Get story details"""
        # JSON: Return story data
        # HTMX: Return stories/detail.html template

    def update(self, request, story_uuid: UUID, payload: StoryIn) -> StoryOut:
        """PATCH /stories/{uuid} - Update story"""
        # JSON: Return updated story
        # HTMX: Return 204 with HX-Trigger events

    def destroy(self, request, story_uuid: UUID):
        """DELETE /stories/{uuid} - Delete story"""
        # JSON: Return 204
        # HTMX: Return HX-Trigger delete event

    # Specialized endpoints
    def get_title(self, request, story_uuid: UUID) -> StoryTitleOut:
        """GET /stories/{uuid}/title - Get story title"""

    def get_description(self, request, story_uuid: UUID) -> StoryDescriptionOut:
        """GET /stories/{uuid}/description - Get story description"""
```

### PageViewSet Class Structure

```python
class PageViewSet(ViewSet):
    """
    Comprehensive Page CRUD operations with nested story routing.
    Handles page ordering, content management, and image operations.
    """

    def get_story(self, story_uuid: UUID):
        """Get story and verify user ownership."""
        return get_object_or_404(Story, uuid=story_uuid, user=self.request.user)

    def get_page(self, story_uuid: UUID, page_uuid: UUID):
        """Get page and verify user owns parent story."""
        story = self.get_story(story_uuid)
        return get_object_or_404(Page, uuid=page_uuid, story=story), story

    def list(self, request, story_uuid: UUID) -> List[PageOut]:
        """GET /stories/{uuid}/pages/ - List story pages"""

    def create(self, request, story_uuid: UUID, payload: PageIn) -> PageOut:
        """POST /stories/{uuid}/pages/ - Create new page"""

    def retrieve(self, request, story_uuid: UUID, page_uuid: UUID) -> PageOut:
        """GET /stories/{uuid}/pages/{uuid} - Get page details"""

    def update(self, request, story_uuid: UUID, page_uuid: UUID, payload: PageIn) -> PageOut:
        """PATCH /stories/{uuid}/pages/{uuid} - Update page"""

    def destroy(self, request, story_uuid: UUID, page_uuid: UUID):
        """DELETE /stories/{uuid}/pages/{uuid} - Delete page"""

    # Specialized content endpoints
    def get_content(self, request, story_uuid: UUID, page_uuid: UUID) -> PageContentOut:
        """GET /stories/{uuid}/pages/{uuid}/content"""

    def get_image_text(self, request, story_uuid: UUID, page_uuid: UUID) -> PageImageTextOut:
        """GET /stories/{uuid}/pages/{uuid}/image_text"""

    def get_image(self, request, story_uuid: UUID, page_uuid: UUID) -> PageImageOut:
        """GET /stories/{uuid}/pages/{uuid}/image"""

    # Page management operations
    def move_up(self, request, story_uuid: UUID, page_uuid: UUID) -> PageOut:
        """POST /stories/{uuid}/pages/{uuid}/move/up"""

    def move_down(self, request, story_uuid: UUID, page_uuid: UUID) -> PageOut:
        """POST /stories/{uuid}/pages/{uuid}/move/down"""

    # Image operations
    def upload_image(self, request, story_uuid: UUID, page_uuid: UUID, file: UploadedFile) -> PageOut:
        """POST /stories/{uuid}/pages/{uuid}/image"""

    def delete_image(self, request, story_uuid: UUID, page_uuid: UUID):
        """DELETE /stories/{uuid}/pages/{uuid}/image"""
```

## Benefits of Class-Based Approach

### 1. Code Organization
- **Single Responsibility**: One class per resource type
- **Grouped Operations**: Related methods in same class
- **Shared Logic**: Common authorization/validation in base methods
- **Consistent Patterns**: Standardized CRUD method names

### 2. Maintainability
- **DRY Principle**: Shared `get_story()` and `get_page()` methods
- **Error Handling**: Centralized permission checks
- **Code Reuse**: Base authorization logic shared across methods
- **Testing**: Easier to test complete resource operations

### 3. API Consistency
- **RESTful Patterns**: Standard HTTP verbs and resource paths
- **Predictable URLs**: `/stories/` and `/stories/{uuid}/pages/` patterns
- **Unified Response**: Consistent JSON/HTMX handling per method

### 4. Feature Completeness
- **Full CRUD**: Create, Read, Update, Delete for both resources
- **Specialized Endpoints**: Content, image, and metadata access
- **Page Management**: Ordering and image operations
- **User Security**: Authorization built into base methods

## MCP Integration Strategy

### API-First Approach
```python
# MCP tools call the class-based API endpoints
class StoryMCPToolset(MCPToolset):
    def get_story_by_id(self, story_uuid: str) -> dict:
        # Calls StoryViewSet.retrieve() via internal API
        response = self.api_client.get(f"/api/stories/{story_uuid}")
        return response.json()

    def create_story(self, title: str, description: str = "") -> dict:
        # Calls StoryViewSet.create() via internal API
        payload = {"title": title, "description": description}
        response = self.api_client.post("/api/stories/", json=payload)
        return response.json()
```

### Benefits of API-First MCP
1. **Single Source of Truth**: API handles all business logic
2. **Consistency**: MCP tools use same validation/authorization as web UI
3. **Testing**: API endpoints already tested, MCP inherits reliability
4. **Maintenance**: Changes to business logic automatically affect MCP tools

## Implementation Priority

### Phase 1: Story Class Refactor
1. Create `StoryViewSet` class with all current story operations
2. Replace function-based routes with class-based routes
3. Maintain backward compatibility with existing URLs
4. Test JSON and HTMX response parity

### Phase 2: Page Class Refactor
1. Create `PageViewSet` class with all current page operations
2. Implement nested routing pattern for pages within stories
3. Maintain all specialized endpoints (content, image_text, image)
4. Test page ordering and image operations

### Phase 3: MCP Integration
1. Implement `StoryMCPToolset` that calls class-based API
2. Add comprehensive MCP tools for story and page manipulation
3. Integrate MCP toolset with pydantic-ai agent
4. Test end-to-end agent story creation workflows

This class-based approach provides better organization, maintainability, and a solid foundation for MCP integration while preserving all existing functionality.