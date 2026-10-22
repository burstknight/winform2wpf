"""Unit tests for the style translation module."""

from __future__ import annotations

from wf2wpf.styles import to_wpf_brush, to_wpf_font


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


def test_font_family_size_and_style():
    """A font expression becomes the WPF text properties."""
    attributes = to_wpf_font(
        'new Font("Microsoft JhengHei UI", 16F, FontStyle.Regular, '
        "GraphicsUnit.Point)"
    )
    assert attributes == {
        "FontFamily": "Microsoft JhengHei UI",
        "FontSize": "21.33",
    }


def test_font_size_converts_points_to_dip():
    """WinForms measures in points, WPF in 1/96 inch, so the size is scaled."""
    attributes = to_wpf_font('new Font("Arial", 12F)')
    assert attributes["FontSize"] == "16"


def test_font_size_keeps_pixel_units():
    """A font given in pixels is already a device independent size."""
    attributes = to_wpf_font(
        'new Font("Arial", 20F, FontStyle.Regular, GraphicsUnit.Pixel)'
    )
    assert attributes["FontSize"] == "20"


def test_font_bold_and_italic():
    """The bold and italic flags map onto the matching WPF properties."""
    attributes = to_wpf_font(
        'new Font("Arial", 10F, FontStyle.Bold | FontStyle.Italic)'
    )
    assert attributes["FontWeight"] == "Bold"
    assert attributes["FontStyle"] == "Italic"


def test_font_with_namespaced_style_flags():
    """The designer may qualify the FontStyle enum with its namespace."""
    attributes = to_wpf_font(
        'new System.Drawing.Font("Arial", 9.75F, '
        "System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic)"
    )
    assert attributes["FontWeight"] == "Bold"
    assert attributes["FontStyle"] == "Italic"


def test_unparsable_font_is_ignored():
    """An expression that is not a font must not produce any property."""
    assert to_wpf_font("garbage") == {}
    assert to_wpf_font("") == {}
    assert to_wpf_font(None) == {}
