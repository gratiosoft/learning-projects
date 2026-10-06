.PHONY: setup test lint fmt package tf-check plan deploy check

setup:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check . && uv run ruff format --check .

package:
	./scripts/package.sh

tf-check:
	terraform -chdir=infra fmt -check -recursive
	terraform -chdir=infra init -backend=false -input=false >/dev/null
	terraform -chdir=infra validate

check: lint test tf-check

# plan/deploy need AWS credentials and infra/terraform.tfvars (gitignored). deploy asks for confirmation.
plan: package
	terraform -chdir=infra init -input=false
	terraform -chdir=infra plan

deploy: package
	terraform -chdir=infra init -input=false
	terraform -chdir=infra apply
