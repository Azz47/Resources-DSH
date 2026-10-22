# -*- coding: utf-8 -*-
"""把与 skill 相关的文档对齐到 2026-10-08 实测现实。

⚠️ 这是一次性迁移脚本（2026-10-08 已执行完毕），**不是现状说明**。
脚本里出现的「48 个可用技能」「4 本手册」「20 本手册」等字符串是**被替换的目标**（旧说法），
不要把它们当成事实引用。现状只认：
  D:\\Resources\\DSH\\技能现状速查.md  与  D:\\Resources\\DSH\\_probe\\skills-inventory.json
（执行记录与证据见 环境盘点与整合方案.md 第八 ~ 十章。）

规则：每个替换模式必须**恰好命中 1 次**；同一文件任一模式失配 → 该文件整体不写。
每个文件首次改写前存一份 .bak-20261008。
"""
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SK = Path(r"C:\Users\Administrator\.dsh\skills\daofa-lesson-prep\references")
AG = Path(r"C:\Users\Administrator\.dsh\AGENTS.md")

EDITS = []

# ── 1. skill-routing.md ───────────────────────────────────────────────────────
EDITS.append((SK / "skill-routing.md", [
    (
        "> 本机当前共 **48 个可用技能**（来源：插件自带 + 用户目录 + DSH 内置）。\n"
        "> 本文件回答一个问题：**做道法课件的每一步，到底该调哪个技能/工具。**\n"
        "> 盘点脚本：`D:\\Resources\\DSH\\_probe\\inventory_skills.py`；清单快照 `_probe\\skills-inventory.json`。",
        "> 本机当前共 **74 个技能**（2026-10-08 实测：生效 73 / 未生效 1；来源：插件自带 71 + 用户目录 3）。\n"
        "> 本文件回答一个问题：**做道法课件的每一步，到底该调哪个技能/工具。**\n"
        "> 盘点脚本（权威）：`C:\\Users\\Administrator\\.dsh\\skills\\daofa-lesson-prep\\scripts\\inventory-skills.py`；"
        "清单快照 `D:\\Resources\\DSH\\_probe\\skills-inventory.json`。\n"
        "> 技能启停 / 导入 / 回滚入口：**设置 → 技能**（`@michengai/dsh-skills-manager`）——启停只写本地策略，**不动源 `SKILL.md`**。",
    ),
    (
        "22 个 `ppt_*` 工具与 20 本手册**只在「PPT 工作室」预设作用域可见**",
        "22 个 `ppt_*` 工具与 17 本手册（4 核心 + 12 图形配方 + 1 总手册）**只在「PPT 工作室」预设作用域可见**",
    ),
    (
        "| 技能管理 | `skill-explorer` / `echocat` 面板 | — | 查看技能被调用的次数 |",
        "| **技能管理**（启停 / 导入 / 仓库 / 回滚） | **设置 → 技能**（`@michengai/dsh-skills-manager`） | "
        "插件市场（`dshmarket`）管插件本身 | 停用只写本地策略、源文件不动；侧栏旧「技能中心」（`skill-explorer`）与 "
        "`echocat` 面板**均已停用** |\n"
        "| MCP 服务器 | `dsh-skill-mcp-manager`（`mcp_register` / `mcp_load` / `mcp_call`） | — | 本机唯一 MCP 管理入口 |",
    ),
    (
        "## 四、本机能力现实（2026-10-07 实测）",
        "## 四、本机能力现实（2026-10-08 复核）",
    ),
    (
        "| `git` | ✅ `D:\\tools\\git`（2.56.0） | 已装；但见下条 |",
        "| `git` | ⚠️ 已装但**不在 PATH**（`D:\\tools\\git\\bin\\git.exe`，2.56.0） | 裸 `git` 命令调不到；插件安装仍见下条 |",
    ),
    (
        "| `ffmpeg` | ⏳ `D:\\tools\\ffmpeg`（下载中） | 无 ffmpeg 时**不能做视频后处理**；"
        "但 `ppt-animation`/`video-shot-demos` 靠录屏，不依赖它 |",
        "| `ffmpeg` | ❌ `D:\\tools\\ffmpeg` 不存在（2026-10-08 复核） | 不能做视频后处理；"
        "但 `ppt-animation`/`video-shot-demos` 靠录屏，不依赖它 |",
    ),
]))

# ── 2. tool-routing.md ────────────────────────────────────────────────────────
OLD_ENV = """**没有的**（2026-10-07 实测）：

| 工具 | 状态 | 影响 |
| --- | --- | --- |
| `git` | ❌ 全部路径都没有 | 任何 `github:` 规格的插件安装都会失败；只能用 npm 或 codeload tarball |
| `ffmpeg` / `ffprobe` | ❌ | **不能直接产出微课 MP4**；视频类插件装了也跑不动 |
| `soffice` / `libreoffice`（PATH 上） | ❌ | 但 DSH 自带 `@deepseek-ai/libreoffice-kit`，Office 转换走它即可 |
| `pandoc` / `magick` | ❌ | 不要依赖 |
| `node`（PATH 上） | ❌ | 用 DSH 自带的：`D:\\tools\\dsh\\resources\\runtime\\primary-runtime\\dependencies\\node\\bin\\node.exe` |

**有的**：DSH 自带 **Python 3.12.14**（含 python-docx / python-pptx / openpyxl / pandas / Pillow）、**pnpm 11.7.0**、**LibreOffice kit**、Edge/Chrome。"""

NEW_ENV = """**没有的**（2026-10-08 复核）：

| 工具 | 状态 | 影响 |
| --- | --- | --- |
| `git`（PATH 上） | ⚠️ **已装但不在 PATH**：`D:\\tools\\git\\bin\\git.exe`（2.56.0） | 裸 `git` 调不到；`github:` 规格的插件安装仍会失败（github.com:443 超时），只能用 npm 或 codeload tarball |
| `ffmpeg` / `ffprobe` | ❌（`D:\\tools\\ffmpeg` 也不存在） | **不能直接产出微课 MP4**；视频类插件装了也跑不动 |
| `soffice` / `libreoffice`（PATH 上） | ❌ | 但 DSH 自带 `@deepseek-ai/libreoffice-kit`，Office 转换走它即可 |
| `pnpm`（PATH 上） | ❌ | 只随 DSH 运行时存在，命令行直接调不到；装插件走应用内的插件市场 |
| `pandoc` / `magick` | ❌ | 不要依赖 |

**有的**：**`node` ✅ 在 PATH 上**（`C:\\Program Files\\nodejs\\node.exe`，v24.19.0）；DSH 另带一份 node 在 `D:\\tools\\dsh\\resources\\runtime\\primary-runtime\\dependencies\\node\\bin\\node.exe`。另有 DSH 自带的 **Python 3.12.14**（含 python-docx / python-pptx / openpyxl / pandas / Pillow）、**LibreOffice kit**、Edge/Chrome。"""

OLD_PLUGIN = '''## 五、插件管理命令（本机）

```powershell
# 安装 / 卸载（desktop profile）
& "D:\\tools\\dsh\\resources\\runtime\\cli\\bin\\dsh.cmd" plugin --profile desktop add    <包名>
& "D:\\tools\\dsh\\resources\\runtime\\cli\\bin\\dsh.cmd" plugin --profile desktop remove <包名>

# 图形化：设置 → 插件市场（dshmarket 已装）
```

装完好坏**不用重启**：profile 有 HMR，插件的工具/技能/提示段会在几秒内出现在当前会话；但**浏览器端的 UI 页签需要刷新页面**。'''

NEW_PLUGIN = '''## 五、插件管理（本机）

**⚠️ CLI 用不了**：desktop profile 由 Electron 应用独占 —— `dsh plugin --profile desktop add/remove` 会被拒：

```text
error: profile "desktop" is managed exclusively by the Electron application
```

**正确入口：设置 → 插件市场（`dshmarket` 已装）**；技能维度的启停 / 导入 / 仓库 / 回滚走 **设置 → 技能（`@michengai/dsh-skills-manager`）**。

**市场也办不到时**：直接编辑 `C:\\Users\\Administrator\\.dsh\\profiles\\desktop\\package.json` 的 `dsh.profile.bundles` 数组（**先备份**）。
每个插件包靠自带的 `cordis.patch.yml` 把自己的那一行 insert 进来，所以**加一行 = 挂载，删一行 = 不挂载**；从 bundles 删掉但保留 `dependencies` 里的条目 = 「已安装、未装载」，加回一行即可还原。应用启动时会重写这个文件（可能顺带升级版本）。'''

EDITS.append((SK / "tool-routing.md", [
    ("| 4 本手册可加载 | 无 |", "| 17 本手册可加载（4 核心 + 12 图形配方 + 1 总手册） | 无 |"),
    (OLD_ENV, NEW_ENV),
    (OLD_PLUGIN, NEW_PLUGIN),
]))

# ── 3. ~/.dsh/AGENTS.md ───────────────────────────────────────────────────────
EDITS.append((AG, [
    (
        "`using-git-worktrees`（本机无 git）",
        "`using-git-worktrees`（git 不在 PATH）",
    ),
    (
        "- **本机无 `git`**，不要依赖 git 命令；也不要为脑图文件跑 git。",
        "- **`git` 不在 PATH**（已装在 `D:\\tools\\git`，2.56.0；全路径 `D:\\tools\\git\\bin\\git.exe` 可用）："
        "不要依赖裸 `git` 命令；也不要为脑图文件跑 git。",
    ),
]))

for path, pairs in EDITS:
    text = path.read_text(encoding="utf-8")
    problems = []
    for i, (old, new) in enumerate(pairs, 1):
        n = text.count(old)
        if n != 1:
            problems.append(f"  模式 {i} 命中 {n} 次（需 1）: {old[:60]!r}")
    if problems:
        print(f"✗ 跳过 {path}")
        for p in problems:
            print(p)
        continue
    bak = path.with_suffix(path.suffix + ".bak-20261008")
    if not bak.exists():
        shutil.copy2(path, bak)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"✓ {path}  ({len(pairs)} 处)  → {path.stat().st_size}B   备份 {bak.name}")
