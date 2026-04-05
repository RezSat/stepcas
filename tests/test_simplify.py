from stepcas import Add, Mul, Number, Pow, Symbol, simplify

from tests.trace_helpers import assert_trace_before_after_integrity, assert_trace_rule_sequence


def test_remove_add_zero() -> None:
    assert simplify(Add(Symbol("x"), Number(0))) == Symbol("x")


def test_simplify_trace_rule_sequence_and_integrity() -> None:
    expr = Add(Symbol("x"), Number(0))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Symbol("x")
    assert_trace_rule_sequence(trace_result, ["fold-add-constants", "collapse-single-add"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_fold_constants() -> None:
    assert simplify(Add(Number(2), Number(3), Symbol("x"))) == Add(Symbol("x"), Number(5))


def test_multiplication_by_zero() -> None:
    assert simplify(Mul(Symbol("x"), Number(0), Symbol("y"))) == Number(0)


def test_power_identities() -> None:
    assert simplify(Pow(Symbol("x"), Number(1))) == Symbol("x")


def test_zero_power_corner_cases() -> None:
    assert simplify(Pow(Symbol("x"), Number(0))) == Number(1)
    assert simplify(Pow(Number(0), Number(0))) == Number(1)


def test_zero_base_symbolic_exponent_current_semantics() -> None:
    assert simplify(Pow(Number(0), Symbol("x"))) == Number(0)


def test_nested_add_flatten_and_fold_reaches_stable_fixpoint() -> None:
    expr = Add(Add(Number(1), Symbol("x")), Add(Number(2), Add(Number(3), Number(-6))))

    simplified = simplify(expr)
    assert simplified == Symbol("x")

    trace_result = simplify(simplified, trace=True)
    assert trace_result.expr == Symbol("x")
    assert_trace_rule_sequence(trace_result, [])
    assert_trace_before_after_integrity(simplified, trace_result)


def test_nested_mul_flatten_and_fold_reaches_stable_fixpoint() -> None:
    expr = Mul(Mul(Number(2), Symbol("x")), Mul(Number(3), Number(4), Number(1)))

    simplified = simplify(expr)
    assert simplified == Mul(Number(24), Symbol("x"))

    trace_result = simplify(simplified, trace=True)
    assert trace_result.expr == Mul(Number(24), Symbol("x"))
    assert_trace_rule_sequence(trace_result, [])
    assert_trace_before_after_integrity(simplified, trace_result)
