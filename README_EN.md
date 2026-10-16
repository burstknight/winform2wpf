# wf2wpf (English)

**wf2wpf** is a Python CLI tool that converts WinForms `*.Designer.cs` files to WPF `*.xaml` files. Instead of translating absolute coordinates (like `Canvas.Left/Top`), it infers layout intent from WinForms design clues such as `Dock`, `FlowLayoutPanel`, `TableLayoutPanel`, and control alignment to generate more idiomatic WPF layouts (`StackPanel`, `DockPanel`, `WrapPanel`, `Grid`).

## Features

- Parse WinForms `*.Designer.cs` to build a control tree
- Infer layout: prefer `WrapPanel`/`DockPanel`/`StackPanel`/`Grid`; `Canvas` only as a last resort
- Map common WinForms controls and properties to WPF equivalents
- Recursively render valid WPF XAML with correct namespaces
- Generate a conversion report highlighting items that need manual review
- Designed for both modern .NET WinForms and older .NET Framework WinForms projects

## Requirements

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) for environment and dependency management

## Installation & Usage

### Development (local)

```bash
# Clone and enter the repository
cd winform2wpf

# Sync development dependencies
uv sync --dev

# Run the CLI
uv run wf2wpf --help
uv run wf2wpf convert path/to/Form.Designer.cs
```

### Run from local directory with uvx

```bash
uvx --from . wf2wpf --help
uvx --from . wf2wpf convert path/to/Form.Designer.cs
```

### Run from git (future)

```bash
uvx --from git+https://github.com/<your-repo>/winform2wpf wf2wpf convert path/to/Form.Designer.cs
```

### Run from PyPI (future)

```bash
uvx wf2wpf convert path/to/Form.Designer.cs
```

## Development

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/wf2wpf --cov-report=term-missing

# Verify CLI entry
uv run wf2wpf --help
```

## Limitations (MVP)

- Focuses on parsing `InitializeComponent()` from `*.Designer.cs`
- Supports common controls: `Label`, `Button`, `TextBox`, `CheckBox`, `RadioButton`, `Panel`, `GroupBox`, `FlowLayoutPanel`, `TableLayoutPanel`, `TabControl`, etc.
- Does not parse dynamically added controls at runtime
- `.resx` resource handling is minimal in MVP (placeholder)
- Complex custom/user controls may require manual adjustment

## Documentation

- [Development Plan (EN)](docs/DEVELOPMENT_PLAN_EN.md) / [(ZH-TW)](docs/DEVELOPMENT_PLAN_ZH-TW.md)
- [Architecture (EN)](docs/ARCHITECTURE_EN.md) / [(ZH-TW)](docs/ARCHITECTURE_ZH-TW.md)
- [Test Strategy (EN)](docs/TEST_STRATEGY_EN.md) / [(ZH-TW)](docs/TEST_STRATEGY_ZH-TW.md)
