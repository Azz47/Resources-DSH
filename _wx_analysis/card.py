import sys, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
from PIL import Image
SRC=r"D:\Resources\xwechat_files\wxid_9ka181duelek22_80a9\msg\file\2026-10\单元思考与行动(1).pptx"
z=zipfile.ZipFile(SRC)
for n in ('ppt/slideLayouts/_rels/slideLayout1.xml.rels','ppt/slideLayouts/_rels/slideLayout2.xml.rels','ppt/slideLayouts/_rels/slideLayout3.xml.rels'):
    print(n, z.read(n).decode()[:500]); print()
print(etree.tostring(etree.fromstring(z.read('ppt/slideLayouts/slideLayout2.xml')),encoding='unicode')[:2500])
print("\n---- white card bbox scan (page2) ----")
im=Image.open(r'D:\Resources\DSH\decks\单元思考与行动-参赛版\_probe\friend_render\page-0002.png').convert('RGB')
W,H=im.size
def iswhite(p): return p[0]>200 and p[1]>200 and p[2]>200
col=[im.getpixel((5,y)) for y in range(H)]
row=[im.getpixel((x,5)) for x in range(W)]
ytop=next((y for y,p in enumerate(col) if iswhite(p)), None)
ybot=max((y for y,p in enumerate(col) if iswhite(p)), default=None)
xleft=next((x for x,p in enumerate(row) if iswhite(p)), None)
print("white starts y=",ytop," ends y=",ybot, " at x=5; white at y=5 starts x=",xleft)
# vertical scan at center
colc=[im.getpixel((W//2,y)) for y in range(H)]
print("center col: y0..12:",colc[:12])
print("center col last 8:",colc[-8:])
rowc=[im.getpixel((x,H//2)) for x in range(W)]
print("center row first 8:",rowc[:8]," last 8:",rowc[-8:])
