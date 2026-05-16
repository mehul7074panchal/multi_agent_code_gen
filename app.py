"""
Multi-Agent Natural Language to Code System - Gradio UI
Professional dashboard for AI-powered code generation workflow
"""

import html as html_lib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Iterator, Optional
import traceback

import gradio as gr

from workflow import run_workflow

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

def process_workflow(user_prompt: str) -> Iterator[tuple[str, str, str, str, str]]:
    """
    Execute the workflow and stream log updates to the UI.
    """
    
    if not user_prompt or not user_prompt.strip():
        raise ValueError("Please enter a coding request")
    
    workflow_state.reset()
    generated_code = None
    generated_tests = None
    execution_results = None
    evaluation_json = None
    empty_outputs = (
        render_code_tab(None),
        render_tests_tab(None),
        render_execution_tab(None),
        render_evaluation_tab(None),
    )
    
    try:
        logs = workflow_state.add_log("System", "Starting multi-agent workflow...")
        yield logs, *empty_outputs

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_workflow, user_prompt)
            start_time = time.time()
            last_second = -1

            while not future.done():
                elapsed_seconds = int(time.time() - start_time)
                if elapsed_seconds != last_second:
                    last_second = elapsed_seconds
                    logs = workflow_state.add_log(
                        "System",
                        f"Workflow running... {elapsed_seconds}s",
                    )
                    yield logs, *empty_outputs

                time.sleep(0.5)

            result = future.result()

        if not result.get("success"):
            raise ValueError(result.get("error", "Workflow failed"))

        route_result = result.get("route", {})
        requirements = result.get("requirements", {})
        generated_code = result.get("generated_code")
        generated_tests = result.get("generated_tests")
        execution_results = result.get("execution_result")
        evaluation = result.get("evaluation", {})
        evaluation_json = evaluation.get("coverage_report", evaluation)

        logs = workflow_state.add_log(
            "Router Agent",
            f"✓ Detected: {route_result.get('task_type', 'unknown').upper()} task",
        )
        yield logs, *empty_outputs

        logs = workflow_state.add_log(
            "Requirements Agent",
            f"✓ Extracted requirements for {requirements.get('function_name') or 'generated code'}",
        )
        yield logs, *empty_outputs

        logs = workflow_state.add_log(
            "Code Generation Agent",
            f"✓ Generated {len((generated_code or '').splitlines())} lines of code",
        )
        yield logs, render_code_tab(generated_code), empty_outputs[1], empty_outputs[2], empty_outputs[3]

        logs = workflow_state.add_log(
            "Test Generation Agent",
            f"✓ Created {(generated_tests or '').count('def test_')} test cases",
        )
        yield logs, render_code_tab(generated_code), render_tests_tab(generated_tests), empty_outputs[2], empty_outputs[3]

        logs = workflow_state.add_log(
            "Execution Agent",
            "✓ Tests passed" if execution_results.get("success") else "✗ Tests failed",
        )
        yield (
            logs,
            render_code_tab(generated_code),
            render_tests_tab(generated_tests),
            render_execution_tab(execution_results),
            empty_outputs[3],
        )

        logs = workflow_state.add_log(
            "Evaluation Agent",
            f"✓ Coverage: {evaluation_json.get('overall_coverage_percentage', 0)}%",
        )
        logs = workflow_state.add_log("System", "✓ Workflow completed successfully")
        
    except Exception as e:
        logs = workflow_state.add_log("System", f"✗ Error: {str(e)}")
        logs = workflow_state.add_log("System", f"Details: {traceback.format_exc()}")
    
    # Render outputs
    code_html = render_code_tab(generated_code)
    tests_html = render_tests_tab(generated_tests)
    execution_html = render_execution_tab(execution_results)
    evaluation_html = render_evaluation_tab(evaluation_json)
    
    yield logs, code_html, tests_html, execution_html, evaluation_html

# ============================================================================
# UI RENDERING FUNCTIONS
# ============================================================================

def create_header():
    """Create a compact header section."""
    return gr.HTML("""
    <div style="text-align: center; padding: 14px 18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px; margin-bottom: 14px;">
        <h1 style="margin: 0; color: white; font-size: 1.45em; font-weight: 800; line-height: 1.2;">
            Multi-Agent Natural Language to Code
        </h1>
        <p style="margin: 4px 0 0 0; color: rgba(255,255,255,0.88); font-size: 0.9em;">
            AI Agent Orchestration Demo
        </p>
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
            <div style="font-size: 0.85em; color: rgba(255,255,255,0.8);">Test Definitions</div>
            <div style="font-size: 1.8em; font-weight: bold;">{test_count}</div>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto;">
            <pre style="margin: 0; color: #e2e8f0; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em;"><code>{tests}</code></pre>
        </div>
    </div>
    """
    return html


def _parse_pytest_counts(output: str) -> tuple[int, int]:
    """Read pytest summary lines like '1 failed, 14 passed in 0.07s'."""
    passed_matches = re.findall(r"(\d+)\s+passed", output)
    failed_matches = re.findall(r"(\d+)\s+failed", output)

    passed_count = int(passed_matches[-1]) if passed_matches else 0
    failed_count = int(failed_matches[-1]) if failed_matches else 0

    return passed_count, failed_count


def render_execution_tab(execution_results: Optional[dict]) -> str:
    """Render the Execution Results tab"""
    if not execution_results:
        return "No execution results yet."
    
    stdout = execution_results.get("stdout", "")
    stderr = execution_results.get("stderr", "")
    output_text = stdout if stdout else stderr
    success = execution_results.get("success", False)
    
    passed_count, failed_count = _parse_pytest_counts(f"{stdout}\n{stderr}")
    
    status_color = "#10b981" if success else "#ef4444"
    status_text = "✓ All Tests Passed" if success else "✗ Some Tests Failed"
    output_color = "#10b981" if success else "#e2e8f0"
    escaped_output = html_lib.escape(output_text)
    
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="background: {status_color}22; border-left: 4px solid {status_color}; padding: 15px; border-radius: 8px;">
            <div style="color: {status_color}; font-weight: bold; font-size: 1.1em;">{status_text}</div>
            <div style="color: #cbd5e1; margin-top: 8px;">
                Passed: {passed_count} | Failed: {failed_count} | Return Code: {execution_results.get('return_code', 'N/A')}
            </div>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-x: auto; max-height: 500px; overflow-y: auto;">
            <pre style="margin: 0; color: {output_color}; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.85em;"><code>{escaped_output}</code></pre>
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
                    <div style="color: #64748b; font-size: 0.75em;">Test Definitions: {func_data.get('test_cases', 0)}</div>
                </div>
            """
    
    html += """
            </div>
        </div>
    </div>
    """
    return html

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
    .gr-label { color: #cbd5e1; }
    """) as demo:
        
        # Header
        create_header()
        
        with gr.Row():
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("### 📝 Enter Your Coding Request", elem_id="left-panel-title")
                
                user_input = gr.Textbox(
                    label=None,
                    placeholder="Example: Create a Python palindrome checker that handles case sensitivity and special characters...",
                    lines=6,
                    interactive=True,
                    show_label=False,
                )
                
                # Control buttons
                with gr.Row():
                    generate_btn = gr.Button("🚀 Generate Solution", scale=2, variant="primary")
                    clear_btn = gr.Button("🔄 Clear", scale=1)
                
                # Logs panel
                gr.Markdown("#### 📋 Live Agent Logs")
                logs_display = gr.Textbox(
                    label=None,
                    lines=15,
                    interactive=False,
                    max_lines=None,
                    elem_id="logs-panel",
                    show_label=False,
                )

            with gr.Column(scale=2, min_width=600):
                gr.Markdown("### 📊 Results & Analysis")
                
                with gr.Tabs():
                    with gr.TabItem("Generated Code", id="code_tab"):
                        code_output = gr.HTML()
                    
                    with gr.TabItem("Generated Tests", id="tests_tab"):
                        tests_output = gr.HTML()
                    
                    with gr.TabItem("Execution Results", id="execution_tab"):
                        execution_output = gr.HTML()
                    
                    with gr.TabItem("Evaluation Report", id="evaluation_tab"):
                        evaluation_output = gr.HTML()
        
        # Clear button functionality
        def clear_all():
            return "", "", "", "", "", ""
        
        clear_btn.click(
            clear_all,
            outputs=[
                user_input,
                logs_display,
                code_output,
                tests_output,
                execution_output,
                evaluation_output,
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
            ],
            show_progress="minimal",
        )
    
    return demo

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    app = create_app()
    app.launch(share=False, show_error=True)
