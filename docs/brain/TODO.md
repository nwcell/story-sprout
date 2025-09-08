# Project TODO

This file tracks high-level tasks and future development goals for the Story Sprout project.

## Rules

- mark tasks as in progress while working on them.
- work on one task at a time
- treat nested tasks as standalone tasks (so don't work on all of the subtasks at once)
- if you are not 100% on the way to proceed, write add a question to the task, provide a space for a response & pause


## High Priority

- [ ] Migrate to pydantic ai
    - [ ] Review subtasks & verify any clarifying questions w/ user.  list questions as sub bullets.  leave space for answers.
    - [ ] Pause until user answers questions
    - [ ] Update subtasks based on user answers
    - [ ] Pause until user approves revisions
    - [ ] Make one pydantic ai enpdpoint that can update the title
        - [ ] api call (ninja)
        - [ ] celery task
        - [ ] sse notification
    - [ ] Make the pydantic title endpoint so that it updates the title w/ a tool
        - [ ] make story tool
        - [ ] story ai chip
    - [ ] Check w/ user for further instructions

## Medium Priority

- [ ]

## Low Priority

- [ ] Migrate to Bubble UI
- [ ] Migrate to locally building Tailwind
- [ ] Clean up Marketing site codebase & make presentable
- [ ] Deploy to Digital Ocean
