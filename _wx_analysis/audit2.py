import sys, os, json, zipfile, re, hashlib
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
SRC=r"D:\Resources\xwechat_files\wxid_9ka181duelek22_80a9\msg\file\2026-10\单元思考与行动(1).pptx"
OUT=r"D:\Resources\DSH\_wx_analysis"; MED=os.path.join(OUT,'media'); os.makedirs(MED,exist_ok=True)
z=zipfile.ZipFile(SRC)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
A='{%s}'%ns['a']; P='{%s}'%ns['p']; R='{%s}'%ns['r']
EMU=12700.0
def pt(v): return round(int(v)/EMU,2)
# media info
print("== MEDIA ==")
tot=0
for n in sorted(z.namelist()):
    if n.startswith('ppt/media/'):
        b=z.read(n); tot+=len(b)
        open(os.path.join(MED,os.path.basename(n)),'wb').write(b)
        dims=''
        if n.lower().endswith(('.jpeg','.jpg','.png')):
            try:
                from PIL import Image; import io
                im=Image.open(io.BytesIO(b)); dims='%dx%d %s ar=%.3f'%(im.size[0],im.size[1],im.mode,im.size[0]/im.size[1])
                im.convert('RGB').resize((1,1)).getpixel((0,0))
            except Exception as e: dims=str(e)
        print("  %-24s %8d B  %s"%(n.split('/')[-1],len(b),dims))
print("  media total bytes:",tot)
# per slide bg + pictures + effects
print("\n== SLIDES: bg / pictures / effects ==")
rows=[]
for i in range(1,41):
    x=etree.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
    bg=x.find('.//'+P+'cSld/'+P+'bg')
    bgs='inherit'
    if bg is not None:
        bl=bg.find('.//'+A+'blip')
        bgs='PIC '+bl.get(R+'embed') if bl is not None else ('solid '+ (bg.find('.//'+A+'srgbClr').get('val') if bg.find('.//'+A+'srgbClr') is not None else '?'))
    pics=[]
    for pic in x.iter(P+'pic'):
        nv=pic.find('.//'+P+'cNvPr'); xf=pic.find('.//'+A+'xfrm')
        off=xf.find(A+'off'); ext=xf.find(A+'ext')
        src=pic.find('.//'+A+'blip').get(R+'embed')
        eff = pic.find('.//'+P+'spPr/'+A+'effectLst')
        ln  = pic.find('.//'+P+'spPr/'+A+'ln')
        pics.append((nv.get('name'), pt(off.get('x')), pt(off.get('y')), pt(ext.get('cx')), pt(ext.get('cy')),
                     src, 'SHADOW' if eff is not None and eff.find(A+'outerShdw') is not None else ('eff' if eff is not None else '-'),
                     'LINE' if ln is not None else '-'))
    rows.append((i,bgs,pics))
# rels per slide
for i,bgs,pics in rows:
    if bgs!='inherit' or any(p[6]!='-' or p[7]!='-' for p in pics):
        print(f"p{i:02d} bg={bgs} " + "; ".join(f"{p[0]}@{p[1]},{p[2]} {p[3]}x{p[4]} src={p[5]} {p[6]} {p[7]}" for p in pics))
print("  (未列出的页 = 母版底图 + 无阴影无描边图片)")
