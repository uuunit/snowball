#!/usr/bin/env python3
"""滚雪球网页版生成器"""
import json, os, re, html, datetime

ROOT = '/Volumes/T7/MacMini/Project/snowball-web'
DATA = json.load(open(f'{ROOT}/json/book_structure.json'))

def esc(s):
    return html.escape(s, quote=False)

def load_annotations():
    """加载注释（如果子 agent 已完成）"""
    ann = {}
    for f in ['annotations_all.json', 'annotations_1_31.json', 'annotations_32_62.json']:
        p = f'{ROOT}/json/{f}'
        if os.path.exists(p):
            for item in json.load(open(p)):
                ann[item['chap_no']] = item
    return ann

def load_quotes_hero():
    """从注释里抽金句给首页轮播"""
    ann = load_annotations()
    quotes = []
    for ch in sorted(ann.keys())[:12]:
        q = ann[ch].get('quote', '')
        title = next((c['title'] for p in DATA for c in p['chapters'] if c['chap_no'] == ch), '')
        if q:
            quotes.append((q, f"第{ch}章 {title}"))
    return quotes

def part_page(part, idx):
    """部分页"""
    pno, pname = part['part_no'], part['part_name']
    chapters = part['chapters']
    
    chap_links = ''.join(
        f'<a href="ch{c["chap_no"]:02d}.html"><span class="ch-no">{c["chap_no"]}</span>{esc(c["title"])}</a>'
        for c in chapters
    )
    
    img = f'<img class="hero-img" src="img/part{idx+1}.webp" alt="" loading="lazy">' if os.path.exists(f'{ROOT}/img/part{idx+1}.webp') else ''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{pno} {esc(pname)} - 滚雪球</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="hero" style="min-height:60vh">
  {img}
  <div class="hero-content">
    <div class="hero-kicker">{pno}</div>
    <h1 style="font-size:clamp(2.5rem,7vw,4.5rem)">{esc(pname)}</h1>
    <div class="hero-meta">{len(chapters)} 章 · {(datetime.datetime.now().year)}</div>
  </div>
</div>

<div class="toc">
  <div class="toc-title">目录</div>
  <div class="toc-desc">{pno} · {esc(pname)}</div>
  <div class="part">
    <div class="chapter-list">{chap_links}</div>
  </div>
  <div style="text-align:center;margin-top:40px">
    <a href="index.html" style="color:var(--gold);text-decoration:none;letter-spacing:.2em">← 返回首页</a>
  </div>
</div>
<div class="footer">滚雪球：巴菲特和他的财富人生 · 线稿极简插画版</div>
<script>
let fs=1;function adjFont(d){{fs=Math.max(.8,Math.min(1.6,fs+d*.1));document.documentElement.style.fontSize=fs+'em';localStorage.setItem('snowball-fs',fs)}}window.addEventListener('load',()=>{{let s=parseFloat(localStorage.getItem('snowball-fs'));if(s){{fs=s;document.documentElement.style.fontSize=fs+'em'}}}})
</script>
</body>
</html>'''

def chapter_page(ch, ann, prev, nxt):
    """章节内容页"""
    n = ch['chap_no']
    title = ch['title']
    subtitle = ch['subtitle']
    paras = ch['paras']
    
    # 正文段落（第一段首字下沉）
    body = []
    for i, p in enumerate(paras):
        cls = 'para para-dropcap' if i == 0 else 'para'
        body.append(f'<p class="{cls}">{esc(p)}</p>')
    
    # 章节配图（线稿风）
    chap_img = ''
    for ext in ['webp', 'jpg', 'png']:
        p = f'{ROOT}/img/ch/ch{n:02d}.{ext}'
        if os.path.exists(p):
            chap_img = f'<img class="chap-img" src="img/ch/ch{n:02d}.{ext}" alt="" loading="lazy">'
            break

    # 金句
    quote_html = ''
    a = ann.get(n)
    if a and a.get('quote'):
        quote_html = f'<div class="quote-card">{esc(a["quote"])}<span class="q-src">——《滚雪球》第{n}章</span></div>'

    # 注释
    ann_html = ''
    if a and a.get('annotation'):
        ann_html = f'<div class="annotation"><div class="annotation-title">✎ 注</div><div>{esc(a["annotation"])}</div></div>'

    # 左右侧栏
    sidebar = sidebar_html(n, title)
    
    prev_link = f'<a href="{prev[1]}" class="prev">← {prev[0]}</a>' if prev else '<span></span>'
    next_link = f'<a href="{nxt[1]}" class="next">{nxt[0]} →</a>' if nxt else '<span></span>'
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第{n}章 {esc(title)} - 滚雪球</title>
<link rel="stylesheet" href="style.css">
{f'<link rel="prefetch" href="{nxt[1]}">' if nxt else ''}
</head>
<body>
<div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
<div class="topbar">
  <a href="index.html" class="brand">滚雪球</a>
  <div class="nav-links">
    <span class="font-ctrl">
      <button onclick="adjFont(-1)" aria-label="缩小">A−</button>
      <button onclick="adjFont(1)" aria-label="放大">A+</button>
    </span>
    <a href="index.html">目录</a>
    <a href="#weread" class="only-desktop">微信读书</a>
  </div>
</div>

<div class="layout">
  <nav class="sidebar">
    <h3>目录</h3>
    {sidebar}
  </nav>
  
  <main class="content">
    <div class="chap-head">
      <h1 class="chap-title">第{n}章 {esc(title)}</h1>
      {f'<div class="chap-subtitle">{esc(subtitle)}</div>' if subtitle else ''}
    </div>
    {ann_html}
    {chap_img}
    {quote_html}
    {''.join(body)}
    
    <div class="page-nav" data-prev="{prev[1] if prev else ''}" data-next="{nxt[1] if nxt else ''}">
      {prev_link}
      {next_link}
    </div>
  </main>
  
  <aside class="aside">
    <div class="aside-box">
      <h4>本书信息</h4>
      <p>《滚雪球：巴菲特和他的财富人生》<br>艾丽斯·施罗德 著<br>中信出版社 纪念版</p>
    </div>
    <div class="aside-box">
      <h4>本页</h4>
      <p>第{n}章 · {esc(title)}<br>{len(paras)} 段 · {ch["char_count"]:,} 字</p>
    </div>
  </aside>
</div>

<div class="mobile-bar">
  {prev_link}
  <a href="index.html">目录</a>
  {next_link}
</div>
<div class="footer">滚雪球：巴菲特和他的财富人生 · 第{n}章</div>
<script>
let fs=1;function adjFont(d){{fs=Math.max(.8,Math.min(1.6,fs+d*.1));document.documentElement.style.fontSize=fs+'em';localStorage.setItem('snowball-fs',fs)}}window.addEventListener('load',()=>{{let s=parseFloat(localStorage.getItem('snowball-fs'));if(s){{fs=s;document.documentElement.style.fontSize=fs+'em'}}}})
window.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;let p=Math.min(100,Math.max(0,window.scrollY/h*100));let f=document.getElementById('progressFill');if(f)f.style.width=p+'%'}})
document.addEventListener('keydown',e=>{{let n=document.querySelector('.page-nav');if(!n)return;if(e.key==='ArrowLeft'&&n.dataset.prev)location.href=n.dataset.prev;if(e.key==='ArrowRight'&&n.dataset.next)location.href=n.dataset.next}})
</script>
</body>
</html>'''

def sidebar_html(cur_n, cur_title):
    parts = []
    for p in DATA:
        chs = ''.join(
            f'<div class="side-chapter"><a href="ch{c["chap_no"]:02d}.html" class="{"active" if c["chap_no"]==cur_n else ""}">{c["chap_no"]:02d} {esc(c["title"])}</a></div>'
            for c in p['chapters']
        )
        parts.append(f'<div class="side-part"><div class="side-part-name">{p["part_no"]} {esc(p["part_name"])}</div>{chs}</div>')
    return ''.join(parts)

def index_page(quotes):
    """首页"""
    # 目录
    parts_html = []
    for i, p in enumerate(DATA):
        chs = ''.join(
            f'<a href="ch{c["chap_no"]:02d}.html"><span class="ch-no">{c["chap_no"]}</span>{esc(c["title"])}</a>'
            for c in p['chapters']
        )
        total = sum(c['char_count'] for c in p['chapters'])
        parts_html.append(f'''
        <div class="part">
          <div class="part-head">
            <span class="part-no">{p["part_no"]}</span>
            <span class="part-name">{esc(p["part_name"])}</span>
            <span style="margin-left:auto;color:var(--gray);font-size:.85rem">{len(p["chapters"])}章 · {total:,}字</span>
          </div>
          <div class="chapter-list">{chs}</div>
        </div>''')
    
    hero_img = '<img class="hero-img" src="img/hero.webp" alt="">' if os.path.exists(f'{ROOT}/img/hero.webp') else ''
    
    # 金句轮播
    quote_html = ''
    if quotes:
        blocks = ''.join(
            f'<div class="quote-block" style="display:none"><div>{esc(q)}</div><div class="quote-src">—— {esc(src)}</div></div>'
            for q, src in quotes[:6]
        )
        quote_html = f'''
        <div class="quotes">
          <div class="quotes-title">书中金句</div>
          <div id="quoteRotate">{blocks}</div>
        </div>
        <script>
          (function(){{
            var qs = document.querySelectorAll('#quoteRotate .quote-block');
            var i = 0;
            if (qs.length > 0) qs[0].style.display = '';
            setInterval(function(){{
              if (qs.length === 0) return;
              qs[i].style.display = 'none';
              i = (i + 1) % qs.length;
              qs[i].style.display = '';
            }}, 5000);
          }})();
        </script>'''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>滚雪球：巴菲特和他的财富人生</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="hero">
  {hero_img}
  <div class="hero-content">
    <div class="hero-kicker">The Snowball</div>
    <h1>滚雪球</h1>
    <div class="hero-sub">沃伦·巴菲特和他的财富人生</div>
    <div class="hero-meta">艾丽斯·施罗德 著 · 纪念版 · 全62章</div>
  </div>
  <div class="scroll-hint">向下翻页</div>
</div>

<div class="toc">
  <div class="toc-title">目录</div>
  <div class="toc-desc">六部 · 六十二章 · 一场持续六十年的复利人生</div>
  {''.join(parts_html)}
</div>

{quote_html}

<div class="footer">滚雪球：巴菲特和他的财富人生 · 纪念版 · 由 AI 生成 · {datetime.datetime.now().year}</div>
<script>
let fs=1;function adjFont(d){{fs=Math.max(.8,Math.min(1.6,fs+d*.1));document.documentElement.style.fontSize=fs+'em';localStorage.setItem('snowball-fs',fs)}}window.addEventListener('load',()=>{{let s=parseFloat(localStorage.getItem('snowball-fs'));if(s){{fs=s;document.documentElement.style.fontSize=fs+'em'}}}})
</script>
</body>
</html>'''

def main():
    ann = load_annotations()
    print(f"注释已加载: {len(ann)} 章")
    
    # 所有章节列表（用于前后导航）
    all_chs = [c for p in DATA for c in p['chapters']]
    by_no = {c['chap_no']: c for c in all_chs}
    
    # 首页
    quotes = load_quotes_hero()
    open(f'{ROOT}/index.html', 'w').write(index_page(quotes))
    print("index.html ✓")
    
    # 部分页
    for i, p in enumerate(DATA):
        open(f'{ROOT}/part{i+1}.html', 'w').write(part_page(p, i))
        print(f"part{i+1}.html ✓ ({p['part_name']})")
    
    # 章节页
    for idx, c in enumerate(all_chs):
        n = c['chap_no']
        prev = None if idx == 0 else (all_chs[idx-1]['title'], f'ch{all_chs[idx-1]["chap_no"]:02d}.html')
        nxt = None if idx == len(all_chs)-1 else (all_chs[idx+1]['title'], f'ch{all_chs[idx+1]["chap_no"]:02d}.html')
        open(f'{ROOT}/ch{n:02d}.html', 'w').write(chapter_page(c, ann, prev, nxt))
        if idx % 10 == 0:
            print(f"ch{n:02d}.html ✓")
    print(f"章节页 ✓ ({len(all_chs)} 页)")
    
    total = sum(c['char_count'] for c in all_chs)
    print(f"\n全书 {len(all_chs)} 章 · {total:,} 字")
    print("完成！")

if __name__ == '__main__':
    main()
