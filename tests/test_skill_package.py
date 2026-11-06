from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_report  # noqa: E402


GOOD_REPORT = textwrap.dedent(
    """\
    ### 资料与口径

    - 出生资料：示例资料。
    - 排盘依据与采用口径：示例参数。
    - 资料可信度：L3。
    - 需要保留的不确定性：示例误差。

    > 说明：以下为传统文化与象征性解读，不能科学验证，也不构成预测或重大决策依据。

    ### 总体格局

    这是一个示例主轴。

    - 优势：示例优势。
    - 挑战：示例挑战。
    - 适合的发展方式：示例方式。

    ### 四体系观察

    - **四柱八字**：示例观察。
    - **紫微斗数**：示例观察。
    - **七政四余**：示例观察。
    - **西方占星**：示例观察。

    ### 交叉结论

    - 多体系共通主题：示例主题。
    - 各体系独有观察：示例观察。
    - 体系分歧与可能原因：示例原因。

    ### 大运与人生阶段

    时间来源：示例；年龄按周岁；误差约 ±1 年。

    | 阶段 | 主要主题 | 机会与可用资源 | 需要处理的挑战 | 现实建议 |
    |---|---|---|---|---|
    | 约 20–29 岁 | 建立能力 | 学习资源 | 容易分散 | 做一个 3 个月小项目 |

    ### 重点领域

    #### 事业

    示例开放问题与现实建议。

    ### 总结

    1. 示例行动一。
    2. 示例行动二。
    3. 示例行动三。

    > 命理是反思工具，不是现实判断的替代品。涉及医疗、法律、投资、婚育等重大决定，请结合现实资料与专业意见。
    """
)


def run_script(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def make_minimal_package(root: Path, name: str = "test-skill") -> None:
    root.mkdir(parents=True, exist_ok=True)
    for directory in ["references", "assets", "scripts", "examples", "tests"]:
        (root / directory).mkdir(exist_ok=True)

    skill = f"""\
---
name: {name}
description: "A test skill description that is long enough to pass validation."
whenToUse: "Use for validator tests."
license: "MIT"
metadata:
  version: "1.0.0"
---

# Test skill

## 运行契约

This is a test skill. 不能科学验证，也不构成预测。

## 输出格式

Use the template.

## 表达风格

Plain Chinese.
"""
    (root / "SKILL.md").write_text(skill, encoding="utf-8")
    for filename in ["README.md", "README.en.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md"]:
        (root / filename).write_text("# Test\n", encoding="utf-8")
    for rel in [
        "references/intake-and-privacy.md",
        "references/chart-data.md",
        "references/interpretation.md",
        "references/timeline.md",
        "references/safety.md",
        "references/output-spec.md",
        "references/glossary.md",
        "references/sources.md",
        "assets/intake-form.md",
        "assets/output-template.md",
        "assets/observation-card.md",
        "assets/ambiguity-log.md",
    ]:
        (root / rel).write_text("# Test\n", encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def test_repository_package_passes(self) -> None:
        result = run_script("validate_skill.py", "--root", str(ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "test-skill"
            make_minimal_package(root, name="Bad_Name")
            result = run_script("validate_skill.py", "--root", str(root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("kebab-case", result.stderr)

    def test_broken_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "test-skill"
            make_minimal_package(root)
            with (root / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n[missing](references/missing.md)\n")
            result = run_script("validate_skill.py", "--root", str(root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("broken link", result.stderr)

    def test_missing_description_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "test-skill"
            make_minimal_package(root)
            skill = (root / "SKILL.md").read_text(encoding="utf-8")
            skill = skill.replace(
                'description: "A test skill description that is long enough to pass validation."\n',
                "",
            )
            (root / "SKILL.md").write_text(skill, encoding="utf-8")
            result = run_script("validate_skill.py", "--root", str(root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("description", result.stderr)


class ReportCheckerTests(unittest.TestCase):
    def test_good_report_passes(self) -> None:
        errors, warnings = check_report.lint(GOOD_REPORT)
        self.assertEqual(errors, [])

    def test_full_example_passes(self) -> None:
        result = run_script("check_report.py", str(ROOT / "examples" / "full-reading.md"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_partial_example_passes_with_warning(self) -> None:
        result = run_script("check_report.py", str(ROOT / "examples" / "partial-data.md"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no stage table", result.stdout)

    def test_boundary_example_passes(self) -> None:
        result = run_script("check_report.py", str(ROOT / "examples" / "boundary-time.md"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_deterministic_phrase_is_rejected(self) -> None:
        errors, _ = check_report.lint(GOOD_REPORT.replace("示例开放问题与现实建议。", "你一定会离婚。"))
        self.assertTrue(any("deterministic" in error for error in errors))

    def test_harmful_label_is_rejected(self) -> None:
        errors, _ = check_report.lint(GOOD_REPORT.replace("示例开放问题与现实建议。", "你是克夫命。"))
        self.assertTrue(any("stigmatizing" in error for error in errors))

    def test_missing_section_is_rejected(self) -> None:
        broken = GOOD_REPORT.replace("### 总结", "### 结论")
        errors, _ = check_report.lint(broken)
        self.assertTrue(any("总结" in error for error in errors))

    def test_fake_consensus_is_rejected(self) -> None:
        errors, _ = check_report.lint(GOOD_REPORT.replace("示例原因。", "四套体系完全一致。"))
        self.assertTrue(any("consensus" in error for error in errors))

    def test_negated_phrase_is_allowed(self) -> None:
        errors, _ = check_report.lint(
            GOOD_REPORT.replace("示例开放问题与现实建议。", "这不是一定会发生的事件。")
        )
        self.assertFalse(any("deterministic" in error for error in errors))


class PackagingTests(unittest.TestCase):
    def test_builds_flat_and_bundle_zips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dist"
            result = run_script(
                "package.py",
                "--root",
                str(ROOT),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            flat = output / "life-pattern-reading-v1.0.0-flat.zip"
            bundle = output / "life-pattern-reading-v1.0.0-bundle.zip"
            unpacked = output / "life-pattern-reading"
            self.assertTrue(flat.is_file())
            self.assertTrue(bundle.is_file())
            self.assertTrue((unpacked / "SKILL.md").is_file())

            with zipfile.ZipFile(flat) as zf:
                self.assertIn("SKILL.md", zf.namelist())
                self.assertIn("references/safety.md", zf.namelist())
            with zipfile.ZipFile(bundle) as zf:
                self.assertIn("life-pattern-reading/SKILL.md", zf.namelist())

            result = run_script("validate_skill.py", "--root", str(unpacked))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
