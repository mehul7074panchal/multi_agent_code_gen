"""
Demo script to test the multi-agent code generation system.
Run this to verify all components are working before launching the Gradio UI.
"""

import json
from datetime import datetime

from agents.router import route_request
from agents.requirements_agent import extract_requirements
from agents.python_coder import generate_python_code
from agents.test_writer import generate_test_cases
from executor import run_tests
from agents.evaluator import generate_coverage_report_json


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def demo_workflow():
    """Run a complete demo workflow"""
    
    print_section("🚀 Multi-Agent Code Generation System - Demo")
    print("Starting workflow demonstration...\n")
    
    # User prompt
    user_prompt = "Create a palindrome checker function"
    print(f"📝 User Prompt: {user_prompt}\n")
    
    # Step 1: Router
    print_section("Step 1: Router Agent")
    print("Analyzing request type...")
    route_result = route_request(user_prompt)
    print(f"✓ Task Type: {route_result['task_type'].upper()}")
    print(f"✓ Target Agent: {route_result['target_agent']}\n")
    
    # Step 2: Requirements
    print_section("Step 2: Requirements Agent")
    print("Extracting structured requirements...")
    requirements = extract_requirements(user_prompt)
    print(f"✓ Task: {requirements['task']}")
    print(f"✓ Language: {requirements['language']}")
    print(f"✓ Requirements ({len(requirements['requirements'])}):")
    for i, req in enumerate(requirements['requirements'], 1):
        print(f"  {i}. {req}")
    print()
    
    # Step 3: Code Generation
    print_section("Step 3: Code Generation Agent")
    print("Generating Python code...")
    generated_code = generate_python_code(user_prompt)
    print("✓ Generated Code:")
    print("-" * 80)
    print(generated_code)
    print("-" * 80)
    print(f"\n✓ Code Statistics:")
    print(f"  - Lines: {len(generated_code.splitlines())}")
    print(f"  - Functions: {generated_code.count('def ')}")
    print(f"  - Classes: {generated_code.count('class ')}\n")
    
    # Step 4: Test Generation
    print_section("Step 4: Test Generation Agent")
    print("Generating pytest test cases...")
    generated_tests = generate_test_cases(generated_code)
    test_count = generated_tests.count("def test_")
    print("✓ Generated Tests:")
    print("-" * 80)
    print(generated_tests)
    print("-" * 80)
    print(f"\n✓ Test Statistics:")
    print(f"  - Test Functions: {test_count}\n")
    
    # Step 5: Execution
    print_section("Step 5: Execution Agent")
    print("Running tests in sandbox...")
    execution_results = run_tests(generated_code, generated_tests)
    print("✓ Execution Results:")
    print(f"  - Success: {execution_results['success']}")
    print(f"  - Return Code: {execution_results['return_code']}")
    
    stdout = execution_results["stdout"]
    passed = stdout.count(" PASSED")
    failed = stdout.count(" FAILED")
    print(f"  - Passed: {passed}")
    print(f"  - Failed: {failed}")
    print("\n✓ Test Output:")
    print("-" * 80)
    print(execution_results["stdout"])
    print("-" * 80)
    
    if execution_results["stderr"]:
        print("✗ Errors:")
        print(execution_results["stderr"])
    print()
    
    # Step 6: Evaluation
    print_section("Step 6: Evaluation Agent")
    print("Computing coverage metrics...")
    evaluation_results_json = generate_coverage_report_json(generated_code, generated_tests)
    evaluation_results = json.loads(evaluation_results_json)
    
    print("✓ Evaluation Results:")
    print(f"  - Coverage: {evaluation_results['overall_coverage_percentage']}%")
    print(f"  - Total Functions: {evaluation_results['total_functions']}")
    print(f"  - Tested Functions: {evaluation_results['tested_functions']}")
    print(f"  - Untested Functions: {evaluation_results['untested_functions']}")
    
    if "functions" in evaluation_results:
        print("\n  Function Coverage:")
        for func_name, func_data in evaluation_results["functions"].items():
            print(f"    - {func_name}: {func_data['coverage_percentage']}% ({func_data['test_cases']} tests)")
    print()
    
    # Summary
    print_section("✨ Workflow Completed Successfully")
    print("All agents executed without errors!")
    print("\nSummary:")
    print(f"  - Code Lines: {len(generated_code.splitlines())}")
    print(f"  - Test Cases: {test_count}")
    print(f"  - Tests Passed: {passed}")
    print(f"  - Code Coverage: {evaluation_results['overall_coverage_percentage']}%")
    print(f"\n💡 Tip: Run 'python app.py' to launch the Gradio UI dashboard!\n")


if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print_section("❌ Error During Demo")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify API key is set in .env file")
        print("2. Check internet connection for LLM API calls")
        print("3. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("4. Review the error message above for specific issues")
