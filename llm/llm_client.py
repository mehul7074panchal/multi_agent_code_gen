import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)


SUPPORTED_PROVIDERS = {"openai", "groq"}
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _require_api_key(value: str | None, env_name: str, provider_name: str) -> str:
    if not value or value.strip().startswith("your_"):
        raise ValueError(
            f"{env_name} is missing or still uses the placeholder value. "
            f"Add a valid {provider_name} API key to your .env file."
        )

    return value.strip()


def _get_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{provider}'. Use one of: {supported}."
        )

    return provider


def _build_client(provider: str) -> tuple[OpenAI, str]:
    if provider == "openai":
        api_key = _require_api_key(
            os.getenv("OPENAI_API_KEY"),
            "OPENAI_API_KEY",
            "OpenAI",
        )
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        return OpenAI(api_key=api_key), model

    api_key = _require_api_key(
        os.getenv("GROQ_API_KEY"),
        "GROQ_API_KEY",
        "Groq",
    )
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    base_url = os.getenv("GROQ_BASE_URL", DEFAULT_GROQ_BASE_URL)

    return OpenAI(api_key=api_key, base_url=base_url), model


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call the configured LLM provider and return the response text.

    Provider is selected with LLM_PROVIDER in .env:
    - openai
    - groq
    """
    if not system_prompt or not system_prompt.strip():
        raise ValueError("System prompt cannot be empty.")

    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    provider = _get_provider()
    client, model = _build_client(provider)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response.")

    return content.strip()
