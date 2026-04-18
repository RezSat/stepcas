from __future__ import annotations

from typing import Optional

from .expression import Add, Expr, Mul, Number
from .rewrite import RuleFn, rewrite_fixpoint
from .trace import Step, TraceResult


def rule_distribute_constant_over_add(expr: Expr) -> Optional[tuple[Expr, str]]:
    """Distribute a constant over addition: c*(a+b) -> c*a + c*b.
    
    This is a narrow rule for constant multiplication over add expressions only.
    Does NOT do general polynomial expansion - only handles the c*(a+b) case.
    """
    if not isinstance(expr, Mul):
        return None
    
    # Look for exactly one Number factor and one Add factor
    constant_factor = None
    add_factor = None
    other_factors = []
    
    for factor in expr.factors:
        if isinstance(factor, Number):
            if constant_factor is not None:
                # Multiple constants - let other rules handle this
                return None
            constant_factor = factor
        elif isinstance(factor, Add):
            if add_factor is not None:
                # Multiple Add expressions - let other rules handle this
                return None
            add_factor = factor
        else:
            other_factors.append(factor)
    
    if constant_factor is None or add_factor is None:
        return None
    
    # Distribute: c*(a+b) -> c*a + c*b
    distributed_terms = []
    for term in add_factor.terms:
        if other_factors:
            distributed_terms.append(Mul(constant_factor, term, *other_factors))
        else:
            distributed_terms.append(Mul(constant_factor, term))
    
    result = Add(*distributed_terms)
    return result, "Distribute constant over addition"


# Expand rule set - narrow and focused only
EXPAND_RULES: list[tuple[str, RuleFn]] = [
    ("distribute-constant-over-add", rule_distribute_constant_over_add),
]


# Also export rule for external use or composition
DISTRIBUTE_CONSTANT_OVER_ADD = rule_distribute_constant_over_add


def expand(expr: Expr, trace: bool = False) -> Expr | TraceResult:
    """Apply narrow expand operations to an expression.
    
    Currently implements:
    - Distribution of constants over addition: c*(a+b) -> c*a + c*b
    
    This is an opt-in algorithm path, separate from simplify.
    """
    steps: list[Step] = []
    result = rewrite_fixpoint(expr, EXPAND_RULES, steps)
    if trace:
        return TraceResult(expr=result, steps=steps)
    return result