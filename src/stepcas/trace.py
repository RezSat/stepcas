from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .expression import Expr


@dataclass(frozen=True)
class Step:
    rule: str
    before: Expr
    after: Expr
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceResult:
    expr: Expr
    steps: List[Step]
