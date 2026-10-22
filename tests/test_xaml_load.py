"""Load-time validation of the rendered XAML against the real WPF parser.

The golden files are parsed with ``System.Windows.Markup.XamlReader`` through
Windows PowerShell 5.1, so a XAML that is well-formed XML but invalid for WPF
(an unknown enum value, a bogus property, ...) fails the test instead of only
showing up when a developer opens the file in Visual Studio.

The whole module is skipped when Windows PowerShell or the WPF assemblies are
not available.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import get_expected_path

CHECK_SCRIPT = Path(__file__).resolve().parent / "xaml_load_check.ps1"
EXPECTED_DIR = Path(__file__).resolve().parent / "expected"

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or shutil.which("powershell.exe") is None,
    reason="loading XAML in WPF requires Windows PowerShell 5.1",
)


def _load_in_wpf(xaml_path: Path) -> subprocess.CompletedProcess[str]:
    """Parse a XAML file with the WPF parser and report the outcome."""
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(CHECK_SCRIPT),
            str(xaml_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_golden_xaml_loads_in_wpf():
    """Every golden file must be loadable by WPF."""
    goldens = sorted(EXPECTED_DIR.glob("*.xaml"))
    assert goldens, "no golden files found"

    for golden in goldens:
        result = _load_in_wpf(golden)
        if result.returncode == 2:
            pytest.skip("WPF assemblies are not available on this machine")
        assert result.returncode == 0, (
            f"WPF refused to load {golden.name}: {result.stdout.strip()}"
        )
