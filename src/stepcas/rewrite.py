from __future__ import annotations

from typing import Callable, List, Optional

from .errors import REWRITE_INVALID_RULE_RESULT, RewriteError
from .expression import Add, Expr, Mul, Number, Pow, Symbol
from .trace import Step

RuleFn = Callable[[Expr], Optional[tuple[Expr, str]]]


def expr_sort_key(expr: Expr) -> tuple:
    if isinstance(expr, Number):
        return (0, expr.value)
    if isinstance(expr, Symbol):
        return (1, expr.name)
    if isinstance(expr, Pow):
        return (2, expr_sort_key(expr.base), expr_sort_key(expr.exponent))
    if isinstance(expr, Mul):
        return (3, tuple(expr_sort_key(factor) for factor in expr.factors))
    if isinstance(expr, Add):
        return (4, tuple(expr_sort_key(term) for term in expr.terms))
    return (99, repr(expr))


def rewrite_fixpoint(expr: Expr, rules: List[tuple[str, RuleFn]], steps: List[Step]) -> Expr:
    changed = True
    current = expr
    while changed:
        changed = False
        current, local_changed = _rewrite_once(current, rules, steps)
        changed = local_changed
    return current


def _rewrite_once(
    expr: Expr, rules: List[tuple[str, RuleFn]], steps: List[Step]
) -> tuple[Expr, bool]:
    rebuilt = _rewrite_children(expr, rules, steps)
    if rebuilt != expr:
        expr = rebuilt
    for rule_name, rule_fn in rules:
        result = rule_fn(expr)
        if result is None:
            continue
        if not isinstance(result, tuple) or len(result) != 2:
            raise RewriteError(
                f"Rule '{rule_name}' must return (Expr, str) or None",
                code=REWRITE_INVALID_RULE_RESULT,
            )
        after, explanation = result
        if not isinstance(after, Expr) or not isinstance(explanation, str):
            raise RewriteError(
                f"Rule '{rule_name}' returned invalid result types",
                code=REWRITE_INVALID_RULE_RESULT,
            )
        steps.append(Step(rule=rule_name, before=expr, after=after, explanation=explanation))
        return after, True
    return expr, rebuilt != expr


def _rewrite_children(expr: Expr, rules: List[tuple[str, RuleFn]], steps: List[Step]) -> Expr:
    if isinstance(expr, Add):
        terms = [rewrite_fixpoint(term, rules, steps) for term in expr.terms]
        return Add(*terms)
    if isinstance(expr, Mul):
        factors = [rewrite_fixpoint(factor, rules, steps) for factor in expr.factors]
        return Mul(*factors)
    if isinstance(expr, Pow):
        base = rewrite_fixpoint(expr.base, rules, steps)
        exponent = rewrite_fixpoint(expr.exponent, rules, steps)
        return Pow(base, exponent)
    return expr


def rule_flatten_add(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None
    new_terms = []
    changed = False
    for term in expr.terms:
        if isinstance(term, Add):
            new_terms.extend(term.terms)
            changed = True
        else:
            new_terms.append(term)
    if not changed:
        return None
    return Add(*new_terms), "Flatten nested addition"


def rule_flatten_mul(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None
    new_factors = []
    changed = False
    for factor in expr.factors:
        if isinstance(factor, Mul):
            new_factors.extend(factor.factors)
            changed = True
        else:
            new_factors.append(factor)
    if not changed:
        return None
    return Mul(*new_factors), "Flatten nested multiplication"


def rule_fold_add_constants(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None
    constant_sum = 0
    others = []
    constant_count = 0
    for term in expr.terms:
        if isinstance(term, Number):
            constant_sum += term.value
            constant_count += 1
        else:
            others.append(term)
    if constant_count == 0:
        return None
    if constant_sum != 0 or not others:
        others.append(Number(constant_sum))
    if len(others) == len(expr.terms) and constant_count == 1:
        return None
    return Add(*others), "Fold additive constants"


def _decompose_add_term(term: Expr) -> tuple[int | float, Expr | None]:
    if isinstance(term, Number):
        return term.value, None
    if not isinstance(term, Mul):
        return 1, term

    coefficient = 1
    non_numeric_factors = []
    for factor in term.factors:
        if isinstance(factor, Number):
            coefficient *= factor.value
        else:
            non_numeric_factors.append(factor)

    if not non_numeric_factors:
        return coefficient, None
    if len(non_numeric_factors) == 1:
        return coefficient, non_numeric_factors[0]
    return coefficient, Mul(*non_numeric_factors)


def _compose_add_term(coefficient: int | float, core: Expr) -> Expr:
    if coefficient == 1:
        return core
    if coefficient == -1:
        return Mul(Number(-1), core)
    return Mul(Number(coefficient), core)


def _positive_integer_number_value(number: Number) -> int | None:
    value = number.value
    if isinstance(value, int) and value >= 1:
        return value
    if isinstance(value, float) and value >= 1 and value.is_integer():
        return int(value)
    return None


def _normalized_like_term_core(core: Expr) -> Expr:
    if isinstance(core, Pow) and isinstance(core.exponent, Number):
        exponent = _positive_integer_number_value(core.exponent)
        if exponent is not None:
            return Pow(core.base, Number(exponent))

    if not isinstance(core, Mul):
        return core

    exponent_by_base: dict[Expr, int] = {}
    for factor in core.factors:
        if isinstance(factor, Pow) and isinstance(factor.exponent, Number):
            exponent = _positive_integer_number_value(factor.exponent)
        else:
            exponent = None

        if exponent is not None:
            base = factor.base
        else:
            base = factor
            exponent = 1
        exponent_by_base[base] = exponent_by_base.get(base, 0) + exponent

    normalized_factors = []
    for base in sorted(exponent_by_base, key=expr_sort_key):
        exponent = exponent_by_base[base]
        if exponent == 1:
            normalized_factors.append(base)
        else:
            normalized_factors.append(Pow(base, Number(exponent)))

    if len(normalized_factors) == 1:
        return normalized_factors[0]
    return Mul(*normalized_factors)


def rule_collect_like_terms_add(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None

    constants = []
    coefficient_by_core: dict[Expr, int | float] = {}
    core_order = []
    symbolic_term_count = 0
    for term in expr.terms:
        coefficient, core = _decompose_add_term(term)
        if core is None:
            constants.append(term)
            continue
        core = _normalized_like_term_core(core)
        symbolic_term_count += 1
        if core not in coefficient_by_core:
            coefficient_by_core[core] = 0
            core_order.append(core)
        coefficient_by_core[core] += coefficient

    if symbolic_term_count == len(core_order) and all(
        coefficient_by_core[core] == 1 for core in core_order
    ):
        return None

    rebuilt_terms = list(constants)
    for core in core_order:
        total_coefficient = coefficient_by_core[core]
        if total_coefficient == 0:
            continue
        rebuilt_terms.append(_compose_add_term(total_coefficient, core))

    if not rebuilt_terms:
        return Number(0), "Collect exact like terms in addition"

    rebuilt = Add(*rebuilt_terms)
    if rebuilt == expr:
        return None
    return rebuilt, "Collect exact like terms in addition"


def rule_fold_mul_constants(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None
    constant_product = 1
    others = []
    constant_count = 0
    for factor in expr.factors:
        if isinstance(factor, Number):
            constant_product *= factor.value
            constant_count += 1
        else:
            others.append(factor)
    if constant_count == 0:
        return None
    if constant_product == 0:
        return Number(0), "Anything multiplied by zero becomes zero"
    if constant_product != 1 or not others:
        others.insert(0, Number(constant_product))
    if len(others) == len(expr.factors) and constant_count == 1:
        return None
    return Mul(*others), "Fold multiplicative constants"


def rule_remove_add_zero(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None
    filtered = [term for term in expr.terms if not (isinstance(term, Number) and term.value == 0)]
    if len(filtered) == len(expr.terms):
        return None
    if not filtered:
        return Number(0), "Zero is the additive identity"
    if len(filtered) == 1:
        return filtered[0], "Remove additive identity"
    return Add(*filtered), "Remove additive zeros"


def rule_remove_mul_one(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None
    filtered = [
        factor for factor in expr.factors if not (isinstance(factor, Number) and factor.value == 1)
    ]
    if len(filtered) == len(expr.factors):
        return None
    if not filtered:
        return Number(1), "One is the multiplicative identity"
    if len(filtered) == 1:
        return filtered[0], "Remove multiplicative identity"
    return Mul(*filtered), "Remove multiplicative ones"


def rule_pow_identities(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Pow):
        return None
    if isinstance(expr.exponent, Number) and expr.exponent.value == 1:
        return expr.base, "Power of one leaves the base unchanged"
    if isinstance(expr.exponent, Number) and expr.exponent.value == 0:
        return Number(1), "Nonzero base to the zero power is one"
    if isinstance(expr.base, Number) and expr.base.value == 0:
        return Number(0), "Zero to a positive power is zero"
    if isinstance(expr.base, Number) and expr.base.value == 1:
        return Number(1), "One to any power is one"
    return None


def rule_collapse_single_add(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None
    if len(expr.terms) != 1:
        return None
    return expr.terms[0], "Collapse single-term addition"


def rule_collapse_single_mul(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None
    if len(expr.factors) != 1:
        return None
    return expr.factors[0], "Collapse single-factor multiplication"


def rule_canonical_order_add(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Add):
        return None
    ordered_terms = tuple(sorted(expr.terms, key=expr_sort_key))
    if ordered_terms == expr.terms:
        return None
    return Add(*ordered_terms), "Canonicalize addition term order"


def rule_canonical_order_mul(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None
    ordered_factors = tuple(sorted(expr.factors, key=expr_sort_key))
    if ordered_factors == expr.factors:
        return None
    return Mul(*ordered_factors), "Canonicalize multiplication factor order"


def rule_merge_repeated_bases_mul(expr: Expr) -> Optional[tuple[Expr, str]]:
    if not isinstance(expr, Mul):
        return None

    exponent_by_base: dict[Expr, int] = {}
    untouched_factors = []
    for factor in expr.factors:
        if isinstance(factor, Number):
            untouched_factors.append(factor)
            continue

        if isinstance(factor, Pow) and isinstance(factor.exponent, Number):
            exponent = _positive_integer_number_value(factor.exponent)
        else:
            exponent = None

        if exponent is not None and not isinstance(factor.base, Number):
            exponent_by_base[factor.base] = exponent_by_base.get(factor.base, 0) + exponent
            continue

        if isinstance(factor, Pow):
            untouched_factors.append(factor)
            continue

        exponent_by_base[factor] = exponent_by_base.get(factor, 0) + 1

    merged_factors = []
    for base in sorted(exponent_by_base, key=expr_sort_key):
        exponent = exponent_by_base[base]
        if exponent == 1:
            merged_factors.append(base)
        else:
            merged_factors.append(Pow(base, Number(exponent)))

    rebuilt_factors = tuple(sorted([*untouched_factors, *merged_factors], key=expr_sort_key))
    rebuilt = Mul(*rebuilt_factors)
    if rebuilt == expr:
        return None
    return rebuilt, "Merge repeated multiplicative bases into integer powers"


DEFAULT_RULES: List[tuple[str, RuleFn]] = [
    ("flatten-add", rule_flatten_add),
    ("flatten-mul", rule_flatten_mul),
    ("fold-add-constants", rule_fold_add_constants),
    ("fold-mul-constants", rule_fold_mul_constants),
    ("remove-add-zero", rule_remove_add_zero),
    ("remove-mul-one", rule_remove_mul_one),
    ("canonical-order-mul", rule_canonical_order_mul),
    ("merge-repeated-bases-mul", rule_merge_repeated_bases_mul),
    ("collect-like-terms-add", rule_collect_like_terms_add),
    ("canonical-order-add", rule_canonical_order_add),
    ("collapse-single-add", rule_collapse_single_add),
    ("collapse-single-mul", rule_collapse_single_mul),
    ("pow-identities", rule_pow_identities),
]
