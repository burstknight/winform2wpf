"""Integration tests using synthetic fixtures and golden files."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from wf2wpf.analyzer import analyze_tree
from wf2wpf.parser import parse_designer_cs
from wf2wpf.renderer import render_xaml
from tests.conftest import get_fixture_path, get_expected_path


def test_integration_simple_form():
    """Integration test for 01_simple_form."""
    fixture = get_fixture_path("01_simple_form.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)

    # Structural assertions
    assert "<Window" in xaml
    assert "x:Name=\"Form1\"" in xaml
    assert "Title=\"Login\"" in xaml
    assert "<StackPanel" in xaml or "<Grid" in xaml
    assert "x:Name=\"label1\"" in xaml
    assert "x:Name=\"textBox1\"" in xaml
    assert "x:Name=\"button1\"" in xaml

    # XML parseable
    ET.fromstring(xaml)


def test_integration_horizontal_buttons():
    """Integration test for 02_horizontal_buttons."""
    fixture = get_fixture_path("02_horizontal_buttons.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)
    assert "<Window" in xaml
    assert "x:Name=\"Form2\"" in xaml
    assert "StackPanel" in xaml
    assert "Orientation=\"Horizontal\"" in xaml
    ET.fromstring(xaml)


def test_integration_dockpanel_like():
    """Integration test for 03_dockpanel_like."""
    fixture = get_fixture_path("03_dockpanel_like.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)
    assert "<Window" in xaml
    ET.fromstring(xaml)


def test_integration_flowlayout():
    """Integration test for 04_flowlayout."""
    fixture = get_fixture_path("04_flowlayout.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)
    assert "<Window" in xaml
    ET.fromstring(xaml)


def test_integration_tablelayout():
    """Integration test for 05_tablelayout."""
    fixture = get_fixture_path("05_tablelayout.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)
    assert "<Window" in xaml
    ET.fromstring(xaml)


def test_integration_nested_panel():
    """Integration test for 06_nested_panel."""
    fixture = get_fixture_path("06_nested_panel.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)
    assert "<Window" in xaml
    ET.fromstring(xaml)


def test_integration_modern_style():
    """Modern this-less designer files must render a full tree, not an empty window."""
    fixture = get_fixture_path("07_modern_style.Designer.cs")
    tree = parse_designer_cs(fixture)
    decisions = analyze_tree(tree)
    xaml = render_xaml(tree, decisions)

    assert "Title=\"現代風格表單\"" in xaml
    assert "x:Name=\"groupBox1\"" in xaml
    assert "x:Name=\"button1\"" in xaml
    assert "x:Name=\"label1\"" in xaml
    assert "Content=\"送出\"" in xaml

    root = ET.fromstring(xaml)
    names = [elem.get("{http://schemas.microsoft.com/winfx/2006/xaml}Name") for elem in root.iter()]
    assert "groupBox1" in names
    assert "button1" in names
    assert "label1" in names
