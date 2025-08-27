from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Story

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
