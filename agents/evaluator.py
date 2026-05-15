from llm.llm_client import call_llm


SYSTEM_PROMPT = """You are an expert Python test evaluator and code coverage analyst.

Evaluate test cases and provide detailed coverage analysis and quality metrics.

Rules:
- Return ONLY Python code or JSON output as specified
- No markdown
- No explanations outside code blocks
- Provide comprehensive test coverage analysis
- Evaluate test quality (positive/negative cases, edge cases)
- Estimate code coverage percentage
- Identify untested code paths
- Provide recommendations for missing tests
- Assess test independence and isolation
- Check for proper error handling coverage
- Analyze parameterization efficiency
- Do not include example usage unless the user asks for it
"""


def clean_response(response: str) -> str:
    """Remove common markdown code fences from an LLM response."""
    code = response.strip()

    if code.startswith("```python"):
        code = code.removeprefix("```python").strip()
    elif code.startswith("```json"):
        code = code.removeprefix("```json").strip()
    elif code.startswith("```py"):
        code = code.removeprefix("```py").strip()
    elif code.startswith("```"):
        code = code.removeprefix("```").strip()

    if code.endswith("```"):
        code = code.removesuffix("```").strip()

    return code


def evaluate_test_coverage(source_code: str, test_code: str, output_format: str = "json") -> str:
    """
    Evaluate test cases and generate coverage analysis.
    
    Args:
        source_code: The Python source code being tested
        test_code: The pytest test code to evaluate
        output_format: "json" for structured output, "python" for Python report generator
    
    Returns:
        String containing test coverage analysis and metrics
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty.")
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    eval_prompt = f"""Evaluate the following test cases and provide detailed coverage analysis.

SOURCE CODE:
{source_code.strip()}

TEST CODE:
{test_code.strip()}

Analyze and provide (in {output_format} format):
1. Estimated code coverage percentage (0-100%)
2. List of tested functions/methods
3. List of untested or partially tested functions/methods
4. Coverage breakdown by function
5. Number of positive test cases
6. Number of negative test cases
7. Edge cases coverage assessment
8. Error handling coverage assessment
9. Missing test scenarios (list 3-5 most important)
10. Overall test quality score (0-10)
11. Recommendations for improving coverage
12. Risk assessment for untested code paths

{f"Return as {output_format}." if output_format == "json" else "Return as Python code that generates this report."}"""

    response = call_llm(SYSTEM_PROMPT, eval_prompt)
    return clean_response(response)


def generate_coverage_report_json(source_code: str, test_code: str) -> str:
    """
    Generate a detailed coverage report in JSON format.
    
    Args:
        source_code: The Python source code being tested
        test_code: The pytest test code to evaluate
    
    Returns:
        String containing JSON coverage report with all metrics
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty.")
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    report_prompt = f"""Analyze the following source code and test code, then generate a comprehensive coverage report in JSON format.

SOURCE CODE:
{source_code.strip()}

TEST CODE:
{test_code.strip()}

Generate JSON with the following structure:
{{
    "overall_coverage_percentage": <0-100>,
    "total_functions": <number>,
    "tested_functions": <number>,
    "untested_functions": <number>,
    "functions": {{
        "<function_name>": {{
            "tested": <true/false>,
            "coverage_percentage": <0-100>,
            "test_cases": <number>
        }}
    }},
    "test_metrics": {{
        "total_tests": <number>,
        "positive_tests": <number>,
        "negative_tests": <number>,
        "edge_case_tests": <number>,
        "error_handling_tests": <number>
    }},
    "coverage_assessment": {{
        "edge_cases": "<good/fair/poor>",
        "error_handling": "<good/fair/poor>",
        "parameterization": "<good/fair/poor>"
    }},
    "untested_code_paths": [<list of untested functions/methods>],
    "missing_test_scenarios": [<list of 3-5 important missing scenarios>],
    "quality_score": <0-10>,
    "recommendations": [<list of improvement recommendations>],
    "risk_assessment": "<low/medium/high>"
}}

Return only valid JSON."""

    response = call_llm(SYSTEM_PROMPT, report_prompt)
    return clean_response(response)


def generate_coverage_report_code(source_code: str, test_code: str) -> str:
    """
    Generate Python code that creates a detailed coverage report.
    
    Args:
        source_code: The Python source code being tested
        test_code: The pytest test code to evaluate
    
    Returns:
        String containing Python code to generate coverage reports
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty.")
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    report_prompt = f"""Generate Python code that analyzes and reports on test coverage.

SOURCE CODE:
{source_code.strip()}

TEST CODE:
{test_code.strip()}

Create a Python module with:
1. A function to parse and analyze test coverage
2. A function to calculate coverage percentage
3. A function to identify untested code paths
4. A function to generate a formatted coverage report
5. A function to suggest missing tests
6. A ReportGenerator class that consolidates all analysis
7. Functions to output in multiple formats (text, JSON, HTML)

The code should:
- Use AST parsing to analyze source code structure
- Use regex/parsing to analyze test code
- Calculate accurate coverage metrics
- Generate clear, actionable recommendations
- Be production-ready and well-documented

Return only valid Python code."""

    response = call_llm(SYSTEM_PROMPT, report_prompt)
    return clean_response(response)


def analyze_test_quality(test_code: str, test_name: str = "") -> str:
    """
    Analyze the quality of test cases.
    
    Args:
        test_code: The pytest test code to analyze
        test_name: Optional name of the test file/module
    
    Returns:
        String containing JSON with quality metrics
    """
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    quality_prompt = f"""Analyze the quality of these pytest test cases and return JSON metrics.

TEST CODE:
{test_code.strip()}

{f"Test Name: {test_name}" if test_name else ""}

Provide JSON with:
1. Number of tests
2. Test count by category (positive, negative, edge cases, error handling)
3. Average test length (lines of code)
4. Fixture usage score (0-10)
5. Parameterization score (0-10)
6. Assertion quality score (0-10)
7. Test independence score (0-10)
8. Documentation quality score (0-10)
9. Mock/patch usage score (0-10)
10. Overall test suite quality score (0-10)
11. Issues found (list of problems)
12. Improvement suggestions (list)

Return as valid JSON only."""

    response = call_llm(SYSTEM_PROMPT, quality_prompt)
    return clean_response(response)