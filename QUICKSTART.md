# Quick Start Guide - Multi-Agent Code Generation System

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys (2 min)

Create `.env` file in project root:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Groq (free): https://console.groq.com/keys

### Step 3: Run Demo (1 min)
```bash
python demo.py
```

This tests all components before launching the UI.

### Step 4: Launch UI (1 min)
```bash
python app.py
```

Open browser to: **http://127.0.0.1:7860**

---

## 🎯 How to Use the Dashboard

### Input Section (Left Panel)

1. **Enter Prompt** - Describe the code you want:
   ```
   Create a palindrome checker
   ```

2. **Or Select Example** - Choose from pre-loaded examples

3. **Click "🚀 Generate Solution"** - Watch agents work in real-time

### Results Section (Right Panel)

6 tabs showing:
- **Generated Code** - The created Python code
- **Generated Tests** - Pytest test cases
- **Execution Results** - Test pass/fail output
- **Evaluation Report** - Coverage and quality metrics
- **Agent Trace** - Detailed workflow logs
- **Architecture** - System diagram

---

## 📊 Example Workflow

### Input
```
Create a function that checks if a string is a palindrome
```

### Output (Automatic)

1. ✅ **Router Agent** - Detects Python task
2. ✅ **Requirements Agent** - Extracts: ["accepts string", "returns bool", "case insensitive"]
3. ✅ **Code Agent** - Generates palindrome function
4. ✅ **Test Agent** - Creates 8 pytest test cases
5. ✅ **Execution Agent** - Runs tests: 8/8 PASSED ✓
6. ✅ **Evaluation Agent** - Reports 100% coverage

---

## 🔧 Configuration

### Switch LLM Provider

**To use Groq instead of OpenAI:**

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### Customize Example Prompts

Edit `app.py`, find `EXAMPLE_PROMPTS` list:

```python
EXAMPLE_PROMPTS = [
    "Your custom prompt 1",
    "Your custom prompt 2",
]
```

---

## 📁 Project Structure

```
multi_agent_code_gen/
├── app.py                 ← Main Gradio dashboard
├── demo.py                ← Test script
├── executor.py            ← Test runner
├── requirements.txt       ← Dependencies
├── .env                   ← API keys (create this)
│
├── agents/                ← AI agents
│   ├── router.py          
│   ├── requirements_agent.py
│   ├── python_coder.py    
│   ├── test_writer.py     
│   └── evaluator.py       
│
└── llm/                   ← LLM integration
    └── llm_client.py      
```

---

## ⚙️ Agent Responsibilities

| Agent | Task |
|-------|------|
| **Router** | Detect task type (Python/SQL) |
| **Requirements** | Extract structured requirements |
| **Code Generator** | Write Python code |
| **Test Generator** | Create pytest test cases |
| **Executor** | Run tests, capture results |
| **Evaluator** | Compute coverage & metrics |

---

## 🐛 Troubleshooting

### API Key Error
```
Error: OPENAI_API_KEY is missing or still uses the placeholder value
```
**Fix:** Add valid API key to `.env` file

### Port Already in Use
```
Error: Address already in use
```
**Fix:** Kill existing process or use different port:
```python
# In app.py:
app.launch(server_port=7861)
```

### Test Timeout
```
Test execution timed out after 10 seconds
```
**Likely:** Infinite loop in generated code. Check code output.

### Empty LLM Response
```
Error: LLM returned an empty response
```
**Fix:** Try different prompt or check API rate limits

---

## 🎓 Educational Use Cases

### Teaching AI/Agents
- Demonstrate multi-agent collaboration
- Show LLM capabilities in code generation
- Visualize AI decision-making

### Learning Python
- Generate code examples
- Understand test-driven development
- See real pytest usage

### Prototyping
- Quickly generate boilerplate
- Test algorithm ideas
- Create function templates

---

## 🚀 Advanced Features

### Session History
Code automatically saves execution history in memory. Access via:
```python
from memory.session_store import session_store
history = session_store.get_history()
```

### Export Results
Results shown in dashboard can be copied/downloaded:
- Copy code button in Generated Code tab
- Export as JSON via Session History

### Custom Styling
Modify Gradio theme in `app.py`:
```python
gr.Blocks(theme=gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="purple"
))
```

---

## 📊 Sample Prompts to Try

```
1. Create a function to check if a number is prime
2. Write a binary search implementation
3. Generate a function to reverse a string
4. Create a function to calculate Fibonacci
5. Write code to find max value in a list
6. Create a person class with name and age
7. Generate a merge sort implementation
8. Write a function to check anagrams
```

---

## 🎤 Hackathon Demo Tips

1. **Start Simple** - Begin with palindrome checker
2. **Show Real-Time** - Point out logs updating
3. **Highlight Metrics** - Show coverage percentage
4. **Explain Flow** - Walk through agent handoff
5. **Compare** - Mention unique multi-agent approach
6. **Live Test** - Try 2-3 different prompts
7. **Show Code Quality** - Review generated tests

---

## 📈 Next Steps

1. ✅ Complete setup (follow 5-min guide)
2. ✅ Run `demo.py` to test components
3. ✅ Launch `app.py` to see dashboard
4. ✅ Try different prompts
5. ✅ Explore agent implementations
6. ✅ Customize for your use case

---

## 💡 Pro Tips

- **API Cost:** Use Groq free tier to avoid charges
- **Fast Responses:** Groq model is faster than OpenAI
- **Better Code:** GPT-4 generates more readable code than mini models
- **Iterations:** Try similar prompts to see consistency
- **Error Learning:** Note agent limitations with complex requests

---

## 📞 Common Questions

**Q: Can I generate other languages?**
A: Currently Python only. Router detects Python/SQL but SQL code gen not implemented.

**Q: Is execution sandboxed?**
A: Yes, tests run in isolated `sandbox/` directory with 10-second timeout.

**Q: Can I see the prompts sent to LLM?**
A: Check agent files (e.g., `agents/python_coder.py`) for system prompts.

**Q: How long does execution take?**
A: Usually 5-15 seconds depending on LLM provider (Groq faster).

**Q: Can I deploy this?**
A: Yes, but needs security hardening for production (auth, rate limiting, etc).

---

**Ready to launch?** Run: `python app.py` 🚀
