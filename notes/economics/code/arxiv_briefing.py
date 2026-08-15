#!/usr/bin/env python3
"""
arXiv 经济学前沿扫描器 — 每周定时简报
用法: python3 arxiv_briefing.py [--days 7]
输出: briefings/YYYY-MM-DD-econ-frontier.md
cron: 每周一 09:00 (见 README)
"""
import urllib.request, xml.etree.ElementTree as ET, re, os, sys, datetime

DAYS = 7
CATS = ["econ.GN", "econ.EM", "econ.TH"]
EXTRA_QUERIES = ['cat:cs.GT AND (all:mechanism OR all:auction OR all:market)']

def fetch(query, maxr=25):
    url = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(query) +
           f"&start=0&max_results={maxr}&sortBy=submittedDate&sortOrder=descending")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read().decode()
    except Exception as e:
        print(f"  fetch fail: {e}", file=sys.stderr); return ""

def parse(xml):
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    out = []
    try: root = ET.fromstring(xml)
    except Exception: return out
    for e in root.findall('a:entry', ns):
        title = ' '.join((e.findtext('a:title','',ns) or '').split())
        aid = (e.findtext('a:id','',ns) or '').replace('http://arxiv.org/abs/','')
        pub = (e.findtext('a:published','',ns) or '')[:10]
        summ = ' '.join((e.findtext('a:summary','',ns) or '').split())[:280]
        cats = [c.get('term') for c in e.findall('a:category', ns)]
        out.append((pub, aid, title, cats, summ))
    return out

def main():
    import urllib.parse
    cutoff = (datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat()
    seen, items = set(), []
    for c in CATS:
        for it in parse(fetch(f"cat:{c}")):
            if it[1] not in seen and it[0] >= cutoff:
                seen.add(it[1]); items.append((c,)+it)
    for q in EXTRA_QUERIES:
        for it in parse(fetch(q)):
            if it[1] not in seen and it[0] >= cutoff:
                seen.add(it[1]); items.append(('cs.GT*',)+it)
    items.sort(key=lambda x: x[1], reverse=True)
    today = datetime.date.today().isoformat()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'briefings')
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{today}-econ-frontier.md")
    with open(path, 'w') as f:
        f.write(f"# 经济学前沿简报 · {today}\n\n")
        f.write(f"> 覆盖: {', '.join(CATS)} + 筛选的 cs.GT 机制设计 | 近 {DAYS} 天 | 共 {len(items)} 篇\n")
        f.write("> 由 arxiv_briefing.py 自动生成\n\n---\n\n")
        for cat, pub, aid, title, cats, summ in items:
            f.write(f"### [{pub}] {title}\n\n")
            f.write(f"`{aid}` · {cat}\n\n{summ}...\n\n[全文](https://arxiv.org/abs/{aid})\n\n---\n\n")
    print(f"✓ {path} ({len(items)} papers)")

if __name__ == '__main__':
    main()
