## Why

Currently, human tasks (`TaskType.HUMAN`) immediately generate a placeholder artifact and the onboarding workflow continues without waiting. This can lead to dependent automatic tasks executing early before the necessary human task has actually been completed in the real world (e.g., creating a physical keycard).

## What Changes

- Pause workflow execution when a human task is reached.
- Prompt the CLI supervisor: "Task requires supervisor action: <task name>. Press Enter when completed to continue."
- Resume execution only after the supervisor confirms completion, ensuring that dependent tasks do not execute early.

## Capabilities

### New Capabilities
- `interactive-hitl`: Enable pausing the workflow and prompting for confirmation/input when executing a human-in-the-loop (HITL) task.

### Modified Capabilities

## Impact

- `warehouse_assistant/workflow.py`: Modify how tasks are executed to detect human tasks and pause/prompt the supervisor.
- `warehouse_assistant/agents/executor.py`: Update the executor agent behavior for human tasks to either prompt/wait or cooperate with the workflow pause/prompt mechanism.
