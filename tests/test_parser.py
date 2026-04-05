import pytest

from stepcas import Add, Mul, Number, ParseError, Pow, Symbol, parse_expr


def test_parse_addition() -> None:
    assert parse_expr("x + 2") == Add(Symbol("x"), Number(2))


def test_parse_division_as_negative_power() -> None:
    assert parse_expr("x / y") == Mul(Symbol("x"), Pow(Symbol("y"), Number(-1)))


def test_parse_unary_minus() -> None:
    assert parse_expr("-x") == Mul(Number(-1), Symbol("x"))


def test_parse_operator_precedence() -> None:
    assert parse_expr("x + y * z") == Add(Symbol("x"), Mul(Symbol("y"), Symbol("z")))


def test_parse_power_right_associative() -> None:
    assert parse_expr("x ** y ** z") == Pow(Symbol("x"), Pow(Symbol("y"), Symbol("z")))


def test_parse_subtraction_left_associative() -> None:
    assert parse_expr("x - y - z") == Add(
        Add(Symbol("x"), Mul(Number(-1), Symbol("y"))),
        Mul(Number(-1), Symbol("z")),
    )


@pytest.mark.parametrize("source", ["f(x)", "x // y", "x +", "("])
def test_parse_rejects_unsupported_or_malformed_syntax(source: str) -> None:
    with pytest.raises(ParseError):
        parse_expr(source)
