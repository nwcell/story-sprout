import logging

from pydantic_ai import RunContext
from pydantic_ai.messages import ImageUrl, ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.stories.services import PageSchema, StorySchema

logger = logging.getLogger(__name__)


# Context Tools
def get_story(ctx: RunContext[StoryAgentDeps]) -> StorySchema:
    """Get story information for the current conversation."""
    logger.info(f"tool.get_story({ctx.deps.story_uuid})")
    story_service = ctx.deps.story_service
    story = story_service.get_story()
    logger.info(f"tool.get_story retrieved story: title='{story.title}', page_count={story.page_count}")
    return story


def get_page(ctx: RunContext[StoryAgentDeps], page_num: int) -> PageSchema:
    """Get page information by page number."""
    logger.info(f"tool.get_page({ctx.deps.story_uuid}, {page_num})")
    story_service = ctx.deps.story_service
    page = story_service.get_page(page_num)
    logger.info(f"tool.get_page retrieved page: {page}")
    return page


def get_page_image(ctx: RunContext[StoryAgentDeps], page_num: int) -> ToolReturn:
    """Get page image by page number."""
    logger.info(f"tool.get_page_image({ctx.deps.story_uuid}, {page_num})")
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
    """Update story title and description.

    Use this tool when the user wants to change the story title and/or description.
    Returns confirmation of what was updated."""

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
    """Update the text content and/or image for a specific page.

    Use this tool to set or update the content, image text, and/or image for a page.
    For image_url, provide the URL of an image (e.g., from generate_image tool).
    Returns confirmation of what was updated."""

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
    """Request an illustration from the children's book artist."""
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
