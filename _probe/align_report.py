# -*- coding: utf-8 -*-
"""给整合方案报告加状态横幅、修正第八章过期数据、追加第九章。"""
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = Path(r"D:\Resources\DSH\环境盘点与整合方案.md")

BANNER_OLD = """盘点时间：2026-10-07　范围：插件（bundles）/ 工具 / 技能 / 工作区
数据来源：`D:\\Resources\\DSH\\_probe\\plugin_audit.py`、`plugin_cost.py`、`C:\\Users\\Administrator\\.dsh\\profiles\\desktop\\package.json`"""

BANNER_NEW = BANNER_OLD + """

> **⚠️ 状态横幅（2026-10-08 03:20 复核）**：第一 ~ 七章是 **2026-10-07 的历史记录**（当时 37 / 40 个 bundle，"5 个插件都在做技能管理"的结论已过时）。
> **当前实际状态以第八、九章为准**：bundles **41 条**、技能 **74 个（生效 73）**、技能管理唯一入口 = **设置 → 技能**（`@michengai/dsh-skills-manager` 1.1.13）。"""

SEC91_OLD = "| 3 | `dsh-skills-manager`（实装 1.1.10） | ✅ **本轮启用** | 设置 → 技能 |"
SEC91_NEW = "| 3 | `dsh-skills-manager`（实装 **1.1.13**；本轮启用时是 1.1.10，02:38 由应用升级） | ✅ **本轮启用** | 设置 → 技能 |"

SEC83_OLD = "| `desktop\\package.json` | `json.loads` 通过；bundles 40 条；dependencies 38 条**一条未动**（没做任何卸载，加回一行即可还原） |"
SEC83_NEW = ("| `desktop\\package.json` | `json.loads` 通过；本轮改完 bundles 40 条；dependencies 38 条**一条未动**（没做任何卸载，加回一行即可还原）。"
             "**⚠️ 2026-10-08 02:38 应用重写了这个文件 → bundles 41 条**（新装 `dsh-plugin-wallpaper-engine` 1.3.1）、dependencies 39 条；"
             "本轮两处改动（+skills-manager / −skill-explorer）都还在 |")

SEC84_OLD = "| 版本漂移 | `@michengai/dsh-skills-manager` 实装 1.1.10 → npm 1.1.13；`billion-context` 依赖声明 0.1.186 / 实装 0.1.187 | 重启 DSH 后在应用内插件管理面板统一升级 |"
SEC84_NEW = "| ~~版本漂移~~ **已解决** | `@michengai/dsh-skills-manager` 实装 1.1.10 → npm 1.1.13；`billion-context` 依赖声明 0.1.186 / 实装 0.1.187 | 2026-10-08 02:38 应用已自行对齐（声明 = 实装 = skills-manager **1.1.13** / billion-context **0.1.187**） |"

SEC9 = """

---

## 九、第三轮（2026-10-08 03:20）：把「涉及 skill 的文件与设置」对齐到实际

用户要求（原话）：**「调整所有涉及到skill的文件、设置，使符合实际情况」**

### 9.1 复核发现的漂移（应用在 02:38 自己改的，不是本轮改的）

| 项 | 旧记录 | 2026-10-08 03:11 实物 |
| --- | --- | --- |
| bundles | 40 条 | **41 条**：应用新装 `dsh-plugin-wallpaper-engine` 1.3.1（包内无 SKILL.md，不新增技能） |
| `@michengai/dsh-skills-manager` | 声明 1.1.10 / 实装 1.1.10 | 声明 **1.1.13** / 实装 **1.1.13**（应用已升级，"版本漂移"消失） |
| `billion-context` | 声明 0.1.186 / 实装 0.1.187 | 声明 **0.1.187** / 实装 0.1.187（已对齐） |
| `@linxin666/dsh-client-ui-skill-explorer` | 在 bundles 里 | 仍在 `dependencies`（^0.4.5）与 node_modules，**不在 bundles** = 已安装、未装载（加回一行即可还原） |
| 技能账 | 64（旧清单，脚本崩过） | **74 个 `SKILL.md` / 生效 73 / 未生效 1**（`@anionex/dsh-vision-toolkit` 的 `skill`，该插件未装载） |

### 9.2 对齐的文件（全部定点替换，每个模式命中数必须 = 1，否则整文件不写）

| 文件 | 改了什么 | 依据 |
| --- | --- | --- |
| `~\\.dsh\\skills\\daofa-lesson-prep\\references\\skill-routing.md` | ①技能数 48 → **74（生效 73）**；②盘点脚本由 `_probe\\inventory_skills.py`（旧副本）改为权威脚本 `…\\daofa-lesson-prep\\scripts\\inventory-skills.py`；③新增「设置 → 技能」为启停入口；④技能管理行 `skill-explorer` / `echocat` 面板 → **设置 → 技能（skills-manager）**，并补 `dsh-skill-mcp-manager` 行；⑤`ppt_*` 手册数 20 → **17**；⑥§四标题改「2026-10-08 复核」、`git` 行改「已装但不在 PATH」、`ffmpeg` 由「下载中」改「`D:\\tools\\ffmpeg` 不存在」 | 实跑 `inventory-skills.py`、`Test-Path`、`git --version` |
| `~\\.dsh\\skills\\daofa-lesson-prep\\references\\tool-routing.md` | ①手册数 4 → **17**（4 核心 + 12 图形配方 + 1 总手册）；②§三能力表：`git` ❌→**⚠️ 已装（`D:\\tools\\git\\bin\\git.exe` 2.56.0）但不在 PATH**、`node` ❌→**✅ 在 PATH（v24.19.0）**、`pnpm` 由"有"→**❌ 不在 PATH**、`ffmpeg` 补记目录不存在；③§五整段重写：CLI 被应用独占拒绝（贴原文 `error: profile "desktop" is managed exclusively by the Electron application`），改指 **设置 → 插件市场 / 设置 → 技能**，并写明「改 `package.json` 的 `dsh.profile.bundles`：加一行 = 挂载、删一行 = 不挂载，`dependencies` 保留 = 已安装未装载」 | 同上 |
| `~\\.dsh\\AGENTS.md` | ①「本机无 `git`」→「**`git` 不在 PATH**（已装在 `D:\\tools\\git`，2.56.0；全路径 `D:\\tools\\git\\bin\\git.exe` 可用）」，规则本身（不要跑 git）保留；②`using-git-worktrees`（本机无 git）→（git 不在 PATH）。10 683 → **10 919 B** | `git --version` = 2.56.0.windows.2 |

备份：三个文件各自 `.bak-20261008`；批量脚本 `D:\\Resources\\DSH\\_probe\\align_skill_docs.py`。

### 9.3 顺带清掉的 skill 残留

| 对象 | 处理 |
| --- | --- |
| `~\\.dsh\\skill-report\\translations.json`（13.6 KB，echocat 面板的翻译缓存；该插件未装载 → 死数据） | 移到 `~\\.dsh\\_removed\\skill-report-20261008\\` |
| `~\\.dsh\\skills\\pptx-layout-craft\\scripts\\__pycache__\\`（6 个 .pyc ≈ 62 KB，可再生的字节码） | 移到 `~\\.dsh\\_removed\\__pycache__-20261008\\` |
| `D:\\Resources\\DSH\\_probe\\inventory_skills.py`（2.7 KB，会产出过期清单的旧副本） | 移到 `~\\.dsh\\_removed\\inventory_skills.py-20261008` |
| `~\\.dsh\\skill-mcp-manager\\session-audit.json`（129 B，扫描 0 项、无异常） | **保留**（插件自管，无害） |

### 9.4 两处"看着矛盾"的旧说法，真实情况

- `skill-routing.md` 写「`git` ✅ `D:\\tools\\git` 2.56.0」，`AGENTS.md` 写「本机无 git」——**两者都不准确**：git 确实装着（2.56.0），但没进 PATH，裸命令用不了。现已统一为「已装但不在 PATH」。
- `skill-routing.md` 说 ppt-studio「20 本手册」、`tool-routing.md` 说「4 本手册」——**实际 17 本**（`skills\\` 下 17 个 `SKILL.md`：4 本核心 craft/copy/data/manual + 1 本 `ppt-studio-diagram` 索引 + 12 张图形配方）；插件注释里的「4 本内嵌技能」指预设内嵌的那 4 本核心手册。工具数 **22** 已核实：`lib\\tools.js` 21 处 `defineTool` + `lib\\index.js:210` 注册的 `ppt_state`。

### 9.5 与 skill 有关的设置，现状一览

| 维度 | 入口 / 归属 | 状态 |
| --- | --- | --- |
| 技能启停 / 导入 / 仓库 / 回滚 | 设置 → 技能（`@michengai/dsh-skills-manager` 1.1.13） | ✅ 唯一入口；启停只写本地策略，源 `SKILL.md` 不动 |
| 插件安装 / 卸载 / 更新 | 设置 → 插件市场（`dshmarket`）；**CLI 被应用独占，用不了** | ✅ |
| MCP 服务器 | `dsh-skill-mcp-manager`（`mcp_register` / `mcp_load` / `mcp_call`） | ✅ 独立于技能管理 |
| 会话经验 → 技能草稿 | `dsh-run2skill` | ✅ 保留 |
| 侧栏旧「技能中心」 | `@linxin666/dsh-client-ui-skill-explorer` | ⛔ 已装未装载（会改源 frontmatter + 每日心跳） |
| `dsh-echocat-skill-panel` | — | ⛔ 未启用（停用靠搬目录，与 skills-manager 策略冲突） |
| 技能文件本体 | `C:\\Users\\Administrator\\.dsh\\skills\\`（自建 3 个）+ 各插件包内 `skills\\` | ✅ 74 个，生效 73 |
"""

text = P.read_text(encoding="utf-8")
pairs = [(BANNER_OLD, BANNER_NEW), (SEC91_OLD, SEC91_NEW), (SEC83_OLD, SEC83_NEW), (SEC84_OLD, SEC84_NEW)]
ok = True
for i, (old, _) in enumerate(pairs, 1):
    n = text.count(old)
    if n != 1:
        print(f"✗ 模式 {i} 命中 {n} 次（需 1）: {old[:70]!r}")
        ok = False
if ok:
    bak = P.with_suffix(".md.bak-20261008")
    if not bak.exists():
        shutil.copy2(P, bak)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + "\n" + SEC9
    P.write_text(text, encoding="utf-8")
    print(f"✓ {P}  → {P.stat().st_size}B（{len(text.splitlines())} 行）  备份 {bak.name}")
