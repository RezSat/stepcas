---
name: commit-style
description: Write small, human-looking commits for this repository
---

Rules:
- One concern per commit.
- Commit after tests pass for that concern.
- If Commits are left to do before begining a new task, then commit before the task starts and commit after a task is over, then push (git push)
- Message format: imperative, specific, no hype.
- Good examples:
  - add step trace model and result wrapper
  - implement constant folding in add and multiply
  - cover derivative simplification edge cases
  - document step-first architecture in ADR 0001
- Bad examples:
  - big update
  - improve everything
  - ai generated changes
