"""Data models for the warehouse onboarding assistant.

The models intentionally stay small and explicit so the planner and executor
can exchange structured outputs without leaking implementation details into the
workflow layer.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskType(StrEnum):
    """The type of work a task represents."""

    AUTO = "auto"
    HUMAN = "human"


class Task(BaseModel):
    """A single onboarding task produced by the planner."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique task identifier.")
    name: str = Field(..., description="Human-readable task title.")
    description: str = Field(
        default="",
        description="Additional task context for the executor.",
    )
    dependency_ids: list[str] = Field(
        default_factory=list,
        description="Identifiers of tasks that must complete first.",
    )
    task_type: TaskType = Field(
        default=TaskType.AUTO,
        description="Whether the task is handled automatically or by a human.",
    )
    artifact_type: str = Field(
        default="text",
        description="Type of artifact the executor must generate.",
    )
    artifact_instruction: str = Field(
        default="",
        description="Task-specific instructions for the executor.",
    )

    @field_validator(
        "id",
        "name",
        "artifact_type",
        "artifact_instruction",
        mode="before",
    )
    @classmethod
    def _strip_required_strings(cls, value: str) -> str:
        """Normalize task strings before validation."""

        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("dependency_ids", mode="before")
    @classmethod
    def _normalize_dependency_ids(cls, value: list[str]) -> list[str]:
        """Normalize dependency identifiers before validation."""

        if not value:
            return []
        return [
            item.strip()
            for item in value
            if isinstance(item, str) and item.strip()
        ]


class OnboardingPlan(BaseModel):
    """Structured output produced by the planner."""

    model_config = ConfigDict(extra="forbid")

    request: str = Field(..., description="The original user request.")
    tasks: list[Task] = Field(
        default_factory=list,
        description="Ordered tasks that the executor must process one by one.",
    )
    summary: str = Field(
        default="",
        description="Short natural-language summary of the plan.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made while turning the request into tasks.",
    )

    @field_validator("request", "summary", mode="before")
    @classmethod
    def _strip_plan_strings(cls, value: str) -> str:
        """Normalize plan strings before validation."""

        if isinstance(value, str):
            return value.strip()
        return value


class Artifact(BaseModel):
    """Structured output produced by the executor for a single task."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(
        ..., description="Identifier of the task that created the artifact."
    )
    artifact_type: str = Field(..., description="Artifact category or format.")
    value: str = Field(..., description="The generated artifact payload.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata attached to the artifact.",
    )

    @field_validator("task_id", "artifact_type", "value", mode="before")
    @classmethod
    def _strip_artifact_strings(cls, value: str) -> str:
        """Normalize artifact strings before validation."""

        if isinstance(value, str):
            return value.strip()
        return value


class ExecutionMetrics(BaseModel):
    """Timing and throughput metrics collected during workflow execution."""

    model_config = ConfigDict(extra="forbid")

    planning_time_seconds: float = Field(default=0.0, ge=0.0)
    execution_time_seconds: float = Field(default=0.0, ge=0.0)
    total_runtime_seconds: float = Field(default=0.0, ge=0.0)
    number_of_tasks: int = Field(default=0, ge=0)
    auto_tasks: int = Field(default=0, ge=0)
    human_tasks: int = Field(default=0, ge=0)


class WorkflowResult(BaseModel):
    """Complete result produced by a successful workflow run."""

    model_config = ConfigDict(extra="forbid")

    request: str = Field(..., description="Original user request.")
    plan: OnboardingPlan = Field(..., description="Structured onboarding plan.")
    artifacts: list[Artifact] = Field(
        default_factory=list,
        description="Artifacts produced by the executor.",
    )
    metrics: ExecutionMetrics = Field(..., description="Timing and task metrics.")
