# Environment Configuration Guide

## Overview
This guide explains how to set up and configure the Multi-Agent Code Generation System.

## Prerequisites
- Python 3.11 or higher
- pip package manager
- API key from OpenAI or Groq

## Step 1: Get API Keys

### Option A: OpenAI (Paid, Recommended for Production)

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Create new API key
4. Copy the key (won't be shown again)

**Recommended Model:** `gpt-4o-mini` (cheap and capable)

### Option B: Groq (Free, Recommended for Demo)

1. Go to: https://console.groq.com/keys
2. Create account (uses social login)
3. Create API key in console
4. Copy the key

**No rate limits or cost!**

## Step 2: Create .env File

In the project root directory, create a file named `.env`:

```
project_root/
├── app.py
├── .env                ← Create this file
├── requirements.txt
└── ...
```

## Step 3: Configure .env File

### Option A: OpenAI Setup

```env
# LLM Provider
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

Replace `sk-proj-xxxxxxxxxxxxxxxxxxxx` with your actual API key.

### Option B: Groq Setup

```env
# LLM Provider
LLM_PROVIDER=groq

# Groq Configuration
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

Replace `gsk-xxxxxxxxxxxxxxxxxxxx` with your actual API key.

## Step 4: Verify Configuration

Run the demo to verify everything works:

```bash
python demo.py
```

You should see a complete workflow execute without errors.

## Troubleshooting Configuration

### Error: "API key is missing or invalid"

**Problem:** .env file not found or API key is wrong

**Solution:**
1. Check .env file exists in project root
2. Verify API key is correct (not expired, no typos)
3. Make sure no quotes around the key value

**Example (WRONG):**
```env
OPENAI_API_KEY="sk-proj-xxx"  # Don't use quotes
```

**Example (CORRECT):**
```env
OPENAI_API_KEY=sk-proj-xxx    # No quotes
```

### Error: "Unsupported LLM_PROVIDER 'xxx'"

**Problem:** Invalid provider name

**Solution:** Use only `openai` or `groq` (case-sensitive, lowercase)

**Example (WRONG):**
```env
LLM_PROVIDER=OpenAI     # Wrong case
LLM_PROVIDER=gpt-4      # Not a provider
```

**Example (CORRECT):**
```env
LLM_PROVIDER=openai
LLM_PROVIDER=groq
```

### Error: "Rate limit exceeded"

**Problem:** Too many API calls to LLM provider

**Solution:**
- Wait a few minutes before retrying
- Use different provider (Groq has no limits for free tier)
- Check your API dashboard for usage

### Error: "Connection timeout"

**Problem:** Can't reach LLM API servers

**Solution:**
1. Check internet connection
2. Check if API service is down (check status page)
3. Try with different provider
4. Try from different network

## Advanced Configuration

### Custom LLM Model

You can use different models from the same provider:

```env
# Use GPT-4 (more capable, more expensive)
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4

# Use different Groq model
LLM_PROVIDER=groq
GROQ_MODEL=mixtral-8x7b-32768
```

**Available OpenAI Models:**
- `gpt-4` - Most capable (expensive)
- `gpt-4-turbo` - Faster than gpt-4
- `gpt-4o` - Best for code generation
- `gpt-4o-mini` - Cheapest, good quality

**Available Groq Models:**
- `llama-3.3-70b-versatile` - Fast, good quality
- `mixtral-8x7b-32768` - Alternative
- `llama-2-70b-chat` - Older but stable

### Temperature Setting

The system uses `temperature=0.2` by default (deterministic, good for code).

To modify, edit in `llm/llm_client.py`:

```python
response = client.chat.completions.create(
    model=model,
    messages=[...],
    temperature=0.2  # 0 = deterministic, 1 = creative
)
```

Lower = more deterministic code
Higher = more creative/varied

## Security Best Practices

### Do NOT commit .env file

Add to `.gitignore`:
```
.env
.env.local
*.key
```

### Do NOT share your API key

- Don't post in chat/forums
- Don't commit to GitHub
- Don't share with others

### Use environment variables in production

For deployment, use your platform's secret management:
- GitHub Secrets (for CI/CD)
- AWS Secrets Manager
- Azure Key Vault
- Heroku Config Vars
- etc.

Example for Gradio deployment:
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

## Example .env Files

### For Development (OpenAI)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-test-key
OPENAI_MODEL=gpt-4o-mini
```

### For Development (Groq)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-free-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### For Production Deployment

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=${OPENAI_API_KEY}        # From platform secrets
OPENAI_MODEL=gpt-4o

# Add for production
DEBUG=false
LOG_LEVEL=INFO
MAX_EXECUTION_TIMEOUT=30
```

## Testing Configuration

After setting up .env, verify it works:

```bash
# Test 1: Run demo
python demo.py

# Test 2: Check imports
python -c "from llm.llm_client import call_llm; print('✓ LLM imports OK')"

# Test 3: Test single agent
python -c "from agents.router import route_request; print(route_request('Create palindrome checker'))"

# Test 4: Launch UI
python app.py
```

## FAQ

**Q: Can I use multiple API keys?**
A: The system uses one provider at a time. Create separate .env files or use CI/CD secrets.

**Q: What if I don't have API credit?**
A: Use Groq (free, unlimited within fair use). OpenAI offers $5 free trial.

**Q: Can I switch providers mid-project?**
A: Yes, just change `LLM_PROVIDER` and add the appropriate API key.

**Q: Is my API key safe in .env?**
A: Yes if you keep it private. Add `.env` to `.gitignore`.

**Q: What if I have multiple projects?**
A: Create separate .env files for each, or use environment variable overrides.

---

**Next:** Run `python demo.py` to test your configuration!
