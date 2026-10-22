# -*- coding: utf-8 -*-
import glob
import io
import json
import re
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

rows = [json.loads(l) for l in io.open(r"D:\Resources\DSH\corpus\contest.jsonl", encoding="utf-8") if l.strip()]
print("contest rows:", len(rows))
print("keys:", list(rows[0].keys()))
for k, v in rows[0].items():
    print("  ", k, "=", str(v)[:140])

p = glob.glob(r"C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles\dark--premium-navy\*.pptx")[0]
z = zipfile.ZipFile(p)
xml = z.read("ppt/slides/slide1.xml").decode("utf-8", "ignore")
print("\ntemplate:", p.split("styles")[-1], "| slide1 bytes:", len(xml))
print("srgbClr:", re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)[:12])
print("schemeClr:", re.findall(r'schemeClr val="(\w+)"', xml)[:10])
print("texts:", re.findall(r"<a:t>([^<]{1,40})</a:t>", xml)[:10])
print("shapes:", len(re.findall(r"<p:sp>", xml)), "| pics:", len(re.findall(r"<p:pic>", xml)))

# 统计所有模板的显式色与主题色使用量
from collections import Counter

c = Counter()
for f in glob.glob(r"C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles\*\*.pptx"):
    zz = zipfile.ZipFile(f)
    for n in zz.namelist():
        if re.match(r"ppt/slides/slide\d+\.xml$", n):
            x = zz.read(n).decode("utf-8", "ignore")
            c.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', x))
print("\n全部模板显式色 Top15:", c.most_common(15))
