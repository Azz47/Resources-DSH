# -*- coding: utf-8 -*-
"""给导出的 pptx 逐页注入 p:transition（淡入）。slow 页：封面 + 三个环节页 + 收束页。"""
import sys, zipfile, shutil, os, io, re

PPTX = sys.argv[1]
SLOW = {1, 6, 15, 23, 35, 44}

NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"')

tmp = PPTX + ".tmp"
zin = zipfile.ZipFile(PPTX, "r")
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)

slides = sorted([n for n in zin.namelist()
                 if re.match(r"ppt/slides/slide\d+\.xml$", n)],
                key=lambda s: int(re.search(r"(\d+)\.xml$", s).group(1)))

inject = {}
for i, name in enumerate(slides, 1):
    xml = zin.read(name).decode("utf-8")
    if "<p:transition" in xml:
        inject[name] = xml
        continue
    spd = ' spd="slow"' if i in SLOW else ""
    tr = '<p:transition%s><p:fade/></p:transition>' % spd
    # 插到 cSld 结束之后（p:cSld ... </p:cSld>  ->  + transition）
    m = re.search(r"</p:cSld>", xml)
    if not m:
        inject[name] = xml
        continue
    xml2 = xml[:m.end()] + tr + xml[m.end():]
    inject[name] = xml2

for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename in inject:
        data = inject[item.filename].encode("utf-8")
    zout.writestr(item, data)
zin.close()
zout.close()
shutil.move(tmp, PPTX)

# 自证
z = zipfile.ZipFile(PPTX)
bad = z.testzip()
cnt = 0
slow = 0
err = 0
for n in slides:
    x = z.read(n).decode("utf-8")
    if "<p:transition" in x:
        cnt += 1
    if 'spd="slow"' in x:
        slow += 1
    try:
        from xml.etree import ElementTree as ET
        ET.fromstring(x)
    except Exception:
        err += 1
print("slides=%d  with_transition=%d  slow=%d  xml_errors=%d  zip_bad=%s  size=%d"
      % (len(slides), cnt, slow, err, bad, os.path.getsize(PPTX)))
