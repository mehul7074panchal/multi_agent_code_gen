import json
from concurrent.futures import ThreadPoolExecutor

from agents.python_coder import generate_python_code
from agents.requirements import extract_requirements
from agents.router import route_request
from agents.tester import generate_test_cases, generate_tests_from_requirements
from executor import run_tests
from memory.session_store import session_store
from utils.code_parser import validate_python_code
from utils.import_normalizer import normalize_generated_code_imports


WORKFLOW_GRAPH_EDGES = [
    ("START", "route"),
    ("route", "requirements"),
    ("requirements", "code_generation"),
    ("requirements", "test_generation"),
    ("code_generation", "ast_validation"),
    ("test_generation", "execution"),
    ("ast_validation", "execution"),
    ("execution", "evaluation"),
    ("evaluation", "END"),
]


def _evaluate_solution(generated_code: str, execution_result: dict, generated_tests: str) -> dict:
    from agents.evaluator import generate_coverage_report_json

    coverage_report = json.loads(
        generate_coverage_report_json(generated_code, generated_tests)
    )
    tests_passed = bool(execution_result.get("success"))
    quality_score = int(coverage_report.get("quality_score", 0))

    if tests_passed:
        score = max(7, quality_score)
        summary = "Generated code passed the pytest suite."
        strengths = [
            "Generated code executed successfully.",
            f"Static function coverage is {coverage_report['overall_coverage_percentage']}%.",
        ]
        issues = coverage_report.get("recommendations", [])
    else:
        score = min(3, quality_score)
        summary = (
            "Generated code or generated tests failed during pytest execution. "
            f"Return code: {execution_result.get('return_code')}."
        )
        strengths = []
        issues = _extract_execution_issues(execution_result)

    return {
        "score": score,
        "tests_passed": tests_passed,
        "summary": summary,
        "strengths": strengths,
        "issues": issues,
        "coverage_report": coverage_report,
    }


def _extract_execution_issues(execution_result: dict) -> list[str]:
    stdout = str(execution_result.get("stdout") or "")
    stderr = str(execution_result.get("stderr") or "").strip()

    if stderr:
        return [_truncate_text(stderr)]

    issue_lines = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip()
        and (
            "failed" in line.lower()
            or "error" in line.lower()
            or "did not raise" in line.lower()
            or "assert" in line.lower()
            or "modulenotfounderror" in line.lower()
            or "importerror" in line.lower()
        )
    ]

    if issue_lines:
        return [_truncate_text("\n".join(issue_lines[-8:]))]

    return ["Tests failed. Inspect execution_result stdout and stderr for details."]

# Helper function to truncate long error messages while preserving readability
def _truncate_text(text: str, limit: int = 900) -> str:
    if len(text) <= limit:
        return text

    return text[:limit].rstrip() + "..."


def _build_code_prompt_from_requirements(user_prompt: str, requirements: dict) -> str:
    """Give the code agent the same contract that the test agent uses."""
    function_name = requirements.get("function_name")
    parameters = requirements.get("parameters") or []
    expected_output = requirements.get("expected_output")
    special_requirements = requirements.get("special_requirements") or []

    return f"""Create Python code for this user request:

{user_prompt.strip()}

Structured requirements:
- language: {requirements.get("language", "Python")}
- task_type: {requirements.get("task_type", "function")}
- function_name: {function_name or "infer a clear snake_case name"}
- parameters: {parameters}
- expected_output: {expected_output or "infer from request"}
- special_requirements: {special_requirements}

Follow the structured requirements exactly when they are present."""


def run_workflow(user_prompt: str) -> dict:
    """
    Run the simple linear multi-agent workflow.
    """
    execution = None

    try:
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")

        execution = session_store.create_execution(user_prompt)
        execution.status = "running"
        session_store.save_execution(execution)
        session_store.set_state("user_prompt", user_prompt.strip())
        session_store.set_state("pipeline_status", "running")

        print("Routing request...")
        route = route_request(user_prompt)
        execution.route = route
        session_store.save_result(
            agent="router",
            task=user_prompt,
            report=json.dumps(route, indent=2),
        )

        if route.get("task_type") != "python":
            error_message = "Current MVP supports Python generation only."
            execution.status = "failed"
            execution.error = error_message
            session_store.save_execution(execution)
            session_store.set_state("pipeline_status", "failed")

            return {
                "success": False,
                "error": error_message,
                "route": route,
                "execution_id": execution.execution_id,
            }

        print("Extracting requirements...")
        requirements = extract_requirements(user_prompt)
        execution.requirements = requirements
        session_store.save_result(
            agent="requirements",
            task=user_prompt,
            report=json.dumps(requirements, indent=2),
        )
        code_prompt = _build_code_prompt_from_requirements(user_prompt, requirements)

        print("Generating code and tests in parallel...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            code_future = executor.submit(generate_python_code, code_prompt)
            tests_future = executor.submit(generate_tests_from_requirements, requirements)

            generated_code = code_future.result()
            generated_tests = tests_future.result()

        execution.generated_code = generated_code
        execution.generated_tests = generated_tests
        session_store.save_result(
            agent="python_coder",
            task=code_prompt,
            code=generated_code,
        )
        session_store.save_result(
            agent="tester",
            task="Generate pytest tests from structured requirements.",
            source_code=json.dumps(requirements, indent=2),
            code=generated_tests,
        )

        print("Validating generated code...")
        ast_validation = validate_python_code(generated_code)

        if not ast_validation["valid"]:
            execution.status = "failed"
            execution.error = ast_validation["error"]
            session_store.save_execution(execution)
            session_store.set_state("pipeline_status", "failed")

            return {
                "success": False,
                "error": ast_validation["error"],
                "route": route,
                "requirements": requirements,
                "generated_code": generated_code,
                "generated_tests": generated_tests,
                "ast_validation": ast_validation,
                "execution_id": execution.execution_id,
            }

        print("Normalizing test imports...")
        generated_tests = normalize_generated_code_imports(generated_tests)
        execution.generated_tests = generated_tests

        print("Running tests...")
        execution_result = run_tests(generated_code, generated_tests)

        if not execution_result.get("success"):
            print("Regenerating tests from generated code after failed execution...")
            generated_tests = generate_test_cases(generated_code, user_prompt)
            generated_tests = normalize_generated_code_imports(generated_tests)
            execution.generated_tests = generated_tests
            session_store.save_result(
                agent="tester",
                task="Regenerate pytest tests from generated code after failed execution.",
                source_code=generated_code,
                code=generated_tests,
            )
            execution_result = run_tests(generated_code, generated_tests)

        execution.execution_results = execution_result
        session_store.save_result(
            agent="execution",
            task="Run generated pytest suite.",
            source_code=generated_code,
            test_code=generated_tests,
            report=json.dumps(execution_result, indent=2),
            status="success" if execution_result.get("success") else "failed",
            error=str(execution_result.get("stderr") or ""),
        )

        print("Evaluating solution...")
        evaluation = _evaluate_solution(generated_code, execution_result, generated_tests)
        execution.evaluation_results = evaluation
        execution.status = "completed" if execution_result.get("success") else "failed"
        execution.error = "" if execution_result.get("success") else evaluation["summary"]
        session_store.save_result(
            agent="evaluator",
            task="Evaluate generated solution.",
            source_code=generated_code,
            test_code=generated_tests,
            report=json.dumps(evaluation, indent=2),
            status="success" if execution_result.get("success") else "failed",
            error="" if execution_result.get("success") else evaluation["summary"],
        )
        session_store.save_execution(execution)
        session_store.set_state("pipeline_status", execution.status)

        return {
            "success": True,
            "route": route,
            "requirements": requirements,
            "generated_code": generated_code,
            "generated_tests": generated_tests,
            "ast_validation": ast_validation,
            "execution_result": execution_result,
            "evaluation": evaluation,
            "execution_id": execution.execution_id,
            "memory_summary": session_store.summary(),
        }
    except Exception as error:
        if execution is not None:
            execution.status = "failed"
            execution.error = str(error)
            session_store.save_execution(execution)
            session_store.save_result(
                agent="execution",
                task="Workflow failed before completion.",
                status="failed",
                error=str(error),
            )

        session_store.set_state("pipeline_status", "failed")

        return {
            "success": False,
            "error": str(error),
            "execution_id": execution.execution_id if execution else None,
        }


def get_workflow_mermaid() -> str:
    """
    Return a Mermaid graph for the current MVP workflow.
    """
    labels = {
        "START": "START",
        "route": "Router Agent",
        "requirements": "Requirements Agent",
        "code_generation": "Code Agent",
        "test_generation": "Test Agent",
        "ast_validation": "AST Validation",
        "execution": "Execution Agent",
        "evaluation": "Evaluator Agent",
        "END": "END",
    }
    lines = ["flowchart TD"]

    for source, target in WORKFLOW_GRAPH_EDGES:
        lines.append(f"    {source}[{labels[source]}] --> {target}[{labels[target]}]")

    return "\n".join(lines)


def show_workflow_graph() -> object:
    """
    Display the workflow graph in a Jupyter notebook.
    """
    mermaid = get_workflow_mermaid()

    try:
        from IPython.display import HTML, display
    except ImportError:
        return mermaid

    graph = HTML(
        f"""
        <pre class="mermaid">
{mermaid}
        </pre>
        <script type="module">
            import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
            mermaid.initialize({{ startOnLoad: true }});
            mermaid.run();
        </script>
        """
    )
    display(graph)
    return graph
