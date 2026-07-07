"""Shared pytest fixtures for the warehouse onboarding assistant tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from warehouse_assistant.models import Artifact, OnboardingPlan, Task, TaskType


@dataclass
class DummyStructuredOutput:
    """Simple stand-in for a LangChain structured output runnable."""

    output: Any

    def invoke(self, prompt: str) -> Any:
        """Return the configured output regardless of the prompt."""

        if callable(self.output):
            return self.output(prompt)
        if isinstance(self.output, list):
            if not self.output:
                raise AssertionError(
                    "DummyStructuredOutput ran out of configured outputs."
                )
            return self.output.pop(0)
        return self.output


class DummyLLM:
    """Minimal LLM double with the ``with_structured_output`` interface."""

    def __init__(self, output: Any) -> None:
        """Store the output that should be returned by the dummy runnable."""

        self.output = output
        self.prompts: list[str] = []

    def with_structured_output(self, schema: type[Any]) -> DummyStructuredOutput:
        """Return a runnable that records prompt invocations."""

        del schema
        return DummyStructuredOutput(self.output)


@pytest.fixture()
def sample_tasks() -> list[Task]:
    """Return a small valid task graph."""

    return [
        Task(
            id="task_1",
            name="Provision access",
            description="Create required system access.",
            dependency_ids=[],
            task_type=TaskType.AUTO,
            artifact_type="checklist",
            artifact_instruction="Summarize the access provisioning steps.",
        ),
        Task(
            id="task_2",
            name="Schedule safety orientation",
            description="Set up mandatory safety orientation.",
            dependency_ids=["task_1"],
            task_type=TaskType.HUMAN,
            artifact_type="email",
            artifact_instruction="Draft a scheduling note for the safety orientation.",
        ),
    ]


@pytest.fixture()
def sample_plan(sample_tasks: list[Task]) -> OnboardingPlan:
    """Return a valid structured onboarding plan."""

    return OnboardingPlan(
        request="Onboard a new warehouse supervisor.",
        tasks=sample_tasks,
        summary="Provision access and schedule orientation.",
        assumptions=["The new supervisor has an employee record already."],
    )


@pytest.fixture()
def sample_artifacts() -> list[Artifact]:
    """Return a valid list of artifacts."""

    return [
        Artifact(
            task_id="task_1",
            artifact_type="checklist",
            value="Create access, confirm permissions, and record completion.",
            metadata={"format": "markdown"},
        ),
        Artifact(
            task_id="task_2",
            artifact_type="email",
            value="Draft a scheduling email for safety orientation.",
            metadata={"format": "plain_text"},
        ),
    ]


@pytest.fixture()
def sample_task(sample_tasks: list[Task]) -> Task:
    """Return a representative task for executor tests."""

    return sample_tasks[0]


@pytest.fixture()
def dummy_planner_llm(sample_plan: OnboardingPlan) -> DummyLLM:
    """Return a planner double that produces the sample plan."""

    return DummyLLM(sample_plan)


@pytest.fixture()
def dummy_executor_llm(sample_artifacts: list[Artifact]) -> DummyLLM:
    """Return an executor double that produces the sample artifacts in order."""

    return DummyLLM(sample_artifacts.copy())
