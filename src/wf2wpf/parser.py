"""Parser for WinForms Designer.cs files.

This module parses WinForms Designer.cs files to extract control information
and build a control tree for layout analysis and XAML rendering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from wf2wpf.io import TextFileReader


@dataclass
class Control:
    """Represents a WinForms control.

    Attributes:
        name: Control name (may be None if not set).
        type_name: Control type name (e.g., "System.Windows.Forms.Button").
        parent_name: Parent control name (may be None).
        location_x: X coordinate.
        location_y: Y coordinate.
        size_w: Width.
        size_h: Height.
        dock: Dock value (Top/Bottom/Left/Right/Fill).
        anchor: Anchor value string.
        tab_index: Tab index.
        text: Text/Content value.
        enabled: Enabled flag.
        visible: Visible flag.
        column: Column index for TableLayoutPanel.
        row: Row index for TableLayoutPanel.
        column_span: Column span.
        row_span: Row span.
        column_count: Column count.
        row_count: Row count.
        column_styles: Column style definitions.
        row_styles: Row style definitions.
        flow_direction: Flow direction for FlowLayoutPanel.
        wrap_contents: Wrap contents flag.
        children: Child controls.
        properties_raw: Raw unhandled properties for reporting.
    """

    name: Optional[str] = None
    type_name: str = ""
    parent_name: Optional[str] = None
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    size_w: Optional[float] = None
    size_h: Optional[float] = None
    dock: Optional[str] = None
    anchor: Optional[str] = None
    tab_index: Optional[int] = None
    text: Optional[str] = None
    enabled: Optional[bool] = None
    visible: Optional[bool] = None
    column: Optional[int] = None
    row: Optional[int] = None
    column_span: Optional[int] = None
    row_span: Optional[int] = None
    column_count: Optional[int] = None
    row_count: Optional[int] = None
    column_styles: Optional[list[dict[str, Any]]] = None
    row_styles: Optional[list[dict[str, Any]]] = None
    flow_direction: Optional[str] = None
    wrap_contents: Optional[bool] = None
    children: list["Control"] = field(default_factory=list)
    properties_raw: dict[str, str] = field(default_factory=dict)


@dataclass
class ControlTree:
    """Represents a control tree parsed from Designer.cs."""

    root: Optional[Control] = None
    controls: dict[str, Control] = field(default_factory=dict)

    def add_control(self, control: Control) -> None:
        """Add a control to the tree."""
        if control.name:
            self.controls[control.name] = control

    def get_control(self, name: str) -> Optional[Control]:
        """Get a control by name."""
        return self.controls.get(name)

    def build_hierarchy(self) -> None:
        """Build parent-child hierarchy based on parent_name."""
        for ctrl in list(self.controls.values()):
            if ctrl.parent_name and ctrl.parent_name in self.controls:
                parent = self.controls[ctrl.parent_name]
                if ctrl not in parent.children:
                    parent.children.append(ctrl)


def _extract_quoted(val: str) -> Optional[str]:
    q = re.search(r'"([^"]*)"', val)
    if q:
        return q.group(1)
    q2 = re.search(r"'([^']*)'", val)
    if q2:
        return q2.group(1)
    return None


def parse_designer_cs(path: str | Path, reader: Optional[TextFileReader] = None) -> ControlTree:
    """Parse a Designer.cs file and return a control tree.

    Args:
        path: Path to Designer.cs file.
        reader: Optional text reader with a configured encoding detector.
            When omitted, a reader with default auto-detection is used.

    Returns:
        ControlTree containing parsed controls.
    """
    path = Path(path)
    tree = ControlTree()
    try:
        content = (reader or TextFileReader()).read_all_text(path)
    except Exception:
        return tree

    # Find root form class name
    form_match = re.search(r"partial class\s+(\w+)", content)
    form_name = form_match.group(1) if form_match else "Form"

    # Create root
    root = Control(name=form_name, type_name="Form")
    tree.root = root
    tree.add_control(root)

    # Extract control declarations
    decl_re = re.compile(
        r"private\s+(?:System\.(?:Windows\.)?Forms\.|System\.ComponentModel\.)?(\w+)\s+(\w+)\s*;",
        re.IGNORECASE,
    )
    for m in decl_re.finditer(content):
        ctype = m.group(1)
        cname = m.group(2)
        if ctype in ("IContainer", "ComponentContainer"):
            continue
        ftype = f"System.Windows.Forms.{ctype}"
        ctrl = Control(name=cname, type_name=ftype)
        tree.add_control(ctrl)

    # Property assignments: "this.name.Property = ..." (classic designer) or
    # "name.Property = ..." (modern .NET designer omits the "this." qualifier).
    # Anchored to line starts so a form-level "Text = ..." can never be matched
    # as "name.Property" and vice versa.
    prop_re = re.compile(
        r"^[ \t]*(?:this\.)?(\w+)\.(\w+)\s*=\s*([^;]+);",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in prop_re.finditer(content):
        cname = m.group(1)
        prop = m.group(2)
        val = m.group(3).strip()
        ctrl = tree.get_control(cname)
        if not ctrl:
            continue
        pl = prop.lower()
        if pl == "name":
            ctrl.name = cname
        elif pl == "text":
            qv = _extract_quoted(val)
            if qv is not None:
                ctrl.text = qv
        elif pl == "dock":
            d = re.search(r"DockStyle\.(\w+)", val)
            if d:
                ctrl.dock = d.group(1)
        elif pl == "location":
            p = re.search(r"Point\(([^,]+),\s*([^)]+)\)", val)
            if p:
                try:
                    ctrl.location_x = float(p.group(1).strip())
                    ctrl.location_y = float(p.group(2).strip())
                except Exception:
                    pass
        elif pl == "size":
            s = re.search(r"Size\(([^,]+),\s*([^)]+)\)", val)
            if s:
                try:
                    ctrl.size_w = float(s.group(1).strip())
                    ctrl.size_h = float(s.group(2).strip())
                except Exception:
                    pass
        elif pl in ("columncount", "rowcount"):
            n = re.match(r"\d+", val)
            if n:
                count = int(n.group(0))
                if pl == "columncount":
                    ctrl.column_count = count
                else:
                    ctrl.row_count = count

    # Form-level properties: "this.Property = ..." or "Property = ..." (modern
    # style). The line anchor is essential: without it, an indented
    # "groupBox1.Text = "24";" would match as form-level "Text = ...".
    formprop_re = re.compile(
        r"^[ \t]*(?:this\.)?(\w+)\s*=\s*([^;]+);",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in formprop_re.finditer(content):
        prop = m.group(1)
        val = m.group(2).strip()
        pl = prop.lower()
        if pl == "name":
            if root:
                root.name = _extract_quoted(val) or val.strip() or root.name
        elif pl == "text":
            if root:
                qv = _extract_quoted(val)
                if qv is not None:
                    root.text = qv
        elif pl == "clientsize":
            if root:
                s = re.search(r"Size\(([^,]+),\s*([^)]+)\)", val)
                if s:
                    try:
                        root.size_w = float(s.group(1).strip())
                        root.size_h = float(s.group(2).strip())
                    except Exception:
                        pass

    # Add controls
    # "this.x.Controls.Add(this.y)" (classic) or "x.Controls.Add(y)" (modern),
    # with the TableLayoutPanel overload "Add(child, column, row)".
    # Anchored so the form-level "Controls.Add(x)" form below never matches
    # as a child control named "Controls".
    add_re = re.compile(
        r"^[ \t]*(?:this\.)?(\w+)\.Controls\.Add\(\s*(?:this\.)?(\w+)"
        r"\s*(?:,\s*(\d+)\s*,\s*(\d+)\s*)?\)",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in add_re.finditer(content):
        parent = m.group(1)
        if parent == "this":  # form-level "this.Controls.Add(this.x)" line
            continue
        child = m.group(2)
        c = tree.get_control(child)
        if c:
            c.parent_name = parent
            if m.group(3) is not None and m.group(4) is not None:
                c.column = int(m.group(3))
                c.row = int(m.group(4))

    addroot_re = re.compile(
        r"^[ \t]*(?:this\.)?Controls\.Add\(\s*(?:this\.)?(\w+)\s*\)",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in addroot_re.finditer(content):
        child = m.group(1)
        c = tree.get_control(child)
        if c:
            c.parent_name = form_name

    tree.build_hierarchy()
    return tree
