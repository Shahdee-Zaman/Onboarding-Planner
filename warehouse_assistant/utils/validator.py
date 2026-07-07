"""Validation helpers for onboarding plans and generated artifacts."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Sequence

from ..exceptions import (
    CyclicDependencyError,
    DuplicateTaskIdError,
    EmptyTaskNameError,
    InvalidArtifactError,
    MissingDependencyError,
)
from ..models import Artifact, OnboardingPlan, Task


def validate_plan(plan: OnboardingPlan) -> None:
    """Validate structural integrity of an onboarding plan.

    Args:
        plan: Structured onboarding plan produced by the planner.

    Raises:
        DuplicateTaskIdError: If two tasks share the same identifier.
        MissingDependencyError: If a task references an unknown dependency.
        CyclicDependencyError: If dependency links create a cycle.
        EmptyTaskNameError: If any task name is blank.
    """

    task_ids = [task.id for task in plan.tasks]
    _validate_duplicate_task_ids(task_ids)
    _validate_task_names(plan.tasks)
    _validate_dependency_ids(plan.tasks)
    _validate_cyclic_dependencies(plan.tasks)


def validate_artifact(artifact: Artifact, task_id: str) -> None:
    """Validate a single executor artifact.

    Args:
        artifact: Artifact created by the executor.
        task_id: Expected task identifier for the artifact.

    Raises:
        InvalidArtifactError: If the artifact is malformed or empty.
    """

    if artifact.task_id != task_id:
        raise InvalidArtifactError(
            "Artifact task id "
            f"'{artifact.task_id}' does not match expected task id '{task_id}'."
        )
    if not artifact.value.strip():
        raise InvalidArtifactError(
            f"Artifact for task '{task_id}' has an empty value."
        )
    if not artifact.artifact_type.strip():
        raise InvalidArtifactError(
            f"Artifact for task '{task_id}' has an empty artifact type."
        )


def validate_artifacts(artifacts: Sequence[Artifact], task_ids: Sequence[str]) -> None:
    """Validate a collection of artifacts against known task ids.

    Args:
        artifacts: Artifacts created by executor runs.
        task_ids: Task identifiers that are expected to appear in the artifacts.

    Raises:
        InvalidArtifactError: If any artifact is malformed.
    """

    known_task_ids = set(task_ids)
    for artifact in artifacts:
        if artifact.task_id not in known_task_ids:
            raise InvalidArtifactError(
                f"Artifact references unknown task id '{artifact.task_id}'."
            )
        validate_artifact(artifact, artifact.task_id)


def _validate_duplicate_task_ids(task_ids: Iterable[str]) -> None:
    """Raise when duplicate task identifiers are detected."""

    seen: set[str] = set()
    for task_id in task_ids:
        if task_id in seen:
            raise DuplicateTaskIdError(
                f"Duplicate task id detected: '{task_id}'."
            )
        seen.add(task_id)


def _validate_task_names(tasks: Sequence[Task]) -> None:
    """Raise when any task name is blank."""

    for task in tasks:
        if not task.name.strip():
            raise EmptyTaskNameError(f"Task '{task.id}' has an empty name.")


def _validate_dependency_ids(tasks: Sequence[Task]) -> None:
    """Raise when a dependency references a missing task."""

    known_ids = {task.id for task in tasks}
    for task in tasks:
        for dependency_id in task.dependency_ids:
            if dependency_id not in known_ids:
                raise MissingDependencyError(
                    f"Task '{task.id}' depends on missing task id '{dependency_id}'."
                )


def _validate_cyclic_dependencies(tasks: Sequence[Task]) -> None:
    """Raise when dependency links create a cycle."""

    graph: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        graph[task.id] = list(task.dependency_ids)

    visited: set[str] = set()
    active_path: set[str] = set()

    def visit(task_id: str) -> None:
        """Depth-first traversal with cycle detection."""

        if task_id in active_path:
            raise CyclicDependencyError(
                f"Cyclic dependency detected involving task id '{task_id}'."
            )
        if task_id in visited:
            return
        active_path.add(task_id)
        for dependency_id in graph[task_id]:
            visit(dependency_id)
        active_path.remove(task_id)
        visited.add(task_id)

    for task in tasks:
        visit(task.id)
