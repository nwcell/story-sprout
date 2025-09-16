# Project TODO

This file tracks high-level tasks and future development goals for the Story Sprout project.

## Rules

- mark tasks as in progress while working on them.
- work on one task at a time
- treat nested tasks as standalone tasks (so don't work on all of the subtasks at once)
- if you are not 100% on the way to proceed, write add a question to the task, provide a space for a response & pause


## High Priority

- [x] Migrate to pydantic ai
    - [x] Review subtasks & verify any clarifying questions w/ user.  list questions as sub bullets.  leave space for answers.
        - [x] Pydantic AI Architecture - agents with tools or just completion replacement? One agent or multiple?
            - Answer: Single agent tht is used to handle assigned tasks for now
        - [x] Migration Scope - all 6 endpoints or just title first? Keep current API structure?
            - Answer: make a new endpoint.  it'll become a generic endpoint.  for now, only give it the ability to update the title
        - [x] Tool Integration - what is "story tool" and "story ai chip"? Direct model updates or service layer?
            - Answer: In ai agents, there is the concept of tool calling, which is a concept where ai agents can make function calls to retrieve further context & impact external systems.  look at the docs for pydantic ai for more information.  We're going to implement a system that leverages the work done so far w/ the story/api.py.
        - [x] Prompt Templates - convert to pydantic AI system or keep Django templates? Use structured output?
            - Answer: keep the prompt template system in place for now, but we're not going to use it for this task
        - [x] Dependencies - remove litellm completely or keep for transition?
            - Answer: keep all legacy ai capabilities in place for now
    - [x] Pause until user answers questions
    - [x] Update subtasks based on user answers
    - [x] Pause until user approves revisions ← **APPROVED**
    - [x] Add pydantic-ai dependency
    - [x] Create single pydantic AI agent for story tasks
    - [ ] Make new generic pydantic ai endpoint that can update the title _(in-progress)_
        - [x] api call (ninja) - new generic endpoint
        - [ ] celery task - integrate with existing job system _(in-progress)_
        - [ ] sse notification (use existing update title service) _(in-progress)_
    - [ ] Pause until user approves
    - [ ] Add tools to the agent
        - [ ] Review tool requirements & verify clarifying questions w/ user
        - [ ] Pause until user answers questions
        - [ ] Update tool subtasks based on user answers
        - [ ] Create story context retrieval tool
        - [ ] Create story title update tool (leverage existing story services)
        - [ ] Test agent with tools end-to-end
    - [ ] Check w/ user for further instructions

## Medium Priority

- [ ]

## Low Priority

- [ ] Unified launch & log command w/ centralized reboot (https://github.com/DarthSim/overmind)
- [ ] Migrate to Bubble UI
- [ ] Migrate to locally building Tailwind
- [ ] Clean up Marketing site codebase & make presentable
- [ ] Deploy to Digital Ocean
