# from dataclasses import dataclass
import mimetypes
from dataclasses import dataclass, field
from uuid import UUID

from google.genai import Client as GoogleClient
from pydantic_ai import Agent, BinaryContent, RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from apps.stories.models import Story
from apps.stories.schema import PageSchema, StorySchema


@dataclass
class ImageDependencies:
    client: GoogleClient = field(default_factory=lambda: GoogleClient())
    model: str = "gemini-2.5-flash-image-preview"


@dataclass
class Dependencies:
    story_uuid: UUID
    image: ImageDependencies = field(default_factory=lambda: ImageDependencies())


def get_story(ctx: RunContext[Dependencies]) -> StorySchema:
    story = Story.objects.get(uuid=ctx.deps.story_uuid)
    return StorySchema.from_orm(story)


async def get_page(ctx: RunContext[Dependencies], page_num: int) -> PageSchema:
    story = Story.objects.get(uuid=ctx.deps.story_uuid)
    return PageSchema.from_orm(story.get_page_by_num(page_num))


async def get_page_image(ctx: RunContext[Dependencies], page_num: int) -> BinaryContent | None:
    story = Story.objects.get(uuid=ctx.deps.story_uuid)
    page = story.get_page_by_num(page_num)
    if not page.image:
        return None
    image_binary = page.image_binary
    mt, _ = mimetypes.guess_type(page.image.name)
    media_type = mt or "image/png"
    return BinaryContent(data=image_binary, media_type=media_type)


async def generate_image(ctx: RunContext[Dependencies], prompt: str) -> ToolReturn:
    resp = ctx.deps.image.client.models.generate_content(
        model=ctx.deps.image.model,
        contents=[prompt],
        # config={"response_modalities": ["TEXT", "IMAGE"]},
    )

    content_blocks = []  # what the LLM will “see”
    return_value = {"texts": [], "images": []}  # for your app logic

    for cand in resp.candidates or []:
        for part in cand.content.parts or []:
            if part.text:
                # capture all text parts
                content_blocks.append(part.text)
                return_value["texts"].append(part.text)
            elif part.inline_data:
                mime = getattr(part.inline_data, "mime_type", "image/png")
                data = part.inline_data.data  # already bytes
                img = BinaryContent(data=data, media_type=mime)
                content_blocks.append(img)
                return_value["images"].append({"mime": mime, "len": len(data)})

    return ToolReturn(
        return_value=return_value,
        content=content_blocks,
    )


book_toolset = FunctionToolset([get_story, get_page, get_page_image])
image_toolset = FunctionToolset([generate_image])


agent = Agent(
    "openai:gpt-4o",
    deps_type=Dependencies,
    system_prompt=("You are a childrens book ghost author.\nYou are helping ghostwrite childrens stories."),
    toolsets=[book_toolset, image_toolset],
)


# @agent.instructions
# async def add_story_uuid(ctx: RunContext[str]) -> str:
#     return f"Story UUID: {ctx.deps.story_uuid}."


# # story = Story.objects.get(uuid="067527ac-0ee5-4fe9-ad51-b316b12d5cc1")
# deps = Dependencies(story_uuid="067527ac-0ee5-4fe9-ad51-b316b12d5cc1")

# prompt = (
#     "Generate a new illustration for page 1.  use a watercolor style"
#     "The page content should be at the bottom of the image, in text format"
#     # "Use the image tool to create it. Scene: a cozy watercolor of a baby sea otter "
#     # "floating among lily pads at sunset with warm, whimsical caption on the bottom."
# )

# result = await agent.run(prompt, deps=deps)

# # Show the assistant's final text (optional)
# print(result.output)

# # Render any images the tool returned
# for msg in result.new_messages():  # or result.all_messages()
#     # Each message has .parts (SystemPromptPart, UserPromptPart, TextPart, etc.)
#     for part in getattr(msg, "parts", []):
#         # Some parts (e.g., UserPromptPart) wrap a list of "user content" items
#         content = getattr(part, "content", None)
#         if isinstance(content, list):
#             for item in content:
#                 if isinstance(item, BinaryContent) and item.is_image:
#                     display(NBImage(data=item.data))
#         elif isinstance(content, BinaryContent) and content.is_image:
#             display(NBImage(data=content.data))
