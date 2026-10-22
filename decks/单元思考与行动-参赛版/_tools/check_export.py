# -*- coding: utf-8 -*-
"""校验导出 pptx：ZIP 完整性、页数、转场覆盖、以及每页是否仍可解析为合法 XML。"""
import glob
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cands = [p for p in glob.glob(os.path.join(d, "*.pptx")) if "backup" not in os.path.basename(p)]
if len(sys.argv) > 1:
    cands = [sys.argv[1]]
for p in cands:
    z = zipfile.ZipFile(p)
    names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    with_t, xmlerr, slow = 0, 0, 0
    for nm in names:
        data = z.read(nm)
        if b"<p:transition" in data:
            with_t += 1
            if b'spd="slow"' in data:
                slow += 1
        try:
            ET.fromstring(data)
        except Exception as e:
            xmlerr += 1
            print("  XML 解析失败", nm, e)
    print("%s\n  zip_bad=%s  slides=%d  with_transition=%d (slow=%d)  xml_errors=%d  size=%d"
          % (os.path.basename(p), z.testzip(), len(names), with_t, slow, xmlerr, os.path.getsize(p)))
