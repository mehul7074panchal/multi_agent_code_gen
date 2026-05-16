import json
from typing import TypedDict

from agents.python_coder import generate_python_code
from agents.requirements_agent import extract_requirements
from agents.router import route_request
from agents.tester import generate_tests
from executor import run_tests
from utils.code_parser import validate_python_code
from utils.import_normalizer import normalize_generated_code_imports


class WorkflowState(TypedDict, total=False):
    user_prompt: str
    route: dict
    requirements: dict
    generated_code: str
    generated_tests: str
    ast_validation: dict
    execution_result: dict
    evaluation: dict
    success: bool
    error: str


LANGGRAPH_FLOW_EDGES = [
    ("START", "route"),
    ("route", "requirements"),
    ("requirements", "code_generation"),
    ("code_generation", "ast_validation"),
    ("ast_validation", "test_generation"),
    ("test_generation", "execution"),
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


def _truncate_text(text: str, limit: int = 900) -> str:
    if len(text) <= limit:
        return text

    return text[:limit].rstrip() + "..."


def run_workflow(user_prompt: str) -> dict:
    """
    Run the simple linear multi-agent workflow.
    """
    try:
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")

        print("Routing request...")
        route = route_request(user_prompt)

        if route.get("task_type") != "python":
            return {
                "success": False,
                "error": "Current MVP supports Python generation only.",
                "route": route,
            }

        print("Extracting requirements...")
        requirements = extract_requirements(user_prompt)

        print("Generating code...")
        generated_code = generate_python_code(user_prompt)

        print("Validating generated code...")
        ast_validation = validate_python_code(generated_code)

        if not ast_validation["valid"]:
            return {
                "success": False,
                "error": ast_validation["error"],
                "route": route,
                "requirements": requirements,
                "generated_code": generated_code,
                "ast_validation": ast_validation,
            }

        print("Generating tests...")
        generated_tests = generate_tests(generated_code)

        print("Normalizing test imports...")
        generated_tests = normalize_generated_code_imports(generated_tests)

        print("Running tests...")
        execution_result = run_tests(generated_code, generated_tests)

        print("Evaluating solution...")
        evaluation = _evaluate_solution(generated_code, execution_result, generated_tests)

        # TODO:
        # save_result(...)

        return {
            "success": True,
            "route": route,
            "requirements": requirements,
            "generated_code": generated_code,
            "generated_tests": generated_tests,
            "ast_validation": ast_validation,
            "execution_result": execution_result,
            "evaluation": evaluation,
        }
    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


def route_node(state: WorkflowState) -> WorkflowState:
    print("Routing request...")
    state["route"] = route_request(state["user_prompt"])
    return state


def requirements_node(state: WorkflowState) -> WorkflowState:
    print("Extracting requirements...")
    state["requirements"] = extract_requirements(state["user_prompt"])
    return state


def code_generation_node(state: WorkflowState) -> WorkflowState:
    print("Generating code...")
    state["generated_code"] = generate_python_code(state["user_prompt"])
    return state


def ast_validation_node(state: WorkflowState) -> WorkflowState:
    print("Validating generated code...")
    state["ast_validation"] = validate_python_code(state["generated_code"])
    return state


def test_generation_node(state: WorkflowState) -> WorkflowState:
    print("Generating tests...")
    generated_tests = generate_tests(state["generated_code"])
    state["generated_tests"] = normalize_generated_code_imports(generated_tests)
    return state


def execution_node(state: WorkflowState) -> WorkflowState:
    print("Running tests...")
    state["execution_result"] = run_tests(
        state["generated_code"],
        state["generated_tests"],
    )
    return state


def evaluation_node(state: WorkflowState) -> WorkflowState:
    print("Evaluating solution...")
    state["evaluation"] = _evaluate_solution(
        state["generated_code"],
        state["execution_result"],
        state["generated_tests"],
    )
    state["success"] = True
    return state


def build_langgraph_workflow():
    """
    Build a lightweight LangGraph workflow for MVP graph orchestration.
    """
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as error:
        raise ImportError(
            "LangGraph is not installed. Run: pip install -r requirements.txt"
        ) from error

    workflow = StateGraph(WorkflowState)

    workflow.add_node("route", route_node)
    workflow.add_node("requirements", requirements_node)
    workflow.add_node("code_generation", code_generation_node)
    workflow.add_node("ast_validation", ast_validation_node)
    workflow.add_node("test_generation", test_generation_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("evaluation", evaluation_node)

    workflow.set_entry_point("route")
    workflow.add_edge("route", "requirements")
    workflow.add_edge("requirements", "code_generation")
    workflow.add_edge("code_generation", "ast_validation")
    workflow.add_edge("ast_validation", "test_generation")
    workflow.add_edge("test_generation", "execution")
    workflow.add_edge("execution", "evaluation")
    workflow.add_edge("evaluation", END)

    return workflow.compile()


def get_langgraph_flow_text() -> str:
    """
    Return a simple text view of the LangGraph workflow.
    """
    return " -> ".join(edge[0] for edge in LANGGRAPH_FLOW_EDGES) + " -> END"


def get_langgraph_mermaid() -> str:
    """
    Return Mermaid text for displaying the workflow graph in notebooks/docs.
    """
    lines = ["flowchart TD"]

    for source, target in LANGGRAPH_FLOW_EDGES:
        lines.append(f"    {source} --> {target}")

    return "\n".join(lines)


def display_langgraph_flow(output_format: str = "text") -> str:
    """
    Display the LangGraph flow as text or Mermaid.

    Use output_format="mermaid" in notebooks that support Mermaid rendering.
    """
    if output_format == "mermaid":
        flow = get_langgraph_mermaid()
    elif output_format == "text":
        flow = get_langgraph_flow_text()
    else:
        raise ValueError("output_format must be 'text' or 'mermaid'.")

    print(flow)
    return flow


def display_compiled_langgraph_mermaid() -> str:
    """
    Return Mermaid text using LangGraph's built-in graph drawing API.
    """
    graph = build_langgraph_workflow()
    mermaid = graph.get_graph().draw_mermaid()

    return mermaid


def display_compiled_langgraph_png() -> bytes:
    """
    Return PNG bytes using LangGraph's built-in graph drawing API.

    In Jupyter:
        from IPython.display import Image, display
        display(Image(display_compiled_langgraph_png()))
    """
    graph = build_langgraph_workflow()
    return graph.get_graph().draw_mermaid_png()


def show_compiled_langgraph() -> object:
    """
    Render the compiled LangGraph directly in a notebook when IPython is available.
    """
    png_bytes = display_compiled_langgraph_png()

    try:
        from IPython.display import Image, display
    except ImportError:
        return png_bytes

    image = Image(png_bytes)
    display(image)
    return image


def run_langgraph_workflow(user_prompt: str) -> dict:
    """
    Run the LangGraph workflow version.
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty")

    route = route_request(user_prompt)
    if route.get("task_type") != "python":
        return {
            "success": False,
            "error": "Current MVP supports Python generation only.",
            "route": route,
        }

    graph = build_langgraph_workflow()
    state = graph.invoke({"user_prompt": user_prompt})

    ast_validation = state.get("ast_validation", {})
    if ast_validation and not ast_validation.get("valid", False):
        return {
            "success": False,
            "error": ast_validation.get("error"),
            **state,
        }

    # TODO:
    # save_result(...)

    return state
