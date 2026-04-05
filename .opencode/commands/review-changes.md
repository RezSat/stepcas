---
description: Review recent changes for correctness and maintainability
agent: test-engineer
---
Review the recent changes in this repository.

Recent commits:
!`git log --oneline -10`

Recent diff summary:
!`git diff --stat HEAD~3..HEAD`

Focus on correctness, missing edge cases, regression risk, and test gaps.
