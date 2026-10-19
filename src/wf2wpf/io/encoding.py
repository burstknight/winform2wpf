"""Text file encoding detection utilities.

Traditional Chinese WinForms projects are frequently stored in Big5/CP950
rather than UTF-8, which produces mojibake if the source is read as UTF-8.
This module resolves the input encoding before parsing so Chinese literals
survive the conversion. Output files are always written as UTF-8 (no BOM).

Detection order:

1. Forced encoding (explicit user override)
2. BOM (UTF-8, UTF-16 LE/BE)
3. Strict UTF-8 (no BOM)
4. Fallback encodings (default: Big5, then CP950)
"""

from __future__ import annotations

import codecs
import fnmatch
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

DEFAULT_FALLBACK_ENCODINGS = ("big5", "cp950")


class TextFileEncodingReason(str, Enum):
    """Reason an encoding was selected."""

    FORCED = "Forced"
    BOM = "Bom"
    UTF8_STRICT = "Utf8Strict"
    BIG5 = "Big5"
    CP950 = "Cp950"


@dataclass(frozen=True)
class TextFileEncoding:
    """Resolved text encoding and the reason it was selected."""

    encoding: str
    reason: TextFileEncodingReason

    @property
    def name(self) -> str:
        """Python codec name, e.g. ``big5`` or ``utf-8``."""
        return self.encoding


def normalize_encoding_name(name: str) -> str:
    """Map a user-friendly encoding name to a Python codec name."""
    name_lower = name.strip().lower()
    aliases = {
        "utf-8": "utf-8",
        "utf8": "utf-8",
        "utf-8-sig": "utf-8-sig",
        "utf8-sig": "utf-8-sig",
        "big5": "big5",
        "big-5": "big5",
        "big5-tw": "big5",
        "big5hkscs": "big5",
        "cp950": "cp950",
        "ms950": "cp950",
        "windows-950": "cp950",
        "utf-16": "utf-16",
        "utf-16-le": "utf-16-le",
        "utf-16-be": "utf-16-be",
    }
    return aliases.get(name_lower, name_lower)


def reason_for_encoding_name(name: str) -> TextFileEncodingReason:
    """Classify a configured encoding name as a Big5 or CP950 detection."""
    if normalize_encoding_name(name) == "cp950":
        return TextFileEncodingReason.CP950
    return TextFileEncodingReason.BIG5


def validate_encoding_name(name: str) -> str:
    """Normalize an encoding name and ensure Python supports it."""
    normalized = normalize_encoding_name(name)
    try:
        codecs.lookup(normalized)
    except LookupError as exc:
        raise ValueError(f"Unknown encoding: {name}") from exc
    return normalized


class ITextFileEncodingDetector(ABC):
    """Interface for text file encoding detection."""

    @abstractmethod
    def detect(
        self,
        path: Union[str, Path] | None = None,
        bytes_data: Optional[bytes] = None,
    ) -> TextFileEncoding:
        """Detect the encoding of a file or byte buffer."""
        raise NotImplementedError


class DefaultTextFileEncodingDetector(ITextFileEncodingDetector):
    """Detect encoding for traditional Chinese WinForms source files."""

    def __init__(
        self,
        forced_encoding: Optional[str] = None,
        fallback_encoding_names: Optional[Iterable[str]] = None,
        include_utf16_bom: bool = True,
    ) -> None:
        """Initialize the detector.

        Args:
            forced_encoding: When set, always use this encoding (skips auto-detect).
            fallback_encoding_names: Ordered fallback list (default: big5, cp950).
            include_utf16_bom: Whether to honor UTF-16 BOMs.
        """
        self.forced_encoding = validate_encoding_name(forced_encoding) if forced_encoding else None
        if fallback_encoding_names is None:
            self.fallback_encoding_names = list(DEFAULT_FALLBACK_ENCODINGS)
        else:
            self.fallback_encoding_names = [
                validate_encoding_name(n) for n in fallback_encoding_names if n and n.strip()
            ]
        self.include_utf16_bom = include_utf16_bom

    def detect(
        self,
        path: Union[str, Path] | None = None,
        bytes_data: Optional[bytes] = None,
    ) -> TextFileEncoding:
        """Detect encoding from a path or byte buffer."""
        if bytes_data is None:
            if path is None:
                raise ValueError("Either path or bytes_data must be provided")
            bytes_data = Path(path).read_bytes()

        # 1. Explicit override wins over everything.
        if self.forced_encoding:
            return TextFileEncoding(self.forced_encoding, TextFileEncodingReason.FORCED)

        # 2. BOM is authoritative.
        bom = self._detect_bom(bytes_data)
        if bom is not None:
            return bom

        # 3. Only treat a file as UTF-8 when the entire stream decodes cleanly.
        if self._is_strict_utf8(bytes_data):
            return TextFileEncoding("utf-8", TextFileEncodingReason.UTF8_STRICT)

        # 4. Regional fallbacks, first clean decode wins.
        for name in self.fallback_encoding_names:
            if self._decodes_cleanly(bytes_data, name):
                return TextFileEncoding(name, reason_for_encoding_name(name))

        # 5. Nothing decoded cleanly; use the first fallback with replacement
        # characters so the pipeline continues instead of aborting.
        if self.fallback_encoding_names:
            name = self.fallback_encoding_names[0]
            return TextFileEncoding(name, reason_for_encoding_name(name))
        return TextFileEncoding("utf-8", TextFileEncodingReason.UTF8_STRICT)

    def _detect_bom(self, data: bytes) -> Optional[TextFileEncoding]:
        if data.startswith(b"\xef\xbb\xbf"):
            return TextFileEncoding("utf-8-sig", TextFileEncodingReason.BOM)
        if self.include_utf16_bom:
            if data.startswith(b"\xff\xfe"):
                return TextFileEncoding("utf-16-le", TextFileEncodingReason.BOM)
            if data.startswith(b"\xfe\xff"):
                return TextFileEncoding("utf-16-be", TextFileEncodingReason.BOM)
        return None

    @staticmethod
    def _is_strict_utf8(data: bytes) -> bool:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return False
        return True

    @staticmethod
    def _decodes_cleanly(data: bytes, encoding: str) -> bool:
        try:
            data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            return False
        return True


class MappingTextFileEncodingDetector(ITextFileEncodingDetector):
    """Force an encoding for paths matching glob patterns, else auto-detect."""

    def __init__(
        self,
        mappings: Sequence[tuple[str, str]],
        fallback_detector: Optional[ITextFileEncodingDetector] = None,
    ) -> None:
        self.mappings = [(pattern, normalize_encoding_name(enc)) for pattern, enc in mappings]
        self.fallback_detector = fallback_detector or DefaultTextFileEncodingDetector()

    def detect(
        self,
        path: Union[str, Path] | None = None,
        bytes_data: Optional[bytes] = None,
    ) -> TextFileEncoding:
        if path is not None:
            normalized = str(path).replace("\\", "/")
            for pattern, encoding in self.mappings:
                if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(Path(normalized).name, pattern):
                    return TextFileEncoding(encoding, TextFileEncodingReason.FORCED)
        return self.fallback_detector.detect(path=path, bytes_data=bytes_data)


class TextFileReader:
    """Read text files using encoding detection, avoiding mojibake."""

    def __init__(self, detector: Optional[ITextFileEncodingDetector] = None) -> None:
        self.detector = detector or DefaultTextFileEncodingDetector()

    def read_all_text_with_detection(
        self, path: Union[str, Path]
    ) -> tuple[str, TextFileEncoding]:
        """Read a file and return its content plus the detected encoding."""
        path = Path(path)
        bytes_data = path.read_bytes()
        detected = self.detector.detect(path=path, bytes_data=bytes_data)
        return bytes_data.decode(detected.encoding), detected

    def read_all_text(self, path: Union[str, Path]) -> str:
        """Read a file as text using encoding detection."""
        return self.read_all_text_with_detection(path)[0]
