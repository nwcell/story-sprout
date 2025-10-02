import logging

from pydantic_ai import RunContext
from pydantic_ai.messages import ImageUrl, ToolReturn

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.types import tool_return
from apps.stories.services import PageSchema

logger = logging.getLogger(__name__)


# Read operations - inspect existing content


# TODO: Add flag to get_story to include page images
def get_story(ctx: RunContext[StoryAgentDeps]) -> ToolReturn:
    """Get comprehensive story information including title, description, and all pages.

    This tool retrieves the complete story data for the current conversation context,
    including metadata and all page information. Note that only image metadata
    (URLs, dimensions, filenames) is included - actual page images must be
    requested separately using get_page_image().

    Args:
        ctx: The runtime context containing story dependencies.

    Returns:
        StorySchema: Complete story information including title, description, page count,
        and detailed information for all pages. Page image data includes only metadata
        (URL, dimensions, filename) - use get_page_image() for actual image content.
    """
    logger.info("tool.get_story()")
    story_service = ctx.deps.story_service
    story = story_service.get_story()
    return tool_return(story)


# TODO: Add flag to get_story to include page images
def get_page(ctx: RunContext[StoryAgentDeps], page_num: int) -> PageSchema:
    """Get detailed information for a specific page in the story.

    Retrieves comprehensive page data including content, image descriptions,
    and metadata for the specified page number. Note that only image metadata
    (URLs, dimensions, filenames) is included - actual page images must be
    requested separately using get_page_image().

    Args:
        ctx: The runtime context containing story dependencies.
        page_num: The page number to retrieve (1-indexed).

    Returns:
        PageSchema: Detailed page information including UUID, content, image_text,
        image metadata, and position flags (is_first, is_last). Image data includes
        only metadata - use get_page_image() for actual image content.
    """
    logger.info(f"tool.get_page({page_num})")
    story_service = ctx.deps.story_service
    page = story_service.get_page(page_num)
    return tool_return(page)


def get_page_image(ctx: RunContext[StoryAgentDeps], page_num: int) -> ToolReturn:
    """Retrieve the image associated with a specific page.

    This tool fetches the image for the specified page number and returns it
    as part of the tool response. If no image exists for the page, returns
    an appropriate message.

    Args:
        ctx: The runtime context containing story dependencies.
        page_num: The page number to get the image for (1-indexed).

    Returns:
        ToolReturn: Contains either the page image as ImageUrl content or
        a message indicating no image was found.
    """
    logger.info(f"tool.get_page_image({page_num})")
    story_service = ctx.deps.story_service
    page = story_service.get_page(page_num)
    if not page.image:
        return tool_return("No image found for page {page_num}")
    return tool_return(
        f"Found image for page {page_num}",
        content=[
            # BinaryContent(data=image_binary, media_type=media_type),
            ImageUrl(url=page.image.url, force_download=True),
        ],
    )


# Create operations - add new content
def create_page(
    ctx: RunContext[StoryAgentDeps],
    content: str | None = None,
    image_text: str | None = None,
    image_url: str | None = None,
):
    """Create a new page at the end of the story.

    This tool adds a new page to the story with optional content, image description,
    and image. The page is automatically positioned at the end of the story and
    assigned the next sequential page number. Updates are immediately saved and
    will trigger UI refresh events.

    Args:
        ctx: The runtime context containing story dependencies.
        content: Initial text content for the new page. Optional.
        image_text: Description/prompt for the page's image. Optional.
        image_url: URL of image to associate with the page. Can be from
            artist_request tool or external source. Optional.

    Returns:
        dict: Confirmation object with 'action' key and created page details.

    Note:
        At least one of the optional parameters should typically be provided
        to create meaningful content, though an empty page is allowed.
    """
    logger.info(f"tool.create_page({content}, {image_text}, {image_url})")
    story_service = ctx.deps.story_service
    story_service.create_page(content=content, image_text=image_text, image_data=image_url)

    # Get the updated story to find the new page number
    story = story_service.get_story()
    new_page_num = story.page_count

    out = {"action": "created_page", "page_num": new_page_num}
    if content:
        out["content"] = content
    if image_text:
        out["image_text"] = image_text
    if image_url:
        out["image_url"] = image_url

    logger.info(f"tool.create_page created page {new_page_num}: {out}")
    return tool_return(out)


# Tools that have side effects
def update_story(ctx: RunContext[StoryAgentDeps], title: str | None = None, description: str | None = None):
    """Update the story's title and/or description.

    This tool modifies the story metadata. At least one parameter must be provided.
    Updates are immediately saved and will trigger UI refresh events.

    Args:
        ctx: The runtime context containing story dependencies.
        title: New title for the story. Optional.
        description: New description for the story. Optional.

    Note:
        Must provide one or more of: title, description.

    Returns:
        dict: Confirmation object with 'action' key and updated fields.

    Raises:
        ValueError: If neither title nor description is provided.
    """
    logger.info(f"tool.update_story({title}, {description})")
    if not title and not description:
        raise ValueError("Must provide at least one of title or description")

    story_service = ctx.deps.story_service
    story_service.update_story(title, description)

    out = {}
    if title:
        out["title"] = title
    if description:
        out["description"] = description
    out = {"action": "updated_story", **out}
    logger.info(f"tool.update_story updated story: {out}")
    return tool_return(out)


def update_page(
    ctx: RunContext[StoryAgentDeps],
    page_num: int,
    content: str | None = None,
    image_text: str | None = None,
    image_url: str | None = None,
):
    """Update content, image description, and/or image for a specific page.

    This tool modifies page content including the story text, image descriptions,
    and actual images. At least one parameter must be provided. Updates are
    immediately saved and will trigger UI refresh events.

    Args:
        ctx: The runtime context containing story dependencies.
        page_num: The page number to update (1-indexed).
        content: New text content for the page. Optional.
        image_text: New description/prompt for the page's image. Optional.
        image_url: URL of new image to associate with the page. Can be from
            artist_request tool or external source. Optional.

    Note:
        Must provide one or more of: content, image_text, image_url.

    Returns:
        dict: Confirmation object with 'action' key and updated fields.

    Raises:
        ValueError: If no parameters are provided for update.
    """
    logger.info(f"tool.update_page({page_num}, {content}, {image_text}, {image_url})")
    if not content and not image_text and not image_url:
        raise ValueError("Must provide at least one of content, image_text, or image_url")

    story_service = ctx.deps.story_service
    story_service.update_page(page_key=page_num, content=content, image_text=image_text, image_data=image_url)

    out = {}
    if content:
        out["content"] = content
    if image_text:
        out["image_text"] = image_text
    if image_url:
        out["image_url"] = image_url
    out = {"action": "updated_page", **out}
    logger.info(f"tool.update_page updated page {page_num}: {out}")
    return tool_return(out)


# Reorganize operations - change structure
def move_page(ctx: RunContext[StoryAgentDeps], page_num: int, target: str | int):
    """Move a page to a new position within the story.

    This tool reorders pages within the story. You can move a page to a specific
    position or use directional commands. Page numbers are automatically updated
    after the move. Updates are immediately saved and will trigger UI refresh events.

    Args:
        ctx: The runtime context containing story dependencies.
        page_num: The page number to move (1-indexed).
        target: Target position. Can be:
            - "first": Move to beginning of story
            - "last": Move to end of story
            - "up": Move one position earlier
            - "down": Move one position later
            - int: Move to specific page number (1-indexed, not 0-indexed)

    Returns:
        dict: Confirmation object with 'action' key, original and new positions.

    Raises:
        ValueError: If page_num or target is out of range or invalid.

    Note:
        When moving to a specific position (int), other pages shift automatically.
        Page numbers are 1-based, not 0-based indexes.
    """
    logger.info(f"tool.move_page({page_num}, {target})")
    story_service = ctx.deps.story_service

    # Get original position for logging
    original_pos = page_num

    story_service.move_page(page_key=page_num, target=target)

    out = {"action": "moved_page", "original_position": original_pos, "target": target}
    logger.info(f"tool.move_page moved page from {original_pos} to {target}: {out}")
    return tool_return(out)


# Destructive operations - remove content (use carefully)
def delete_page(ctx: RunContext[StoryAgentDeps], page_num: int):
    """Delete a specific page from the story.

    This tool permanently removes a page and all its content from the story.
    Page numbers are automatically reordered after deletion. Updates are
    immediately saved and will trigger UI refresh events.

    Args:
        ctx: The runtime context containing story dependencies.
        page_num: The page number to delete (1-indexed).

    Returns:
        dict: Confirmation object with 'action' key and deleted page number.

    Raises:
        ValueError: If page_num is out of range or invalid.

    Warning:
        This operation cannot be undone. The page and all its content
        (text, images, descriptions) will be permanently lost.
    """
    logger.info(f"tool.delete_page({page_num})")
    story_service = ctx.deps.story_service
    story_service.delete_page(page_key=page_num)

    out = {"action": "deleted_page", "page_num": page_num}
    logger.info(f"tool.delete_page deleted page {page_num}: {out}")
    return tool_return(out)
