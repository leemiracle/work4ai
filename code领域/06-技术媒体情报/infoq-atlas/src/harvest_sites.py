"""多经典技术网站采集框架。

每个 source 是一个 adapter，产出统一记录 schema：
  source, source_type(feed/api/html), id, title, url, summary, author,
  published(iso str), tags(list), content(全文或''), lang, fetched_at

支持 RSS 2.0 / Atom（xml.etree）、JSON API、HTML（readability 抽取）。
采集后落 data/raw/sites/{source}.jsonl。
"""
from __future__ import annotations
import json
import re
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Any

from . import config as C

UA = C.USER_AGENT
NS = {"atom": "http://www.w3.org/2005/Atom",
      "content": "http://purl.org/rss/1.0/modules/content/",
      "dc": "http://purl.org/dc/elements/1.1/"}


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "*/*"})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last = e
            time.sleep(1.5)
    raise RuntimeError(f"GET {url}: {last}")


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _strip_html(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------- RSS 2.0 / Atom 解析 ----------------
def parse_feed(xml_bytes: bytes, source: str, lang: str = "zh") -> list[dict]:
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  [{source}] XML 解析失败: {e}")
        return items
    # Atom?
    if root.tag.endswith("feed"):
        for e in root.findall("atom:entry", NS):
            content_el = (e.find("atom:content", NS) or e.find("atom:summary", NS))
            content = _text(content_el)
            link = ""
            lkel = e.find("atom:link", NS)
            if lkel is not None:
                link = lkel.get("href", "") or _text(e.find("atom:id", NS))
            items.append(_rec(source, "feed", _text(e.find("atom:id", NS)),
                              _text(e.find("atom:title", NS)), link,
                              _strip_html(_text(e.find("atom:summary", NS))
                                          or content)[:500],
                              _text(e.find("atom:author/atom:name", NS)),
                              _text(e.find("atom:published", NS)),
                              [], _strip_html(content), lang))
    else:  # RSS 2.0
        for it in root.iter("item"):
            content = _text(it.find("content:encoded", NS)) or _text(it.find("description"))
            cats = [c.text for c in it.findall("category") if c.text]
            items.append(_rec(source, "feed",
                              _text(it.find("guid")) or _text(it.find("link")),
                              _text(it.find("title")), _text(it.find("link")),
                              _strip_html(_text(it.find("description")))[:500],
                              _text(it.find("dc:creator", NS)) or _text(it.find("author")),
                              _text(it.find("pubDate")),
                              cats, _strip_html(content), lang))
    return items


def _rec(source, stype, id_, title, url, summary, author, published, tags,
         content, lang) -> dict:
    if not id_:
        id_ = url or title
    return {"source": source, "source_type": stype, "id": id_,
            "title": _strip_html(title), "url": url,
            "summary": summary[:600], "author": author,
            "published": published, "tags": tags,
            "content": content[:50000], "lang": lang,
            "fetched_at": int(time.time())}


# ---------------- readability 全文抽取（HTML） ----------------
_TAG_RE = re.compile(r"<(script|style|nav|footer|header|aside|noscript)[^>]*>.*?</\1>",
                     re.S | re.I)
_BLOCK_RE = re.compile(r"<(p|article|section|div|li|td|h[1-6]|pre|blockquote)(\s[^>]*)?>"
                       r"(.*?)</\1>", re.S | re.I)


def extract_main_text(html: str) -> str:
    """简易 readability：去脚本/导航，取最长 <p> 文本块集合。"""
    if not html:
        return ""
    html = _TAG_RE.sub(" ", html)
    paras: list[str] = []
    for m in _BLOCK_RE.finditer(html):
        inner = m.group(3)
        txt = _strip_html(inner)
        if len(txt) >= 40:               # 过滤短碎片
            paras.append(txt)
    if not paras:
        return _strip_html(html)[:3000]
    # 取文本量大的连续段落
    paras.sort(key=len, reverse=True)
    out = "\n\n".join(paras[:60])
    return out[:30000]


# ---------------- 各经典站 adapter ----------------
def src_meituan() -> list[dict]:
    return parse_feed(_get("https://tech.meituan.com/atom.xml"), "美团技术团队", "zh")


def src_cnblogs() -> list[dict]:
    return parse_feed(_get("https://www.cnblogs.com/rss"), "博客园", "zh")


def src_oschina() -> list[dict]:
    return parse_feed(_get("https://www.oschina.net/news/rss"), "开源中国", "zh")


def src_zhangxinxu() -> list[dict]:
    return parse_feed(_get("https://www.zhangxinxu.com/wordpress/feed/"),
                      "张鑫旭-前端", "zh")


def src_hackernews(limit: int = 80) -> list[dict]:
    """HN Algolia API：按热度取 front_page 故事，多页。"""
    out = []
    for page in range(0, 2):
        url = (f"https://hn.algolia.com/api/v1/search?tags=front_page"
               f"&hitsPerPage={limit // 2}&page={page}")
        try:
            data = json.loads(_get(url))
        except Exception:
            continue
        for h in data.get("hits", []):
            tags = h.get("_tags", [])
            out.append(_rec("HackerNews", "api", str(h.get("objectID")),
                             h.get("title") or h.get("story_title") or "",
                             h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                             (h.get("story_text") or h.get("comment_text") or "")[:500],
                             h.get("author"), h.get("created_at"),
                             tags + [f"points:{h.get('points')}"], "", "en"))
        time.sleep(0.3)
    # 去重
    seen = set()
    uniq = []
    for r in out:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    return uniq


def src_devto(per_page: int = 60) -> list[dict]:
    """dev.to：热门(周榜) + 最新，并抓取头部全文。"""
    out: list[dict] = []
    for ep in ["top/7", "latest"]:
        url = f"https://dev.to/api/articles?per_page={per_page}&{ep}=1"
        try:
            data = json.loads(_get(url))
        except Exception:
            continue
        for a in data:
            out.append(_rec("dev.to", "api", str(a.get("id")),
                             a.get("title", ""), a.get("url", ""),
                             (a.get("description") or "")[:500],
                             a.get("user", {}).get("name", ""),
                             a.get("published_at"),
                             a.get("tag_list") or [], "", "en"))
        time.sleep(0.3)
    # 去重 + 抓头部全文
    seen = set()
    uniq = []
    for r in out:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    # 取 tag 命中多的/靠前的抓全文
    for r in uniq[:40]:
        aid = r["id"]
        try:
            full = json.loads(_get(f"https://dev.to/api/articles/{aid}"))
            body = full.get("body_markdown") or ""
            if body:
                r["content"] = _strip_html(body)[:40000]
            time.sleep(0.2)
        except Exception:
            pass
    return uniq


def src_ruanyifeng() -> list[dict]:
    """阮一峰科技爱好者周刊：HTML 列表页，解析每期链接。"""
    html = _get("https://www.ruanyifeng.com/blog/weekly/").decode("utf-8", "ignore")
    out = []
    for m in re.finditer(r'<a\s+href="(https?://www\.ruanyefeng\.com/blog/\d{4}/\d+/weekly-issue-\d+\.html)"[^>]*>'
                         r'科技爱好者周刊[^<]*</a>', html):
        url = m.group(1)
        out.append(_rec("阮一峰周刊", "html", url,
                         "科技爱好者周刊 " + url.rsplit("issue-", 1)[-1].split(".")[0],
                         url, "阮一峰每周技术资讯汇编", "阮一峰",
                         "", ["周刊"], "", "zh"))
    return out[-40:]   # 最近 40 期


def src_martinfowler() -> list[dict]:
    """Martin Fowler：软件架构权威博客，Atom feed。"""
    return parse_feed(_get("https://martinfowler.com/feed.atom"),
                      "MartinFowler", "en")


def src_csstricks() -> list[dict]:
    """CSS-Tricks：经典前端站，RSS。"""
    return parse_feed(_get("https://css-tricks.com/feed/"),
                      "CSS-Tricks", "en")


SOURCES = [
    ("美团技术团队", src_meituan),
    ("博客园", src_cnblogs),
    ("开源中国", src_oschina),
    ("张鑫旭-前端", src_zhangxinxu),
    ("HackerNews", src_hackernews),
    ("dev.to", src_devto),
    ("阮一峰周刊", src_ruanyifeng),
    ("MartinFowler", src_martinfowler),
    ("CSS-Tricks", src_csstricks),
]


def harvest_all(fetch_full: bool = True, full_sources=("美团技术团队", "张鑫旭-前端",
                                                       "博客园", "开源中国")):
    C.RAW.parent.mkdir(parents=True, exist_ok=True)
    sdir = C.ROOT / "data" / "raw" / "sites"
    sdir.mkdir(parents=True, exist_ok=True)
    grand = []
    for name, fn in SOURCES:
        try:
            items = fn()
        except Exception as e:
            print(f"  [{name}] 采集失败: {e}")
            continue
        # 可选：抓全文（正文过短则抓）
        if fetch_full and name in full_sources:
            got = 0
            for it in items[:80]:
                if len(it.get("content", "")) >= 300 or not it.get("url"):
                    continue
                try:
                    html = _get(it["url"], timeout=15).decode("utf-8", "ignore")
                    main = extract_main_text(html)
                    if len(main) > len(it.get("content", "")):
                        it["content"] = main
                    got += 1
                    time.sleep(0.2)
                except Exception:
                    pass
            print(f"  [{name}] 全文抓取 {got}/{len(items)}")
        path = sdir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        nfull = sum(1 for it in items if it.get("content"))
        print(f"  [{name}] {len(items)} 条（含全文 {nfull}）-> {path.name}")
        for it in items:
            grand.append(it)
    summary = {"fetched_at": int(time.time()),
               "sources": {fn.__name__: len(grand)}
               if False else
               {name: sum(1 for it in grand if it["source"] == name)
                for name, _ in SOURCES}}
    (sdir / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False,
                                                   indent=2), encoding="utf-8")
    print(f"\n[harvest] 共 {len(grand)} 条，来自 {len(summary['sources'])} 个经典站")
    return grand


if __name__ == "__main__":
    harvest_all()
