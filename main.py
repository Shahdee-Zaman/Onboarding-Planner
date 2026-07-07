"""Command-line entry point for the warehouse onboarding assistant."""

from __future__ import annotations

import argparse

from warehouse_assistant.agents import ExecutorAgent, PlannerAgent
from warehouse_assistant.logging_config import configure_logging
from warehouse_assistant.workflow import WarehouseOnboardingWorkflow


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run the warehouse onboarding assistant."
    )
    parser.add_argument(
        "--provider",
        help="Optional LLM provider override, for example 'ollama' or 'gemini'.",
    )
    parser.add_argument(
        "--model",
        help="Optional model name override for the selected provider.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Optional model temperature override.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the onboarding workflow from the command line."""

    args = parse_args()
    configure_logging()
    
    print("Warehouse Onboarding Assistant initialized.")
    request = input("\nHow can I help you today? ")
    
    if not request.strip():
        print("No request provided. Exiting.")
        return

    print(f"\nProcessing request: '{request}'...")

    planner = PlannerAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    executor = ExecutorAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    result = WarehouseOnboardingWorkflow(
        planner=planner,
        executor=executor,
    ).run(request)
    
    print("\n" + "="*50)
    print("     PLANNER AGENT SUMMARY")
    print("="*50)
    print(f"Summary: {result.plan.summary}\n")
    if result.plan.assumptions:
        print("Assumptions:")
        for a in result.plan.assumptions:
            print(f" - {a}")
        print()
    print("Tasks Scheduled:")
    for i, task in enumerate(result.plan.tasks, 1):
        print(f" {i}. [{task.task_type.upper()}] {task.name}")
        print(f"    {task.description}")

    print("\n" + "="*50)
    print("     EXECUTOR AGENT RESULTS")
    print("="*50)
    for artifact in result.artifacts:
        print(f"\nTask ID: {artifact.task_id} | Type: {artifact.artifact_type}")
        print("-" * 30)
        print(artifact.value)
        print("-" * 30)

    print("\n" + "="*50)
    print("     EXECUTION METRICS")
    print("="*50)
    print(f"Tasks Completed: {result.metrics.number_of_tasks} ({result.metrics.auto_tasks} auto, {result.metrics.human_tasks} human)")
    print(f"Planning Time:   {result.metrics.planning_time_seconds:.2f}s")
    print(f"Execution Time:  {result.metrics.execution_time_seconds:.2f}s")
    print(f"Total Time:      {result.metrics.total_runtime_seconds:.2f}s")


if __name__ == "__main__":
    main()

