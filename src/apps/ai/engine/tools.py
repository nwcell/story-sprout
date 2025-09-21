import logging

from pydantic_ai import RunContext
from pydantic_ai.messages import ImageUrl, ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.stories.services import PageSchema, StorySchema

logger = logging.getLogger(__name__)


# Context Tools
# TODO: Add flag to get_story to include page images
def get_story(ctx: RunContext[StoryAgentDeps]) -> StorySchema:
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
    logger.info(f"tool.get_story retrieved story: title='{story.title}', page_count={story.page_count}")
    return story


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
    logger.info(f"tool.get_page retrieved page: {page}")
    return page


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
        return ToolReturn(return_value=f"No image found for page {page_num}")
    return ToolReturn(
        return_value=f"Found image for page {page_num}",
        content=[
            # BinaryContent(data=image_binary, media_type=media_type),
            ImageUrl(url=page.image.url, force_download=True),
        ],
    )


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
    return out


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
    return out


# Artist Tools
def artist_request(ctx: RunContext[StoryAgentDeps], prompt: str) -> ToolReturn:
    """Generate illustrations using AI image generation for the story.

    This tool creates custom illustrations based on the provided prompt and
    automatically includes comprehensive story context. The generator already has
    access to the complete story (all pages, text, and existing images), so you
    only need to specify the visual requirements for the new illustration.

    Args:
        ctx: The runtime context containing story dependencies and image client.
        prompt: Detailed description of the illustration to generate.
            Story context is automatically provided - no need to repeat story details.

    Returns:
        ToolReturn: Contains success/failure message and URLs of generated
        images. Generated image URLs can be used with update_page tool.

    Note:
        Generated images are saved as artifacts and accessible via absolute URLs.
        The tool automatically provides complete story context to ensure illustrations
        match the narrative and maintain visual consistency.
    """
    logger.info(f"tool.artist_request({ctx.deps.story_uuid}, {prompt})")

    # Use story service to prepare properly formatted story context with images
    story_service = ctx.deps.story_service
    contents = [
        "SYSTEM_INSTRUCTION: You are a talented children's book illustrator creating artwork for this story.",
        "PROMPT:",
        prompt,
        "STORY_CONTEXT:",
        *story_service.gemini_parts(),
    ]

    # Use direct Gemini client instead of nested Agent to avoid binary content issues
    resp = ctx.deps.image_client.models.generate_content(
        model=ctx.deps.image_model,
        contents=contents,
    )

    content_blocks = []
    image_urls = []
    for cand in resp.candidates or []:
        for part in cand.content.parts or []:
            if part.inline_data:
                data = part.inline_data.data
                image_url = ctx.deps.artifact_service.save_image(data)
                image_urls.append(image_url)
                logger.info(f"Artist created image: {image_url}")

    if image_urls:
        return_msg = f"Artist created {len(image_urls)} illustration(s): {', '.join(image_urls)}"
        content_blocks.append(return_msg)
        return ToolReturn(return_value="Artifacts saved", content=content_blocks)
    else:
        content_blocks.append("Artist request completed but no images were generated")
        return ToolReturn(return_value="No artifacts", content=content_blocks)


# Create toolsets
book_toolset = FunctionToolset([get_story, get_page, get_page_image, update_story, update_page])
image_toolset = FunctionToolset([artist_request])
