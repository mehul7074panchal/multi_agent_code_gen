"""
Agents module for multi-agent code generation system.

This module contains specialized agents for different code generation tasks:
- python_coder: Generates Python code from natural language descriptions
- test_writer: Generates pytest test cases with positive and negative scenarios
- evaluator: Evaluates test cases and analyzes code coverage
"""

from .python_coder import generate_python_code
from .test_writer import generate_test_cases
from .evaluator import (
    evaluate_test_coverage,
    generate_coverage_report_json,
    generate_coverage_report_code,
    analyze_test_quality,
)

__all__ = [
    "generate_python_code",
    "generate_test_cases",
    "evaluate_test_coverage",
    "generate_coverage_report_json",
    "generate_coverage_report_code",
    "analyze_test_quality",
]
