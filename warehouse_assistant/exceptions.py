"""Custom exceptions used by the warehouse onboarding assistant."""

from __future__ import annotations


class AssistantError(Exception):
    """Base class for all application-specific exceptions."""


class PlannerError(AssistantError):
    """Raised when the planner cannot create or return a valid plan."""


class ExecutorError(AssistantError):
    """Raised when the executor cannot create or return a valid artifact."""


class WorkflowError(AssistantError):
    """Raised when the workflow orchestration fails."""


class ValidationError(AssistantError):
    """Raised when workflow data fails structural validation."""


class ConfigurationError(AssistantError):
    """Raised when runtime configuration is invalid or unsupported."""


class DuplicateTaskIdError(ValidationError):
    """Raised when a plan contains duplicate task identifiers."""


class MissingDependencyError(ValidationError):
    """Raised when a task dependency references an unknown task identifier."""


class CyclicDependencyError(ValidationError):
    """Raised when task dependencies create a cycle."""


class EmptyTaskNameError(ValidationError):
    """Raised when a task name is blank."""


class InvalidArtifactError(ValidationError):
    """Raised when an artifact has an invalid value or malformed shape."""
