from uuid import UUID

from ninja import Schema


class UserSchema(Schema):
    id: int
    first_name: str
    last_name: str
    email: str


class PageSchema(Schema):
    uuid: UUID
    content: str
    image_text: str
    # image: str


class StorySchema(Schema):
    uuid: UUID
    user: UserSchema
    title: str
    description: str
    page_count: int
    channel: str
    # pages: list[PageSchema]

    # @classmethod
    # def from_orm(cls, story: Story):
    #     return cls(
    #         uuid=story.uuid,
    #         title=story.title or "",
    #         description=story.description or "",
    #         user=story.user_id,
    #         page_count=story.page_count,
    #         channel=story.channel,
    #     )
