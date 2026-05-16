import ast
import json


def generate_coverage_report_json(source_code: str, test_code: str) -> str:
    """
    Generate a deterministic lightweight test coverage report.

    This is not runtime line coverage. It is a static MVP report based on
    function names, imports, assertions, and pytest test functions.
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty.")

    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    source_functions = _get_function_names(source_code)
    test_functions = _get_test_function_nodes(test_code)
    test_text_by_name = {
        node.name: ast.get_source_segment(test_code, node) or "" for node in test_functions
    }

    tested_functions = [
        function_name
        for function_name in source_functions
        if _is_function_referenced(function_name, test_code)
    ]
    untested_functions = [
        function_name
        for function_name in source_functions
        if function_name not in tested_functions
    ]

    total_functions = len(source_functions)
    tested_count = len(tested_functions)
    overall_coverage = round((tested_count / total_functions) * 100, 2) if total_functions else 0

    metrics = _calculate_test_metrics(test_text_by_name)

    report = {
        "overall_coverage_percentage": overall_coverage,
        "total_functions": total_functions,
        "tested_functions": tested_count,
        "untested_functions": len(untested_functions),
        "functions": {
            function_name: {
                "tested": function_name in tested_functions,
                "coverage_percentage": 100 if function_name in tested_functions else 0,
                "test_cases": _count_tests_for_function(function_name, test_text_by_name),
            }
            for function_name in source_functions
        },
        "test_metrics": metrics,
        "coverage_assessment": {
            "edge_cases": _rate_count(metrics["edge_case_tests"]),
            "error_handling": _rate_count(metrics["error_handling_tests"]),
            "parameterization": "good" if "@pytest.mark.parametrize" in test_code else "poor",
        },
        "untested_code_paths": untested_functions,
        "missing_test_scenarios": _suggest_missing_tests(untested_functions, metrics),
        "quality_score": _calculate_quality_score(overall_coverage, metrics),
        "recommendations": _build_recommendations(untested_functions, metrics),
        "risk_assessment": _risk_assessment(overall_coverage, metrics),
    }

    return json.dumps(report, indent=2)


def evaluate_result(
    generated_code: str,
    generated_tests: str,
    execution_result: dict,
) -> dict:
    """
    Evaluate generated code quality using the pytest execution result.
    """
    if not generated_code or not generated_code.strip():
        raise ValueError("Generated code cannot be empty.")

    if not generated_tests or not generated_tests.strip():
        raise ValueError("Generated tests cannot be empty.")

    if not isinstance(execution_result, dict):
        raise ValueError("Execution result must be a dictionary.")

    tests_passed = bool(execution_result.get("success"))
    coverage_report = json.loads(generate_coverage_report_json(generated_code, generated_tests))

    if tests_passed:
        score = max(7, coverage_report["quality_score"])
        return {
            "score": score,
            "tests_passed": True,
            "summary": "Generated code passed the pytest suite.",
            "strengths": ["Tests completed successfully."],
            "issues": coverage_report["recommendations"],
        }

    return {
        "score": min(3, coverage_report["quality_score"]),
        "tests_passed": False,
        "summary": f"Generated code did not pass the pytest suite. Return code: {execution_result.get('return_code')}.",
        "strengths": [],
        "issues": _extract_failure_detail(
            str(execution_result.get("stdout") or ""),
            str(execution_result.get("stderr") or ""),
        ),
    }


def evaluate_test_coverage(source_code: str, test_code: str, output_format: str = "json") -> str:
    if output_format != "json":
        raise ValueError("Only json output_format is supported for the MVP evaluator.")

    return generate_coverage_report_json(source_code, test_code)


def analyze_test_quality(test_code: str, test_name: str = "") -> str:
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    metrics = _calculate_test_metrics(
        {node.name: ast.get_source_segment(test_code, node) or "" for node in _get_test_function_nodes(test_code)}
    )

    report = {
        "test_name": test_name,
        "test_metrics": metrics,
        "quality_score": _calculate_quality_score(0, metrics),
    }

    return json.dumps(report, indent=2)


def _get_function_names(source_code: str) -> list[str]:
    tree = ast.parse(source_code)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def _get_test_function_nodes(test_code: str) -> list[ast.FunctionDef]:
    tree = ast.parse(test_code)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def _is_function_referenced(function_name: str, test_code: str) -> bool:
    tree = ast.parse(test_code)
    return any(
        isinstance(node, ast.Name) and node.id == function_name for node in ast.walk(tree)
    )


def _calculate_test_metrics(test_text_by_name: dict[str, str]) -> dict:
    total_tests = len(test_text_by_name)
    positive_tests = 0
    negative_tests = 0
    edge_case_tests = 0
    error_handling_tests = 0

    for test_name, test_text in test_text_by_name.items():
        searchable_text = f"{test_name}\n{test_text}".lower()

        is_error_test = "pytest.raises" in searchable_text or "exception" in searchable_text
        is_edge_test = any(
            keyword in searchable_text
            for keyword in ["edge", "zero", "empty", "none", "negative", "invalid", "large"]
        )
        is_negative_test = is_error_test or any(
            keyword in searchable_text
            for keyword in ["negative", "invalid", "error", "raises", "fail"]
        )

        if is_negative_test:
            negative_tests += 1
        else:
            positive_tests += 1

        if is_edge_test:
            edge_case_tests += 1

        if is_error_test:
            error_handling_tests += 1

    return {
        "total_tests": total_tests,
        "positive_tests": positive_tests,
        "negative_tests": negative_tests,
        "edge_case_tests": edge_case_tests,
        "error_handling_tests": error_handling_tests,
    }


def _count_tests_for_function(function_name: str, test_text_by_name: dict[str, str]) -> int:
    return sum(1 for test_text in test_text_by_name.values() if function_name in test_text)


def _rate_count(count: int) -> str:
    if count >= 3:
        return "good"
    if count >= 1:
        return "fair"
    return "poor"


def _suggest_missing_tests(untested_functions: list[str], metrics: dict) -> list[str]:
    suggestions = [f"Add tests for {function_name}." for function_name in untested_functions]

    if metrics["negative_tests"] == 0:
        suggestions.append("Add negative tests for invalid inputs.")

    if metrics["edge_case_tests"] == 0:
        suggestions.append("Add edge case tests.")

    if metrics["error_handling_tests"] == 0:
        suggestions.append("Add tests for error handling.")

    return suggestions[:5]


def _calculate_quality_score(overall_coverage: float, metrics: dict) -> int:
    score = round(overall_coverage / 20)

    if metrics["total_tests"] > 0:
        score += 2

    if metrics["negative_tests"] > 0:
        score += 1

    if metrics["edge_case_tests"] > 0:
        score += 1

    if metrics["error_handling_tests"] > 0:
        score += 1

    return max(0, min(10, score))


def _build_recommendations(untested_functions: list[str], metrics: dict) -> list[str]:
    recommendations = _suggest_missing_tests(untested_functions, metrics)
    return recommendations or ["Test coverage looks reasonable for the MVP."]


def _risk_assessment(overall_coverage: float, metrics: dict) -> str:
    if overall_coverage < 50 or metrics["total_tests"] == 0:
        return "high"
    if overall_coverage < 80 or metrics["negative_tests"] == 0:
        return "medium"
    return "low"


def _extract_failure_detail(stdout: str, stderr: str) -> list[str]:
    details = []

    if stderr.strip():
        details.append(_truncate_text(stderr.strip()))

    failure_lines = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip()
        and (
            "error" in line.lower()
            or "failed" in line.lower()
            or "assert" in line.lower()
            or "importerror" in line.lower()
            or "modulenotfounderror" in line.lower()
        )
    ]

    if failure_lines:
        details.append(_truncate_text("\n".join(failure_lines[:8])))

    return details or ["Tests failed. Inspect stdout and stderr for details."]


def _truncate_text(text: str, limit: int = 700) -> str:
    if len(text) <= limit:
        return text

    return text[:limit].rstrip() + "..."
