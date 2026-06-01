import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.core.llm_provider import LLMProvider

_PLACEHOLDER_KEYS = (
    "your_openai_api_key_here",
    "your_gemini_api_key_here",
)


def create_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """Load LLM provider from .env (DEFAULT_PROVIDER, DEFAULT_MODEL, API keys)."""
    load_dotenv()

    provider_name = (provider or os.getenv("DEFAULT_PROVIDER", "openai")).lower()
    model_name = model or os.getenv("DEFAULT_MODEL")

    if provider_name == "openai":
        from src.core.openai_provider import OpenAIProvider

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key in _PLACEHOLDER_KEYS:
            raise ValueError(
                "OPENAI_API_KEY is missing or still a placeholder in .env"
            )

        return OpenAIProvider(
            model_name=model_name or "gpt-4o",
            api_key=api_key,
        )

    if provider_name in ("google", "gemini"):
        from src.core.gemini_provider import GeminiProvider

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key in _PLACEHOLDER_KEYS:
            raise ValueError(
                "GEMINI_API_KEY is missing or still a placeholder in .env"
            )

        return GeminiProvider(
            model_name=model_name or "gemini-1.5-flash",
            api_key=api_key,
        )

    if provider_name == "local":
        try:
            from src.core.local_provider import LocalProvider
        except ImportError as e:
            raise ImportError(
                "Local provider requires llama-cpp-python in the active environment.\n"
                "  .\\venv\\Scripts\\activate\n"
                "  pip install llama-cpp-python\n"
                "Or set DEFAULT_PROVIDER=google/openai in .env."
            ) from e

        model_path = os.getenv(
            "LOCAL_MODEL_PATH",
            "./models/Phi-3-mini-4k-instruct-q4.gguf",
        )
        if not Path(model_path).is_file():
            raise FileNotFoundError(
                f"GGUF model not found: {model_path}\n"
                "Download Phi-3 GGUF (see README) into the models/ folder."
            )

        return LocalProvider(model_path=model_path)

    raise ValueError(
        f"Unknown DEFAULT_PROVIDER={provider_name!r}. "
        "Use openai, google/gemini, or local."
    )
