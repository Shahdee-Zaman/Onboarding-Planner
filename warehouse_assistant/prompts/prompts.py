"""Prompt templates for the Planner and Executor agents.

Keeping prompt construction in one package makes the system easier to document,
test, and tune without changing the orchestration code.
"""

from __future__ import annotations

from ..models import Task


def build_planner_prompt(user_request: str) -> str:
    """Build the planner prompt for a single onboarding request.

    Args:
        user_request: Natural-language onboarding request from the user.

    Returns:
        A prompt string for structured plan generation.
    """

    return (
        "You are the Planner Agent for a warehouse onboarding assistant.\n"
        "Your job is to create a structured onboarding plan from one user request.\n"
        "Do not create artifacts. Do not execute tasks. Do not re-plan.\n"
        "Return only a plan that matches the expected structured schema.\n\n"
        f"User request:\n{user_request.strip()}\n"
    )


def build_executor_prompt(user_request: str, task: Task) -> str:
    """Build the executor prompt for one task.

    Args:
        user_request: The original onboarding request.
        task: The single task to execute.

    Returns:
        A prompt string for one-artifact generation.
    """

    dependency_text = ", ".join(task.dependency_ids) if task.dependency_ids else "none"
    return (
        "You are the Executor Agent for a warehouse onboarding assistant.\n"
        "Your job is to complete exactly one task and produce exactly one artifact.\n"
        "Do not plan. Do not split the task. Do not return multiple artifacts.\n"
        "Return only the artifact that matches the expected structured schema.\n\n"
        f"Original request:\n{user_request.strip()}\n\n"
        f"Task id: {task.id}\n"
        f"Task name: {task.name}\n"
        f"Task description: {task.description}\n"
        f"Task type: {task.task_type}\n"
        f"Artifact type: {task.artifact_type}\n"
        f"Artifact instruction: {task.artifact_instruction}\n"
        f"Dependencies: {dependency_text}\n"
    )

