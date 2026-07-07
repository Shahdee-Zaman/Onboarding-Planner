# Prompts

## Planner Prompt Responsibilities

The Planner prompt is responsible for:

- turning one user request into a structured onboarding plan,
- preserving the separation between planning and execution,
- producing task ordering and dependency information,
- avoiding any artifact generation.

### Planner Input

- One natural-language onboarding request.

### Planner Output

- A structured plan object containing the request, tasks, summary, and assumptions.

### Example Planner Output

```json
{
  "request": "Onboard a new warehouse operations manager for Chicago.",
  "summary": "Create access, complete safety orientation, and schedule first-week training.",
  "assumptions": ["The manager already has a corporate email account."],
  "tasks": [
    {
      "id": "task_1",
      "name": "Provision access",
      "description": "Create systems access and verify permissions.",
      "dependency_ids": [],
      "task_type": "auto",
      "artifact_type": "checklist",
      "artifact_instruction": "Describe the access provisioning checklist."
    }
  ]
}
```

## Executor Prompt Responsibilities

The Executor prompt is responsible for:

- consuming exactly one task,
- producing exactly one artifact,
- following the task instructions without creating a plan,
- keeping output constrained to a single artifact schema.

### Executor Input

- The original request.
- One task from the plan.

### Executor Output

- One artifact object tied to the task id.

### Example Executor Output

```json
{
  "task_id": "task_1",
  "artifact_type": "checklist",
  "value": "1. Create warehouse system access\n2. Verify permissions\n3. Confirm completion with the onboarding lead",
  "metadata": {
    "format": "markdown"
  }
}
```

## Why the Prompts Are Separated

Prompt separation enforces separation of concerns:

- the Planner prompt optimizes for decomposition and sequencing,
- the Executor prompt optimizes for task-level generation,
- each agent receives only the context it needs,
- the workflow can validate and test each phase independently.

This reduces accidental prompt leakage, improves testability, and keeps the architecture stable when prompts are tuned.

