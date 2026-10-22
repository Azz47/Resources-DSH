# 动效库 · motion-patterns

> 用途：给一册 PPT 决定「用什么动、动多久、哪里不动」。
> 数据来源：27 套 morph-ppt 样式模板、3 份 GitHub 高星中文模板、本机两册参赛件、`morph-ppt` 技能规则、`ppt-animation`/`frontend-slides` 的网页动效纪律（2026-10-18 实测）。

---

## 0. 三句话

1. **动效分三层**：跨页连续（morph）＞ 页间转场（fade）＞ 页内进场（appear/stagger）。层级越高，叙事价值越大，翻车成本也越高。
2. **静态模板几乎不带动效**：3 份网络样本里 2 份只有 fade（18 处 / 0 处），27 套样式库全部 fade。动效必须自己写，不能指望模板。
3. **动效是节奏器，不是装饰**：一页一个主角、一组进场；观众 1 秒内要能定位到新信息，否则就是噪声。

---

## 1. 实测基线（先看证据再定规则）

| 来源 | 样本 | 转场实测 | 结论 |
|---|---|---|---|
| morph-ppt 样式库 | 27 套 .pptx | 全部 `<p:transition><p:fade/></p:transition>`，每套 8–12 处 | 静态模板只给 fade，不含 morph |
| GordenPPTSkill `data-viz-deck` | 41 页 | fade × 18 | 数据汇报件用 fade 足够 |
| GordenPPTSkill `report-massive-charts` | 38 页 | 无转场 | 图表件甚至可以零转场 |
| GordenPPTSkill `red-teaching-framework` | 30 页 | 待回读（见 §6） | 教学件转场少而稳 |
| 本机参赛件 v2 | 45 页 | fade 45 处，其中 6 页 `spd="slow"`（第 1/6/15/23/35/44 页） | 结构页慢、正文页快的分层做法已落地 |
| 本机参赛件 v1 | 46 页 | fade 46 处，5 页 slow | 同上，v1 已验证 |

**推论**：`fade + 结构页 slow` 是安全基线；`morph` 是我们还没用、但观众最能感知的一层。

---

## 2. 页间转场选型

| 场景 | 用什么 | 参数 | 备注 |
|---|---|---|---|
| 正文页（大多数） | fade | 默认（约 0.75 s） | 不抢注意力 |
| 章节扉页 / 封面 / 收束页 | fade | `spd="slow"`（约 1.5–2 s） | 给观众"换气"的时间 |
| 同一元素跨页演进（数字长大、地图推进、结构拆解） | **morph** | `transition=morph` 或 `morph-slow` / `morph-1500` | 需要形状同名，见 §4 |
| 并列对比页之间 | 无转场 | — | 靠版式差异区分，别用 push 左右滑 |
| 目录 → 章节 | fade slow | — | 不要旋转、翻转、立方体 |

**禁用**：push / cover / wipe / split / 旋转 / 立方体 / 棋盘 / 随机。它们只增加眩晕，不增加信息。

---

## 3. 页内进场（元素级）

- **一组进场，不做逐字**：标题先、内容组后，同组元素 **同时**出现（PowerPoint 里用"与上一动画同时"）。
- **节奏**：单页进场总时长 **≤ 2.5 s**；元素间延迟 **80–120 ms**（网页复刻用 `--i * 90ms` 已验证顺眼）。
- **缓动**：`ease-out`（快进慢停）。禁用弹跳、回弹、旋转进入。
- **与讲稿对齐**：1 页/分钟的节奏下，进场必须在老师说第一句话之前完成；否则改为"点击触发"。
- officecli 侧：`officecli help pptx animation`（preset / trigger / duration），命令示例
  `officecli set deck.pptx /slide[3]/shape[@name=#s3-card] --prop animation=appear --prop animationTrigger=afterPrevious --prop animationDuration=400`（属性名以 `help` 为准）。

---

## 4. morph 配方（硬规则 7 条）

1. **同名配对**：相邻两页上要插值的形状必须同名，且同属 `!!` 前缀体系；`!!scene-*` 与 `!!actor-*` 不得重名。
2. **只在需要连续叙事的页用**：≥2 张相邻页共享一个"会变形"的元素；单页装饰不要 morph。
3. **空间位移要够**：相邻页至少位移 ≥5 cm、或旋转 ≥15°、或尺寸变化 ≥30%（≥3 个配对形状），否则 morph 退化成 fade（静默失败）。
4. **入场即命名**：新元素第一次出现的那页也要带 `transition=morph`，否则从 fade 跳变。
5. **Ghost 纪律**：`!!` 形状一旦出现，后续每页都会显示；退场要显式移到 `x=36cm`（画布右侧外），不要删除。
6. **同时性**：同一对 morph 形状严格同时运动，没有单形状延迟；需要错峰就插中间关键帧页。
7. **图表只动框**：图表可整体位移/缩放，但不能插值数据；要"柱子长高"就用手工矩形（`!!actor-bar-K` 同名跨页改宽高）。

**命令（officecli 1.0.157 实测回读正常）**

```bash
officecli set deck.pptx "/slide[2]" --prop transition=morph            # 默认
officecli set deck.pptx "/slide[2]" --prop transition=morph-slow       # 回读 transitionSpeed=slow
officecli set deck.pptx "/slide[2]" --prop transition=morph-1500       # 回读 transitionDuration=1500
officecli query deck.pptx "/slide[2]" --prop transition                # 自证
```

**渲染前提**：morph 需要 PowerPoint 365 / Keynote / WPS；LibreOffice 预览会看不到（汇报前要用真渲染器核对一次）。

---

## 5. 禁忌清单（8 条）

1. 逐字/逐词飞入（观众会读字，不听讲）。
2. 一页里三组以上不同方向进场。
3. 进场总时长 > 8 s（拖节奏）。
4. 用 push/wipe/旋转做页间转场。
5. 在 morph 页之间插入普通 fade 页（运动链断裂）。
6. 忘记 ghost 导致形状残留。
7. 用 LibreOffice 预览 morph 后判定"没生效"。
8. 动画压住正文/图注（层级错乱，见 checklist A 段）。

---

## 6. 自检（可复跑）

```bash
# 每页转场类型与时长
python - <<'PY'
import re, zipfile
z = zipfile.ZipFile(r"deck.pptx")
for n in sorted(x for x in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", x)):
    x = z.read(n).decode("utf-8")
    t = re.findall(r"<p:transition([^>]*)>|<p:transition([^>]*)/>", x)
    if t:
        print(n, "".join(a or b for a, b in t).strip())
PY
```

- morph 页数 / fade 页数 / 无转场页数 三者相加应等于总页数。
- `slow` 只出现在结构页（封面、环节扉页、收束）。
- 任意相邻页的 `!!` 名称集合差异要能在 30 秒内讲清（讲不清就是过度设计）。

---

## 7. 学习待办（下一册可验证）

- [ ] 在 v2 的「数据长大」页（p08 高铁里程）做 **2 页 morph 试点**：同一数字框 + 同一条增长线，位移 ≥5 cm。
- [ ] 把结构页 slow 的 6 页收敛为 5 页（目前 1/6/15/23/35/44，按五环节对齐）。
- [ ] 给 `_check_deck.py` 加 `--motion`：统计 morph/fade/无转场与 slow 页分布。
