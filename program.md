# AutoResearch Program for stepcas

You are helping build `stepcas`, a step-first symbolic algebra system.

## Mission

Build a symbolic math engine that is:

- exact and computation-grounded,
- auditable,
- pleasant to import from Python,
- usable from the terminal,
- ready to grow into a service and UI,
- designed so AI systems can rely on it for actual math instead of style-only output.

## Philosophy

1. Every meaningful transformation should be representable as a machine-readable step.
2. Simplicity before feature count.
3. Small commits.
4. Every code change must leave behind evidence: tests, docs, ADR, benchmark note, or all of them.
5. Do not build clever magic that cannot later explain itself.
6. Optimize for architecture that can scale into a real CAS, not a hacky demo.

## Development law

When making changes:

1. Read the relevant architecture docs first.
2. Plan before editing.
3. Keep diffs narrow.
4. Run tests.
5. Update docs when behavior changes.
6. Prefer adding or refining rules over ad hoc branching.
7. Preserve immutable expression semantics.
8. Never silently remove step information.
9. Commit with small, specific messages.
10. Leave TODO notes only when paired with an issue or roadmap item.

## Target architecture

Build toward these packages:

- `stepcas.core`
- `stepcas.rules`
- `stepcas.rewrite`
- `stepcas.trace`
- `stepcas.algorithms`
- `stepcas.frontends`
- `stepcas.explain`

This starter is smaller, but every change should point in that direction.

## Immediate priorities

1. Stabilize the expression model.
2. Expand canonical simplification.
3. Improve differentiation coverage.
4. Add equation solving primitives.
5. Introduce structured explanation templates.
6. Add benchmarks.
7. Expose a clean JSON trace format for web/API use.

## Agent behavior

- Use planning and review agents before big edits.
- Use test and benchmark agents before claiming quality.
- Use docs agents before closing work.
- If a change grows beyond one concern, split it.

## Definition of done

A task is only done when:

- code works,
- tests exist or were updated,
- docs reflect the change,
- commit message is precise,
- the system remains simpler or more coherent than before.
