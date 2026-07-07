"""Factory helpers for creating LangChain chat models.

The factory keeps provider-specific imports and configuration in one place so
the rest of the application can switch between Ollama, Gemini, or other
providers without touching agent logic.
"""

from __future__ import annotations

import os
from typing import Any

from .config import API_BASE_URL, API_KEY_ENV_VAR, LLM_PROVIDER, MODEL_NAME, TEMPERATURE
from .exceptions import ConfigurationError


def create_llm_client(
    provider: str | None = None,
    model_name: str | None = None,
    api_key_env_var: str | None = None,
    api_base_url: str | None = None,
    temperature: float | None = None,
) -> Any:
    """Create a chat model client for the requested provider.

    Args:
        provider: LLM provider name such as ``ollama`` or ``gemini``.
        model_name: Optional override for the configured model name.
        api_key_env_var: Optional environment variable name containing an API key.
        api_base_url: Optional API base URL for providers that support it.
        temperature: Sampling temperature passed to the chat model.

    Returns:
        A LangChain-compatible chat model instance.

    Raises:
        ConfigurationError: If the provider is unsupported or unavailable.
    """

    normalized_provider = (provider or LLM_PROVIDER).strip().lower()
    resolved_model = model_name or MODEL_NAME
    resolved_temperature = TEMPERATURE if temperature is None else temperature
    resolved_api_key = _resolve_api_key(
        provider=normalized_provider,
        api_key_env_var=api_key_env_var,
    )
    resolved_base_url = api_base_url or API_BASE_URL or None

    if normalized_provider == "ollama":
        return _create_ollama_client(
            model_name=resolved_model,
            temperature=resolved_temperature,
            base_url=resolved_base_url,
        )
    if normalized_provider == "gemini":
        return _create_gemini_client(
            model_name=resolved_model,
            temperature=resolved_temperature,
            api_key=resolved_api_key,
        )
    if normalized_provider == "openai":
        return _create_openai_client(
            model_name=resolved_model,
            temperature=resolved_temperature,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )
    raise ConfigurationError(
        f"Unsupported LLM provider: '{provider}'."
    )


def _resolve_api_key(
    provider: str,
    api_key_env_var: str | None = None,
) -> str | None:
    """Resolve the configured API key from the environment.

    Args:
        provider: Normalized LLM provider name.
        api_key_env_var: Optional environment variable name containing an API key.

    Returns:
        The API key value, or ``None`` when no key is configured.
    """

    default_env_vars = {
        "gemini": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    env_var = api_key_env_var or API_KEY_ENV_VAR or default_env_vars.get(provider, "")
    if not env_var:
        return None
    return os.getenv(env_var)


def _create_ollama_client(
    model_name: str,
    temperature: float,
    base_url: str | None,
) -> Any:
    """Create a ChatOllama client.

    Args:
        model_name: Ollama model identifier.
        temperature: Sampling temperature for the model.
        base_url: Optional Ollama base URL.

    Returns:
        A configured ChatOllama instance.
    """

    try:
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama
    except ImportError as exc:
        raise ConfigurationError(
            "ChatOllama is not available. Install "
            "langchain-ollama or langchain-community."
        ) from exc
    kwargs: dict[str, Any] = {"model": model_name, "temperature": temperature}
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOllama(**kwargs)


def _create_gemini_client(
    model_name: str,
    temperature: float,
    api_key: str | None,
) -> Any:
    """Create a ChatGoogleGenerativeAI client.

    Args:
        model_name: Gemini model identifier.
        temperature: Sampling temperature for the model.
        api_key: Optional Gemini API key.

    Returns:
        A configured ChatGoogleGenerativeAI instance.
    """

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise ConfigurationError(
            "ChatGoogleGenerativeAI is not available. Install "
            "langchain-google-genai."
        ) from exc
    kwargs: dict[str, Any] = {"model": model_name, "temperature": temperature}
    if api_key:
        kwargs["google_api_key"] = api_key
    return ChatGoogleGenerativeAI(**kwargs)


def _create_openai_client(
    model_name: str,
    temperature: float,
    api_key: str | None,
    base_url: str | None,
) -> Any:
    """Create a ChatOpenAI client.

    Args:
        model_name: OpenAI or OpenAI-compatible model identifier.
        temperature: Sampling temperature for the model.
        api_key: Optional API key.
        base_url: Optional API base URL for compatible endpoints.

    Returns:
        A configured ChatOpenAI instance.
    """

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ConfigurationError(
            "ChatOpenAI is not available. Install langchain-openai."
        ) from exc

    kwargs: dict[str, Any] = {"model": model_name, "temperature": temperature}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)
