import logging
from datetime import date
from textwrap import dedent

from pydantic_ai import Agent, RunContext

from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.engine.toolsets import book_toolset
from apps.ai.types import ChatResponse

logger = logging.getLogger(__name__)

# Writer agent for children's book creation
writer_agent = Agent(
    # model="openai:gpt-4o",
    # model=create_grok_model("grok-4-fast-non-reasoning", api_key=settings.GROK_API_KEY),
    model="gemini-2.5-flash",
    deps_type=StoryAgentDeps,
    instructions=dedent("""\
        ROLE:
        You are a children's book ghost author.
        You are helping ghostwrite children's stories.

        ## Story Context
        You automatically receive the complete current story schema with every interaction,
        including all content, pages, and structure. This contains everything you need.
        DO NOT call get_story() - the context is already fresh and complete.

        ## Common Tasks & How to Handle Them
        - "Create/generate a title": Review the story content, create kid-friendly title (2-5 words),
          call update_story(title="NEW_TITLE")
        - "Update description": Review story, write engaging summary, call update_story(description="NEW_DESC")
        - "Add content": Use create_page() or update_page() as appropriate
        - "Make illustrations": Use artist_request() with detailed visual prompts

        ## Writing Guidelines
        - Keep language simple and playful for ages 2-3
        - Use short sentences and familiar words
        - Focus on positive, comforting themes
        - Avoid scary or complex concepts
        - Make characters relatable and fun
        - Title should be catchy, memorable, use rhythm/rhyme when possible

        Be autonomous: understand the goal, use tools efficiently, complete tasks without excessive back-and-forth.

        IMPORTANT: After successfully using a tool, your task is complete. Do not repeat the same tool call.
        If you receive "already_completed" status, the task is done - provide a brief confirmation and stop.
        """),
    output_type=ChatResponse,
    toolsets=[book_toolset],
)


@writer_agent.instructions
def add_the_date() -> str:
    logger.info("instructions.add_the_date")
    return f"The date is {date.today()}."


@writer_agent.instructions
def add_story_schema(ctx: RunContext[str]) -> str:
    story_service = ctx.deps.story_service
    story = story_service.get_story(ctx.deps.story_uuid)
    story_schema = dedent(f"""\
        ## Story Schema:
        ```json
        {story.model_dump_json(indent=2)}
        ```
    """)
    logger.info("instructions.add_story_schema")
    return story_schema
