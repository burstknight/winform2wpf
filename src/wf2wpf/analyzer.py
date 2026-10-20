"""Layout inference for WinForms control tree.

This module analyzes control layout intent and infers appropriate WPF panels
(StackPanel, DockPanel, WrapPanel, Grid). Absolute layouts fall back to a Grid
with per-child margins; Canvas is never required.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from wf2wpf.parser import Control, ControlTree


PanelType = Literal["StackPanel", "DockPanel", "WrapPanel", "Grid", "Canvas"]


def infer_container_panel(control: Control) -> dict[str, Any]:
    """Infer the best WPF panel type for a container control.

    Priority:
        1. FlowLayoutPanel -> WrapPanel
        2. TableLayoutPanel -> Grid
        3. Dock intent -> DockPanel
        4. Linear chains (same row -> Horizontal, same column -> Vertical)
           -> StackPanel
        5. Children scattered on both axes (absolute WinForms layout)
           -> Grid, rendered with per-child Margin/Width/Height
        6. Single child -> StackPanel (Vertical)

    Args:
        control: Container control to analyze.

    Returns:
        Dictionary containing panel type and layout parameters.
    """
    result: dict[str, Any] = {
        "panel_type": "Grid",
        "orientation": None,
        "column_defs": [],
        "row_defs": [],
        "rationale": "Default fallback to Grid",
    }

    if not control or not control.children:
        result["rationale"] = "No children; default to Grid"
        return result

    type_lower = (control.type_name or "").lower()

    # 1. FlowLayoutPanel -> WrapPanel
    if "flowlayoutpanel" in type_lower:
        result["panel_type"] = "WrapPanel"
        result["rationale"] = "FlowLayoutPanel -> WrapPanel"
        return result

    # 2. TableLayoutPanel -> Grid
    if "tablelayoutpanel" in type_lower:
        result["panel_type"] = "Grid"
        result["rationale"] = "TableLayoutPanel -> Grid"
        # Column/row definitions to be filled during full implementation
        return result

    # 3. Dock intent detection
    has_dock_intent = any(child.dock for child in control.children)
    if has_dock_intent:
        result["panel_type"] = "DockPanel"
        result["rationale"] = "Dock intent detected -> DockPanel"
        return result

    # 4. Linear chain detection - simple heuristic
    # Same row (e.g. horizontal buttons) -> horizontal stack; same column
    # (e.g. a list of radio buttons) -> vertical stack.
    if len(control.children) >= 2:
        ys = []
        xs = []
        for c in control.children:
            ys.append(c.location_y if c.location_y is not None else 0)
            xs.append(c.location_x if c.location_x is not None else 0)
        y_spread = max(ys) - min(ys) if ys else 0
        x_spread = max(xs) - min(xs) if xs else 0
        if y_spread < 20 and x_spread > 10:  # roughly same row, spread horizontally
            result["panel_type"] = "StackPanel"
            result["orientation"] = "Horizontal"
            result["rationale"] = "Horizontal linear chain -> StackPanel (Horizontal)"
            return result
        if x_spread < 20:  # roughly same column, stacked vertically
            result["panel_type"] = "StackPanel"
            result["orientation"] = "Vertical"
            result["rationale"] = "Vertical linear chain -> StackPanel (Vertical)"
            return result
        # 5. Scattered on both axes: an absolute WinForms layout that must not
        # be reflowed into a stack - keep positions via a Grid + Margin.
        result["panel_type"] = "Grid"
        result["orientation"] = None
        result["rationale"] = "Scattered absolute positions -> Grid with Margin"
        return result

    # 6. Single child: a vertical stack is the neutral choice.
    result["panel_type"] = "StackPanel"
    result["orientation"] = "Vertical"
    result["rationale"] = "Single child -> StackPanel (Vertical)"
    return result


def analyze_tree(tree: ControlTree) -> dict[str, dict[str, Any]]:
    """Analyze entire control tree and return layout decisions per container.

    Args:
        tree: Control tree to analyze.

    Returns:
        Mapping of control name to layout decision dict.
    """
    decisions: dict[str, dict[str, Any]] = {}

    # Analyze containers (controls that have children)
    for name, control in tree.controls.items():
        if control.children:
            decisions[name] = infer_container_panel(control)

    # Analyze root
    if tree.root and tree.root.name not in decisions and tree.root.children:
        key = tree.root.name or "root"
        decisions[key] = infer_container_panel(tree.root)

    return decisions
