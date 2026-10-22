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
- Golden-file comparison test: every fixture in `tests/fixtures/` is rendered and compared against `tests/expected/`; the goldens were regenerated to the current output (window dimensions, absolute-layout margins, Grid cell definitions) and a golden was added for `07_modern_style`
- Load-time test that parses the golden XAML with the real WPF parser (`System.Windows.Markup.XamlReader`, run through Windows PowerShell 5.1); the test is skipped when PowerShell or the WPF assemblies are unavailable

### [Changed]

- Rendered XAML is now pretty-printed with tab indentation instead of a single line; golden files in `tests/expected/` reformatted the same way (content unchanged)
- `.editorconfig` now enforces tab indentation for `*.xaml`
- XAML files written by `render_xaml`/the CLI now end with a final newline, as required by `.editorconfig` (`insert_final_newline`)

### [Fixed]

- Parser now supports modern .NET designer files that omit the `this.` qualifier (control/form property assignments and `Controls.Add`); previously such files silently produced an empty `<Window />` with zero children
- Parser now recognizes the three-argument `Controls.Add(child, column, row)` overload and records the cell position (`Control.column`/`row`) plus `ColumnCount`/`RowCount`; TableLayoutPanel children were previously orphaned and dropped from the rendered XAML (the `05_tablelayout` case recorded in `TODO.md`)
- Renderer keeps a container control's `Text` (e.g. GroupBox station headers) as the WPF `Header` instead of dropping it, and emits `Header` rather than the invalid `Content` on GroupBox elements; elements with no WPF text property (panels, layout containers) no longer receive a stray `Content` attribute
- Renderer no longer nests a duplicate inner panel when the container element already maps to the inferred panel type (`TableLayoutPanel` -> `Grid`, `FlowLayoutPanel` -> `WrapPanel`, `Panel` -> `StackPanel`), which had emitted `Grid` inside `Grid` and the extra `WrapPanel` recorded in `TODO.md`
- Renderer emits `RowDefinitions`/`ColumnDefinitions` and the `Grid.Row`/`Grid.Column` attached properties for `TableLayoutPanel` grids (percent styles map to equal star sizes); previously all cells collapsed into a single overlapping cell
- Analyzer now separates vertical linear chains from layouts scattered on both axes: scattered containers infer a `Grid` (the priority its docstring already promised) instead of a vertical `StackPanel` that reflowed absolute layouts
- Absolute layout fidelity: children of layout `Grid`s keep their WinForms `Location`/`Size` as `HorizontalAlignment`/`VerticalAlignment` + `Margin` + `Width`/`Height`, and the form `ClientSize` becomes the WPF `Window` `Width`/`Height`; parsed `Location`/`Size` data was previously discarded by the renderer
- Renderer no longer emits the invalid `DockPanel.Dock="Fill"`: WPF's `Dock` enum has no `Fill` member, so Visual Studio reported `XAML0431` for every occurrence and the generated window failed to load. WinForms `DockStyle.Fill` children are now emitted without a `Dock` attribute and moved to the end of the `DockPanel`, where `DockPanel.LastChildFill` (True by default) gives them the remaining space; `DockPanel.LastChildFill="False"` is emitted when the last child keeps an explicit `Dock`

### [Security]

### [Removed]

### [Deprecated]

