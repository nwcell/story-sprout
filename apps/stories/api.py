from typing import Literal
from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django_htmx.http import push_url
from ninja import File, ModelSchema, Router, Schema
from ninja.files import UploadedFile

from apps.stories.models import Page, Story
from core.utils import append_content

router = Router()


# Story
class StoryOut(ModelSchema):
    class Meta:
        model = Story
        fields = ["uuid", "title", "description", "user"]


class StoryIn(Schema):
    title: str | None = None
    description: str | None = None


@router.get("", response=list[StoryOut])
def list_stories(request):
    story_list = Story.objects.filter(user=request.user)
    if request.htmx:
        # TODO: Verify this works
        response = render(request, "cotton/stories/index.html", {"stories": story_list, "oob": True})
        # response = push_url(response, reverse("stories:stories"))
        response["HX-Trigger"] = "list-stories"
        return response
    return story_list


@router.post("", response=StoryOut)
def create_story(request, payload: StoryIn | None = None):
    if not payload:
        payload = StoryIn()
    story = Story.objects.create(user=request.user, **payload.dict())
    if request.htmx:
        response = render(request, "cotton/stories/detail.html", {"story": story})
        response = push_url(response, reverse("stories:story_detail", kwargs={"story_uuid": story.uuid}))
        return response
    return story


@router.get("/{story_uuid}", response=StoryOut)
def get_story(request, story_uuid: UUID):
    story = Story.objects.get(uuid=story_uuid)
    if request.htmx:
        # TODO: Fix this
        return render(request, "cotton/stories/detail.html", {"story": story})
    return story


@router.patch("/{story_uuid}", response=StoryOut)
def update_story(request, story_uuid: UUID, payload: StoryIn):
    story = get_object_or_404(Story, uuid=story_uuid)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(story, attr, value)
    story.save()

    if request.htmx:
        # TODO: Add logic to detect autozave vs a generic update
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "update-story"
        return response
    return story


@router.delete("/{story_uuid}")
def delete_story(request, story_uuid: UUID):
    story = get_object_or_404(Story, uuid=story_uuid)
    story.delete()

    if request.htmx:
        response = HttpResponse("")
        response["HX-Trigger"] = "delete-story"
        return response
    return HttpResponse(status=204)


# Page
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
        response = render(request, "cotton/stories/page/index.html", context)
        response["HX-Trigger"] = "create-page"

        # Add OOB new button
        if page.order == 0:
            response = append_content(response, "cotton/stories/page/new_page_button.html", context, oob=True)

        # Update OOB move buttons
        for oob_page in story.pages.all():
            context["page"] = oob_page
            response = append_content(response, "cotton/stories/page/move_page_buttons.html", context, oob=True)
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

    context = {"story": story}
    if request.htmx:
        response = HttpResponse("")
        response["HX-Trigger"] = "delete-page"
        # Update OOB
        response = append_content(response, "cotton/stories/page/new_page_button.html", context, oob=True)
        for oob_page in story.pages.all():
            context["page"] = oob_page
            response = append_content(response, "cotton/stories/page/move_page_buttons.html", context, oob=True)
        return response

    return HttpResponse(status=204)


@router.post("/{story_uuid}/pages/{page_uuid}/move/{direction}", response=PageOut)
def move_page(request, story_uuid: UUID, page_uuid: UUID, direction: Literal["up", "down"]):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)

    if direction == "up":
        page.up()
    else:
        page.down()

    if request.htmx:
        return render(request, "cotton/stories/page/list.html", {"story": story})
    return page


@router.post("/{story_uuid}/pages/{page_uuid}/image", response=PageOut)
def upload_page_image(request, story_uuid: UUID, page_uuid: UUID, file: File[UploadedFile]):
    story = get_object_or_404(Story, uuid=story_uuid)
    page = get_object_or_404(Page, uuid=page_uuid, story=story)

    # Basic server-side validation (client-side already filters)
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types or file.size > 10 * 1024 * 1024:
        return HttpResponse("Invalid file", status=422)
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
