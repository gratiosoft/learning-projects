# 0001. Python 3.12 with uv and ruff

Status: accepted

## Context
The Lambda, the Airtable client and the CLIs are all glue code around HTTP APIs. The repo rules require `uv` for Python projects.

## Decision
Python 3.12, managed with `uv` (`uv add`, `uv run pytest`). Lint and format with `ruff`. HTTP via `requests` (not in the Lambda runtime, so it is bundled into the zip). Tests with `pytest`, `responses` (HTTP mocks) and `moto` (AWS mocks).

## Consequences
- One toolchain, no Node needed (see 0002).
- Lambda packaging needs a build step that installs dependencies into a folder (`make package`).
- `boto3` is provided by the Lambda runtime, so it is a dev-only dependency for the Lambda but a runtime dependency for the CLI.
