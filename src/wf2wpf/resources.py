"""Resource handling for .resx files.

This module provides minimal skeleton for future .resx handling.
Resources (images, icons) are not fully processed in MVP.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


def parse_resx(path: str | Path) -> dict[str, Any]:
    """Parse .resx file.

    Args:
        path: Path to .resx file.

    Returns:
        Dictionary of resources.

    Note:
        MVP implementation is a placeholder. Full implementation TBD.
    """
    # TODO: Implement .resx parsing for images/icons
    return {}
