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
        Path(output_path).write_text(xml_str, encoding="utf-8", newline="\n")

    return xml_str


def _render_container(
    control: Control, parent_elem: ET.Element, decisions: dict[str, dict[str, Any]]
) -> None:
    """Render a container's children with inferred panel."""
    if not control.children:
        return

    panel_name = "StackPanel"
    orientation = None
    dock_target = None

    key = control.name or "root"
    dec = decisions.get(key) or decisions.get("root") or {}
    if dec:
        ptype = dec.get("panel_type")
        if ptype in ("StackPanel", "DockPanel", "WrapPanel", "Grid", "Canvas"):
            panel_name = ptype
        orient = dec.get("orientation")
        if orient:
            orientation = orient

    panel_elem = ET.SubElement(parent_elem, panel_name)
    if control.name and panel_name != "Window":
        pass  # Don't duplicate name on inner panel unless needed
    if orientation and panel_name == "StackPanel":
        panel_elem.set("Orientation", orientation)

    for child in control.children:
        child_elem = _create_element(child, panel_elem, panel_name)
        # Recursively render if container
        if child.children:
            _render_container(child, child_elem, decisions)
        else:
            _set_content(child, child_elem)


def _create_element(child: Control, parent_panel: ET.Element, panel_name: str) -> ET.Element:
    """Create XAML element for child control."""
    child_type = _get_wpf_short_type(child.type_name)
    elem = ET.SubElement(parent_panel, child_type)
    if child.name:
        elem.set("x:Name", child.name)
    if child.dock and panel_name == "DockPanel":
        elem.set("DockPanel.Dock", child.dock)
    return elem


def _set_content(child: Control, elem: ET.Element) -> None:
    """Set content/text for leaf element."""
    if child.text is not None:
        t = child.text
        # Map common types
        short = _get_wpf_short_type(child.type_name)
        if short in ("Label", "Button", "CheckBox", "RadioButton", "GroupBox"):
            elem.set("Content", t)
        elif short in ("TextBox"):
            elem.set("Text", t)
        else:
            elem.set("Content", t)


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
