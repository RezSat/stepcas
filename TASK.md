# StepCAS Autonomous Company Handoff Task

You are continuing the development of StepCAS as an autonomous engineering company.

## Mission

Build and continuously improve StepCAS into a scalable, explainable symbolic algebra system that can:

- work as a Python library
- work as a terminal CLI
- later support a web/API layer
- show correct computed intermediate steps, not guessed natural language
- remain maintainable, minimal, scalable, and well-documented

## Current expectations

You must continue improving the system in small, coherent, human-like slices.

You may plan, implement, debug, test, benchmark, refactor, and document as needed.

You must preserve long-term architecture quality.

## Rules

### Source of truth
Read and follow these first:

- `AGENTS.md`
- `program.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- ADR files under `docs/adr/`
- current source code
- current tests
- current company task state

### Task management
Do not manually edit `company/tasks.json`.
Do not append raw JSON into `company/tasks.json`.
Do not revert `company/tasks.json` with git.

When you need to create follow-up tasks, use this PowerShell command:

```powershell
.\scripts\add-task.ps1 -Id "<ID>" -Title "<TITLE>" -Agent "<AGENT>" -Command "<COMMAND>" -Priority <PRIORITY> -Branch "<BRANCH>"
```

Use that script only.

### Git discipline

For implementation work:

* make focused changes only
* run relevant tests
* update docs when needed
* make small clean commits
* push the current branch if possible
* if push fails, report it clearly

Do not commit logs, runtime junk, or supervisor-owned queue files.

### Runtime files

Do not manually modify:

* `company/tasks.json`
* files under `company/logs/`

Treat them as supervisor-owned runtime state.

### Agents

Only primary agents should be used as top-level task agents.

Use subagents internally when useful, but do not schedule a subagent directly as the task agent.

### Scope control

Do not overbuild.
Do not rewrite large areas without need.
Prefer the smallest safe next slice.

## Queue continuity rule

The company must not leave the backlog empty unless the project is genuinely complete.

If queued all actionable tasks have completed then a planning/governance agent must inspect the repository and add more tasks using `.\scripts\add-task.ps1`.

Task generation must remain diversified across implementation, testing, docs, maintenance, architecture, and future capability work.

## Development loop

Repeat this loop continuously:

1. inspect current backlog and repository state
2. choose the highest-priority unblocked task
3. implement only one coherent slice
4. run tests
5. commit the slice (before ending the session, inspect current backlog and repository state)
6. create follow-up tasks using `.\scripts\add-task.ps1`
7. move to the next highest-value task

Note: when you add a task like this, it will start that task as soon as the current one ends, that is how this is setup, but if all tasks were to be completed the system goes into sleep mode, do not let it sleep. Always from the start check what's need to fix, add, test features and even after a task end do these and add at least one task before ending the current task.

## Technical priorities

Prioritize work that moves StepCAS toward:

1. canonical expression ordering
2. like-term collection
3. equation solving
4. JSON step trace export
5. benchmark harness
6. stronger simplification architecture
7. CLI improvements
8. API/web-readiness
9. docs and architecture health
10. regression tests and maintenance

## Deliverable style

All work should look like a real engineering team produced it.

That means:

* small commits
* passing tests
* explainable code
* minimal but scalable design
* clear docs
* no fake completion claims

Continue operating autonomously until paused by the user.

Do not even try reading `company/tasks.json` it will grow and it's just waste of tokens and memory to even to read it
