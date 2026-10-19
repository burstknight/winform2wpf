"""Input/output utilities."""

from __future__ import annotations

from .encoding import (
    DEFAULT_FALLBACK_ENCODINGS,
    DefaultTextFileEncodingDetector,
    ITextFileEncodingDetector,
    MappingTextFileEncodingDetector,
    TextFileEncoding,
    TextFileEncodingReason,
    TextFileReader,
    normalize_encoding_name,
    reason_for_encoding_name,
    validate_encoding_name,
)

__all__ = [
    "DEFAULT_FALLBACK_ENCODINGS",
    "DefaultTextFileEncodingDetector",
    "ITextFileEncodingDetector",
    "MappingTextFileEncodingDetector",
    "TextFileEncoding",
    "TextFileEncodingReason",
    "TextFileReader",
    "normalize_encoding_name",
    "reason_for_encoding_name",
    "validate_encoding_name",
]
