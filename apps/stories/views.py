from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.urls import reverse
from .models import Story

# Create your views here.

@login_required
@require_http_methods(['GET'])
def stories(request):
    # Get stories for the logged-in user, ordered by most recently updated
    user_stories = Story.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'user_stories': user_stories
    }
    
    return render(request, 'stories/stories.html', context)

@login_required
@require_http_methods(['GET'])
def story_detail(request, story_uuid):
    # Get the story by UUID
    story = get_object_or_404(Story, uuid=story_uuid)
    
    # Check if the user has permission to view this story
    if story.user != request.user:
        raise Http404("Story not found")
    
    # Get the pages ordered by the OrderedModel's order field
    pages = story.pages.all()
    
    context = {
        'story': story,
        'pages': pages
    }
    
    return render(request, 'stories/story_detail.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def new_story(request):
    if request.method == 'POST':
        # Process form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        # Create new story
        if title and description:  # Basic validation
            story = Story.objects.create(
                title=title,
                description=description,
                user=request.user
            )
            # Redirect to the newly created story
            return redirect(reverse('stories:story_detail', kwargs={'story_uuid': story.uuid}))
    
    # Display new story form
    return render(request, 'stories/new_story.html')
