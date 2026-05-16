import json

from llm.llm_client import call_llm


SYSTEM_PROMPT = """You are a software requirements analyst.

Extract structured coding requirements from the user's request.

Return ONLY valid JSON.

Required JSON fields:
- language
- task_type
- function_name
- parameters
- expected_output
- special_requirements
- original_prompt

Rules:
- Infer reasonable defaults when possible
- Default language to Python if not specified
- Keep parameter names simple
- Use null when a field cannot be inferred
- Use an empty list when no parameters or special requirements are found
- Do not include explanations
- Return valid JSON only
"""


FALLBACK_LANGUAGE = "Python"
FALLBACK_TASK_TYPE = "function"


def _fallback_requirements(user_prompt: str) -> dict:
    """Return a stable requirements shape when LLM extraction cannot be parsed."""
    return {
        "language": FALLBACK_LANGUAGE,
        "task_type": FALLBACK_TASK_TYPE,
        "function_name": None,
        "parameters": [],
        "expected_output": None,
        "special_requirements": [],
        "original_prompt": user_prompt,
    }


def _clean_json_response(response: str) -> str:
    """Remove common markdown fences so json.loads can parse the response."""
    cleaned_response = response.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.removeprefix("```json").strip()
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.removeprefix("```").strip()

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response.removesuffix("```").strip()

    return cleaned_response


def _normalize_list(value: object) -> list[str]:
    """Keep only clean string values from list-like fields."""
    if not isinstance(value, list):
        return []

    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _normalize_optional_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    normalized_value = value.strip()
    return normalized_value or None


def _normalize_requirements(requirements: dict, user_prompt: str) -> dict:
    """Ensure the parsed LLM result always uses the expected dictionary shape."""
    language = _normalize_optional_string(requirements.get("language"))
    task_type = _normalize_optional_string(requirements.get("task_type"))

    return {
        "language": language or FALLBACK_LANGUAGE,
        "task_type": task_type or FALLBACK_TASK_TYPE,
        "function_name": _normalize_optional_string(requirements.get("function_name")),
        "parameters": _normalize_list(requirements.get("parameters")),
        "expected_output": _normalize_optional_string(requirements.get("expected_output")),
        "special_requirements": _normalize_list(
            requirements.get("special_requirements")
        ),
        "original_prompt": user_prompt,
    }


def extract_requirements(user_prompt: str) -> dict:
    """
    Extract structured coding requirements from a natural-language user prompt.
    """
    if not isinstance(user_prompt, str) or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    extraction_prompt = f"""Analyze this coding request and extract structured requirements:

{user_prompt.strip()}

Return only valid JSON with this exact shape:
{{
  "language": "Python",
  "task_type": "function",
  "function_name": "example_name",
  "parameters": ["parameter_name"],
  "expected_output": "output_type",
  "special_requirements": ["special behavior"],
  "original_prompt": "{user_prompt}"
}}

Extraction guidance:
- task_type should be concise, such as function, class, script, api, or cli
- function_name should be snake_case when a function is requested
- parameters should contain simple names only, not full type annotations
- expected_output should describe the returned value or observable result
- special_requirements should capture constraints, edge cases, algorithms, or formatting rules
- original_prompt must match the user's request exactly"""

    try:
        response = call_llm(SYSTEM_PROMPT, extraction_prompt)
    except Exception:
        return _fallback_requirements(user_prompt)

    if not response or not response.strip():
        return _fallback_requirements(user_prompt)

    try:
        parsed_requirements = json.loads(_clean_json_response(response))
    except json.JSONDecodeError:
        return _fallback_requirements(user_prompt)

    if not isinstance(parsed_requirements, dict):
        return _fallback_requirements(user_prompt)

    return _normalize_requirements(parsed_requirements, user_prompt)
