"""Tests for the structured data models."""

from __future__ import annotations

from warehouse_assistant.models import (
    Artifact,
    ExecutionMetrics,
    OnboardingPlan,
    Task,
    TaskType,
    WorkflowResult,
)


def test_task_model_accepts_valid_data(sample_tasks: list[Task]) -> None:
    """A task with valid data should be created successfully."""

    task = sample_tasks[0]
    assert task.id == "task_1"
    assert task.task_type == TaskType.AUTO


def test_plan_model_accepts_valid_data(sample_plan: OnboardingPlan) -> None:
    """A valid plan should preserve the request and tasks."""

    assert sample_plan.request == "Onboard a new warehouse supervisor."
    assert len(sample_plan.tasks) == 2


def test_artifact_model_accepts_valid_data(sample_artifacts: list[Artifact]) -> None:
    """A valid artifact should retain the task linkage and payload."""

    artifact = sample_artifacts[0]
    assert artifact.task_id == "task_1"
    assert artifact.value.startswith("Create access")


def test_workflow_result_model_combines_plan_and_metrics(
    sample_plan: OnboardingPlan,
    sample_artifacts: list[Artifact],
) -> None:
    """A workflow result should be instantiable from the component models."""

    result = WorkflowResult(
        request=sample_plan.request,
        plan=sample_plan,
        artifacts=sample_artifacts,
        metrics=ExecutionMetrics(
            planning_time_seconds=0.1,
            execution_time_seconds=0.2,
            total_runtime_seconds=0.3,
            number_of_tasks=2,
            auto_tasks=1,
            human_tasks=1,
        ),
    )
    assert result.metrics.number_of_tasks == 2
    assert len(result.artifacts) == 2
