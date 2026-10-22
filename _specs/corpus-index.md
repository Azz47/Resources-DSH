# 语料索引 · corpus-index

> 本机 PPT 学习资产的总账。更新于 2026-10-18。
> 纪律：**索引只记位置与口径，不复制内容**；源文件改了，改这里的一行即可。

---

## 1. 全景（实测）

| 资产 | 数量 | 体量 | 位置 |
|---|---|---|---|
| 课件语料（1ppt 抓取，去重） | **480 份** | 17,375 页；预览图 1,118 张 | `corpus\1ppt2\`（`index.jsonl` + `images\`） |
| 课件语料（早期批，1ppt） | 80 份（⊂480） | 2,684 页；159 张图 | `corpus\1ppt\` |
| 语料 JSONL（含指标） | 23 条 | 16,247 B | `corpus\corpus.jsonl` |
| 参赛语料 JSONL | 62 条 | 24,346 B | `corpus\contest.jsonl` |
| 样式模板（morph-ppt 技能） | **27 套 .pptx** | 每套 4–7 页，0 媒体 | `C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles\` |
| 网络高星中文模板（本轮下载） | **3 份 .pptx** | 30/41/38 页 | `corpus\_web\gordensun\` |
| 本机参赛件 | 2 册 + 9 份历史 | 45/46 页 | `decks\`、`_archive\20261015-旧工程\` |
| 网页动效样板 | 1 套 | 3 页 HTML | `demo\deck2motion\` |

## 2. 课件语料：按学科（每科 40 份）

| 学科 | 中位页数 | 范围 | 目录键 |
|---|---|---|---|
| 物理 | 53 | 30–76 | `wuli` |
| 英语 | 46 | 27–73 | `yingyu` |
| 化学 | 46 | 31–72 | `huaxue` |
| 历史 | 43 | 18–62 | `lishi` |
| 政治 | 41 | 26–59 | `zhengzhi` |
| 生物 | 41 | 29–70 | `shengwu` |
| 数学 | 39 | 23–53 | `shuxue` |
| 语文 | 28 | 14–50 | `yuwen` |
| 地理 | 26 | 16–52 | `dili` |
| 道法 | 23 | 14–41 | `daode` |
| 班会 | 21 | 15–31 | `banhui` |
| 美术 | 20 | 8–36 | `meishu` |

**读法**：要写哪一科，先看这一科的「中位页数」——高出 30% 就要有理由（推导/实验/语篇），低于 30% 就要担心讲不完。

## 3. 每条语料的结构

`corpus\1ppt2\index.jsonl` 每行：

```json
{"cat":"zhengzhi","url":"https://www.1ppt.com/kejian/139801.html",
 "title":"…PPT优质课件","pages":"28",
 "images":["https://img.1ppt.com/…_1.jpg","…_2.jpg"],
 "saved":["zhengzhi_139801_1_…_1.jpg","…_2.jpg"]}
```

- `pages` 是抓取页声明的页数（用于体量统计，不代表本地有全部页）。
- `images` 只有 2 张预览图/份 —— **不能**据此还原版式；版式结论以 27 套 .pptx + 我们自己的件为准。
- 版权：预览图仅作内部学习/统计，不二次分发；引用页码可以，整页搬运不行。

## 4. 样式模板：27 套的风格谱

`reference\styles\<family>--<name>\*.pptx`，family 六类：`bw`(3) / `dark`(16) / `light`(4) / `vivid`(2) / `warm`(3) / `mixed`(1)。

每套 4–7 页、0 媒体、纯矢量；颜色是**显式 RGB**（不走主题），所以可以逐套抄色板。逐套数据见 `_specs\_learn_styles.md`。

## 5. 网络样本（高星）

| 仓库 | 星 | 许可 | 取用 |
|---|---|---|---|
| `hugohe3/ppt-master` | **63,284** | MIT | 已作为技能安装（本机 `skills\ppt-master`），未重复下载 |
| `GordenSun/GordenPPTSkill` | **3,669** | NOASSERTION（自定，转载前查） | 下载 3 份到 `corpus\_web\gordensun\` 仅作学习 |

下载清单：`data-viz-deck.pptx`(41 页/14 表)、`report-massive-charts.pptx`(38 页)、`red-teaching-framework.pptx`(30 页/55 图/78 形状每页)。

## 6. 怎么查（脚本）

```bash
PY='C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
"$PY" _probe\learn_corpus_images.py     # 480 份语料 + 1,118 图的统计
"$PY" _probe\learn_styles.py            # 27 套样式的色板/字号/形状密度
"$PY" _probe\learn_web_templates.py     # 网络样本解剖
"$PY" _probe\measure_density.py         # 4 份 pptx 的形状/页对照 + 标题词频
```

产物：`_specs\_learn_corpus.md`、`_learn_styles.md`、`_learn_web.md`（脚本生成，勿手改）。

## 7. 更新与新增

1. 新抓一批课件 → 追加到 `corpus\1ppt2\index.jsonl`，重跑 `learn_corpus_images.py`。
2. 新看到一个好样式 → 存 `.pptx` 到 `corpus\_web\<来源>\`，重跑 `learn_web_templates.py`，并在此表加一行 **星数/许可/取用范围**。
3. 自己产出一册 → 在 `课件方法库.md` 追加「册 00N」，只写 3 条新学。

## 8. 已知缺口

- 没有「页级」结构数据：480 份只有 2 张预览图，无法统计每页版式。
- 没有播放态数据：转场/动画只能从 .pptx 回读，看不到实际播放效果。
- 中文字体授权未逐项核对（思源黑体/MiSans/阿里巴巴普惠体为开源可商用，需在使用处标注）。
