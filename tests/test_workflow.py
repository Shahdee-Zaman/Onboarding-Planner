"""Integration-style tests for the full workflow."""

from __future__ import annotations

import logging

import pytest

from warehouse_assistant.exceptions import PlannerError, WorkflowError
from warehouse_assistant.agents.executor import ExecutorAgent
from warehouse_assistant.agents.planner import PlannerAgent
from warehouse_assistant.workflow import WarehouseOnboardingWorkflow


def test_workflow_runs_planner_then_executor(
    dummy_planner_llm,
    dummy_executor_llm,
    sample_plan,
    caplog,
) -> None:
    """The workflow should call the planner once and the executor once per task."""

    planner = PlannerAgent(llm=dummy_planner_llm)
    executor = ExecutorAgent(llm=dummy_executor_llm)
    workflow = WarehouseOnboardingWorkflow(planner=planner, executor=executor)

    with caplog.at_level(logging.INFO):
        result = workflow.run("Onboard a new warehouse supervisor.")

    assert result.plan.request == sample_plan.request
    assert len(result.artifacts) == len(sample_plan.tasks)
    assert result.metrics.number_of_tasks == len(sample_plan.tasks)
    assert result.metrics.auto_tasks == 1
    assert result.metrics.human_tasks == 1
    assert "workflow completion" in caplog.text


def test_workflow_wraps_agent_initialization_failures(monkeypatch) -> None:
    """Workflow construction should convert agent initialization failures."""

    class BrokenPlanner:
        """Planner double that fails during initialization."""

        def __init__(self) -> None:
            """Raise an initialization error."""

            raise PlannerError("broken")

    monkeypatch.setattr("warehouse_assistant.workflow.PlannerAgent", BrokenPlanner)

    with pytest.raises(WorkflowError):
        WarehouseOnboardingWorkflow()
