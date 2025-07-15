# AI Content Generation Feature Specification

## 1. Feature Overview

This feature allows users to generate content for a story's page directly from the editing interface. When a user is editing a page's content, they can click a "Generate" button. This action will trigger an asynchronous AI task to generate relevant text based on the story's context. The UI will provide real-time feedback (e.g., a loading spinner) and insert the generated text into the editor upon completion.

## 2. User Experience (UX) Flow

1.  **User enters edit mode:** The user clicks to edit the content of a `Page`.
2.  **"Generate" button appears:** Alongside the standard save/cancel buttons, a new "Generate with AI" button is visible.
3.  **User clicks "Generate":** The user clicks the button to initiate AI content generation.
4.  **Loading state:** The "Generate" button becomes disabled, and a loading indicator (spinner) appears next to it. The text area might become read-only to prevent concurrent edits.
5.  **AI generates content:** A background task is executed.
6.  **Content appears:** Once the task is complete, the generated text is inserted into the text area, replacing any existing content. The loading indicator disappears, and the button is re-enabled.

## 3. Technical Architecture

We will follow a clean, decoupled architecture that separates the domain logic (`stories`) from the infrastructure logic (`ai`).

### 3.1. Directory Structure

```
apps/
├─ stories/                     # Domain App
│  ├─ models.py                 # Story, Page models
│  ├─ tasks.py                  # New: attach_page_text Celery task
│  ├─ views.py                  # New: view to queue the AI task
│  └─ urls.py                   # New: URL for the queueing view
│
└─ ai/                          # Infrastructure App (No Django Models)
   ├─ adapters/                 # SDK Shims
   │  └─ litellm.py             # New: LiteLLM adapter
   ├─ prompts/                  # Prompt Templates
   │  └─ page_content.jinja     # New: Prompt for generating page content
   ├─ workflows/                # Pure Python Orchestration
   │  └─ text.py                # New: generate() workflow
   ├─ tasks/                    # Celery Task Definitions
   │  └─ text.py                # New: generate_page_text Celery task
   └─ __init__.py               # Public API for the AI app
```

### 3.2. Core Principles

-   **Dependency Inversion:** The `stories` app will depend on the `ai` app, but the `ai` app will have no knowledge of `stories`. This is crucial for modularity.
-   **Pure Workflows:** `ai/workflows` and `ai/adapters` will contain pure Python code with **no Django imports**. This makes them portable, independently testable, and framework-agnostic.
-   **Filesystem-based Prompts:** Prompts will be managed as `.jinja` files under version control, allowing for easy iteration and review.

### 3.3. Design Rationale: Why Jinja2 for Prompts?

While Django's templating engine is already in use, Jinja2 was chosen for the `ai` app for a critical reason: **decoupling**. 

- **Framework Independence:** The core architectural goal is to keep the `ai` app's workflows and adapters free of Django-specific code. Jinja2 is a standalone library, allowing us to render prompts in a pure Python environment without importing any Django components.
- **Handles Complexity:** Use cases like iterating over previous pages to build context are handled cleanly with Jinja2's loops and conditionals. This is difficult to manage with simple f-strings.
- **Maintainability:** Storing prompts in dedicated `.jinja` files keeps them organized and easy to edit, separating the prompt's structure from the Python orchestration code.

This choice enforces the desired architectural separation, ensuring the AI module remains portable and independently testable.

## 4. Data & Task Flow

The end-to-end process is orchestrated via a Celery chain.

1.  **UI (HTMX Request):** The user clicks the "Generate" button, which sends an `hx-post` request to a new Django view in the `stories` app (e.g., `/stories/page/42/generate-text/`).

2.  **`stories.views.queue_page_text_view`:**
    -   Receives the `page_id`.
    -   Calls the public API function: `ai.queue_page_text(page_id=42, user_id=1)`.
    -   Returns an HTTP 202 Accepted response to the client to indicate the task has started.

3.  **`ai.queue_page_text` (`ai/__init__.py`):**
    -   This function constructs and launches the Celery chain.
    -   **Chain:** `ai.tasks.text.generate_page_text` | `stories.tasks.attach_page_text`

4.  **Task 1: `ai.tasks.text.generate_page_text`:**
    -   **Input:** `page_id`, `user_id`.
    -   **Action:**
        -   Fetches the `Page` and `Story` objects to build context (this is the one exception where the `ai` task needs to know about a domain model ID).
        -   The context might include story title, summary, previous page content, etc.
        -   Calls the pure workflow: `ai.workflows.text.generate(context)`.
    -   **Output:** A dictionary containing the generated text: `{'generated_text': '...'}`. This task **does not** write to the database.

5.  **Task 2: `stories.tasks.attach_page_text`:**
    -   **Input:** The dictionary from the previous task.
    -   **Action:**
        -   Retrieves the `Page` object using its ID.
        -   Updates the `Page.content` field with `generated_text`.
        -   Saves the `Page` object.
    -   **Output:** None.

## 5. Component Breakdown

### 5.1. Frontend (HTMX & Alpine.js)

-   **`page_edit_form.html` (Partial Template):**
    -   The form will include a button:
        ```html
        <button hx-post="{% url 'stories:generate_page_text' page.id %}"
                hx-target="#page-content-editor" hx-swap="outerHTML"
                class="htmx-indicator:hidden">
            Generate with AI
        </button>
        <img src="/static/spinner.gif" class="htmx-indicator" />
        ```
    -   `hx-target` will point to the text area or its container.
    -   The `htmx-indicator` class will be used to show/hide the button and spinner during the request.

### 5.2. `stories` App

-   **`views.py`:**
    -   `generate_page_text_view(request, page_id)`: A new view that calls `ai.queue_page_text`.
-   **`urls.py`:**
    -   A new path: `path('page/<int:page_id>/generate-text/', views.generate_page_text_view, name='generate_page_text')`.
-   **`tasks.py`:**
    -   `attach_page_text(result_dict, page_id)`: New Celery task to update the database.

### 5.3. `ai` App

-   **`__init__.py`:**
    -   `queue_page_text(page_id, user_id)`: Creates and dispatches the Celery chain.
-   **`tasks/text.py`:**
    -   `generate_page_text(page_id, user_id)`: Celery task to orchestrate context building and call the workflow.
-   **`workflows/text.py`:**
    -   `generate(context: dict) -> str`: Pure Python function that loads the Jinja prompt, populates it with context, and calls the LiteLLM adapter.
-   **`adapters/litellm.py`:**
    -   A simple wrapper around `litellm.completion` for standardized calls.
-   **`prompts/page_content.jinja`:**
    -   A new prompt template, e.g.:
        ```jinja
        You are a creative assistant helping write a story titled "{{ story_title }}".
        The story summary is: {{ story_summary }}
        The previous page was: {{ previous_page_content }}

        Please write the next section of the story.
        ```

## 6. Celery Configuration

-   **Queues:** We will define a new queue named `cpu_tasks` for text generation.
    ```python
    # core/settings.py
    CELERY_TASK_QUEUES = {
        'default': {'exchange': 'default', 'routing_key': 'default'},
        'cpu_tasks': {'exchange': 'cpu_tasks', 'routing_key': 'cpu_tasks'},
    }
    CELERY_DEFAULT_QUEUE = 'default'
    ```
-   **Task Routing:** The `generate_page_text` task will be routed to the `cpu_tasks` queue.
    ```python
    # ai/tasks/text.py
    @shared_task(queue='cpu_tasks')
    def generate_page_text(...):
        # ...
    ```
-   **Worker Command:** A dedicated worker will be started to consume from this queue:
    ```bash
    uv run celery -A core worker -l info -Q cpu_tasks -n cpu_worker@%h
    ```

This specification provides a comprehensive plan for implementing the feature while adhering to best practices for building a scalable and maintainable AI-powered application.
