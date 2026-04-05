from __future__ import annotations

import ast

from .expression import Add, Expr, Mul, Number, Pow, Symbol


class ParseError(ValueError):
    pass


_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_ALLOWED_UNARY = (ast.UAdd, ast.USub)


def parse_expr(source: str) -> Expr:
    try:
        node = ast.parse(source, mode="eval").body
    except SyntaxError as exc:
        raise ParseError(str(exc)) from exc
    return _convert(node)


def _convert(node: ast.AST) -> Expr:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Number(node.value)
    if isinstance(node, ast.Name):
        return Symbol(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_BINOPS):
        left = _convert(node.left)
        right = _convert(node.right)
        if isinstance(node.op, ast.Add):
            return Add(left, right)
        if isinstance(node.op, ast.Sub):
            return Add(left, Mul(Number(-1), right))
        if isinstance(node.op, ast.Mult):
            return Mul(left, right)
        if isinstance(node.op, ast.Div):
            return Mul(left, Pow(right, Number(-1)))
        if isinstance(node.op, ast.Pow):
            return Pow(left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, _ALLOWED_UNARY):
        operand = _convert(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand
        return Mul(Number(-1), operand)
    raise ParseError(f"Unsupported syntax: {ast.dump(node)}")
