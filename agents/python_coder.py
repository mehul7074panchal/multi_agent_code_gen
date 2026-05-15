from llm.llm_client import call_llm


SYSTEM_PROMPT = """You are an expert Python software engineer.

Generate clean executable Python code.

Rules:
- Return ONLY Python code
- No markdown
- No explanations
- No comments outside code
- Keep implementation simple and readable
- Prefer functions over classes unless necessary
- Include type hints when they make the code clearer
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


def generate_python_code(user_prompt: str) -> str:
    """
    Generate executable Python code from a natural language user request.
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    coding_prompt = f"""Create Python code for this request:

{user_prompt.strip()}

Return only valid Python code."""

    response = call_llm(SYSTEM_PROMPT, coding_prompt)
    return clean_code_response(response)
