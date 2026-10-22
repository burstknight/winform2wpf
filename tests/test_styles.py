"""Unit tests for the style translation module."""

from __future__ import annotations

from wf2wpf.styles import to_wpf_brush


def test_named_color_becomes_hex():
    """A named WinForms colour keeps its exact .NET value."""
    assert to_wpf_brush("Color.Green") == "#FF008000"
    assert to_wpf_brush("Color.Red") == "#FFFF0000"
    assert to_wpf_brush("Color.Yellow") == "#FFFFFF00"
    assert to_wpf_brush("Color.Blue") == "#FF0000FF"


def test_named_color_accepts_the_drawing_namespace():
    """The designer may write the colour with its full namespace."""
    assert to_wpf_brush("System.Drawing.Color.Green") == "#FF008000"


def test_from_argb_with_three_channels():
    """Color.FromArgb(r, g, b) is opaque."""
    assert to_wpf_brush("Color.FromArgb(255, 192, 0)") == "#FFFFC000"


def test_from_argb_with_four_channels():
    """Color.FromArgb(a, r, g, b) keeps the alpha channel."""
    assert to_wpf_brush("Color.FromArgb(128, 10, 20, 30)") == "#800A141E"


def test_from_argb_with_designer_casts():
    """The designer writes colours as ((int)(((byte)(240)))); the casts vanish."""
    expression = (
        "System.Drawing.Color.FromArgb(((int)(((byte)(255)))), "
        "((int)(((byte)(192)))), ((int)(((byte)(0))))"
    )
    assert to_wpf_brush(expression) == "#FFFFC000"


def test_from_argb_with_alpha_and_named_color():
    """Color.FromArgb(alpha, Color.X) combines both values."""
    assert to_wpf_brush("Color.FromArgb(200, Color.Red)") == "#C8FF0000"


def test_system_color_becomes_a_system_brush():
    """A system colour follows the Windows theme, so a brush key is used."""
    assert to_wpf_brush("SystemColors.ControlText") == (
        "{DynamicResource {x:Static SystemColors.ControlTextBrushKey}}"
    )
    assert to_wpf_brush("SystemColors.WindowText") == (
        "{DynamicResource {x:Static SystemColors.WindowTextBrushKey}}"
    )


def test_empty_and_unknown_colors_are_skipped():
    """Colour.Empty and unknown names must not produce a brush value."""
    assert to_wpf_brush("Color.Empty") is None
    assert to_wpf_brush("Color.NotAColor") is None
    assert to_wpf_brush("") is None
    assert to_wpf_brush(None) is None

