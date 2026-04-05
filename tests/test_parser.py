from stepcas import Add, Mul, Number, Pow, Symbol, parse_expr


def test_parse_addition() -> None:
    assert parse_expr("x + 2") == Add(Symbol("x"), Number(2))


def test_parse_division_as_negative_power() -> None:
    assert parse_expr("x / y") == Mul(Symbol("x"), Pow(Symbol("y"), Number(-1)))


def test_parse_unary_minus() -> None:
    assert parse_expr("-x") == Mul(Number(-1), Symbol("x"))
