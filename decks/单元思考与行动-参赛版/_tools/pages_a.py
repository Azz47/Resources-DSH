# -*- coding: utf-8 -*-
"""第二稿页面 A（P01–P21）：导引 + 子任务一（展板）+ 子任务二（解码）。"""
from theme2 import *  # noqa: F401,F403


def lead(els, text, accent, y=132, w=CW, eid="lead"):
    e, h = bar2(eid, L, y, w, accent, text, size=SZ_BODY)
    els += e
    return y + h


# ------------------------------------------------------------------ P01 封面
def p01(els):
    c1, c2 = SEC["intro"]
    els.append(S("cv_top", [0, 0, 960, 7], "rect", grad(c1, c2, 0)))
    els.append(dict(S("cv_badge", [700, 38, 216, 32], "roundRect", grad(PANEL, PANEL, 0, 94)),
                    contains=["cv_badget"]))
    els.append(T("cv_badget", [700, 44, 216, 22], "基础教育精品课 · 学科课程", SZ_SMALL, c2, HEI,
                 bold=True, align="center", width=216, wrap_on=True))
    els.append(T("cv_kicker", [96, 146, 620, 26], "统编版《道德与法治》九年级上册", SZ_BODY,
                 CHALK_DIM, HEI, width=620))
    els.append(T("cv_t1", [96, 178, 660, 68], "第二单元　进入新时代", 48, CHALK, "微软雅黑",
                 bold=True, width=660, wrap_on=True))
    els.append(T("cv_t2", [96, 250, 660, 56], "单元思考与行动", 40, c1, "微软雅黑", bold=True,
                 width=660, wrap_on=True))
    els.append(S("cv_rule", [96, 306, 300, 3.5], "rect", grad(c2, c1, 0)))
    els.append(T("cv_meta", [96, 316, 700, 96],
                 "年　级：九年级　　学　科：道德与法治（统编版）\n主讲人：张紫璇　　学　校：运城市盐湖区北城初级中学",
                 22, CHALK, KAI, width=700, lineHeight=1.5))
    els.append(T("cv_tag", [96, 418, 660, 24], "主题：以青春见证中国腾飞，用成长助推家乡发展", SZ_BODY,
                 CHALK_DIM, KAI, width=660))


# ------------------------------------------------------------------ P02–P05 导引
def p02(els):
    c2 = SEC["intro"][1]
    y = lead(els, "本单元以“中国特色社会主义进入新时代”为主题，围绕“新时代新在哪里”展开。", c2)
    spec = [("第四课\n新的历史方位", "我国发展新的历史方位，社会主要矛盾的历史性变化。"),
            ("第五课\n新时代的思想旗帜", "习近平新时代中国特色社会主义思想的确立与指导地位。"),
            ("第六课\n中国腾飞谱新篇", "新时代党和国家事业取得的历史性成就、发生的历史性变革。")]
    e, h = row2(spec, y + 12, c2, tsize=SZ_CARD, bsize=SZ_BODY)
    els += e
    e2, _ = bar2("p02sum", L, y + 12 + h + 12, CW, c2,
                 "三课层层递进：先看“方位”，再立“旗帜”，最后落到“成就”。",
                 size=SZ_SMALL, fill=PANEL_W)
    els += e2


def p03(els):
    y = lead(els, "把“新时代”拆开看，它新在四个地方。", SEC["intro"][1])
    spec = [("矛盾新变化", "人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾。"),
            ("历史新方位", "我国发展站到了新的历史起点上，进入新的发展阶段。"),
            ("理论新飞跃", "习近平新时代中国特色社会主义思想成为全党全国人民的思想旗帜。"),
            ("发展新成就", "经济、政治、文化、社会、生态文明各领域取得历史性成就。")]
    e, h = row2(spec, y + 22, SEC["intro"][1], tsize=SZ_CARD, bsize=SZ_BODY)
    els += e


def p04(els):
    c1, c2 = SEC["intro"]
    e, h = bar2("p04q", L, 128, CW, c2, "成就何以铸就，青年何以担当？", size=SZ_SUB, bold=True)
    els += e
    items = [("1　观展选品——感悟新时代", "梳理国家发展成就，补充完善展览展品。"),
             ("2　撰写解说——解码新成就", "结合展板撰写解说词，解码成就背后的密码。"),
             ("3　拓展策展——循迹盐湖行", "立足盐湖调研，设计家乡研学活动方案。")]
    e2, _ = bullets("p04", items, 128 + h + 20, c2, size=SZ_CARD)
    els += e2


def p05(els):
    c1, c2 = SEC["s1"]
    y = lead(els, "为引导学生深入了解新时代党和国家事业的发展历程及取得的辉煌成就，学校以“感悟新时代，解码新成就”为主题举办展览活动。同学们广泛搜集资料，并制作展板。", c2, y=130)
    e, h = bar2("p05task", L, y + 20, CW, c2,
                "任务：查阅资料，进一步从“五位一体”总体布局丰富展览内容。", size=SZ_SUB, bold=True)
    els += e
    spec = [("展示", "把本组展板推介给同学"),
            ("补充", "从剩余方面补一块空白展板"),
            ("追问", "这些成就从哪里来")]
    e2, _ = row2(spec, y + 20 + h + 20, c2, tsize=SZ_CARD, bsize=SZ_BODY)
    els += e2


# ------------------------------------------------------------------ P06–P12 六块展板
def _board_img_text(els, accent, img, iw, ih, cap, body, src=None, y=132):
    e, ih2 = imgcard("bimg", L, y, iw, ih, img, accent, cap=cap)
    els += e
    x2 = L + iw + 2 * 9 + 16
    e2, h2 = card2("btxt", x2, y - 9, R - x2, accent, None, body, bsize=SZ_BODY)
    els += e2
    if src:
        srcnote(els, src, y=max(y + max(ih2, h2) + 14, 424))


def p06(els):
    c1, c2 = SEC["s1"]
    e, h = bar2("p06tag", L, 128, CW, c2, "展板一　科技发展　·　经济建设", size=SZ_SUB, bold=True)
    els += e
    _board_img_text(els, c2, "media/image4.jpeg", 250, 186, "图：我国空间站长期有人驻留",
                    "浩瀚太空，我国空间站已正式开启长期有人驻留模式；远程医疗、智慧物流等新业态蓬勃发展；"
                    "工业互联网和人工智能融合赋能，为推进我国新型工业化注入强大动力。",
                    src="图片来源：人民日报", y=128 + h + 18)


def p07(els):
    c1, c2 = SEC["s1"]
    e, h = bar2("p07tag", L, 126, CW, c2, "展板二　交通基建　·　经济建设", size=SZ_SUB, bold=True)
    els += e
    y = 126 + h + 16
    imgs = [("media/image5.jpeg", "中国路"), ("media/image7.jpeg", "平陆运河"),
            ("media/image6.jpeg", "中国港")]
    x = L
    h2 = 0
    for i, (src, cap) in enumerate(imgs):
        e2, h2 = imgcard("p07i%d" % i, x, y, 176, 84, src, c2, cap=cap)
        els += e2
        x += 200
    body = ("看中国路：高铁营业里程突破 5 万公里。\n"
            "看中国运河：平陆运河是第一条通江达海的大运河。\n"
            "看中国港：全球前十港口中，中国占六席和八席。")
    e3, h3 = card2("p07t", L, y + h2 + 16, CW, c2, None, body, bsize=SZ_BODY)
    els += e3
    srcnote(els, "图片均来源于：人民网", y=y + h2 + 16 + h3 + 8)


def p08(els):
    c1, c2 = SEC["s1"]
    e, h = bar2("p08tag", L, 128, CW, c2, "展板三　平安中国　·　社会建设", size=SZ_SUB, bold=True)
    els += e
    _board_img_text(els, c2, "media/image8.jpeg", 250, 186, "图：平安中国建设",
                    "随着平安中国建设深入推进，我国成为世界上最有安全感的国家之一。"
                    "群众安全感连续多年保持 98% 以上，是世界上命案发生率最低的国家之一。",
                    src="图片来源：人民网", y=128 + h + 18)


def p09(els):
    c1, c2 = SEC["s1"]
    y = lead(els, "情境思考 · 把六块展板排一排，你发现了什么？", c2)
    e, h = card2("p09q1", L, y + 10, CW, c2, "问题一",
                 "已有展板体现了“五位一体”总体布局的哪些方面？", bsize=SZ_SUB)
    els += e
    e2, h2 = bar2("p09a1", L, y + 10 + h + 8, CW, c2,
                  "我们党统筹推进经济建设、政治建设、文化建设、社会建设、生态文明建设“五位一体”总体布局。",
                  size=SZ_BODY)
    els += e2
    e3, h3 = card2("p09q2", L, y + 10 + h + 8 + h2 + 8, CW, c2, "问题二",
                   "可以从剩余方面补充空白展板，请完善展板。", bsize=SZ_SUB)
    els += e3


def p10(els):
    c1, c2 = SEC["s1"]
    e, h = bar2("p10tag", L, 126, CW, c2, "展板四　民主法治　·　政治建设", size=SZ_SUB, bold=True)
    els += e
    y = 126 + h + 16
    h2 = 0
    for i, (src, cap) in enumerate([("media/image9.jpeg", "基层立法联系点"),
                                    ("media/image10.png", "生态环境法典")]):
        e2, h2 = imgcard("p10i%d" % i, L + i * 286, y, 268, 88, src, c2, cap=cap)
        els += e2
    body = ("发展全过程人民民主，坚持全面依法治国。\n"
            "《中华人民共和国生态环境法典》以法治护航美丽中国。\n"
            "基层立法联系点让民意直达国家立法机关。")
    e3, h3 = card2("p10t", L, y + h2 + 10, CW, c2, None, body, bsize=SZ_BODY)
    els += e3
    srcnote(els, "图片来源：人民网 · 人民日报", y=y + h2 + 16 + h3 + 8)


def p11(els):
    c1, c2 = SEC["s1"]
    y = lead(els, "传承弘扬中华优秀传统文化，推动中华优秀传统文化实现创造性转化、创新性发展。", c2)
    e, h = bar2("p11tag", L, y + 18, CW, c2, "展板五　文化传承　·　文化建设", size=SZ_SUB, bold=True)
    els += e
    y2 = y + 18 + h + 16
    caps = ["三星堆不断有考古新发现", "良渚古城遗址列入世界遗产",
            "国家版本馆建成开馆", "《只此青绿》向世界展示东方美学"]
    srcs = ["media/image11.jpeg", "media/image12.jpeg", "media/image13.jpeg", "media/image14.png"]
    x = L
    for i, (s, cap) in enumerate(zip(srcs, caps)):
        e2, h2 = imgcard("p11i%d" % i, x, y2, 130, 98, s, c2, cap=cap)
        els += e2
        x += 148
    srcnote(els, "以上图片均来源：新华社", y=y2 + h2 + 12)


def p12(els):
    c1, c2 = SEC["s1"]
    e, h = bar2("p12tag", L, 126, CW, c2, "展板六　江河战略　·　生态文明建设", size=SZ_SUB, bold=True)
    els += e
    y = 126 + h + 16
    h2 = 0
    for i, (src, cap) in enumerate([("media/image15.png", "长江"), ("media/image16.jpeg", "黄河")]):
        e2, h2 = imgcard("p12i%d" % i, L + i * 286, y, 268, 92, src, c2, cap=cap)
        els += e2
    body = ("“共抓大保护，不搞大开发”：长江经济带优良水质比例从 67% 提升到 96.5%。\n"
            "“让黄河成为造福人民的幸福河”：一体推进山水林田湖草沙保护和治理，筑牢生态屏障。")
    e3, h3 = card2("p12t", L, y + h2 + 10, CW, c2, None, body, bsize=SZ_BODY)
    els += e3
    srcnote(els, "图片来源：人民日报", y=y + h2 + 16 + h3 + 8)


# ------------------------------------------------------------------ P13–P20 解码
def p13(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p13q", L, 130, CW, c2, "结合所学知识，分析新时代党和国家事业取得辉煌成就的原因。",
                size=SZ_SUB, bold=True)
    els += e
    items = [("先看现象", "把成就摆出来，看清它到底变在哪里。"),
             ("再用工具", "用“四步解码法”把原因一层层问出来。"),
             ("写成解说", "把结论写进展板解说词，让证据自己说话。")]
    e2, _ = bullets("p13", items, 130 + h + 22, c2, size=SZ_CARD)
    els += e2


def p14(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p14tag", L, 126, CW, c2, "以黄河流域生态保护和高质量发展为例", size=SZ_SUB, bold=True)
    els += e
    y = 126 + h + 18
    e2, h2 = numhero("p14n1", L, y, 150, c2, "226 天", "1997 年断流天数")
    els += e2
    e3, h3 = numhero("p14n2", 206, y, 150, c2, "27 年", "连续不断流")
    els += e3
    e4, h4 = card2("p14t", 372, y, R - 372, c2, None,
                   "1972—1999 年，28 年间黄河有 22 年断流。", bsize=SZ_BODY)
    els += e4
    y2 = y + max(h2, h3, h4) + 18
    e5, h5 = card2("p14t2", L, y2, CW, c2, None,
                   "今天，黄河已实现自 1999 年以来连续 27 年不断流；干流连续 4 年稳定保持 Ⅱ 类水质。",
                   bsize=SZ_BODY)
    els += e5
    e6, _ = bar2("p14q", L, y2 + h5 + 16, CW, c2,
                 "从 226 天断流到连续 27 年不断流，究竟是什么原因导致黄河之变？", size=SZ_BODY,
                 bold=True)
    els += e6


def p15(els):
    c1, c2 = SEC["s2"]
    y = lead(els, "带着这个问题，先找五条线索——每一条都是“黄河之变”的一段证据链。", c2, y=128)
    rows = [["线索", "事实"],
            ["1. 水量统一调度", "1999 年起实施全河统一调度，统筹分配流域水资源，守住河道生态流量，终结断流。"],
            ["2. 九省区协同治污", "沿黄九省跨区域联防，上下游协同治理污染，推动流域水质稳步提升。"],
            ["3. 生态补水", "常态化向河口、湿地补水，修复流域湿地生态，保障河流健康生命。"],
            ["4. 水土流失治理", "黄土高原持续开展植被修复与小流域治理，水土流失实现面积、强度双下降。"],
            ["5. 《黄河保护法》护航", "将黄河保护的各项制度固化为法律，用法治保障黄河长治久安。"]]
    e, _ = table2("p15tbl", L, y + 20, CW, rows[0], rows[1:], row_h=44, size=SZ_SMALL)
    els += e


def p16(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p16tag", L, 126, CW, c2, "思维工具 · 四步解码法", size=SZ_SUB, bold=True)
    els += e
    spec = [("1　问机制", "它是怎么“变”回来的？把“怎么做到的”说清楚——这是推理的起点。"),
            ("2　反证", "假如没有它，还成不成？用“如果没有……会怎样”做反事实追问。"),
            ("3　比较", "别人为什么做不到？横向对照，找出“我们比别的国家多什么”。"),
            ("4　归纳", "能不能用课本来验证？把原因抽取归并，再用课本原文验证——论从史出。")]
    e2, h2 = row2(spec, 126 + h + 18, c2, tsize=SZ_CARD, bsize=SZ_BODY)
    els += e2


def p17(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p17tag", L, 126, CW, c2, "四步解码法 · 用在这条河上", size=SZ_SUB, bold=True)
    els += e
    spec = [("1　问机制", "统一调度、九省协同、生态补水、法治护航。"),
            ("2　反证", "没有党中央集中统一领导，跨九省工程难成。"),
            ("3　比较", "别国大河治理常因跨区协调失败。"),
            ("4　归纳", "抽象出不可替代的条件，再用课本验证。")]
    e2, h2 = row2(spec, 126 + h + 18, c2, tsize=SZ_CARD, bsize=SZ_BODY)
    els += e2
    e3, _ = bar2("p17sum", L, 126 + h + 18 + h2 + 18, CW, c2,
                 "四步走完，答案就不是“背”出来的，而是推出来的。", size=SZ_BODY, bold=True)
    els += e3


def p18(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p18q", L, 126, CW, c2, "新时代党和国家事业取得辉煌成就的原因是什么？", size=SZ_SUB,
                bold=True)
    els += e
    spec = [("科学指引", "习近平新时代中国特色社会主义思想的科学指导。"),
            ("党的领导", "坚持和加强党的全面领导。"),
            ("制度优势", "中国特色社会主义制度具有显著优势。"),
            ("人民至上", "坚持以人民为中心的发展思想。")]
    e2, h2 = row2(spec, 126 + h + 20, c2, tsize=SZ_CARD, bsize=SZ_BODY)
    els += e2
    e3, _ = bar2("p18task", L, 126 + h + 20 + h2 + 18, CW, c2,
                 "小组合作探究：根据四大原因，撰写成就解码解说词。", size=SZ_BODY, bold=True)
    els += e3


def p19(els):
    c1, c2 = SEC["s2"]
    y = lead(els, "解说词脚手架：三段话，把一块展板讲清楚。", c2, y=130)
    items = [("第一段　展示成就", "这一块展板展示了怎样的成就？用事实和数据说话。"),
             ("第二段　解码原因", "取得这样的成就，原因是什么？用四步解码法推出来。"),
             ("第三段　联系自身", "这启示我们今后如何做？把结论接到自己的生活上。")]
    e, h = bullets("p19", items, y + 22, c2, size=SZ_CARD)
    els += e


def p20(els):
    c1, c2 = SEC["s2"]
    e, h = bar2("p20tag", L, 126, CW, c2, "小组合作探究成果 · 解说词示例", size=SZ_SUB, bold=True)
    els += e
    body = ("黄河，从 226 天断流到连续 27 年不断流。\n"
            "这条母亲河的“重生”告诉我们：奇迹不是凭空发生的。\n"
            "它的背后，站着党的全面领导、科学理论的指引、制度的优势和人民至上的立场。\n"
            "从断流到安澜，这条大河的变迁，就是国家发展奇迹的生动缩影。\n"
            "解码成就，不是为了记住几个结论，而是学会用这把钥匙，去读懂我们的国家。")
    e2, h2 = card2("p20t", L, 126 + h + 18, CW, c2, None, body, bsize=SZ_BODY, fill=PANEL_W)
    els += e2


# ------------------------------------------------------------------ P21 子任务三
def p21(els):
    c1, c2 = SEC["s3"]
    e, h = bar2("p21task", L, 130, CW, c2, "围绕展览主题，立足家乡的变化发展，开展一次研学活动。",
                size=SZ_SUB, bold=True)
    els += e
    items = [("选定线索", "黄河流域生态保护和高质量发展 · 盐湖之变。"),
             ("走进现场", "实地走访或线上查阅，收集事实与数据。"),
             ("形成成果", "完成一份《家乡发展调研报告》。")]
    e2, _ = bullets("p21", items, 130 + h + 22, c2, size=SZ_CARD)
    els += e2


PAGES_A = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12,
           p13, p14, p15, p16, p17, p18, p19, p20, p21]
