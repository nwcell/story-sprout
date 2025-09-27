import warnings
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobStatus(BaseModel):
    job_uuid: UUID
    status: str


class StoryJob(BaseModel):
    """DEPRECATED: Use apps.ai.types.StoryJob instead."""
    story_uuid: UUID

    def __init__(self, **data):
        warnings.warn(
            "StoryJob from schemas.py is deprecated. Use apps.ai.types.StoryJob instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(**data)


class PageJob(BaseModel):
    """DEPRECATED: Use apps.ai.types.PageJob instead."""
    page_uuid: UUID

    def __init__(self, **data):
        warnings.warn(
            "PageJob from schemas.py is deprecated. Use apps.ai.types.PageJob instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(**data)


class RequestSchema(BaseModel):
    conversation_uuid: UUID | None = None
    agent: Literal["writer"] = "writer"
    prompt: str


class AgentRequestSchema(BaseModel):
    conversation_uuid: UUID
    agent: str
    prompt: str


class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    content: dict


# class ConversationSchema(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     uuid: UUID
#     title: str | None
#     meta: dict
#     created_at: datetime
#     updated_at: datetime


# class ConversationDetailSchema(ConversationSchema):
#     messages: list[MessageSchema]

#     @field_validator("messages", mode="before")
#     @classmethod
#     def coerce_related_manager(cls, v):
#         # Accept RelatedManager, QuerySet, or list
#         if hasattr(v, "all"):
#             return list(v.all())
#         return list(v)
