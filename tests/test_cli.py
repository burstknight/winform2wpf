"""Integration tests for the CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from wf2wpf.cli import main

_DESIGNER = """partial class Form1
{
    private System.Windows.Forms.Label label1;
    private void InitializeComponent()
    {
        this.label1 = new System.Windows.Forms.Label();
        this.label1.Name = "label1";
        this.label1.Text = "登入";
        this.Name = "Form1";
        this.Text = "程式入口";
        this.Controls.Add(this.label1);
    }
}
"""


def _run(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["wf2wpf", *argv])
    main()


def test_convert_big5_source_to_utf8(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "Form1.Designer.cs"
    src.write_bytes(_DESIGNER.encode("big5"))
    out = tmp_path / "Form1.xaml"

    _run(["convert", str(src), "-o", str(out)], monkeypatch)

    assert out.exists()
    data = out.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8")
    assert "登入" in text
    assert "程式入口" in text


def test_convert_forced_encoding(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "Form1.Designer.cs"
    src.write_bytes(_DESIGNER.encode("big5"))
    out = tmp_path / "Form1.xaml"

    _run(["convert", str(src), "-o", str(out), "--src-encoding", "big5"], monkeypatch)

    assert "登入" in out.read_text(encoding="utf-8")


def test_unknown_encoding_name_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "Form1.Designer.cs"
    src.write_bytes(_DESIGNER.encode("big5"))
    out = tmp_path / "Form1.xaml"

    # A bogus encoding name should fail fast rather than silently produce a
    # corrupt/empty result.
    with pytest.raises(SystemExit):
        _run(["convert", str(src), "-o", str(out), "--src-encoding", "not-a-codec"], monkeypatch)


def test_invalid_encoding_map_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "Form1.Designer.cs"
    src.write_bytes(_DESIGNER.encode("big5"))
    out = tmp_path / "Form1.xaml"

    with pytest.raises(SystemExit):
        _run(["convert", str(src), "-o", str(out), "--encoding-map", "broken"], monkeypatch)
