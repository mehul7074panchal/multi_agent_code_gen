SQL_KEYWORDS = [
    "sql",
    "query",
    "database",
    "select",
    "join",
    "group by",
]


def route_request(user_prompt: str) -> dict:
    """
    Route a coding request to the correct agent using simple keyword detection.
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty")

    normalized_prompt = user_prompt.lower()

    if any(keyword in normalized_prompt for keyword in SQL_KEYWORDS):
        return {
            "task_type": "sql",
            "target_agent": "sql_coder",
        }

    return {
        "task_type": "python",
        "target_agent": "python_coder",
    }
