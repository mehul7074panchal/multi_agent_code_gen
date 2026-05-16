"""
memory/session_store.py
------------------------
Session memory store for the multi-agent code generation pipeline.

Tracks the full lifecycle of a code generation session across the MVP agents:
    1. router        → routes the request          (agents/router.py)
    2. requirements  → extracts requirements       (agents/requirements.py)
    3. python_coder  → generates Python code       (agents/python_coder.py)
    4. tester        → generates pytest test cases (agents/tester.py)
    5. execution     → runs tests                  (executor.py)
    6. evaluator     → evaluates coverage/quality  (agents/evaluator.py)

Drop-in upgrade for the simple pattern:

    session_history = []
    def save_result(data):    session_history.append(data)
    def get_history():        return session_history

Quick-start
-----------
    from memory.session_store import session_store

    # 1. python_coder saves generated code
    session_store.save_result(
        agent="python_coder",
        task=user_prompt,
        code=generated_code,
    )

    # 2. tester reads source code and saves test output
    source = session_store.get_latest_code()
    session_store.save_result(
        agent="tester",
        task="generate tests",
        source_code=source,
        code=test_code,
    )

    # 3. evaluator reads both and saves its report
    session_store.save_result(
        agent="evaluator",
        task="evaluate coverage",
        source_code=session_store.get_latest_code(),
        test_code=session_store.get_latest_test_code(),
        report=coverage_json,
    )

    # Anywhere — get full history
    session_store.get_history()

    # Shared state across agents
    session_store.set_state("language", "python")
    session_store.get_state("language")
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


# ---------------------------------------------------------------------------
# Types — agent names match the current workflow steps
# ---------------------------------------------------------------------------

AgentName = Literal[
    "router",
    "requirements",
    "python_coder",
    "tester",
    "execution",
    "evaluator",
]
StatusType = Literal["success", "failed", "pending", "reviewing"]
ExecutionStatus = Literal["pending", "running", "completed", "failed"]


# ---------------------------------------------------------------------------
# Session Entry
# ---------------------------------------------------------------------------

@dataclass
class SessionEntry:
    """
    One result entry saved by an agent during the session.

    Fields map directly to what each agent produces:
      - python_coder  → task, code
      - tester   → task, code (test code), source_code
      - execution     → task, source_code, test_code, report
      - evaluator     → task, report, source_code, test_code
    """
    agent: AgentName          # Which agent saved this
    task: str                 # User prompt or instruction passed to the agent
    code: str = ""            # python_coder: source code / tester: test code
    source_code: str = ""     # Input to tester / evaluator
    test_code: str = ""       # Input to evaluator
    report: str = ""          # Evaluator JSON / text report
    status: StatusType = "success"
    error: str = ""           # Populated when status == "failed"
    timestamp: float = field(default_factory=time.time)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        """Plain dict — easy to print, log, or serialize."""
        return {
            "entry_id":    self.entry_id,
            "agent":       self.agent,
            "task":        self.task,
            "status":      self.status,
            "code":        self.code,
            "source_code": self.source_code,
            "test_code":   self.test_code,
            "report":      self.report,
            "error":       self.error,
            "timestamp":   self.timestamp,
        }


@dataclass
class ExecutionResult:
    """
    One end-to-end workflow run saved by the UI or orchestrator.

    This complements SessionEntry. SessionEntry is useful for per-agent logs,
    while ExecutionResult stores the final generated artifacts for a prompt.
    """
    user_prompt: str
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    generated_code: str = ""
    generated_tests: str = ""
    execution_results: Dict[str, Any] = field(default_factory=dict)
    evaluation_results: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    route: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = "pending"
    error: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "user_prompt": self.user_prompt,
            "generated_code": self.generated_code,
            "generated_tests": self.generated_tests,
            "execution_results": self.execution_results,
            "evaluation_results": self.evaluation_results,
            "requirements": self.requirements,
            "route": self.route,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Session Store
# ---------------------------------------------------------------------------

class SessionStore:
    """
    Central in-session memory for the multi-agent code generation pipeline.

    A single instance (`session_store`) is created at module level and
    imported directly by any agent or orchestrator.
    """

    def __init__(self):
        self.session_id: str = str(uuid.uuid4())[:8]
        self.created_at: float = time.time()
        self._history: List[SessionEntry] = []   # replaces: session_history = []
        self._executions: List[ExecutionResult] = []
        self._state: Dict[str, Any] = {}         # shared blackboard between agents

    # -----------------------------------------------------------------------
    # Core API — replaces save_result(data) / get_history()
    # -----------------------------------------------------------------------

    def save_result(
        self,
        agent: AgentName,
        task: str = "",
        code: str = "",
        source_code: str = "",
        test_code: str = "",
        report: str = "",
        status: StatusType = "success",
        error: str = "",
    ) -> SessionEntry:
        """
        Save the output of any agent.
        Direct upgrade for: session_history.append(data)

        Args:
            agent:       "router" | "requirements" | "python_coder" | "tester" | "execution" | "evaluator"
            task:        The prompt / instruction the agent received
            code:        Code string produced by python_coder or tester
            source_code: Source code passed as input to tester / evaluator
            test_code:   Test code passed as input to evaluator
            report:      Evaluator JSON or text report
            status:      "success" | "failed" | "pending" | "reviewing"
            error:       Exception message when status is "failed"

        Returns:
            SessionEntry (use .entry_id to update it later if needed)

        Examples:
            # python_coder — happy path
            entry = session_store.save_result(
                agent="python_coder",
                task=user_prompt,
                code=generated_code,
            )

            # python_coder — failed run
            session_store.save_result(
                agent="python_coder",
                task=user_prompt,
                status="failed",
                error=str(exc),
            )

            # tester
            session_store.save_result(
                agent="tester",
                task="generate tests",
                source_code=generated_code,
                code=test_code,
            )

            # evaluator
            session_store.save_result(
                agent="evaluator",
                task="evaluate coverage",
                source_code=generated_code,
                test_code=test_code,
                report=coverage_json,
            )
        """
        
        entry = SessionEntry(
            agent=agent,
            task=task,
            code=code,
            source_code=source_code,
            test_code=test_code,
            report=report,
            status=status,
            error=error,
        )
        self._history.append(entry)
        return entry

    def get_history(self, as_dicts: bool = False) -> List[Any]:
        """
        Return the full session history.
        Direct replacement for: get_history()

        Args:
            as_dicts: If True, returns plain dicts (useful for logging/printing).
        """
        if as_dicts:
            return [e.to_dict() for e in self._history]
        return list(self._history)

    # -----------------------------------------------------------------------
    # Agent pipeline helpers
    # (each agent calls these to pick up the previous agent's output)
    # -----------------------------------------------------------------------

    def get_latest_code(self) -> Optional[str]:
        """
        Return the most recent code from python_coder.
        Called by tester to get the source code to test.

        Example:
            source_code = session_store.get_latest_code()
            test_code = generate_test_cases(source_code)
        """
        for entry in reversed(self._history):
            if entry.agent == "python_coder" and entry.status == "success" and entry.code:
                return entry.code
        return None

    def get_latest_test_code(self) -> Optional[str]:
        """
        Return the most recent test code from tester.
        Called by evaluator to get the tests to evaluate.

        Example:
            test_code = session_store.get_latest_test_code()
            report = evaluate_test_coverage(source_code, test_code)
        """
        for entry in reversed(self._history):
            if entry.agent == "tester" and entry.status == "success" and entry.code:
                return entry.code
        return None

    # -----------------------------------------------------------------------
    # End-to-end execution history used by the Gradio app
    # -----------------------------------------------------------------------

    def create_execution(self, user_prompt: str) -> ExecutionResult:
        """Create a pending execution record for one full workflow run."""
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty.")

        return ExecutionResult(user_prompt=user_prompt.strip())

    def save_execution(self, execution: ExecutionResult) -> ExecutionResult:
        """
        Save or replace an end-to-end workflow execution.

        The replacement behavior prevents duplicate rows when the UI creates a
        pending object and saves it again after the workflow finishes.
        """
        if not isinstance(execution, ExecutionResult):
            raise ValueError("Execution must be an ExecutionResult.")

        execution.updated_at = time.time()

        for index, existing_execution in enumerate(self._executions):
            if existing_execution.execution_id == execution.execution_id:
                self._executions[index] = execution
                return execution

        self._executions.append(execution)
        return execution

    def get_executions(self, as_dicts: bool = False) -> List[Any]:
        """Return saved end-to-end workflow executions, oldest first."""
        if as_dicts:
            return [execution.to_dict() for execution in self._executions]
        return list(self._executions)

    def get_latest_execution(self) -> Optional[ExecutionResult]:
        """Return the most recent end-to-end workflow execution."""
        return self._executions[-1] if self._executions else None

    def get_execution(self, execution_id: str) -> Optional[ExecutionResult]:
        """Find an execution by id."""
        for execution in self._executions:
            if execution.execution_id == execution_id:
                return execution
        return None

    def get_latest_report(self) -> Optional[str]:
        """
        Return the most recent evaluator report.
        Useful for orchestrators or a UI layer that needs the final report.
        """
        for entry in reversed(self._history):
            if entry.agent == "evaluator" and entry.status == "success" and entry.report:
                return entry.report
        return None

    def get_by_agent(self, agent: AgentName) -> List[SessionEntry]:
        """All entries produced by a specific agent."""
        return [e for e in self._history if e.agent == agent]

    def get_failed(self) -> List[SessionEntry]:
        """
        All failed entries.
        Useful for retry logic or surfacing errors to the user.
        """
        return [e for e in self._history if e.status == "failed"]

    def get_last(self) -> Optional[SessionEntry]:
        """Most recent entry regardless of agent."""
        return self._history[-1] if self._history else None

    # -----------------------------------------------------------------------
    # Update helpers
    # -----------------------------------------------------------------------

    def update_status(
        self, entry_id: str, status: StatusType, note: str = ""
    ) -> bool:
        """
        Update the status of a saved entry.
        Useful if a later step determines an earlier result was bad.
        Returns True if found and updated.
        """
        for entry in self._history:
            if entry.entry_id == entry_id:
                entry.status = status
                if note:
                    entry.error = note
                return True
        return False

    # -----------------------------------------------------------------------
    # Shared state — blackboard between agents
    # -----------------------------------------------------------------------

    def set_state(self, key: str, value: Any) -> None:
        """
        Write a value any agent can read.

        Common keys used across your pipeline:
            "user_prompt"     — original user request
            "language"        — target language (default "python")
            "pipeline_status" — "running" | "done" | "error"
        """
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Read a shared value. Returns default if not set."""
        return self._state.get(key, default)

    def get_all_state(self) -> Dict[str, Any]:
        """Full snapshot of shared state."""
        return dict(self._state)

    # -----------------------------------------------------------------------
    # Session management
    # -----------------------------------------------------------------------

    def clear(self) -> None:
        """Reset everything — call this to start a new session."""
        self._history.clear()
        self._executions.clear()
        self._state.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Return compact metrics for UI cards or debug output."""
        completed_count = sum(
            1 for execution in self._executions if execution.status == "completed"
        )
        failed_count = sum(
            1 for execution in self._executions if execution.status == "failed"
        )

        return {
            "session_id": self.session_id,
            "total_agent_entries": len(self._history),
            "total_executions": len(self._executions),
            "completed_executions": completed_count,
            "failed_executions": failed_count,
            "created_at": self.created_at,
        }

    def summary(self) -> Dict[str, Any]:
        """
        High-level summary of the session.
        Log this at the end of a pipeline run to see what happened.

        Example output:
        {
            "session_id": "a1b2c3d4",
            "total_entries": 3,
            "entries_by_agent": {"python_coder": 1, "tester": 1, "evaluator": 1},
            "failed_count": 0,
            "failed_entries": [],
            "shared_state": {"user_prompt": "...", "pipeline_status": "done"}
        }
        """
        counts: Dict[str, int] = {}
        for e in self._history:
            counts[e.agent] = counts.get(e.agent, 0) + 1

        return {
            "session_id":       self.session_id,
            "total_entries":    len(self._history),
            "total_executions": len(self._executions),
            "entries_by_agent": counts,
            "failed_count":     len(self.get_failed()),
            "failed_entries":   [e.to_dict() for e in self.get_failed()],
            "latest_execution": (
                self._executions[-1].to_dict() if self._executions else None
            ),
            "shared_state":     self.get_all_state(),
        }

    def __repr__(self) -> str:
        return (
            f"SessionStore(session_id={self.session_id}, "
            f"entries={len(self._history)})"
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# Import this directly in any agent or orchestrator:
#   from memory.session_store import session_store
# ---------------------------------------------------------------------------

session_store = SessionStore()
