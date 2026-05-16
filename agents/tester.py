from utils.import_normalizer import normalize_generated_code_imports


SYSTEM_PROMPT = """You are an expert Python test engineer specializing in pytest.

Generate practical pytest test cases for Python code.

Rules:
- Return ONLY Python code
- No markdown
- No explanations
- No comments outside code
- Write pytest-style test cases
- Include positive, edge-case, and error tests only when supported by the code
- Use descriptive test names
- Use assertions that clearly state expected behavior
- Include fixtures and helper functions when needed
- Use pytest.raises for exception testing
- Parameterize tests when testing multiple similar scenarios
- Each test should be independent and self-contained
- Include docstrings for test modules and test classes
- Mock external dependencies when necessary
- Do not include example usage unless the user asks for it
- Import generated functions and classes from generated_code
- Do not import from your_module, main, solution, app, or unknown modules
- Only test behavior that is visible in the provided code
- Do not assume extra validation unless it exists in the provided code
- Do not treat type hints as runtime validation
- Do not expect TypeError for floats, strings, or None unless the code explicitly raises it
- Prefer tests that should pass for the provided code
"""


def clean_code_response(response: str) -> str:
    """Remove common markdown code fences from an LLM response."""
    code = response.strip()

    if code.startswith("```python"):
        code = code.removeprefix("```python").strip()
    elif code.startswith("```py"):
        code = code.removeprefix("```py").strip()
    elif code.startswith("```"):
        code = code.removeprefix("```").strip()

    if code.endswith("```"):
        code = code.removesuffix("```").strip()

    return code


def generate_test_cases(python_code: str, code_description: str = "") -> str:
    """
    Generate pytest test cases for the given Python code.
    """
    if not python_code or not python_code.strip():
        raise ValueError("Python code cannot be empty.")

    test_prompt = f"""Write comprehensive pytest test cases for the following Python code:

{python_code.strip()}

{f"Context: {code_description}" if code_description else ""}

Requirements:
- Generate positive tests for normal scenarios
- Generate edge-case tests that match the actual code behavior
- Generate error tests only when the code explicitly raises exceptions
- Test all functions and methods
- Test error handling and exceptions only when present
- Use pytest fixtures for setup/teardown only when useful
- Use parameterization for similar test scenarios
- Include docstrings in the test module
- Make tests independent and isolated
- Import all tested functions/classes from generated_code
- Do not use imports like your_module, main, solution, or app
- Only test behavior visible in the code above
- Do not invent validation rules that are not present in the code
- Type hints do not count as runtime validation
- Do not expect TypeError for floats, strings, None, or collections unless the code explicitly checks and raises
- Prefer a compact test suite that should pass against the provided code

Return only valid Python pytest code."""

    from llm.llm_client import call_llm

    response = call_llm(SYSTEM_PROMPT, test_prompt)
    return normalize_generated_code_imports(clean_code_response(response))


def generate_tests_from_requirements(requirements: dict) -> str:
    """
    Generate pytest test cases from structured requirements before code exists.
    """
    if not isinstance(requirements, dict):
        raise ValueError("Requirements must be a dictionary.")

    original_prompt = str(requirements.get("original_prompt") or "").strip()
    function_name = str(requirements.get("function_name") or "").strip()

    if not original_prompt and not function_name:
        raise ValueError("Requirements must include an original prompt or function name.")

    requirements_prompt = f"""Write practical pytest test cases for code that will be generated from these structured requirements:

{requirements}

Target module:
- Import generated functions and classes from generated_code

Known target:
- Function name: {function_name or "infer from requirements"}

Requirements:
- Generate tests based only on the structured requirements above
- Test the expected behavior, edge cases, and special requirements
- Import the target function/class from generated_code
- If a function_name is provided, tests must call that exact function name
- Do not test implementation details
- Do not invent validation rules unless the requirements explicitly ask for them
- Type hints do not count as runtime validation
- Prefer tests that should pass for a straightforward implementation

Return only valid Python pytest code."""

    from llm.llm_client import call_llm

    response = call_llm(SYSTEM_PROMPT, requirements_prompt)
    return normalize_generated_code_imports(clean_code_response(response))


def generate_tests(python_code: str, code_description: str = "") -> str:
    """
    Generate pytest test cases for the given Python code.
    """
    return generate_test_cases(python_code, code_description)
