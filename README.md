# Warehouse Onboarding Assistant

## Overview

This project implements a LangChain-based warehouse onboarding assistant with a strict two-agent architecture:

- Planner Agent: turns one natural-language request into a structured onboarding plan.
- Executor Agent: takes one task at a time and produces exactly one artifact.

The business flow is intentionally simple and stable:

1. The planner runs once.
2. The executor runs once per task.
3. The workflow validates the plan, executes tasks, collects artifacts, and reports metrics.

Model/provider selection is centralized in `warehouse_assistant/config.py`, so swapping from Ollama to Gemini or an OpenAI-compatible API only requires config changes.

## Architecture

The architecture is preserved as a separation of concerns:

- The Planner is responsible only for planning.
- The Executor is responsible only for artifact generation.
- The Workflow coordinates both agents and handles validation, logging, metrics, and error handling.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

Or, using the requirements file:

```bash
pip install -r requirements.txt
```

## Configuration

The runtime can be adjusted in `warehouse_assistant/config.py` or through `.env`:

- `WAREHOUSE_LLM_PROVIDER` controls the provider: `ollama`, `gemini`, or `openai`.
- `WAREHOUSE_MODEL_NAME` sets the model name for the selected provider.
- `WAREHOUSE_API_KEY_ENV_VAR` names the environment variable that stores the API key.
- `WAREHOUSE_API_BASE_URL` sets an optional local or OpenAI-compatible base URL.
- `WAREHOUSE_TEMPERATURE` sets the sampling temperature.
- `WAREHOUSE_LOG_LEVEL` sets the logging level.

Example `.env` values for Gemini:

```env
WAREHOUSE_LLM_PROVIDER=gemini
WAREHOUSE_MODEL_NAME=gemini-1.5-flash
WAREHOUSE_API_KEY_ENV_VAR=GOOGLE_API_KEY
GOOGLE_API_KEY=your-key-here
```

Example `.env` values for OpenAI:

```env
WAREHOUSE_LLM_PROVIDER=openai
WAREHOUSE_MODEL_NAME=gpt-4o-mini
WAREHOUSE_API_KEY_ENV_VAR=OPENAI_API_KEY
WAREHOUSE_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your-key-here
```

## Usage

Run the program with `main.py`:

```bash
python main.py "Onboard a new warehouse supervisor for the Dallas site."
```

You can also override the provider or model at runtime:

```bash
python main.py "Onboard a new warehouse supervisor." --provider gemini --model gemini-1.5-flash
```

Or import the workflow from Python:

```python
from warehouse_assistant import run_workflow

result = run_workflow("Onboard a new warehouse supervisor for the Dallas site.")
print(result.artifacts)
print(result.metrics.model_dump())
```

## Project Structure

```text
main.py
warehouse_assistant/
  __init__.py
  config.py
  exceptions.py
  llm_factory.py
  logging_config.py
  metrics.py
  models.py
  agents/
    __init__.py
    executor.py
    planner.py
  prompts/
    __init__.py
    prompts.py
  utils/
    __init__.py
    validator.py
  workflow.py
docs/
  architecture.md
  prompts.md
  workflow.md
tests/
  conftest.py
  test_executor.py
  test_llm_factory.py
  test_models.py
  test_planner.py
  test_validator.py
  test_workflow.py
```

## Technologies Used

- Python 3.11
- LangChain
- ChatOllama
- ChatGoogleGenerativeAI
- ChatOpenAI
- python-dotenv
- Pydantic
- pytest
- logging

## Sample Request

```text
Onboard a new warehouse operations manager for the Chicago facility.
Include training, access provisioning, safety orientation, and first-week tasks.
```

## Sample Output

```json
{
  "artifacts": [
    {
      "task_id": "task_1",
      "artifact_type": "checklist",
      "value": "Provision system access and complete safety orientation..."
    }
  ],
  "metrics": {
    "planning_time_seconds": 0.42,
    "execution_time_seconds": 1.31,
    "total_runtime_seconds": 1.73,
    "number_of_tasks": 3,
    "auto_tasks": 2,
    "human_tasks": 1
  }
}
```

## Future Improvements

- Add persistence for plans and artifacts.
- Add retries and backoff for model calls.
- Add richer artifact schema support.
- Add tracing integration for end-to-end observability.
