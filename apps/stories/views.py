from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Story, Page

# Create your views here.

@login_required
@require_http_methods(['POST'])
def move_page_up(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    story = page.story
    
    # Security check - ensure the user owns the story
    if story.user != request.user:
        raise Http404("Page not found")
    
    # Use django-ordered-model's built-in up() method
    page.up()
    
    # Return all pages for the story in the new order
    pages = story.pages.all()
    
    # Add first/last flags for each page
    for i, p in enumerate(pages):
        p.is_first = i == 0
        p.is_last = i == len(pages) - 1
    
    context = {'story': story, 'pages': pages}
    return render(request, 'stories/partials/pages_list.html', context)

@login_required
@require_http_methods(['POST'])
def move_page_down(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    story = page.story
    
    # Security check - ensure the user owns the story
    if story.user != request.user:
        raise Http404("Page not found")
    
    # Use django-ordered-model's built-in down() method
    page.down()
    
    # Return all pages for the story in the new order
    pages = story.pages.all()
    
    # Add first/last flags for each page
    for i, p in enumerate(pages):
        p.is_first = i == 0
        p.is_last = i == len(pages) - 1
    
    context = {'story': story, 'pages': pages}
    return render(request, 'stories/partials/pages_list.html', context)


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
    
    # Process pages: add first/last flags and prepare content_draft for display
    for i, page in enumerate(pages):
        page.is_first = i == 0
        page.is_last = i == len(pages) - 1
        
        # If magic mode is active, prepare draft content for display
        if page.content_generating and page.content_draft is not None:
            # Create a temporary copy for template display
            page.display_content = page.content_draft
        else:
            page.display_content = page.content
    
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

# HTMX Views for In-Place Editing

@login_required
def get_story_title(request, story_uuid):
    """HTMX endpoint to get the display version of a story's title."""
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    return render(request, 'stories/partials/story_title.html', {'story': story})


@login_required
def get_story_description(request, story_uuid):
    """HTMX endpoint to get the display version of a story's description."""
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    return render(request, 'stories/partials/story_description.html', {'story': story})


@login_required
def edit_story_title(request, story_uuid):
    """HTMX endpoint for editing story title"""
    if not request.htmx:
        return HttpResponseBadRequest()
    
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    
    if request.method == 'POST':
        # Update title
        title = request.POST.get('title', '').strip()
        if title:
            story.title = title
            story.save()
        return render(request, 'stories/partials/story_title.html', {
            'story': story, 'editing': False
        })
    
    # Show edit form
    return render(request, 'stories/partials/story_title_form.html', {
        'story': story
    })

@login_required
def edit_story_description(request, story_uuid):
    """HTMX endpoint for editing story description"""
    if not request.htmx:
        return HttpResponseBadRequest()
    
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    
    if request.method == 'POST':
        # Update description
        description = request.POST.get('description', '').strip()
        story.description = description
        story.save()
        return render(request, 'stories/partials/story_description.html', {
            'story': story, 'editing': False
        })
    
    # Show edit form
    return render(request, 'stories/partials/story_description_form.html', {
        'story': story
    })

@login_required
def get_page_content(request, page_id):
    """HTMX endpoint to get the display version of a page's content."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    editing = request.GET.get('editing') == 'true'
    
    # If explicitly requesting editing form or content is generating
    if editing or page.content_generating:
        # Prepare context for template
        context = {'page': page}
        
        # Show draft content in the textarea if magic mode is active
        if page.content_generating and page.content_draft is not None:
            # Set display_content for the template
            page.display_content = page.content_draft
        
        return render(request, 'components/editable_content_form.html', context)
    
    # Otherwise show the display view
    return render(request, 'components/editable_content.html', {
        'page': page
    })

@login_required
def edit_page_content(request, page_id):
    """HTMX endpoint for editing page content"""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        content_generating = request.POST.get('content_generating') == 'true'
        
        if not content_generating:
            page.content = content
            page.content_draft = None
        else:
            page.content_draft = content
            
        page.content_generating = content_generating
        page.save(update_fields=['content', 'content_draft', 'content_generating'])
        
        # If magic mode is active, return the form with draft content
        if content_generating:
            # Set display_content for the template
            if page.content_draft is not None:
                page.display_content = page.content_draft
            return render(request, 'components/editable_content_form.html', {'page': page})
        
        # Otherwise return the display view
        return render(request, 'components/editable_content.html', {'page': page})
    
    # If not POST, just get the content (same as get_page_content with editing=true)
    if page.content_generating and page.content_draft is not None:
        page.display_content = page.content_draft
    return render(request, 'components/editable_content_form.html', {'page': page})

@login_required
def toggle_content_generating(request, page_id):
    """Toggle the content generating flag and handle draft content."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    current_content = request.POST.get('content', '').strip()
    
    if not page.content_generating:
        # Switching from normal mode to magic mode - save current as draft
        page.content_draft = current_content
        page.content_generating = True
    else:
        # Switching from magic mode to normal mode - commit draft to content
        if page.content_draft:
            page.content = page.content_draft
        page.content_draft = None
        page.content_generating = False
        
    page.save(update_fields=['content', 'content_draft', 'content_generating'])
    
    # Set display_content for the template if in magic mode
    if page.content_generating and page.content_draft is not None:
        page.display_content = page.content_draft
        
    # Return the form - it will handle showing disabled controls in magic mode
    return render(request, 'components/editable_content_form.html', {'page': page})

@login_required
def add_page(request, story_uuid):
    """HTMX endpoint for adding a new page"""
    if not request.htmx or request.method != 'POST':
        return HttpResponseBadRequest()
    
    story = get_object_or_404(Story, uuid=story_uuid, user=request.user)
    
    # Create new page
    page = Page.objects.create(
        story=story,
        content="Click to edit content..."
    )
    
    return render(request, 'stories/partials/page_item.html', {
        'page': page
    })

@login_required
def delete_page(request, page_id):
    """HTMX endpoint for deleting a page"""
    if not request.htmx or request.method != 'DELETE':
        return HttpResponseBadRequest()
    
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    page.delete()
    
    # Return empty response for removal
    return HttpResponse("")

@login_required
def get_page_image_text(request, page_id):
    """HTMX endpoint to get the display version of a page's image text."""
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    return render(request, 'stories/partials/page_image_text.html', {'page': page})

@login_required
def edit_page_image_text(request, page_id):
    """HTMX endpoint for showing the edit form for page image text"""
    if not request.htmx:
        return HttpResponseBadRequest()
    
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    
    # Show edit form
    return render(request, 'stories/partials/page_image_text_form.html', {
        'page': page
    })

@login_required
def update_page_image_text(request, page_id):
    """HTMX endpoint for saving updated page image text"""
    if not request.htmx or request.method != 'POST':
        return HttpResponseBadRequest()
    
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    
    # Update image text
    image_text = request.POST.get('image_text', '').strip()
    page.image_text = image_text
    page.save()
    
    return render(request, 'stories/partials/page_image_text.html', {
        'page': page
    })

@login_required
def upload_page_image(request, page_id):
    """AJAX/HTMX endpoint for uploading a page image"""
    if request.method != 'POST' or not request.FILES.get('image'):
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
    
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    
    # Delete old image if it exists
    if page.image:
        page.image.delete(save=False)
    
    # Save new image
    page.image = request.FILES['image']
    page.save()
    
    # Render the updated image container
    html = render_to_string('stories/partials/page_image_container.html', {
        'page': page
    }, request=request)
    
    # Return JSON response with success status and the HTML for the container
    return JsonResponse({
        'success': True,
        'html': html
    })

@login_required
@require_http_methods(['DELETE'])
def delete_page_image(request, page_id):
    """HTMX endpoint for deleting a page image"""
    if not request.htmx:
        return HttpResponseBadRequest()
    
    page = get_object_or_404(Page, id=page_id, story__user=request.user)
    
    # Delete the image
    if page.image:
        page.image.delete()
    
    # Return the empty image container
    return render(request, 'stories/partials/page_image_container.html', {
        'page': page
    })
