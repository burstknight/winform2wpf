# Architecture (EN)

## Overview

This document describes the module structure, data model, layout inference, rendering, and packaging design for **wf2wpf**.

The tool follows a pipeline: **Parse → Analyze → Map → Render → Report**.

```text
Designer.cs → parser.py (Control Tree) → analyzer.py (Layout decisions)
→ mapper.py (Property mapping) → renderer.py (XAML) + report.py (Report)
→ CLI (wf2wpf convert)
```

## Directory Layout

```text
winform2wpf/
├── src/
│   └── wf2wpf/
│       ├── __init__.py      # Package metadata and version
│       ├── analyzer.py      # Layout inference logic
│       ├── cli.py           # CLI entry point
│       ├── mapper.py        # WinForms -> WPF mappings
│       ├── parser.py        # Designer.cs parsing
│       ├── renderer.py      # XAML generation
│       ├── report.py        # Conversion report
│       └── resources.py     # .resx handling (placeholder)
├── tests/
│   ├── fixtures/           # Synthetic Designer.cs
│   ├── expected/           # Golden XAML files
│   ├── test_*.py           # Unit + integration tests
│   └── conftest.py
├── docs/                   # Bilingual documentation
├── pyproject.toml          # uv + hatchling config
├── rules.yaml              # Mapping rules
└── README*.md              # Bilingual READMEs
```

## Core Modules

### parser.py

Responsibilities:
- Read `*.Designer.cs`
- Extract `InitializeComponent()` block
- Collect field declarations and `new` instantiations
- Extract property assignments (`Location`, `Size`, `Dock`, `Anchor`, `Text`, `TabIndex`, `Enabled`, `Visible`)
- Extract parent-child via `Controls.Add`
- Reconstruct control tree

Key data structures (using `dataclasses`, English comments, Google-style docstrings):

- `Control`: Represents a single WinForms control
- `ControlTree`: Container for root + helpers to build/navigate tree

Parsing approach: **targeted regex** (MVP). This is tolerant of formatting and typical Visual Studio output.

### analyzer.py

Responsibilities: For each container control, infer the most appropriate WPF panel.

Priority (as defined in plan):
1. `FlowLayoutPanel` → `WrapPanel`
2. `TableLayoutPanel` → `Grid` (with column/row definitions)
3. `Dock` intent present → `DockPanel`
4. Horizontal/vertical linear chains → `StackPanel`
5. Otherwise → `Grid` + `Margin` + alignment (no `Canvas` by default)
6. Fallback → `Grid`

Outputs per container: `panel_type`, `orientation`, `column_defs`, `row_defs`, and rationale stored for reporting.

### mapper.py

Responsibilities: Map WinForms types/properties to WPF equivalents.

Mappings (representative):
- `Form` → `Window` (root)
- `UserControl` → `UserControl`
- `Name` → `x:Name`
- `Text` (Label/Button/CheckBox/RadioButton) → `Content`
- `TextBox.Text` → `Text`
- `Enabled` → `IsEnabled`
- `Visible` → `Visibility` (`true/false` → `Visible/Collapsed`)
- `Dock` → `DockPanel.Dock` (`DockStyle.Fill` has no WPF counterpart, see below)
- `ForeColor` → `Foreground` (`#AARRGGBB`; a `SystemColors.*` value becomes a `DynamicResource` on the matching system brush)
- `BackColor` → `Background`
- `TabIndex` → `TabIndex`

Rules sourced from `rules.yaml` where practical.

### styles.py

Responsibilities: Translate the WinForms colour expressions into WPF values.

- `to_wpf_brush()` maps a colour expression (`Color.Green`, `Color.FromArgb(...)`, `SystemColors.ControlText`) to a WPF brush value; the .NET named colours keep their exact value, a system colour refers to the WPF system brush so it keeps following the Windows theme
- An expression that cannot be translated produces no value at all instead of a guess

### renderer.py

Responsibilities: Recursively render XAML from control tree + analyzer decisions.

Requirements:
- Required namespaces: `xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"` and `xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"`
- Root: `Window` for Form (include `Title`, `x:Name` if present)
- For each container emit correct panel and attach layout-specific attributes to children
- Map WinForms `DockStyle.Fill` to the WPF fill semantics: the WPF `Dock` enum has no `Fill` member, so the child is emitted without a `Dock` attribute and moved to the end of the `DockPanel`, where `DockPanel.LastChildFill` (True by default) gives it the remaining space. When the last child keeps an explicit `Dock`, `LastChildFill="False"` is emitted so that value is honoured
- Carry the WinForms `ForeColor` inheritance down the tree: a child without its own colour takes the colour of its container, because the WPF theme styles set `Foreground` on most controls and an inherited colour would otherwise never reach them. WPF panels have no `Foreground`, so a panel hands its colour to its children instead of carrying it itself
- Use `xml.etree.ElementTree` to build and validate XML structure
- Output well-formed XAML text

### report.py

Responsibilities: Generate conversion report.

Sections:
- Converted: list of controls (type, name)
- Needs review: Font, Anchor nuances, custom/user controls, unmapped properties
- Skipped/Unmapped: unsupported types/properties
- Layout decisions: per-container panel choice + brief rationale
- Warnings

Supports text (default) and JSON (future). Uses `rich` for CLI-friendly text output where available.

### cli.py

Entry: `def main() -> None:` mapped to `wf2wpf = "wf2wpf.cli:main"` in `pyproject.toml`.

Commands:
- `wf2wpf convert <input.Designer.cs> [--output <out.xaml>] [--report] [--report-format text|json]`
- `wf2wpf --help`, `wf2wpf --version`

Behavior:
- Resolve paths, call parser/analyzer/mapper/renderer/report
- Write XAML to output path
- Optionally print report to stdout
- Clear English error messages

### resources.py

Placeholder module for future `.resx` handling. Contains minimal stubs and TODOs in English. No MVP implementation.

## Data Model Concepts

- `Control.name`: WinForms control name (may be `None`)
- `Control.type_name`: Full or short type name
- `Control.children`: List of child controls (tree)
- `Control.dock/anchor/location/size`: Layout-related attributes
- `Control.column/row/column_span/row_span`: TableLayoutPanel info
- `Control.properties_raw`: Preserve unhandled assignments for reporting

## Packaging & uvx Support

`pyproject.toml`:
- `[build-system]` uses `hatchling>=1.25.0`
- `[project.scripts]` defines `wf2wpf = "wf2wpf.cli:main"`
- `[tool.hatch.build.targets.wheel]` packages `["src/wf2wpf"]` only
- Dev deps: `pytest`, `pytest-cov`, `rich`, `pyyaml`

This enables:
- `uv run wf2wpf ...` (dev)
- `uvx --from . wf2wpf ...` (local isolated)
- `uvx --from git+... wf2wpf ...` (remote)
- `uvx wf2wpf ...` (PyPI)
