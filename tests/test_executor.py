"""Tests for the executor agent."""

from __future__ import annotations

import logging

import pytest

from warehouse_assistant.exceptions import ExecutorError
from warehouse_assistant.agents.executor import ExecutorAgent
from warehouse_assistant.models import Artifact


def test_executor_returns_one_artifact(
    dummy_executor_llm,
    sample_task,
    caplog,
) -> None:
    """The executor should return the structured artifact produced by the mock LLM."""

    executor = ExecutorAgent(llm=dummy_executor_llm)
    with caplog.at_level(logging.INFO):
        artifact = executor.execute(
            task=sample_task,
            user_request="Onboard a new warehouse supervisor.",
        )
    assert isinstance(artifact, Artifact)
    assert artifact.task_id == "task_1"
    assert "executor start" in caplog.text
    assert "executor finish" in caplog.text


def test_executor_wraps_llm_failures(sample_task) -> None:
    """Executor LLM failures should be converted into ExecutorError."""

    class FailingRunnable:
        """Runnable double that always fails when invoked."""

        def invoke(self, prompt: str) -> None:
            """Raise a failure to simulate an LLM outage."""

            del prompt
            raise ValueError("boom")

    class FailingLLM:
        """LLM double that returns the failing runnable."""

        def with_structured_output(self, schema: type[Artifact]) -> FailingRunnable:
            """Return a runnable that raises on invoke."""

            del schema
            return FailingRunnable()

    executor = ExecutorAgent(llm=FailingLLM())
    with pytest.raises(ExecutorError):
        executor.execute(
            task=sample_task,
            user_request="Onboard a new warehouse supervisor.",
        )
