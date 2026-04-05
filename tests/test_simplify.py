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
    assert simplify(Add(Number(2), Number(3), Symbol("x"))) == Add(Number(5), Symbol("x"))


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


def test_canonical_order_add_emits_explicit_trace_step() -> None:
    expr = Add(Symbol("y"), Number(2), Symbol("x"))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Add(Number(2), Symbol("x"), Symbol("y"))
    assert_trace_rule_sequence(trace_result, ["canonical-order-add"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_canonical_order_mul_emits_explicit_trace_step() -> None:
    expr = Mul(Symbol("y"), Number(2), Symbol("x"))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Mul(Number(2), Symbol("x"), Symbol("y"))
    assert_trace_rule_sequence(trace_result, ["canonical-order-mul"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_canonical_order_output_is_idempotent() -> None:
    expr = Add(Symbol("z"), Number(1), Symbol("a"))
    simplified = simplify(expr)

    assert simplified == Add(Number(1), Symbol("a"), Symbol("z"))

    trace_result = simplify(simplified, trace=True)
    assert trace_result.expr == simplified
    assert_trace_rule_sequence(trace_result, [])
    assert_trace_before_after_integrity(simplified, trace_result)


def test_collect_like_terms_simple_duplicate() -> None:
    assert simplify(Add(Symbol("x"), Symbol("x"))) == Mul(Number(2), Symbol("x"))


def test_collect_like_terms_with_coefficients_emits_explicit_step() -> None:
    expr = Add(Mul(Number(2), Symbol("x")), Mul(Number(3), Symbol("x")))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Mul(Number(5), Symbol("x"))
    assert_trace_rule_sequence(trace_result, ["collect-like-terms-add", "collapse-single-add"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_collect_like_terms_cancellation_reaches_zero() -> None:
    expr = Add(Symbol("x"), Mul(Number(-1), Symbol("x")))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Number(0)
    assert_trace_rule_sequence(trace_result, ["collect-like-terms-add"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_collect_like_terms_preserves_canonical_add_order() -> None:
    expr = Add(Symbol("x"), Symbol("y"), Symbol("x"))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Add(Symbol("y"), Mul(Number(2), Symbol("x")))
    assert_trace_rule_sequence(
        trace_result,
        ["collect-like-terms-add", "canonical-order-add"],
    )
    assert_trace_before_after_integrity(expr, trace_result)


def test_collect_like_terms_matches_repeated_mul_with_power() -> None:
    expr = Add(Mul(Symbol("x"), Symbol("x")), Pow(Symbol("x"), Number(2)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Mul(Number(2), Pow(Symbol("x"), Number(2)))
    assert_trace_rule_sequence(
        trace_result,
        [
            "merge-repeated-bases-mul",
            "collapse-single-mul",
            "collect-like-terms-add",
            "collapse-single-add",
        ],
    )


def test_collect_like_terms_matches_mixed_power_and_product_forms() -> None:
    expr = Add(
        Mul(Number(2), Symbol("x"), Symbol("x")),
        Mul(Number(3), Pow(Symbol("x"), Number(2))),
        Symbol("y"),
    )

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Add(Symbol("y"), Mul(Number(5), Pow(Symbol("x"), Number(2))))
    assert_trace_rule_sequence(
        trace_result,
        ["merge-repeated-bases-mul", "collect-like-terms-add", "canonical-order-add"],
    )


def test_collect_like_terms_matches_integral_float_and_integer_powers() -> None:
    expr = Add(Pow(Symbol("x"), Number(2.0)), Pow(Symbol("x"), Number(2)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Mul(Number(2), Pow(Symbol("x"), Number(2)))
    assert_trace_rule_sequence(trace_result, ["collect-like-terms-add", "collapse-single-add"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_simple_duplicate() -> None:
    expr = Mul(Symbol("x"), Symbol("x"))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Pow(Symbol("x"), Number(2))
    assert_trace_rule_sequence(trace_result, ["merge-repeated-bases-mul", "collapse-single-mul"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_with_existing_power() -> None:
    expr = Mul(Symbol("x"), Pow(Symbol("x"), Number(2)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Pow(Symbol("x"), Number(3))
    assert_trace_rule_sequence(trace_result, ["merge-repeated-bases-mul", "collapse-single-mul"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_runs_after_canonical_order() -> None:
    expr = Mul(Pow(Symbol("x"), Number(2)), Symbol("x"))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Pow(Symbol("x"), Number(3))
    assert_trace_rule_sequence(
        trace_result,
        ["canonical-order-mul", "merge-repeated-bases-mul", "collapse-single-mul"],
    )
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_skips_non_integer_exponents() -> None:
    expr = Mul(Symbol("x"), Pow(Symbol("x"), Number(2.5)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == expr
    assert_trace_rule_sequence(trace_result, [])
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_skips_non_positive_exponents() -> None:
    expr = Mul(Symbol("x"), Pow(Symbol("x"), Number(-1)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == expr
    assert_trace_rule_sequence(trace_result, [])
    assert_trace_before_after_integrity(expr, trace_result)


def test_merge_repeated_bases_mul_accepts_integral_float_exponents() -> None:
    expr = Mul(Symbol("x"), Pow(Symbol("x"), Number(2.0)))

    trace_result = simplify(expr, trace=True)
    assert trace_result.expr == Pow(Symbol("x"), Number(3))
    assert_trace_rule_sequence(trace_result, ["merge-repeated-bases-mul", "collapse-single-mul"])
    assert_trace_before_after_integrity(expr, trace_result)
