# Learning Projects: Repo Instructions

Overview and project list: [README.md](README.md). Ideas and roadmaps: [project-ideas.md](project-ideas.md).

## Roadmaps

- Every project under `## Project Ideas Overview` in `project-ideas.md` must have its own expanded roadmap section further down, following Projects 1 and 2 (phases, numbered steps, **Learning Outcomes**).
- When adding a project to the overview, add its roadmap in the same change.

## Starting a project

1. Create the branch first: `feat/<project-slug>` (semantic prefixes: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`).
2. Create the project folder at the repo root: `<project-slug>/`. Folders are created only when the project is started, never beforehand.
3. Create inside it:
   - `README.md`: purpose, setup, run, test, deploy, link to docs.
   - `CLAUDE.md`: project-specific instructions (stack, commands, conventions, env vars, gotchas). Must not contradict this file.
   - `docs/prd.md`: PRD (problem, goals, non-goals, users, requirements, success metrics).
   - `docs/architecture.md`: architecture spec with diagrams in **Mermaid or D2** (system context, components, data flow, deployment).
   - `docs/adr/NNNN-<decision>.md`: one ADR per significant decision (context, decision, consequences, status). Number sequentially.
   - `infra/`: IaC for every AWS resource.
   - `tests/`: tests for all code.
4. Update the status table in the root `README.md`.

Write the PRD, architecture and first ADRs before implementation code.

## Rules

- **One branch per project.** Never develop a project on `main`; merge via PR.
- **Conventional Commits**: `type(scope): subject` (`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `build`). Scope is the project slug. Imperative, lowercase subject.
- **AWS = IaC only**: AWS CDK or Terraform. No manual console resources; no hardcoded credentials or secrets (use env vars / SSM / Secrets Manager; keep `.env` gitignored).
- **Tests are mandatory** for every project, including Lambda handlers and API client code. Mock external services (Airtable, Spotify, AWS).
- **Diagrams** are text-based (Mermaid or D2), versioned alongside docs.
- **Tooling**: Node.js → Vite (+ npm/pnpm, Vitest for tests). Python → uv (`uv init`, `uv add`, `uv run pytest`).
- **Airtable**: select fields must be created with a distinct color per option (the API cannot recolor them later).
- Keep docs concise; update PRD/architecture/ADRs when behavior changes.

## Definition of done (per project)

- [ ] Roadmap phases complete
- [ ] PRD, architecture spec (with diagrams), and ADRs present and current
- [ ] IaC deploys cleanly
- [ ] Tests pass
- [ ] Project README and CLAUDE.md accurate
- [ ] Root README status updated
