# AI Agent Architecture and Integration Analysis

This document provides a thorough analysis of the experimental AI agent developed in `notebooks/agent_01.py` and outlines a strategy for integrating it into the Story Sprout application, following best practices derived from the `pydantic-ai` documentation.

## 1. Initial Analysis

The `agent_01.py` notebook demonstrates a powerful proof-of-concept. It successfully combines an LLM (OpenAI's GPT-4o) with a set of tools that can query the Django database and generate images (using Google's Gemini). This establishes the core functionality required for a generic agent capable of working on stories.

However, the current implementation is a script designed for a notebook environment. Integrating it into the main web application requires significant architectural changes to ensure it is scalable, maintainable, secure, and decoupled from the web layer.

### Key Observations:

- **Data Models:** The agent uses Python's `dataclasses` for dependency injection (`Dependencies`) and data structures (`Page`). While functional, this is not aligned with the `pydantic-ai` library's core, which is built on Pydantic `BaseModel`.
- **Direct DB Access:** Tool functions like `get_story` and `get_page` directly use the Django ORM (`Story.objects.get`). This tightly couples the agent's tools to the database layer, bypassing any service or business logic layers.
- **Hardcoded Configuration:** The agent's model (`openai:gpt-4o`), system prompt, and other settings are hardcoded. This makes it inflexible and difficult to manage.
- **Synchronous Operations:** The tool functions are a mix of `async` and synchronous code. The image generation tool appears to be synchronous, which could block the event loop if run in an async context.
- **Environment Coupling:** The agent relies on a running Django environment to be imported and used, which is not ideal for a decoupled, scalable architecture.

## 2. Questions & Iterative Answers

To refine the integration strategy, let's explore some critical questions.

**Question 1: Why use Pydantic `BaseModel` instead of `dataclasses`?**

*Answer:* The `pydantic-ai` library is fundamentally designed to leverage Pydantic's features. While it may have some compatibility with `dataclasses`, using `BaseModel` is the idiomatic approach. It provides:
    - **Robust Validation:** Pydantic models perform data validation, coercion, and provide clear error messages out-of-the-box.
    - **Serialization Control:** Pydantic offers powerful control over serialization to and from JSON, which is crucial for API boundaries and Celery task arguments.
    - **Ecosystem Integration:** The entire `pydantic-ai` ecosystem, including `RunContext` and `ToolReturn`, is optimized for Pydantic models.
    - **Clearer Schema Definition:** Pydantic is the de-facto standard for defining data schemas in modern Python applications, making the code more understandable for developers.

**Question 2: What is the risk of tools accessing the database directly?**

*Answer:* Direct database access from agent tools presents several risks:
    - **Security:** It bypasses permission checks and business logic that would normally be enforced in a service layer. An LLM could potentially find a way to call tools with unintended parameters, leading to data exposure or corruption.
    - **Maintainability:** If the database schema changes, you would need to update the agent's tools directly. A service layer provides a stable interface that isolates the agent from backend changes.
    - **Scalability:** It requires the agent to run in a process that has direct database access. In a scalable architecture, agents should be stateless workers that communicate with the application via a well-defined API, not a direct database connection.

**Question 3: How should the agent be invoked and managed within the Django application?**

*Answer:* The agent should not run within the Django web process (e.g., in a view). Doing so would block the web server and lead to timeouts for any non-trivial task. The correct approach is to use a background task queue like Celery.

- **Workflow:**
    1. A user action in the frontend triggers a Django view.
    2. The view validates the request and dispatches a Celery task (e.g., `run_agent_on_story`).
    3. A Celery worker picks up the task, initializes the agent, and executes the run.
    4. During the run, the agent can use tools that make secure API calls back to the Django application to fetch data or perform actions.
    5. The result of the agent's run is stored, and the user is notified (e.g., via Server-Sent Events or a webhook).

**Question 4: How do we provide real-time feedback to the user while the agent is running?**

*Answer:* Long-running agent tasks require a mechanism to push updates to the client. The project already has `django-eventstream` set up, which is perfect for this.

- **Implementation:**
    - The Celery task that runs the agent should be given a unique channel ID.
    - As the agent progresses (e.g., starts a tool, finishes a step), the Celery task publishes events to that channel using `django_eventstream.send_event`.
    - The frontend listens to this event stream and updates the UI in real-time (e.g., showing a spinner, logging progress messages, displaying generated images as they arrive).

## 3. Checklist for Optimizing `agent_01.py`

This checklist focuses on refactoring the notebook code to follow pydantic-ai best practices before integrating it.

- [x] **Use Correct Data Structures**
    - [x] Keep `@dataclass` for `Dependencies` and `ImageDependencies` (per [pydantic-ai dependencies docs](https://ai.pydantic.dev/dependencies/#defining-dependencies))
    - [x] Remove the `Page` dataclass, as `PageSchema` already serves this purpose.

- [ ] **Follow Tool Function Patterns**
    - [ ] Ensure all tools use `@agent.tool` decorator and accept `RunContext[Dependencies]` as first parameter (per [tools documentation](https://ai.pydantic.dev/tools/#registering-via-decorator))
    - [ ] Keep Django ORM calls in tool functions - tools are meant to perform I/O operations directly (see [weather agent example](https://ai.pydantic.dev/examples/weather-agent/))
    - [ ] Ensure all I/O-bound tool functions are `async`

- [ ] **Proper Dependency Management**
    - [ ] Dependencies can contain runtime objects like `GoogleClient` - this is the intended pattern (see [weather agent with AsyncClient](https://ai.pydantic.dev/examples/weather-agent/))
    - [ ] Initialize clients once and pass them through dependencies for efficiency

- [ ] **Agent Configuration**
    - [ ] Move the agent's definition (`Agent(...)`) into a dedicated factory function or class for reusability
    - [ ] Externalize the `system_prompt` and `model` name into Django settings or a database model

## 4. Action Plan for Application Integration

This plan outlines the steps to build a generic, reusable AI agent feature within the Story Sprout application.

- [ ] **Phase 1: Create a Decoupled AI App**
    - [ ] Create a new Django app: `apps/agents`.
    - [ ] Define Pydantic models for agent configuration and invocation in `apps/agents/schemas.py`.
    - [ ] Create an `apps/agents/services.py` to contain the logic for initializing and running agents.
    - [ ] Implement a factory function in `services.py` to construct an agent with a specific configuration (model, prompt, tools).

- [ ] **Phase 2: Implement Agent as a Celery Task**
    - [ ] Create `apps/agents/tasks.py`.
    - [ ] Define a Celery task `run_agent_task(story_uuid: UUID, prompt: str, user_id: int)`.
    - [ ] Inside the task, use the service from `apps/agents/services.py` to get an agent instance and run it.
    - [ ] The task should handle agent execution, including passing dependencies and processing results.

- [ ] **Phase 3: Secure Tooling with an API Layer**
    - [ ] Create a dedicated API endpoint for agent tools (e.g., `/api/v1/agent-tools/`). This could use Django Ninja or DRF for structure and validation.
    - [ ] **Sub-checklist for Tool API:**
        - [ ] Create an endpoint for `get_story` that takes a UUID and returns `StorySchema` JSON. This endpoint must enforce permissions (i.e., the user associated with the agent run must own the story).
        - [ ] Create an endpoint for `get_page`.
        - [ ] Create an endpoint for `generate_image`. This endpoint should internally call the Google API and handle saving the resulting image.
    - [ ] Refactor the agent's `FunctionToolset` to call these new API endpoints instead of accessing the database directly. The tools will now be simple `httpx` API calls.

- [ ] **Phase 4: Frontend Integration**
    - [ ] Create a new UI component in the story editor for interacting with the agent (e.g., a chat-like interface).
    - [ ] The UI should POST to a new Django view (e.g., `/stories/<uuid>/agent/invoke/`).
    - [ ] The view will trigger the `run_agent_task` Celery task and return a unique `channel_id` for the SSE connection.
    - [ ] **Sub-checklist for Real-time Updates:**
        - [ ] The frontend will use the `channel_id` to connect to the `django-eventstream` endpoint.
        - [ ] The `run_agent_task` will publish progress updates (e.g., `{'status': 'running_tool', 'tool_name': 'generate_image'}`).
        - [ ] The frontend will listen for these events and update the UI accordingly, displaying progress and final results without a page reload.
