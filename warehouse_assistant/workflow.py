"""Workflow orchestration for the warehouse onboarding assistant.

This module wires the Planner and Executor together, validates the planner
output, records runtime metrics, and converts internal failures into consistent
application exceptions.
"""

from __future__ import annotations

from time import perf_counter
from typing import Sequence

from .agents.executor import ExecutorAgent
from .agents.planner import PlannerAgent
from .exceptions import ExecutorError, PlannerError, WorkflowError
from .logging_config import get_logger
from .models import (
    Artifact,
    ExecutionMetrics,
    OnboardingPlan,
    Task,
    TaskType,
    WorkflowResult,
)
from .utils.validator import validate_artifact, validate_artifacts, validate_plan

logger = get_logger(__name__)


class WarehouseOnboardingWorkflow:
    """Coordinate the planner and executor while preserving their separation."""

    def __init__(
        self,
        planner: PlannerAgent | None = None,
        executor: ExecutorAgent | None = None,
    ) -> None:
        """Initialize the workflow with optional test doubles.

        Args:
            planner: Planner instance. A default planner is created when omitted.
            executor: Executor instance. A default executor is created when omitted.
        """
        try:
            self._planner = planner or PlannerAgent()
            self._executor = executor or ExecutorAgent()
        except (PlannerError, ExecutorError) as exc:
            raise WorkflowError("Workflow agent initialization failed.") from exc

    def run(self, user_request: str) -> WorkflowResult:
        """Run the planner once and the executor once per task.

        Args:
            user_request: Natural-language onboarding request.

        Returns:
            A full workflow result containing the plan, artifacts, and metrics.

        Raises:
            WorkflowError: If planning, validation, or execution fails.
        """

        total_start = perf_counter()
        try:
            plan_start = perf_counter()
            plan = self._planner.plan(user_request)
            planning_time = perf_counter() - plan_start

            validate_plan(plan)

            execution_start = perf_counter()
            artifacts = self._execute_tasks(user_request, plan.tasks)
            execution_time = perf_counter() - execution_start

            metrics = ExecutionMetrics(
                planning_time_seconds=planning_time,
                execution_time_seconds=execution_time,
                total_runtime_seconds=perf_counter() - total_start,
                number_of_tasks=len(plan.tasks),
                auto_tasks=sum(
                    1 for task in plan.tasks if task.task_type == TaskType.AUTO
                ),
                human_tasks=sum(
                    1 for task in plan.tasks if task.task_type == TaskType.HUMAN
                ),
            )
            validate_artifacts(artifacts, [task.id for task in plan.tasks])
            logger.info("workflow completion")
            return WorkflowResult(
                request=user_request,
                plan=plan,
                artifacts=artifacts,
                metrics=metrics,
            )
        except (PlannerError, ExecutorError) as exc:
            logger.error("workflow failure", exc_info=True)
            raise WorkflowError(
                "Workflow failed while running the planner or executor."
            ) from exc
        except Exception as exc:
            logger.error("workflow failure", exc_info=True)
            raise WorkflowError(
                "Workflow failed during validation or orchestration."
            ) from exc

    def _execute_tasks(
        self,
        user_request: str,
        tasks: Sequence[Task],
    ) -> list[Artifact]:
        """Execute each validated task sequentially.

        Args:
            user_request: The original user request.
            tasks: Ordered task list produced by the planner.

        Returns:
            A list of artifacts in the same order as the tasks.
        """

        artifacts: list[Artifact] = []
        for task in tasks:
            artifact = self._executor.execute(task, user_request)
            validate_artifact(artifact, task.id)
            artifacts.append(artifact)
        return artifacts


def run_workflow(
    user_request: str,
    planner: PlannerAgent | None = None,
    executor: ExecutorAgent | None = None,
) -> WorkflowResult:
    """Convenience wrapper for running the full workflow.

    Args:
        user_request: Natural-language onboarding request.
        planner: Optional planner dependency injection point.
        executor: Optional executor dependency injection point.

    Returns:
        A successful workflow result.
    """

    workflow = WarehouseOnboardingWorkflow(
        planner=planner,
        executor=executor,
    )
    return workflow.run(user_request)
