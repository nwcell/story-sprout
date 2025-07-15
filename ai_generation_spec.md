# AI Content Generation Feature Specification

## 1. Feature Overview

This feature allows users to generate AI-powered content for story pages directly from the editing interface. When editing a page, users can click a "Generate with AI" button that triggers an asynchronous AI task. The system provides real-time UI feedback and inserts generated text upon completion.

## 2. User Experience (UX) Flow

1. **User enters edit mode:** User clicks to edit a `Page`'s content in the in-place editor
2. **Generate button appears:** Below the save/cancel button group, a "Generate with AI" button with magic wand icon is visible
3. **User clicks Generate:** Initiates AI content generation
4. **Loading state:** 
   - Generate button becomes disabled
   - Textarea becomes read-only to prevent concurrent edits
   - Spinner/loading indicator appears to show generation in progress
5. **AI generates content:** Background task executes using full story context
6. **Content appears:** Generated text replaces existing content in textarea, loading state clears
7. **Error handling:** If generation fails, show notification modal/bar and restore original content

## 3. Technical Architecture

### 3.1. Goals

Build an async AI layer for Story-Sprout that:
1. Queues AI work via DB-backed jobs (fault-tolerant, auditable)
2. Keeps domain ↔ ai dependencies one-way (stories ➜ ai)
3. Provides comprehensive context (all pages in story) for generation

### 3.2. Directory Structure

```
apps/
├─ stories/                     # Domain App
│  ├─ models.py                 # Story, Page models
│  ├─ services.py               # request_page_text(page, user) → AiJob
│  ├─ tasks.py                  # attach_result(job_id)
│  └─ views/admin               # call services.request_*()
│
└─ ai/                          # Infrastructure App
   ├─ models.py                 # AiJob model
   ├─ adapters/                 # SDK Shims
   │  └─ litellm.py             # LiteLLM adapter
   ├─ prompts/                  # Prompt Templates
   │  └─ page_content.jinja     # Page generation prompts
   ├─ workflows/                # Pure Python Orchestration
   │  └─ text.py                # generate(ctx) workflow
   ├─ tasks.py                  # run_ai_job(job_id) Celery task
   └─ queue.py                  # queue_ai_job(job_id)
```

### 3.3. Core Principles

- **One-way Dependencies:** Domain apps import `ai.queue` / `ai.models`, never the reverse
- **Pure Workflows:** `ai/workflows` and `ai/adapters` contain **no Django imports**
- **DB-backed Jobs:** All AI work tracked via `AiJob` model for fault tolerance and auditing
- **Filesystem Prompts:** Prompts managed as `.jinja` files under version control
- **Default Queue:** Use default Celery queue for CPU tasks (GPU queue reserved for future image work)

### 3.4. Design Rationale: Why Jinja2?

Jinja2 was chosen over Django templates for critical architectural reasons:

- **Framework Independence:** Keeps `ai/workflows` and `ai/adapters` free of Django dependencies
- **Context Complexity:** Cleanly handles iterating over all story pages and conditional logic
- **Maintainability:** Separates prompt structure from Python orchestration code

## 4. AiJob Model

The `AiJob` model serves as the central tracking mechanism for all AI operations:

```python
class AiJob(models.Model):
    # Core identification
    id = models.AutoField(primary_key=True)
    job_type = models.CharField(max_length=50)  # 'page_text_generation'
    status = models.CharField(max_length=20)    # 'pending', 'running', 'succeeded', 'failed'
    
    # Target object (generic foreign key)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # AI configuration
    template_key = models.CharField(max_length=100)  # 'page_content'
    template_version = models.CharField(max_length=20, default='1.0')
    model_name = models.CharField(max_length=100, default='gpt-4o')
    
    # Job data
    prompt_payload = models.JSONField()  # Context data for prompt rendering
    output_text = models.TextField(blank=True)
    
    # Usage tracking
    usage_tokens = models.IntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

## 5. Data & Task Flow

### 5.1. Complete Flow

1. **UI → Service:**
   ```python
   # User clicks generate button
   stories.services.request_page_text(page, user)
   ```

2. **Service Creates Job:**
   - Builds prompt context (all story pages, story title/description)
   - Creates `AiJob` with `status='pending'`
   - Uses `on_commit()` to queue job: `ai.queue.queue_ai_job(job.id)`

3. **Celery Task Execution:**
   ```python
   ai.tasks.run_ai_job(job_id)
   ```
   - Marks job as `running`
   - Calls workflow via adapter
   - Saves output/cost, sets status to `succeeded`/`failed`
   - Chains to `stories.tasks.attach_result(job_id)`

4. **Result Attachment:**
   ```python
   stories.tasks.attach_result(job_id)
   ```
   - Fetches Page via GenericFK
   - Updates `page.content = job.output_text`
   - Saves page

### 5.2. Context Building

**For Blank Pages (New Content):**
- Story title: `story.title`
- Story summary: `story.description`
- All existing pages: `story.pages.all().order_by('order')`
- Prompt focuses on creating new content

**For Existing Content (Revision):**
- Same context as above
- Current page content included
- Prompt instructs to "revise & redo this page"

### 5.3. Model Field Mapping

- **Story title:** `Story.title`
- **Story summary:** `Story.description`
- **Page content:** `Page.content`
- **Page ordering:** `Page.order` (from OrderedModel)

## 6. Component Implementation

### 6.1. Frontend (HTMX & Alpine.js)

**Generate Button Placement:**
- Location: Below save/cancel button group in in-place editor
- Icon: Magic wand or similar AI generation icon
- States: Normal, Loading (disabled + spinner), Error

**Loading State:**
- Textarea becomes read-only
- Generate button disabled with spinner
- Visual indication that generation is in progress

**Error Handling:**
- Show notification modal or banner on failure
- Restore original textarea content
- Re-enable editing capabilities

### 6.2. Backend Services

**stories/services.py:**
```python
def request_page_text(page: Page, user: User) -> AiJob:
    # Build context from all story pages
    # Create AiJob with context payload
    # Queue job for processing
    # Return job instance
```

**ai/queue.py:**
```python
def queue_ai_job(job_id: int):
    # Dispatch to Celery
    run_ai_job.delay(job_id)
```

**ai/tasks.py:**
```python
@shared_task
def run_ai_job(job_id: int):
    # Load job, mark running
    # Call workflow with context
    # Save results, update status
    # Chain to attach_result
```

### 6.3. Prompt Templates

**page_content.jinja:**
```jinja
You are a creative storyteller writing "{{ story_title }}".

{% if story_description %}
Story Summary: {{ story_description }}
{% endif %}

{% if existing_pages %}
Existing Pages:
{% for page in existing_pages %}
Page {{ page.order + 1 }}: {{ page.content }}
{% endfor %}
{% endif %}

{% if current_content %}
Current page content to revise:
{{ current_content }}

Please revise and improve this page content.
{% else %}
Please write the next page of this story.
{% endif %}
```

## 7. Testing

**Manual Testing:**
```python
# Django shell
from stories.services import request_page_text
from stories.models import Page
from django.contrib.auth import get_user_model

User = get_user_model()
page = Page.objects.get(pk=42)
user = User.objects.first()

job = request_page_text(page, user)
# Check Celery logs for job processing
# Verify page.content updated after completion
```

**Celery Worker:**
```bash
uv run celery -A core worker -Q default -l info
```

This specification provides a comprehensive plan for implementing DB-backed, fault-tolerant AI content generation with proper architectural separation and full story context.
