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

- Parser now supports modern .NET designer files that omit the `this.` qualifier (control/form property assignments and `Controls.Add`); previously such files silently produced an empty `<Window />` with zero children
- Parser now recognizes the three-argument `Controls.Add(child, column, row)` overload and records the cell position (`Control.column`/`row`) plus `ColumnCount`/`RowCount`; TableLayoutPanel children were previously orphaned and dropped from the rendered XAML (the `05_tablelayout` case recorded in `TODO.md`)
- Renderer keeps a container control's `Text` (e.g. GroupBox station headers) as the WPF `Header` instead of dropping it, and emits `Header` rather than the invalid `Content` on GroupBox elements; elements with no WPF text property (panels, layout containers) no longer receive a stray `Content` attribute
- Renderer no longer nests a duplicate inner panel when the container element already maps to the inferred panel type (`TableLayoutPanel` -> `Grid`, `FlowLayoutPanel` -> `WrapPanel`, `Panel` -> `StackPanel`), which had emitted `Grid` inside `Grid` and the extra `WrapPanel` recorded in `TODO.md`
- Renderer emits `RowDefinitions`/`ColumnDefinitions` and the `Grid.Row`/`Grid.Column` attached properties for `TableLayoutPanel` grids (percent styles map to equal star sizes); previously all cells collapsed into a single overlapping cell
- Analyzer now separates vertical linear chains from layouts scattered on both axes: scattered containers infer a `Grid` (the priority its docstring already promised) instead of a vertical `StackPanel` that reflowed absolute layouts
- Absolute layout fidelity: children of layout `Grid`s keep their WinForms `Location`/`Size` as `HorizontalAlignment`/`VerticalAlignment` + `Margin` + `Width`/`Height`, and the form `ClientSize` becomes the WPF `Window` `Width`/`Height`; parsed `Location`/`Size` data was previously discarded by the renderer

### [Security]

### [Removed]

### [Deprecated]

