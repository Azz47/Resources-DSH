# -*- coding: utf-8 -*-
"""把「以 dsh-codex-ui 家族为基准」的 v2 整合结果写回 ~/.dsh/AGENTS.md。

只做 4 处定点替换（每处必须唯一命中，否则整体不写），先备份再落盘：
  1. D 区「出 PDF / Word / Excel / 排版」行 → 补全 8 个 univer-* 技能
  2. C 区「上手陌生代码库」行        → 补 hindsight-coding-agent
  3. E 区「建/改/验证技能」后        → 新增「管技能」与「查项目记忆」两行
  4. 五、注意事项                   → 新增「技能启停入口唯一」一条
"""
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"C:\Users\Administrator\.dsh\AGENTS.md"
BAK = P + ".bak-before-codexui-family-v2"

R = []

R.append((
    "| 出 PDF / Word / Excel / 排版 | — | **文档工程师** | `load_workspace_dependencies` |",
    "| 出 PDF / Word / Excel / PPT / 排版 | `univer`（总入口）；按件取 `univer-doc`（Word）、"
    "`univer-sheet`（表格）、`univer-slide`（幻灯片）、`univer-base`（多维表）、`univer-board`（画布/白板）、"
    "`univer-embed`（嵌入）、`univer-cross-unit-formula`（跨表公式） | **文档工程师** | "
    "`univer_*`（new/status/import/execute/inspect/screenshot/export/print_pdf/compile_svg）、`load_workspace_dependencies` |",
))

R.append((
    "| 上手陌生代码库 / 讲清调用链 | — | **工程效率工程师** | — |",
    "| 上手陌生代码库 / 讲清调用链 / 查项目既有决策与约定 | `hindsight-coding-agent` | **工程效率工程师** | "
    "`hindsight_*`（list/search/read knowledge pages、reflect、ingest_document） |",
))

R.append((
    "| 建 / 改 / 验证技能 | 加载 `writing-skills` |",
    "| 建 / 改 / 验证技能 | 加载 `writing-skills` |\n"
    "| 管技能（启用/停用/导入/仓库/回滚） | 设置 → 技能（@michengai/dsh-skills-manager）：全局/项目分栏、"
    "ZIP 或文件夹或 SKILL.md 导入、GitHub 技能仓库、回收站与版本回滚；**启停只写本地策略，不动源 SKILL.md** |\n"
    "| 查项目记忆 / 沉淀决策与经验 | 加载 `hindsight-coding-agent`；先 `hindsight_search_knowledge_pages` "
    "或 `hindsight_reflect`，新结论用 `hindsight_ingest_document` 落库 |",
))

R.append((
    "- **加载技能用 `skill` 工具**：按目录里的准确名字直接加载，不要为了找技能去全盘搜索或递归调用路由。",
    "- **加载技能用 `skill` 工具**：按目录里的准确名字直接加载，不要为了找技能去全盘搜索或递归调用路由。\n"
    "- **技能启停入口唯一**：设置 → 技能（@michengai/dsh-skills-manager；停用 = 模型侧不可见，源文件不动）。"
    "侧栏旧「技能中心」（@linxin666/dsh-client-ui-skill-explorer）已停用，`dsh-echocat-skill-panel` 未启用。",
))

s = open(P, encoding="utf-8").read()
before = len(s.encode())
shutil.copy2(P, BAK)

for i, (old, new) in enumerate(R, 1):
    n = s.count(old)
    if n != 1:
        raise SystemExit("ABORT: 第 %d 处模式命中 %d 次，未写入任何内容" % (i, n))
    s = s.replace(old, new)

open(P, "w", encoding="utf-8", newline="").write(s)

after = len(s.encode())
print("AGENTS.md %d -> %d bytes (backup: %s)" % (before, after, BAK))
print()
for i, line in enumerate(s.split("\n"), 1):
    if "univer" in line or "hindsight" in line or "skills-manager" in line or "技能中心" in line:
        print("%3d| %s" % (i, line))
print()
missing = [n for n in ("hindsight-coding-agent", "univer", "univer-base", "univer-board",
                       "univer-cross-unit-formula", "univer-doc", "univer-embed", "univer-sheet",
                       "univer-slide") if n not in s]
print("原先缺引用的 9 个技能现在缺失:", missing if missing else "无（全部已引用）")
