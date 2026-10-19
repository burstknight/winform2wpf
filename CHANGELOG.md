# Change Log

## [Unreleased]
### [Added]

- Bilingual maintenance guide (`docs/CONTRIBUTING_EN.md`, `docs/CONTRIBUTING_ZH-TW.md`)
- Initial wf2wpf tool skeleton with `src/wf2wpf/` modules (`parser`, `analyzer`, `mapper`, `renderer`, `report`, `resources`, `cli`)
- CLI entry point `wf2wpf convert` with `--report` support
- Layout inference prioritizing `WrapPanel`/`DockPanel`/`StackPanel`/`Grid` (`Canvas` as last resort)
- Bilingual documentation (EN/ZH-TW): README, Architecture, Development Plan, Test Strategy
- Synthetic test fixtures and golden XAML files with unit and integration tests
- Packaging via `pyproject.toml` with hatchling build backend (uv + pytest support, future `uvx` compatibility)
- Source file encoding detection (BOM → strict UTF-8 → Big5 → CP950) in `wf2wpf.io`, with a unified `TextFileReader`; `parse_designer_cs` now auto-detects non-UTF-8 (e.g. Big5/CP950) `Designer.cs` files so Chinese literals are no longer corrupted
- `convert` encoding options: `--src-encoding`, `--encoding-fallbacks`, `--encoding-map` (glob overrides), and `--encoding-report`

### [Changed]

- Rendered XAML is now pretty-printed with tab indentation instead of a single line; golden files in `tests/expected/` reformatted the same way (content unchanged)
- `.editorconfig` now enforces tab indentation for `*.xaml`

### [Fixed]

### [Security]

### [Removed]

### [Deprecated]

