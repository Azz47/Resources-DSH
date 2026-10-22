# -*- coding: utf-8 -*-
"""给导出的 pptx 逐页写入 PowerPoint 原生切换效果（转场）。
不改动任何形状/文本/版式，只在每张 slideN.xml 的 </p:sld> 前插入一段
<p:transition>。PowerPoint / WPS / Keynote 都认这个元素；缺失时等于「无转场」。

用法：
    python _tools/add_transitions.py <pptx> [--slow 1,6,19,30,46] [--dry]
"""
import os
import re
import sys
import shutil
import zipfile

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"

# 节奏较重的页（封面 / 三个环节开场 / 结页）用慢速淡入，其余中速
SLOW_DEFAULT = {1, 6, 19, 30, 46}


def slide_order(z):
    """按 presentation.xml 的 sldIdLst 顺序返回 slide 部件名列表。"""
    pres = z.read("ppt/presentation.xml").decode("utf-8")
    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
    rmap = dict(re.findall(r'Id="([^"]+)"[^>]*?Target="([^"]+)"', rels))
    order = []
    lst = re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres, re.S)
    for rid in re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', lst.group(1) if lst else ""):
        t = rmap.get(rid, "")
        if t:
            order.append("ppt/" + t.lstrip("/") if not t.startswith("ppt/") else t)
    return order


def transition_xml(slow):
    spd = "slow" if slow else "med"
    return ('<p:transition spd="%s"><p:fade/></p:transition>' % spd).encode("utf-8")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = os.path.abspath(sys.argv[1])
    slow = set(SLOW_DEFAULT)
    if "--slow" in sys.argv:
        slow = {int(x) for x in sys.argv[sys.argv.index("--slow") + 1].split(",") if x.strip()}
    dry = "--dry" in sys.argv
    if not os.path.isfile(src):
        print("找不到文件：%s" % src)
        return 2

    tmp = src + ".tmp"
    z = zipfile.ZipFile(src)
    order = slide_order(z)
    if not order:
        print("没能解析出幻灯片顺序，放弃。")
        return 2

    n_added = 0
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for item in z.infolist():
            data = z.read(item.filename)
            if item.filename in order:
                page = order.index(item.filename) + 1
                if page in slow:
                    n_added += 1
                if b"<p:transition" not in data and data.rstrip().endswith(b"</p:sld>"):
                    data = re.sub(rb"</p:sld>\s*$",
                                  transition_xml(page in slow) + b"</p:sld>", data)
                else:
                    print("  跳过（已有转场或结构异常）：%s" % item.filename)
            out.writestr(item, data)
    z.close()

    if dry:
        os.remove(tmp)
        print("dry-run：会写入 %d 页转场，慢速页 %s" % (len(order), sorted(slow)))
        return 0

    shutil.move(tmp, src)
    print("[OK] wrote transitions on %d pages (slow: %s), total %d -> %s"
          % (n_added, sorted(slow), len(order), src))
    return 0


if __name__ == "__main__":
    sys.exit(main())
