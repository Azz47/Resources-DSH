#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""10-14 技能扩容后的文档同步：
  A) 环境盘点与整合方案.md —— 更新状态横幅 + 追加第十二章
  B) ~/.dsh/AGENTS.md —— 修正加载不到的名字 + 新增第二节 F 区（10-14 新增批次）
每处替换都断言「恰好命中 1 次」，否则整体不写。
"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPORT = r"D:\Resources\DSH\环境盘点与整合方案.md"
AGENTS = r"C:\Users\Administrator\.dsh\AGENTS.md"
BAK = ".bak-before-skillsync-20261014"


def backup(p):
    dst = p + BAK
    if not os.path.exists(dst):
        shutil.copy2(p, dst)
    return dst


def sub(text, old, new, tag):
    n = text.count(old)
    assert n == 1, "[%s] 命中 %d 次（要求 1 次）:\n%s" % (tag, n, old[:160])
    return text.replace(old, new)


# ---------------------------------------------------------------- A) 报告
r = open(REPORT, encoding="utf-8").read()
backup(REPORT)

OLD_BANNER = """> **⚠️ 状态横幅（2026-10-08 03:20 复核）**：第一 ~ 七章是 **2026-10-07 的历史记录**（当时 37 / 40 个 bundle，"5 个插件都在做技能管理"的结论已过时）。
> **当前实际状态以第八、九章为准**：bundles **41 条**、技能 **74 个（生效 73）**、技能管理唯一入口 = **设置 → 技能**（`@michengai/dsh-skills-manager` 1.1.13）。"""

NEW_BANNER = """> **⚠️ 状态横幅（2026-10-14 复核）**：第一 ~ 七章是 **2026-10-07 的历史记录**（当时 37 / 40 个 bundle，"5 个插件都在做技能管理"的结论已过时）。
> **当前实际状态以第八、九、十、十一、十二章为准**：bundles **41 条** / `deps 36`（**`deps ⊆ bundles`**）、技能 **144 个（生效 144 / 未生效 0）**、技能管理唯一入口 = **设置 → 技能**（`@michengai/dsh-skills-manager` 1.1.13）。
> **技能账的最新口径**：`D:\\Resources\\DSH\\技能现状速查.md`（10-14 版）+ `_probe\\skills-inventory.json`（144 条）；本文档第六章与第十、十一、十二章是历史与证据。"""

r = sub(r, OLD_BANNER, NEW_BANNER, "banner")

OLD_ROW = "| 技能 | 10 个技能根 / 64 个 SKILL.md（**10-07 快照**；10-08 实测 **12 个来源包 / 74 个**，见第六章表与第十章） | 自建 3 个，重复脚本已合并 |"
NEW_ROW = "| 技能 | 10 个技能根 / 64 个 SKILL.md（**10-07 快照**；10-08 实测 12 个来源包 / 74 个；**10-14 实测 11 个来源组 / 144 个**，见第六、十、十二章） | 自建 3 个；10-14 导入 7 个 GitHub 仓库 71 个技能 |"
r = sub(r, OLD_ROW, NEW_ROW, "ch1-row")

CHAPTER12 = """

---

## 十二、10-14 技能扩容：+71 个用户技能（7 个 GitHub 仓库）

起因：用户点名安装 7 个技能仓库。10-14 全部落地，用户技能根 **3 → 74**，全机技能账 **74 → 144**。

### 12.1 变化总账

| 项 | 10-08 | 10-14 | 说明 |
| --- | --- | --- | --- |
| 用户技能根 `C:\\Users\\Administrator\\.dsh\\skills\\` | 3 | **74** | 新增 71（7 个仓库），磁盘 14.25 MB |
| 插件自带技能 | 71（生效 70 + 未生效 1） | **70（全部生效）** | `@anionex/dsh-vision-toolkit` 随包删除而消失 |
| 全机 `SKILL.md` | 74 | **144** | 生效 144 / 未生效 0 |
| 来源组 | 12 个来源包 | **11 个**（10 插件 + 用户根） | 唯一未生效项消失 |
| profile `package.json` | deps 39 / bundles 41（有不装载的包） | **deps 36 / bundles 41，`deps ⊆ bundles`** | 用户侧 10-14 19:31 清理：`skill-explorer`、`echocat-skill-panel`、`@anionex/dsh-vision-toolkit` 从 `deps` 与 `node_modules` 移除 |

按仓库：`mattpocock/skills` 38、`leonxlnx/taste-skill` 14、`Egonex-AI/Understand-Anything` 9、`nextlevelbuilder/ui-ux-pro-max-skill` 7、`blader/humanizer` 1、`panniantong/agent-reach` 1、`zarazhangrui/frontend-slides` 1。明细与「目录名 ≠ frontmatter 名」对照表见 `技能现状速查.md` 第八节。

### 12.2 安装通道（可复用）

1. **网络实况**：`github.com:443` 超时（`git clone` → `error: RPC failed; curl 56 Recv failure: Connection was reset`）；`api.github.com` / `codeload.github.com` 通 → **本机只能走 ZIP 通道**；下载必须带 `--connect-timeout 15 --max-time 300` 并校验非 0 字节。
2. **落盘**：ZIP 解到 `D:\\Resources\\DSH\\_skillinstall\\<repo>\\`；再用 `D:\\Resources\\DSH\\_probe\\import_skills.mjs`（**import 插件自己的 `@michengai/dsh-skills-manager\\lib\\core.js` 的 `importSkill`**，`--dirs` 逐个装、`--dry` 预演）导入用户技能根 —— 走插件自己的代码，落盘格式与「设置 → 技能」一致。
3. **两层结构要拆开传**：`mattpocock/skills` 是 `skills\\<组>\\<name>\\`，插件 batch 语义只认一层 → 按组目录分别传，否则 `error.import.emptySource`。
4. **副本要避重**：`ui-ux-pro-max-skill` 的 `.claude\\skills\\*` 与 `cli\\assets\\skills\\*` 同名 → 只导前者，导后者报 `error.import.duplicateName`。
5. **EPERM 可重试**：`EPERM: operation not permitted, rename '<root>\\.<name>.dssm-stage-<uuid>' -> '<root>\\<name>'` 是暂存目录改名的瞬时占用（杀软/索引），原样重试即成功（8 个里 7 个），顽固的用 `Copy-Item -Recurse -Force` 兜底；无 `.dssm-stage-*` 残留。
6. **目录名太泛先改名**：`panniantong/agent-reach` 的技能文件在 `agent_reach\\skill\\SKILL.md` → 先拷到 `_skillinstall\\_named\\agent-reach` 再导，避免落成 `skill`。

### 12.3 路由同步（AGENTS.md）

新增的 71 个技能已写入 `~/.dsh/AGENTS.md` 第二节 **F 区「10-14 新增批次」**（按用途分组：写代码 / 拆计划 / 评审 / 排错 / 读代码库 / 前端审美 / 品牌平面 / 写作 / 调研 / 压测 / 交接 / 环境 / 教学 / 输出纪律），避免「装了但路由表不知道」。

同时修正了三处**加载不到的名字**（原表按文件存在与否判定，实际 `skill()` 取不到）：

| 位置 | 旧写法 | 新写法 | 原因 |
| --- | --- | --- | --- |
| 第一节 A 区 | `学霸笔记` | `scholar-notes` | frontmatter 名是中文「学霸笔记」，会话技能目录用的是**目录名** |
| 第一节 A 区 | `code` / `learn` / `game-study` / `ml` / `quant` | ⚠️ `stage-panel` 的**子模式**（按文件读 `…\\stage-panel\\submode\\<name>\\SKILL.md`） | 子模式文档**没有 frontmatter**，不是独立技能 |
| 第一节 A 区 | `dsh-craft-your-textbook` | ⚠️ 按文件读 `…\\node_modules\\dsh-craft-your-textbook\\resources\\SKILL.md` | 该插件的技能根是 `resources\\`，不进标准会话目录 |

### 12.4 复核证据（10-14 实跑）

- `_probe\\skill_roots_summary.py` → `roots: 144`；`active=144 inactive=0`
- `_probe\\classify_skills_1014.py`（新增）→ 用户根 74 目录按仓库分组，**缺 `SKILL.md` 的：无**，合计 14.25 MB
- `_probe\\skill_coverage.py` / `_probe\\verify_agents_names.py` → 见 12.5 的口径变化
- `inventory-skills.py` 重跑 → `_probe\\skills-inventory.json`（144 条，字段含 `active`）

### 12.5 遗留与口径

- **checker 的参照物升级**：`verify_agents_names.py` 原来拿 `skills-inventory.json`（递归扫 `SKILL.md`）当现实，会把「文件存在但 `skill()` 取不到」的名字判成 ✅ —— 10-14 起同时给出 **`loadable` 判据**（`name == 目录名` 且父目录是技能根），加载不到的必须带 ⚠️ 标注。
- **暂存未清**：`D:\\Resources\\DSH\\_skillinstall\\`（7 个仓库 + `_named`）保留，便于重装与比对；确认不需要后可删（约 35 MB）。
- **待办**：Hindsight 记忆库仍未配置 token（401），本批变更尚未 ingest。
"""

if "## 十二、10-14 技能扩容" not in r:
    r = r.rstrip("\n") + CHAPTER12

open(REPORT, "w", encoding="utf-8", newline="\n").write(r)
print("报告已更新:", len(r.encode("utf-8")), "B /", r.count("\n") + 1, "行")

# ---------------------------------------------------------------- B) AGENTS.md
a = open(AGENTS, encoding="utf-8").read()
backup(AGENTS)

a = sub(
    a,
    "| 学霸笔记 / 手写笔记风学习材料 | `学霸笔记` | — | — |",
    "| 学霸笔记 / 手写笔记风学习材料 | `scholar-notes`（frontmatter 名是「学霸笔记」，**调用要用目录名 `scholar-notes`**） | — | — |",
    "agents-scholar",
)

a = sub(
    a,
    "| 把资料变成自己的教材 / 讲义 | `dsh-craft-your-textbook` | 企业培训师 | — |",
    "| 把资料变成自己的教材 / 讲义 | ⚠️ `dsh-craft-your-textbook`（**不在会话技能目录**，按文件读 `…\\node_modules\\dsh-craft-your-textbook\\resources\\SKILL.md`） | 企业培训师 | — |",
    "agents-textbook",
)

OLD_SUBMODE = """| 编程学习 / 教学代码演示 | `code`、`learn` | — | `openmaic_widget`(code) |
| 游戏化学习 / 知识点闯关 | `game-study` | — | `openmaic_widget`(game) |
| 机器学习 / 量化教学 | `ml`、`quant` | — | — |"""
NEW_SUBMODE = """| 编程学习 / 教学代码演示 | ⚠️ `stage-panel` 子模式 `code` / `learn`（**不是独立技能**，按文件读 `…\\@arcaneorion\\dsh-teaching-board\\skills\\stage-panel\\submode\\code\\SKILL.md`，子模式无 frontmatter、`skill()` 取不到） | — | `openmaic_widget`(code) |
| 游戏化学习 / 知识点闯关 | ⚠️ 同上，子模式 `game-study`（`…\\submode\\game-study\\SKILL.md`） | — | `openmaic_widget`(game) |
| 机器学习 / 量化教学 | ⚠️ 同上，子模式 `ml` / `quant`（`…\\submode\\ml\\SKILL.md`、`…\\submode\\quant\\SKILL.md`） | — | — |"""
a = sub(a, OLD_SUBMODE, NEW_SUBMODE, "agents-submode")

SECTION_F = """### F. 10-14 新增批次（7 个 GitHub 仓库 / 71 个技能）

> 全部装在用户技能根 `C:\\Users\\Administrator\\.dsh\\skills\\`，**可直接 `skill(<name>)`**。完整明细（含「目录名 ≠ frontmatter 名」的 11 处）见 `D:\\Resources\\DSH\\技能现状速查.md` 第八节。

| 触发信号 | 技能 |
| --- | --- |
| 写实现 / 加功能 | `implement`、`implement-spec`、`tdd`、`prototype`、`migrate-to-shoehorn` |
| 拆计划 / 写票据 / 铺脚手架 | `to-spec`、`to-tickets`、`wayfinder`、`triage`、`wizard`、`scaffold-exercises` |
| 代码评审 / 架构与建模 | `code-review`、`improve-codebase-architecture`、`codebase-design`、`domain-modeling` |
| 排错 / 定位难 bug | `diagnosing-bugs` |
| 读陌生代码库（知识图谱） | `understand`（+ `understand-chat` / `-dashboard` / `-diff` / `-domain` / `-explain` / `-figma` / `-knowledge` / `-onboard`） |
| 前端 / 审美 / 反 AI 味设计 | `design-taste-frontend`（v2 默认）、`design-taste-frontend-v1`、`design-taste-frontend-v2-experimental`、`ui-ux-pro-max`、`ui-styling`、`high-end-visual-design`、`minimalist-ui`、`industrial-brutalist-ui`、`redesign-existing-projects`、`stitch-design-taste`、`gpt-taste`、`image-to-code`、`imagegen-frontend-web`、`imagegen-frontend-mobile` |
| 品牌 / 平面 / 幻灯片 | `design`、`design-system`、`brand`、`brandkit`、`banner-design`、`slides`、`frontend-slides` |
| 写文章 / 去 AI 味 | `humanizer`、`writing-fragments`、`writing-beats`、`writing-shape`、`writing-for-agents`、`pr` |
| 联网调研 / 查资料 | `agent-reach`（16 平台）、`research` |
| 压测想法 / 逼问细节 | `grilling`、`grill-me`、`grill-with-docs`、`ask-matt`、`wait-what` |
| 交接 / 复盘 / 长任务 | `handoff`、`claude-handoff`、`chief-of-staff`、`loop-me`、`retro` |
| 环境与提交纪律 | `setup-matt-pocock-skills`、`setup-pre-commit`、`setup-ts-deep-modules`、`git-guardrails-claude-code` |
| 教学 / 问卷化 | `teach`、`to-questionnaire` |
| 输出纪律（别偷懒截断） | `full-output-enforcement` |

**⚠️ 调用名规则**：`skill()` 用的是**会话技能目录里的名字** —— frontmatter `name` 是 ASCII 时用它（如 `taste-skill` 目录要调 `design-taste-frontend`），是中文等非 ASCII 时回落到**目录名**（如 `scholar-notes`）。**目录名与调用名不一致是正常的**，两者都要认；名字不在目录里就按文件读 `SKILL.md`，不要判成不存在。

"""

a = sub(a, "\n---\n\n## 三、专家调用规则", "\n" + SECTION_F + "---\n\n## 三、专家调用规则", "agents-sectionF")

a = sub(
    a,
    "- **工作区约定**：`D:\\Resources\\DSH` 为工作区；自建技能在 `C:\\Users\\Administrator\\.dsh\\skills\\`。",
    "- **工作区约定**：`D:\\Resources\\DSH` 为工作区；自建技能在 `C:\\Users\\Administrator\\.dsh\\skills\\`（10-14 起该根共 **74** 个技能，含导入的 71 个）。\n- **技能名以会话技能目录为准**：全机 144 个 `SKILL.md`，但 `skill()` 只认目录里的名字；`ppt-studio-*`（预设隔离）、`stage-panel` 子模式、`dsh-craft-your-textbook`（技能根是 `resources\\`）都只能按文件读，详见 `D:\\Resources\\DSH\\技能现状速查.md` 第七节。",
    "agents-notes",
)

open(AGENTS, "w", encoding="utf-8", newline="\n").write(a)
print("AGENTS.md 已更新:", len(a.encode("utf-8")), "B /", a.count("\n") + 1, "行")
