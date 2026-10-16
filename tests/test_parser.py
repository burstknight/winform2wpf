"""Unit tests for parser module."""

from __future__ import annotations

from wf2wpf.parser import Control, ControlTree, parse_designer_cs
from tests.conftest import get_fixture_path


def test_control_creation():
    """Test Control dataclass creation."""
    ctrl = Control(name="button1", type_name="System.Windows.Forms.Button")
    assert ctrl.name == "button1"
    assert ctrl.type_name == "System.Windows.Forms.Button"
    assert isinstance(ctrl.children, list)


def test_control_tree_add():
    """Test adding control to tree."""
    tree = ControlTree()
    ctrl = Control(name="label1", type_name="System.Windows.Forms.Label")
    tree.add_control(ctrl)
    assert "label1" in tree.controls


def test_parse_simple_form():
    """Test parsing simple form fixture."""
    fixture = get_fixture_path("01_simple_form.Designer.cs")
    tree = parse_designer_cs(fixture)
    assert isinstance(tree, ControlTree)
