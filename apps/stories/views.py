from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Page, Story

# https://github.com/spookylukey/django-htmx-patterns/blob/master/inline_partials.rst


@login_required
@require_http_methods(["GET"])
def stories(request):
    # Get stories for the logged-in user, ordered by most recently updated
    stories = Story.objects.filter(user=request.user).order_by("-updated_at")

    context = {"stories": stories}

    return render(request, "stories/index.html", context)


@login_required
@require_http_methods(["GET"])
def story_detail(request, story_uuid):
    """New componentized version of the story detail view."""
    # Get the story by UUID
    story = get_object_or_404(Story, uuid=story_uuid)

    # Prefetch pages for efficiency
    story = Story.objects.prefetch_related("pages").get(uuid=story_uuid)

    # Check if the user has permission to view this story
    if story.user != request.user:
        raise Http404("Story not found")

    context = {"story": story}

    return render(request, "stories/detail.html", context)


@login_required
@require_http_methods(["POST"])
def move_page(request, page_id, direction):
    page = get_object_or_404(Page, id=page_id)
    story = page.story

    # Security check - ensure the user owns the story
    if story.user != request.user:
        raise Http404("Page not found")

    # Use django-ordered-model's built-in up() or down() method
    if direction == "up":
        page.up()
    else:
        page.down()

    # Return all pages for the story in the new order
    pages = story.pages.all()

    context = {"story": story, "pages": pages}
    return render(request, "stories/partials/pages_list.html", context)


@login_required
@require_http_methods(["GET"])
def story_detail_old(request, story_uuid):
    # Get the story by UUID
    story = get_object_or_404(Story, uuid=story_uuid)

    # Check if the user has permission to view this story
    if story.user != request.user:
        raise Http404("Story not found")

    # Get the pages ordered by the OrderedModel's order field
    pages = story.pages.all()

    # Process pages: add first/last flags and prepare content_draft for display
    for page in pages:
        # If magic mode is active, prepare draft content for display
        if page.content_generating and page.content_draft is not None:
            # Create a temporary copy for template display
            page.display_content = page.content_draft
        else:
            page.display_content = page.content

    context = {"story": story, "pages": pages}

    return render(request, "stories/story_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def new_story(request):
    if request.method == "POST":
        # Process form submission
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Create new story
        if title and description:  # Basic validation
            story = Story.objects.create(title=title, description=description, user=request.user)
            # Redirect to the newly created story
            return redirect(reverse("stories:story_detail", kwargs={"story_uuid": story.uuid}))

    # Display new story form
    return render(request, "stories/new_story.html")


# HTMX Views for In-Place Editing


@login_required
def get_story_title(request, story_uuid):
    """HTMX endpoint to get the display version of a story's title."""
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    return render(request, "stories/partials/story_title.html", {"story": story})


@login_required
def get_story_description(request, story_uuid):
    """HTMX endpoint to get the display version of a story's description."""
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    return render(request, "stories/partials/story_description.html", {"story": story})


@login_required
def edit_story_title(request, story_uuid):
    """HTMX endpoint for editing story title"""
    if not request.htmx:
        return HttpResponseBadRequest()

    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)

    if request.method == "POST":
        # Update title
        title = request.POST.get("title", "").strip()
        if title:
            story.title = title
            story.save()
        return render(request, "stories/partials/story_title.html", {"story": story, "editing": False})

    # Show edit form
    return render(request, "stories/partials/story_title_form.html", {"story": story})


@login_required
def edit_story_description(request, story_uuid):
    """HTMX endpoint for editing story description"""
    if not request.htmx:
        return HttpResponseBadRequest()

    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)

    if request.method == "POST":
        story.description = request.POST.get("description", "").strip()
        story.save()
        return render(request, "stories/partials/story_description.html", {"story": story, "editing": False})

    return render(request, "stories/partials/story_description_form.html", {"story": story})


@login_required
def get_page_content(request, page_id):
    """HTMX endpoint to get the display version of a page's content."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    editing = request.GET.get("editing") == "true"

    if editing or page.content_generating:
        if page.content_generating and page.content_draft is not None:
            page.display_content = page.content_draft
        return render(request, "stories/partials/page_content_form.html", {"page": page})

    return render(request, "stories/partials/page_content.html", {"page": page})


@login_required
def edit_page_content(request, page_id):
    """HTMX endpoint for editing page content"""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        content_generating = request.POST.get("content_generating") == "true"

        if not content_generating:
            page.content = content
            page.content_draft = None
        else:
            page.content_draft = content

        page.content_generating = content_generating
        page.save(update_fields=["content", "content_draft", "content_generating"])

        if content_generating and page.content_draft:
            page.display_content = page.content_draft
            return render(request, "stories/partials/page_content_form.html", {"page": page})
        return render(request, "stories/partials/page_content.html", {"page": page})

    # GET request
    if page.content_generating and page.content_draft is not None:
        page.display_content = page.content_draft
    return render(request, "stories/partials/page_content_form.html", {"page": page})


@login_required
def toggle_content_generating(request, page_id):
    """Toggle the content generating flag and handle draft content."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    was_generating = page.content_generating
    current_content = request.POST.get("content", "").strip()

    if not page.content_generating:
        page.content_draft = current_content
        page.content_generating = True
    else:
        if page.content_draft:
            page.content = page.content_draft
        page.content_draft = None
        page.content_generating = False

    page.save(update_fields=["content", "content_draft", "content_generating"])

    if page.content_generating and page.content_draft:
        page.display_content = page.content_draft

    template = "stories/partials/page_content.html" if was_generating else "stories/partials/page_content_form.html"
    return render(request, template, {"page": page})


@login_required
def check_content_generating_status(request, page_id):
    """Check if a page is still in content_generating mode for HTMX polling."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    if not page.content_generating:
        return render(request, "stories/partials/page_content.html", {"page": page})
    return HttpResponse(status=204)


@login_required
def add_page(request, story_uuid):
    """HTMX endpoint for adding a new page"""
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest()

    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)

    # Create new page
    page = Page.objects.create(story=story, content="Click to edit content...")

    return render(request, "stories/partials/page_item.html", {"page": page})


@login_required
def delete_page(request, page_id):
    """HTMX endpoint for deleting a page"""
    if not request.htmx or request.method != "DELETE":
        return HttpResponseBadRequest()

    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    page.delete()

    # Return empty response for removal
    return HttpResponse("")


@login_required
def get_page_image_text(request, page_id):
    """HTMX endpoint to get the display version of a page's image text."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    return render(request, "stories/partials/page_image_text.html", {"page": page})


@login_required
def edit_page_image_text(request, page_id):
    """HTMX endpoint for showing the edit form for page image text"""
    if not request.htmx:
        return HttpResponseBadRequest()

    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    # Show edit form
    return render(request, "stories/partials/page_image_text_form.html", {"page": page})


@login_required
def update_page_image_text(request, page_id):
    """HTMX endpoint for saving updated page image text"""
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest()

    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    # Update image text
    image_text = request.POST.get("image_text", "").strip()
    page.image_text = image_text
    page.save()

    return render(request, "stories/partials/page_image_text.html", {"page": page})


@login_required
def upload_page_image(request, page_id):
    """HTMX endpoint for rendering and uploading a page image"""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    # Handle GET request - just render the component
    if request.method == "GET" and request.htmx:
        return render(request, "stories/partials/page_image_container.html", {"page": page})

    # Handle POST request - process image upload
    if request.method == "POST" and request.FILES.get("image"):
        # Delete old image if it exists
        if page.image:
            page.image.delete(save=False)

        # Save new image
        page.image = request.FILES["image"]
        page.save()

        # Render the updated image container
        html = render_to_string("stories/partials/page_image_container.html", {"page": page}, request=request)

        # Return JSON response with success status and the HTML for the container
        return JsonResponse({"success": True, "html": html})

    # Handle invalid requests
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_page_image(request, page_id):
    """HTMX endpoint for deleting a page image"""
    if not request.htmx:
        return HttpResponseBadRequest()

    page = get_object_or_404(Page, id=page_id, story__user=request.user)

    # Delete the image
    if page.image:
        page.image.delete()

    # Return the empty image container
    return render(request, "stories/partials/page_image_container.html", {"page": page})
