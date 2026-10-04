# Learning Projects

Hands-on projects for learning Airtable (Free plan), AWS Lambda/S3, and third-party APIs (e.g. Spotify). Full ideas and roadmaps: [project-ideas.md](project-ideas.md).

## Projects

| # | Project | Status | Folder |
|---|---------|--------|--------|
| 1 | Game Collection Tracker | Not started | — |
| 2 | Music Playlist Curator | Not started | — |
| 3 | Personal Fitness Log | Not started | — |
| 4 | Mini Movie Review Site | Not started | — |
| 5 | Digital Art Portfolio | Not started | — |

Each project's folder is created only when the project is started.

## Repository rules

- **Roadmaps**: every project listed under `## Project Ideas Overview` in [project-ideas.md](project-ideas.md) must have a detailed roadmap further down, following the format of Projects 1 and 2 (phases, numbered steps, learning outcomes).
- **Per-project docs**: each project folder has its own `README.md` and `CLAUDE.md`.
- **Required documents** per project:
  - **PRD** (Product Requirements Document)
  - **Architecture specification** with diagrams in [Mermaid](https://mermaid.js.org/) or [D2](https://d2lang.com/)
  - **ADR** (Architecture Decision Records)
  - **Tests**
- **Infrastructure as Code**: all AWS resources are defined with AWS CDK or Terraform. No manual console-only infrastructure.
- **Branching**: one branch per project, with semantic names (e.g. `feat/game-collection-tracker`, `fix/...`, `docs/...`).
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat(game-tracker): add S3 upload lambda`).
- **Tooling**: Node.js projects use [Vite](https://vite.dev/); Python projects use [uv](https://docs.astral.sh/uv/).

## Project folder layout

```
<project-name>/
├── README.md
├── CLAUDE.md
├── docs/
│   ├── prd.md
│   ├── architecture.md      # Mermaid or D2 diagrams
│   └── adr/
│       └── 0001-<decision>.md
├── infra/                   # AWS CDK or Terraform
├── src/
└── tests/
```
