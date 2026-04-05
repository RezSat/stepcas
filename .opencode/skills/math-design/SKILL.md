---
name: math-design
description: Design rules and algorithms for a scalable symbolic algebra engine
---

Guidelines:
- Prefer algebraic rules with names and narrow scope.
- Do not bury symbolic logic inside CLI or parser code.
- Preserve exactness whenever possible.
- If a rule is educationally important, make it visible in traces.
- If a performance shortcut removes steps, provide a traced variant.
