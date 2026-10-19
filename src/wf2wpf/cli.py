"""Command-line interface for wf2wpf."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wf2wpf import __version__
from wf2wpf.analyzer import analyze_tree
from wf2wpf.io import (
    DEFAULT_FALLBACK_ENCODINGS,
    DefaultTextFileEncodingDetector,
    MappingTextFileEncodingDetector,
    TextFileReader,
)
from wf2wpf.parser import parse_designer_cs
from wf2wpf.renderer import render_xaml
from wf2wpf.report import generate_report


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert WinForms Designer.cs to WPF XAML with layout inference"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"wf2wpf {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert WinForms Designer.cs to WPF XAML",
    )
    convert_parser.add_argument(
        "input",
        help="Path to Designer.cs file",
    )
    convert_parser.add_argument(
        "--output",
        "-o",
        help="Output XAML path (default: input with .xaml extension)",
    )
    convert_parser.add_argument(
        "--report",
        action="store_true",
        help="Generate and print conversion report",
    )
    convert_parser.add_argument(
        "--report-format",
        choices=["text", "json"],
        default="text",
        help="Report format (default: text)",
    )
    convert_parser.add_argument(
        "--src-encoding",
        default="auto",
        help=(
            "Force the source file encoding instead of auto-detecting "
            "(e.g. utf-8, big5, cp950; default: auto)"
        ),
    )
    convert_parser.add_argument(
        "--encoding-fallbacks",
        help=(
            "Comma-separated fallback encodings tried during auto-detection "
            f"(default: {','.join(DEFAULT_FALLBACK_ENCODINGS)})"
        ),
    )
    convert_parser.add_argument(
        "--encoding-map",
        action="append",
        default=[],
        metavar="GLOB=ENCODING",
        help=(
            "Force the encoding for paths matching a glob pattern; may be "
            'repeated (e.g. --encoding-map "**/*.Designer.cs=big5")'
        ),
    )
    convert_parser.add_argument(
        "--encoding-report",
        action="store_true",
        help="Print the detected encoding for the input file",
    )

    args = parser.parse_args()

    if args.command == "convert":
        _handle_convert(args)
    else:
        parser.print_help()


def _build_reader(args: argparse.Namespace) -> TextFileReader:
    """Build a text reader from the encoding-related CLI options."""
    forced = None if args.src_encoding.lower() == "auto" else args.src_encoding

    fallbacks = None
    if args.encoding_fallbacks:
        fallbacks = [name.strip() for name in args.encoding_fallbacks.split(",") if name.strip()]

    detector = DefaultTextFileEncodingDetector(
        forced_encoding=forced,
        fallback_encoding_names=fallbacks,
    )

    if args.encoding_map:
        mappings = []
        for item in args.encoding_map:
            pattern, _, encoding = item.partition("=")
            if not pattern or not encoding:
                print(
                    f"Error: invalid --encoding-map value '{item}' (expected GLOB=ENCODING)",
                    file=sys.stderr,
                )
                sys.exit(1)
            mappings.append((pattern, encoding.strip()))
        detector = MappingTextFileEncodingDetector(mappings, fallback_detector=detector)

    return TextFileReader(detector)


def _handle_convert(args: argparse.Namespace) -> None:
    """Handle convert command."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path:
        output_path = input_path.with_suffix(".xaml")

    try:
        reader = _build_reader(args)

        if args.encoding_report:
            _, detected = reader.read_all_text_with_detection(input_path)
            print(f"Encoding: {input_path} -> {detected.name} ({detected.reason.value})")

        # Parse
        tree = parse_designer_cs(input_path, reader=reader)

        # Analyze
        decisions = analyze_tree(tree)

        # Render
        render_xaml(tree, decisions, output_path)

        # Report
        if args.report:
            report = generate_report(tree=tree, decisions=decisions)
            if args.report_format == "json":
                import json

                print(json.dumps(report.to_json(), indent=2))
            else:
                print(report.to_text())

        print(f"Converted: {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
