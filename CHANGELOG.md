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

### [Changed]

### [Fixed]

### [Security]

### [Removed]

### [Deprecated]

