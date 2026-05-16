"""
Multi-Agent Natural Language to Code System - Gradio UI
Professional dashboard for AI-powered code generation workflow
"""

import json
from datetime import datetime
from typing import Optional, Tuple
import traceback

import gradio as gr

# Import backend modules
from agents.router import route_request
from agents.requirements_agent import extract_requirements
from agents.python_coder import generate_python_code
from agents.test_writer import generate_test_cases
from executor import run_tests
from agents.evaluator import generate_coverage_report_json
from memory.session_store import session_store, ExecutionResult

# ============================================================================
# EXAMPLE PROMPTS
# ============================================================================

EXAMPLE_PROMPTS = [
    "Create a Python palindrome checker that handles case-insensitivity and special characters",
    "Write a function to check if a number is prime",
    "Generate a function to reverse a string",
    "Create a function to find the factorial of a number",
    "Write code to check if a number is a perfect square",
]


# ============================================================================
# WORKFLOW STATE MANAGEMENT
# ============================================================================

class WorkflowState:
    """Manages the state of the workflow execution"""
    def __init__(self):
        self.logs = []
        
    def reset(self):
        self.logs = []
        
    def add_log(self, agent: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{agent}] {message}"
        self.logs.append(log_entry)
        return "\n".join(self.logs)


workflow_state = WorkflowState()

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

def process_workflow(user_prompt: str) -> Tuple[str, str, str, str, str]:
    """
    Execute the full workflow: Router → Requirements → Code → Tests → Execution → Evaluation
    Returns: (logs, code_html, tests_html, execution_html, evaluation_html)
    """
    
    if not user_prompt or not user_prompt.strip():
        raise ValueError("Please enter a coding request")
    
    workflow_state.reset()
    generated_code = None
    generated_tests = None
    execution_results = None
    evaluation_json = None
    
    try:
        # Step 1: Router Agent
        logs = workflow_state.add_log("Router Agent", "Analyzing request type...")
        route_result = route_request(user_prompt)
        logs = workflow_state.add_log("Router Agent", f"✓ Detected: {route_result['task_type'].upper()} task")
        
        # Step 2: Requirements Agent
        logs = workflow_state.add_log("Requirements Agent", "Extracting requirements...")
        requirements = extract_requirements(user_prompt)
        logs = workflow_state.add_log("Requirements Agent", f"✓ Extracted {len(requirements['requirements'])} requirements")
        
        # Step 3: Python Code Generation
        logs = workflow_state.add_log("Code Generation Agent", "Generating Python code...")
        generated_code = generate_python_code(user_prompt)
        logs = workflow_state.add_log("Code Generation Agent", f"✓ Generated {len(generated_code.splitlines())} lines of code")
        
        # Step 4: Test Generation
        logs = workflow_state.add_log("Test Generation Agent", "Creating pytest test cases...")
        generated_tests = generate_test_cases(generated_code)
        logs = workflow_state.add_log("Test Generation Agent", f"✓ Created {generated_tests.count('def test_')} test cases")
        
        # Step 5: Execution
        logs = workflow_state.add_log("Execution Agent", "Running tests in sandbox...")
        execution_results = run_tests(generated_code, generated_tests)
        passed_count = execution_results["stdout"].count(" PASSED")
        failed_count = execution_results["stdout"].count(" FAILED")
        logs = workflow_state.add_log(
            "Execution Agent",
            f"✓ Tests completed: {passed_count} passed, {failed_count} failed"
        )
        
        # Step 6: Evaluation
        logs = workflow_state.add_log("Evaluation Agent", "Computing coverage metrics...")
        evaluation_results = generate_coverage_report_json(generated_code, generated_tests)
        evaluation_json = json.loads(evaluation_results)
        coverage_pct = evaluation_json.get("overall_coverage_percentage", 0)
        logs = workflow_state.add_log("Evaluation Agent", f"✓ Coverage: {coverage_pct}%")
        
        logs = workflow_state.add_log("System", "✓ Workflow completed successfully")
        
        # Save to session store
        execution = session_store.create_execution(user_prompt)
        execution.generated_code = generated_code
        execution.generated_tests = generated_tests
        execution.execution_results = execution_results
        execution.evaluation_results = evaluation_json
        execution.status = "completed"
        session_store.save_execution(execution)
        
    except Exception as e:
        logs = workflow_state.add_log("System", f"✗ Error: {str(e)}")
        logs = workflow_state.add_log("System", f"Details: {traceback.format_exc()}")
    
    # Render outputs
    code_html = render_code_tab(generated_code)
    tests_html = render_tests_tab(generated_tests)
    execution_html = render_execution_tab(execution_results)
    evaluation_html = render_evaluation_tab(evaluation_json)
    
    return logs, code_html, tests_html, execution_html, evaluation_html

# ============================================================================
# UI RENDERING FUNCTIONS
# ============================================================================

def create_header():
    """Create the header section with title and workflow badges"""
    return gr.HTML("""
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 30px;">
        <h1 style="margin: 0; color: white; font-size: 2.5em; font-weight: 800;">
            🤖 Multi-Agent Natural Language to Code
        </h1>
        <p style="margin: 10px 0; color: rgba(255,255,255,0.9); font-size: 1.1em;">
            AI Agent Orchestration Demo - Real-time Workflow Visualization
        </p>
        <div style="margin-top: 20px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.85em;">
                🔀 Router
            </span>
            <span style="color: white; font-size: 0.9em;">→</span>
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.85em;">
                💻 Code Gen
            </span>
            <span style="color: white; font-size: 0.9em;">→</span>
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.85em;">
                🧪 Tests
            </span>
            <span style="color: white; font-size: 0.9em;">→</span>
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.85em;">
                ⚙️ Execute
            </span>
            <span style="color: white; font-size: 0.9em;">→</span>
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.85em;">
                📊 Evaluate
            </span>
        </div>
    </div>
    """)

def create_workflow_progress_tracker():
    """Create visual workflow progress tracker"""
    return gr.HTML("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #3b82f6;">
        <h3 style="margin: 0 0 15px 0; color: #3b82f6;">Workflow Progress</h3>
        <div id="workflow-progress" style="display: flex; justify-content: space-between; align-items: center;">
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">1</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Router</span>
            </div>
            <div style="color: #4b5563;">→</div>
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">2</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Requirements</span>
            </div>
            <div style="color: #4b5563;">→</div>
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">3</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Code Gen</span>
            </div>
            <div style="color: #4b5563;">→</div>
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">4</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Tests</span>
            </div>
            <div style="color: #4b5563;">→</div>
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">5</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Execute</span>
            </div>
            <div style="color: #4b5563;">→</div>
            <div class="workflow-step waiting" style="flex: 1; text-align: center; padding: 10px;">
                <div style="width: 40px; height: 40px; margin: 0 auto 8px; background: #374151; border-radius: 50%; 
                           display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">6</div>
                <span style="color: #9ca3af; font-size: 0.85em;">Evaluate</span>
            </div>
        </div>
    </div>
    """)

def render_code_tab(code: Optional[str]) -> str:
    """Render the Generated Code tab"""
    if not code:
        return "No code generated yet. Submit a prompt to get started."
    
    lines = code.splitlines()
    functions = code.count("def ")
    classes = code.count("class ")
    
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white;">
                <div style="font-size: 0.85em; color: rgba(255,255,255,0.8);">Lines of Code</div>
                <div style="font-size: 1.8em; font-weight: bold;">{len(lines)}</div>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 8px; color: white;">
                <div style="font-size: 0.85em; color: rgba(255,255,255,0.8);">Functions</div>
                <div style="font-size: 1.8em; font-weight: bold;">{functions}</div>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 15px; border-radius: 8px; color: white;">
                <div style="font-size: 0.85em; color: rgba(255,255,255,0.8);">Classes</div>
                <div style="font-size: 1.8em; font-weight: bold;">{classes}</div>
            </div>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto;">
            <pre style="margin: 0; color: #e2e8f0; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em;"><code>{code}</code></pre>
        </div>
    </div>
    """
    return html

def render_tests_tab(tests: Optional[str]) -> str:
    """Render the Generated Tests tab"""
    if not tests:
        return "No tests generated yet."
    
    test_count = tests.count("def test_")
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white;">
            <div style="font-size: 0.85em; color: rgba(255,255,255,0.8);">Test Functions</div>
            <div style="font-size: 1.8em; font-weight: bold;">{test_count}</div>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto;">
            <pre style="margin: 0; color: #e2e8f0; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em;"><code>{tests}</code></pre>
        </div>
    </div>
    """
    return html

def render_execution_tab(execution_results: Optional[dict]) -> str:
    """Render the Execution Results tab"""
    if not execution_results:
        return "No execution results yet."
    
    stdout = execution_results.get("stdout", "")
    success = execution_results.get("success", False)
    
    passed_count = stdout.count(" PASSED")
    failed_count = stdout.count(" FAILED")
    
    status_color = "#10b981" if success else "#ef4444"
    status_text = "✓ All Tests Passed" if success else "✗ Some Tests Failed"
    
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="background: {status_color}22; border-left: 4px solid {status_color}; padding: 15px; border-radius: 8px;">
            <div style="color: {status_color}; font-weight: bold; font-size: 1.1em;">{status_text}</div>
            <div style="color: #cbd5e1; margin-top: 8px;">
                Passed: {passed_count} | Failed: {failed_count} | Return Code: {execution_results.get('return_code', 'N/A')}
            </div>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto; max-height: 500px; overflow-y: auto;">
            <pre style="margin: 0; color: #10b981; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.85em;"><code>{stdout}</code></pre>
        </div>
    </div>
    """
    return html

def render_evaluation_tab(evaluation_results: Optional[dict]) -> str:
    """Render the Evaluation Report tab"""
    if not evaluation_results:
        return "No evaluation results yet."
    
    coverage = evaluation_results.get("overall_coverage_percentage", 0)
    tested = evaluation_results.get("tested_functions", 0)
    total = evaluation_results.get("total_functions", 0)
    
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   border-radius: 12px; color: white;">
            <div style="font-size: 0.9em; color: rgba(255,255,255,0.8);">Code Coverage</div>
            <div style="font-size: 3em; font-weight: bold; margin: 10px 0;">{coverage}%</div>
            <div style="font-size: 0.9em; color: rgba(255,255,255,0.8);">{tested} of {total} functions tested</div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
            <div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
                <div style="color: #94a3b8; font-size: 0.85em;">Tested Functions</div>
                <div style="color: #10b981; font-size: 1.6em; font-weight: bold; margin-top: 5px;">{tested}</div>
            </div>
            <div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <div style="color: #94a3b8; font-size: 0.85em;">Untested Functions</div>
                <div style="color: #f59e0b; font-size: 1.6em; font-weight: bold; margin-top: 5px;">{evaluation_results.get('untested_functions', 0)}</div>
            </div>
        </div>
        
        <div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <div style="color: #94a3b8; font-size: 0.85em; margin-bottom: 10px;">Quality Metrics</div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
    """
    
    if "functions" in evaluation_results:
        for func_name, func_data in evaluation_results["functions"].items():
            html += f"""
                <div style="background: #0f172a; padding: 10px; border-radius: 6px;">
                    <div style="color: #cbd5e1; font-size: 0.85em;">{func_name}</div>
                    <div style="color: #10b981; font-size: 1.2em; font-weight: bold;">{func_data.get('coverage_percentage', 0)}%</div>
                    <div style="color: #64748b; font-size: 0.75em;">Test Cases: {func_data.get('test_cases', 0)}</div>
                </div>
            """
    
    html += """
            </div>
        </div>
    </div>
    """
    return html

def render_agent_trace_tab(logs: str) -> str:
    """Render the Agent Trace tab"""
    return f"""
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto; max-height: 600px; overflow-y: auto;">
        <pre style="margin: 0; color: #10b981; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em;"><code>{logs}</code></pre>
    </div>
    """

def render_architecture_tab() -> str:
    """Render the Architecture View tab"""
    return """
    <div style="text-align: center; padding: 30px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   padding: 40px; border-radius: 12px; margin-bottom: 20px; color: white;">
            <h3 style="margin: 0 0 15px 0;">📝 User Prompt</h3>
            <div style="font-size: 0.95em; color: rgba(255,255,255,0.9);">
                "Create a Python palindrome checker"
            </div>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #3b82f6;">
            <h4 style="margin: 0; color: #3b82f6;">🔀 Router Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Detects task type (Python/SQL)</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #667eea;">
            <h4 style="margin: 0; color: #667eea;">📋 Requirements Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Extracts structured requirements</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #f093fb;">
            <h4 style="margin: 0; color: #f093fb;">💻 Code Generation Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Generates executable Python code</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #4facfe;">
            <h4 style="margin: 0; color: #4facfe;">🧪 Test Generation Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Creates comprehensive pytest test cases</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #10b981;">
            <h4 style="margin: 0; color: #10b981;">⚙️ Execution Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Runs tests in isolated sandbox</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #f59e0b;">
            <h4 style="margin: 0; color: #f59e0b;">📊 Evaluation Agent</h4>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.9em;">Computes coverage & quality metrics</p>
        </div>
        
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <div style="color: #667eea; font-size: 1.5em;">↓</div>
        </div>
        
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                   padding: 40px; border-radius: 12px; color: white;">
            <h3 style="margin: 0 0 15px 0;">✨ Results Dashboard</h3>
            <div style="font-size: 0.95em; color: rgba(255,255,255,0.9);">
                Generated Code + Tests + Metrics
            </div>
        </div>
    </div>
    """

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def create_app():
    """Create the Gradio application"""
    
    with gr.Blocks(theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="purple"
    ), css="""
    body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
    .gradio-container { max-width: 1600px; margin: 0 auto; }
    .gr-form { background: transparent; border: none; }
    .gr-textbox, .gr-textarea { border: 1px solid #334155; }
    .gr-textbox input, .gr-textarea textarea { background: #1e293b; color: #e2e8f0; }
    .gr-button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .gr-button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4); }
    .gr-radio { color: #e2e8f0; }
    .gr-label { color: #cbd5e1; }
    """) as demo:
        
        # Header
        create_header()
        
        # Main content grid
        with gr.Row():
            # Left Panel - Input and Logs
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("### 📝 Enter Your Coding Request", elem_id="left-panel-title")
                
                user_input = gr.Textbox(
                    label="Describe what code you want to generate",
                    placeholder="Example: Create a Python palindrome checker that handles case sensitivity and special characters...",
                    lines=6,
                    interactive=True
                )
                
                gr.Markdown("#### Quick Examples")
                example_buttons = gr.Radio(
                    choices=EXAMPLE_PROMPTS,
                    label="Select an example",
                    interactive=True
                )
                
                def set_example(example):
                    return example
                
                example_buttons.change(set_example, example_buttons, user_input)
                
                # Control buttons
                with gr.Row():
                    generate_btn = gr.Button("🚀 Generate Solution", scale=2, variant="primary")
                    clear_btn = gr.Button("🔄 Clear", scale=1)
                
                # Workflow progress
                create_workflow_progress_tracker()
                
                # Logs panel
                gr.Markdown("#### 📋 Live Agent Logs")
                logs_display = gr.Textbox(
                    label="Agent Activity",
                    lines=15,
                    interactive=False,
                    max_lines=None,
                    elem_id="logs-panel"
                )
                
            # Right Panel - Results
            with gr.Column(scale=2, min_width=600):
                gr.Markdown("### 📊 Results & Analysis")
                
                with gr.Tabs():
                    with gr.TabItem("Generated Code", id="code_tab"):
                        code_output = gr.HTML(label="Code")
                    
                    with gr.TabItem("Generated Tests", id="tests_tab"):
                        tests_output = gr.HTML(label="Tests")
                    
                    with gr.TabItem("Execution Results", id="execution_tab"):
                        execution_output = gr.HTML(label="Execution")
                    
                    with gr.TabItem("Evaluation Report", id="evaluation_tab"):
                        evaluation_output = gr.HTML(label="Evaluation")
                    
                    with gr.TabItem("Agent Trace", id="trace_tab"):
                        trace_output = gr.Textbox(label="Trace", lines=20, interactive=False)
                    
                    with gr.TabItem("Architecture", id="arch_tab"):
                        arch_output = gr.HTML(label="Architecture")
        
        # Initialize architecture tab on load
        def init_app():
            return render_architecture_tab()
        
        demo.load(init_app, outputs=[arch_output])
        
        # Clear button functionality
        def clear_all():
            return "", "", "", "", "", "", ""
        
        clear_btn.click(
            clear_all,
            outputs=[
                user_input,
                logs_display,
                code_output,
                tests_output,
                execution_output,
                evaluation_output,
                trace_output
            ]
        )
        
        # Generate button functionality
        generate_btn.click(
            process_workflow,
            inputs=[user_input],
            outputs=[
                logs_display,
                code_output,
                tests_output,
                execution_output,
                evaluation_output
            ]
        )
    
    return demo

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    app = create_app()
    app.launch(share=False, show_error=True)
