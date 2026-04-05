from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class Expr:
    def children(self) -> Tuple[Expr, ...]:
        return ()


@dataclass(frozen=True)
class Number(Expr):
    value: int | float

    def __str__(self) -> str:
        if isinstance(self.value, float) and self.value.is_integer():
            return str(int(self.value))
        return str(self.value)


@dataclass(frozen=True)
class Symbol(Expr):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Add(Expr):
    terms: Tuple[Expr, ...]

    def __init__(self, *terms: Expr) -> None:
        object.__setattr__(self, "terms", tuple(terms))

    def children(self) -> Tuple[Expr, ...]:
        return self.terms

    def __str__(self) -> str:
        return " + ".join(_maybe_parenthesize(term, self) for term in self.terms)


@dataclass(frozen=True)
class Mul(Expr):
    factors: Tuple[Expr, ...]

    def __init__(self, *factors: Expr) -> None:
        object.__setattr__(self, "factors", tuple(factors))

    def children(self) -> Tuple[Expr, ...]:
        return self.factors

    def __str__(self) -> str:
        return " * ".join(_maybe_parenthesize(factor, self) for factor in self.factors)


@dataclass(frozen=True)
class Pow(Expr):
    base: Expr
    exponent: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.base, self.exponent)

    def __str__(self) -> str:
        return f"{_maybe_parenthesize(self.base, self)}**{_maybe_parenthesize(self.exponent, self)}"


def _maybe_parenthesize(expr: Expr, parent: Expr) -> str:
    if isinstance(parent, Add):
        return str(expr)
    if isinstance(parent, Mul) and isinstance(expr, Add):
        return f"({expr})"
    if isinstance(parent, Pow) and isinstance(expr, (Add, Mul)):
        return f"({expr})"
    if isinstance(parent, Pow) and isinstance(expr, Pow):
        return f"({expr})"
    return str(expr)


def ensure_expr(value: Expr | int | float | str) -> Expr:
    if isinstance(value, Expr):
        return value
    if isinstance(value, (int, float)):
        return Number(value)
    if isinstance(value, str):
        return Symbol(value)
    raise TypeError(f"Unsupported expression value: {value!r}")


def walk(expr: Expr) -> Iterable[Expr]:
    yield expr
    for child in expr.children():
        yield from walk(child)
