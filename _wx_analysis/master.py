import sys, os, zipfile, json
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
from PIL import Image
SRC=r"D:\Resources\xwechat_files\wxid_9ka181duelek22_80a9\msg\file\2026-10\单元思考与行动(1).pptx"
z=zipfile.ZipFile(SRC)
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'; P='{http://schemas.openxmlformats.org/presentationml/2006/main}'; R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
def dump(name):
    x=etree.fromstring(z.read(name)); print("=== "+name+" ===")
    for sp in x.iter(P+'sp'):
        nv=sp.find('.//'+P+'cNvPr'); xf=sp.find('.//'+A+'xfrm')
        off=xf.find(A+'off') if xf is not None else None; ext=xf.find(A+'ext') if xf is not None else None
        fill=sp.find('.//'+P+'spPr/'+A+'solidFill/'+A+'srgbClr')
        t=''.join(v.text or '' for v in sp.iter(A+'t'))
        print("  sp %-24s %s,%s %sx%s fill=%s :: %s"%(nv.get('name'),
            round(int(off.get('x'))/12700) if off is not None else '-', round(int(off.get('y'))/12700) if off is not None else '-',
            round(int(ext.get('cx'))/12700) if ext is not None else '-', round(int(ext.get('cy'))/12700) if ext is not None else '-',
            fill.get('val') if fill is not None else '-', t[:30]))
    for pic in x.iter(P+'pic'):
        nv=pic.find('.//'+P+'cNvPr'); xf=pic.find('.//'+A+'xfrm')
        off=xf.find(A+'off'); ext=xf.find(A+'ext')
        print("  pic %-23s %s,%s %sx%s"%(nv.get('name'), round(int(off.get('x'))/12700),round(int(off.get('y'))/12700),round(int(ext.get('cx'))/12700),round(int(ext.get('cy'))/12700)))
    for gf in x.iter(P+'graphicFrame'):
        nv=gf.find('.//'+P+'cNvPr'); xf=gf.find('.'+P+'xfrm')
        off=xf.find(A+'off'); ext=xf.find(A+'ext')
        print("  frame %-21s %s,%s %sx%s"%(nv.get('name'), round(int(off.get('x'))/12700),round(int(off.get('y'))/12700),round(int(ext.get('cx'))/12700),round(int(ext.get('cy'))/12700)))
dump('ppt/slideMasters/slideMaster1.xml')
for i in (1,2,3): dump('ppt/slideLayouts/slideLayout%d.xml'%i)
print("\n== 每个 slide 用哪个 layout ==")
import re
for i in range(1,41):
    rels=z.read('ppt/slides/_rels/slide%d.xml.rels'%i).decode()
    m=re.search(r'slideLayout(\d+)\.xml',rels)
    print(i, m.group(1) if m else '?', end='; ')
print()
print("\n== 页面边框取样 P02/P03/P30 (1921x1081) ==")
for pg in (2,3,30):
    im=Image.open(r'D:\Resources\DSH\decks\单元思考与行动-参赛版\_probe\friend_render\page-%04d.png'%pg).convert('RGB')
    W,H=im.size
    pts={'TL':(8,8),'Tmid':(W//2,8),'TR':(W-8,8),'Lmid':(8,H//2),'Rmid':(W-8,H//2),'BL':(8,H-8),'Bmid':(W//2,H-8),'center':(W//2,H//2)}
    print('p%02d'%pg, {k:im.getpixel(v) for k,v in pts.items()})
