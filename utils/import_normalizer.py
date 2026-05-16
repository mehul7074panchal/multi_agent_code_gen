import re


def normalize_generated_code_imports(test_code: str) -> str:
    """
    Replace common placeholder imports with the sandbox module name.
    """
    if not test_code:
        return test_code

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
        r"\s*#\s*replace ['\"]?(your_module|generated_code)['\"]? with the actual module name",
        "",
        normalized,
        flags=re.IGNORECASE,
    )

    return normalized
