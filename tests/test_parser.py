"""Unit tests for parser module."""

from __future__ import annotations

import tempfile
from pathlib import Path

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


_BIG5_DESIGNER = """partial class Form1
{
    private System.Windows.Forms.Label label1;
    private void InitializeComponent()
    {
        this.label1 = new System.Windows.Forms.Label();
        this.label1.Name = "label1";
        this.label1.Text = "登入";
        this.Name = "Form1";
        this.Text = "程式入口";
    }
}
"""


def test_parse_big5_designer_preserves_chinese():
    """Chinese literals in a Big5-encoded Designer.cs must survive parsing."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "Form1.Designer.cs"
        p.write_bytes(_BIG5_DESIGNER.encode("big5"))
        tree = parse_designer_cs(p)
        assert tree.root is not None
        assert tree.root.text == "程式入口"
        assert tree.get_control("label1").text == "登入"
