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

Return only valid Python pytest code."""

    response = call_llm(SYSTEM_PROMPT, test_prompt)
    return clean_code_response(response)
