# Copilot / Codex Project Setup Prompt

You are helping build a hackathon project called:

# Multi-Agent Natural Language to Code System

Read the project architecture and requirements from:

```text
MULTI_AGENT_NL_TO_CODE_SYSTEM.md
```

Follow the architecture and implementation details strictly.

---

# Goal

Build a Python-based multi-agent AI system that:

1. Accepts natural language coding requests
2. Generates Python code dynamically using LLM
3. Generates pytest unit tests automatically
4. Executes generated tests
5. Evaluates generated solution quality
6. Stores lightweight execution history in memory
7. Displays all outputs in Gradio UI

---

# Important Constraints

- Python only
- Keep architecture simple
- Focus on stable demo
- No database required
- No authentication
- No vector DB
- No complex autonomous loops
- No microservices
- No production deployment logic

---

# Required Stack

## Language

- Python 3.11+

## UI

- Gradio

## AI

- OpenAI
- Groq

## Workflow

- LangGraph OR simple orchestration

## Testing

- pytest

---

# Required Project Structure

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

# Current Task

Create the initial project setup with:

1. Folder structure
2. requirements.txt
3. .env.example
4. Base Gradio app
5. Base workflow pipeline
6. Stub agent files
7. Shared llm client
8. In-memory session store
9. Git repository setup files
10. README setup and run instructions

---

# Requirements

## 1. Project Setup

Create the required Python project foundation.

Required setup files:

```text
requirements.txt
.env.example
.gitignore
README.md
```

`requirements.txt` must include:

```text
openai
langgraph
gradio
pytest
python-dotenv
rich
```

`.env.example` must include:

```env
LLM_PROVIDER=openai

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

`.gitignore` must exclude:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
.DS_Store
sandbox/generated_code.py
sandbox/test_generated_code.py
```

`README.md` must include:

- project overview
- setup steps
- virtual environment creation
- dependency installation
- `.env` creation from `.env.example`
- local Gradio run command
- example prompts

Recommended local setup commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

---

## 2. Git Setup

Set up the project so it is ready for Git.

Required Git deliverables:

1. Create `.gitignore`
2. Keep secrets out of Git
3. Track `.env.example`, not `.env`
4. Track source files, docs, and requirements
5. Do not track generated runtime files or cache folders

If Git has not been initialized yet, run:

```bash
git init
git add .
git commit -m "Initial multi-agent code generation setup"
```

Before committing, verify:

```bash
git status
```

Important:

- Do not commit `.env`
- Do not commit API keys
- Do not commit virtual environments
- Do not commit Python cache files
- Do not commit pytest cache files

---

## 3. LLM Provider Switching

Support:

- OpenAI
- Groq

Switch provider dynamically using `.env`.

---

## 4. Shared LLM Client

Create reusable:

```text
llm/llm_client.py
```

Responsibilities:

- initialize provider
- switch model dynamically
- expose reusable `call_llm()` function
- read configuration from environment variables
- fail with helpful error messages when API keys are missing

---

## 5. Gradio UI

Create minimal clean UI with:

- prompt textbox
- generate button
- generated code section
- generated tests section
- execution logs
- evaluation section
- session history section

---

## 6. In-Memory Session Store

Create lightweight session tracking.

Store:

- prompt
- score
- tests passed
- timestamp

No database required.

---

# Workflow Logic

```python
task = router_agent(user_prompt)

requirements = requirements_agent(user_prompt)

code = python_code_agent(requirements)

tests = test_agent(code)

result = executor(code, tests)

evaluation = evaluator(result)

save_result(...)
```

---

# Coding Guidelines

- Use meaningful names
- Keep files modular
- Use comments where useful
- Keep code beginner-friendly
- Avoid overengineering
- Keep hackathon speed in mind
- Make the project runnable after setup
- Use safe placeholders where real LLM behavior will be added later
- Avoid committing secrets or generated runtime artifacts

---

# Important

Do NOT implement advanced features yet.

Only create:
- clean setup
- reusable structure
- working foundation
- placeholder agent implementations
- git-ready repository files

We will implement agents incrementally later.
