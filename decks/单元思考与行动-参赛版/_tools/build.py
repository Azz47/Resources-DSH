# -*- coding: utf-8 -*-
"""装配第二稿 42 页 → pages/*.yaml + deck.yaml。

用法：python _tools/build.py
"""
import io
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import theme2 as T2  # noqa: E402
from theme2 import L, R, CW, SZ_TITLE  # noqa: E402
import pages_a  # noqa: E402
import pages_b  # noqa: E402

# P22–P42 的生成函数在 pages_b；这里做一次别名，让下面的页表统一写 pages_a.pNN
for _n in range(22, 43):
    setattr(pages_a, "p%02d" % _n, getattr(pages_b, "p%02d" % _n))

DECK_DIR = os.path.dirname(HERE)
OUT = os.path.join(DECK_DIR, "pages")
IMPORTED = os.path.join(DECK_DIR, "_imported")

RB_DECL = ["rb_rule", "rb_chip_a", "rb_chip_b", "rb_tag1", "rb_tag2", "rb_tagrule", "rb_num"]
CV_DECL = ["cv_top", "cv_badge", "cv_badget", "cv_kicker", "cv_t1", "cv_t2", "cv_meta", "cv_tag"]

BODY_TOP = 94


def lift(els, top=BODY_TOP):
    """把正文块整体上移到 BODY_TOP。

    黑板照片的板面只到 y≈460（木框 460–505、左下角本/笔 y>445）：
    正文必须整块收在 [top, 445] 内。页眉压缩到 y≤92 后，用这一处统一上移，
    避免去改 42 个页面函数的起始坐标。
    """
    body = [e for e in els
            if e.get("bounds") and e["bounds"][1] >= 112
            and not str(e.get("id", "")).startswith("rb_")]
    if not body:
        return
    dy = top - min(e["bounds"][1] for e in body)
    if dy:
        for e in body:
            e["bounds"][1] += dy


# (文件名, 环节, 页标题, 讲稿备注, 生成函数)
P = [
    ("01_cover", "intro", None,
     "上课铃响前循环播放。开场只用一句：同学们，这节课我们要给“新时代”办一个展。",
     pages_a.p01),
    ("02_intro_unit", "intro", "新课导入 · 本单元学什么",
     "先给整单元的骨架：第四课讲新的历史方位，第五课讲思想旗帜，第六课讲腾飞成就。三十秒带过，不要展开。",
     pages_a.p02),
    ("03_intro_new", "intro", '新时代"新"在哪里',
     "追问：如果只用一个字概括这个时代，你会选哪个字？引出四个“新”，停在这里，不急着给答案。",
     pages_a.p03),
    ("04_task", "intro", "本课任务 · 时代答卷人",
     "亮出总议题：成就何以铸就，青年何以担当。三个子任务串成一条线——看成就、解码原因、落到行动。",
     pages_a.p04),
    ("05_scene", "s1", "情境导入 · 学校要办一个展",
     "读出情境，请学生代入策展人身份。提问：如果展板交给你，你会先放什么？先不出示答案。",
     pages_a.p05),
    ("06_board1", "s1", "展板一 · 科技发展：把想象变成日常",
     "重点讲空间站的“长期有人驻留”，让学生说一件自己用过的科技产品，把宏大叙事落到日常。",
     pages_a.p06),
    ("07_board2", "s1", "展板二 · 交通基建：一张网，改变中国",
     "三个数字要念出来：5 万公里高铁、19.1 万公里高速、港口六席与八席。追问：路网密了，你的生活变了什么？",
     pages_a.p07),
    ("08_board3", "s1", "展板三 · 平安中国：安全感从哪里来",
     "安全感 98% 以上这个数字最有说服力。追问：你身上的哪一件“安心”，其实背后有人在守？",
     pages_a.p08),
    ("09_thinking", "s1", "情境思考 · 六块展板排一排",
     "带学生把六块展板归到“五位一体”的五个方面，留出空白展板让学生自己补——这是本环节的小高潮。",
     pages_a.p09),
    ("10_board4", "s1", "展板四 · 民主法治：民意直达国家立法机关",
     "用“基层立法联系点”讲全过程人民民主，让学生明白：法律不是离他很远的东西。",
     pages_a.p10),
    ("11_board5", "s1", "展板五 · 文化传承：让老东西有新活法",
     "四张图快速过，重点停在“创造性转化、创新性发展”这八个字上，用只此青绿举例。",
     pages_a.p11),
    ("12_board6", "s1", "展板六 · 江河战略：把绿色写进发展",
     "长江水质从 67% 到 96.5%，用这组数字收束环节一：成就是看得见的，但为什么会发生，还没回答。",
     pages_a.p12),
    ("13_task2", "s2", "子任务二 · 撰写解说——解码新成就",
     "承接上一页的悬念：看见了成就，紧接着问为什么。把“四步解码法”预告一下，不展开。",
     pages_a.p13),
    ("14_yellow", "s2", "黄河之变 · 从 226 天到 27 年",
     "两个数字对比最强：226 天断流到连续 27 年不断流。先让学生惊讶，再抛出问题。",
     pages_a.p14),
    ("15_clues", "s2", "黄河之变 · 五条线索",
     "逐条读，但只读一级：水量统一调度、九省协同、生态补水、水土流失治理、法治护航。",
     pages_a.p15),
    ("16_tool", "s2", "思维工具 · 四步解码法",
     "这是本课最重要的一页工具页，要慢讲：问机制、反证、比较、归纳。每一步举一个例子。",
     pages_a.p16),
    ("17_tool_use", "s2", "四步解码法 · 用在这条河上",
     "现场演示一遍：把黄河治理套进四步。学生能听懂“反证”这一步，就说明方法立住了。",
     pages_a.p17),
    ("18_reasons", "s2", "四大原因 · 成就背后的密码",
     "四条原因对应教材：科学指导、党的全面领导、制度优势、人民至上。写板书时用四个短语。",
     pages_a.p18),
    ("19_scaffold", "s2", "解说词脚手架 · 三段话",
     "给支架不给答案：先说成就，再说原因，最后说启示。请一位同学现场说第一段。",
     pages_a.p19),
    ("20_speech", "s2", "小组合作探究成果 · 解说词示例",
     "读一遍示例，重点读最后一句：解码成就，不是为了记住结论，而是学会读国家。",
     pages_a.p20),
    ("21_task3", "s3", "子任务三 · 拓展策展——循迹盐湖行",
     "从国家拉回家乡：把刚才的方法用到盐湖。说明这次要走出教室，先交代任务边界。",
     pages_a.p21),
    ("22_saltlake", "s3", "盐湖 · 从工业矿区到城市生态客厅",
     "念总书记的话时放慢。强调“逐步恢复其生态功能”——保护不是停下来，是换一种用法。",
     pages_a.p22),
    ("23_saltlake_change", "s3", "盐湖之变 · 两个维度看家乡",
     "文化之变对应“创造性转化”，生态之变对应“绿水青山”。25.2 亿元、119.77 公里要念出来。",
     pages_a.p23),
    ("24_require", "s3", "研学活动要求 · 五步走",
     "把“看”变成“查”，把“感想”变成“证据”——这句话是本页的关键，要重复一次。",
     pages_a.p24),
    ("25_plan", "s3", "研学活动方案 · 七个要素",
     "带学生逐条填。最容易漏的是“调研目的”——先说清要弄清什么问题，再谈怎么去。",
     pages_a.p25),
    ("26_report1", "s3", "调研报告 · 封面与分工",
     "四个角色必须都有人：有人查、有人记、有人讲、有人追问。现场分组确认。",
     pages_a.p26),
    ("27_report2", "s3", "调研报告 · 七个部分",
     "强调第三到第五部分是核心：变化、问题、建议。没有现场证据的问题不算真问题。",
     pages_a.p27),
    ("28_tips", "s3", "研学活动提示 · 四条纪律",
     "安全与礼貌先讲：文明走访、尊重隐私。这既是纪律，也是法治意识的现场练习。",
     pages_a.p28),
    ("29_debate", "s3", "思辨探究 · 和我们有关吗",
     "不急于表态。先请正反两方各说一条理由，再从“谁被排除在外”切入——这是本课唯一的真问题。",
     pages_a.p29),
    ("30_answer", "s3", "我们这样回答 · 从见证者到建设者",
     "答案此刻才出现：人人共建、人人共享。三条行动要落到学生今天就能做的小事上。",
     pages_a.p30),
    ("31_extend", "end", "课后延伸 · A / B 分层",
     "按条件分层，不做优劣判断：能出去就走出去，出不去就把资料查透。两条路都算完成。",
     pages_a.p31),
    ("32_rubric", "end", "活动评价量表 · 自评 互评 师评",
     "念一遍五个维度，重点解释星级差别在哪。请学生当场给自己打一次自评。",
     pages_a.p32),
    ("33_summary1", "end", "课堂小结 · 两幅画面",
     "两幅图对照：会场里的自豪与广场上的清晨。问一句：这两幅画面之间，是什么连着？",
     pages_a.p33),
    ("34_summary2", "end", "课堂小结 · 我们的青春答卷",
     "收束全课。最后一句齐读：以青春见证中国腾飞，用成长助推家乡发展。不拖堂。",
     pages_a.p34),
    ("35_quiz1", "end", "课堂练习 1 · 新时代的认识",
     "选择题限时一分钟，先读题干再选。答案 B，请学生说为什么排除 A。",
     pages_a.p35),
    ("36_quiz2", "end", "课堂练习 2 · 黄河保护法",
     "答案 B。提醒③“生态保护可以脱离经济发展单独推进”是典型错误说法，这类选项要先划掉。",
     pages_a.p36),
    ("37_quiz3", "end", "课堂练习 3 · 新质生产力",
     "答案 B。材料里的“新三样”和 3.5 倍增长是关键词，指向创新驱动。",
     pages_a.p37),
    ("38_quiz4", "end", "课堂练习 4 · 阅读材料",
     "材料较长，给两分钟默读。提示学生边读边圈“从……到……”的对比句。",
     pages_a.p38),
    ("39_quiz5", "end", "课堂练习 5 · 结合三问",
     "把三问一起给出：变化、原因、做法。答题用三段式，逐问作答。",
     pages_a.p39),
    ("40_quiz6", "end", "（1）概括变化 · 参考答案",
     "参考答案三点：体系、行列、转变。请学生对照自己的答案补漏，不必逐字一致。",
     pages_a.p40),
    ("41_quiz7", "end", "（2）分析原因 · 参考答案",
     "四点原因教材里都有出处，重点讲第二点的“全面领导”和第三点的“集中力量办大事”。",
     pages_a.p41),
    ("42_quiz8", "end", "（3）青少年怎么做 · 参考答案",
     "三点落到自身：学知识、动手做、立志向。收尾时回到本课总议题，形成闭环。",
     pages_a.p42),
]

THEME_COLORS = {
    "panel": "#E9EFE9", "panelW": "#F0E8D8",
    "ink": "#1D2B23", "soft": "#2E4438", "muted": "#465C4D",
    "chalk": "#F4F8F4", "chalkDim": "#BFD2C2", "chalkFaint": "#A9C0AE",
    "rule": "#7E9A85", "shadow": "#0E1A12",
    "mint": "#7FD6B0", "mint2": "#1F6B4F",
    "gold": "#E8C15A", "gold2": "#8A6A1E",
    "cyan": "#6FC7E8", "cyan2": "#1F6383",
    "coral": "#EE8A72", "coral2": "#8E3F2E",
    "lavender": "#B9A7E8", "lavender2": "#584C86",
}

DECK_YAML = """# 第二稿 · 由 _tools/build.py 生成（黑板 × 粉笔擦卡；字号严格 14–24pt）
# 底稿：source.pptx（= 朋友的《单元思考与行动(1).pptx》，零失真真相层）
# 硬约束：内容走廊 x ∈ [44, 640]pt；右侧 640–960 只放不承载信息的装饰（rb_*，已逐页声明出界）
version: 1
title: "第二单元 进入新时代 · 单元思考与行动（参赛版）"
size: [960, 540]
theme:
  colors:
{colors}
  textStyles:
    pageTitle: {{fontSize: 24, color: "$chalk", bold: true, fontFamily: "黑体"}}
    section: {{fontSize: 14, color: "$chalkDim", fontFamily: "黑体"}}
    cardTitle: {{fontSize: 17, color: "$ink", bold: true, fontFamily: "黑体"}}
    body: {{fontSize: 16, color: "$soft", fontFamily: "楷体"}}
    note: {{fontSize: 14, color: "$muted", fontFamily: "楷体"}}
  safeArea: {{top: 20, bottom: 16, left: 36, right: 320}}
  minFontSize: 14
pages:
{pages}
referenceSource:
  name: "单元思考与行动(1).pptx"
  source: source.pptx
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    # 把导入器的 slide_*.yaml 挪到 _imported/，避免与第二稿页面混淆
    if not os.path.isdir(IMPORTED):
        os.makedirs(IMPORTED, exist_ok=True)
        for f in sorted(os.listdir(OUT)):
            if f.startswith("slide_") and f.endswith(".yaml"):
                shutil.move(os.path.join(OUT, f), os.path.join(IMPORTED, f))

    total = len(P)
    page_paths = []
    for i, (name, sec, title, notes, fn) in enumerate(P, 1):
        fname = name + ".yaml"
        path = os.path.join(OUT, fname)
        els = []
        if name == "01_cover":
            fn(els)
            T2.dump(path, els, notes, {"pageType": "cover", "expectedOutOfSafeArea": list(CV_DECL)})
        else:
            T2.hd(els, sec, title, i)
            T2.rband(els, i, sec, total)
            fn(els)
            lift(els)
            T2.dump(path, els, notes, {"expectedOutOfSafeArea": list(RB_DECL)})
        page_paths.append("  - pages/" + fname)

    colors = "\n".join('    %s: "%s"' % (k, v) for k, v in THEME_COLORS.items())
    io.open(os.path.join(DECK_DIR, "deck.yaml"), "w", encoding="utf8").write(
        DECK_YAML.format(colors=colors, pages="\n".join(page_paths)))
    print("wrote %d pages + deck.yaml" % total)


if __name__ == "__main__":
    main()
