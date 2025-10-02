# Create toolsets
import logging

from pydantic_ai.toolsets import FunctionToolset

from apps.ai.engine.base.toolsets import EnhancedToolset
from apps.ai.engine.tools.art import artist_request
from apps.ai.engine.tools.story import (
    create_page,
    delete_page,
    get_page,
    get_page_image,
    get_story,
    move_page,
    update_page,
    update_story,
)

logger = logging.getLogger(__name__)

_book_function_toolset = FunctionToolset(
    [
        # Read operations - inspect existing content
        get_story,
        get_page,
        get_page_image,
        # Create operations - add new content
        create_page,
        # Update operations - modify existing content
        update_story,
        update_page,
        # Reorganize operations - change structure
        move_page,
        # Destructive operations - remove content (use carefully)
        delete_page,
        # Image Generation
        artist_request,
    ]
)
_image_function_toolset = FunctionToolset([artist_request])

# Wrap toolsets with enhanced functionality
book_toolset = EnhancedToolset(_book_function_toolset)
image_toolset = EnhancedToolset(_image_function_toolset)
