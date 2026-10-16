"""Shared test fixtures and helpers."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for tests
SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def get_fixture_path(name: str) -> Path:
    """Get path to fixture file."""
    return Path(__file__).resolve().parent / "fixtures" / name


def get_expected_path(name: str) -> Path:
    """Get path to expected file."""
    return Path(__file__).resolve().parent / "expected" / name
