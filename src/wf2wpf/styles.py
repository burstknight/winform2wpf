"""WinForms colour expressions translated into WPF values.

The WinForms designer stores colours as C# expressions (``Color.Green``,
``System.Drawing.Color.FromArgb(...)``). This module turns those expressions
into the brush values WPF understands for ``Foreground`` and ``Background``.
"""

from __future__ import annotations

import re
from typing import Optional

__all__ = ["to_wpf_brush"]


# The .NET known colours. Their names and values are identical to the WPF
# colour names, so a WinForms colour maps one to one onto a WPF brush.
KNOWN_COLORS: dict[str, str] = {
    "AliceBlue": "#FFF0F8FF",
    "AntiqueWhite": "#FFFAEBD7",
    "Aqua": "#FF00FFFF",
    "Aquamarine": "#FF7FFFD4",
    "Azure": "#FFF0FFFF",
    "Beige": "#FFF5F5DC",
    "Bisque": "#FFFFE4C4",
    "Black": "#FF000000",
    "BlanchedAlmond": "#FFFFEBCD",
    "Blue": "#FF0000FF",
    "BlueViolet": "#FF8A2BE2",
    "Brown": "#FFA52A2A",
    "BurlyWood": "#FFDEB887",
    "CadetBlue": "#FF5F9EA0",
    "Chartreuse": "#FF7FFF00",
    "Chocolate": "#FFD2691E",
    "Coral": "#FFFF7F50",
    "CornflowerBlue": "#FF6495ED",
    "Cornsilk": "#FFFFF8DC",
    "Crimson": "#FFDC143C",
    "Cyan": "#FF00FFFF",
    "DarkBlue": "#FF00008B",
    "DarkCyan": "#FF008B8B",
    "DarkGoldenrod": "#FFB8860B",
    "DarkGray": "#FFA9A9A9",
    "DarkGreen": "#FF006400",
    "DarkKhaki": "#FFBDB76B",
    "DarkMagenta": "#FF8B008B",
    "DarkOliveGreen": "#FF556B2F",
    "DarkOrange": "#FFFF8C00",
    "DarkOrchid": "#FF9932CC",
    "DarkRed": "#FF8B0000",
    "DarkSalmon": "#FFE9967A",
    "DarkSeaGreen": "#FF8FBC8B",
    "DarkSlateBlue": "#FF483D8B",
    "DarkSlateGray": "#FF2F4F4F",
    "DarkTurquoise": "#FF00CED1",
    "DarkViolet": "#FF9400D3",
    "DeepPink": "#FFFF1493",
    "DeepSkyBlue": "#FF00BFFF",
    "DimGray": "#FF696969",
    "DodgerBlue": "#FF1E90FF",
    "Firebrick": "#FFB22222",
    "FloralWhite": "#FFFFFAF0",
    "ForestGreen": "#FF228B22",
    "Fuchsia": "#FFFF00FF",
    "Gainsboro": "#FFDCDCDC",
    "GhostWhite": "#FFF8F8FF",
    "Gold": "#FFFFD700",
    "Goldenrod": "#FFDAA520",
    "Gray": "#FF808080",
    "Green": "#FF008000",
    "GreenYellow": "#FFADFF2F",
    "Honeydew": "#FFF0FFF0",
    "HotPink": "#FFFF69B4",
    "IndianRed": "#FFCD5C5C",
    "Indigo": "#FF4B0082",
    "Ivory": "#FFFFFFF0",
    "Khaki": "#FFF0E68C",
    "Lavender": "#FFE6E6FA",
    "LavenderBlush": "#FFFFF0F5",
    "LawnGreen": "#FF7CFC00",
    "LemonChiffon": "#FFFFFACD",
    "LightBlue": "#FFADD8E6",
    "LightCoral": "#FFF08080",
    "LightCyan": "#FFE0FFFF",
    "LightGoldenrodYellow": "#FFFAFAD2",
    "LightGray": "#FFD3D3D3",
    "LightGreen": "#FF90EE90",
    "LightPink": "#FFFFB6C1",
    "LightSalmon": "#FFFFA07A",
    "LightSeaGreen": "#FF20B2AA",
    "LightSkyBlue": "#FF87CEFA",
    "LightSlateGray": "#FF778899",
    "LightSteelBlue": "#FFB0C4DE",
    "LightYellow": "#FFFFFFE0",
    "Lime": "#FF00FF00",
    "LimeGreen": "#FF32CD32",
    "Linen": "#FFFAF0E6",
    "Magenta": "#FFFF00FF",
    "Maroon": "#FF800000",
    "MediumAquamarine": "#FF66CDAA",
    "MediumBlue": "#FF0000CD",
    "MediumOrchid": "#FFBA55D3",
    "MediumPurple": "#FF9370DB",
    "MediumSeaGreen": "#FF3CB371",
    "MediumSlateBlue": "#FF7B68EE",
    "MediumSpringGreen": "#FF00FA9A",
    "MediumTurquoise": "#FF48D1CC",
    "MediumVioletRed": "#FFC71585",
    "MidnightBlue": "#FF191970",
    "MintCream": "#FFF5FFFA",
    "MistyRose": "#FFFFE4E1",
    "Moccasin": "#FFFFE4B5",
    "NavajoWhite": "#FFFFDEAD",
    "Navy": "#FF000080",
    "OldLace": "#FFFDF5E6",
    "Olive": "#FF808000",
    "OliveDrab": "#FF6B8E23",
    "Orange": "#FFFFA500",
    "OrangeRed": "#FFFF4500",
    "Orchid": "#FFDA70D6",
    "PaleGoldenrod": "#FFEEE8AA",
    "PaleGreen": "#FF98FB98",
    "PaleTurquoise": "#FFAFEEEE",
    "PaleVioletRed": "#FFDB7093",
    "PapayaWhip": "#FFFFEFD5",
    "PeachPuff": "#FFFFDAB9",
    "Peru": "#FFCD853F",
    "Pink": "#FFFFC0CB",
    "Plum": "#FFDDA0DD",
    "PowderBlue": "#FFB0E0E6",
    "Purple": "#FF800080",
    "Red": "#FFFF0000",
    "RosyBrown": "#FFBC8F8F",
    "RoyalBlue": "#FF4169E1",
    "SaddleBrown": "#FF8B4513",
    "Salmon": "#FFFA8072",
    "SandyBrown": "#FFF4A460",
    "SeaGreen": "#FF2E8B57",
    "SeaShell": "#FFFFF5EE",
    "Sienna": "#FFA0522D",
    "Silver": "#FFC0C0C0",
    "SkyBlue": "#FF87CEEB",
    "SlateBlue": "#FF6A5ACD",
    "SlateGray": "#FF708090",
    "Snow": "#FFFFFAFA",
    "SpringGreen": "#FF00FF7F",
    "SteelBlue": "#FF4682B4",
    "Tan": "#FFD2B48C",
    "Teal": "#FF008080",
    "Thistle": "#FFD8BFD8",
    "Tomato": "#FFFF6347",
    "Transparent": "#00FFFFFF",
    "Turquoise": "#FF40E0D0",
    "Violet": "#FFEE82EE",
    "Wheat": "#FFF5DEB3",
    "White": "#FFFFFFFF",
    "WhiteSmoke": "#FFF5F5F5",
    "Yellow": "#FFFFFF00",
    "YellowGreen": "#FF9ACD32",
}


# WinForms SystemColors members and the WPF system brush with the same name.
# A WPF system brush follows the current Windows theme, just like the WinForms
# system colour, so the XAML refers to it instead of freezing a hex value.
SYSTEM_COLOR_BRUSHES: dict[str, str] = {
    "ActiveBorder": "ActiveBorderBrushKey",
    "ActiveCaption": "ActiveCaptionBrushKey",
    "ActiveCaptionText": "ActiveCaptionTextBrushKey",
    "AppWorkspace": "AppWorkspaceBrushKey",
    "Control": "ControlBrushKey",
    "ControlDark": "ControlDarkBrushKey",
    "ControlDarkDark": "ControlDarkDarkBrushKey",
    "ControlLight": "ControlLightBrushKey",
    "ControlLightLight": "ControlLightLightBrushKey",
    "ControlText": "ControlTextBrushKey",
    "Desktop": "DesktopBrushKey",
    "GradientActiveCaption": "GradientActiveCaptionBrushKey",
    "GradientInactiveCaption": "GradientInactiveCaptionBrushKey",
    "GrayText": "GrayTextBrushKey",
    "Highlight": "HighlightBrushKey",
    "HighlightText": "HighlightTextBrushKey",
    "HotTrack": "HotTrackBrushKey",
    "InactiveBorder": "InactiveBorderBrushKey",
    "InactiveCaption": "InactiveCaptionBrushKey",
    "InactiveCaptionText": "InactiveCaptionTextBrushKey",
    "Info": "InfoBrushKey",
    "InfoText": "InfoTextBrushKey",
    "Menu": "MenuBrushKey",
    "MenuBar": "MenuBarBrushKey",
    "MenuHighlight": "MenuHighlightBrushKey",
    "MenuText": "MenuTextBrushKey",
    "ScrollBar": "ScrollBarBrushKey",
    "Window": "WindowBrushKey",
    "WindowFrame": "WindowFrameBrushKey",
    "WindowText": "WindowTextBrushKey",
}


_SYSTEM_COLOR_RE = re.compile(r"^SystemColors\.(?P<name>\w+)$", re.IGNORECASE)
_FROM_ARGB_RE = re.compile(r"^Color\.FromArgb\((?P<args>.*)\)$", re.DOTALL | re.IGNORECASE)
_NAMED_COLOR_RE = re.compile(r"^Color\.(?P<name>\w+)$", re.IGNORECASE)
def _split_arguments(args: str) -> list[str]:
    """Split an argument list on commas that are not nested in parentheses."""
    parts: list[str] = []
    depth = 0
    in_string = False
    current: list[str] = []
    for char in args:
        if char == '"':
            in_string = not in_string
        if not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
        current.append(char)
    parts.append("".join(current).strip())
    return parts


def _parse_int(text: str) -> Optional[int]:
    """Parse an integer argument, tolerating the designer cast noise.

    The designer writes colours as ``((int)(((byte)(240))))``; the casts carry
    no information beyond the number itself.
    """
    stripped = text.strip()
    if re.fullmatch(r"0[xX][0-9A-Fa-f]+", stripped):
        return int(stripped, 16)
    without_casts = re.sub(r"\b(?:int|byte|uint|sbyte)\b", "", stripped)
    without_casts = re.sub(r"[()\s]", "", without_casts)
    if without_casts.isdigit():
        return int(without_casts)
    return None


def _hex(rgb: int, alpha: int = 255) -> str:
    """Format an RGB(A) value as a WPF ``#AARRGGBB`` string."""
    return f"#{alpha:02X}{rgb & 0xFFFFFF:06X}"


def _from_argb(args: str) -> Optional[str]:
    """Translate the arguments of ``Color.FromArgb(...)`` into a brush value."""
    parts = _split_arguments(args)
    if not parts:
        return None

    numbers: list[int] = []
    colors: list[str] = []
    for part in parts:
        number = _parse_int(part)
        if number is None:
            colors.append(part)
        else:
            numbers.append(number)

    if colors:
        base = to_wpf_brush(colors[0])
        if base is None:
            return None
        if not numbers:
            return base
        alpha = max(0, min(255, numbers[0]))
        return f"#{alpha:02X}{base[3:]}"

    if len(numbers) == 3:
        red, green, blue = numbers
        return _hex((red << 16) | (green << 8) | blue)
    if len(numbers) == 4:
        alpha, red, green, blue = numbers
        return _hex((red << 16) | (green << 8) | blue, alpha)
    return None


def to_wpf_brush(expression: Optional[str]) -> Optional[str]:
    """Translate a WinForms colour expression into a WPF brush value.

    Args:
        expression: WinForms colour expression, e.g. ``Color.Green`` or
            ``System.Drawing.Color.FromArgb(255, 0, 0)``.

    Returns:
        A WPF brush value (``#AARRGGBB`` or a ``DynamicResource`` reference)
        or None when the expression cannot be translated.
    """
    if not expression:
        return None

    text = expression.strip().rstrip(";")
    text = re.sub(r"^System\.Drawing\.", "", text)

    system_color = _SYSTEM_COLOR_RE.match(text)
    if system_color:
        key = SYSTEM_COLOR_BRUSHES.get(system_color.group("name"))
        if key is None:
            return None
        return f"{{DynamicResource {{x:Static SystemColors.{key}}}}}"

    from_argb = _FROM_ARGB_RE.match(text)
    if from_argb:
        return _from_argb(from_argb.group("args"))

    named = _NAMED_COLOR_RE.match(text)
    if named:
        name = named.group("name")
        if name.lower() == "empty":
            # Color.Empty means "no colour assigned".
            return None
        return KNOWN_COLORS.get(name)

    return None

