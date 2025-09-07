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

- [ ] **Verify `Page` Model Fields**
    - [ ] **File:** `apps/stories/models.py`
    - [ ] **Analysis:** The `Page` model already contains `image` and `image_generating` fields. No database migration is needed.
- [ ] **Add Image Generation Method to AIEngine**
    - [ ] **File:** `apps/ai/util/ai.py`
    - [ ] **Analysis:** The existing pattern for AI interactions is to add methods to the `AIEngine` class. Creating a separate `services.py` file would be inconsistent.
    - [ ] **Action:** Add a new method `generate_image(self, prompt: str) -> ContentFile | None` to the `AIEngine` class.
    - [ ] **Implementation Details:** This method will encapsulate the call to `litellm.image_generation`, download the image from the returned URL using `requests`, and return it as a Django `ContentFile`. This centralizes all `litellm` interactions.
- [ ] **Create Notification Service Function**
    - [ ] **File:** `apps/stories/services.py`.
    - [ ] **Analysis:** This follows the established pattern of creating a dedicated service function to update a model and send an SSE notification. Reusing the existing `get_page` event is an efficient approach.
    - [ ] **Action:** Add the function `set_page_image_and_notify(page: Page, image_file: ContentFile) -> None`.
- [ ] **Create Celery Task**
    - [ ] **File:** `apps/ai/tasks.py`.
    - [ ] **Analysis:** The plan correctly follows the existing pattern of using `@shared_task`, accepting a Pydantic payload, and calling services. The use of a `finally` block to reset the `image_generating` flag is a robust addition for this stateful operation.
    - [ ] **Action:** Add the function `generate_page_image_task(payload: PageJob)`.
    - [ ] **Refinement:** The task should return a string for logging/tracking, consistent with other tasks: `return f"job:{page.story.channel}:ai.page_image"`.
- [ ] **Create Ninja API Endpoint**
    - [ ] **File:** `apps/ai/api.py`.
    - [ ] **Analysis:** The plan correctly follows the project's pattern of using a Ninja endpoint to trigger a background job via `enqueue_job` and returning a 204 for HTMX requests.
    - [ ] **Action:** Add the endpoint decorated with `@router.post("/jobs/page/image/generate", name="generate_page_image")`.
    - [ ] **Refinement:** The call to `enqueue_job` must use `workflow="ai.page_image"` to match the Celery task name.

### Frontend

- [ ] **Locate the Page Component Template**
    - [ ] **Analysis:** The component is directory-based. The correct file to modify is `templates/cotton/stories/page/index.html`.
- [ ] **Add Image Generation Chip**
    - [ ] **File:** `templates/cotton/stories/page/index.html`.
    - [ ] **Analysis:** The plan to add a `<c-ai.chip>` with the specified HTMX attributes correctly follows the existing pattern for AI-triggered actions.
    - [ ] **Action:** Place the chip directly after the `<c-fields.image>` component, conditionally rendered with `{% if not page.image and not page.image_generating %}`.
- [ ] **Implement Loading and Final States**
    - [ ] **File:** `templates/cotton/stories/page/index.html`.
    - [ ] **Analysis:** The plan to use `htmx-indicator` for the loading state and rely on the existing `get_page` SSE event for the final UI update is correct and aligns with the project's architecture. This is an efficient use of existing patterns.
