#!/usr/bin/env python3
"""Build distributable ZIPs for the skill.

Outputs:
  dist/life-pattern-reading-vX.Y.Z/                 (unpacked tree)
  dist/life-pattern-reading-vX.Y.Z-bundle.zip       (contains life-pattern-reading/)
  dist/life-pattern-reading-vX.Y.Z-flat.zip         (SKILL.md at ZIP root)
  dist/SHA256SUMS.txt

The flat ZIP is useful for platforms that require SKILL.md at the archive root.
The bundle ZIP is useful for manual installation into a skills directory.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT_FILES = [
    "SKILL.md",
    "README.md",
    "README.en.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
]

ROOT_DIRS = [
    "references",
    "assets",
    "scripts",
    "examples",
]

SKIP_DIRS = {"__pycache__", ".git", ".github", "dist", "tests", ".venv"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def read_version(root: Path) -> str:
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^\s*version:\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)", text)
    if not match:
        raise ValueError("could not find a semantic version in SKILL.md metadata")
    return match.group(1)


def iter_files(root: Path):
    for name in ROOT_FILES:
        path = root / name
        if path.is_file():
            yield path
    for dirname in ROOT_DIRS:
        base = root / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in SKIP_DIRS for part in relative.parts):
                continue
            if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
                continue
            yield path


def copy_tree(root: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    for path in iter_files(root):
        target = destination / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def add_tree(zf: zipfile.ZipFile, source: Path, arc_prefix: str = "") -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
            continue
        arcname = Path(arc_prefix) / relative if arc_prefix else relative
        zf.write(path, arcname.as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="skill package root (default: .)")
    parser.add_argument("--output", default="dist", help="output directory (default: dist)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (root / args.output).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    version = read_version(root)
    bundle_name = f"life-pattern-reading-v{version}"
    # Keep the unpacked directory name equal to the skill name: some hosts and
    # the Agent Skills specification require the folder name to match `name`.
    unpacked = output / "life-pattern-reading"
    copy_tree(root, unpacked)

    bundle_zip = output / f"{bundle_name}-bundle.zip"
    with zipfile.ZipFile(bundle_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        add_tree(zf, unpacked, arc_prefix="life-pattern-reading")

    flat_zip = output / f"{bundle_name}-flat.zip"
    with zipfile.ZipFile(flat_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        add_tree(zf, unpacked)

    checksums = output / "SHA256SUMS.txt"
    lines = []
    for path in [bundle_zip, flat_zip]:
        lines.append(f"{sha256(path)}  {path.name}")
    checksums.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Version: {version}")
    print(f"Unpacked: {unpacked}")
    for path in [bundle_zip, flat_zip, checksums]:
        print(f"Built: {path} ({path.stat().st_size} bytes)")
    print("Bundle ZIP contains the life-pattern-reading/ folder; flat ZIP has SKILL.md at its root.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - clean CLI error
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
