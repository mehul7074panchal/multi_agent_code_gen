import ast


def validate_python_code(code: str) -> dict:
    """
    Validate generated Python code with AST parsing.
    """
    if not code or not code.strip():
        return {
            "valid": False,
            "error": "Generated code cannot be empty.",
        }

    try:
        ast.parse(code)
    except SyntaxError as error:
        return {
            "valid": False,
            "error": f"Python syntax error: {error.msg} at line {error.lineno}.",
        }

    return {
        "valid": True,
        "error": None,
    }
