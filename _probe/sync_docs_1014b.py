#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10-14 第二批（ppt-master / OfficeCLI / human-writing）文档同步。

一次性迁移脚本：下面 OLD 字符串是「被替换的目标」，跑完即可留档。
每处替换必须恰好命中 1 次，否则整体不写。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUICK = r"D:\Resources\DSH\技能现状速查.md"
REPORT = r"D:\Resources\DSH\环境盘点与整合方案.md"
BAK = ".bak-before-batch2-20261014"

REPLACEMENTS = [
    (
        "# 技能现状速查（2026-10-14 实测）",
        "# 技能现状速查（2026-10-14 实测 · 含第二批 3 仓库）",
    ),
    (
        "历史快照（10-07：10 个根 / 64 个；10-08：12 个来源包 / 74 个）只作留档",
        "历史快照（10-07：10 个根 / 64 个；10-08：12 个来源包 / 74 个；10-14 第一批：7 仓库 / 144 个）只作留档",
    ),
    (
        "- **144 个 `SKILL.md`**，来自 **11 个来源组**（插件 **70** + 用户技能根 **74**）",
        "- **157 个 `SKILL.md`**，来自 **12 个来源组**（插件 **70** + 用户技能根 **87**）",
    ),
    (
        "- **生效 144 / 未生效 0**：",
        "- **生效 157 / 未生效 0**：",
    ),
    (
        "- **10-14 扩容**：用户技能根 **3 → 74**（一次导入 7 个 GitHub 仓库共 **71** 个技能）",
        "- **10-14 扩容（两批）**：用户技能根 **3 → 74 → 87** —— 第一批导入 7 个 GitHub 仓库共 **71** 个；第二批 3 个仓库共 **13** 个（`hugohe3/ppt-master` 1、`iOfficeAI/OfficeCLI` 11、`KKKKhazix/human-writing` 1）",
    ),
    (
        "**用户技能根 `C:\\Users\\Administrator\\.dsh\\skills\\`（74，全部可直接 `skill(<name>)`）**",
        "**用户技能根 `C:\\Users\\Administrator\\.dsh\\skills\\`（87，全部可直接 `skill(<name>)`）**",
    ),
    (
        "| **合计** | **74** | 磁盘占用 **14.25 MB**（ui-ux 9.57 / taste 1.97 / frontend-slides 1.67 / Understand 0.57 / mattpocock 0.26 / 自建 0.11 / 其余 0.11） |",
        "| `hugohe3/ppt-master` | 1 | ppt-master（**13,016 文件 / 37.17 MB** 素材库；`name: ppt-master` / `metadata.version: 6.7.0` / MIT，description 是 YAML 折叠块标量 `>`） |\n"
        "| `iOfficeAI/OfficeCLI` | 11 | `officecli` 总入口 + `officecli-{docx,xlsx,pptx,academic-paper,data-dashboard,financial-model,pitch-deck,word-form}` + `morph-ppt`（111 文件，含 27 个 .pptx 模板）/ `morph-ppt-3d`；仓库根 `SKILL.md` 与 `skills\\officecli\\SKILL.md` 字节相同，**只装 `skills\\` 下 11 个** |\n"
        "| `KKKKhazix/human-writing` | 1 | human-writing（中文创作与改稿；用户只给了 `human-writing` 无 owner，按「仓库名完全匹配 + 中文写作定位 + 星数最高」选定；其余候选 n-eriksson / jpeggdev / lguz / TraX22 未采用） |\n"
        "| **合计** | **87** | 磁盘占用 **53.11 MB**（ppt-master 37.17 / ui-styling 5.50 / ui-ux-pro-max 3.48 / frontend-slides 1.67 / taste-skill 1.66 / morph-ppt 1.21 / understand 0.47 / design 0.27 / 其余 1.67） |",
    ),
    (
        "> 74 个目录**全部有 `SKILL.md` 且都有 `name:` 字段**，0 缺失（`_probe\\classify_skills_1014.py` 实跑）。",
        "> 87 个目录**全部有 `SKILL.md`**，0 缺失（`_probe\\size_second_batch.py` 实跑：`user_root_dirs=87  no_skill_md=0  total_bytes=55693317`）。",
    ),
    (
        "- 用户技能根：`C:\\Users\\Administrator\\.dsh\\skills\\`（**74 个技能目录 / 14.25 MB**）",
        "- 用户技能根：`C:\\Users\\Administrator\\.dsh\\skills\\`（**87 个技能目录 / 53.11 MB**）",
    ),
    (
        "- **10-14 新增 71 个**：见第八节与 `AGENTS.md` 第二节 F 区",
        "- **10-14 第一批 71 个**：见第八节与 `AGENTS.md` 第二节 F 区\n"
        "- **10-14 第二批 13 个**：见第九节与 `AGENTS.md` 第二节 G 区（⚠️ `officecli*` / `morph-ppt*` 需先装 `officecli` CLI 才能真正驱动）",
    ),
    (
        "| `_probe\\skill_coverage.py`（现实 → 表） | 技能总数 **144**　已引用 **144**　未引用 **0**（10-14 已把 71 个新技能写进 `AGENTS.md` 第二节 F 区） |",
        "| `_probe\\skill_coverage.py`（现实 → 表） | 技能总数 **157**　已引用 **157**　未引用 **0**（71 个写在 F 区、13 个写在 G 区） |",
    ),
    (
        "| `_probe\\verify_agents_names.py`（表 → 现实） | 技能 **144 个** = **可直接 `skill()` 138 + 只能按文件读 6**",
        "| `_probe\\verify_agents_names.py`（表 → 现实） | 技能 **157 个** = **可直接 `skill()` 151 + 只能按文件读 6**",
    ),
    (
        "| `_probe\\skill_roots_summary.py` | `roots: 144`；`active=144 inactive=0` |",
        "| `_probe\\skill_roots_summary.py` | `roots: 157`；`active=157 inactive=0` |",
    ),
    (
        "| `_probe\\classify_skills_1014.py`（本次新增） | 用户根 74 目录按仓库分组；**缺 `SKILL.md` 的：无**；合计 14.25 MB |",
        "| `_probe\\classify_skills_1014.py`（第一批） | 用户根 74 目录按仓库分组；**缺 `SKILL.md` 的：无**；合计 14.25 MB |\n"
        "| `_probe\\size_second_batch.py`（第二批） | 用户根 **87** 目录、缺 `SKILL.md` **0**、合计 **53.11 MB**（55,693,317 B）；第二批 13 个 = ppt-master 38,971,339 B + morph-ppt 1,268,572 B + human-writing 92,901 B + 其余 10 个单文件（25,711–66,735 B） |\n"
        "| `_probe\\verify_extract_zip.py`（下载完整性） | OfficeCLI **122/122**、ppt-master **13,016/13,016** 条目与上游 tree blob SHA 一致，哈希不符 0、缺失 0 |",
    ),
    (
        "| `inventory-skills.py` | 重跑刷新 `_probe\\skills-inventory.json`（144 条，字段 `source / pkg / dir / path / name / desc / active`） |",
        "| `inventory-skills.py` | 重跑刷新 `_probe\\skills-inventory.json`（**157 条**；本次修了 YAML 块标量 `>` / `\\|` 的 description 解析，否则 ppt-master 的 desc 只会得到 `>`) |",
    ),
    (
        "| 用户技能根 | `C:\\Users\\Administrator\\.dsh\\skills\\` | **74** | 所有会话，直接 `skill(<name>)` |",
        "| 用户技能根 | `C:\\Users\\Administrator\\.dsh\\skills\\` | **87** | 所有会话，直接 `skill(<name>)` |",
    ),
    (
        "「本机只有 3 个技能」这句话只对**用户技能根**成立（10-14 起那里也变成 74 个了）。",
        "「本机只有 3 个技能」这句话只对**用户技能根**成立（10-14 起那里也变成 87 个了）。",
    ),
]

SECTION9 = """
## 九、10-14 第二批（3 个仓库 / 13 个技能）

| 仓库 | 数量 | 导入路径特征 | 备注 |
| --- | --- | --- | --- |
| `hugohe3/ppt-master` | 1 | `skills\\ppt-master\\`（仓库根另有 `.claude-plugin\\`） | 13,016 文件 / 37.17 MB；`metadata.version: 6.7.0`；MIT；自带 Brand/Style/Layout/Deck 工作区与 svg 素材库 |
| `iOfficeAI/OfficeCLI` | 11 | `skills\\<name>\\` | 根 `SKILL.md`（25974 B）与 `skills\\officecli\\SKILL.md` **字节完全相同** → 跳过根文件；除 `morph-ppt`（111 文件）外 10 个都是单文件技能 |
| `KKKKhazix/human-writing` | 1 | 仓库根 `human-writing\\` 即技能 | 中文创作与改稿；用户只给了 `human-writing` 无 owner，按「仓库名完全匹配 + 中文写作定位 + 星数最高」选定 |

| 目录名 | `skill()` 用名 | 说明 |
| --- | --- | --- |
| `ppt-master`（导入时暂存名 `ppt-master-skill`） | `ppt-master` | 导入脚本按**暂存目录名**落盘 → 已 `Move-Item` 改名为 `ppt-master` |
| 其余 12 个 | 与目录名一致 | frontmatter `name` 全为 ASCII |

**⚠️ 前置依赖（未装）**：`officecli*` 与 `morph-ppt*` 这 11 个技能驱动的是**外部 CLI `officecli`**（SKILL.md 里的命令都是 `officecli ...`），本机 `officecli` **不在 PATH**。文档给的装法：`irm https://d.officecli.ai/install.ps1 | iex`，或从 `https://github.com/iOfficeAI/OfficeCLI/releases` 取二进制，或用 npm 的 `officecli@0.2.121`。**未擅自执行远程安装脚本** —— 装之前这 11 个只能读手册。

**本批踩过的坑**

1. **后台作业不传数据**：`run_in_background` 的 pwsh 作业（pwsh-59 / 60 / 78 / 79 / 94）状态一直 running，但目标 zip 长期停在 0 字节；**同一 URL 前台调用立刻正常** → 长下载一律用前台调用。
2. **下载通道实测**：`codeload.github.com` 25–36 KB/s 且**忽略 Range**（不能续传）；jsDelivr 0.3–36 KB/s 极不稳（`data.jsdelivr.com` 403）；镜像 **`gh-proxy.com` 277 KB/s > `ghfast.top` 216 KB/s > `ghproxy.net` 69 KB/s**，`hub.gitmirror.com` 报 `schannel: SEC_E_ILLEGAL_MESSAGE`、`gh.llkk.cc` 超时 → **走 `https://gh-proxy.com/https://github.com/<owner>/<repo>/archive/refs/heads/main.zip`**。结果：OfficeCLI 78,714,337 B（66 s）、ppt-master 56,576,409 B（152 s）。
3. **镜像字节可证未被篡改**：`_probe\\verify_extract_zip.py` 按 GitHub tree 的 blob SHA（`sha1(b"blob <len>\\0" + data)`）逐条校验 ZIP → **OfficeCLI 122/122、ppt-master 13,016/13,016 全通过**；`--strip skills/ppt-master/` 用来对齐 tree 相对路径与 ZIP 内绝对路径，否则会误报 13,013 个缺失（仓库根的 `.env.example` / `requirements.txt` 抢了同名 key）。
4. **YAML 块标量**：ppt-master 的 `description` 用 `>` 折叠标量，`inventory-skills.py` 原来只取到 `>` → 已加 `BLOCK_SCALAR = re.compile(r"^([A-Za-z_-]+):\\s*([>|])[-+]?\\s*$")` 合并后续缩进行。
5. **pwsh 内联 python 会崩**：`strip('\\"\\'')` 这类嵌套引号直接让 PowerShell 报「表达式或语句中包含意外的标记」→ 复杂脚本一律先落 `.py` 文件再跑。
"""

SECTION13 = """
---

## 十三、10-14 第二批：3 个技能仓库 / 13 个技能

### 13.1 账目

| 仓库 | 技能数 | 落地位置 | 体积 |
| --- | --- | --- | --- |
| `hugohe3/ppt-master` | 1（`ppt-master`） | `…\\.dsh\\skills\\ppt-master\\`（导入暂存名 `ppt-master-skill`，已改名） | 13,016 文件 / 37.17 MB |
| `iOfficeAI/OfficeCLI` | 11 | `…\\.dsh\\skills\\`（`officecli` 总入口 + 8 个场景技能 + `morph-ppt` + `morph-ppt-3d`） | 1.49 MB（`morph-ppt` 1.21 MB，含 27 个 .pptx 模板；其余 10 个是单文件，25,974–66,735 B） |
| `KKKKhazix/human-writing` | 1 | `…\\.dsh\\skills\\human-writing\\` | 92,901 B / 11 文件 |

用户技能根：**74 → 87**（自建 3 + 导入 84），合计 **53.11 MB**；全机 **144 → 157 个 `SKILL.md`**，生效 157 / 未生效 0。

### 13.2 下载通道（本机实测，可复用）

| 通道 | 速度 | 备注 |
| --- | --- | --- |
| `github.com`（`git clone`） | — | **不通**：`Failed to connect to github.com:443 after 21049 ms` / `error: RPC failed; curl 56 Recv failure: Connection was reset` |
| `api.github.com` | 通 | 元数据与 tree API；**大仓库的树会吐几 MB，务必 curl 落盘交给脚本解析，不要进上下文** |
| `codeload.github.com` | 25–36 KB/s | **忽略 Range，不能续传**；chunked 且不返回 content-length |
| jsDelivr | 0.3–36 KB/s | 极不稳；`data.jsdelivr.com` 返回 403 |
| **`gh-proxy.com`** | **277 KB/s** | **首选**：`https://gh-proxy.com/https://github.com/<owner>/<repo>/archive/refs/heads/main.zip`，并返回 Content-Length |
| `ghfast.top` | 216 KB/s | 备选 |
| `ghproxy.net` | 69 KB/s | 备选 |
| `hub.gitmirror.com` | — | `schannel: SEC_E_ILLEGAL_MESSAGE` |
| `gh.llkk.cc` | — | 连接超时 |

**⚠️ 后台作业不传数据**：`run_in_background` 的 pwsh 作业（pwsh-59 / 60 / 78 / 79 / 94）状态一直 running，但目标 zip 长期 0 字节；同一 URL 前台调用正常。⇒ **长下载用前台调用**。

### 13.3 完整性校验（证明镜像字节 = 上游）

`_probe\\verify_extract_zip.py` 读 GitHub tree API 的 `size` + `sha`，对 ZIP 内每个条目复算 `sha1(b"blob <len>\\0" + data)` 比对；只解出登记且校验通过的文件，另报「哈希不符 / ZIP 缺 / 额外文件」。

- OfficeCLI：**122 / 122 通过**
- ppt-master：**13,016 / 13,016 通过**
- 哈希不符 0、ZIP 缺 0 ⇒ 镜像下载内容与上游仓库逐字节一致

### 13.4 落在文档与路由上的改动

- `C:\\Users\\Administrator\\.dsh\\AGENTS.md`：新增**第二节 G 区「10-14 第二批（3 个 GitHub 仓库 / 13 个技能）」**（9 行触发→技能路由 + `officecli` CLI 前置依赖警告）；第五节改为「该根共 **87** 个技能 = 自建 3 + 导入 84」与「全机 **157** 个 `SKILL.md`」。现 **16543 B / 186 行**。
- `D:\\Resources\\DSH\\技能现状速查.md`：总数 157 / 87+70，新增**第九节 第二批**（仓库表 + 目录名→调用名 + 前置依赖 + 5 条坑）。
- 本文件本章。
- 复核：`_probe\\skill_coverage.py` → **157 / 已引用 157 / 未引用 0**；`_probe\\verify_agents_names.py` → 技能 **157 = 可直接 `skill()` 151 + 只能按文件读 6**，假名 0、漏路由 0、专家 **27/27**，总判定 **✅ 双向核对通过**。

### 13.5 遗留

1. **`officecli` CLI 未安装** —— `officecli*` / `morph-ppt*` 共 11 个技能目前只能读手册；装法见 13.4 的 G 区警告（**未擅自运行远程 install.ps1**）。
2. `dshmarket` 可更新（1.66.10 → 1.66.21）；其余 33 个依赖已是最新；`@haoranwang0921/dsh-session-cleaner`、`@openmaic/dsh-openmaic` 在 npm 404（未发布/私有来源）。
3. `D:\\Resources\\DSH\\_skillinstall_1014b\\` 两个 ZIP（约 135 MB）保留未删。
4. 技能更新检测：**最新 26 / 仅换行差异 44 / 真实差异 2（均为「本机多」）/ 上游有本机未装 12** —— 无上游更新需要拉取。
5. Hindsight 记忆库仍无 token（401），本系列文档尚未入库。
"""


def main():
    with io.open(QUICK, "r", encoding="utf-8") as fh:
        quick = fh.read()
    with io.open(REPORT, "r", encoding="utf-8") as fh:
        report = fh.read()

    problems = []
    for index, (old, new) in enumerate(REPLACEMENTS, 1):
        hits = quick.count(old)
        if hits != 1:
            problems.append("replacement %d matched %d times: %r" % (index, hits, old[:60]))
    if problems:
        print("ABORT — no file written:")
        for line in problems:
            print("  " + line)
        return 1

    for old, new in REPLACEMENTS:
        quick = quick.replace(old, new, 1)
    if "## 九、10-14 第二批" not in quick:
        quick = quick.rstrip("\n") + "\n" + SECTION9
    if "## 十三、10-14 第二批" not in report:
        report = report.rstrip("\n") + "\n" + SECTION13

    for path, text in ((QUICK, quick), (REPORT, report)):
        if not os.path.exists(path + BAK):
            with io.open(path + BAK, "w", encoding="utf-8", newline="") as fh:
                with io.open(path, "r", encoding="utf-8", newline="") as src:
                    fh.write(src.read())
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("%s -> %d B / %d lines" % (path, len(text.encode("utf-8")), text.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
