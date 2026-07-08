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


def test_executor_prompts_on_human_task(
    dummy_executor_llm,
    sample_tasks,
    monkeypatch,
    caplog,
) -> None:
    """The executor should pause, prompt the user, and return a completed artifact for HUMAN tasks."""

    human_task = sample_tasks[1]
    
    # Mock input to return instantly and capture the prompt string
    prompt_calls = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompt_calls.append(prompt))
    
    executor = ExecutorAgent(llm=dummy_executor_llm)
    with caplog.at_level(logging.INFO):
        artifact = executor.execute(
            task=human_task,
            user_request="Onboard a new warehouse supervisor.",
        )
        
    assert isinstance(artifact, Artifact)
    assert artifact.task_id == human_task.id
    assert artifact.metadata["status"] == "completed"
    assert "Pausing for human task completion." in caplog.text
    assert len(prompt_calls) == 1
    assert f"Task requires supervisor action: {human_task.name}." in prompt_calls[0]
