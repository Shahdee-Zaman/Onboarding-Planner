## Context

Currently, human tasks (`TaskType.HUMAN`) immediately generate a placeholder artifact and the onboarding workflow continues without pausing. This can result in dependent automated tasks executing before the real-world human task actually completes.

## Goals / Non-Goals

**Goals:**
- Detect tasks of type `TaskType.HUMAN` during execution.
- Pause workflow execution and prompt the operator/supervisor on the command line using: `Task requires supervisor action: <task name>. Press Enter when completed to continue.`
- Resume the workflow and generate a completed artifact for the human task after receiving supervisor confirmation.

**Non-Goals:**
- Adding a GUI or web interface for supervisor interaction (CLI `input()` is sufficient).
- Changing how automated tasks (`TaskType.AUTO`) are handled.

## Decisions

### 1. Interception Location
We will handle the pausing and prompting directly within `ExecutorAgent.execute()`. 
- **Option A (Chosen)**: Handle in `ExecutorAgent.execute()`.
  - *Pros*: The executor is already responsible for executing individual tasks and handles special case logic for `TaskType.HUMAN`. Implementing the interactive prompt here keeps the orchestration loop in `workflow.py` clean.
  - *Cons*: The executor is coupled to console `input()`. We can mitigate this in testing by mocking `builtins.input`.
- **Option B**: Handle in `WarehouseOnboardingWorkflow.run()`.
  - *Pros*: Keeps the executor purely functional without I/O blocking.
  - *Cons*: Splitting `TaskType` logic makes it harder to maintain and duplicates `TaskType.HUMAN` artifact generation logic.

## Risks / Trade-offs

- **Risk**: Automatic tests will block or fail when `input()` is called.
  - *Mitigation*: We will mock `builtins.input` in the pytest environment to simulate instant supervisor confirmation.
- **Risk**: Output formatting issues depending on terminal capabilities.
  - *Mitigation*: Use Python's built-in `input()` with the exact requested string to ensure standard interactive behavior.
