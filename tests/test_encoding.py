"""Unit tests for encoding module."""

from __future__ import annotations

import tempfile
from pathlib import Path

from wf2wpf.io import (
    DefaultTextFileEncodingDetector,
    MappingTextFileEncodingDetector,
    TextFileEncodingReason,
    TextFileReader,
    normalize_encoding_name,
)


def _write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def test_encoding_ascii_utf8_strict():
    detector = DefaultTextFileEncodingDetector()
    data = b"class Form1 { }"
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.UTF8_STRICT


def test_encoding_utf8_bom():
    detector = DefaultTextFileEncodingDetector()
    data = b"\xef\xbb\xbf// \xe8\xa1\xa8\xe5\x8d\x95\n"
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.BOM


def test_encoding_utf8_nobom():
    detector = DefaultTextFileEncodingDetector()
    data = "// \xe8\xa1\xa8\xe5\x8d\x95\n".encode("utf-8")
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.UTF8_STRICT


def test_encoding_big5():
    detector = DefaultTextFileEncodingDetector()
    data = "// 表單\n".encode("big5")
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.BIG5


def test_encoding_cp950():
    detector = DefaultTextFileEncodingDetector(fallback_encoding_names=["cp950", "big5"])
    data = "Label: 窗口\n".encode("cp950")
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.CP950


def test_encoding_forced():
    detector = DefaultTextFileEncodingDetector(forced_encoding="big5")
    data = b"some data"
    result = detector.detect(bytes_data=data)
    assert result.reason == TextFileEncodingReason.FORCED


def test_reader_reads_big5():
    data = "// 表單\n".encode("big5")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.cs"
        p.write_bytes(data)
        reader = TextFileReader()
        content, detected = reader.read_all_text_with_detection(p)
        assert detected.reason == TextFileEncodingReason.BIG5
        assert "表單" in content


def test_reader_reads_utf8_bom():
    data = b"\xef\xbb\xbfnamespace Test {}\n"
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.cs"
        p.write_bytes(data)
        reader = TextFileReader()
        content, detected = reader.read_all_text_with_detection(p)
        assert detected.reason == TextFileEncodingReason.BOM
        assert "namespace" in content


def test_encoding_name_aliases():
    assert normalize_encoding_name("UTF-8") == "utf-8"
    assert normalize_encoding_name("Big5") == "big5"
    assert normalize_encoding_name("MS950") == "cp950"


def test_forced_encoding_skips_detection():
    detector = DefaultTextFileEncodingDetector(forced_encoding="big5")
    result = detector.detect(bytes_data=b"\xef\xbb\xbfhello")
    assert result.name == "big5"
    assert result.reason == TextFileEncodingReason.FORCED


def test_mapping_detector_forces_matching_path():
    inner = DefaultTextFileEncodingDetector()
    detector = MappingTextFileEncodingDetector([("**/Form1.Designer.cs", "cp950")], inner)
    matched = detector.detect(path="C:/src/Form1.Designer.cs", bytes_data=b"hello")
    assert matched.name == "cp950"
    assert matched.reason == TextFileEncodingReason.FORCED


def test_mapping_detector_delegates_non_matching_path():
    inner = DefaultTextFileEncodingDetector()
    detector = MappingTextFileEncodingDetector([("**/Other.cs", "cp950")], inner)
    result = detector.detect(path="C:/src/Form1.Designer.cs", bytes_data=b"hello")
    assert result.reason == TextFileEncodingReason.UTF8_STRICT


def test_fallback_disabled_uses_utf8():
    detector = DefaultTextFileEncodingDetector(fallback_encoding_names=[])
    result = detector.detect(bytes_data="中文".encode("big5"))
    assert result.name == "utf-8"
