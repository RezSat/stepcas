# StepCAS company runtime

This folder adds a lightweight supervisor around OpenCode so the project can run semi-autonomously on your machine.

## Model

- `opencode serve` is the long-lived backend.
- `company/runner.py` is the external supervisor.
- tasks live in `company/tasks.json`.
- each task becomes one isolated `opencode run --attach ...` call.
- the agent may use subagents inside a run, but it should not spawn nested OpenCode processes.

## Why this shape

This gives you:
- clean pause and resume
- clear logs
- one task per session
- less context pollution
- no uncontrolled self-recursion

## Task states

- `queued`
- `running`
- `done`
- `failed`
- `blocked`

## Typical use

1. start the company server
2. start the runner
3. add tasks to `tasks.json`
4. let the runner dispatch them one by one
5. stop the runner when you want to pause the company

## Safety rules

- max one active task by default
- runner owns process spawning
- agents must not call `opencode` inside `opencode`
- every task should be narrow
- tests should run before a task is marked done
