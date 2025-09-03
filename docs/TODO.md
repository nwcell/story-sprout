# TODO

This document outlines the implementation plan for the AI feature set, focusing on a user-story-driven approach.

---

## AI Implementation Plan

This plan adapts the "Signal, Stream, Swap" pattern to use an explicit `AIRequest` model, ensuring a robust and scalable architecture.

### User Story 1: As a user, I can trigger an AI content generation task for a page and see a loading indicator.

**Goal:** Initiate the AI workflow and provide immediate UI feedback.

- [ ] **Create the API Endpoint for AI Requests**
    - [x] In a new `apps/ai/api.py`, create a Ninja API router.
    - [ ] Add a `POST /ai/requests` endpoint.
    - [ ] This endpoint will create an `AIRequest` instance, linking it to the target object (e.g., a `Page`) and the user.

- [ ] **Implement the `post_save` Signal for `AIRequest`**
    - [ ] In `apps/ai/signals.py`, create a `post_save` signal receiver for the `AIRequest` model.
    - [ ] On `create`, the signal will dispatch the appropriate Celery task (e.g., `page_content_workflow`) based on `AIRequest.workflow_name`.

- [ ] **Update the Frontend to Trigger the AI Request**
    - [ ] Create an HTMX button that `POST`s to the new `/ai/requests` endpoint.
    - [ ] The endpoint will return a partial that shows a loading state (e.g., `Generating...`) and includes the SSE connection logic from the design document.

### User Story 2: As a user, I can see the AI-generated content stream into the UI in real-time.

**Goal:** Provide a live, streaming experience for the user.

- [ ] **Implement the SSE Streaming View**
    - [ ] In `apps/ai/api.py`, create an endpoint `GET /ai/requests/{request_uuid}/stream`.
    - [ ] This view will use `StreamingHttpResponse` to send Server-Sent Events.
    - [ ] It will listen to a Redis channel (e.g., `ai_request_{request_uuid}`) for updates from the Celery task.

- [ ] **Modify the Celery Task to Stream Content**
    - [ ] In `apps/ai/tasks.py`, update `page_content_workflow` to accept an `AIRequest` ID.
    - [ ] Use `litellm.completion(..., stream=True)`.
    - [ ] As chunks are received from the AI model, publish them to the Redis channel.
    - [ ] Publish a special `event: close` message upon completion.

### User Story 3: As a user, the UI seamlessly updates with the final content once generation is complete.

**Goal:** Finalize the workflow and replace the temporary streaming content with the persistent data.

- [ ] **Finalize the AI Workflow in the Celery Task**
    - [ ] After the stream is complete, save the full generated text to the target model (e.g., `page.content`).
    - [ ] Update the `AIRequest` status to `SUCCESS` and store the final output.

- [ ] **Implement the Final Swap on the Frontend**
    - [ ] The HTMX partial will listen for the `sse:close` event.
    - [ ] On `close`, it will trigger a `GET` request to an endpoint that returns the final, rendered content for the target object.
    - [ ] This new content will replace the streaming container via `hx-swap="outerHTML"`.

---

## Low Priority

- [ ] Migrate to Bubble UI
- [ ] Migrate to locally building Tailwind
- [ ] Clean up Marketing site codebase & make presentable
- [ ] Deploy to Digital Ocean
