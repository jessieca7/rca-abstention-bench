"""Settings, read from environment variables (and a local .env file).

Switching from Ollama to another provider later (Gemini, Groq, ...) means
changing only these three values in .env. No code changes.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Project root = two levels above this file's package folder (src/<pkg>/config.py).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str
    model: str
    api_key: str
    log_path: Path


def load_settings() -> Settings:
    return Settings(
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("LLM_MODEL", "llama3.2:3b"),
        api_key=os.getenv("LLM_API_KEY", "ollama"),
        log_path=PROJECT_ROOT / "results" / "raw" / "llm_calls.jsonl",
    )
