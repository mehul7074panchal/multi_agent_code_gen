import re

from llm.llm_client import call_llm


SYSTEM_PROMPT = """You are an expert Python test engineer specializing in pytest.

Generate comprehensive test cases for Python code with both positive and negative scenarios.

Rules:
- Return ONLY Python code
- No markdown
- No explanations
- No comments outside code
- Write pytest-style test cases
- Include both positive (happy path) and negative (edge cases, errors) test cases
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


def normalize_generated_code_imports(test_code: str) -> str:
    """
    Replace common placeholder module imports with the sandbox module name.
    """
    placeholder_modules = [
        "your_module",
        "module_name",
        "solution",
        "main",
        "app",
    ]

    normalized = test_code

    for module_name in placeholder_modules:
        normalized = re.sub(
            rf"from\s+{module_name}\s+import\s+",
            "from generated_code import ",
            normalized,
        )
        normalized = re.sub(
            rf"import\s+{module_name}\b",
            "import generated_code",
            normalized,
        )

    normalized = re.sub(
        r"\s*#\s*replace ['\"]?generated_code['\"]? with the actual module name",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\s*#\s*replace ['\"]?your_module['\"]? with the actual module name",
        "",
        normalized,
        flags=re.IGNORECASE,
    )

    return normalized


def generate_test_cases(python_code: str, code_description: str = "") -> str:
    """
    Generate comprehensive pytest test cases for the given Python code.
    
    Args:
        python_code: The Python code to write tests for
        code_description: Optional description of what the code does
    
    Returns:
        String containing pytest test code with positive and negative test cases
    """
    if not python_code or not python_code.strip():
        raise ValueError("Python code cannot be empty.")

    test_prompt = f"""Write comprehensive pytest test cases for the following Python code:

{python_code.strip()}

{f"Context: {code_description}" if code_description else ""}

Requirements:
- Generate multiple positive test cases (happy path, normal scenarios)
- Generate multiple negative test cases (edge cases, errors, invalid inputs)
- Test all functions and methods
- Test error handling and exceptions
- Use pytest fixtures for setup/teardown
- Use parameterization for similar test scenarios
- Include docstrings in the test module
- Make tests independent and isolated
- Import all tested functions/classes from generated_code
- Do not use imports like your_module, main, solution, or app
- Only test behavior visible in the code above
- Do not invent validation rules that are not present in the code

Return only valid Python pytest code."""

    response = call_llm(SYSTEM_PROMPT, test_prompt)
    return normalize_generated_code_imports(clean_code_response(response))
