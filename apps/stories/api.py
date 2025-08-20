from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from ninja import File, ModelSchema, Router, Schema
from ninja.files import UploadedFile

from apps.stories.models import Page, Story
from core.utils import append_content

router = Router()


class StoryOut(ModelSchema):
    class Meta:
        model = Story
        fields = ["uuid", "title", "description", "user"]


class StoryIn(Schema):
    title: str | None = None
    description: str | None = None


@router.get("/{key}", response=StoryOut)
def get_story(request, key: UUID):
    story = Story.objects.get(uuid=key)
    if request.htmx:
        # TODO: Fix this
        return render(request, "stories/story_detail_new.html", {"story": story})
    return story


@router.patch("/{key}", response=StoryOut)
def update_story(request, key: UUID, payload: StoryIn):
    story = get_object_or_404(Story, uuid=key)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(story, attr, value)
    story.save()

    if request.htmx:
        # TODO: Add logic to detect autozave vs a generic update
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "update-story"
        return response
    return story


class PageOut(ModelSchema):
    class Meta:
        model = Page
        fields = ["uuid", "content", "image_text", "image"]


class PageIn(Schema):
    content: str | None = None
    image_text: str | None = None


@router.post("/{story_uuid}/pages", response=PageOut)
def create_page(request, story_uuid: UUID, payload: PageIn):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = Page.objects.create(story=story, **payload.dict())

    if request.htmx:
        # Get new page and append OOB new page button
        context = {"page": page, "story": story}
        response = render(request, "cotton/story/page/index.html", context)
        response["HX-Trigger"] = "create-page"

        # Add OOB new button
        if page.order == 0:
            response = append_content(response, "cotton/story/page/new_page_button.html", context, oob=True)

        # Update OOB move buttons
        for page in story.pages.all():
            response = append_content(response, "cotton/story/page/move_page_buttons.html", {"page": page}, oob=True)
        return response
    return page


@router.patch("/{story_uuid}/pages/{page_uuid}", response=PageOut)
def update_page(request, story_uuid: UUID, page_uuid: UUID, payload: PageIn):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)

    # Update page fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(page, field, value)
    page.save()

    if request.htmx:
        # TODO: Add logic to detect autozave vs a generic update
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "update-page"
        return response
    return page


@router.delete("/{story_uuid}/pages/{page_uuid}")
def delete_page(request, story_uuid: UUID, page_uuid: UUID):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)
    page.delete()

    if request.htmx:
        response = HttpResponse("")
        response["HX-Trigger"] = "delete-page"
        # Update OOB move buttons
        for page in story.pages.all():
            response = append_content(response, "cotton/story/page/move_page_buttons.html", {"page": page}, oob=True)
        return response

    return HttpResponse(status=204)


@router.post("/{story_uuid}/pages/{page_uuid}/image", response=PageOut)
def upload_page_image(request, story_uuid: UUID, page_uuid: UUID, file: File[UploadedFile]):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)
    page.image = file
    page.save()

    if request.htmx:
        # Return the updated image component with all required context
        context = {
            "image": page.image,
            "upload_url": request.path,
            "delete_url": request.path,
        }
        return render(request, "cotton/fields/image.html", context)
    return page


@router.delete("/{story_uuid}/pages/{page_uuid}/image")
def delete_page_image(request, story_uuid: UUID, page_uuid: UUID):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)
    page.image = None
    page.save()

    if request.htmx:
        # Return the updated image component with all required context
        context = {
            "image": page.image,
            "upload_url": request.path,
            "delete_url": request.path,
        }
        return render(request, "cotton/fields/image.html", context)
    return page
