import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)


SUPPORTED_PROVIDERS = {"openai", "xai"}
DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"


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
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

        return OpenAI(api_key=api_key), model

    api_key = os.getenv("XAI_API_KEY")
    model = os.getenv("XAI_MODEL", "grok-3-mini")
    base_url = os.getenv("XAI_BASE_URL", DEFAULT_XAI_BASE_URL)

    if not api_key:
        raise ValueError("XAI_API_KEY is missing. Add it to your .env file.")

    return OpenAI(api_key=api_key, base_url=base_url), model


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call the configured LLM provider and return the response text.

    Provider is selected with LLM_PROVIDER in .env:
    - openai
    - xai
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
