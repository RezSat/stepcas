from __future__ import annotations


def validate_target_variable(
    variable: object,
    *,
    error_cls: type[Exception],
    code: str,
) -> str:
    if isinstance(variable, str) and variable and variable.isidentifier():
        return variable
    raise error_cls(
        "Target variable must be a single symbol name",
        code=code,
    )
