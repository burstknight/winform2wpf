# AGENTS.md

## Repo status

- Greenfield: only scaffold files exist (`README.md`, `TODO.md`, `CHANGELOG.md`, `LICENSE`, `.editorconfig`, `.gitattributes`, `.gitignore`). No source code, project/solution files, CI, or build/test/lint tooling yet.
- Do not invent build/test commands. When tooling is added, record the verified commands here.
- Stack is not fixed by config: `.gitattributes` enumerates .NET file types (`*.cs`, `*.xaml`, `*.sln`, `*.csproj`, `*.nuspec`, `*.vdproj`), but the `[*.py]`/JS rules in `.editorconfig` and the Python/Node sections in `.gitignore` are stock upstream template boilerplate — do not treat them as a language decision.

## Maintenance rules

Full guide: `docs/CONTRIBUTING_EN.md` / `docs/CONTRIBUTING_ZH-TW.md`. Non-negotiable rules:

- Commit, but never push: creating commits is allowed; `git push` is reserved for the maintainer.
- Split large changes into multiple logical commits; each commit must be self-contained and pass tests.
- Commit message body must state what was changed and why; subject uses conventional prefixes (see Verified conventions).
- Code changes (fixes, features, behavior changes) must update `CHANGELOG.md` under `[Unreleased]`.
- Record discovered follow-up work in `TODO.md` when relevant.
- User-facing docs are bilingual pairs (`docs/*_EN.md` + `*_ZH-TW.md`, `README_EN.md` + `README_ZH-TW.md`); keep both languages in sync. Code comments and docstrings may be English.
- Verified tooling: `uv sync --dev`, `uv run pytest`. All tests must pass before each commit.

## Verified conventions

- Line endings: `.gitattributes` forces `eol=lf` for all files. Keep LF; write UTF-8 files with a final newline (`.editorconfig`, `root = true`).
- Commits: conventional prefixes, capitalized subject after the colon. Match history exactly, e.g. `chore: Add \`.editorconfig\``, `doc: Add \`TODO.md\``.
- `CHANGELOG.md` is a Keep a Changelog template: `## [Unreleased]` with `### [Added]` / `[Changed]` / `[Fixed]` / `[Security]` / `[Removed]` / `[Deprecated]`. Record notable changes under `[Unreleased]`.
- `README.md` and `TODO.md` are placeholders (title only); expand rather than replace their structure.
