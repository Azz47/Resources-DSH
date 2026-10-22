"""全局同步：把报告里「10 个技能根 / 64 个 SKILL.md」等 10-07 旧数字对齐到 10-08 实测。
定点替换：每处模式必须恰好命中 1 次，任一失配则整文件不写；首次改写前存 .bak-before-globalsync-20261008。
"""
import io
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPORT = r"D:\Resources\DSH\环境盘点与整合方案.md"
BAK = REPORT + ".bak-before-globalsync-20261008"

text = io.open(REPORT, encoding="utf-8").read()
orig = text

ROOT_TABLE_OLD = """**技能根分布（10 根 / 64 个 SKILL.md）**

| 技能根 | 数量 |
| --- | --- |
| `dsh-ppt-studio\\skills` | 17 |
| `superpowers-dsh\\skills` | 15 |
| `@michengai\\dsh-pua\\assets\\pua\\upstream\\skills` | 12 |
| `dsh-animations\\skills` | 8 |
| `@arcaneorion\\dsh-teaching-board\\skills\\stage-panel\\submode` | 5 |
| **`C:\\Users\\Administrator\\.dsh\\skills`（自建）** | **3** |
| teaching-board\\skills | 1 |
| `@changfenhuang` | 1 |
| `archify-dsh\\skills` | 1 |
| `dsh-craft-your-textbook` | 1 |"""

ROOT_TABLE_NEW = """**技能根分布（10-07 快照：10 根 / 64 个 → **10-08 实测：12 个来源包 / 74 个 SKILL.md**）**

| 技能根（来源包） | 10-07 | 10-08 |
| --- | --- | --- |
| `dsh-ppt-studio\\skills` | 17 | 17 |
| `superpowers-dsh\\skills` | 15 | 15 |
| `@michengai\\dsh-pua\\assets\\pua\\upstream\\skills` | 12 | 12 |
| `dsh-animations\\skills` | 8 | 8 |
| `@arcaneorion\\dsh-teaching-board`（`skills` 1 + `skills\\stage-panel\\submode` 5） | 6 | 6 |
| **`C:\\Users\\Administrator\\.dsh\\skills`（自建）** | **3** | **3** |
| `@changfenhuang/dsh-genui` | 1 | 1 |
| `@tt-a1i/archify-dsh\\skills` | 1 | 1 |
| `dsh-craft-your-textbook` | 1 | 1 |
| **`dsh-univer-office`（10-08 新装）** | — | **8** |
| **`@vectorize-io/hindsight-coding-agents`（10-08 新装）** | — | **1（生效）** |
| **`@anionex/dsh-vision-toolkit`（未装载）** | — | **1（未生效）** |
| **合计** | **64** | **74（生效 73）** |"""

SECTION_10 = """
---

## 十、全局同步：10-07 旧数字 → 10-08 实测

第十章是 10-08 对「技能账」做的一次**全盘检索 + 对齐**，起因是第一章那句「10 个技能根 / 64 个 SKILL.md」在文档里被当成现状引用。

### 10.1 差在哪里（64 → 74）

| 变化 | 数量 | 说明 |
| --- | --- | --- |
| `dsh-univer-office` | **+8** | 10-08 装载（univer / univer-base / univer-board / univer-cross-unit-formula / univer-doc / univer-embed / univer-sheet / univer-slide） |
| `@vectorize-io/hindsight-coding-agents` | **+1** | 10-08 装载（`hindsight-coding-agent`，生效） |
| `@anionex/dsh-vision-toolkit` | **+1（未生效）** | 包在 `dependencies` 里但**不在 `bundles`**，静态技能清单能扫到、会话里看不到 → 计入总数、不计入生效数 |
| teaching-board 根合并计数 | 0 | 旧表把同一插件拆成 `skills`(1) 与 `stage-panel\\submode`(5) 两行，10-08 按包合并为 6；总数不变 |
| **合计** | **74（生效 73）** | 来源包 **12 个**（旧表 10 个）+ 用户目录 3 个 = 74 |

### 10.2 全盘检索：旧数字出现在哪、怎么处置

| 位置 | 旧内容 | 处置 |
| --- | --- | --- |
| `环境盘点与整合方案.md:16`（第一章现状表） | 10 根 / 64 个 SKILL.md | **加 10-07 快照标注 + 指到实测值**（保留历史行，不改写历史） |
| `环境盘点与整合方案.md:138-151`（第六章技能根表） | 10 根 / 64 个 | **换成两列对照表**（10-07 vs 10-08，合计 64 → 74） |
| `环境盘点与整合方案.md:130` | `deck-design-spec.md` 13,410 B / 242 行 | 改为 **17,318 B / 229 行**（10-08 实测） |
| `环境盘点与整合方案.md:131` | `inventory-skills.py` 2,671 B | 改为 **3,916 B / 107 行**（已修崩溃 bug 的版本） |
| `_skilltest\\skills-backup-20261007\\...\\skill-routing.md:3` | 「48 个可用技能」 | **不动快照本体**，在同目录加 `SNAPSHOT-README.txt` 标明这是 10-07 快照 |
| `_probe\\align_skill_docs.py` | 内含旧字符串（替换模式） | **加文件头标注**：一次性迁移脚本，旧说法是「被替换的目标」不是事实 |
| `_removed\\skill-docs-bak-20261008\\` | 旧版 skill-routing/tool-routing | 在 `_removed` 里，目录名自带日期，无需再处理 |
| Hindsight 记忆库 | 可能存有旧技能账 | **本次无法写**：`hindsight_diagnose` 显示 `api_token_configured: false`，`C:\\Users\\Administrator\\.hindsight\\coding-agent.json` 不存在 → 所有 `hindsight_*` 调用 401。已备好可直投的 `技能现状速查.md` |

### 10.3 唯一的现状口径

以后要引用技能账，只认这三处（其余一律当历史）：

1. **数据**：`D:\\Resources\\DSH\\_probe\\skills-inventory.json`（`inventory-skills.py` 重跑产出，含 `active` 字段）
2. **速查**：`D:\\Resources\\DSH\\技能现状速查.md`（本机现状一页纸，供人读 / 供记忆库 ingest）
3. **本文档第八、九、十章**（决策与证据）

### 10.4 复核证据（10-08 实跑）

- `_probe\\skill_coverage.py` → 技能总数 **74**　已引用 **74**　未引用 **0**
- `_probe\\verify_agents_names.py` → 技能 **74/74** 真实存在、假名 0、漏路由 0；专家 **27/27**；总判定 ✅ 双向核对通过
- `_probe\\skill_roots_summary.py`（本次新增）→ 按 `pkg` 分组 **12 个来源包**；`active` 字段 **73 / 1**
- 全盘 grep `技能根|64 个 SKILL|48 个可用技能` → 命中只剩「已标注的快照 / 迁移脚本 / 带快照标注的历史行」
"""

used = []
for old, new in [
    (
        "| 技能 | 10 个技能根 / 64 个 SKILL.md | 自建 3 个，重复脚本已合并 |",
        "| 技能 | 10 个技能根 / 64 个 SKILL.md（**10-07 快照**；10-08 实测 **12 个来源包 / 74 个**，见第六章表与第十章） | 自建 3 个，重复脚本已合并 |",
    ),
    (ROOT_TABLE_OLD, ROOT_TABLE_NEW),
    (
        "（13,410 B / 242 行）",
        "（**10-08 实测 17,318 B / 229 行**；10-07 记录为 13,410 B / 242 行）",
    ),
    (
        "与 `inventory-skills.py`（2,671 B）。",
        "与 `inventory-skills.py`（**10-08 实测 3,916 B / 107 行**，已修好 Unicode 崩溃；10-07 记录为 2,671 B）。",
    ),
]:
    n = text.count(old)
    assert n == 1, "模式命中 %d 次（应为 1）: %r" % (n, old[:60])
    text = text.replace(old, new)
    used.append(old[:40])

text = text.rstrip("\n") + "\n" + SECTION_10

shutil.copyfile(REPORT, BAK)
io.open(REPORT, "w", encoding="utf-8", newline="\n").write(text)
print("备份:", BAK)
print("定点替换:", len(used), "处")
for u in used:
    print("  -", u)
print("旧长度 %d B / %d 行 → 新长度 %d B / %d 行" % (
    len(orig.encode("utf-8")), orig.count("\n") + 1,
    len(text.encode("utf-8")), text.count("\n") + 1,
))
