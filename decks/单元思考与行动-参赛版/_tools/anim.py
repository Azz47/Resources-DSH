# -*- coding: utf-8 -*-
"""
把 preview/deck.html 的 46 页真课件，重构成**单文件动画播放器**
（dsh-animations / ppt-animation 技能）。

产物：<deck>/第二单元 进入新时代-动画演示.html
  - 16:9 舞台，自适应缩放，黑板主题原样保留
  - 键盘 ←→ / 空格 / 滚轮 / 点击左右 / Home End / 触屏滑动 翻页
  - 顶部进度条（按板书五板块变色）+ 底部页码与按钮
  - 每次翻页后页内元素**依次缓入**（粉笔浮现感：淡入 + 上移 + 去模糊）
  - ?p=N 直达第 N 页；?still=1 全部静止显示（截图/打印用）
  - ?auto=秒 自动播放
"""
import base64
import io
import mimetypes
import os
import re

DECK = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SRC = os.path.join(DECK, "preview", "deck.html")
OUT = os.path.join(DECK, "第二单元 进入新时代-动画演示.html")
MEDIA = os.path.join(DECK, "media")

# 五板块主色（与 kit.py SEC 一致）
SEC_COLORS = ["#7FD6B0"] * 5 + ["#E8C15A"] * 13 + ["#6FC7E8"] * 11 + ["#EE8A72"] * 13 + ["#B9A7E8"] * 4
assert len(SEC_COLORS) == 46, len(SEC_COLORS)

raw = io.open(SRC, encoding="utf-8").read()

# ---- 1. 抽出 46 个 .slide ----
# （切块放在图片内联之后，见步骤 4 之前的重新切块）

# 背景断言：每页都是同一张黑板
bgs = set(re.findall(r'<div class="slide" style=\'([^\']*)\'', raw))
assert len(bgs) == 1, bgs
bg_css = list(bgs)[0]

# ---- 2. defs（箭头 marker）各页颜色不同，逐页重命名 id 以免全文档 id 冲突 ----

# ---- 3. 图片内联为 data URI ----
def data_uri(name):
    p = os.path.join(MEDIA, name)
    mime = mimetypes.guess_type(p)[0] or "application/octet-stream"
    b64 = base64.b64encode(open(p, "rb").read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


used = sorted(set(re.findall(r'\.\./media/([A-Za-z0-9_.\-]+)', raw)))
embed = {n: data_uri(n) for n in used if n != "image1.jpeg"}
print("内联图片：", ", ".join("%s(%dKB)" % (n, len(embed[n]) // 1024) for n in embed))

for n, uri in embed.items():
    raw = raw.replace("../media/" + n, uri)

# 图片内联之后再切块，否则切出来的是未内联的旧文本
blocks = re.findall(r'(<div class="slide"[^>]*>)(.*?)(</div></section>)', raw, re.S)
assert len(blocks) == 46, "slide count = %d" % len(blocks)

# image1（黑板底）单独提到样式表里，只出现一次
BB = data_uri("image1.jpeg")
print("黑板底图内联：%dKB" % (len(BB) // 1024))

# ---- 4. 组装页面 ----
pages_html = []
for i, (open_tag, body, _close) in enumerate(blocks, 1):
    body = body.replace('<marker id="arr"', '<marker id="arr%d"' % i)
    body = body.replace("url(#arr)", "url(#arr%d)" % i)
    body = re.sub(r'<div class="slide"[^>]*>', "", body)
    body = body.replace("../media/image1.jpeg", BB)  # 兜底
    # 去掉 slide 的内联背景，背景统一由样式表给
    pages_html.append('<div class="page" data-i="%d"><div class="slide">%s</div></div>' % (i, body))

PAGES = "\n".join(pages_html)
SEC_JS = "[" + ",".join('"%s"' % c for c in SEC_COLORS) + "]"
TITLES = re.findall(r'<div[^>]*class="el"[^>]*id="hd_title"[^>]*>(.*?)</div>', raw)
TITLES = [re.sub(r"<[^>]+>", "", t) for t in TITLES]

CSS = """
*{box-sizing:border-box;margin:0}
html,body{height:100%;background:#0f1418;overflow:hidden}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;color:#cfe0d6}
#app{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#stage{position:relative;width:960px;height:540px;transform-origin:center center;
  box-shadow:0 24px 70px rgba(0,0,0,.72),0 0 0 1px rgba(255,255,255,.06);border-radius:3px;overflow:hidden;background:#2A4436}
#pages{position:absolute;inset:0}
.page{position:absolute;inset:0;opacity:0;visibility:hidden;transform:scale(1.008);
  transition:opacity .18s ease,transform .42s cubic-bezier(.22,.85,.24,1)}
.page.active{opacity:1;visibility:visible;transform:none}
.slide{position:relative;width:960px;height:540px;overflow:hidden;
  background:url("__BB__") center / cover no-repeat}
.slide>img{max-width:none}

/* ---------- 元素出场：粉笔浮现 ---------- */
.page.play .slide>*{animation-name:kText;animation-duration:.46s;
  animation-timing-function:cubic-bezier(.22,.85,.24,1);animation-fill-mode:both;
  animation-delay:var(--d,0ms)}
.page.play .slide>.v-block{animation-name:kBlock;animation-duration:.40s}
.page.play .slide>.v-img{animation-name:kImg;animation-duration:.58s}
.page.play .slide>.v-line{animation-name:kLine;animation-duration:.44s;transform-origin:left center}
.page.play .slide>.v-bar{animation-name:kBar;animation-duration:.42s;transform-origin:left center}
/* 标题走「粉笔擦写」：从右往左揭开，同时由虚转实 */
.page.play .slide>#hd_title{animation-name:kChalk;animation-duration:.68s;
  animation-timing-function:cubic-bezier(.3,.9,.25,1)}
/* 分隔线走横向拉出，取代默认的整体缩放 */
.page.play .slide>#hd_rule,.page.play .slide>#hd_rule2{animation-name:kRule;animation-duration:.52s}
.slide>*{will-change:opacity,transform,filter}

@keyframes kText{from{opacity:0;transform:translateY(10px);filter:blur(6px)}to{opacity:1;transform:none;filter:blur(0)}}
@keyframes kBlock{from{opacity:0;transform:scale(.965)}to{opacity:1;transform:none}}
@keyframes kImg{from{opacity:0;transform:scale(1.035)}to{opacity:1;transform:none}}
@keyframes kLine{from{opacity:0;transform:scaleX(0)}to{opacity:1;transform:scaleX(1)}}
@keyframes kBar{from{opacity:0;transform:scaleX(.9)}to{opacity:1;transform:scaleX(1)}}
@keyframes kChalk{from{opacity:0;clip-path:inset(0 100% 0 0);filter:blur(3px)}
  to{opacity:1;clip-path:inset(0 0 0 0);filter:blur(0)}}
@keyframes kRule{from{opacity:.15;transform:scaleX(0)}to{opacity:1;transform:scaleX(1)}}
body.still .page.play .slide>*{animation:none!important;opacity:1!important;transform:none!important;filter:none!important}

/* ---------- HUD ---------- */
#prog{position:fixed;left:0;top:0;height:3px;width:100%;background:rgba(255,255,255,.07);z-index:40}
#progfill{height:100%;width:0;background:#7FD6B0;transition:width .22s ease,background .3s ease;
  box-shadow:0 0 12px currentColor}
#hud{position:fixed;left:0;right:0;bottom:0;z-index:40;display:flex;align-items:center;gap:14px;
  padding:0 22px 14px;font-size:12.5px;color:#8fa79a;opacity:0;transition:opacity .3s ease;
  background:linear-gradient(transparent,rgba(8,12,14,.85) 55%)}
#hud.show{opacity:1}
#hud .sp{flex:1}
#hud b{color:#e4eee2;font-weight:600;font-size:13px;letter-spacing:.3px}
#hud .cap{max-width:44%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
button{appearance:none;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);
  color:#cfe0d6;font:inherit;font-size:12.5px;padding:6px 12px;border-radius:6px;cursor:pointer;
  transition:.16s;white-space:nowrap}
button:hover{background:rgba(255,255,255,.13);border-color:rgba(255,255,255,.3);color:#fff}
button.on{background:#7FD6B0;border-color:#7FD6B0;color:#123024;font-weight:600}
#idx{font-variant-numeric:tabular-nums;color:#cfe0d6;font-size:13px}
#idx i{color:#6f8478;font-style:normal}
#toast{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:60;pointer-events:none;
  font-size:120px;font-weight:700;color:rgba(255,255,255,.14);opacity:0;transition:opacity .3s ease}
#toast.show{opacity:1}
@media (max-width:700px){#hud{font-size:11px;gap:8px;padding:0 10px 10px}.cap{display:none}}
""" .replace("__BB__", BB)

JS = """
(function(){
  var pages = [].slice.call(document.querySelectorAll('.page'));
  var N = pages.length, cur = 1, autoplay = 0, timer = null;
  var SEC = __SEC__, TITLES = __TITLES__;
  var still = /[?&]still=1/.test(location.search);

  var STEP = {0:70,1:70,2:110,3:150,4:80,5:110,6:95,7:130};

  function tierOf(el){
    var id = el.id || '';
    var kind = el.getAttribute('data-kind') || (el.tagName.toLowerCase() === 'svg' ? 'line' : 'shape');
    if (/^hd_chip/.test(id)) return 0;
    if (/^hd_(info|num)$/.test(id)) return 1;
    if (/^hd_sec$/.test(id)) return 2;
    if (/^hd_title$/.test(id)) return 3;
    if (el.tagName.toLowerCase() === 'svg') return 4;
    if (/^hd_rule/.test(id)) return 4;
    if (kind === 'image') return 5;
    if (id === 'sn' || /(bar|std|foot|grade|task|note)$/i.test(id)) return 7;
    return 6;
  }
  function variantOf(el){
    var id = el.id || '';
    var kind = el.getAttribute('data-kind') || '';
    if (el.tagName.toLowerCase() === 'svg') return 'v-line';
    if (kind === 'image') return 'v-img';
    if (kind === 'text') return 'v-text';
    if (kind === 'table' || kind === 'chart') return 'v-block';
    var st = el.getAttribute('style') || '';
    var h = parseFloat((st.match(/height:\\s*([\\d.]+)px/) || [0, 999])[1]);
    return h <= 14 ? 'v-bar' : 'v-block';
  }

  pages.forEach(function(pg){
    var kids = [].slice.call(pg.querySelector('.slide').children);
    var t = 0, delays = [];
    kids.forEach(function(el){
      var tr = tierOf(el);
      el.classList.add(variantOf(el));
      t += STEP[tr];
      delays.push(t);
    });
    var mx = delays.length ? delays[delays.length - 1] : 0;
    var k = mx > 2000 ? 2000 / mx : 1;
    kids.forEach(function(el, i){ el.style.setProperty('--d', Math.round(delays[i] * k) + 'ms'); });
  });

  var prog = document.getElementById('progfill'),
      ii = document.getElementById('idx'),
      cap = document.getElementById('cap'),
      toast = document.getElementById('toast'),
      hud = document.getElementById('hud');

  function paintHud(){
    var c = SEC[cur-1] || '#7FD6B0';
    prog.style.width = (cur / N * 100) + '%';
    prog.style.background = c; prog.style.color = c;
    ii.innerHTML = cur + '<i> / ' + N + '</i>';
    cap.textContent = TITLES[cur-1] || '';
  }
  function replay(pg){
    pg.classList.remove('play');
    void pg.offsetWidth;
    pg.classList.add('play');
  }
  function go(n, silent){
    n = Math.max(1, Math.min(N, n));
    if (n === cur && pages[cur-1].classList.contains('active')) { replay(pages[cur-1]); return; }
    pages[cur-1].classList.remove('active');
    cur = n;
    var pg = pages[cur-1];
    pg.classList.add('active');
    replay(pg);
    paintHud();
    if (!silent) flash();
    if (autoplay) restart();
  }
  function flash(){
    toast.textContent = cur;
    toast.classList.add('show');
    clearTimeout(flash._t);
    flash._t = setTimeout(function(){ toast.classList.remove('show'); }, 420);
  }
  function restart(){
    clearInterval(timer);
    if (autoplay) timer = setInterval(function(){
      if (cur >= N) { setAuto(0); return; }
      go(cur + 1);
    }, autoplay * 1000);
  }
  function setAuto(sec){
    autoplay = sec;
    document.getElementById('bAuto').classList.toggle('on', !!sec);
    document.getElementById('bAuto').textContent = sec ? ('自动 ' + sec + 's') : '自动播放';
    restart();
  }

  // ---- 输入 ----
  var lastWheel = 0;
  window.addEventListener('wheel', function(e){
    var now = Date.now();
    if (now - lastWheel < 520 || Math.abs(e.deltaY) < 6) return;
    lastWheel = now;
    go(cur + (e.deltaY > 0 ? 1 : -1));
  }, {passive: true});

  document.addEventListener('keydown', function(e){
    var k = e.key;
    if (k === 'ArrowRight' || k === 'ArrowDown' || k === 'PageDown' || k === ' ' || k === 'Enter') { e.preventDefault(); go(cur+1); }
    else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'PageUp') { e.preventDefault(); go(cur-1); }
    else if (k === 'Home') go(1);
    else if (k === 'End') go(N);
    else if (k === 'r' || k === 'R') replay(pages[cur-1]);
    else if (k === 'p' || k === 'P') setAuto(autoplay ? 0 : 14);
    else if (k === 'f' || k === 'F') toggleFs();
  });

  document.getElementById('stage').addEventListener('click', function(e){
    var r = this.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width;
    go(cur + (x < 0.33 ? -1 : 1));
  });

  var tx = 0, ty = 0;
  window.addEventListener('touchstart', function(e){ tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, {passive:true});
  window.addEventListener('touchend', function(e){
    var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 46 && Math.abs(dx) > Math.abs(dy)) go(cur + (dx < 0 ? 1 : -1));
  }, {passive:true});

  function toggleFs(){
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
  }

  // ---- 缩放 ----
  function fit(){
    var s = Math.min(window.innerWidth / 1000, (window.innerHeight - 74) / 560);
    document.getElementById('stage').style.transform = 'scale(' + s.toFixed(4) + ')';
  }
  window.addEventListener('resize', fit);
  fit();

  // ---- HUD 自动隐藏 ----
  var hideT;
  function poke(){
    hud.classList.add('show');
    clearTimeout(hideT);
    hideT = setTimeout(function(){ hud.classList.remove('show'); }, 2600);
  }
  window.addEventListener('mousemove', poke);
  window.addEventListener('touchstart', poke, {passive:true});

  document.getElementById('bPrev').onclick = function(e){ e.stopPropagation(); go(cur-1); };
  document.getElementById('bNext').onclick = function(e){ e.stopPropagation(); go(cur+1); };
  document.getElementById('bReplay').onclick = function(e){ e.stopPropagation(); replay(pages[cur-1]); };
  document.getElementById('bAuto').onclick = function(e){ e.stopPropagation(); setAuto(autoplay ? 0 : 14); };
  document.getElementById('bFull').onclick = function(e){ e.stopPropagation(); toggleFs(); };

  // ---- 启动 ----
  var m = location.search.match(/[?&]p=(\\d+)/);
  var start = m ? parseInt(m[1], 10) : 1;
  var ma = location.search.match(/[?&]auto=(\\d+)/);
  if (still) document.body.classList.add('still');
  pages[Math.max(1, Math.min(N, start)) - 1].classList.add('active');
  cur = Math.max(1, Math.min(N, start));
  replay(pages[cur-1]);
  paintHud();
  if (ma) setAuto(parseInt(ma[1], 10));
  poke();
})();
"""
JS = JS.replace("__SEC__", SEC_JS).replace("__TITLES__", "[" + ",".join(
    '"' + t.replace("\\", "").replace('"', '\\"') + '"' for t in TITLES) + "]")
assert "__SEC__" not in JS and "__TITLES__" not in JS

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>第二单元 进入新时代 · 单元思考与行动 —— 动画演示</title>
<style>__CSS__</style>
</head>
<body>
<div id="prog"><div id="progfill"></div></div>
<div id="app"><div id="stage"><div id="pages">
__PAGES__
</div></div></div>
<div id="toast"></div>
<div id="hud">
  <button id="bPrev">◀ 上一页</button>
  <button id="bNext">下一页 ▶</button>
  <button id="bReplay">重播本页 (R)</button>
  <button id="bAuto">自动播放</button>
  <button id="bFull">全屏 (F)</button>
  <span id="idx"></span>
  <span class="sp"></span>
  <span class="cap" id="cap"></span>
  <span>← → 翻页 · 滚轮/点击左右 · Home/End 首末页</span>
</div>
<script>__JS__</script>
</body>
</html>
"""
HTML = (HTML.replace("__CSS__", CSS).replace("__PAGES__", PAGES)
            .replace("__JS__", JS))

io.open(OUT, "w", encoding="utf-8").write(HTML)
print("写出:", OUT)
print("大小: %.2f MB" % (len(HTML.encode("utf-8")) / 1024 / 1024))
print("页数: %d" % len(pages_html))
