"""Parser for WinForms Designer.cs files.

This module parses WinForms Designer.cs files to extract control information
and build a control tree for layout analysis and XAML rendering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


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


def parse_designer_cs(path: str | Path) -> ControlTree:
    """Parse a Designer.cs file and return a control tree.

    Args:
        path: Path to Designer.cs file.

    Returns:
        ControlTree containing parsed controls.
    """
    path = Path(path)
    tree = ControlTree()
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return tree

    # Find root form class name
    form_match = re.search(r"partial class\s+(\w+)", content)
    form_name = form_match.group(1) if form_match else "Form"

    # Create root
    root = Control(name=form_name, type_name="Form")
    tree.root = root
    tree.add_control(root)

    # Extract control declarations: private System.Windows.Forms.Xxx name;
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

    # Property assignments: this.name.Property = ...
    prop_re = re.compile(
        r"this\.(\w+)\.(\w+)\s*=\s*([^;]+);",
        re.IGNORECASE,
    )
    for m in prop_re.finditer(content):
        cname = m.group(1)
        prop = m.group(2)
        val = m.group(3).strip()
        ctrl = tree.get_control(cname)
        if not ctrl:
            continue
        if prop.lower() == "name":
            ctrl.name = cname
        elif prop.lower() == "text":
            # Extract quoted string
            q = re.search(r'"([^"]*)"', val)
            if q:
                ctrl.text = q.group(1)
        elif prop.lower() == "dock":
            d = re.search(r"DockStyle\.(\w+)", val)
            if d:
                ctrl.dock = d.group(1)
        elif prop.lower() == "location":
            p = re.search(r"Point\(([^,]+),\s*([^)]+)\)", val)
            if p:
                try:
                    ctrl.location_x = float(p.group(1).strip())
                    ctrl.location_y = float(p.group(2).strip())
                except Exception:
                    pass
        elif prop.lower() == "size":
            s = re.search(r"Size\(([^,]+),\s*([^)]+)\)", val)
            if s:
                try:
                    ctrl.size_w = float(s.group(1).strip())
                    ctrl.size_h = float(s.group(2).strip())
                except Exception:
                    pass

    # Add controls: this.container.Controls.Add(this.child);
    add_re = re.compile(
        r"this\.(\w+)\.Controls\.Add\(this\.(\w+)\)",
        re.IGNORECASE,
    )
    for m in add_re.finditer(content):
        parent = m.group(1)
        child = m.group(2)
        c = tree.get_control(child)
        if c:
            c.parent_name = parent

    # Add to root if added to this.Controls
    addroot_re = re.compile(
        r"this\.Controls\.Add\(this\.(\w+)\)",
        re.IGNORECASE,
    )
    for m in addroot_re.finditer(content):
        child = m.group(1)
        c = tree.get_control(child)
        if c:
            c.parent_name = form_name

    tree.build_hierarchy()
    return tree
