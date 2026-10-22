# -*- coding: utf-8 -*-
"""10-14 晚同步：下载姿势改进（blobless+sparse）与 officecli CLI 已安装，落到三份文档。
每处替换断言恰好命中 1 次，否则整体不写。改前留 .bak-before-cli-20261014。
"""
import io
import os
import shutil
import sys

SUFFIX = ".bak-before-cli-20261014"

ROUTING = r"C:\Users\Administrator\.dsh\skills\daofa-lesson-prep\references\skill-routing.md"
QUICK = r"D:\Resources\DSH\技能现状速查.md"
REPORT = r"D:\Resources\DSH\环境盘点与整合方案.md"

# ---- A. skill-routing.md ----
A1_OLD = "| `github.com:443` | ❌ **连接超时**（`git clone` → `error: RPC failed; curl 56 Recv failure: Connection was reset`） | `github:` 规格装插件必失败 → 走 ZIP 通道。**首选镜像** `https://gh-proxy.com/https://github.com/<owner>/<repo>/archive/refs/heads/main.zip`（实测 277 KB/s；ghfast.top 216、ghproxy.net 69 KB/s；hub.gitmirror.com / gh.llkk.cc 不通）；codeload 直连仅 25–36 KB/s **且忽略 Range，不能续传** |"
A1_NEW = "| `github.com:443` | ⚠️ **可直连但吞吐差**（10-14 晚复核：blobless clone 成功，约 33 KB/s） | ①**只取技能目录时首选 blobless + sparse**：`pwsh -File D:\\Resources\\DSH\\_probe\\sparse_fetch_skill.ps1 -Repo <owner>/<repo> -Path skills -Dest <目录>` —— OfficeCLI 技能本体只有 121 文件 / 1.62 MiB，同一仓库整仓 ZIP 是 78.7 MB；②要整仓才走镜像 ZIP `https://gh-proxy.com/https://github.com/<owner>/<repo>/archive/refs/heads/main.zip`（277 KB/s；ghfast.top 216、ghproxy.net 69；hub.gitmirror.com / gh.llkk.cc 不通）；codeload 直连仅 25–36 KB/s **且忽略 Range，不能续传** |"

A2_OLD = "| **Office 文档读写与体检** | `officecli`（总入口）→ `officecli-docx` / `-xlsx` / `-pptx` | ⚠️ **需先装外部 CLI `officecli`（本机未装）**，否则只能读手册；`office-*`（univer 系）不需要外部 CLI |"
A2_NEW = "| **Office 文档读写与体检** | `officecli`（总入口）→ `officecli-docx` / `-xlsx` / `-pptx` | ✅ **外部 CLI 已装**：`C:\\Users\\Administrator\\AppData\\Local\\OfficeCLI\\officecli.exe`（1.0.157，已进用户 PATH）；首次运行**自动刷新这 11 个技能的 94 个文件**，此后不必再跟 GitHub 更新；`office-*`（univer 系）不需要外部 CLI |"

# ---- B. 技能现状速查.md ----
B1_OLD = "2. **`github.com:443` 超时**（`git clone` → `error: RPC failed; curl 56 Recv failure: Connection was reset`），但 `api.github.com` 与 `codeload.github.com` 通 —— 本机走 **ZIP 通道**下载；下载必须带 `--connect-timeout 15 --max-time 300` 并确认不是 0 字节。"
B1_NEW = "2. **`github.com:443` 当时超时**（`git clone` → `error: RPC failed; curl 56 Recv failure: Connection was reset`），故改走 ZIP 通道；**10-14 晚复核已可直连**（blobless clone 成功，约 33 KB/s）—— 只取技能目录请用 **blobless + sparse**（见第十节），要整仓才走镜像 ZIP。下载一律带 `--connect-timeout 15 --max-time 300` 并确认不是 0 字节。"

B2_OLD = "**⚠️ 前置依赖（未装）**：`officecli*` 与 `morph-ppt*` 这 11 个技能驱动的是**外部 CLI `officecli`**（SKILL.md 里的命令都是 `officecli ...`），本机 `officecli` **不在 PATH**。文档给的装法：`irm https://d.officecli.ai/install.ps1 | iex`，或从 `https://github.com/iOfficeAI/OfficeCLI/releases` 取二进制，或用 npm 的 `officecli@0.2.121`。**未擅自执行远程安装脚本** —— 装之前这 11 个只能读手册。"
B2_NEW = "**✅ 前置依赖已补齐（10-14 晚）**：`officecli*` 与 `morph-ppt*` 这 11 个技能驱动的**外部 CLI `officecli` 已安装** —— `C:\\Users\\Administrator\\AppData\\Local\\OfficeCLI\\officecli.exe`（**1.0.157**，33,513,384 B，SHA256 与官方 `SHA256SUMS` 一致，已进用户 PATH）。**未执行远程 `install.ps1`**，改用官方 release 二进制；首次运行该二进制即**自动刷新这 11 个技能目录的 94 个文件**（技能与二进制版本对齐）→ 这批技能此后不必再跟 GitHub。冒烟测试：`officecli create x.docx` → 5,184 B、`get /` 返回 document/body/styles/numbering。详见第十节。"

B_APPEND = """
---

## 十、10-14 晚：下载姿势改进 + `officecli` CLI 安装

**1. 卡点不是带宽，是「整仓下载」这个动作。** 技能本体常只占整仓几十分之一：`iOfficeAI/OfficeCLI` 整仓 ZIP **78,714,337 B**，技能本体只要 **121 文件 / 1,703,082 B（1.62 MiB）**。

| 通道 | 取到什么 | 体量 | 耗时 | 结论 |
| --- | --- | --- | --- | --- |
| 镜像整仓 ZIP（`gh-proxy.com`） | 整仓（技能的 1/40 有用） | 78,714,337 B | 66 s | 兜底，不首选 |
| **blobless + sparse** | 只有 `skills\\` + 根散件 | **1.62 MiB**（+ ≈0.2 MB） | 22 s | ✅ **首选** |
| 官方镜像二进制（`d.officecli.ai`） | `officecli-win-x64.exe` | 33,513,384 B | 161 s（208 KB/s） | 取二进制用这条 |

落地脚本：**`D:\\Resources\\DSH\\_probe\\sparse_fetch_skill.ps1`**（`-Repo` / `-Path` / `-Dest` / `-ExtraFiles` / `-Branch`；目标已存在则拒绝覆盖；断线重跑即补齐）。`github.com:443` **现在直连可用**（旧文档的「连接超时」是当时的瞬时状态，已修正）。

**2. `officecli` CLI（11 个技能的前置）**

| 项 | 证据 |
| --- | --- |
| 版本 | `officecli --version` → **1.0.157** |
| 落盘 | `C:\\Users\\Administrator\\AppData\\Local\\OfficeCLI\\officecli.exe`，已追加进**用户 PATH** |
| 完整性 | SHA256 `bd64eba587e56cc71709cdd1f38ae9ac77cd65a9c8ea744b0996897c0557e343` **=** 官方 `SHA256SUMS` 的 `officecli-win-x64.exe` 行 |
| 自刷新 | 首次运行输出 `refreshed 94 skill file(s) after upgrade`（11 个技能目录）→ 技能与二进制对齐 |
| 冒烟 | `officecli create` → 5,184 B docx；`officecli get <f> /` 正常返回 document 树 |
"""

# ---- C. 环境盘点与整合方案.md ----
C_OLD = """### 13.5 遗留

1. **`officecli` CLI 未安装** —— `officecli*` / `morph-ppt*` 共 11 个技能目前只能读手册；装法见 13.4 的 G 区警告（**未擅自运行远程 install.ps1**）。
2. `dshmarket` 可更新（1.66.10 → 1.66.21）；其余 33 个依赖已是最新；`@haoranwang0921/dsh-session-cleaner`、`@openmaic/dsh-openmaic` 在 npm 404（未发布/私有来源）。
3. `D:\\Resources\\DSH\\_skillinstall_1014b\\` 两个 ZIP（约 135 MB）保留未删。
4. 技能更新检测：**最新 26 / 仅换行差异 44 / 真实差异 2（均为「本机多」）/ 上游有本机未装 12** —— 无上游更新需要拉取。
5. Hindsight 记忆库仍无 token（401），本系列文档尚未入库。"""

C_NEW = """### 13.5 下载姿势改进与 `officecli` CLI 安装（10-14 晚）

**卡点诊断**：整仓下载不是网络问题，是动作选错 —— 技能本体常只占整仓的几十分之一；`iOfficeAI/OfficeCLI` 整仓 ZIP **78,714,337 B**，技能本体只要 **121 文件 / 1,703,082 B（1.62 MiB）**。

| 通道 | 取到什么 | 体量 | 耗时 | 结论 |
| --- | --- | --- | --- | --- |
| 镜像整仓 ZIP（`gh-proxy.com`） | 整仓（只有 1/40 是技能） | 78,714,337 B | 66 s | 兜底，不首选 |
| **blobless + sparse**（`git clone --filter=blob:none --no-checkout --depth 1` + `sparse-checkout init --cone` + `set skills` + `checkout`） | 只有 `skills\\` + 根散件 | **1.62 MiB**（+ ≈0.2 MB） | 22 s | ✅ **首选** |
| 官方镜像二进制（`d.officecli.ai`） | `officecli-win-x64.exe` | 33,513,384 B | 161 s（208 KB/s） | 取二进制用这条 |

- 落地脚本：**`D:\\Resources\\DSH\\_probe\\sparse_fetch_skill.ps1`**（`-Repo` / `-Path` / `-Dest` / `-ExtraFiles` / `-Branch`；目标已存在则拒绝覆盖；断线重跑即补齐）。
- **纠正旧结论**：`github.com:443` 现在直连可用（blobless clone 实测成功），只是吞吐约 33 KB/s；旧文档的「连接超时」是当时的瞬时状态，已同步修正 `skill-routing.md` 第四节。

**CLI 安装（补齐 11 个 `officecli*` / `morph-ppt*` 技能的前置）**

| 项 | 证据 |
| --- | --- |
| 版本 | `officecli --version` → **1.0.157** |
| 落盘 | `C:\\Users\\Administrator\\AppData\\Local\\OfficeCLI\\officecli.exe`（33,513,384 B），已追加进**用户 PATH** |
| 完整性 | SHA256 `bd64eba587e56cc71709cdd1f38ae9ac77cd65a9c8ea744b0996897c0557e343` = 官方 `SHA256SUMS` 的 `officecli-win-x64.exe` 行（**match=True**） |
| 首次运行 | `refreshed 94 skill file(s) after upgrade` —— 11 个技能目录被自动刷新、与二进制版本对齐 ⇒ 这批技能**不需要再跟 GitHub 更新** |
| 冒烟测试 | `officecli create x.docx` → 5,184 B；`officecli get x.docx /` 正常返回 document / body / styles / numbering 树（`extended.application=OfficeCLI/1.0.157`） |

### 13.6 遗留

1. ~~`officecli` CLI 未安装~~ → **已装并自检通过**（见 13.5）；未执行远程 `install.ps1`，改用官方 release 二进制 + SHA256 校验。
2. `dshmarket` 可更新（1.66.10 → 1.66.21）；其余 33 个依赖已是最新；`@haoranwang0921/dsh-session-cleaner`、`@openmaic/dsh-openmaic` 在 npm 404（未发布/私有来源）。
3. 下载产物保留未删：`_skillinstall_1014b\\` 两个 ZIP（约 135 MB）、`_skillinstall_sparse\\OfficeCLI\\`（技能本体 + 33.5 MB 二进制 + `.git`）。
4. 技能更新检测：**最新 26 / 仅换行差异 44 / 真实差异 2（均为「本机多」）/ 上游有本机未装 12** —— 无上游更新需要拉取；`officecli*` / `morph-ppt*` 改由 CLI 自刷新，不再手动跟仓库。
5. Hindsight 记忆库仍无 token（401），本系列文档尚未入库。"""

JOBS = [
    (ROUTING, A1_OLD, A1_NEW, "skill-routing: github.com:443 行"),
    (ROUTING, A2_OLD, A2_NEW, "skill-routing: officecli 前置依赖行"),
    (QUICK, B1_OLD, B1_NEW, "速查: 坑 2 github 超时"),
    (QUICK, B2_OLD, B2_NEW, "速查: 第九节 前置依赖"),
    (REPORT, C_OLD, C_NEW, "报告: 13.5 重写为下载姿势+CLI，13.6 遗留"),
]

def main():
    blobs = {}
    for path in {p for p, _, _, _ in JOBS} | {QUICK}:
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            blobs[path] = fh.read()

    for path, old, new, label in JOBS:
        n = blobs[path].count(old)
        if n != 1:
            print("FAIL  %-42s 命中 %d 次（应为 1）" % (label, n))
            return 1
        blobs[path] = blobs[path].replace(old, new)
        print("ok    %-42s 1 处" % label)

    if B_APPEND.strip() not in blobs[QUICK]:
        blobs[QUICK] = blobs[QUICK].rstrip("\n") + "\n" + B_APPEND
        print("ok    %-42s 追加第十节" % "速查: 新增第十节")

    for path, text in blobs.items():
        if not os.path.exists(path + SUFFIX):
            shutil.copy2(path, path + SUFFIX)
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        n_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        print("write %-46s %6d B / %d 行" % (os.path.basename(path), len(text.encode("utf-8")), n_lines))
    return 0

if __name__ == "__main__":
    sys.exit(main())
