from __future__ import annotations


ERROR_DOMAIN_PARSE = "parse"
ERROR_DOMAIN_DIFFERENTIATE = "differentiate"
ERROR_DOMAIN_REWRITE = "rewrite"

PARSE_SYNTAX_ERROR = "parse.syntax"
PARSE_UNSUPPORTED_SYNTAX = "parse.unsupported_syntax"

DIFFERENTIATE_NON_CONSTANT_EXPONENT = "differentiate.non_constant_exponent"
DIFFERENTIATE_UNSUPPORTED_EXPRESSION = "differentiate.unsupported_expression"

REWRITE_INVALID_RULE_RESULT = "rewrite.invalid_rule_result"


class StepcasError(Exception):
    """Base exception for all public stepcas domain errors."""

    domain: str
    code: str

    def __init__(self, message: str, *, domain: str, code: str) -> None:
        super().__init__(message)
        self.domain = domain
        self.code = code


class ParseError(StepcasError, ValueError):
    def __init__(self, message: str, *, code: str = PARSE_UNSUPPORTED_SYNTAX) -> None:
        super().__init__(message, domain=ERROR_DOMAIN_PARSE, code=code)


class DifferentiationError(StepcasError, ValueError):
    def __init__(
        self,
        message: str,
        *,
        code: str = DIFFERENTIATE_UNSUPPORTED_EXPRESSION,
    ) -> None:
        super().__init__(message, domain=ERROR_DOMAIN_DIFFERENTIATE, code=code)


class RewriteError(StepcasError, ValueError):
    def __init__(self, message: str, *, code: str = REWRITE_INVALID_RULE_RESULT) -> None:
        super().__init__(message, domain=ERROR_DOMAIN_REWRITE, code=code)


__all__ = [
    "DIFFERENTIATE_NON_CONSTANT_EXPONENT",
    "DIFFERENTIATE_UNSUPPORTED_EXPRESSION",
    "DifferentiationError",
    "ERROR_DOMAIN_DIFFERENTIATE",
    "ERROR_DOMAIN_PARSE",
    "ERROR_DOMAIN_REWRITE",
    "PARSE_SYNTAX_ERROR",
    "PARSE_UNSUPPORTED_SYNTAX",
    "ParseError",
    "REWRITE_INVALID_RULE_RESULT",
    "RewriteError",
    "StepcasError",
]
