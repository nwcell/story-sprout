import logging
from textwrap import dedent

from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.types import tool_return

logger = logging.getLogger(__name__)


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

    instructions = dedent(f"""\
        # INSTRUCTIONS
        ## ROLE:
        You are a talented children's book illustrator creating artwork for this story.

        ## SYSTEM_INSTRUCTION:
        * Always include the story text in the generated image.
        * Ensure the text is readable & consistent with other images.
        * Text should be thoroughly proofread.

        ## PROMPT:
        {prompt}
        ------
    """)

    contents = [
        instructions,
        "## STORY_CONTEXT:",
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
        return tool_return("Artifacts saved", content=content_blocks)
    else:
        content_blocks.append("Artist request completed but no images were generated")
        return tool_return("No artifacts", content=content_blocks)
