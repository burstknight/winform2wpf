"""XAML renderer for WPF output."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from wf2wpf.parser import Control, ControlTree


def render_xaml(
    tree: ControlTree,
    decisions: dict[str, dict[str, Any]],
    output_path: str | Path | None = None,
) -> str:
    """Render control tree to WPF XAML.

    Args:
        tree: Control tree to render.
        decisions: Layout decisions from analyzer.
        output_path: Optional output path to write XAML.

    Returns:
        XAML string.
    """

    # Create root element (default to Window for Form)
    root_elem = ET.Element("Window")
    root_elem.set(
        "xmlns",
        "http://schemas.microsoft.com/winfx/2006/xaml/presentation",
    )
    root_elem.set("xmlns:x", "http://schemas.microsoft.com/winfx/2006/xaml")

    if tree.root:
        if tree.root.name:
            root_elem.set("x:Name", tree.root.name)
        if tree.root.text:
            root_elem.set("Title", tree.root.text)
        # ClientSize of the WinForms form approximates the WPF window size
        # (WPF Width/Height include chrome; close enough for migration).
        if tree.root.size_w is not None:
            root_elem.set("Width", _num(tree.root.size_w))
        if tree.root.size_h is not None:
            root_elem.set("Height", _num(tree.root.size_h))

    # Render children of root
    if tree.root:
        _render_container(tree.root, root_elem, decisions)

    # Register namespaces for clean output
    ET.register_namespace("", "http://schemas.microsoft.com/winfx/2006/xaml/presentation")
    ET.register_namespace("x", "http://schemas.microsoft.com/winfx/2006/xaml")

    # Pretty-print with tab indentation for readable output
    ET.indent(root_elem, space="\t")
    xml_str = ET.tostring(root_elem, encoding="unicode", xml_declaration=False)

    if output_path:
        # Final newline per .editorconfig insert_final_newline.
        Path(output_path).write_text(xml_str + "\n", encoding="utf-8", newline="\n")

    return xml_str


def _is_fill_dock(control: Control) -> bool:
    """Whether a control uses WinForms ``DockStyle.Fill``."""
    return (control.dock or "").strip().lower() == "fill"


def _ordered_children(control: Control, panel_name: str) -> list[Control]:
    """Order children so that DockPanel fill semantics match WinForms.

    WinForms applies docking in z-order and a ``DockStyle.Fill`` control eats
    the remaining space of its parent. WPF has no ``Fill`` member in its
    ``Dock`` enum; instead ``DockPanel.LastChildFill`` (True by default) gives
    the remaining space to the *last* child. Moving fill children to the end
    therefore reproduces the WinForms result.
    """
    if panel_name != "DockPanel":
        return list(control.children)
    fills = [c for c in control.children if _is_fill_dock(c)]
    others = [c for c in control.children if not _is_fill_dock(c)]
    return others + fills


def _apply_last_child_fill(children: list[Control], panel_elem: ET.Element) -> None:
    """Keep an explicit Dock on the last child of a DockPanel.

    ``DockPanel.LastChildFill`` defaults to True, which overrides the Dock
    value of the last child: it fills the remaining space instead of docking.
    When the last child is not a fill child it keeps an explicit Dock, so the
    fill behaviour has to be switched off.
    """
    if not children:
        return
    if _is_fill_dock(children[-1]):
        return
    panel_elem.set("LastChildFill", "False")


def _render_container(
    control: Control, parent_elem: ET.Element, decisions: dict[str, dict[str, Any]]
) -> None:
    """Render a container's children with inferred panel."""
    if not control.children:
        return

    panel_name = "StackPanel"
    orientation = None

    key = control.name or "root"
    dec = decisions.get(key) or decisions.get("root") or {}
    if dec:
        ptype = dec.get("panel_type")
        if ptype in ("StackPanel", "DockPanel", "WrapPanel", "Grid", "Canvas"):
            panel_name = ptype
        orient = dec.get("orientation")
        if orient:
            orientation = orient

    # Reuse the container's own element when it already maps to the inferred
    # panel type (e.g. TableLayoutPanel -> Grid, FlowLayoutPanel -> WrapPanel);
    # otherwise add an inner panel element.
    if parent_elem.tag == panel_name:
        panel_elem = parent_elem
    else:
        panel_elem = ET.SubElement(parent_elem, panel_name)

    if orientation and panel_name == "StackPanel":
        panel_elem.set("Orientation", orientation)

    if panel_elem.tag == "Grid":
        _add_grid_definitions(control, panel_elem)

    children = _ordered_children(control, panel_name)
    for child in children:
        child_elem = _create_element(child, panel_elem, panel_name)
        _set_text(child, child_elem)
        if child.children:
            _render_container(child, child_elem, decisions)

    if panel_name == "DockPanel":
        _apply_last_child_fill(children, panel_elem)


def _add_grid_definitions(control: Control, panel_elem: ET.Element) -> None:
    """Emit RowDefinitions/ColumnDefinitions for a TableLayoutPanel-backed Grid.

    Column/Row styles are approximated: WinForms percent styles map to equal
    star-sized definitions (a follow-up in TODO.md covers absolute pixel
    styles). Grids used for absolute layout (no counts, no cells) get no
    definitions.
    """
    cells = [c for c in control.children if c.column is not None or c.row is not None]
    column_count = control.column_count
    row_count = control.row_count
    if cells:
        if not column_count:
            column_count = max((c.column for c in cells if c.column is not None), default=-1) + 1
        if not row_count:
            row_count = max((c.row for c in cells if c.row is not None), default=-1) + 1
    if not column_count and not row_count:
        return
    if row_count:
        row_defs = ET.SubElement(panel_elem, "Grid.RowDefinitions")
        for _ in range(row_count):
            ET.SubElement(row_defs, "RowDefinition").set("Height", "*")
    if column_count:
        col_defs = ET.SubElement(panel_elem, "Grid.ColumnDefinitions")
        for _ in range(column_count):
            ET.SubElement(col_defs, "ColumnDefinition").set("Width", "*")


def _num(value: float) -> str:
    """Format a parsed WinForms number for XAML (12.0 -> '12')."""
    return f"{value:g}"


def _create_element(child: Control, parent_panel: ET.Element, panel_name: str) -> ET.Element:
    """Create XAML element for child control."""
    child_type = _get_wpf_short_type(child.type_name)
    elem = ET.SubElement(parent_panel, child_type)
    if child.name:
        elem.set("x:Name", child.name)
    if child.dock and panel_name == "DockPanel" and not _is_fill_dock(child):
        elem.set("DockPanel.Dock", child.dock)
    if panel_name == "Grid":
        # TableLayoutPanel cell placement; ignored when unset (absolute layout).
        if child.column is not None:
            elem.set("Grid.Column", str(child.column))
        if child.row is not None:
            elem.set("Grid.Row", str(child.row))
        # Absolute-layout children (no cell, no dock) keep their WinForms
        # Location/Size as top-left alignment, margin, and explicit size.
        if child.column is None and child.dock is None:
            has_position = child.location_x is not None and child.location_y is not None
            if has_position or child.size_w is not None or child.size_h is not None:
                elem.set("HorizontalAlignment", "Left")
                elem.set("VerticalAlignment", "Top")
            if has_position:
                elem.set(
                    "Margin",
                    f"{_num(child.location_x)},{_num(child.location_y)},0,0",
                )
            if child.size_w is not None:
                elem.set("Width", _num(child.size_w))
            if child.size_h is not None:
                elem.set("Height", _num(child.size_h))
    return elem


# WPF property that carries WinForms Text for each kind of element. GroupBox is
# a HeaderedContentControl, so its text belongs on Header, never Content.
_HEADER_TYPES = frozenset(("GroupBox", "TabItem", "TabPage"))
_CONTENT_TYPES = frozenset(("Label", "Button", "CheckBox", "RadioButton", "ToggleButton"))
_TEXT_TYPES = frozenset(("TextBox",))


def _set_text(child: Control, elem: ET.Element) -> None:
    """Set the text-carrying property for leaf and container elements alike.

    Container controls (e.g. a GroupBox wrapping a panel) keep their header;
    elements with no WPF text property (panels, layout containers) are skipped
    instead of receiving an invalid attribute.
    """
    if child.text is None:
        return
    short = _get_wpf_short_type(child.type_name)
    if short in _HEADER_TYPES:
        elem.set("Header", child.text)
    elif short in _CONTENT_TYPES:
        elem.set("Content", child.text)
    elif short in _TEXT_TYPES:
        elem.set("Text", child.text)


def _get_wpf_short_type(winforms_type: str) -> str:
    """Get short WPF type name."""
    if not winforms_type:
        return "FrameworkElement"
    short = winforms_type.split(".")[-1] if "." in winforms_type else winforms_type
    mapping = {
        "Form": "Window",
        "Panel": "StackPanel",
        "FlowLayoutPanel": "WrapPanel",
        "TableLayoutPanel": "Grid",
        "UserControl": "UserControl",
        "TabPage": "TabItem",
        "MenuStrip": "Menu",
        "ToolStrip": "ToolBar",
        "StatusStrip": "StatusBar",
    }
    return mapping.get(short, short)
