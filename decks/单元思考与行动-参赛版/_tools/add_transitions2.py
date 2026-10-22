# -*- coding: utf-8 -*-
"""给导出的 pptx 逐页注入 PowerPoint 原生淡入转场（环节扉页用 slow）。

用法：python add_transitions2.py <pptx>   （原地替换，先备份 .bak）
"""
import os
import re
import shutil
import sys
import zipfile

SLOW = {1, 5, 13, 21, 31}   # 封面 + 四个环节扉页
TR = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="%s"><p:fade/></p:transition>'


def main():
    src = os.path.abspath(sys.argv[1])
    shutil.copy2(src, src + ".bak")
    zin = zipfile.ZipFile(src)
    items = zin.infolist()
    data = {i.filename: zin.read(i.filename) for i in items}
    zin.close()

    n = 0
    for name in list(data):
        m = re.match(r"ppt/slides/slide(\d+)\.xml$", name)
        if not m:
            continue
        idx = int(m.group(1))
        if b"<p:transition" in data[name]:
            continue
        xml = data[name].decode("utf8")
        spd = "slow" if idx in SLOW else "med"
        if "</p:sld>" not in xml:
            continue
        xml = xml.replace("</p:sld>", (TR % spd) + "</p:sld>", 1)
        data[name] = xml.encode("utf8")
        n += 1

    out = zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED)
    for i in items:
        out.writestr(i.filename, data[i.filename])
    out.close()
    print("injected transitions: %d slides (slow=%s)" % (n, sorted(SLOW)))


if __name__ == "__main__":
    main()
