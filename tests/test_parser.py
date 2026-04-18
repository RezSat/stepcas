import pytest
import random
import string

from stepcas import Add, Mul, Number, ParseError, PARSE_SYNTAX_ERROR, PARSE_UNSUPPORTED_SYNTAX, Pow, Symbol, parse_expr


# Deterministic malformed-expression corpus for parser robustness testing.
# Each entry: (input_string, expected_error_code)
# Note: Some inputs that look malformed are actually valid Python AST but rejected
# by stepcas as unsupported syntax - those use PARSE_UNSUPPORTED_SYNTAX.
MALFORMED_CORPUS: list[tuple[str, str]] = [
    # Empty and whitespace-only
    ("", PARSE_SYNTAX_ERROR),
    ("   ", PARSE_SYNTAX_ERROR),
    # Incomplete expressions
    ("x +", PARSE_SYNTAX_ERROR),
    ("x -", PARSE_SYNTAX_ERROR),
    ("x *", PARSE_SYNTAX_ERROR),
    ("x /", PARSE_SYNTAX_ERROR),
    ("x **", PARSE_SYNTAX_ERROR),
    ("(", PARSE_SYNTAX_ERROR),
    ("(x +", PARSE_SYNTAX_ERROR),
    ("(x + y", PARSE_SYNTAX_ERROR),
    # Mismatched parentheses
    ("x + y)", PARSE_SYNTAX_ERROR),
    ("(x + y))", PARSE_SYNTAX_ERROR),
    ("((x + y)", PARSE_SYNTAX_ERROR),
    # Bitwise and shift operators - valid in Python AST but unsupported by stepcas
    ("x // y", PARSE_UNSUPPORTED_SYNTAX),
    ("x % y", PARSE_UNSUPPORTED_SYNTAX),
    ("x << y", PARSE_UNSUPPORTED_SYNTAX),
    ("x >> y", PARSE_UNSUPPORTED_SYNTAX),
    ("x & y", PARSE_UNSUPPORTED_SYNTAX),
    ("x | y", PARSE_UNSUPPORTED_SYNTAX),
    ("x ^ y", PARSE_UNSUPPORTED_SYNTAX),
    # Function calls (unsupported)
    ("f(x)", PARSE_UNSUPPORTED_SYNTAX),
    ("sin(x)", PARSE_UNSUPPORTED_SYNTAX),
    ("max(x, y)", PARSE_UNSUPPORTED_SYNTAX),
    # Lambda expressions (unsupported)
    ("lambda x: x", PARSE_UNSUPPORTED_SYNTAX),
    # Comparison expressions (unsupported)
    ("x < y", PARSE_UNSUPPORTED_SYNTAX),
    ("x > y", PARSE_UNSUPPORTED_SYNTAX),
    ("x == y", PARSE_UNSUPPORTED_SYNTAX),
    ("x != y", PARSE_UNSUPPORTED_SYNTAX),
    ("x <= y", PARSE_UNSUPPORTED_SYNTAX),
    ("x >= y", PARSE_UNSUPPORTED_SYNTAX),
    # Boolean operations (unsupported)
    ("x and y", PARSE_UNSUPPORTED_SYNTAX),
    ("x or y", PARSE_UNSUPPORTED_SYNTAX),
    ("not x", PARSE_UNSUPPORTED_SYNTAX),
    # Multiple statements (unsupported)
    ("x + y; z", PARSE_SYNTAX_ERROR),
    # Assignment (unsupported)
    ("x = 1", PARSE_SYNTAX_ERROR),
    # Augmented assignment (unsupported)
    ("x += 1", PARSE_SYNTAX_ERROR),
    # Invalid numeric literals
    ("1e", PARSE_SYNTAX_ERROR),
    (".", PARSE_SYNTAX_ERROR),
    ("..", PARSE_SYNTAX_ERROR),
    # Invalid variable names - numbers as leading digit
    ("1x", PARSE_SYNTAX_ERROR),
    # Deeply nested incomplete expressions
    ("((((((", PARSE_SYNTAX_ERROR),
    ("x + (((((", PARSE_SYNTAX_ERROR),
    # Extra operators at start of expression - rejects when invalid syntax
    ("/ x", PARSE_SYNTAX_ERROR),
    ("** x", PARSE_SYNTAX_ERROR),
    # Adjacent operators without operand
    ("x + * y", PARSE_SYNTAX_ERROR),
    # Invalid after power
    ("x **", PARSE_SYNTAX_ERROR),
    ("x ** * y", PARSE_SYNTAX_ERROR),
    # Non-integer/non-float constants - string constants in Python AST
    ('"x"', PARSE_UNSUPPORTED_SYNTAX),
    ("None", PARSE_UNSUPPORTED_SYNTAX),
    # Complex numbers (unsupported)
    ("1+1j", PARSE_UNSUPPORTED_SYNTAX),
]


@pytest.mark.parametrize("source,expected_code", MALFORMED_CORPUS)
def test_parse_corpus_rejects_with_stable_codes(source: str, expected_code: str) -> None:
    """Validate that all malformed inputs raise ParseError with predictable codes."""
    with pytest.raises(ParseError) as exc_info:
        parse_expr(source)
    assert exc_info.value.code == expected_code


def test_parse_corpus_all_raise_parse_error() -> None:
    """Verify every corpus entry raises ParseError (not other exceptions)."""
    for source, _ in MALFORMED_CORPUS:
        with pytest.raises(ParseError):
            parse_expr(source)


def test_parse_fuzz_random_strings() -> None:
    """Fuzz-style test: random strings should not cause uncaught exceptions."""
    random.seed(12345)
    for _ in range(200):
        # Generate random string of printable ASCII characters
        length = random.randint(0, 30)
        chars = ''.join(random.choices(string.printable, k=length))
        # Should either raise ParseError or succeed (not crash)
        try:
            parse_expr(chars)
        except ParseError:
            pass  # Expected - malformed input rejected


def test_parse_fuzz_deeply_nested_parens() -> None:
    """Fuzz-style test: deeply nested parentheses should not cause stack overflow."""
    for depth in [50, 100, 200]:
        source = "(" * depth + "x" + ")" * depth
        # Should either parse or raise ParseError, not crash
        try:
            result = parse_expr(source)
            # Valid nested parens are simplified to just x
            assert result == Symbol("x")
        except ParseError:
            pass  # Expected for malformed nesting


def test_parse_fuzz_extreme_exponent() -> None:
    """Fuzz-style test: extremely large exponents should not cause overflow crashes."""
    for exp in ["10**10", "10**100", "10**1000"]:
        try:
            parse_expr(exp)
        except ParseError:
            pass


def test_parse_fuzz_empty_mixed() -> None:
    """Fuzz-style test: mix of valid and invalid tokens randomly combined."""
    random.seed(54321)
    valid = ["x", "y", "1", "2.5", "(", ")"]
    invalid = ["f", "//", "%", "<<", "&", "|", "^", "and", "or"]
    for _ in range(50):
        # Occasionally create random expression strings
        tokens = random.choices(valid + invalid, k=random.randint(1, 10))
        source = " ".join(tokens)
        try:
            parse_expr(source)
        except ParseError:
            pass  # Expected for malformed
        except Exception as e:
            # No other exceptions should propagate
            pytest.fail(f"Unexpected exception {type(e).__name__}: {source}")


def test_parse_addition() -> None:
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
