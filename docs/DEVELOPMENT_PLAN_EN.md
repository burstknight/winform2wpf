# Development Plan (EN)

## Overview

**wf2wpf** is a Python-based CLI tool for converting WinForms `*.Designer.cs` files to WPF `*.xaml`. The core principle is: **infer layout intent, not copy absolute coordinates**.

We prioritize idiomatic WPF layouts (`WrapPanel`, `DockPanel`, `StackPanel`, `Grid`) over simulating WinForms pixel positioning. `Canvas` is used only as the final fallback when layout inference cannot determine a better alternative.

## Goals

- Provide a semi-automated conversion that saves time re-creating WinForms UIs in WPF
- Generate human-readable, editable WPF XAML
- Work with both modern .NET WinForms and legacy .NET Framework WinForms (`.Designer.cs` format is largely compatible)
- Keep the tool testable via `uv` + `pytest` with synthetic fixtures and golden files
- Support future use with `uvx` (packaged via `hatchling`, `src/` layout)

## MVP Scope

### In Scope

- [ ] Parse a single `*.Designer.cs` file and build a control tree
- [ ] Extract: control name/type, location/size, parent, `Dock`, `Anchor`, `TabIndex`, `Text`, `Enabled`, `Visible`
- [ ] Layout inference with priority: `WrapPanel` (FlowLayoutPanel) > `DockPanel` (Dock intent) > `StackPanel` (linear chains) > `Grid` (TableLayoutPanel or fallback)
- [ ] Basic controls: `Label`, `Button`, `TextBox`, `CheckBox`, `RadioButton`, `Panel`, `GroupBox`
- [ ] Common containers: `FlowLayoutPanel`, `TableLayoutPanel`, `TabControl` (structure aware)
- [ ] Render valid WPF XAML with required namespaces
- [ ] Generate conversion report (converted / needs review / unmapped)
- [ ] CLI: `wf2wpf convert <input.Designer.cs> [--output ...] [--report] [--report-format text|json]`

### Out of Scope (MVP)

- Full `.resx` image/icon extraction (placeholder only)
- Runtime dynamically added controls
- Perfect pixel-for-pixel visual match
- Automatic compilation/build of generated WPF project
- Third-party/custom control deep mapping beyond reporting

## Layout Inference Rules

| Priority | Condition | WPF Panel | Notes |
|---|---|---|---|
| 1 | Container is `FlowLayoutPanel` | `WrapPanel` | Closest to FlowLayout behavior |
| 2 | Container is `TableLayoutPanel` with columns/rows | `Grid` | Generate `ColumnDefinitions`/`RowDefinitions` (Absolute/Auto/Percent -> px/Auto/*) |
| 3 | Clear `Dock` intent (`Top/Bottom/Left/Right/Fill`) across children | `DockPanel` | Good for toolbars/sidebars/main content |
| 4 | Children form horizontal/vertical linear chains (similar Y/X, regular spacing) | `StackPanel` (`Horizontal`/`Vertical`) | Promotes automatic layout over absolute positioning |
| 5 | Cannot infer clearly | `Grid` with `Margin` + alignment | Avoid `Canvas` by default; easier to edit in WPF |
| Fallback | Edge case | `Grid` | Safety net |

## Development Phases

1. **Planning + Skeleton** (this phase): docs, `pyproject.toml`, `src/` modules, `rules.yaml`, synthetic fixtures + golden files, tests
2. **Parser implementation**: Extract control tree from `Designer.cs` using regex-based extraction (target `InitializeComponent`)
3. **Analyzer implementation**: Apply inference rules per container
4. **Mapper + Renderer**: Property mapping and recursive XAML generation
5. **Report + CLI**: Human-readable report and CLI polish
6. **Validation**: Run `uv run pytest`; test with synthetic samples; refine with real samples later

## Risks & Mitigations

- **Regex vs AST**: Use targeted regex first (simple, debuggable). Can migrate to `tree-sitter-c-sharp` later if needed
- **Ambiguous layouts**: Favor `Grid+Margin` over `Canvas`; log decisions in report
- **.NET Framework variance**: Parser is text-based and tolerant; add cases when real samples arrive
- **Over-generalization**: Keep rules explicit and testable; extend only when justified

## Non-Functional Requirements

- Python code: English comments only; Google-style docstrings; type hints
- Bilingual documentation (EN + ZH-TW)
- Local-only git commits (no push)
- Split commits when changes are large
- Use `uv` for env; `pytest` for tests
- `src/wf2wpf` layout + `hatchling` build system for `uvx` compatibility
