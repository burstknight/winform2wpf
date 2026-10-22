# Test Strategy (EN)

## Objectives

- Ensure correctness of parser, analyzer, mapper, renderer, CLI
- Catch regressions when modifying layout inference rules
- Use synthetic fixtures to validate behavior without requiring real company samples
- Keep tests fast and deterministic
- Follow `uv` + `pytest` workflow

## Test Types

- **Unit tests**: Focus on individual modules (parser/analyzer/mapper/renderer). Use small, constructed inputs
- **Integration tests**: End-to-end from `Designer.cs` → XAML using synthetic fixtures; compare against golden files with structural assertions

## Test Data

Synthetic fixtures under `tests/fixtures/` cover representative layouts:

| # | File | Scenario | Expected Panel |
|---|---|---|---|
| 01 | `01_simple_form.Designer.cs` | Simple form (Label + TextBox + Button) | `StackPanel` (vertical) or `Grid` |
| 02 | `02_horizontal_buttons.Designer.cs` | Horizontal button group | `StackPanel` (Horizontal) |
| 03 | `03_dockpanel_like.Designer.cs` | Dock-like layout (Top/Left/Fill) | `DockPanel` |
| 04 | `04_flowlayout.Designer.cs` | FlowLayoutPanel-like flow | `WrapPanel` |
| 05 | `05_tablelayout.Designer.cs` | TableLayoutPanel form fields | `Grid` with column/row definitions |
| 06 | `06_nested_panel.Designer.cs` | Nested containers | Each container inferred independently |
| 07 | `07_modern_style.Designer.cs` | Designer file without the `this.` qualifier | Same as the classic style |
| 08 | `08_colors.Designer.cs` | ForeColor/BackColor on groups and children | `Foreground`/`Background` with colour inheritance |

Golden files in `tests/expected/` represent the expected XAML structure per case.

## Test Files

- `tests/test_parser.py`: Control extraction, properties, parent-child, tree structure
- `tests/test_analyzer.py`: Inference rules (FlowLayout→WrapPanel, TableLayout→Grid, Dock→DockPanel, chains→StackPanel, fallback→Grid)
- `tests/test_mapper.py`: Type/property mappings (Text→Content, x:Name, Visibility/IsEnabled, Dock)
- `tests/test_renderer.py`: Namespaces, root element, panel types, nesting, layout attributes, XML parseability
- `tests/test_styles.py`: Colour translation (named colours, `Color.FromArgb`, system colours)
- `tests/test_integration.py`: End-to-end against golden files (structural assertions)
- `tests/test_xaml_load.py`: Parses the golden XAML with the real WPF parser (`System.Windows.Markup.XamlReader`, run through Windows PowerShell 5.1); skipped when PowerShell or the WPF assemblies are unavailable
- `tests/conftest.py`: Shared fixtures/helpers (load fixtures/expected, temp paths)

## Golden File Approach

Use **structural assertions** rather than byte-for-byte string equality:
- Verify root element and panel types are present
- Verify `x:Name` exists for controls that had WinForms names
- Verify key attributes (`Content`, `Text`, `DockPanel.Dock`, `Grid.Row`, `Grid.Column`, etc.)
- Verify nesting matches control tree
- Verify XAML is parseable via `xml.etree.ElementTree.parse`

This avoids false failures from whitespace, attribute order, or minor formatting tweaks.

## Running Tests

```bash
# Sync dev environment
uv sync --dev

# Run all tests
uv run pytest

# Verbose
uv run pytest -v

# With coverage
uv run pytest --cov=src/wf2wpf --cov-report=term-missing

# Target specific test
uv run pytest tests/test_analyzer.py -v
```

## Success Criteria

- All tests pass: `uv run pytest` returns 0
- CLI help works: `uv run wf2wpf --help`
- `uvx --from . wf2wpf --help` works (verifies packaging)
- No unintended imports from `tests/` into package
- Tests validate the core “layout intent” behavior (especially StackPanel/DockPanel/WrapPanel/Grid choices)
