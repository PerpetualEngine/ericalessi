#!/usr/bin/env python3
"""Build ericalessi.com in the Wikipedia-tables design.

Sources (edit these, never the generated pages):
  _src/canon.html            the Canon entries, <details class="entry"> markup per shelf
  _src/home.html             the old homepage (lab text, student quotes, newsletter sample)
  _src/journal/<slug>.html   one file per Practice Journal entry

Outputs (generated, overwritten on every run):
  index.html, contact-improvisation-canon/index.html, journal/<slug>/index.html

Run from the repo root:  python3 _src/build_site.py
"""
import re, os, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_src')
KIT = 'https://perpetual-engine.kit.com/47f9180ef6'
SITE = 'https://ericalessi.com'
UPDATED = 'October 2026'

# per-shelf pastel: header row, even rows
PASTEL = {1: ('#dbe3ef', '#f2f5f9'), 2: ('#dbe8ef', '#f2f7f9'), 3: ('#dbefdb', '#f2f9f2'), 4: ('#efe1db', '#f9f4f2'),
          5: ('#efe9db', '#f9f7f2'), 6: ('#efe5db', '#f9f6f2'), 7: ('#eadbef', '#f7f2f9'), 8: ('#e3efdb', '#f5f9f2'),
          9: ('#e0dbef', '#f4f2f9')}

CSS = r'''
:root{--blue:#3366cc;--rule:#a2a9b1;--boxbg:#f8f9fa;--ink:#202122;--muted:#54595d;--hair:#eaecf0}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:var(--ink);font-family:-apple-system,"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:14px;line-height:1.6}
a{color:var(--blue);text-decoration:none}a:visited{color:var(--blue)}a:hover{text-decoration:underline}
.topbar{border-bottom:1px solid var(--hair);padding:.55rem 1.2rem;font-size:13px;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;background:#fff;position:sticky;top:0;z-index:5}
.topbar .brand{font-family:"Linux Libertine",Georgia,"Times New Roman",serif;font-size:1.3rem;color:var(--ink)}
.topbar nav a{margin-left:1.1rem;color:var(--ink)}
.topbar nav a.cur{font-weight:700}
.layout{display:grid;grid-template-columns:230px minmax(0,1fr);max-width:1180px;margin:0 auto;gap:1.6rem;padding:1.2rem}
.sidebar{font-size:13px}
.toc{position:sticky;top:3.4rem;border:1px solid var(--hair);background:var(--boxbg);padding:.8rem 1rem;border-radius:2px;max-height:calc(100vh - 4.4rem);overflow:auto}
.toc h2{font-size:14px;margin:.1em 0 .5em;font-family:inherit;border:none;font-weight:700;padding:0}
.toc ul{list-style:none;margin:0;padding:0}
.toc li{margin:.35em 0}
.tocnum{color:var(--ink);margin-right:.4em}
h1{font-family:"Linux Libertine",Georgia,"Times New Roman",serif;font-size:2rem;font-weight:400;margin:0 0 .1em;border-bottom:1px solid var(--rule);padding-bottom:.15em;line-height:1.3}
.siteSub{font-size:12.5px;color:var(--muted);margin:0 0 1em}
.hatnote{font-size:13px;font-style:italic;color:var(--muted);padding-left:1.6em;margin:.4em 0 1em}
h2{font-family:"Linux Libertine",Georgia,"Times New Roman",serif;font-size:1.5rem;font-weight:400;border-bottom:1px solid var(--rule);margin:1.6em 0 .4em;padding-bottom:.15em;line-height:1.3}
h3{font-size:1.05rem;font-weight:700;margin:1.2em 0 .3em}
main p{margin:.5em 0}
.wdesc{color:var(--muted);margin:.2em 0 1em}
.wmeta{color:var(--muted);font-weight:400}
.wdet{color:var(--muted);font-size:13px}
.lang{font-size:10.5px;border:1px solid var(--rule);padding:0 .35em;margin-left:.4em;color:var(--muted);vertical-align:middle;font-weight:400}
.infobox{float:right;clear:right;width:272px;margin:0 0 1em 1.6em;border:1px solid var(--rule);background:var(--boxbg);font-size:12.5px;line-height:1.5;padding:0;border-radius:2px}
.infobox .ib-title{text-align:center;font-weight:700;font-size:14px;padding:.5em .6em;background:var(--hair)}
.infobox img{width:100%;display:block}
.infobox .cap{font-size:11.5px;color:var(--muted);padding:.3em .6em .4em;text-align:center}
.infobox table{border-collapse:collapse;width:100%}
.infobox th{text-align:left;vertical-align:top;padding:.35em .6em;width:42%;font-weight:700}
.infobox td{padding:.35em .6em}
.thumb{float:right;clear:right;margin:.5em 0 1em 1.6em;border:1px solid #c8ccd1;background:var(--boxbg);padding:3px;width:272px;font-size:12px}
.thumb img{width:100%;display:block;border:1px solid #c8ccd1}
.thumb .tcap{padding:.4em .3em .2em;color:var(--ink)}
.wikitable{border-collapse:collapse;font-size:13.5px;margin:1em 0;width:100%}
.wikitable th{background:var(--hair);border:1px solid var(--rule);padding:.4em .6em;text-align:left}
.wikitable td{border:1px solid var(--rule);padding:.4em .6em;vertical-align:top}
.wikitable td p{margin:.25em 0}
.catbox{border:1px solid var(--rule);background:var(--boxbg);font-size:13px;padding:.5em .8em;margin:2.5em 0 1em}
.catbox a{margin:0 .15em}
blockquote{margin:.6em 0 .6em 1.6em;color:#444;border-left:3px solid var(--hair);padding-left:1em}
blockquote p{margin:.3em 0}
.quote-attr{color:var(--muted);font-size:13px}
sup a{font-size:11px}sup a::before{content:"["}sup a::after{content:"]"}
.footnotes p{font-size:12.5px;margin:.3em 0}
.footnotes .fnum{display:inline-block;min-width:1.3em;color:var(--blue)}
.footnotes .fnum::before{content:"^ "}
.signoff{margin:1.4em 0}
.navbox{border:1px solid var(--rule);background:var(--boxbg);font-size:12.5px;margin:2em 0 0;padding:.5em .8em;width:100%}
.navbox th{background:var(--hair);text-align:center;padding:.3em}
.ambox{border:1px solid var(--rule);border-left:10px solid #36c;background:#fbfbfb;padding:.5em 1em;margin:.8em 0 1.2em;font-size:13px}
.sister{border:1px solid var(--rule);background:var(--boxbg);padding:.8em 1em;margin:1.2em 0;font-size:13px}
.sister .s-head{font-weight:700;font-size:14px;margin-bottom:.2em}
.sister .btn{display:inline-block;margin-top:.5em;border:1px solid var(--rule);background:#fff;padding:.35em .9em;border-radius:2px;color:var(--ink);font-weight:600}
.sister .btn:hover{text-decoration:none;background:var(--hair)}
.sample{border:1px solid var(--hair);background:#fff;padding:1em 1.2em;margin:.8em 0 0;font-size:13.5px}
.sample .lab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-top:.9em}
.sample .q{font-family:"Linux Libertine",Georgia,"Times New Roman",serif;font-size:1.2rem;margin:.2em 0}
.footer{max-width:1180px;margin:2rem auto 0;padding:1rem 1.2rem 2rem;border-top:1px solid var(--hair);font-size:12px;color:var(--muted)}
''' + '\n'.join('.s%d table.wikitable th{background:%s} .s%d table.wikitable tr:nth-child(even) td{background:%s}' % (n, a, n, b) for n, (a, b) in PASTEL.items()) + r'''
@media(max-width:900px){.layout{display:block;padding:1rem}.toc{position:static;margin-bottom:1.2rem;max-height:none}.infobox,.thumb{float:none;width:100%;margin:0 0 1em}.topbar nav a{margin:0 .9rem 0 0}.topbar{position:static}}
'''

HEAD_SCRIPTS = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CTZBMMVBGR"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-CTZBMMVBGR');</script>
<script data-goatcounter="https://alessieric.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'''


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def nav(cur):
    items = [('World Library', '/contact-improvisation-canon/'), ('Classes', '/#curiosilab'), ('Journal', '/#journal'), ('Subscribe', KIT)]
    return ''.join('<a href="%s"%s>%s</a>' % (u, ' class="cur"' if n == cur else '', n) for n, u in items)


def shell(title, url, cur, toc_items, body, desc, og_type='website', og_image=None, og_title=None, og_desc=None):
    toc = '<ul>' + ''.join(toc_items) + '</ul>'
    og_image = og_image or SITE + '/images/eric-alessi-portrait.jpg'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_SCRIPTS}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<meta property="og:title" content="{H.escape(og_title or title)}">
<meta property="og:description" content="{H.escape(og_desc or desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_image}">
<link rel="canonical" href="{url}">
<style>{CSS}</style>
</head>
<body>
<div class="topbar"><a class="brand" href="/">Eric Alessi</a><nav>{nav(cur)}</nav></div>
<div class="layout">
<aside class="sidebar"><div class="toc"><h2>Contents</h2>{toc}</div></aside>
<main>
{body}
</main>
</div>
<div class="footer">Eric Alessi &middot; Updated {UPDATED} &middot; Contact Improvisation &middot; Koh Phangan, Thailand</div>
</body>
</html>'''


def write(rel, content):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(content)


# ---------------------------------------------------------------- Canon
def parse_canon():
    s = open(os.path.join(SRC, 'canon.html')).read()
    shelves = []
    pos = [m.start() for m in re.finditer(r'<details class="shelf" id="shelf\d"', s)] + [s.find('<h2 style="margin-top:3.5rem">Anything missing?')]
    for n in range(9):
        seg = s[pos[n]:pos[n + 1]]
        title = re.search(r'shelf-title">(.*?)</span>', seg, re.S).group(1).strip()
        desc = re.search(r'shelf-desc">(.*?)</span>', seg, re.S)
        desc = re.sub(r'\s+', ' ', desc.group(1)).strip() if desc else ''
        entries = []
        for m in re.finditer(r'<details class="entry"(?: data-cost="(\w+)")?[^>]*>\s*<summary>\s*<h3>(.*?)</h3>\s*</summary>(.*?)</details>', seg, re.S):
            cost, h3, body = m.groups()
            meta = re.search(r'<span class="meta">(.*?)</span>', h3, re.S)
            lang = re.search(r'<span class="lang-tag">(.*?)</span>', h3, re.S)
            t = re.sub(r'<span class="meta">.*?</span>', '', h3, flags=re.S)
            t = re.sub(r'<span class="lang-tag">.*?</span>', '', t, flags=re.S).strip()
            metatxt = re.sub(r'^\s*&middot;\s*', '', re.sub(r'\s+', ' ', meta.group(1)).strip()) if meta else ''
            det = None; src = []; paras = []
            for p in re.findall(r'<p[^>]*>.*?</p>', body, re.S):
                inner = re.sub(r'^<p[^>]*>|</p>$', '', p.strip(), flags=re.S).strip()
                if 'class="bestfor"' in p:
                    lab = re.match(r'\s*<b>(.*?)</b>\s*&middot;\s*(.*)', inner, re.S)
                    if lab and lab.group(1) == 'Details': det = lab.group(2).strip()
                    elif lab: src.append((lab.group(1), lab.group(2).strip()))
                    else: paras.append(inner)
                else:
                    paras.append(inner)
            show_meta = metatxt
            if paras:
                first = strip_tags(paras[0]); mt = strip_tags(metatxt)
                if mt.endswith('…') and first.startswith(mt[:-1].strip()[:60]): show_meta = ''
                elif first == mt: paras = paras[1:]
            if not cost:
                cost = 'free' if 'free' in ' '.join(v for _, v in src).lower() else 'paid'
            entries.append(dict(cost=cost, title=t, meta=show_meta, fullmeta=metatxt, lang=lang.group(1) if lang else '', det=det, src=src, paras=paras))
        shelves.append(dict(n=n + 1, title=title, desc=desc, entries=entries))
    return shelves


def render_table(sh):
    rows = []
    for e in sh['entries']:
        what = ' '.join('<p>%s</p>' % x for x in ([e['meta']] if e['meta'] else []) + e['paras'])
        where = ' '.join(v for _, v in e['src']) or '<span class="wdet">see entry</span>'
        price = re.search(r'(\$\d+[^.<]*)', e['fullmeta'])
        cost = 'Free' if e['cost'] == 'free' else ('Paid' + (' · ' + price.group(1).strip() if price else ''))
        lang = '<span class="lang">%s</span>' % e['lang'] if e['lang'] else ''
        rows.append('<tr><td><b>%s</b>%s<br><span class="wmeta">%s</span></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e['title'], lang, e['det'] or '', what, where, cost))
    if sh['n'] == 7: h = ('Film / footage', 'What it is', 'Where to watch')
    elif sh['n'] in (8, 9): h = ('Book', 'What it is, and why it belongs', 'Where to find it')
    else: h = ('Work', 'What it argues, and when to reach for it', 'Source')
    return '<table class="wikitable"><tr><th style="width:24%%">%s</th><th>%s</th><th style="width:22%%">%s</th><th style="width:9%%">Cost</th></tr>' % h + ''.join(rows) + '</table>'


def build_canon():
    shelves = parse_canon()
    total = sum(len(s['entries']) for s in shelves)
    free = sum(1 for s in shelves for e in s['entries'] if e['cost'] == 'free')
    body = [
        '<h1>The Contact Improvisation Canon</h1>',
        '<div class="siteSub">Eric Alessi\'s World Library &middot; %d works on 9 shelves &middot; %d free, %d paid &middot; updated %s</div>' % (total, free, total - free, UPDATED),
        '<div class="hatnote">"World Library" redirects here. This page lists the texts, films and books of Contact Improvisation, annotated by <a href="/">Eric Alessi</a>.</div>',
        '<div class="infobox"><div class="ib-title">The Contact Improvisation Canon</div><table>'
        '<tr><th>Curator</th><td><a href="/">Eric Alessi</a></td></tr><tr><th>Subject</th><td>Contact Improvisation</td></tr><tr><th>Works</th><td>%d</td></tr>'
        '<tr><th>Free to read or watch</th><td>%d</td></tr><tr><th>Shelves</th><td>9</td></tr><tr><th>Languages</th><td>7</td></tr><tr><th>Started</th><td>September 2026</td></tr></table></div>' % (total, free),
        '<p>A directory I keep growing: the <a href="#shelf1">texts</a> and <a href="#shelf7">films</a> that shape my practice and my teaching, on nine shelves. Each entry says what the work argues and when to reach for it. Where a work has a free, legal home, the entry links to it; sources are being added shelf by shelf. Where a work is for sale, buy it.</p>',
        '<p>The undertaking is deliberately big: to gather every interesting piece of work on Contact Improvisation and share it here, for the benefit of the global CI community. If something essential is missing, <a href="mailto:eric@perpetualnurture.com?subject=Canon%20suggestion">write to me</a>.</p>',
        '<div class="ambox">One clarification on the paid entries: today I earn nothing from anything listed here. No commissions, and no association with any of the authors cited. I am sharing what I find interesting. If that ever changes, for example if book links become affiliate links, I will say so here first.</div>']
    toc = []
    for sh in shelves:
        toc.append('<li><a href="#shelf%d"><span class="tocnum">%d</span> %s</a></li>' % (sh['n'], sh['n'], sh['title']))
        body.append('<section class="s%d"><h2 id="shelf%d">%s <span class="wmeta" style="font-size:.6em">&middot; %d entries</span></h2>' % (sh['n'], sh['n'], sh['title'], len(sh['entries'])))
        if sh['desc']: body.append('<p class="wdesc"><i>%s</i></p>' % sh['desc'])
        body.append(render_table(sh) + '</section>')
    toc.append('<li><a href="#missing"><span class="tocnum">10</span> Anything missing?</a></li>')
    body.append('<h2 id="missing">Anything missing?</h2><p>Suggest a work: title, author, and where it lives. <a href="mailto:eric@perpetualnurture.com?subject=Canon%20suggestion">eric@perpetualnurture.com</a>.</p>')
    body.append('<div class="sister"><div class="s-head">Fuel for the curious dancer</div>One short email a week. One minute to read and be inspired.<br><a class="btn" href="%s">Fuel my curiosity!</a></div>' % KIT)
    body.append('<div class="catbox"><b>Categories:</b> Contact Improvisation &middot; Reading lists &middot; Dance literature &middot; Somatics &middot; Koh Phangan</div>')
    desc = "The Contact Improvisation Canon: a directory of the form's essential texts and films, annotated. Paxton's own words, the gravity school, attention, consent, jams, history, and the OGs' Circle. Every entry links to a legal source."
    write('contact-improvisation-canon/index.html', shell('The Contact Improvisation Canon · Eric Alessi', SITE + '/contact-improvisation-canon/', 'World Library', toc, '\n'.join(body), desc,
          og_image=SITE + '/images/beauty-of-pain-02.jpg', og_title='The Contact Improvisation Canon',
          og_desc="A directory of the form's essential texts, films and books, annotated. %d works across seven languages." % total))
    return total


# ---------------------------------------------------------------- Journal
JOURNAL = [  # (source slug, entry number, title for nav)
    ('the-floor-becomes-the-ceiling-floor-as-sky-contact-improvisation', 1, 'The Floor Becomes the Ceiling'),
    ('a-space-of-nothing-robert-dunn-john-cage-steve-paxton', 2, 'A Space of Nothing'),
]


def build_journal():
    for i, (slug, no, navtitle) in enumerate(JOURNAL):
        s = open(os.path.join(SRC, 'journal', slug + '.html')).read()
        art = re.search(r'<article>(.*?)</article>', s, re.S).group(1)
        title = re.search(r'<h1 class="article-title">(.*?)</h1>', art).group(1)
        author = strip_tags(re.search(r'<div class="article-author">(.*?)</div>', art).group(1))
        meta = lambda k: (re.search(r'<meta (?:name|property)="%s" content="(.*?)"' % k, s) or [None, ''])[1]
        page_title = re.search(r'<title>(.*?)</title>', s).group(1)
        art = re.sub(r'<div class="chapter-tag">.*?</div>\s*<div class="article-author">.*?</div>\s*<h1 class="article-title">.*?</h1>', '', art, flags=re.S)
        art = re.sub(r'<div class="subscribe stamp">.*?</div>\s*</div>', '', art, flags=re.S)
        art = art.replace('<p class="sign-off">', '<p class="signoff">')
        art = art.replace('<div class="footnotes">', '<h2 id="refs">References</h2><div class="footnotes">')
        toc = []; k = 0
        for h in re.findall(r'<h2>(.*?)</h2>', art):
            k += 1; hid = 's%d' % k
            art = art.replace('<h2>%s</h2>' % h, '<h2 id="%s">%s</h2>' % (hid, h), 1)
            toc.append('<li><a href="#%s"><span class="tocnum">%d</span> %s</a></li>' % (hid, k, strip_tags(h)))
        toc.append('<li><a href="#refs"><span class="tocnum">%d</span> References</a></li>' % (k + 1))
        prev = JOURNAL[i - 1] if i > 0 else None
        nxt = JOURNAL[i + 1] if i + 1 < len(JOURNAL) else None
        pv = '<a href="/journal/%s/">&larr; %s</a>' % (prev[0], prev[2]) if prev else '<a href="/#journal">&larr; All entries</a>'
        nx = '<a href="/journal/%s/">%s &rarr;</a>' % (nxt[0], nxt[2]) if nxt else ''
        body = f'''<h1>{title}</h1>
<div class="siteSub">The Practice Journal &middot; Entry {no:02d} (2026) &middot; {author}</div>
<div class="hatnote">An entry in <a href="/#journal">The Practice Journal</a>, Eric Alessi's weekly record of what was taught and what the dancers found.</div>
<div class="infobox"><div class="ib-title">{title}</div><table><tr><th>Series</th><td>The Practice Journal</td></tr><tr><th>Entry</th><td>{no:02d} of {len(JOURNAL)}</td></tr><tr><th>Author</th><td><a href="/">Eric Alessi</a></td></tr><tr><th>Published</th><td>September 2026</td></tr><tr><th>Place</th><td>Koh Phangan, Thailand</td></tr></table></div>
{art}
<div class="sister"><div class="s-head">Fuel for the curious dancer</div>One short email a week. One minute to read and be inspired.<br><a class="btn" href="{KIT}">Fuel my curiosity!</a></div>
<table class="navbox"><tr><th colspan="2">The Practice Journal</th></tr><tr><td>{pv}</td><td style="text-align:right">{nx}</td></tr></table>
<div class="catbox"><b>Categories:</b> The Practice Journal &middot; Contact Improvisation &middot; Koh Phangan</div>'''
        write('journal/%s/index.html' % slug, shell(page_title, SITE + '/journal/%s/' % slug, 'Journal', toc, body, meta('description'), og_type='article',
              og_image=meta('og:image') or None, og_title=meta('og:title') or None, og_desc=meta('og:description') or None))


# ---------------------------------------------------------------- Home
def build_home(total):
    home = open(os.path.join(SRC, 'home.html')).read()
    quotes = re.search(r'<h2 class="brushed">From the students</h2>(.*?)<div class="subscribe', home, re.S).group(1)
    qrows = ''
    for m in re.finditer(r'<blockquote>(.*?)</blockquote>', quotes, re.S):
        q = m.group(1); who = re.search(r'<p class="quote-attr">~\s*(.*?)</p>', q)
        said = re.sub(r'<p class="quote-attr">.*?</p>', '', q, flags=re.S).strip()
        qrows += '<tr><td style="width:18%%"><b>%s</b></td><td>%s</td></tr>' % (strip_tags(who.group(1)) if who else '', said)
    quotes_table = '<table class="wikitable"><tr><th>Dancer</th><th>Said</th></tr>' + qrows + '</table>'
    sample = re.search(r'<div class="sheet email">(.*?)<p class="signoff">', home, re.S).group(1)
    parts = re.findall(r'<div class="lab">(.*?)</div>(.*?)</div></div>', sample, re.S)
    sample_html = '<div class="sample"><b>Fuel for the curious dancer</b> <span class="wdet">&middot; sample edition</span><p>One statement, one question, and one practice for your week.</p>'
    for labtxt, rest in parts:
        rest = rest.replace('<p class="quote">', '<p class="q">').replace('<p class="who">', '<p class="quote-attr">')
        sample_html += '<div class="lab">%s</div>%s' % (labtxt, rest)
    sample_html += '<p class="signoff">Until next week,<br><b>Eric</b></p></div>'
    lab_table = '''<table class="wikitable"><tr><th style="width:24%">CuriosiLab</th><th>Details</th></tr>
<tr><td><b>What it is</b></td><td>Eric's five-hour private group lab, for committed practitioners, held weekly on Koh Phangan.</td></tr>
<tr><td><b>The format</b></td><td>One small group, one garden studio. Eric comes with material, and the group only explores what it truly needs: centers of gravity, the Axis Syllabus, horizontal and vertical planes and beyond, ground work, subtle awareness, the art of falling, fears and the mindless state, and beyond.</td></tr>
<tr><td><b>The tools</b></td><td>Exercises, sharings, written notes, and the witnessing of duets, with space for each dance to develop. Eric gives each dancer his unhurried attention, observing and dancing with them one by one. His feedback is direct and immediate. It helps the dancer receiving it, and it teaches everyone watching.</td></tr>
<tr><td><b>Group size</b></td><td>From six dancers, capped at eight, so everyone gets direct attention and feedback.</td></tr>
<tr><td><b>The four-week program</b></td><td>The deeper format: one lab a week for a month. That is the ideal vision, to truly transform from the inside out.</td></tr>
<tr><td><b>Join the next lab</b></td><td><a href="mailto:eric@perpetualnurture.com?subject=The%20five-hour%20lab">Write to Eric</a>.</td></tr></table>'''
    journal_rows = ''.join('<tr><td>%02d</td><td><a href="/journal/%s/">%s</a><br><span class="wdet">%s</span></td><td>September 2026</td></tr>' % (no, slug, t, d) for (slug, no, t), d in zip(JOURNAL, [
        'Centers of gravity, grounding, and a score that reverses where support comes from.',
        "Robert Ellis Dunn's composition class, the clearing with no recipe, and why I keep coming back to it."]))
    body = f'''<h1>Eric Alessi</h1>
<div class="siteSub">Contact Improvisation teacher &middot; Koh Phangan, Thailand</div>
<div class="hatnote">This page is about the teacher and his lab. For the reading list, see <a href="/contact-improvisation-canon/">The Contact Improvisation Canon</a>. For the newsletter, see <a href="#newsletter">Fuel for the curious dancer</a>.</div>
<div class="infobox"><div class="ib-title">Eric Alessi</div><img src="/images/eric-alessi-portrait.jpg" alt="Eric Alessi sitting on a wooden studio floor in a yellow linen shirt, smiling."><div class="cap">Koh Phangan, 2026</div><table>
<tr><th>Practice</th><td>Contact Improvisation</td></tr><tr><th>Based in</th><td>Koh Phangan, Thailand</td></tr><tr><th>Teaches</th><td>Weekly classes, jams, and <a href="#curiosilab">CuriosiLab</a>, a five-hour private lab</td></tr><tr><th>Writes</th><td><a href="#journal">The Practice Journal</a></td></tr><tr><th>Curates</th><td><a href="/contact-improvisation-canon/">The Contact Improvisation Canon</a></td></tr><tr><th>Newsletter</th><td><a href="#newsletter">Fuel for the curious dancer</a></td></tr><tr><th>Instagram</th><td><a href="https://www.instagram.com/eric.alessi.ci/">@eric.alessi.ci</a></td></tr></table></div>
<p><b>Eric Alessi</b> teaches Contact Improvisation in Koh Phangan, Thailand: weekly classes, jams, and five-hour private labs. In his own words, his curiosity lives at the intersection of Contact Improvisation and Zen, right where no-mind meets gravity.</p>
<div class="thumb"><img src="/media/hero-poster.jpg" alt=""><div class="tcap">In the studio, Koh Phangan.</div></div>
<section class="s2"><h2 id="curiosilab">CuriosiLab</h2>
{lab_table}</section>
<section class="s5"><h2 id="students">From the students</h2>
{quotes_table}</section>
<section class="s1"><h2 id="journal">The Practice Journal</h2>
<p>Each class is documented from both sides: what was taught, and what the dancers found, in their own words from the recorded closing sharing. Each entry ends with one thing to practice and a question to carry.</p>
<table class="wikitable"><tr><th style="width:8%">No.</th><th>Entry</th><th style="width:20%">Published</th></tr>{journal_rows}</table></section>
<h2 id="library">The World Library</h2>
<p><a href="/contact-improvisation-canon/">The Contact Improvisation Canon</a>: {total} texts, films and books on nine shelves, each annotated with what it argues and when to reach for it, and linked to a free legal home where one exists.</p>
<h2 id="newsletter">Fuel for the curious dancer</h2>
<div class="sister"><div class="s-head">Join my newsletter</div>One short email a week. One minute to read and be inspired.<br><a class="btn" href="{KIT}">Fuel my curiosity!</a></div>
<p class="wdet">Not yet sure? Here is a newsletter sample:</p>
{sample_html}
<div class="catbox"><b>Categories:</b> Contact Improvisation teachers &middot; Koh Phangan &middot; Somatics</div>'''
    toc = ['<li><a href="#curiosilab"><span class="tocnum">1</span> CuriosiLab</a></li>', '<li><a href="#students"><span class="tocnum">2</span> From the students</a></li>',
           '<li><a href="#journal"><span class="tocnum">3</span> The Practice Journal</a></li>', '<li><a href="#library"><span class="tocnum">4</span> The World Library</a></li>',
           '<li><a href="#newsletter"><span class="tocnum">5</span> Fuel for the curious dancer</a></li>']
    write('index.html', shell('Eric Alessi · Contact Improvisation, Koh Phangan', SITE + '/', 'Home', toc, body,
          'Eric Alessi teaches Contact Improvisation in Koh Phangan, Thailand: weekly classes, jams, and five-hour private labs. The Practice Journal: five things guiding the practice each week.',
          og_image=SITE + '/images/beauty-of-pain-02.jpg', og_desc='Weekly classes, jams, and five-hour private labs in Koh Phangan, Thailand.'))


if __name__ == '__main__':
    total = build_canon()
    build_journal()
    build_home(total)
    print('built: canon %d works, %d journal entries, home' % (total, len(JOURNAL)))
