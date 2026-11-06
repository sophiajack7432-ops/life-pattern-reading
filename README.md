# life-pattern-reading

> 用四柱八字、紫微斗数、七政四余与西方占星，做**有边界、可核验、不恐吓**的人生格局与阶段轨迹解读。

这是一个可导入 Agent Skills / DeepSeek Harness 的技能包。它不是排盘软件，也不是“预测机器”；它把“接资料 → 审口径 → 分体系解读 → 交叉比较 → 阶段表 → 质检”的完整流程固化成一套可复用的 skill。

[English README](README.en.md) · [SKILL.md](SKILL.md) · [安全边界](references/safety.md) · [示例](examples/full-reading.md)

---

## 这个 skill 解决什么问题

很多命理类提示词有两个问题：

1. **没有盘也敢说**：编造四柱、星曜、宫位、度数和起止年份；
2. **为了显得完整而伪造一致**：把四套体系说成“完全一致”，或者用恐吓性措辞制造权威。

这个包把这两件事作为硬约束：

- 没有可靠盘面，就只做资料整理与非盘面反思；
- 四套体系分别陈述，再比较共通、独有与分歧；
- 每个重要判断标注体系、依据与置信度；
- 不预测疾病、死亡、灾祸、破产、离婚等具体事件；
- 不用“克夫/克妻/短命/贫贱”等标签；
- 医疗、法律、投资、婚育等主题转介现实专业意见。

## 特点

- **完整流程**：资料接收 → 可靠性分级 → 盘面事实表 → 单体系观察卡 → 交叉比较 → 阶段表 → 重点领域 → 质检。
- **反编造设计**：明确“本 skill 不内置星历/历法引擎”，没有盘就不排盘。
- **边界敏感**：出生时间接近时辰、日界、节气、宫位临界点时，自动降级为双盘面对照。
- **四体系独立**：不把十神、星曜、宫位、行星做一一对应，不伪造“四套一致”。
- **安全优先**：包含高风险主题矩阵、危机处理、拒绝话术、隐私与去污名化规范。
- **可直接交付**：附带输入表单、报告模板、观察卡、歧义记录表、三个完整示例。
- **可维护**：Python 标准库校验脚本、报告 lint、打包脚本、单元测试、GitHub Actions。
- **零运行时依赖**：skill 正文不需要安装包；脚本只依赖 Python 3.9+ 标准库。

## 已知限制

- **不内置排盘**：需要用户提供可信盘面，或宿主提供可复现的排盘工具；没有资料时不会自行推算。
- **流派差异**：同一体系的不同流派可能给出不同参数或结论；报告会记录口径，不混用。
- **不可科学验证**：四套体系是传统文化与象征性解释，不能当作事实证据或重大决策的唯一依据。
- **不是专业服务**：不替代医疗、法律、投资、心理治疗等专业意见。

## 兼容性

- 目录名 `life-pattern-reading` 与 frontmatter `name` 一致，符合 [Agent Skills 规范](https://agentskills.io/specification)。
- 已通过官方 `skills-ref` 0.1.1 校验（可用 `python -m skills_ref.cli validate /absolute/path/to/life-pattern-reading` 复现）。
- 同一份 `SKILL.md` 可用于 DeepSeek Harness、Claude Code 及其他兼容 Agent Skills 的宿主。
- 不依赖网络、星历或第三方 Python 包；脚本只使用 Python 标准库。

## 快速开始

### 方式一：DeepSeek Harness（用户级）

```bash
git clone <repo-url> ~/.dsh/skills/life-pattern-reading
```

Windows PowerShell：

```powershell
git clone <repo-url> "$HOME/.dsh/skills/life-pattern-reading"
```

### 方式二：DeepSeek Harness（项目级）

在项目根目录执行：

```bash
mkdir -p .dsh/skills
git clone <repo-url> .dsh/skills/life-pattern-reading
```

Windows 下可先执行 `New-Item -ItemType Directory -Force .dsh\skills`，再运行 `git clone`。

DSH 会扫描：

- `<project>/.dsh/skills`
- `<project>/.agents/skills`
- `~/.dsh/skills`
- `~/.agents/skills`

项目根是最近的 `.git` 祖先；没有 `.git` 时使用当前工作目录。把文件夹放在这些根目录的**直接子目录**中，且保证 `life-pattern-reading/SKILL.md` 存在。

### 方式三：Claude Code / 其他 Agent Skills 兼容宿主

```bash
# 用户级
git clone <repo-url> ~/.claude/skills/life-pattern-reading

# 项目级
git clone <repo-url> .claude/skills/life-pattern-reading
```

其他兼容 Agent Skills 的宿主：把仓库放到其 skills 根目录下，确保 `SKILL.md` 位于 `life-pattern-reading/` 根目录。

### 方式四：ZIP 导入

从 GitHub Releases 下载：

- `life-pattern-reading-v1.0.0-bundle.zip`：包含 `life-pattern-reading/` 文件夹，适合手动安装；
- `life-pattern-reading-v1.0.0-flat.zip`：`SKILL.md` 位于 ZIP 根目录，适合要求根级 `SKILL.md` 的平台。

解压后放到对应 skills 根目录，或按平台的上传入口导入。

### 方式五：安装脚本

Windows：

```powershell
powershell -File .\scripts\install.ps1 -Scope user
# 或项目级
powershell -File .\scripts\install.ps1 -Scope project -ProjectPath .
# PowerShell 7+ 也可以把 powershell 换成 pwsh
```

macOS / Linux：

```bash
sh scripts/install.sh
# 或项目级
sh scripts/install.sh --project
```

脚本只复制文件，不执行代码、不安装依赖、不改注册表。已有目录时需加 `--force` / `-Force`。

## 使用

在支持 slash command 的宿主中：

```text
/life-pattern-reading
```

然后提供资料，例如：

```text
公历 1992 年 3 月 18 日 07:40，成都，UTC+8。
时间来自家人口述，可能有 ±15 分钟误差。
我想先看整体格局和事业，再看大运阶段。
```

如果宿主没有 slash command，直接说：

```text
请用 life-pattern-reading skill 帮我做一次有边界的命理格局解读。
资料如下：……
```

### 最少需要提供

| 项目 | 说明 |
|---|---|
| 出生日期 | 公历/农历；农历注明闰月 |
| 出生时间 | 尽量到分钟；说明来源与精确度 |
| 出生地点 | 城市/地区；需要宫位时再给经纬度 |
| 时区 | 如 `Asia/Shanghai`；注意历史夏令时 |
| 关注主题 | 整体、大运、事业、财务、关系等 |
| 现成盘面 | 有则提供体系、软件、版本与参数 |

不想一次填完也可以。skill 会先问最关键的 3 个问题，或在标明假设的前提下做条件式讨论。

## 输出长什么样

完整报告包含：

```markdown
### 资料与口径
### 总体格局
### 四体系观察
### 交叉结论
### 大运与人生阶段
### 重点领域
### 总结
```

并带有证据标签，例如：

```text
【八字·中】资源上更强调“以专业/作品换取空间”，而不是单纯追求规模。
【共通·3/4】三套体系都触及“表达与边界”的主题；这是象征层面的集中，不是事实保证。
```

阶段表固定为：

| 阶段 | 主要主题 | 机会与可用资源 | 需要处理的挑战 | 现实建议 |
|---|---|---|---|---|

没有可靠排运数据时，不硬凑年份；只给通用阶段框架，并明确说明“不是命理排运结论”。

完整示例：

- [完整多体系解读（虚构教学数据）](examples/full-reading.md)
- [资料不足时的诚实输出](examples/partial-data.md)
- [出生时间在节气/时辰边界](examples/boundary-time.md)

## 工作流

```text
0 模式判断
  ↓
1 接收资料（最少问题）
  ↓
2 资料审计（L0–L4、歧义触发器）
  ↓
3 盘面事实表（只写事实）
  ↓
4 单体系解读（观察卡、证据标签）
  ↓
5 交叉比较（共通/独有/分歧，不伪造一致）
  ↓
6 阶段轨迹（只基于可核实时间数据）
  ↓
7 重点领域（开放问题 + 现实建议）
  ↓
8 质检与交付（边界、格式、语气）
```

详细流程见 [SKILL.md](SKILL.md)。

## 资料可靠性等级

| 等级 | 条件 | 能做什么 |
|---|---|---|
| L0 | 无资料 | 不排盘 |
| L1 | 只有日期或缺关键项 | 资料整理、非盘面反思 |
| L2 | 资料基本完整但无盘，或盘来源不明 | 弱判断、条件式讨论 |
| L3 | 可复现盘面：来源/版本/参数清楚 | 各体系的具体判断 |
| L4 | L3 + 第二来源核对 | 较稳定的体系判断 |

**硬规则**：L3/L4 才支持“强/中”置信度；L2 只能给“弱”；L1/L0 不进入四体系解读。

## 边界与安全

- 四套体系属于传统文化与象征性解释，不能科学验证，也不能保证预测准确。
- 不预测疾病、死亡、灾祸、破产、离婚、官司结果、投资收益、胎儿性别。
- 不提供法术、符咒、消灾、改运商品或“付费解锁”。
- 医疗/法律/投资/婚育等重大决定，交给现实资料与专业人士。
- 不用羞辱性标签；不用恐吓推动消费。
- 第三方资料需同意与隐私保护；未成年人额外保护。

完整规范见 [references/safety.md](references/safety.md)。

## 包结构

```text
life-pattern-reading/
├── SKILL.md                     # 入口：角色、工作流、输出格式、质量清单
├── README.md                    # 本文件
├── README.en.md                 # English quick start
├── LICENSE                      # MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── references/
│   ├── intake-and-privacy.md    # 接资料、提问、隐私、第三方
│   ├── chart-data.md            # 四体系字段、参数、一致性检查
│   ├── interpretation.md        # 观察卡、证据分级、交叉比较、偏差
│   ├── timeline.md              # 大运/大限、年龄口径、阶段表
│   ├── output-spec.md           # 报告结构与写法
│   ├── safety.md                # 高风险、危机、拒绝话术、伦理
│   ├── glossary.md              # 术语表
│   └── sources.md               # 文献、时区、星历来源
├── assets/
│   ├── intake-form.md           # 给用户填的资料表
│   ├── output-template.md       # 报告模板
│   ├── observation-card.md      # 单体系观察卡
│   └── ambiguity-log.md         # 歧义/双盘面记录
├── examples/
│   ├── full-reading.md
│   ├── partial-data.md
│   ├── boundary-time.md
│   └── README.md
├── scripts/
│   ├── validate_skill.py        # 包结构/frontmatter/链接校验
│   ├── check_report.py          # 报告格式/禁用措辞 lint
│   ├── package.py               # 生成 flat/bundle ZIP
│   ├── install.ps1              # Windows 安装
│   └── install.sh               # macOS/Linux 安装
├── tests/
│   └── test_skill_package.py
└── .github/workflows/validate.yml
```

## 验证与维护

```bash
# 校验 skill 包
python scripts/validate_skill.py

# 运行测试
python -m unittest discover -s tests -v

# 检查示例报告
python scripts/check_report.py examples/full-reading.md

# 打包
python scripts/package.py
```

产物在 `dist/`：

- `life-pattern-reading/`（解包目录，folder name 与 skill name 一致）
- `life-pattern-reading-v1.0.0-bundle.zip`
- `life-pattern-reading-v1.0.0-flat.zip`
- `SHA256SUMS.txt`

## 上传到 GitHub

这个仓库根目录就是 skill bundle（`SKILL.md` 在根目录），可以直接作为 GitHub 仓库上传。

```bash
git init
git add .
git commit -m "feat: add life-pattern-reading skill"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

发布新版本：

1. 更新 `SKILL.md` 的 `metadata.version` 与 `CHANGELOG.md`；
2. 运行 `python scripts/validate_skill.py`；
3. 运行 `python -m unittest discover -s tests -v`；
4. 运行 `python scripts/package.py`；
5. 打 tag：`git tag v1.0.0 && git push origin v1.0.0`；
6. 在 GitHub Release 中附上 `dist/*.zip` 和 `SHA256SUMS.txt`。

## 贡献

欢迎补充：

- 更清楚的流程说明；
- 新的边界案例；
- 更准确的传统文献出处；
- 更安全的表达模板；
- 对四体系参数差异的校正。

请先读 [CONTRIBUTING.md](CONTRIBUTING.md)。不要提交真实出生资料、真实盘面截图或可识别个人的案例。

## 许可

MIT，见 [LICENSE](LICENSE)。

> 本 skill 是传统文化研究与自我反思工具，不构成医疗、法律、投资、婚育或其他专业建议。命理不能科学验证，也不能保证预测准确。请把输出当作反思角度，而不是事实判决。
