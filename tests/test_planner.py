"""Tests for the planner agent."""

from __future__ import annotations

import logging

import pytest

from warehouse_assistant.exceptions import PlannerError
from warehouse_assistant.agents.planner import PlannerAgent
from warehouse_assistant.models import OnboardingPlan


def test_planner_returns_structured_plan(dummy_planner_llm, caplog) -> None:
    """The planner should return the structured plan produced by the mock LLM."""

    planner = PlannerAgent(llm=dummy_planner_llm)
    with caplog.at_level(logging.INFO):
        plan = planner.plan("Onboard a new warehouse supervisor.")
    assert isinstance(plan, OnboardingPlan)
    assert plan.tasks[0].id == "task_1"
    assert "planner start" in caplog.text
    assert "planner finish" in caplog.text


def test_planner_wraps_llm_failures() -> None:
    """Planner LLM failures should be converted into PlannerError."""

    class FailingRunnable:
        """Runnable double that always fails when invoked."""

        def invoke(self, prompt: str) -> None:
            """Raise a failure to simulate an LLM outage."""

            del prompt
            raise ValueError("boom")

    class FailingLLM:
        """LLM double that returns the failing runnable."""

        def with_structured_output(
            self,
            schema: type[OnboardingPlan],
        ) -> FailingRunnable:
            """Return a runnable that raises on invoke."""

            del schema
            return FailingRunnable()

    planner = PlannerAgent(llm=FailingLLM())
    with pytest.raises(PlannerError):
        planner.plan("Onboard a new warehouse supervisor.")
