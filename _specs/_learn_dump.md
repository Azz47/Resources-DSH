# PPT 库学习 · 原始指标（脚本生成，勿手改）

生成时间：2026-10-18 16:33；脚本：`_probe/learn_ppt_library.py`

## corpus.jsonl（本机模板/成品）（23 条）

- 有页数的样本：22；页数中位 **1**，范围 1–13
- 学科分布：{'未标': 23}
- 字号频次 Top10（pt:次数）：[('20.0', 14), ('26.0', 13), ('18.0', 13), ('14.0', 9), ('32.0', 9), ('19.0', 7), ('36.0', 6), ('22.0', 5), ('16.0', 5), ('24.0', 5)]
- 字体频次 Top8：[('微软雅黑', 81), ('+mj-lt', 3)]
- 颜色频次 Top10：[('1F3A5F', 23), ('6B7280', 21), ('1F2937', 17), ('B03A2E', 14), ('FFFFFF', 4), ('C9D3E0', 1), ('E8B95A', 1)]
- 图片页占比：中位 **0.00**，均值 0.35，范围 0.00–1.00
- 每页字数：中位 35，均值 34
- 每页块数：中位 4.0
- 表格合计 0 个；图表合计 0 个

## contest.jsonl（参赛/优质课样本）（62 条）

- 有页数的样本：0；页数中位 **0**，范围 0–0
- 学科分布：{'未标': 62}
- 字号频次 Top10（pt:次数）：[]
- 字体频次 Top8：[]
- 颜色频次 Top10：[]
- 表格合计 0 个；图表合计 0 个

## 27 个样式模板（morph-ppt/reference/styles）

| 家族 | 样式 | 页数 | 媒体 | 主题主色（accent1/2/3） | 主题字体（latin/ea） | 转场 |
|---|---|---|---|---|---|---|
| bw | brutalist-raw | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| bw | mono-line | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| bw | swiss-bauhaus | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | architectural-plan | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |
| dark | blueprint-grid | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | circle-digital | 7 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×12 |
| dark | cosmic-neon | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | cyber-future | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | diagonal-cut | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | editorial-story | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |
| dark | investor-pitch | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |
| dark | liquid-flow | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |
| dark | luxury-minimal | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | neon-productivity | 7 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×14 |
| dark | premium-navy | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| dark | space-odyssey | 4 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×6 |
| dark | spotlight-stage | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| light | bold-type | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| light | isometric-clean | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| light | minimal-product | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |
| light | watercolor-wash | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| mixed | duotone-split | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| vivid | candy-stripe | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| vivid | playful-marketing | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | 无 |
| warm | brand-refresh | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| warm | earth-organic | 5 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×8 |
| warm | playful-organic | 6 | 0 | #4472C4/#ED7D31/#A5A5A5 | Calibri Light | fade×10 |

- 家族计数：{'bw': 3, 'dark': 14, 'light': 4, 'mixed': 1, 'vivid': 2, 'warm': 3}
- 转场类型合计：{'fade': 228}
