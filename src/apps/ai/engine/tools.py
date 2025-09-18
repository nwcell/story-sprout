from pydantic_ai import RunContext
from pydantic_ai.messages import BinaryContent, ImageUrl, ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from apps.ai.engine.types import AgentDependencies
from apps.stories.services import PageSchema, StorySchema, StoryService


async def get_story(ctx: RunContext[AgentDependencies]) -> StorySchema:
    """Get story information for the current conversation."""
    story_service = StoryService(uuid=ctx.deps.conversation.story_uuid)
    return story_service.story


async def get_page(ctx: RunContext[AgentDependencies], page_num: int) -> PageSchema:
    """Get page information by page number."""
    story_service = StoryService(uuid=ctx.deps.conversation.story_uuid)
    page = story_service.get_page(page_num)
    return page


async def get_page_image(ctx: RunContext[AgentDependencies], page_num: int) -> ToolReturn:
    """Get page image by page number."""
    story_service = StoryService(uuid=ctx.deps.conversation.story_uuid)
    page = story_service.get_page(page_num)
    # media_type = page.image.content_type
    # image_binary = story_service.get_page_image_binary(page_num)
    return ToolReturn(
        return_value=f"Found image for page {page_num}",
        content=[
            # BinaryContent(data=image_binary, media_type=media_type),
            ImageUrl(url=page.image.url, force_download=True),
        ],
    )


async def generate_image(ctx: RunContext[AgentDependencies], prompt: str) -> ToolReturn:
    """Generate an image using the prompt."""
    resp = ctx.deps.image.models.generate_content(
        model="gemini-2.5-flash-image-preview",
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
book_toolset = FunctionToolset([get_story, get_page, get_page_image])
image_toolset = FunctionToolset([generate_image])
