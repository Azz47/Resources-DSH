import sys, os, json, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
SRC=r"D:\Resources\xwechat_files\wxid_9ka181duelek22_80a9\msg\file\2026-10\单元思考与行动(1).pptx"
OUT=r"D:\Resources\DSH\_wx_analysis"
z=zipfile.ZipFile(SRC)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
# theme
th=etree.fromstring(z.read('ppt/theme/theme1.xml'))
scheme=th.find('.//a:clrScheme',ns)
print("== THEME clrScheme ==")
for c in scheme:
    tag=etree.QName(c).localname
    v=c.find('a:srgbClr',ns)
    s=c.find('a:sysClr',ns)
    print("  %-8s %s"%(tag, v.get('val') if v is not None else (s.get('lastClr') if s is not None else '?')))
fnt=th.find('.//a:fontScheme',ns)
for kind in ('majorFont','minorFont'):
    e=fnt.find('a:'+kind,ns); la=e.find('a:latin',ns); ea=e.find('a:ea',ns)
    print("  %s latin=%s ea=%s"%(kind, la.get('typeface') if la is not None else '?', ea.get('typeface') if ea is not None else '?'))
# master bg
m=etree.fromstring(z.read('ppt/slideMasters/slideMaster1.xml'))
bg=m.find('.//p:cSld/p:bg',ns)
print("== MASTER bg ==", etree.tostring(bg,encoding='unicode')[:600] if bg is not None else None)
print("== master shapes ==")
for sp in m.findall('.//p:sp',ns):
    nv=sp.find('.//p:cNvPr',ns); txt=''.join(t.text or '' for t in sp.findall('.//a:t',ns))
    print("   ", nv.get('name'), '|', txt[:40])
# rels of master -> image?
mrel=etree.fromstring(z.read('ppt/slideMasters/_rels/slideMaster1.xml.rels'))
for rel in mrel: print("   masterrel", rel.get('Type').split('/')[-1], rel.get('Target'))
print("== slide1 bg ==")
s1=etree.fromstring(z.read('ppt/slides/slide1.xml'))
print(etree.tostring(s1.find('.//p:cSld/p:bg',ns),encoding='unicode')[:600])
# layouts used
print("== layouts ==")
for n in z.namelist():
    if re.match(r'ppt/slideLayouts/slideLayout\d+\.xml$',n):
        L=etree.fromstring(z.read(n)); bg=L.find('.//p:cSld/p:bg',ns)
        c=[];  
        for sp in L.findall('.//p:sp',ns):
            nv=sp.find('.//p:cNvPr',ns); t=''.join(x.text or '' for x in sp.findall('.//a:t',ns))
            if t: c.append(nv.get('name')+':'+t[:18])
        print("  ",n.split('/')[-1], "bg=",("yes" if bg is not None else "-"), c[:6])
