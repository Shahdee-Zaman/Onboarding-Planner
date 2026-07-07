"""Central application configuration.

Edit this file or the matching values in ``.env`` to choose which LLM provider,
model, and API settings the assistant should use.
"""

from __future__ import annotations

import os
from typing import Final

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed for normal installs
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

# --- Model Configuration ---
# Choose your provider: 'ollama', 'gemini', or 'openai'
LLM_PROVIDER: Final[str] = "gemini"

# Choose your model. Examples:
# - ollama: "llama3.1", "llama3", "mistral"
# - gemini: "gemini-1.5-flash", "gemini-1.5-pro"
# - openai: "gpt-4o", "gpt-4o-mini"
MODEL_NAME: Final[str] = "gemini-2.5-flash"

# --- API Configuration ---
# API keys are securely loaded from the .env file.
# Specify which environment variable contains the API key for your chosen provider.
# Examples: "GOOGLE_API_KEY" (for gemini), "OPENAI_API_KEY" (for openai). 
# Leave as empty string "" for local providers like ollama.
API_KEY_ENV_VAR: Final[str] = "GOOGLE_API_KEY"

# Optional API base URL (e.g., for local OpenAI-compatible endpoints)
API_BASE_URL: Final[str] = ""

# --- Other Settings ---
TEMPERATURE: Final[float] = 0.0
LOG_LEVEL: Final[str] = "INFO"

OLLAMA_MODEL_NAME: Final[str] = MODEL_NAME
GEMINI_MODEL_NAME: Final[str] = MODEL_NAME

DEFAULT_ARTIFACT_TYPE: Final[str] = "text"
DEFAULT_TASK_TYPE: Final[str] = "auto"
