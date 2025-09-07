# Page Image Generation: Detailed Implementation Plan

## 1. Objective & User Story

*   **Objective:** To provide a simple, one-click method for a user to generate a single image for a story page based on its content, following the existing architectural pattern of AI-powered suggestion chips.
*   **User Story:** "As a user, I want to click a 'Generate Image' chip on a page, so that I can quickly create and add an illustration based on the page's `image_text` content."

## 2. High-Level Workflow

1.  **UI:** A user clicks the "✨ Generate Image" chip on a story page.
2.  **HTMX Request:** The chip sends an `hx-post` request to a new Ninja API endpoint.
3.  **API Endpoint:** The endpoint validates the request and enqueues a Celery background task.
4.  **Celery Task:** The task calls an image generation service (LiteLLM), saves the resulting image to the `Page` model, and triggers an SSE event.
5.  **SSE Notification:** The browser receives the event and triggers a final HTMX request to refresh the image container.

## 3. Implementation Checklist

### Backend

- [x] **Verify `Page` Model Fields** ✅ **COMPLETE**
    - [x] **File:** `apps/stories/models.py`
    - [x] **Analysis:** The `Page` model already contains `image` and `image_generating` fields. No database migration is needed.
- [x] **Add Image Generation Method to AIEngine** ✅ **COMPLETE**
    - [x] **File:** `apps/ai/util/ai.py`
    - [x] **Analysis:** The existing pattern for AI interactions is to add methods to the `AIEngine` class. Creating a separate `services.py` file would be inconsistent.
    - [x] **Action:** Add a new method `generate_image(self, prompt: str) -> ContentFile | None` to the `AIEngine` class.
    - [x] **Implementation Details:** 
        - Use OpenAI's image generation API (DALL-E) via `litellm.image_generation`
        - Model: `dall-e-3` (or `dall-e-2` as fallback)
        - Size: `1024x1024` (standard square format)
        - Quality: `standard` (to keep costs reasonable)
        - Download image from returned URL using `requests.get()`
        - Return as Django `ContentFile` with filename based on timestamp
        - Add basic error handling (return `None` on failure for now)
- [x] **Verify Notification Service Function** ✅ **COMPLETE**
    - [x] **File:** `apps/stories/services.py`.
    - [x] **Analysis:** The function `set_page_image_and_notify(page: Page, image_file) -> None` already exists and follows the correct SSE pattern.
    - [x] **Action:** ✅ **COMPLETE** - No changes needed. The function sends `get_page_image#{page.uuid}` event which will trigger the SSE listener.
- [x] **Create Celery Task** ✅ **COMPLETE**
    - [x] **File:** `apps/ai/tasks.py`.
    - [x] **Analysis:** Follow the established pattern with `@shared_task(name="ai.page_image", base=JobTask)` decorator.
    - [x] **Action:** Add the function `generate_page_image_task(payload: PageJob)`.
    - [x] **Implementation Details:**
        - Set `page.image_generating = True` at start
        - Use `page.image_text` as the prompt for image generation
        - Call `ai.generate_image(page.image_text)`
        - If successful, call `set_page_image_and_notify(page, image_file)`
        - Use `finally` block to reset `page.image_generating = False`
        - Return `f"job:{page.story.channel}:ai.page_image"`
        - Import `set_page_image_and_notify` from `apps.stories.services`
- [x] **Create Ninja API Endpoint** ✅ **COMPLETE**
    - [x] **File:** `apps/ai/api.py`.
    - [x] **Analysis:** Follow the established pattern of other AI endpoints in the file.
    - [x] **Action:** Add the endpoint decorated with `@router.post("/jobs/page/image/generate", name="generate_page_image")`.
    - [x] **Implementation Details:**
        - Function signature: `def ai_page_image_generate(request, payload: PageJob) -> JobStatus:`
        - Use `enqueue_job(user=request.user, workflow="ai.page_image", payload=payload)`
        - Return `HttpResponse(status=204)` for HTMX requests
        - Return `{"job_uuid": str(job.uuid), "status": job.status}` for non-HTMX
        - Add logging: `logger.info(f"ai_page_image_generate received: {payload}")`

### Frontend

- [x] **Locate the Page Component Template** ✅ **COMPLETE**
    - [x] **Analysis:** The component is directory-based. The correct file to modify is `templates/cotton/stories/page/index.html`.
- [x] **Add Image Generation Chip** ✅ **COMPLETE**
    - [x] **File:** `templates/cotton/stories/page/index.html`.
    - [x] **Analysis:** Follow the exact pattern of existing AI chips (lines 20-26, 32-38).
    - [x] **Action:** Add chip after the `<c-fields.image>` component (after line 44).
    - [x] **Implementation Details:**
        - Conditional rendering: `{% if not page.image and not page.image_generating %}`
        - Chip attributes:
          ```html
          <c-ai.chip name="ai-chip"
                     type="button"
                     emoji="✨"
                     color="purple"
                     hx-post="{% url 'api-1:ai_page_image_generate' %}"
                     hx-ext='json-enc'
                     hx-vals='{"page_uuid": "{{ page.uuid }}"}'>Generate Image</c-ai.chip>
          ```
- [x] **Add SSE Listener for Image Updates** ✅ **COMPLETE**
    - [x] **File:** `templates/cotton/stories/page/index.html`.
    - [x] **Analysis:** Need to add SSE listener to automatically refresh the image component when generation completes.
    - [x] **Action:** Add SSE listener before the `<c-fields.image>` component (around line 41).
    - [x] **Implementation Details:**
        - Add: `<c-htmx.sse hx-get="{% url 'api-1:get_page_image' story_uuid=story.uuid page_uuid=page.uuid %}" event="get_page_image" key="{{ page.uuid }}" />`
        - This will listen for `get_page_image#{page.uuid}` events sent by the service function
        - Requires creating the `get_page_image` API endpoint that returns just the image component

- [x] **Create Image Component API Endpoint** ✅ **COMPLETE**
    - [x] **File:** `apps/stories/api.py` 
    - [x] **Analysis:** Need endpoint for SSE to refresh just the image component.
    - [x] **Action:** Add `get_page_image` endpoint that renders only the `<c-fields.image>` component.
    - [x] **Implementation Details:**
        - URL pattern: `api/stories/{story_uuid}/pages/{page_uuid}/image/`
        - Return rendered `<c-fields.image>` component with updated image data
        - Include the generate chip if no image and not generating
        - Created template: `templates/cotton/stories/page/image_component.html`

## 4. Review Questions & Clarifications Needed

### Image Generation API Configuration
- **Q:** Is LiteLLM configured for image generation in your project?
- **A:** we have openai wired up.  use openai's image model for now.  we might need to add a manager, or an alternative model attribute for images.

- **Q:** What image generation model/provider are you planning to use (DALL-E, Stable Diffusion, etc.)?
- **A:** use openai's image model for now.

- **Q:** Are the necessary API keys configured?
- **A:** yes.

### Template Structure & Consistency
- **Q:** What does the current page component structure look like in `templates/cotton/stories/page/index.html`?
- **A:** answer this yourself

- **Q:** Are there existing AI chip examples I should follow for consistency?
- **A:** Yes, you can clearly see them in the codebase.  look for "suggest"

### Error Handling & State Management
- **Q:** How should we handle failed image generation?
- **A:** don't worry about it for now.  we'll eventually add an error system.

- **Q:** Should we store error states or just silently fail?
- **A:** don't worry about it for now.  we'll eventually add an error system.

- **Q:** What happens if the user clicks the chip multiple times?
- **A:** don't worry about it for now.

### Image Storage & Processing
- **Q:** What's the expected image format and size?
- **A:** pick something that works.

- **Q:** Should we implement any image optimization or resizing?
- **A:** don't worry about it for now.

- **Q:** How do we handle the temporary download and file naming?
- **A:** we should be popping it into the database pretty quickly.  if you have any suggestions, let me know.

### Implementation Priority
- **Q:** Should I proceed with implementation after you answer these questions, or do you want to review the approach first?
- **A:** No, update the checklist first and then seek my approval before proceeding.
