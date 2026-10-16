"""Conversion report generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

try:
    from rich.console import Console
    from rich.table import Table

    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False


ReportFormat = Literal["text", "json"]


@dataclass
class ConversionReport:
    """Conversion report."""

    converted: list[dict[str, Any]] = field(default_factory=list)
    needs_review: list[dict[str, Any]] = field(default_factory=list)
    unmapped: list[dict[str, Any]] = field(default_factory=list)
    layout_decisions: dict[str, dict[str, Any]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        """Format report as text."""
        lines: list[str] = []
        lines.append("# Conversion Report")
        lines.append("")
        lines.append(f"Converted: {len(self.converted)}")
        lines.append(f"Needs Review: {len(self.needs_review)}")
        lines.append(f"Unmapped: {len(self.unmapped)}")
        lines.append(f"Warnings: {len(self.warnings)}")
        lines.append("")
        if self.layout_decisions:
            lines.append("## Layout Decisions")
            for name, decision in self.layout_decisions.items():
                panel = decision.get("panel_type", "Unknown")
                rationale = decision.get("rationale", "")
                lines.append(f"- {name}: {panel} ({rationale})")
        return "\n".join(lines)

    def to_json(self) -> dict[str, Any]:
        """Format report as JSON-compatible dict."""
        return {
            "converted": self.converted,
            "needs_review": self.needs_review,
            "unmapped": self.unmapped,
            "layout_decisions": self.layout_decisions,
            "warnings": self.warnings,
        }


def generate_report(
    tree: Any = None,
    decisions: dict[str, dict[str, Any]] | None = None,
    **kwargs: Any,
) -> ConversionReport:
    """Generate conversion report.

    Args:
        tree: Control tree.
        decisions: Layout decisions.
        **kwargs: Additional data.

    Returns:
        ConversionReport instance.
    """
    report = ConversionReport()
    if decisions:
        report.layout_decisions = decisions
    return report
