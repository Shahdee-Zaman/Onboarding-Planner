## ADDED Requirements

### Requirement: Pause and Prompt on Human Tasks
The system SHALL detect tasks of type `TaskType.HUMAN` during workflow execution and pause execution. Upon pausing, the system SHALL output a prompt to the console indicating that a supervisor action is required, utilizing the format: "Task requires supervisor action: <task name>. Press Enter when completed to continue."

#### Scenario: Workflow pauses on human task
- **WHEN** the workflow processes a task with `TaskType.HUMAN` and the task name is "Create physical keycard"
- **THEN** the workflow pauses and prompts the supervisor with: "Task requires supervisor action: Create physical keycard. Press Enter when completed to continue."

### Requirement: Resume Execution After Confirmation
The system SHALL resume workflow execution only after receiving supervisor confirmation via the Enter key. Once confirmed, the system SHALL generate the artifact for the human task and proceed to subsequent tasks in the plan.

#### Scenario: Workflow resumes after supervisor confirmation
- **WHEN** the workflow is paused on a human task prompt
- **AND** the supervisor presses the Enter key
- **THEN** the workflow resumes, creates the manual artifact, and executes the remaining tasks in sequence
