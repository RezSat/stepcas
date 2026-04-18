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


def test_cli_solve_json_error_payload_for_nonlinear_input() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "solve",
            "x**2",
            "3",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "linear.nonlinear_form"
    assert payload["error"]["message"]


def test_cli_solve_json_error_payload_for_unsupported_symbol_input() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "solve",
            "x + y",
            "3",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "linear.unsupported_symbol"
    assert payload["error"]["message"]


def test_cli_solve_json_error_payload_for_malformed_input() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "solve",
            "(",
            "3",
            "x",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "parse.syntax"
    assert payload["error"]["message"]


def test_cli_poly_degree_text_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "degree",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "4"


def test_cli_poly_degree_json_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "degree",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["object"] == "polynomial_degree"
    assert payload["data"] == 4


def test_cli_poly_coeffs_text_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "coeffs",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "{4: 3, 1: 2, 0: -1}"


def test_cli_poly_coeffs_json_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "coeffs",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["object"] == "polynomial_coefficients"
    data = payload["data"]
    assert int(data["4"]) == 3
    assert int(data["1"]) == 2
    assert int(data["0"]) == -1


def test_cli_poly_coeff_vector_text_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "coeff-vector",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "[3, 0, 0, 2, -1]"


def test_cli_poly_coeff_vector_json_mode() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "3*x**4 + 2*x - 1",
            "x",
            "--operation",
            "coeff-vector",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["object"] == "polynomial_coeff_vector"
    assert payload["data"] == [3, 0, 0, 2, -1]


def test_cli_poly_json_error_for_non_polynomial_form() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "x**-1",
            "x",
            "--operation",
            "degree",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "polynomial.non_polynomial_form"


def test_cli_poly_json_error_for_unsupported_symbol() -> None:
    completed = run(
        [
            sys.executable,
            "-m",
            "stepcas.cli",
            "poly",
            "x + y",
            "x",
            "--operation",
            "degree",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "polynomial.unsupported_symbol"
