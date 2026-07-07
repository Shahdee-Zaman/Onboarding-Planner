"""Planner agent implementation.

The planner accepts one natural-language onboarding request and returns a
structured onboarding plan without generating artifacts.
"""

from __future__ import annotations

from typing import Any

from ..exceptions import PlannerError
from ..llm_factory import create_llm_client
from ..logging_config import get_logger
from ..models import OnboardingPlan
from ..prompts import build_planner_prompt

logger = get_logger(__name__)


class PlannerAgent:
    """Create structured onboarding plans from natural-language requests."""

    def __init__(
        self,
        llm: Any | None = None,
        provider: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize the planner.

        Args:
            llm: Optional LangChain-compatible LLM instance for testing or production.
            provider: Optional LLM provider override such as ``ollama`` or ``gemini``.
            model_name: Optional model name override for the selected provider.
            temperature: Optional sampling temperature override.

        Raises:
            PlannerError: If the default LLM cannot be created.
        """

        if llm is None:
            try:
                llm = create_llm_client(
                    provider=provider,
                    model_name=model_name,
                    temperature=temperature,
                )
            except Exception as exc:  # pragma: no cover - dependency-specific path
                logger.error("planner initialization failed", exc_info=True)
                raise PlannerError("Planner LLM initialization failed.") from exc
        self._llm = llm

    def plan(self, user_request: str) -> OnboardingPlan:
        """Generate a structured onboarding plan.

        Args:
            user_request: The original onboarding request from the user.

        Returns:
            A validated onboarding plan.

        Raises:
            PlannerError: If structured output generation fails.
        """

        logger.info("planner start")
        try:
            structured_llm = self._llm.with_structured_output(OnboardingPlan)
            plan = structured_llm.invoke(build_planner_prompt(user_request))
            if not isinstance(plan, OnboardingPlan):
                plan = OnboardingPlan.model_validate(plan)
        except Exception as exc:
            logger.error("planner failure", exc_info=True)
            raise PlannerError("Planner failed to generate a plan.") from exc
        logger.info("planner finish")
        return plan
