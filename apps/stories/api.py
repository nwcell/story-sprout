from uuid import UUID

from django.shortcuts import render
from ninja import ModelSchema, Router

from apps.stories.models import Story

router = Router()


class StorySchema(ModelSchema):
    class Meta:
        model = Story
        fields = ["uuid", "title", "description", "user"]


@router.get("/{story_uuid}", response=StorySchema)
def story_details(request, story_uuid: UUID):
    story = Story.objects.get(uuid=story_uuid)
    if request.htmx:
        return render(request, "stories/story_detail_new.html", {"story": story})
    return story
