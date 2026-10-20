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


def test_infer_scattered_children_is_grid():
    """Absolute layouts scattered on both axes must not be reflowed into a stack."""
    ctrl = Control(
        name="panel1",
        type_name="System.Windows.Forms.Panel",
        children=[
            Control(name="a", type_name="Button", location_x=10, location_y=10),
            Control(name="b", type_name="Button", location_x=300, location_y=200),
        ],
    )
    result = infer_container_panel(ctrl)
    assert result["panel_type"] == "Grid"
    assert result["orientation"] is None
    assert "Margin" in result["rationale"]


def test_infer_vertical_chain_is_stackpanel():
    """Children aligned in one column stay a vertical StackPanel."""
    ctrl = Control(
        name="groupBox1",
        type_name="System.Windows.Forms.GroupBox",
        children=[
            Control(name="a", type_name="RadioButton", location_x=2, location_y=34),
            Control(name="b", type_name="RadioButton", location_x=2, location_y=64),
            Control(name="c", type_name="RadioButton", location_x=2, location_y=94),
        ],
    )
    result = infer_container_panel(ctrl)
    assert result["panel_type"] == "StackPanel"
    assert result["orientation"] == "Vertical"
