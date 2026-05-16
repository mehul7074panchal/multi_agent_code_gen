# Multi-Agent Natural Language to Code System

A sophisticated, production-grade Gradio dashboard for demonstrating AI-powered code generation through collaborative multi-agent orchestration.

## 🎯 Overview

This project showcases a **multi-agent workflow** where multiple specialized AI agents work together like a real software engineering team:

```
User Prompt → Router → Requirements → Code Gen → Test Gen → Execution → Evaluation
```

The system automatically:
- ✅ Understands user requests
- ✅ Generates clean Python code
- ✅ Creates comprehensive unit tests
- ✅ Executes tests in an isolated sandbox
- ✅ Evaluates code quality and coverage
- ✅ Displays results in a professional dashboard

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Valid API key for OpenAI or Groq

### Installation

1. **Clone and navigate to project directory:**
```bash
cd multi_agent_code_gen
```

2. **Create virtual environment (optional but recommended):**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the project root:

```env
# LLM Provider Selection
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Alternative: Groq Configuration
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_groq_api_key_here
# GROQ_MODEL=llama-3.3-70b-versatile
# GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### Running the Application

```bash
python app.py
```

The application will launch at:
- **Local:** http://127.0.0.1:7860
- **Public Share:** Use `--share` flag for temporary public link

To enable public sharing:
```bash
# In app.py, modify the launch call:
app.launch(share=True)
```

## 📊 Project Structure

```
multi_agent_code_gen/
├── app.py                          # Main Gradio UI application
├── executor.py                     # Test execution engine
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration
│
├── agents/
│   ├── __init__.py
│   ├── router.py                  # Route requests to appropriate agent
│   ├── requirements_agent.py       # Extract structured requirements
│   ├── python_coder.py             # Generate Python code
│   ├── test_writer.py              # Generate pytest test cases
│   └── evaluator.py                # Evaluate code quality & coverage
│
├── llm/
│   ├── __init__.py
│   └── llm_client.py               # Unified LLM interface
│
├── memory/
│   ├── __init__.py
│   └── session_store.py            # In-memory execution history
│
└── sandbox/                        # Generated code & test execution
    ├── generated_code.py
    └── test_generated_code.py
```

## 🔄 Workflow Architecture

### 1. **Router Agent** (`agents/router.py`)
- Analyzes user request
- Detects language (Python/SQL)
- Routes to appropriate code generation agent

**Input:** Natural language prompt
**Output:** Task type and target agent

### 2. **Requirements Agent** (`agents/requirements_agent.py`)
- Parses user request
- Extracts structured requirements
- Identifies key features and constraints

**Output:** JSON with task, language, and requirement list

### 3. **Code Generation Agent** (`agents/python_coder.py`)
- Generates clean, executable Python code
- Uses LLM with zero-temperature setting
- Removes markdown formatting

**Output:** Valid Python code

### 4. **Test Generation Agent** (`agents/test_writer.py`)
- Creates comprehensive pytest test cases
- Includes positive and negative scenarios
- Adds edge case and error handling tests

**Output:** Pytest test code

### 5. **Execution Agent** (`executor.py`)
- Saves code and tests to isolated sandbox
- Runs pytest with 10-second timeout
- Captures output and exit codes

**Output:** Test results (pass/fail counts, stdout, stderr)

### 6. **Evaluation Agent** (`agents/evaluator.py`)
- Performs static code coverage analysis using AST
- Calculates test metrics
- Generates quality report

**Output:** Coverage percentage, function coverage, test metrics

## 🎨 UI Features

### Dashboard Components

#### Left Panel
- **Prompt Input:** Large textbox for coding requests
- **Quick Examples:** Pre-loaded example prompts
- **Workflow Progress:** Visual pipeline showing agent execution
- **Live Logs:** Real-time agent activity monitoring

#### Right Panel - Tabbed Results

1. **Generated Code**
   - Syntax highlighted Python code
   - Code statistics (lines, functions, classes)
   - Dark theme editor styling

2. **Generated Tests**
   - pytest test cases
   - Test function count
   - Test metrics summary

3. **Execution Results**
   - Pytest output with pass/fail indicators
   - Test summary (passed/failed counts)
   - Execution time and return codes
   - Color-coded results (green=pass, red=fail)

4. **Evaluation Report**
   - Coverage percentage gauge
   - Quality metrics cards
   - Function coverage table
   - Recommendations panel

5. **Agent Trace**
   - Detailed log of agent activities
   - Input/output for each agent
   - Execution timing information
   - Decision making details

6. **Architecture View**
   - Visual system architecture diagram
   - Agent descriptions and roles
   - Data flow visualization

## 🔧 Configuration

### LLM Provider Selection

**OpenAI (Recommended)**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Groq (Alternative)**
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-...
GROQ_MODEL=llama-3.3-70b-versatile
```

### Customization

Modify these values in `app.py`:

```python
# Add more example prompts
EXAMPLE_PROMPTS = [
    "Your custom prompt here",
    "Another example",
]

# Adjust workflow state management
TIMEOUT_SECONDS = 10  # Test execution timeout
```

## 📝 Example Prompts

```
1. Create a Python palindrome checker
2. Write a function to check if a number is prime
3. Generate a binary search implementation
4. Create a function to reverse a string
5. Write code to calculate factorial
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `gradio` | Web UI framework |
| `openai` | OpenAI API client |
| `pytest` | Test execution framework |
| `python-dotenv` | Environment variable management |
| `rich` | Terminal formatting (logs) |
| `langgraph` | Optional: Agent graph orchestration |

## 🐛 Troubleshooting

### Issue: "API key missing or invalid"
**Solution:** Verify `.env` file has valid API key for your selected provider

### Issue: "Test execution timeout"
**Solution:** Code may have infinite loops. Check generated code in editor

### Issue: "LLM returned empty response"
**Solution:** Try with a more specific prompt. Check API rate limits

### Issue: Port 7860 already in use
**Solution:** Change port in app.py:
```python
app.launch(server_name="127.0.0.1", server_port=7861)
```

## 🎓 Learning Path

1. **Understand the workflow** → Read MULTI_AGENT_NL_TO_CODE_SYSTEM.md
2. **Explore agent implementations** → Check agents/ directory
3. **Try the UI** → Run `python app.py`
4. **Modify prompts** → Test with custom requests
5. **Customize styling** → Edit Gradio theme in app.py

## 🌟 Key Features

- ✨ **Professional Dashboard:** Modern, responsive UI with dark theme
- 🎯 **Real-time Visualization:** Watch agents work in real-time
- 📊 **Comprehensive Metrics:** Coverage, quality scores, test results
- 🔧 **LLM Agnostic:** Switch between OpenAI and Groq with one config
- 💾 **Session Tracking:** In-memory execution history
- 🎨 **Beautiful Design:** Gradient backgrounds, smooth animations
- 📱 **Responsive Layout:** Works on desktop and tablet
- 🚀 **Production Ready:** Clean code, error handling, documentation

## 🚧 Limitations & Notes

- **Python Only:** Currently supports Python code generation
- **No Persistent Storage:** Session history is in-memory only
- **No Authentication:** Not for production deployment without security layers
- **LLM Rate Limits:** Subject to API provider rate limiting
- **Sandbox Security:** Uses simple directory isolation, not true container security

## 📈 Future Enhancements

Possible improvements:
- Multi-language support (JavaScript, Go, Rust)
- Persistent database for execution history
- Docker-based sandboxing
- Code optimization agent
- Security analysis agent
- AI-powered debugging
- Deployment pipeline integration

## 🤝 Contributing

To extend this system:

1. **Add new agents:** Create file in `agents/` directory
2. **Modify UI:** Update functions in `app.py`
3. **Add providers:** Extend `llm/llm_client.py`
4. **Improve testing:** Enhance `agents/test_writer.py` prompts

## 📄 License

MIT License - Feel free to use for education and demos

## 🎤 Demo Tips

For hackathon presentation:
- Start with simple prompts (palindrome checker)
- Watch logs in real-time
- Show code quality metrics
- Highlight multi-agent coordination
- Discuss use cases (education, prototyping, automation)
- Compare with traditional AI code tools

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review agent implementations
3. Test with different prompts
4. Verify API keys and rate limits

---

**Built with ❤️ for Hackathons**

Demonstrates how AI agents can collaborate to simulate real software engineering teams.
