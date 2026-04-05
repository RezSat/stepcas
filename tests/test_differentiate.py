from stepcas import Add, Mul, Number, Pow, Symbol, differentiate


def test_differentiate_constant() -> None:
    assert differentiate(Number(9), "x") == Number(0)


def test_differentiate_variable() -> None:
    assert differentiate(Symbol("x"), "x") == Number(1)


def test_differentiate_power() -> None:
    assert differentiate(Pow(Symbol("x"), Number(3)), "x") == Mul(Number(3), Pow(Symbol("x"), Number(2)))


def test_differentiate_sum() -> None:
    assert differentiate(Add(Pow(Symbol("x"), Number(2)), Mul(Number(2), Symbol("x"))), "x") == Add(
        Mul(Number(2), Symbol("x")),
        Number(2),
    )
