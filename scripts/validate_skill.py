#!/usr/bin/env python3
"""Validate the skill package structure, frontmatter, links, and basic hygiene.

No third-party dependencies. Works on Python 3.9+.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
WINDOWS_ABS_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:\\")
UNIX_ABS_RE = re.compile(r"(?<![\w.])/(?:Users|home|root)/")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME)\b|\[待填写\]")

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "README.en.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
]

REQUIRED_DIRS = [
    "references",
    "assets",
    "scripts",
    "examples",
]

REQUIRED_REFERENCES = [
    "references/intake-and-privacy.md",
    "references/chart-data.md",
    "references/interpretation.md",
    "references/timeline.md",
    "references/safety.md",
    "references/output-spec.md",
    "references/glossary.md",
    "references/sources.md",
]

REQUIRED_ASSETS = [
    "assets/intake-form.md",
    "assets/output-template.md",
    "assets/observation-card.md",
    "assets/ambiguity-log.md",
]


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Parse the small YAML subset used by SKILL.md.

    Supports flat `key: value` lines and quoted values. Nested metadata lines
    are ignored for validation but remain in the file.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a '---' frontmatter line")

    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        raise ValueError("frontmatter is missing a closing '---' line")

    data: Dict[str, str] = {}
    for raw in lines[1:closing]:
        line = raw.strip()
        if not line or line.startswith("#") or raw[:1].isspace():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"invalid frontmatter line: {raw!r}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value

    body = "\n".join(lines[closing + 1 :]).strip()
    return data, body


def iter_markdown(root: Path) -> List[Path]:
    skip = {".git", ".github", "dist", "tests", "__pycache__", ".venv"}
    result: List[Path] = []
    for path in root.rglob("*.md"):
        if any(part in skip for part in path.relative_to(root).parts):
            continue
        result.append(path)
    return sorted(result)


def check_links(root: Path, path: Path) -> List[str]:
    errors: List[str] = []
    text = path.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target:
            continue
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Strip an optional title and anchor: path.md "title" / path.md#anchor
        target = target.split("#", 1)[0].strip()
        target = target.split(" ", 1)[0].strip().strip("<>")
        if not target:
            continue
        if target.startswith("/"):
            errors.append(f"{path.relative_to(root)}: absolute link is not portable: {target}")
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(root)}: link escapes package root: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: broken link: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="skill package root (default: .)")
    parser.add_argument("--max-skill-lines", type=int, default=650)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: List[str] = []
    warnings: List[str] = []

    if not (root / "SKILL.md").is_file():
        print(f"ERROR: no SKILL.md under {root}", file=sys.stderr)
        return 1

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing required directory: {rel}")
    for rel in REQUIRED_REFERENCES + REQUIRED_ASSETS:
        if not (root / rel).is_file():
            errors.append(f"missing required resource: {rel}")
    if not (root / "tests").is_dir():
        warnings.append("no tests/ directory (fine for an installed/runtime bundle; expected in the source repo)")

    skill_path = root / "SKILL.md"
    try:
        text = skill_path.read_text(encoding="utf-8")
        front, body = parse_frontmatter(text)
    except Exception as exc:  # noqa: BLE001 - report a clean message
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    name = front.get("name", "").strip()
    description = front.get("description", "").strip()

    if not name:
        errors.append("frontmatter is missing 'name'")
    elif len(name) > 64:
        errors.append("frontmatter 'name' must be 64 characters or fewer")
    elif not NAME_RE.match(name):
        errors.append("frontmatter 'name' must be kebab-case: [a-z0-9]+(-[a-z0-9]+)*")
    elif name != root.name:
        warnings.append(
            f"skill name '{name}' differs from folder name '{root.name}' "
            "(allowed, but the repository folder is usually named after the skill)"
        )

    if not description:
        errors.append("frontmatter is missing 'description'")
    elif len(description) < 20:
        errors.append("frontmatter 'description' is too short to route the skill")
    elif len(description) > 1024:
        errors.append("frontmatter 'description' exceeds 1024 characters")

    if not body:
        errors.append("SKILL.md body is empty")
    if len(text.splitlines()) > args.max_skill_lines:
        errors.append(f"SKILL.md is longer than {args.max_skill_lines} lines")
    if len(text.encode("utf-8")) > 80_000:
        errors.append("SKILL.md is larger than 80 KB")

    if "license" not in front:
        warnings.append("frontmatter has no 'license'; the bundled LICENSE file is still present")
    compatibility = front.get("compatibility", "")
    if compatibility and len(compatibility) > 500:
        errors.append("frontmatter 'compatibility' exceeds 500 characters")

    for heading in ["运行契约", "输出格式", "表达风格"]:
        if heading not in body:
            warnings.append(f"SKILL.md is missing the section heading '{heading}'")
    if "不能科学验证" not in body and "不构成预测" not in body:
        errors.append("SKILL.md does not contain a clear cultural/educational disclaimer")

    for md in iter_markdown(root):
        errors.extend(check_links(root, md))
        content = md.read_text(encoding="utf-8")
        if WINDOWS_ABS_RE.search(content) or UNIX_ABS_RE.search(content):
            errors.append(f"{md.relative_to(root)}: contains a machine-specific absolute path")
        if md.name in {"SKILL.md"} or md.parts[0] in {"references", "assets"}:
            if PLACEHOLDER_RE.search(content):
                errors.append(f"{md.relative_to(root)}: contains a placeholder token")

    print(f"Skill: {name or '(missing name)'}")
    print(f"Root:  {root}")
    print(f"SKILL.md: {len(text.splitlines())} lines, {len(text.encode('utf-8'))} bytes")
    print(f"Markdown files checked: {len(iter_markdown(root))}")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(f"FAILED with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OK: skill package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
