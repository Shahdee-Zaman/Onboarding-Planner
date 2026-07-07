"""Tests for plan and artifact validation."""

from __future__ import annotations

import pytest

from warehouse_assistant.exceptions import (
    CyclicDependencyError,
    DuplicateTaskIdError,
    EmptyTaskNameError,
    InvalidArtifactError,
    MissingDependencyError,
)
from warehouse_assistant.models import Artifact, OnboardingPlan, Task, TaskType
from warehouse_assistant.utils.validator import (
    validate_artifact,
    validate_artifacts,
    validate_plan,
)


def test_validate_plan_rejects_duplicate_task_ids(sample_plan: OnboardingPlan) -> None:
    """Duplicate task identifiers should fail validation."""

    sample_plan.tasks.append(sample_plan.tasks[0].model_copy())
    with pytest.raises(DuplicateTaskIdError):
        validate_plan(sample_plan)


def test_validate_plan_rejects_missing_dependencies(sample_tasks: list[Task]) -> None:
    """A missing dependency should fail validation."""

    sample_tasks[1].dependency_ids = ["missing_task"]
    plan = OnboardingPlan(
        request="Test",
        tasks=sample_tasks,
        summary="summary",
    )
    with pytest.raises(MissingDependencyError):
        validate_plan(plan)


def test_validate_plan_rejects_cycles() -> None:
    """A cyclic dependency graph should fail validation."""

    tasks = [
        Task(
            id="task_1",
            name="Task one",
            dependency_ids=["task_2"],
            task_type=TaskType.AUTO,
            artifact_type="checklist",
            artifact_instruction="Do one thing.",
        ),
        Task(
            id="task_2",
            name="Task two",
            dependency_ids=["task_1"],
            task_type=TaskType.AUTO,
            artifact_type="checklist",
            artifact_instruction="Do another thing.",
        ),
    ]
    plan = OnboardingPlan(request="Test", tasks=tasks, summary="summary")
    with pytest.raises(CyclicDependencyError):
        validate_plan(plan)


def test_validate_plan_rejects_blank_task_names() -> None:
    """A blank task name should fail validation."""

    plan = OnboardingPlan(
        request="Test",
        tasks=[
            Task(
                id="task_1",
                name="Valid",
                dependency_ids=[],
                task_type=TaskType.AUTO,
                artifact_type="checklist",
                artifact_instruction="Do something.",
            ),
            Task(
                id="task_2",
                name="   ",
                dependency_ids=[],
                task_type=TaskType.AUTO,
                artifact_type="checklist",
                artifact_instruction="Do something else.",
            ),
        ],
        summary="summary",
    )
    with pytest.raises(EmptyTaskNameError):
        validate_plan(plan)


def test_validate_artifact_rejects_empty_values() -> None:
    """An artifact with an empty value should fail validation."""

    artifact = Artifact(task_id="task_1", artifact_type="checklist", value="   ")
    with pytest.raises(InvalidArtifactError):
        validate_artifact(artifact, "task_1")


def test_validate_artifacts_rejects_unknown_task_ids() -> None:
    """Artifacts that reference unknown task ids should fail validation."""

    artifact = Artifact(task_id="unknown", artifact_type="checklist", value="valid")
    with pytest.raises(InvalidArtifactError):
        validate_artifacts([artifact], ["task_1"])
