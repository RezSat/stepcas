from __future__ import annotations

from .expression import Expr
from .rewrite import DEFAULT_RULES, rewrite_fixpoint
from .trace import TraceResult


def simplify(expr: Expr, trace: bool = False) -> Expr | TraceResult:
    steps = []
    result = rewrite_fixpoint(expr, DEFAULT_RULES, steps)
    if trace:
        return TraceResult(expr=result, steps=steps)
    return result
