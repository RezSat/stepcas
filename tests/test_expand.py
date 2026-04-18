from __future__ import annotations

from stepcas import Add, Expr, Mul, Number, Symbol
from stepcas.expand import expand

from tests.trace_helpers import assert_trace_before_after_integrity, assert_trace_rule_sequence


def test_expand_distribute_constant_over_add_left() -> None:
    """Test c*(a+b) expands to c*a + c*b."""
    expr = Mul(Number(3), Add(Symbol("x"), Symbol("y")))
    result = expand(expr)
    assert str(result) == "3 * x + 3 * y"


def test_expand_distribute_constant_over_add_right() -> None:
    """Test (a+b)*c expands to a*c + b*c."""
    expr = Mul(Add(Symbol("x"), Symbol("y")), Number(3))
    result = expand(expr)
    assert str(result) == "3 * x + 3 * y"


def test_expand_no_add_returns_same() -> None:
    """Test that expressions without Add are unchanged."""
    expr = Mul(Number(3), Symbol("x"))
    result = expand(expr)
    assert result == expr


def test_expand_trace_integrity_c_times_add() -> None:
    """Test trace integrity for c*(a+b)."""
    expr = Mul(Number(2), Add(Symbol("a"), Symbol("b")))
    trace_result = expand(expr, trace=True)
    
    assert_trace_before_after_integrity(expr, trace_result)


def test_expand_trace_integrity_add_times_c() -> None:
    """Test trace integrity for (a+b)*c."""
    expr = Mul(Add(Symbol("a"), Symbol("b")), Number(2))
    trace_result = expand(expr, trace=True)
    
    assert_trace_before_after_integrity(expr, trace_result)


def test_expand_trace_rule_sequence() -> None:
    """Test that correct rule is applied."""
    expr = Mul(Number(5), Add(Symbol("x"), Symbol("y")))
    trace_result = expand(expr, trace=True)
    
    assert_trace_rule_sequence(
        trace_result,
        ["distribute-constant-over-add"],
    )


def test_expand_nested_add() -> None:
    """Test nested addition distribution."""
    expr = Mul(
        Number(2),
        Add(Add(Symbol("x"), Symbol("y")), Symbol("z"))
    )
    result = expand(expr)
    # Nested add flattened, then distributed
    assert "2 * x" in str(result)
    assert "2 * y" in str(result)
    assert "2 * z" in str(result)


def test_expand_multiple_nonconstants() -> None:
    """Test that expressions with multiple non-constants are unchanged."""
    expr = Mul(Symbol("a"), Add(Symbol("x"), Symbol("y")))
    result = expand(expr)
    # No constant to distribute, should remain unchanged
    assert result == expr