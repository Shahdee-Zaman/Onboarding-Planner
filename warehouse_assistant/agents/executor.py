"""Executor agent implementation.

The executor receives exactly one task at a time and generates one artifact for
that task without performing any planning.
"""

from __future__ import annotations

from typing import Any

from ..exceptions import ExecutorError
from ..llm_factory import create_llm_client
from ..logging_config import get_logger
from ..models import Artifact, Task, TaskType
from ..prompts import build_executor_prompt

logger = get_logger(__name__)


class ExecutorAgent:
    """Generate exactly one artifact for a single planner task."""

    def __init__(
        self,
        llm: Any | None = None,
        provider: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize the executor.

        Args:
            llm: Optional LangChain-compatible LLM instance for testing or production.
            provider: Optional LLM provider override such as ``ollama`` or ``gemini``.
            model_name: Optional model name override for the selected provider.
            temperature: Optional sampling temperature override.

        Raises:
            ExecutorError: If the default LLM cannot be created.
        """

        if llm is None:
            try:
                llm = create_llm_client(
                    provider=provider,
                    model_name=model_name,
                    temperature=temperature,
                )
            except Exception as exc:  # pragma: no cover - dependency-specific path
                logger.error("executor initialization failed", exc_info=True)
                raise ExecutorError("Executor LLM initialization failed.") from exc
        self._llm = llm

    def execute(self, task: Task, user_request: str) -> Artifact:
        """Generate one artifact for a single task.

        Args:
            task: The task to execute.
            user_request: The original user request for context.

        Returns:
            Exactly one artifact for the provided task.

        Raises:
            ExecutorError: If structured output generation fails.
        """

        logger.info("executor start")
        
        if task.task_type == TaskType.HUMAN:
            logger.info("Skipping human task, generating manual artifact.")
            artifact = Artifact(
                task_id=task.id,
                artifact_type="manual_review",
                value="This task is marked as HUMAN. It has been listed for a supervisor to review and complete manually.",
                metadata={"status": "pending_supervisor_review"}
            )
            logger.info("executor finish (human task)")
            return artifact

        try:
            structured_llm = self._llm.with_structured_output(Artifact)
            artifact = structured_llm.invoke(build_executor_prompt(user_request, task))
            if not isinstance(artifact, Artifact):
                artifact = Artifact.model_validate(artifact)
        except Exception as exc:
            logger.error("executor failure", exc_info=True)
            raise ExecutorError("Executor failed to generate an artifact.") from exc
        logger.info("executor finish")
        return artifact
