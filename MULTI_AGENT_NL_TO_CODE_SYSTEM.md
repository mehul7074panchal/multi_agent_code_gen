# Multi-Agent Natural Language to Code System

## Project Overview

This project demonstrates a Multi-Agent AI Coding System that converts natural language prompts into executable Python code.

The system uses multiple specialized AI agents working together similar to a real software engineering team.

The generated code is automatically:

- planned
- generated
- tested
- executed
- evaluated

This is a demo-focused hackathon MVP.

---

# Objective

Build a Python-only AI system where:

User enters:

```text
Create Python palindrome checker
```

System automatically:

1. Understands the task
2. Generates Python code
3. Generates unit tests
4. Executes tests
5. Evaluates the generated solution
6. Stores execution history in memory
7. Displays results in Gradio UI

---

# Final Architecture

```text
User Prompt
    ↓
Gradio UI
    ↓
Router Agent
    ↓
Requirements Agent
    ↓
Python Code Agent
    ↓
Test Generation Agent
    ↓
Execution Agent
    ↓
Evaluator Agent
    ↓
In-Memory Session Store
    ↓
Final Output
```

---

# Tech Stack

## Language

- Python 3.11+

## AI / LLM

- OpenAI
- Groq

## Agent Framework

- LangGraph
  OR
- Simple custom workflow orchestration

## UI

- Gradio

## Testing

- pytest

## Utilities

- python-dotenv
- rich

---

# Required Libraries

Install dependencies:

```bash
pip install openai langgraph gradio pytest python-dotenv rich
```

---

# Project Structure

```text
project/
│
├── agents/
│   ├── router.py
│   ├── requirements.py
│   ├── python_coder.py
│   ├── tester.py
│   ├── evaluator.py
│
├── llm/
│   ├── llm_client.py
│
├── memory/
│   ├── session_store.py
│
├── sandbox/
│   ├── generated_code.py
│   ├── test_generated_code.py
│
├── workflow.py
├── executor.py
├── app.py
├── requirements.txt
├── README.md
└── .env
```

---

# Agent Responsibilities

---

## 1. Router Agent

### Responsibility

Detect task type and route request to correct agent.

### Example

```text
Create Python palindrome checker
```

→ Route to Python Code Agent

### File

```text
agents/router.py
```

---

## 2. Requirements Agent

### Responsibility

Extract structured requirements from user input.

### Example Output

```json
{
  "task": "Palindrome Checker",
  "language": "Python",
  "requirements": [
    "Accept string input",
    "Return boolean",
    "Ignore case sensitivity"
  ]
}
```

### File

```text
agents/requirements.py
```

---

## 3. Python Code Agent

### Responsibility

Generate executable Python code using LLM.

### Example Output

```python
def is_palindrome(s):
    s = s.lower()
    return s == s[::-1]
```

### File

```text
agents/python_coder.py
```

---

## 4. Test Generation Agent

### Responsibility

Generate pytest unit tests automatically.

### Example Output

```python
from generated_code import is_palindrome

def test_palindrome():
    assert is_palindrome("madam") == True

def test_non_palindrome():
    assert is_palindrome("hello") == False
```

### File

```text
agents/tester.py
```

---

## 5. Execution Agent

### Responsibility

Execute generated tests using pytest.

### Responsibilities

- Save generated files
- Run pytest
- Capture results
- Return pass/fail status

### Example

```bash
pytest sandbox/
```

### File

```text
executor.py
```

---

## 6. Evaluator Agent

### Responsibility

Evaluate:

- correctness
- readability
- test success
- code quality

### Example Output

```text
Correctness: 10/10
Code Quality: 8/10
Tests Passed: Yes
```

### File

```text
agents/evaluator.py
```

---

# In-Memory Session Store

The system maintains lightweight in-memory execution history.

Stored Data:

- user prompt
- generated code
- evaluation score
- test results
- timestamp

Purpose:

- session analytics
- execution tracking
- demo visualization

No persistent database is used.

---

# In-Memory Store Example

## File

```text
memory/session_store.py
```

## Example

```python
session_history = []

def save_result(data):
    session_history.append(data)

def get_history():
    return session_history
```

---

# Workflow Logic

```python
task = router_agent(user_prompt)

requirements = requirements_agent(user_prompt)

code = python_code_agent(requirements)

tests = test_agent(code)

result = executor(code, tests)

evaluation = evaluator(result)

save_result({
    "prompt": user_prompt,
    "score": evaluation["score"],
    "tests_passed": evaluation["tests_passed"]
})
```

---

# Flexible LLM Provider Support

The system supports multiple LLM providers dynamically using environment variables.

Supported Providers:

- OpenAI
- Groq

Switch provider without changing code.

---

# Environment Variables

Create `.env`

```env
LLM_PROVIDER=openai

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

---

# LLM Provider Switching

## OpenAI

```env
LLM_PROVIDER=openai
```

## Groq

```env
LLM_PROVIDER=groq
```

---

# Shared LLM Client

## File

```text
llm/llm_client.py
```

### Responsibilities

- Centralized LLM handling
- Dynamic provider switching
- Shared by all agents

### Features

- OpenAI support
- Groq support
- Reusable prompt execution
- Single configuration point

---

# Gradio UI Requirements

## Features

### Input

```text
User enters coding requirement
```

### Generate Button

```text
Generate Solution
```

### Display Sections

- Router Output
- Requirements Extraction
- Generated Code
- Generated Tests
- Execution Logs
- Evaluation Report
- Session History

---

# Suggested UI Flow

```text
User Prompt:
[ Create palindrome checker ]

[ Generate ]

✔ Routing completed
✔ Requirements extracted
✔ Code generated
✔ Tests generated
✔ Tests executed
✔ Evaluation completed
✔ Session saved
```

---

# Suggested Gradio Deployment

## Local Demo

```python
demo.launch()
```

## Public Temporary Share

```python
demo.launch(share=True)
```

## Optional Deployment

- Hugging Face Spaces

---

# Supported Demo Examples

## Stable Python Inputs

```text
Create palindrome checker
Generate factorial function
Check prime number
Reverse a string
Generate Fibonacci series
Find maximum number in list
```

---

# Out of Scope

Do NOT build:

- Authentication
- Database integration
- Vector DB
- Memory systems
- Multi-file project generation
- Complex autonomous agents
- Production deployment pipeline

Keep scope small and stable.

---

# Team Responsibilities

---

## Team Member 1 — Workflow / Agent Orchestration

### Responsibilities

- Build LangGraph workflow
- Connect all agents
- Manage execution sequence
- Handle shared data flow

### Main Files

```text
workflow.py
agents/router.py
agents/requirements.py
```

---

## Team Member 2 — Code + Testing Engine

### Responsibilities

- Generate Python code
- Generate unit tests
- Build execution engine
- Capture pytest results

### Main Files

```text
agents/python_coder.py
agents/tester.py
executor.py
```

---

## Team Member 3 — Gradio UI

### Responsibilities

- Build frontend UI
- Show logs/results
- Display generated code
- Improve demo experience

### Main Files

```text
app.py
```

---

## Team Member 4 — Presentation + Integration

### Responsibilities

- Create PPT
- Prepare architecture diagram
- Help integrate modules
- Handle demo flow
- Prepare backup screenshots/videos

### Deliverables

- 5-slide presentation
- demo narration
- architecture explanation

---

# Example Flow

## Input

```text
Create Python palindrome checker
```

## System Output

### Generated Code

```python
def is_palindrome(s):
    s = s.lower()
    return s == s[::-1]
```

### Generated Tests

```python
def test_palindrome():
    assert is_palindrome("madam")
```

### Execution Result

```text
2 tests passed
```

### Evaluation

```text
Correctness: 10/10
Code Quality: 8/10
```

### Session History

```text
Prompt: Create palindrome checker
Score: 9.2
Tests Passed: Yes
```

---

# Future Scope

Possible future improvements:

- Multi-language support
- Docker sandboxing
- Code optimization agent
- Security analysis agent
- AI debugging agent
- Autonomous software engineering pipeline

---

# Key Selling Point

This system demonstrates how multiple AI agents can collaboratively simulate a real-world software engineering workflow.

Unlike traditional AI code generation tools, this system also:

- validates code
- executes tests
- evaluates quality automatically
- tracks execution history

---

# Success Criteria

The demo is successful if:

- User enters prompt
- Python code is generated dynamically
- Tests are generated automatically
- Tests execute successfully
- Evaluation report is displayed
- Session history is stored in memory
- UI clearly shows multi-agent workflow

---

# Important Notes

- Keep architecture simple
- Focus on reliability over complexity
- Stable demo is more important than advanced features
- Python support is mandatory
- In-memory storage is sufficient for MVP
- No SQL database required
- Gradio UI adds bonus points

---

# Recommended Prompting Strategy

Use focused prompts for each agent.

---

## Python Code Agent Prompt

```text
You are a Python coding expert.

Generate clean executable Python code.

Return only Python code.

Task:
Create palindrome checker.
```

---

## Test Agent Prompt

```text
Generate pytest unit tests for the following Python function.
```

---

# Demo Pitch

"We built a Multi-Agent AI Coding System where specialized AI agents collaborate to generate, test, execute, and evaluate Python code automatically from natural language requirements."
