from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage


class JobStatus(BaseModel):
    job_uuid: UUID
    status: str


class StoryJob(BaseModel):
    story_uuid: UUID


class PageJob(BaseModel):
    page_uuid: UUID


class RequestSchema(BaseModel):
    conversation_uuid: UUID | None = None
    agent: Literal["writer"] = "writer"
    prompt: str


class AgentRequestSchema(BaseModel):
    conversation_uuid: UUID
    agent: str
    prompt: str


class MessageSchema(BaseModel):
    uuid: UUID
    content: ModelMessage


class ConversationSchema(BaseModel):
    uuid: UUID
    title: str | None
    meta: dict
    created_at: datetime
    updated_at: datetime


class ConversationDetailSchema(ConversationSchema):
    messages: list[MessageSchema]
