# life-pattern-reading

> A cautious, evidence-aware skill for life-pattern and life-stage readings using Four Pillars (BaZi), Zi Wei Dou Shu, Qi Zheng Si Yu, and Western astrology.

This is a reusable **Agent Skill / DeepSeek Harness skill**, not an ephemeris engine or a prediction machine. It encodes a complete workflow: intake → data audit → chart fact sheet → independent system readings → cross-system comparison → life-stage table → quality review.

[中文 README](README.md) · [SKILL.md](SKILL.md) · [Safety](references/safety.md) · [Example](examples/full-reading.md)

---

## What it does

- Accepts birth data and, when available, user-supplied chart data.
- Grades data reliability from L0 to L4 and refuses to invent charts.
- Reads each tradition independently before comparing themes.
- Separates convergence from conflict; never fabricates “all four systems agree.”
- Produces a stage table only when verified luck-cycle/transit data exists.
- Refuses event predictions about illness, death, disaster, bankruptcy, divorce, lawsuits, investments, or pregnancy.
- Redirects medical, legal, financial, and other high-stakes questions to qualified professionals.

## What it is not

- Not a scientific instrument; these traditions cannot be scientifically validated.
- Not an ephemeris or chart calculator; it interprets user-supplied or tool-verified chart data.
- Not a substitute for medical, legal, financial, or mental-health care.
- Not a tool for fear-based selling, curses, “destiny changing,” or manipulating third parties.

## Compatibility

- The folder name `life-pattern-reading` matches the frontmatter `name`, following the [Agent Skills specification](https://agentskills.io/specification).
- Validated with the official `skills-ref` 0.1.1 validator (reproduce with `python -m skills_ref.cli validate /absolute/path/to/life-pattern-reading`).
- The same `SKILL.md` works in DeepSeek Harness, Claude Code, and other Agent Skills-compatible hosts.
- No network, ephemeris, or third-party Python dependency is required; scripts use only the standard library.

## Install

### DeepSeek Harness (user scope)

```bash
git clone <repo-url> ~/.dsh/skills/life-pattern-reading
```

Windows PowerShell:

```powershell
git clone <repo-url> "$HOME/.dsh/skills/life-pattern-reading"
```

### DeepSeek Harness (project scope)

```bash
mkdir -p .dsh/skills
git clone <repo-url> .dsh/skills/life-pattern-reading
```

On Windows, create the directory with `New-Item -ItemType Directory -Force .dsh\skills` first.

DSH scans the direct children of `.dsh/skills`, `.agents/skills`, `~/.dsh/skills`, and `~/.agents/skills`. The bundle must contain `SKILL.md` at its root.

### Claude Code / other Agent Skills hosts

```bash
git clone <repo-url> ~/.claude/skills/life-pattern-reading
# or
git clone <repo-url> .claude/skills/life-pattern-reading
```

### ZIP

Download a release asset:

- `life-pattern-reading-v1.0.0-bundle.zip` — contains the `life-pattern-reading/` folder;
- `life-pattern-reading-v1.0.0-flat.zip` — `SKILL.md` at the ZIP root.

### Installer scripts

```powershell
powershell -File .\scripts\install.ps1 -Scope user
# PowerShell 7+ can use pwsh instead of powershell
```

```bash
sh scripts/install.sh
```

The scripts only copy files. Add `-Force` / `--force` to replace an existing copy.

## Use

```text
/life-pattern-reading
```

Then provide:

- birth date (Gregorian or lunar; specify leap month);
- birth time to the minute, with source and accuracy;
- birth city and time zone;
- the topic you want to explore;
- any existing chart, with system, software/version, and parameters.

If your host does not support slash commands, ask directly:

```text
Use the life-pattern-reading skill to give me a bounded reading.
My birth data is: ...
```

## Output

The report follows this structure:

```markdown
### 资料与口径
### 总体格局
### 四体系观察
### 交叉结论
### 大运与人生阶段
### 重点领域
### 总结
```

The main content is in Simplified Chinese by default; ask for another language if needed.

## Reliability ladder

| Level | Condition | Allowed |
|---|---|---|
| L0 | No data | No chart claims |
| L1 | Date only / key data missing | Intake and non-chart reflection |
| L2 | Basic data but no reproducible chart | Weak, conditional observations |
| L3 | Reproducible chart with source/version/parameters | System-specific observations |
| L4 | L3 + second-source check | More stable system observations |

Only L3/L4 support “strong/medium” confidence. L2 is limited to “weak.” L0/L1 do not enter the four-system reading.

## Safety

- These systems are cultural and symbolic, not scientifically validated.
- No predictions of illness, death, disaster, bankruptcy, divorce, legal outcomes, investment returns, or fetal sex.
- No curses, rituals, “destiny-changing” products, or fear-based sales.
- High-stakes decisions belong with qualified professionals and real-world information.
- Third-party readings require consent and privacy protection.

Read [references/safety.md](references/safety.md) for the full policy and refusal scripts.

## Validate and package

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
python scripts/check_report.py examples/full-reading.md
python scripts/package.py
```

Outputs:

- `dist/life-pattern-reading/` (folder name matches the skill name)
- `dist/life-pattern-reading-v1.0.0-bundle.zip`
- `dist/life-pattern-reading-v1.0.0-flat.zip`
- `dist/SHA256SUMS.txt`

## Repository layout

```text
SKILL.md
README.md
README.en.md
LICENSE
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
references/
assets/
examples/
scripts/
tests/
.github/workflows/validate.yml
```

## License

MIT. See [LICENSE](LICENSE).

> This skill is a cultural-reflection tool, not medical, legal, financial, or reproductive advice. It cannot be scientifically validated and does not guarantee accurate predictions.
