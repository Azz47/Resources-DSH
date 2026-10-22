import io, os, shutil, sys

AGENTS = r"C:\Users\Administrator\.dsh\AGENTS.md"
MASTER = r"D:\Resources\DSH\任务工作流总纲.md"

HANDOFF_AGENTS = (
    "**文档 ↔ 动效移交**：产物是 `.pptx` 且用户提到「动效 / 动画 / 演示 / 视频 / 翻页」→ 自动转 P4，不要停在 P6 交付静态文件。要 PPT 原生动效走 `morph-ppt`（`officecli set deck.pptx /slide[N] --prop transition=morph`）；要网页播放走 `python tools/deck2motion.py deck.pptx out/`（抽页 + 生成 HTML 骨架）再交 `ppt-animation` / `frontend-slides` 精修；要逐镜头视频走 `video-shot-demos`。反向（动效脚本 → 可编辑 PPT）用 `officecli` 批量重建。\n"
)

HANDOFF_MASTER = """### 4.1 文档 ↔ 动效 移交（PPT 也走这条）

| 源 | 用户要什么 | 走哪条 | 命令 / 动作 |
| --- | --- | --- | --- |
| `.pptx` 成品 | 文件里自带动效（PowerPoint / WPS 直接播） | `morph-ppt`（officecli 原生 Morph + 形状动画） | `officecli set deck.pptx /slide[2] --prop transition=morph`；形状动画：`officecli help pptx animation` |
| `.pptx` 已有 | 浏览器里播放的动效演示 | `tools/deck2motion.py` 抽页成骨架 → `ppt-animation` / `frontend-slides` 精修 | `python tools/deck2motion.py deck.pptx out/` → `out/index.html` + `out/outline.json` |
| 大纲 / 教案 / md | 从零做动效演示 | `ppt-animation`（PPT 风翻页）/ `video-shot-demos`（逐镜头）/ `card-theater`（卡片叙事） | 按第 7 节矩阵选 |
| 动效脚本 | 要可编辑的 PPT | `officecli` 批量重建 + `transition=morph-*` | batch heredoc，规则见 `morph-ppt` |

**判定**：产物是 `.pptx` 且用户提到「动效 / 动画 / 演示 / 视频 / 翻页」→ 自动进 P4；不要停在 P6 交付静态文件。

**自动化程度**（实测）：① pptx 原生动效＝完全脚本化（officecli）；② pptx→HTML＝抽取与骨架脚本化，视觉重排由模型按 `ppt-animation` 规则完成；③ 大纲→演示＝纯生成，无源文件可抽。

"""


def patch(path, old, new, label):
    s = io.open(path, encoding="utf-8").read()
    assert s.count(old) == 1, f"{label}: anchor count={s.count(old)}"
    s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print(f"{label}: ok  lines={s.count(chr(10)) + 1} bytes={len(s.encode('utf-8'))}")
    return s


agents = patch(
    AGENTS,
    "**三条判定线**：① 需要专业判断 / 多视角 / 高风险 → 必须请专家（第四节）；② ≥3 个互不依赖的子任务 → 并行扇出；③ 能用工具校验的，不靠眼看。\n",
    "**三条判定线**：① 需要专业判断 / 多视角 / 高风险 → 必须请专家（第四节）；② ≥3 个互不依赖的子任务 → 并行扇出；③ 能用工具校验的，不靠眼看。\n\n" + HANDOFF_AGENTS,
    "AGENTS",
)

master = patch(
    MASTER,
    "**默认策略**：单任务串行；拆得开才并行；有专业结论才请专家；能工具校验就不人工目检。\n",
    "**默认策略**：单任务串行；拆得开才并行；有专业结论才请专家；能工具校验就不人工目检。\n\n" + HANDOFF_MASTER,
    "MASTER",
)

# 演示产物归档到非临时目录
src_demo = r"D:\Resources\DSH\_probe\demo"
dst_demo = r"D:\Resources\DSH\demo\deck2motion"
os.makedirs(os.path.dirname(dst_demo), exist_ok=True)
if os.path.isdir(dst_demo):
    shutil.rmtree(dst_demo)
shutil.copytree(src_demo, dst_demo)
print("demo:", dst_demo, "files=", sum(len(f) for _, _, f in os.walk(dst_demo)))
