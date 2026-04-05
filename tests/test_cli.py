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
