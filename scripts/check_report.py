#!/usr/bin/env python3
"""Lint a generated life-pattern-reading report.

This is a mechanical helper, not a substitute for human judgment.
It checks required sections, the stage table, disclaimers, and a small set of
deterministic or stigmatizing phrases that should not appear in a final report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_SECTIONS = [
    "资料与口径",
    "总体格局",
    "四体系观察",
    "交叉结论",
    "大运与人生阶段",
    "重点领域",
    "总结",
]

SYSTEM_LABELS = ["四柱八字", "紫微斗数", "七政四余", "西方占星"]

NEGATIONS = (
    "不",
    "并非",
    "不是",
    "没有",
    "避免",
    "不能",
    "不会",
    "拒绝",
    "不用",
    "不应",
    "不宜",
)

DETERMINISTIC_PATTERNS = [
    r"注定会",
    r"命中注定",
    r"一定会",
    r"必然会",
    r"肯定会",
    r"必定会",
    r"绝对会",
    r"百分之百",
    r"100%",
    r"逃不过",
    r"无法避免",
    r"铁定",
]

HARMFUL_LABEL_PATTERNS = [
    r"你是(?:克夫|克妻|克子|寡妇命|短命|贫贱|绝后|二婚命|贱格)",
    r"(?:克夫|克妻|克子|寡妇命|短命相|贫贱命|绝后命|二婚命|贱格|下格命)",
]

FAKE_CONSENSUS_PATTERNS = [
    r"四套体系(?:完全)?一致",
    r"四个体系(?:完全)?一致",
    r"四套体系(?:都)?证明",
    r"四套体系(?:都)?说明",
]

FAKE_SCIENCE_PATTERNS = [
    r"科学(?:已经)?证明.{0,20}命理",
    r"命理.{0,20}科学(?:已经)?证明",
]

TABLE_HEADER_RE = re.compile(
    r"^\|\s*阶段\s*\|\s*主要主题\s*\|\s*机会与可用资源\s*\|\s*需要处理的挑战\s*\|\s*现实建议\s*\|\s*$",
    re.MULTILINE,
)

HEADING_RE = re.compile(r"^(#{2,4})\s*(.+?)\s*$", re.MULTILINE)


def strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def is_negated(text: str, start: int, window: int = 18) -> bool:
    prefix = text[max(0, start - window) : start]
    return any(neg in prefix for neg in NEGATIONS)


def find_pattern_hits(text: str, patterns: List[str]) -> List[Tuple[str, int]]:
    hits: List[Tuple[str, int]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            if not is_negated(text, match.start()):
                hits.append((match.group(0), match.start()))
    return hits


def extract_section(text: str, title: str) -> str:
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group(2).strip() == title:
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            return text[start:end]
    return ""


def count_table_rows(text: str) -> int:
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if TABLE_HEADER_RE.match(line.strip()):
            header_index = index
            break
    if header_index is None:
        return 0
    rows = 0
    for line in lines[header_index + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        if re.fullmatch(r"\|[\s:|-]+\|", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(not cell for cell in cells):
            continue
        rows += 1
    return rows


def lint(text: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    searchable = strip_fenced_code(text)

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^#{{2,4}}\s*{re.escape(section)}\s*$", searchable, re.MULTILINE):
            errors.append(f"missing required section: {section}")

    for label in SYSTEM_LABELS:
        if label not in searchable:
            errors.append(f"missing system label: {label}")

    if "大运与人生阶段" in searchable:
        rows = count_table_rows(searchable)
        if rows == 0:
            timeline_text = extract_section(searchable, "大运与人生阶段")
            fallback_markers = ["不列具体", "缺少", "无法", "资料不足", "待确认", "暂不"]
            if any(marker in timeline_text for marker in fallback_markers):
                warnings.append(
                    "no stage table found; accepted because the section explains missing timeline data"
                )
            else:
                errors.append(
                    "no valid stage table found and no explicit explanation of missing timeline data"
                )
        elif rows > 6:
            warnings.append(f"stage table has {rows} rows; prefer 3-6 stages")

    disclaimer_ok = (
        "传统文化" in searchable
        and ("不能科学验证" in searchable or "不构成预测" in searchable)
        and ("反思工具" in searchable or "不构成预测" in searchable)
    )
    if not disclaimer_ok:
        errors.append(
            "missing cultural/educational disclaimer (expects 传统文化 + 不能科学验证/不构成预测 + 反思工具)"
        )

    for phrase, _ in find_pattern_hits(searchable, DETERMINISTIC_PATTERNS):
        errors.append(f"deterministic phrase: {phrase}")

    for phrase, _ in find_pattern_hits(searchable, HARMFUL_LABEL_PATTERNS):
        errors.append(f"stigmatizing label: {phrase}")

    for phrase, _ in find_pattern_hits(searchable, FAKE_CONSENSUS_PATTERNS):
        errors.append(f"possibly fabricated four-system consensus: {phrase}")

    for phrase, _ in find_pattern_hits(searchable, FAKE_SCIENCE_PATTERNS):
        errors.append(f"false scientific authority: {phrase}")

    if "四套体系都" in searchable and not any(
        neg in searchable[max(0, searchable.find("四套体系都") - 18) : searchable.find("四套体系都")]
        for neg in NEGATIONS
    ):
        warnings.append("report says '四套体系都...'; verify all four systems have L3/L4 data")

    summary = extract_section(searchable, "总结")
    numbered = re.findall(r"^\s*\d+\.\s+", summary, re.MULTILINE)
    if not summary:
        errors.append("summary section is empty")
    elif not 3 <= len(numbered) <= 5:
        warnings.append(f"summary has {len(numbered)} numbered items; prefer 3-5")

    if "资料可信度" not in searchable and "资料等级" not in searchable:
        warnings.append("no explicit data reliability level (L0-L4) found")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="path to the markdown report")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    path = Path(args.report)
    if not path.is_file():
        print(f"ERROR: report not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    errors, warnings = lint(text)

    if args.strict:
        errors.extend(f"strict: {warning}" for warning in warnings)
        warnings = []

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(path),
                    "ok": not errors,
                    "errors": errors,
                    "warnings": warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Report: {path}")
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if errors:
            print(f"FAILED with {len(errors)} error(s)", file=sys.stderr)
        else:
            print("OK: report lint passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
