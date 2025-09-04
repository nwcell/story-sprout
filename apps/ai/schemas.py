from uuid import UUID

from pydantic import BaseModel


class JobStatus(BaseModel):
    job_uuid: UUID
    status: str


class StoryIn(BaseModel):
    story_uuid: UUID


class StoryTitleOut(BaseModel):
    title: str
