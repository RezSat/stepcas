import json
from subprocess import run
import sys


def test_cli_simplify_steps() -> None:
    completed = run(
        [sys.executable, "-m", "stepcas.cli", "simplify", "x + 0 + 2 + 3", "--steps"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "result: 5 + x" in completed.stdout


def test_cli_simplify_json_trace_result() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "simplify",
            "x + 0 + 2 + 3",
            "--steps",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["object"] == "trace_result"
    assert payload["schema_version"] == "stepcas.v1"
    assert payload["data"]["expr"]["kind"] == "add"


def test_cli_diff_json_expression_result() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "diff",
            "x**2",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["object"] == "expr"
    assert payload["schema_version"] == "stepcas.v1"
    assert payload["data"]["kind"] == "mul"


def test_cli_solve_json_result() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "solve",
            "2*x + 3",
            "11",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["object"] == "linear_solve_result"
    assert payload["schema_version"] == "stepcas.v1"
    assert payload["data"]["kind"] == "solved"
    assert payload["data"]["variable"] == "x"
    assert payload["data"]["value"] == {"kind": "number", "number_type": "int", "value": 4}


def test_cli_diff_json_error_payload_contains_code_and_message() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "diff",
            "x**y",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "differentiate.non_constant_exponent"
    assert "Only constant exponents" in payload["error"]["message"]
