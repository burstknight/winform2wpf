"""Unit tests for renderer module."""

from __future__ import annotations

import xml.etree.ElementTree as ET

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
