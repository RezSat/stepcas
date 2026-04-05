from stepcas import Add, Mul, Number, Pow, Symbol, simplify


def test_remove_add_zero() -> None:
    assert simplify(Add(Symbol("x"), Number(0))) == Symbol("x")


def test_fold_constants() -> None:
    assert simplify(Add(Number(2), Number(3), Symbol("x"))) == Add(Symbol("x"), Number(5))


def test_multiplication_by_zero() -> None:
    assert simplify(Mul(Symbol("x"), Number(0), Symbol("y"))) == Number(0)


def test_power_identities() -> None:
    assert simplify(Pow(Symbol("x"), Number(1))) == Symbol("x")
