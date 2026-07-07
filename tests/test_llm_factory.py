"""Tests for the LLM factory."""

from __future__ import annotations

import pytest

from warehouse_assistant.exceptions import ConfigurationError
import warehouse_assistant.llm_factory as llm_factory
from warehouse_assistant.llm_factory import create_llm_client


def test_llm_factory_rejects_unknown_provider() -> None:
    """An unsupported provider should raise a configuration error."""

    with pytest.raises(ConfigurationError):
        create_llm_client(provider="unknown-provider")


def test_llm_factory_routes_to_gemini(monkeypatch) -> None:
    """The factory should route provider selection without changing agent code."""

    calls: list[tuple[str, str, float, str | None]] = []

    def fake_gemini(
        model_name: str,
        temperature: float,
        api_key: str | None,
    ) -> dict[str, str]:
        """Capture Gemini factory calls."""

        calls.append(("gemini", model_name, temperature, api_key))
        return {"provider": "gemini"}

    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setattr(llm_factory, "_create_gemini_client", fake_gemini)
    result = create_llm_client(
        provider="gemini",
        model_name="gemini-test",
        temperature=0.25,
    )

    assert result == {"provider": "gemini"}
    assert calls == [("gemini", "gemini-test", 0.25, "test-google-key")]


def test_llm_factory_routes_to_openai_compatible_api(monkeypatch) -> None:
    """The factory should pass API key and base URL to OpenAI-compatible APIs."""

    calls: list[tuple[str, float, str | None, str | None]] = []

    def fake_openai(
        model_name: str,
        temperature: float,
        api_key: str | None,
        base_url: str | None,
    ) -> dict[str, str]:
        """Capture OpenAI factory calls."""

        calls.append((model_name, temperature, api_key, base_url))
        return {"provider": "openai"}

    monkeypatch.setenv("CUSTOM_API_KEY", "test-openai-key")
    monkeypatch.setattr(llm_factory, "_create_openai_client", fake_openai)
    result = create_llm_client(
        provider="openai",
        model_name="gpt-test",
        api_key_env_var="CUSTOM_API_KEY",
        api_base_url="https://example.test/v1",
        temperature=0.1,
    )

    assert result == {"provider": "openai"}
    assert calls == [
        ("gpt-test", 0.1, "test-openai-key", "https://example.test/v1")
    ]
