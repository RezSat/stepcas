from __future__ import annotations

from typing import Callable, List, Optional

from .expression import Add, Expr, Mul, Number, Pow
from .trace import Step

RuleFn = Callable[[Expr], Optional[tuple[Expr, str]]]


def rewrite_fixpoint(expr: Expr, rules: List[tuple[str, RuleFn]], steps: List[Step]) -> Expr:
    changed = True
    current = expr
    while changed:
        changed = False
        current, local_changed = _rewrite_once(current, rules, steps)
        changed = local_changed
    return current


def _rewrite_once(expr: Expr, rules: List[tuple[str, RuleFn]], steps: List[Step]) -> tuple[Expr, bool]:
    rebuilt = _rewrite_children(expr, rules, steps)
    if rebuilt != expr:
        expr = rebuilt
    for rule_name, rule_fn in rules:
        result = rule_fn(expr)
        if result is None:
            continue
        after, explanation = result
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
    filtered = [factor for factor in expr.factors if not (isinstance(factor, Number) and factor.value == 1)]
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


DEFAULT_RULES: List[tuple[str, RuleFn]] = [
    ("flatten-add", rule_flatten_add),
    ("flatten-mul", rule_flatten_mul),
    ("fold-add-constants", rule_fold_add_constants),
    ("fold-mul-constants", rule_fold_mul_constants),
    ("remove-add-zero", rule_remove_add_zero),
    ("remove-mul-one", rule_remove_mul_one),
    ("collapse-single-add", rule_collapse_single_add),
    ("collapse-single-mul", rule_collapse_single_mul),
    ("pow-identities", rule_pow_identities),
]
