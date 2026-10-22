import sys, zipfile, re, collections
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
SRC=r"D:\Resources\xwechat_files\wxid_9ka181duelek22_80a9\msg\file\2026-10\单元思考与行动(1).pptx"
z=zipfile.ZipFile(SRC)
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'; P='{http://schemas.openxmlformats.org/presentationml/2006/main}'
anim=[];trans=[]
for i in range(1,41):
    s=z.read('ppt/slides/slide%d.xml'%i).decode('utf-8')
    anim.append((i, s.count('<p:anim'), s.count('<p:par>'), s.count('<p:childTxn') , s.count('animEffect')+s.count('animMotion')))
    m=re.search(r'<p:transition[^>]*>',s); trans.append((i, m.group(0) if m else '-'))
print("== 动画/切换 ==")
print("  页 (anim节点, par节点, childTxn, animEffect/Motion):")
print("  ", [ (i,a,c,d) for i,a,b,c,d in anim if a+d>0 ] or "  全部为 0 —— 无任何动画")
print("  切换:", [t for t in trans if t[1]!='-'][:8], " 有切换页数:", sum(1 for t in trans if t[1]!='-'))
# colors & fonts
col=collections.Counter(); fnt=collections.Counter(); sz=collections.Counter()
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
for i in range(1,41):
    x=etree.fromstring(z.read('ppt/slides/slide%d.xml'%i))
    for r in x.iter(A+'r'):
        rPr=r.find(A+'rPr')
        if rPr is None: continue
        sf=rPr.find(A+'solidFill/'+A+'srgbClr')
        if sf is not None: col[sf.get('val')]+=1
        la=rPr.find(A+'latin')
        if la is not None: fnt[la.get('typeface')]+=1
        if rPr.get('sz'): sz[int(rPr.get('sz'))//100]+=1
print("\n== 文字颜色 TOP ==", col.most_common(12))
print("== 字体 TOP ==", fnt.most_common(8))
print("== 字号分布 ==", sorted(sz.items()))
# 形状填充色
fill=collections.Counter(); line=collections.Counter()
for i in range(1,41):
    x=etree.fromstring(z.read('ppt/slides/slide%d.xml'%i))
    for sp in x.iter(P+'sp'):
        f=sp.find('.//'+P+'spPr/'+A+'solidFill/'+A+'srgbClr')
        if f is not None: fill[f.get('val')]+=1
        l=sp.find('.//'+P+'spPr/'+A+'ln/'+A+'solidFill/'+A+'srgbClr')
        if l is not None: line[l.get('val')]+=1
print("== 形状填充色 TOP ==", fill.most_common(10))
print("== 描边色 TOP ==", line.most_common(8))
# theme-color based fills (schemeClr)
sch=collections.Counter()
for i in range(1,41):
    x=etree.fromstring(z.read('ppt/slides/slide%d.xml'%i))
    for sp in x.iter(P+'sp'):
        f=sp.find('.//'+P+'spPr/'+A+'solidFill/'+A+'schemeClr')
        if f is not None: sch[f.get('val')]+=1
print("== 主题色填充 ==", sch.most_common(10))
