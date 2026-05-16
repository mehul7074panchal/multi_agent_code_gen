import json
import re

from llm.llm_client import call_llm


SYSTEM_PROMPT = """You are a software requirements analyst.

Extract clear structured requirements from the user's coding request.

Return ONLY valid JSON.

JSON fields:
- task
- language
- requirements

Split numbered or sentence-based requests into separate requirement items.
Do not merge independent requirements into one item.
"""


def _split_prompt_requirements(user_prompt: str) -> list[str]:
    prompt = user_prompt.strip()
    numbered_items = [
        item.strip(" .")
        for item in re.split(r"(?:^|\s)\d+[\).]?\s+", prompt)
        if item.strip(" .")
    ]

    if len(numbered_items) > 1:
        return numbered_items

    sentence_items = [
        item.strip(" .")
        for item in re.split(r"(?<=[.!?])\s+", prompt)
        if item.strip(" .")
    ]

    return sentence_items or [prompt]


def _fallback_requirements(user_prompt: str) -> dict:
    return {
        "task": user_prompt.strip(),
        "language": "Python",
        "requirements": _split_prompt_requirements(user_prompt),
    }


def extract_requirements(user_prompt: str) -> dict:
    """
    Extract structured coding requirements from a natural language prompt.
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    prompt = f"""Analyze this coding request and extract structured requirements:

{user_prompt.strip()}

Return only valid JSON with this shape:
{{
  "task": "Task name",
  "language": "Python",
  "requirements": [
    "requirement 1",
    "requirement 2"
  ]
}}

Rules:
- Split each numbered item into a separate requirement.
- Split independent sentences into separate requirements.
- Preserve details about edge cases, error handling, type hints, and docstrings.
- Do not combine all requirements into one string."""

    response = call_llm(SYSTEM_PROMPT, prompt)

    try:
        requirements = json.loads(response)
    except json.JSONDecodeError:
        return _fallback_requirements(user_prompt)

    if not isinstance(requirements, dict):
        return _fallback_requirements(user_prompt)

    task = requirements.get("task")
    language = requirements.get("language")
    requirement_items = requirements.get("requirements")

    if not isinstance(task, str) or not task.strip():
        return _fallback_requirements(user_prompt)

    if not isinstance(language, str) or not language.strip():
        requirements["language"] = "Python"

    if not isinstance(requirement_items, list) or not all(
        isinstance(item, str) and item.strip() for item in requirement_items
    ):
        return _fallback_requirements(user_prompt)

    if len(requirement_items) == 1:
        split_items = _split_prompt_requirements(user_prompt)
        if len(split_items) > 1:
            requirements["requirements"] = split_items

    requirements["requirements"] = [
        item.strip() for item in requirements["requirements"] if item.strip()
    ]

    return requirements
