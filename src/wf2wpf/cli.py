"""Command-line interface for wf2wpf."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wf2wpf import __version__
from wf2wpf.analyzer import analyze_tree
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

    args = parser.parse_args()

    if args.command == "convert":
        _handle_convert(args)
    else:
        parser.print_help()


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
        # Parse
        tree = parse_designer_cs(input_path)

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
