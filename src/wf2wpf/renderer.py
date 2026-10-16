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

    # Render children recursively (skeleton - minimal)
    if tree.root:
        _render_control_children(tree.root, root_elem, decisions)

    # Convert to string
    ET.register_namespace("", "http://schemas.microsoft.com/winfx/2006/xaml/presentation")
    ET.register_namespace("x", "http://schemas.microsoft.com/winfx/2006/xaml")
    xml_str = ET.tostring(root_elem, encoding="unicode", xml_declaration=False)

    if output_path:
        Path(output_path).write_text(xml_str, encoding="utf-8")

    return xml_str


def _render_control_children(
    control: Control, parent_elem: ET.Element, decisions: dict[str, dict[str, Any]]
) -> None:
    """Render children of a control (skeleton)."""
    for child in control.children:
        # Basic element
        child_type = _get_wpf_short_type(child.type_name)
        child_elem = ET.SubElement(parent_elem, child_type)
        if child.name:
            child_elem.set("x:Name", child.name)
        if child.text:
            child_elem.set("Content", child.text)
        _render_control_children(child, child_elem, decisions)


def _get_wpf_short_type(winforms_type: str) -> str:
    """Get short WPF type name."""
    if not winforms_type:
        return "FrameworkElement"
    if "." in winforms_type:
        short = winforms_type.split(".")[-1]
    else:
        short = winforms_type
    mapping = {
        "Form": "Window",
        "Panel": "StackPanel",
        "FlowLayoutPanel": "WrapPanel",
        "TableLayoutPanel": "Grid",
        "UserControl": "UserControl",
    }
    return mapping.get(short, short)
