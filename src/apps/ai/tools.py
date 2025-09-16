from pydantic_ai import BinaryContent, RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from apps.ai.types import AgentDependencies


async def get_story(ctx: RunContext[AgentDependencies]) -> dict:
    """Get story information for the current conversation."""
    # TODO: Implement story retrieval based on conversation context
    return {"message": "Story retrieval not yet implemented"}


async def get_page(ctx: RunContext[AgentDependencies], page_num: int) -> dict:
    """Get page information by page number."""
    # TODO: Implement page retrieval based on conversation context
    return {"message": f"Page {page_num} retrieval not yet implemented"}


async def get_page_image(ctx: RunContext[AgentDependencies], page_num: int) -> BinaryContent | None:
    """Get page image by page number."""
    # TODO: Implement page image retrieval
    return None


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
