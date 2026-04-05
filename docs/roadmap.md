# Roadmap

## Milestone 0

- [x] Expression tree
- [x] Parser
- [x] Simplifier
- [x] Differentiation subset
- [x] CLI
- [x] Tests
- [x] Agent scaffolding

## Milestone 1

- [x] Canonical ordering
- [x] Additive-only exact like-term collection (no expansion/factoring)
- [ ] General like-term collection across transformed forms
- [x] Linear equation solving
- [x] JSON trace export
- [x] Error taxonomy
- [x] Benchmarks

## Decision records added in this phase

- [x] Canonicalization policy and current scope (`docs/adr/0002-canonicalization-policy.md`)
- [x] Solve scope boundaries (`docs/adr/0003-solve-scope-boundaries.md`)
- [x] JSON trace schema contract (`docs/adr/0004-json-trace-schema-contract.md`)
- [x] Error taxonomy contract (`docs/adr/0005-error-taxonomy-contract.md`)

## Milestone 2

- [ ] Polynomial domain utilities (started: univariate `polynomial_degree`, `polynomial_coefficients`, `polynomial_coeff_vector`, `polynomial_leading_term`, and `polynomial_leading_coefficient` utilities)
- [ ] Factoring
- [ ] Expansion
- [ ] Assumption system
- [ ] Web API

## Milestone 3

- [ ] Educational renderer
- [ ] Browser UI
- [ ] LLM adapter package
- [ ] Rich explanation templates
