"""Unit tests for renderer module."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from wf2wpf.analyzer import analyze_tree
from wf2wpf.renderer import render_xaml
from wf2wpf.parser import Control, ControlTree


def test_render_simple_tree():
    """Test rendering simple tree."""
    tree = ControlTree()
    root = Control(name="Form1", type_name="Form", text="Test")
    child = Control(name="btn1", type_name="Button", text="Click")
    root.children.append(child)
    tree.root = root
    tree.add_control(root)
    tree.add_control(child)

    xaml = render_xaml(tree, {})
    # Check basic structure
    assert "Window" in xaml
    assert "x:Name=\"Form1\"" in xaml
    assert "Button" in xaml
    assert "Click" in xaml


def test_render_is_valid_xml():
    """Test rendered XAML is parseable."""
    tree = ControlTree()
    root = Control(name="Form1", type_name="Form")
    tree.root = root
    xaml = render_xaml(tree, {})
    try:
        ET.fromstring(xaml)
        assert True
    except Exception:
        assert False


def _build_tree(root: Control, controls: list[Control]) -> ControlTree:
    tree = ControlTree()
    tree.root = root
    tree.add_control(root)
    for ctrl in controls:
        tree.add_control(ctrl)
    return tree


def test_render_groupbox_container_keeps_header():
    """A container GroupBox must keep its text as Header, not lose it."""
    root = Control(name="Form1", type_name="Form")
    group = Control(
        name="groupBox1",
        type_name="System.Windows.Forms.GroupBox",
        text="站號",
    )
    button = Control(name="button1", type_name="Button", text="送出")
    group.children.append(button)
    root.children.append(group)
    tree = _build_tree(root, [group, button])

    xaml = render_xaml(tree, analyze_tree(tree))
    assert 'Header="站號"' in xaml
    assert 'Content="站號"' not in xaml
    assert 'Content="送出"' in xaml


def test_render_leaf_groupbox_uses_header_not_content():
    """GroupBox is a HeaderedContentControl: Content would be an invalid property."""
    root = Control(name="Form1", type_name="Form")
    group = Control(
        name="groupBox1",
        type_name="System.Windows.Forms.GroupBox",
        text="群組",
    )
    root.children.append(group)
    tree = _build_tree(root, [group])

    xaml = render_xaml(tree, analyze_tree(tree))
    assert 'Header="群組"' in xaml
    assert 'Content="群組"' not in xaml
    ET.fromstring(xaml)


def test_render_panel_with_text_emits_no_invalid_attribute():
    """Panels have neither Content nor Header; a stray attribute would break XAML."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(
        name="panel1",
        type_name="System.Windows.Forms.Panel",
        text="面板",
    )
    button = Control(name="button1", type_name="Button", text="Go")
    panel.children.append(button)
    root.children.append(panel)
    tree = _build_tree(root, [panel, button])

    xaml = render_xaml(tree, analyze_tree(tree))
    assert "面板" not in xaml
    ET.fromstring(xaml)


def test_render_tablelayout_reuses_grid_element():
    """TableLayoutPanel children must land in their own Grid, not a nested wrapper."""
    root = Control(name="Form1", type_name="Form")
    table = Control(
        name="tableLayoutPanel1",
        type_name="System.Windows.Forms.TableLayoutPanel",
        column_count=2,
        row_count=1,
    )
    label = Control(
        name="label1", type_name="Label", text="Name", column=0, row=0
    )
    textbox = Control(name="textBox1", type_name="TextBox", column=1, row=0)
    table.children.extend([label, textbox])
    root.children.append(table)
    tree = _build_tree(root, [table, label, textbox])

    xaml = render_xaml(tree, analyze_tree(tree))
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    grids = [elem for elem in doc.iter() if local(elem.tag) == "Grid"]
    assert len(grids) == 1, "TableLayoutPanel must be a single Grid, not Grid > Grid"
    assert [local(child.tag) for child in grids[0]] == [
        "Grid.RowDefinitions",
        "Grid.ColumnDefinitions",
        "Label",
        "TextBox",
    ]


def test_render_grid_definitions_and_cell_placement():
    """TableLayoutPanel counts become definitions; cells become attached props."""
    root = Control(name="Form1", type_name="Form")
    table = Control(
        name="tableLayoutPanel1",
        type_name="System.Windows.Forms.TableLayoutPanel",
        column_count=3,
        row_count=2,
    )
    a = Control(name="a", type_name="Label", column=0, row=0)
    b = Control(name="b", type_name="Label", column=2, row=1)
    table.children.extend([a, b])
    root.children.append(table)
    tree = _build_tree(root, [table, a, b])

    xaml = render_xaml(tree, analyze_tree(tree))
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    grid = next(e for e in doc.iter() if local(e.tag) == "Grid")
    rows = [e for e in grid if local(e.tag) == "Grid.RowDefinitions"]
    cols = [e for e in grid if local(e.tag) == "Grid.ColumnDefinitions"]
    assert len(rows) == 1
    assert len(list(rows[0])) == 2
    assert len(cols) == 1
    assert len(list(cols[0])) == 3

    by_name = {
        e.get("{http://schemas.microsoft.com/winfx/2006/xaml}Name"): e
        for e in grid
    }
    assert by_name["a"].get("Grid.Column") == "0"
    assert by_name["a"].get("Grid.Row") == "0"
    assert by_name["b"].get("Grid.Column") == "2"
    assert by_name["b"].get("Grid.Row") == "1"


def test_render_grid_derives_counts_from_cells_when_missing():
    """Children cells alone must size the Grid when Column/RowCount are unset."""
    root = Control(name="Form1", type_name="Form")
    table = Control(name="t1", type_name="System.Windows.Forms.TableLayoutPanel")
    a = Control(name="a", type_name="Label", column=1, row=2)
    table.children.append(a)
    root.children.append(table)
    tree = _build_tree(root, [table, a])

    xaml = render_xaml(tree, analyze_tree(tree))
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    grid = next(e for e in doc.iter() if local(e.tag) == "Grid")
    row_defs = next(e for e in grid if local(e.tag) == "Grid.RowDefinitions")
    col_defs = next(e for e in grid if local(e.tag) == "Grid.ColumnDefinitions")
    assert len(list(row_defs)) == 3  # rows 0..2
    assert len(list(col_defs)) == 2  # columns 0..1


def test_render_absolute_grid_has_no_definitions():
    """A Grid used for absolute layout must not gain empty table definitions."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(name="panel1", type_name="System.Windows.Forms.Panel")
    a = Control(name="a", type_name="Button", location_x=5, location_y=5)
    b = Control(name="b", type_name="Button", location_x=5, location_y=40)
    panel.children.extend([a, b])
    root.children.append(panel)
    tree = _build_tree(root, [panel, a, b])

    decisions = {"panel1": {"panel_type": "Grid", "orientation": None}}
    xaml = render_xaml(tree, decisions)
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    assert not any(local(e.tag).endswith("Definitions") for e in doc.iter())


def test_render_absolute_grid_children_keep_location_and_size():
    """Location/Size must reach the XAML as margin and explicit dimensions."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(name="panel1", type_name="System.Windows.Forms.Panel")
    a = Control(
        name="a",
        type_name="Button",
        text="Go",
        location_x=10,
        location_y=20,
        size_w=100,
        size_h=30,
    )
    panel.children.append(a)
    root.children.append(panel)
    tree = _build_tree(root, [panel, a])

    decisions = {"panel1": {"panel_type": "Grid", "orientation": None}}
    xaml = render_xaml(tree, decisions)
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    btn = next(e for e in doc.iter() if local(e.tag) == "Button")
    assert btn.get("HorizontalAlignment") == "Left"
    assert btn.get("VerticalAlignment") == "Top"
    assert btn.get("Margin") == "10,20,0,0"
    assert btn.get("Width") == "100"
    assert btn.get("Height") == "30"


def test_render_window_dimensions_from_client_size():
    """The form's ClientSize becomes the WPF Window Width/Height."""
    tree = ControlTree()
    root = Control(name="Form1", type_name="Form", size_w=800, size_h=600)
    tree.root = root
    tree.add_control(root)

    xaml = render_xaml(tree, {})
    assert 'Width="800"' in xaml
    assert 'Height="600"' in xaml
    ET.fromstring(xaml)


def _xaml_name(elem: ET.Element) -> str | None:
    """Read the x:Name attribute of a rendered element."""
    return elem.get("{http://schemas.microsoft.com/winfx/2006/xaml}Name")


def _dock_panel(xaml: str) -> ET.Element:
    """Return the DockPanel element of a rendered XAML document."""
    doc = ET.fromstring(xaml)
    local = lambda tag: tag.rsplit("}", 1)[-1]
    return next(e for e in doc.iter() if local(e.tag) == "DockPanel")


def test_render_dockstyle_fill_is_not_emitted_as_dock_value():
    """WPF's Dock enum has no Fill member, so the value must not be emitted."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(name="panel1", type_name="System.Windows.Forms.Panel")
    fill = Control(
        name="panelMain", type_name="System.Windows.Forms.Panel", dock="Fill"
    )
    panel.children.append(fill)
    root.children.append(panel)
    tree = _build_tree(root, [panel, fill])

    xaml = render_xaml(tree, analyze_tree(tree))
    assert 'DockPanel.Dock="Fill"' not in xaml
    assert "DockPanel.Dock=" not in xaml


def test_render_dockstyle_fill_child_is_moved_to_the_end():
    """The fill child must be last: DockPanel gives the rest of the space to it."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(name="panel1", type_name="System.Windows.Forms.Panel")
    fill = Control(
        name="panelMain", type_name="System.Windows.Forms.Panel", dock="Fill"
    )
    bottom = Control(
        name="panelBottom", type_name="System.Windows.Forms.Panel", dock="Bottom"
    )
    panel.children.extend([fill, bottom])
    root.children.append(panel)
    tree = _build_tree(root, [panel, fill, bottom])

    xaml = render_xaml(tree, analyze_tree(tree))
    dock_panel = _dock_panel(xaml)
    assert [_xaml_name(child) for child in dock_panel] == ["panelBottom", "panelMain"]
    assert dock_panel.get("LastChildFill") is None


def test_render_dockpanel_disables_last_child_fill_for_explicit_dock():
    """An explicit Dock on the last child must not be overridden by LastChildFill."""
    root = Control(name="Form1", type_name="Form")
    panel = Control(name="panel1", type_name="System.Windows.Forms.Panel")
    top = Control(name="panelTop", type_name="System.Windows.Forms.Panel", dock="Top")
    bottom = Control(
        name="panelBottom", type_name="System.Windows.Forms.Panel", dock="Bottom"
    )
    panel.children.extend([top, bottom])
    root.children.append(panel)
    tree = _build_tree(root, [panel, top, bottom])

    xaml = render_xaml(tree, analyze_tree(tree))
    dock_panel = _dock_panel(xaml)
    assert dock_panel.get("LastChildFill") == "False"
    assert [_xaml_name(child) for child in dock_panel] == ["panelTop", "panelBottom"]
