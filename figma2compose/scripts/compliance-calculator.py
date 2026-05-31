#!/usr/bin/env python3
"""
Figma compliance calculator.

Compares a normalized Figma spec JSON document with a Jetpack Compose Kotlin
implementation and generates a weighted Markdown scorecard.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional


EPSILON = 0.01
WEIGHT_MAP = {
    "100": "Thin",
    "200": "ExtraLight",
    "300": "Light",
    "400": "Normal",
    "500": "Medium",
    "600": "SemiBold",
    "700": "Bold",
    "800": "ExtraBold",
    "900": "Black",
}
LAYOUT_ALIASES = {
    "padding": ["padding"],
    "paddingLeft": ["paddingLeft", "startPadding", "paddingStart"],
    "paddingRight": ["paddingRight", "endPadding", "paddingEnd"],
    "paddingTop": ["paddingTop"],
    "paddingBottom": ["paddingBottom"],
    "gap": ["gap", "spacing", "itemSpacing"],
    "cornerRadius": ["cornerRadius", "radius"],
    "width": ["width"],
    "height": ["height"],
    "statusBarHeight": ["statusBarHeight", "statusBar", "status_bar"],
    "navigationBarHeight": ["navigationBarHeight", "navigationBar", "navigation_bar"],
}


class ComplianceLevel(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    POOR = "POOR"


@dataclass
class ComplianceItem:
    category: str
    item_name: str
    figma_value: str
    compose_value: str
    is_match: bool
    score: int
    max_score: int


@dataclass
class ComplianceReport:
    component_name: str
    node_id: str
    items: List[ComplianceItem]
    total_score: int
    max_total_score: int
    compliance_rate: float
    level: ComplianceLevel


def normalize_color(value: str) -> str:
    if not value:
        return ""

    raw = value.strip()

    rgba_match = re.fullmatch(
        r"rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d+(?:\.\d+)?)\s*\)",
        raw,
        re.IGNORECASE,
    )
    if rgba_match:
        red = int(rgba_match.group(1))
        green = int(rgba_match.group(2))
        blue = int(rgba_match.group(3))
        alpha = float(rgba_match.group(4))
        alpha_byte = int(round(alpha * 255))
        return f"{alpha_byte:02X}{red:02X}{green:02X}{blue:02X}"

    rgb_match = re.fullmatch(
        r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)",
        raw,
        re.IGNORECASE,
    )
    if rgb_match:
        red = int(rgb_match.group(1))
        green = int(rgb_match.group(2))
        blue = int(rgb_match.group(3))
        return f"FF{red:02X}{green:02X}{blue:02X}"

    if raw.lower().startswith("0x"):
        hex_value = raw[2:].upper()
        if len(hex_value) == 6:
            return f"FF{hex_value}"
        if len(hex_value) == 8:
            return hex_value

    if raw.startswith("#"):
        hex_value = raw[1:].upper()
        if len(hex_value) == 6:
            return f"FF{hex_value}"
        if len(hex_value) == 8:
            return hex_value

    return raw.upper()


def normalize_numeric(value: object) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def values_match(figma_value: object, compose_value: object) -> bool:
    figma_numeric = normalize_numeric(figma_value)
    compose_numeric = normalize_numeric(compose_value)
    if figma_numeric is not None and compose_numeric is not None:
        return abs(figma_numeric - compose_numeric) < EPSILON
    return str(figma_value).strip() == str(compose_value).strip()


def find_matching_paren(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return -1


def extract_named_blocks(code: str, constructor_name: str) -> Dict[str, str]:
    blocks: Dict[str, str] = {}
    pattern = re.compile(rf"val\s+(\w+)\s*=\s*{re.escape(constructor_name)}\(")

    for match in pattern.finditer(code):
        name = match.group(1)
        open_paren_index = code.find("(", match.end() - 1)
        close_paren_index = find_matching_paren(code, open_paren_index)
        if close_paren_index == -1:
            continue
        blocks[name] = code[open_paren_index + 1:close_paren_index]

    return blocks


def extract_first(patterns: Iterable[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
    return None


class FigmaSpecParser:
    @staticmethod
    def parse(figma_spec_path: Path) -> Dict:
        with figma_spec_path.open("r", encoding="utf-8") as file:
            return json.load(file)


class ComposeCodeParser:
    @staticmethod
    def parse(compose_file_path: Path) -> Dict:
        with compose_file_path.open("r", encoding="utf-8") as file:
            code = file.read()

        return {
            "colors": ComposeCodeParser._extract_colors(code),
            "typography": ComposeCodeParser._extract_typography(code),
            "layout": ComposeCodeParser._extract_layout(code),
            "flags": ComposeCodeParser._extract_flags(code),
        }

    @staticmethod
    def _extract_colors(code: str) -> Dict[str, str]:
        colors: Dict[str, str] = {}
        pattern = re.compile(
            r"val\s+(\w+)\s*=\s*Color\(\s*(?:color\s*=\s*)?(0x[0-9A-Fa-f]{6,8}|#[0-9A-Fa-f]{6,8})\s*\)"
        )
        for match in pattern.finditer(code):
            colors[match.group(1)] = match.group(2)
        return colors

    @staticmethod
    def _extract_typography(code: str) -> Dict[str, Dict[str, Optional[str]]]:
        typography: Dict[str, Dict[str, Optional[str]]] = {}
        for name, content in extract_named_blocks(code, "TextStyle").items():
            typography[name] = {
                "fontSize": extract_first([r"fontSize\s*=\s*(\d+(?:\.\d+)?)\s*\.sp"], content),
                "fontWeight": extract_first(
                    [
                        r"fontWeight\s*=\s*FontWeight\.(\w+)",
                        r"fontWeight\s*=\s*FontWeight\(\s*(\d+)\s*\)",
                    ],
                    content,
                ),
                "lineHeight": extract_first([r"lineHeight\s*=\s*(\d+(?:\.\d+)?)\s*\.sp"], content),
                "fontFamily": extract_first(
                    [
                        r"fontFamily\s*=\s*(?:FontFamily\.)?(\w+)",
                        r"fontFamily\s*=\s*(\w+)",
                    ],
                    content,
                ),
            }
        return typography

    @staticmethod
    def _extract_layout(code: str) -> Dict[str, str]:
        layout: Dict[str, str] = {}

        for match in re.finditer(r"val\s+(\w+)\s*=\s*(\d+(?:\.\d+)?)\s*\.dp", code):
            layout[match.group(1)] = match.group(2)

        if match := re.search(r"\.padding\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout.setdefault("padding", match.group(1))

        directional_padding_patterns = {
            "paddingLeft": [r"\.padding\([^)]*start\s*=\s*(\d+(?:\.\d+)?)\s*\.dp"],
            "paddingRight": [r"\.padding\([^)]*end\s*=\s*(\d+(?:\.\d+)?)\s*\.dp"],
            "paddingTop": [r"\.padding\([^)]*top\s*=\s*(\d+(?:\.\d+)?)\s*\.dp"],
            "paddingBottom": [r"\.padding\([^)]*bottom\s*=\s*(\d+(?:\.\d+)?)\s*\.dp"],
        }
        for key, patterns in directional_padding_patterns.items():
            value = extract_first(patterns, code)
            if value:
                layout.setdefault(key, value)

        if match := re.search(r"spacedBy\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout.setdefault("gap", match.group(1))

        if match := re.search(r"RoundedCornerShape\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout["cornerRadius"] = match.group(1)

        if match := re.search(r"\.size\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*,\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout.setdefault("width", match.group(1))
            layout.setdefault("height", match.group(2))

        if match := re.search(r"\.width\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout.setdefault("width", match.group(1))
        if match := re.search(r"\.height\(\s*(\d+(?:\.\d+)?)\s*\.dp\s*\)", code):
            layout.setdefault("height", match.group(1))

        if "statusBarsPadding" in code:
            layout["statusBarHeight"] = "statusBarsPadding"
        if "navigationBarsPadding" in code:
            layout["navigationBarHeight"] = "navigationBarsPadding"
        if "safeDrawingPadding" in code:
            layout.setdefault("statusBarHeight", "safeDrawingPadding")
            layout.setdefault("navigationBarHeight", "safeDrawingPadding")

        return layout

    @staticmethod
    def _extract_flags(code: str) -> Dict[str, bool]:
        return {
            "uses_status_bar_insets": "statusBarsPadding" in code or "safeDrawingPadding" in code,
            "uses_navigation_bar_insets": "navigationBarsPadding" in code or "safeDrawingPadding" in code,
        }


class ComplianceCalculator:
    def __init__(self, figma_spec: Dict, compose_impl: Dict):
        self.figma_spec = figma_spec
        self.compose_impl = compose_impl
        self.items: List[ComplianceItem] = []

    def calculate(self) -> ComplianceReport:
        self._check_colors()
        self._check_typography()
        self._check_layout()
        self._check_vibe_coding()

        total_score = sum(item.score for item in self.items)
        max_total_score = sum(item.max_score for item in self.items)
        compliance_rate = (total_score / max_total_score * 100) if max_total_score else 0.0

        if compliance_rate >= 95:
            level = ComplianceLevel.EXCELLENT
        elif compliance_rate >= 80:
            level = ComplianceLevel.GOOD
        else:
            level = ComplianceLevel.POOR

        return ComplianceReport(
            component_name=self.figma_spec.get("component_name", "Unknown"),
            node_id=self.figma_spec.get("node_id", "Unknown"),
            items=self.items,
            total_score=total_score,
            max_total_score=max_total_score,
            compliance_rate=compliance_rate,
            level=level,
        )

    def _check_colors(self) -> None:
        figma_colors = self.figma_spec.get("colors", {})
        compose_colors = self.compose_impl.get("colors", {})

        for color_name, figma_value in figma_colors.items():
            compose_value = compose_colors.get(color_name, "NOT_FOUND")
            is_match = normalize_color(str(figma_value)) == normalize_color(str(compose_value))
            self.items.append(
                ComplianceItem(
                    category="Color",
                    item_name=color_name,
                    figma_value=str(figma_value),
                    compose_value=str(compose_value),
                    is_match=is_match,
                    score=5 if is_match else 0,
                    max_score=5,
                )
            )

    def _check_typography(self) -> None:
        figma_typography = self.figma_spec.get("typography", {})
        compose_typography = self.compose_impl.get("typography", {})

        for text_style_name, figma_values in figma_typography.items():
            compose_values = compose_typography.get(text_style_name, {})
            self._append_typography_item(
                text_style_name,
                "fontSize",
                figma_values.get("fontSize"),
                compose_values.get("fontSize", "NOT_FOUND"),
                8,
                suffixes=("px", ".sp"),
            )

            figma_weight = str(figma_values.get("fontWeight", ""))
            compose_weight = str(compose_values.get("fontWeight", "NOT_FOUND"))
            expected_weight = WEIGHT_MAP.get(figma_weight, figma_weight)
            is_weight_match = expected_weight.upper() == compose_weight.upper()
            self.items.append(
                ComplianceItem(
                    category="Typography",
                    item_name=f"{text_style_name}.fontWeight",
                    figma_value=figma_weight,
                    compose_value=f"FontWeight.{compose_weight}" if compose_weight != "NOT_FOUND" else "NOT_FOUND",
                    is_match=is_weight_match,
                    score=8 if is_weight_match else 0,
                    max_score=8,
                )
            )

            self._append_typography_item(
                text_style_name,
                "lineHeight",
                figma_values.get("lineHeight"),
                compose_values.get("lineHeight", "NOT_FOUND"),
                8,
                suffixes=("px", ".sp"),
            )

            figma_family = str(figma_values.get("fontFamily", ""))
            compose_family = str(compose_values.get("fontFamily", "NOT_FOUND"))
            family_match = figma_family.upper() == compose_family.upper() if figma_family else compose_family == "NOT_FOUND"
            self.items.append(
                ComplianceItem(
                    category="Typography",
                    item_name=f"{text_style_name}.fontFamily",
                    figma_value=figma_family or "UNSPECIFIED",
                    compose_value=compose_family,
                    is_match=family_match,
                    score=6 if family_match else 0,
                    max_score=6,
                )
            )

    def _append_typography_item(
        self,
        style_name: str,
        property_name: str,
        figma_value: object,
        compose_value: object,
        max_score: int,
        suffixes: tuple[str, str],
    ) -> None:
        is_match = values_match(figma_value, compose_value)
        figma_suffix, compose_suffix = suffixes
        self.items.append(
            ComplianceItem(
                category="Typography",
                item_name=f"{style_name}.{property_name}",
                figma_value=f"{figma_value}{figma_suffix}" if figma_value is not None else "NOT_FOUND",
                compose_value=f"{compose_value}{compose_suffix}" if compose_value != "NOT_FOUND" else "NOT_FOUND",
                is_match=is_match,
                score=max_score if is_match else 0,
                max_score=max_score,
            )
        )

    def _check_layout(self) -> None:
        figma_layout = self.figma_spec.get("layout", {})
        compose_layout = self.compose_impl.get("layout", {})

        for layout_name, figma_value in figma_layout.items():
            compose_value = self._resolve_layout_value(layout_name, compose_layout)
            is_match = self._is_layout_match(layout_name, figma_value, compose_value)
            display_value = self._format_layout_display(compose_value)

            self.items.append(
                ComplianceItem(
                    category="Layout",
                    item_name=layout_name,
                    figma_value=f"{figma_value}px" if normalize_numeric(figma_value) is not None else str(figma_value),
                    compose_value=display_value,
                    is_match=is_match,
                    score=5 if is_match else 0,
                    max_score=5,
                )
            )

    def _resolve_layout_value(self, layout_name: str, compose_layout: Dict[str, str]) -> str:
        aliases = LAYOUT_ALIASES.get(layout_name, [layout_name])
        for alias in aliases:
            if alias in compose_layout:
                return compose_layout[alias]
        return "NOT_FOUND"

    def _is_layout_match(self, layout_name: str, figma_value: object, compose_value: object) -> bool:
        if compose_value == "NOT_FOUND":
            return False

        if layout_name in {"statusBarHeight", "statusBar", "status_bar"}:
            return str(compose_value) in {"statusBarsPadding", "safeDrawingPadding"}

        if layout_name in {"navigationBarHeight", "navigationBar", "navigation_bar"}:
            return str(compose_value) in {"navigationBarsPadding", "safeDrawingPadding"}

        return values_match(figma_value, compose_value)

    def _format_layout_display(self, compose_value: object) -> str:
        if compose_value == "NOT_FOUND":
            return "NOT_FOUND"
        if str(compose_value) in {"statusBarsPadding", "navigationBarsPadding", "safeDrawingPadding"}:
            return f"{compose_value}()"
        return f"{compose_value}.dp"

    def _check_vibe_coding(self) -> None:
        vibe_spec = self.figma_spec.get("vibe_coding")
        if vibe_spec is None:
            return

        if isinstance(vibe_spec, dict):
            is_match = not any(bool(value) for value in vibe_spec.values())
            figma_value = "no arbitrary additions or omissions"
            compose_value = "violations found" if not is_match else "no violations detected"
        else:
            is_match = not bool(vibe_spec)
            figma_value = "no arbitrary additions or omissions"
            compose_value = "violations found" if not is_match else "no violations detected"

        self.items.append(
            ComplianceItem(
                category="VibeCoding",
                item_name="noVibeCodingViolations",
                figma_value=figma_value,
                compose_value=compose_value,
                is_match=is_match,
                score=10 if is_match else 0,
                max_score=10,
            )
        )


class ReportGenerator:
    @staticmethod
    def generate_markdown(report: ComplianceReport) -> str:
        lines: List[str] = []
        lines.append("# Implementation Compliance Report")
        lines.append("")
        lines.append(f"## Component: {report.component_name}")
        lines.append(f"## Node ID: {report.node_id}")

        categories: Dict[str, Dict[str, object]] = {}
        for item in report.items:
            bucket = categories.setdefault(item.category, {"score": 0, "max_score": 0, "items": []})
            bucket["score"] = int(bucket["score"]) + item.score
            bucket["max_score"] = int(bucket["max_score"]) + item.max_score
            cast_items = bucket["items"]
            assert isinstance(cast_items, list)
            cast_items.append(item)

        for category, data in categories.items():
            score = int(data["score"])
            max_score = int(data["max_score"])
            items = data["items"]
            assert isinstance(items, list)
            rate = (score / max_score * 100) if max_score else 0.0
            status = "✅" if rate == 100 else "⚠️"

            lines.append("")
            lines.append(f"### {category} Compliance: {score} / {max_score} points ({rate:.1f}%) {status}")
            lines.append("")
            lines.append("| Item | Figma Spec | Compose Impl | Match | Max Points | Points Earned |")
            lines.append("|------|------------|--------------|-------|------------|---------------|")

            for item in items:
                lines.append(
                    f"| {item.item_name} | {item.figma_value} | {item.compose_value} | "
                    f"{'✅' if item.is_match else '❌'} | {item.max_score} | {item.score} |"
                )

        lines.append("")
        lines.append("## Overall Compliance Score")
        lines.append("")
        lines.append(
            f"### Total: {report.total_score} / {report.max_total_score} points ({report.compliance_rate:.1f}%)"
        )
        lines.append("")

        if report.level == ComplianceLevel.EXCELLENT:
            lines.append("### Verdict: ✅ **EXCELLENT** (95% or higher)")
        elif report.level == ComplianceLevel.GOOD:
            lines.append("### Verdict: ⚠️ **GOOD** (80% or higher, less than 95%) - Needs Improvement")
        else:
            lines.append("### Verdict: ❌ **POOR** (less than 80%) - Re-implementation Recommended")

        mismatches = [item for item in report.items if not item.is_match]
        if mismatches:
            lines.append("")
            lines.append("## Improvement Required")
            lines.append("")
            for item in mismatches:
                lines.append(f"- [ ] **{item.item_name}**: change `{item.compose_value}` to `{item.figma_value}`")

        return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Figma compliance calculator for Jetpack Compose")
    parser.add_argument("--figma-spec", required=True, help="Path to normalized Figma specification JSON")
    parser.add_argument("--compose-impl", required=True, help="Path to Jetpack Compose Kotlin file")
    parser.add_argument("--output", default="compliance-report.md", help="Path to output Markdown report")
    return parser.parse_args()


def validate_inputs(figma_spec_path: Path, compose_impl_path: Path) -> None:
    missing = [str(path) for path in (figma_spec_path, compose_impl_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required input file(s): {', '.join(missing)}")


def main() -> None:
    args = parse_args()
    figma_spec_path = Path(args.figma_spec)
    compose_impl_path = Path(args.compose_impl)
    output_path = Path(args.output)

    validate_inputs(figma_spec_path, compose_impl_path)

    figma_spec = FigmaSpecParser.parse(figma_spec_path)
    compose_impl = ComposeCodeParser.parse(compose_impl_path)
    report = ComplianceCalculator(figma_spec, compose_impl).calculate()
    markdown_report = ReportGenerator.generate_markdown(report)

    output_path.write_text(markdown_report, encoding="utf-8")

    print(f"Compliance report generated: {output_path}")
    print(f"Overall Score: {report.compliance_rate:.1f}% ({report.level.value})")


if __name__ == "__main__":
    main()
