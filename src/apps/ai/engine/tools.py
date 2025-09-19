import logging

from pydantic_ai import RunContext
from pydantic_ai.messages import BinaryContent, ImageUrl, ToolReturn
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
):
    """Update the text content for a specific page.

    Use this tool to set or update the content and/or image text for a page.
    Returns confirmation of what was updated."""

    if not content and not image_text:
        raise ValueError("Must provide at least one of content or image_text")

    story_service = ctx.deps.story_service
    story_service.update_page(page_key=page_num, content=content, image_text=image_text)

    out = {}
    if content:
        out["content"] = content
    if image_text:
        out["image_text"] = image_text
    out = {"action": "updated_page", **out}
    logger.info(f"tool.update_page updated page {page_num}: {out}")
    return out


# Expensive Generative Tools
def generate_image(ctx: RunContext[StoryAgentDeps], prompt: str) -> ToolReturn:
    """Generate an image using the prompt."""
    resp = ctx.deps.image_client.models.generate_content(
        model=ctx.deps.image_model,
        contents=[prompt],
    )

    content_blocks = []
    return_value = {"texts": [], "images": []}

    for cand in resp.candidates or []:
        for part in cand.content.parts or []:
            if part.text:
                content_blocks.append(part.text)
                return_value["texts"].append(part.text)
            elif part.inline_data:
                mime = getattr(part.inline_data, "mime_type", "image/png")
                data = part.inline_data.data
                img = BinaryContent(data=data, media_type=mime)
                content_blocks.append(img)
                return_value["images"].append({"mime": mime, "len": len(data)})

    return ToolReturn(
        return_value=return_value,
        content=content_blocks,
    )


# Create toolsets
book_toolset = FunctionToolset([get_story, get_page, get_page_image, update_story, update_page])
image_toolset = FunctionToolset([generate_image])
