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


def test_parse_modern_style_without_this_qualifier():
    """Modern designer files that omit `this.` must parse identically."""
    fixture = get_fixture_path("07_modern_style.Designer.cs")
    tree = parse_designer_cs(fixture)

    # Form-level properties
    assert tree.root is not None
    assert tree.root.text == "現代風格表單"
    assert tree.root.name == "Form7"
    assert tree.root.size_w == 320.0
    assert tree.root.size_h == 240.0

    # Control properties
    group = tree.get_control("groupBox1")
    assert group is not None
    assert group.text == "站號"
    assert group.location_x == 12.0
    assert group.location_y == 12.0
    assert group.size_w == 280.0
    assert group.size_h == 120.0

    button = tree.get_control("button1")
    assert button is not None
    assert button.text == "送出"
    assert button.location_x == 20.0

    # Hierarchy: form -> group box -> button/label
    assert group.parent_name == "Form7"
    assert button.parent_name == "groupBox1"
    assert tree.get_control("label1").parent_name == "groupBox1"

    assert tree.root.children == [group]
    assert [c.name for c in group.children] == ["button1", "label1"]


def test_parse_modern_style_does_not_misread_control_text_as_form_text():
    """A control-level `Text = ...` line must never become the form title."""
    designer = (
        "partial class Form1\n"
        "{\n"
        "    private void InitializeComponent()\n"
        "    {\n"
        "        button1 = new Button();\n"
        '        button1.Text = "按鈕";\n'
        '        Text = "表單";\n'
        "    }\n"
        "    private Button button1;\n"
        "}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "Form1.Designer.cs"
        p.write_text(designer, encoding="utf-8")
        tree = parse_designer_cs(p)
        assert tree.root.text == "表單"
        assert tree.get_control("button1").text == "按鈕"


_TABLE_LAYOUT_DESIGNER = """partial class Form1
{
    private void InitializeComponent()
    {
        tableLayoutPanel1 = new TableLayoutPanel();
        label1 = new Label();
        textBox1 = new TextBox();
        @Q@tableLayoutPanel1.ColumnCount = 2;
        @Q@tableLayoutPanel1.RowCount = 1;
        @Q@tableLayoutPanel1.Controls.Add(@Q@label1, 0, 0);
        @Q@tableLayoutPanel1.Controls.Add(@Q@textBox1, 1, 0);
        @Q@Controls.Add(@Q@tableLayoutPanel1);
    }
    private TableLayoutPanel tableLayoutPanel1;
    private Label label1;
    private TextBox textBox1;
}
"""


def _parse_table_layout(qualifier: str) -> ControlTree:
    designer = _TABLE_LAYOUT_DESIGNER.replace("@Q@", qualifier)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "Form1.Designer.cs"
        p.write_text(designer, encoding="utf-8")
        return parse_designer_cs(p)


def test_parse_three_argument_add_classic_style():
    """`this.x.Controls.Add(this.y, col, row)` must record the cell position."""
    tree = _parse_table_layout("this.")
    grid = tree.get_control("tableLayoutPanel1")
    assert grid.column_count == 2
    assert grid.row_count == 1
    assert [c.name for c in grid.children] == ["label1", "textBox1"]
    label, textbox = grid.children
    assert (label.column, label.row) == (0, 0)
    assert (textbox.column, textbox.row) == (1, 0)


def test_parse_three_argument_add_modern_style():
    """The this-less modern style must record cell positions identically."""
    tree = _parse_table_layout("")
    grid = tree.get_control("tableLayoutPanel1")
    assert grid.column_count == 2
    assert grid.row_count == 1
    assert [c.name for c in grid.children] == ["label1", "textBox1"]
    assert (grid.children[0].column, grid.children[0].row) == (0, 0)
    assert (grid.children[1].column, grid.children[1].row) == (1, 0)


def test_tablelayout_fixture_children_attached():
    """Regression: 05_tablelayout children were orphaned by the 3-arg Add."""
    fixture = get_fixture_path("05_tablelayout.Designer.cs")
    tree = parse_designer_cs(fixture)
    grid = tree.get_control("tableLayoutPanel1")
    assert grid is not None
    assert [c.name for c in grid.children] == ["label1", "textBox1"]
    assert (grid.children[0].column, grid.children[0].row) == (0, 0)
    assert (grid.children[1].column, grid.children[1].row) == (1, 0)


def test_parse_classic_client_size():
    """Classic this-qualified `this.ClientSize = ...` sets the root dimensions."""
    fixture = get_fixture_path("05_tablelayout.Designer.cs")
    tree = parse_designer_cs(fixture)
    assert tree.root is not None
    assert tree.root.size_w == 284.0
    assert tree.root.size_h == 54.0
