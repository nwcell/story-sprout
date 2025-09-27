from typing import Literal, Annotated
from uuid import UUID

from pydantic import BaseModel, TypeAdapter, Field, Discriminator
from pydantic_core import core_schema


class Emoji(str):
    """Exactly one emoji (heuristic, stdlib only)."""

    @classmethod
    def _validate(cls, v: str) -> "Emoji":
        if not isinstance(v, str):
            raise TypeError("emoji must be a string")
        if not cls._looks_like_emoji(v):
            raise ValueError("must be exactly one emoji")
        return cls(v)

    def _looks_like_emoji(s: str) -> bool:
        # Heuristic: no spaces, not empty, contains at least one emoji-range codepoint
        if not s or " " in s:
            return False

        for ch in s:
            codepoint = ord(ch)
            if 0x1F000 <= codepoint <= 0x1FAFF or 0x2600 <= codepoint <= 0x27BF:
                return True

        return False

    @classmethod
    def __get_pydantic_core_schema__(cls, *_):
        return core_schema.no_info_after_validator_function(cls._validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, *_):
        return {
            "type": "string",
            "title": "Emoji",
            "description": "Exactly one emoji (heuristic).",
            "examples": ["🚀", "👍🏽", "🇺🇸", "👩‍💻"],
        }


ChipColor = Literal[
    "pink",
    "rose",
    "purple",
    "violet",
    "indigo",
    "blue",
    "sky",
    "cyan",
    "teal",
    "emerald",
    "green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "red",
    "neutral",
    "slate",
    "rainbow",
]


class Chip(BaseModel):
    emoji: Emoji | None
    color: ChipColor = "neutral"
    value: str


# User and Job Types
class User(BaseModel):
    user_id: int


class Job(BaseModel):
    """Base job type for AI tasks."""
    job_type: str = Field(..., description="Discriminator for job type")


class StoryJob(Job):
    job_type: Literal["story"] = "story"
    story_uuid: UUID


class PageJob(Job):
    job_type: Literal["page"] = "page"
    page_uuid: UUID


class ChatRequest(BaseModel):
    conversation_uuid: UUID | None = None
    message: str | None = None
    artifact_uuids: list[UUID] | None = None


class TaskPayload(BaseModel):
    """Standard payload format for all AI tasks."""
    user: User
    chat_request: ChatRequest
    job: Annotated[StoryJob | PageJob, Field(discriminator="job_type")] | None = None


class ChatResponse(BaseModel):
    message: str
    chips: list[Chip] = []


chat_response_adapter = TypeAdapter(ChatResponse)
