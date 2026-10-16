"""Unit tests for analyzer module."""

from __future__ import annotations

from wf2wpf.analyzer import analyze_tree, infer_container_panel
from wf2wpf.parser import Control, ControlTree


def test_infer_flowlayoutpanel():
    """Test FlowLayoutPanel inference."""
    ctrl = Control(
        name="flow1",
        type_name="System.Windows.Forms.FlowLayoutPanel",
        children=[Control(name="b1", type_name="Button")],
    )
    result = infer_container_panel(ctrl)
    assert result["panel_type"] == "WrapPanel"


def test_infer_tablelayoutpanel():
    """Test TableLayoutPanel inference."""
    ctrl = Control(
        name="table1",
        type_name="System.Windows.Forms.TableLayoutPanel",
        children=[Control(name="l1", type_name="Label")],
    )
    result = infer_container_panel(ctrl)
    assert result["panel_type"] == "Grid"


def test_infer_dock_intent():
    """Test dock intent detection."""
    ctrl = Control(
        name="panel1",
        type_name="System.Windows.Forms.Panel",
        children=[Control(name="top", type_name="Panel", dock="Top")],
    )
    result = infer_container_panel(ctrl)
    assert result["panel_type"] == "DockPanel"


def test_analyze_tree():
    """Test analyzing tree."""
    tree = ControlTree()
    root = Control(name="Form1", type_name="Form", children=[])
    child = Control(
        name="flow1",
        type_name="System.Windows.Forms.FlowLayoutPanel",
        children=[Control(name="b1", type_name="Button")],
    )
    tree.root = root
    tree.add_control(root)
    tree.add_control(child)
    root.children.append(child)
    decisions = analyze_tree(tree)
    assert isinstance(decisions, dict)
