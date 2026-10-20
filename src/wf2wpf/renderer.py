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

    for child in control.children:
        child_elem = _create_element(child, panel_elem, panel_name)
        _set_text(child, child_elem)
        if child.children:
            _render_container(child, child_elem, decisions)


def _create_element(child: Control, parent_panel: ET.Element, panel_name: str) -> ET.Element:
    """Create XAML element for child control."""
    child_type = _get_wpf_short_type(child.type_name)
    elem = ET.SubElement(parent_panel, child_type)
    if child.name:
        elem.set("x:Name", child.name)
    if child.dock and panel_name == "DockPanel":
        elem.set("DockPanel.Dock", child.dock)
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
