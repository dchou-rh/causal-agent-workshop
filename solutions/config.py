import os

from dotenv import load_dotenv

load_dotenv()

ALLOWED_MODELS = frozenset({
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
})

DEFAULT_MODEL = "openai/gpt-oss-20b"


def get_groq_model() -> str:
    """Return the Groq model ID from GROQ_MODEL, or the workshop default."""
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL).strip()
    if model not in ALLOWED_MODELS:
        allowed = ", ".join(sorted(ALLOWED_MODELS))
        raise ValueError(f"GROQ_MODEL must be one of: {allowed}. Got: {model!r}")
    return model
