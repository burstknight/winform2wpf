"""Unit tests for mapper module."""

from __future__ import annotations

from wf2wpf import mapper


def test_map_control_type_form():
    """Test mapping Form."""
    assert mapper.map_control_type("System.Windows.Forms.Form") == "Window"


def test_map_control_type_button():
    """Test mapping Button."""
    assert mapper.map_control_type("System.Windows.Forms.Button") == "Button"


def test_map_control_type_flowlayout():
    """Test mapping FlowLayoutPanel."""
    assert mapper.map_control_type("System.Windows.Forms.FlowLayoutPanel") == "WrapPanel"


def test_map_control_type_tablelayout():
    """Test mapping TableLayoutPanel."""
    assert mapper.map_control_type("System.Windows.Forms.TableLayoutPanel") == "Grid"


def test_load_rules():
    """Test loading rules."""
    rules = mapper.load_rules()
    assert isinstance(rules, dict)
