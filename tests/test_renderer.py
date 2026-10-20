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
    assert [local(child.tag) for child in grids[0]] == ["Label", "TextBox"]
