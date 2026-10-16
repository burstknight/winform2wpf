"""Property and type mapping from WinForms to WPF."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore

    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False


def load_rules(path: str | Path | None = None) -> dict[str, Any]:
    """Load mapping rules from rules.yaml.

    Args:
        path: Optional path to rules.yaml.

    Returns:
        Dictionary of mapping rules.
    """
    if path is None:
        path = Path(__file__).resolve().parents[2] / "rules.yaml"

    path = Path(path)
    if path.exists() and YAML_AVAILABLE:
        try:
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


def map_control_type(winforms_type: str) -> str:
    """Map WinForms control type to WPF control type.

    Args:
        winforms_type: WinForms type name (e.g., "System.Windows.Forms.Button").

    Returns:
        WPF control type name (e.g., "Button").
    """
    if not winforms_type:
        return "FrameworkElement"

    # Extract short name
    if "." in winforms_type:
        short = winforms_type.split(".")[-1]
    else:
        short = winforms_type

    # Common mappings
    mapping = {
        "Form": "Window",
        "UserControl": "UserControl",
        "Button": "Button",
        "Label": "Label",
        "TextBox": "TextBox",
        "CheckBox": "CheckBox",
        "RadioButton": "RadioButton",
        "Panel": "StackPanel",
        "GroupBox": "GroupBox",
        "FlowLayoutPanel": "WrapPanel",
        "TableLayoutPanel": "Grid",
        "TabControl": "TabControl",
        "TabPage": "TabItem",
        "MenuStrip": "Menu",
        "ToolStrip": "ToolBar",
        "StatusStrip": "StatusBar",
    }
    return mapping.get(short, short)
