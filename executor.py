import subprocess
import sys
from pathlib import Path


SANDBOX_DIR = Path("sandbox")
CODE_FILE = SANDBOX_DIR / "generated_code.py"
TEST_FILE = SANDBOX_DIR / "test_generated_code.py"
TIMEOUT_SECONDS = 10


def run_tests(generated_code: str, generated_tests: str) -> dict:
    """
    Save generated code and tests, run pytest, and return execution results.
    """
    if not generated_code or not generated_code.strip():
        raise ValueError("Generated code cannot be empty.")

    if not generated_tests or not generated_tests.strip():
        raise ValueError("Generated tests cannot be empty.")

    SANDBOX_DIR.mkdir(exist_ok=True)
    CODE_FILE.write_text(generated_code.strip() + "\n", encoding="utf-8")
    TEST_FILE.write_text(generated_tests.strip() + "\n", encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", TEST_FILE.name],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=SANDBOX_DIR,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "success": False,
            "stdout": error.stdout or "",
            "stderr": error.stderr or f"Test execution timed out after {TIMEOUT_SECONDS} seconds.",
            "return_code": -1,
        }

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.returncode,
    }
