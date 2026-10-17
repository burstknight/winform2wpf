# Maintenance Guide (EN)

## Overview

This document records the maintenance workflow and rules for this repository. Everyone (including AI agents) working on this project must follow them. The Traditional Chinese version is [CONTRIBUTING_ZH-TW.md](CONTRIBUTING_ZH-TW.md).

## Development Environment

- Manage the environment with `uv` (see `pyproject.toml` and `uv.lock`)
- Sync: `uv sync --dev`
- Test: `uv run pytest`
- Run CLI: `uv run wf2wpf --help`

## Git Rules

### Commit, but never push

- Creating commits when modifying the project is allowed
- Never run `git push`; pushing is reserved for the maintainer

### Split large changes into multiple commits

- If a change is large, split it into multiple logical commits
- Each commit must stand on its own: consistent codebase, passing tests

### Commit messages must explain what and why

- Subject line: conventional prefix (`feat:`, `fix:`, `docs:`, `doc:`, `test:`, `chore:`) followed by a capitalized description (match existing history)
- Body: state what was actually changed and why the change was needed
- Example:

  ```
  fix: Capture form-level Name/Text in parser

  The parser previously ignored properties assigned on the form itself,
  so the generated XAML lost the window title and root name.
  ```

## Verification Before Each Commit

1. `uv sync --dev`
2. `uv run pytest` — all tests must pass before committing

## CHANGELOG Discipline

- Any code change (bug fix, new feature, behavior change) must update `CHANGELOG.md` under `## [Unreleased]`, using the matching category:
  - `[Added]` — new features
  - `[Changed]` — changes to existing behavior
  - `[Fixed]` — bug fixes
  - `[Security]`, `[Removed]`, `[Deprecated]` — as appropriate
- Notable documentation additions may also be recorded

## TODO.md

- If a change reveals follow-up work (known gaps, future improvements, pending refactors), add an item to `TODO.md` so it is not lost

## Documentation Policy

- User-facing documentation must be provided in English and Traditional Chinese as a pair:
  - `docs/*_EN.md` + `docs/*_ZH-TW.md`
  - `README_EN.md` + `README_ZH-TW.md`
- Keep both language versions in sync when updating documentation
- Code comments and docstrings may be written in English (Google-style docstrings)
