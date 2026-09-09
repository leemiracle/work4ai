"""深度采集：对可扩展的经典站做多页/归档抓取，大幅扩充样本。

- dev.to   : latest/top 多页（API 分页可靠）
- HackerNews : Algolia 多页 + 按 points 取热门故事
- 博客园   : 抓「编辑推荐 pick」+ 多个分类列表页
- 开源中国 : 抓新闻列表多页
"""
from __future__ import annotations
import json
import re
import time
from . import config as C
from .harvest_sites import (_get, _rec, _strip_html, extract_main_text, parse_feed)

SDIR = C.ROOT / "data" / "raw" / "sites"


def deep_devto(pages: int = 5) -> list[dict]:
    out: list[dict] = []
    seen = set()
    for ep in ["top/7", "top/30", "latest"]:
        for page in range(1, pages + 1):
            url = f"https://dev.to/api/articles?per_page=50&page={page}&{ep}=1"
            try:
                data = json.loads(_get(url, timeout=20))
            except Exception:
                continue
            if not data:
                break
            for a in data:
                aid = str(a.get("id"))
                if aid in seen:
                    continue
                seen.add(aid)
                out.append(_rec("dev.to", "api", aid, a.get("title", ""),
                                a.get("url", ""),
                                (a.get("description") or "")[:400],
                                a.get("user", {}).get("name", ""),
                                a.get("published_at"),
                                a.get("tag_list") or [], "", "en"))
            time.sleep(0.25)
    return out


def deep_hackernews(pages: int = 5) -> list[dict]:
    out: list[dict] = []
    seen = set()
    for tag in ["front_page", "story"]:
        for page in range(pages):
            url = (f"https://hn.algolia.com/api/v1/search?tags={tag}"
                   f"&hitsPerPage=50&page={page}")
            try:
                data = json.loads(_get(url, timeout=20))
            except Exception:
                continue
            for h in data.get("hits", []):
                oid = str(h.get("objectID"))
                if oid in seen:
                    continue
                seen.add(oid)
                out.append(_rec("HackerNews", "api", oid,
                                h.get("title") or h.get("story_title") or "",
                                h.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                                (h.get("story_text") or "")[:400],
                                h.get("author"), h.get("created_at"),
                                [f"points:{h.get('points')}", f"comments:{h.get('num_comments')}"],
                                "", "en"))
            time.sleep(0.25)
    return out


def _scrape_list(url: str, source: str, title_sel: str, link_pat: str,
                 lang: str, limit: int) -> list[dict]:
    """通用列表页抓取：正则提取文章链接+标题。"""
    try:
        html = _get(url, timeout=15).decode("utf-8", "ignore")
    except Exception:
        return []
    out = []
    seen = set()
    for m in re.finditer(link_pat, html):
        link = m.group(1)
        title = (m.group(2) if m.lastindex and m.lastindex >= 2 else "").strip()
        title = _strip_html(title)
        if link in seen or not title or len(title) < 6:
            continue
        seen.add(link)
        out.append(_rec(source, "html", link, title, link, "", "", "", [], "", lang))
        if len(out) >= limit:
            break
    return out


def deep_cnblogs() -> list[dict]:
    """博客园：编辑推荐 + 热门分类列表。"""
    out = []
    # 编辑推荐 pick 多页
    for p in range(1, 6):
        out += _scrape_list(f"https://www.cnblogs.com/pick/{p}", "博客园", "",
                            r'<a\s+class="post-item-title"\s+href="([^"]+)"[^>]*>([^<]+)</a>',
                            "zh", 30)
        time.sleep(0.2)
    # 几个热门分类
    for cid in [108698, 610, 108703]:   # 综合/编程语言/架构设计
        out += _scrape_list(f"https://www.cnblogs.com/cate/{cid}/", "博客园", "",
                            r'<a\s+class="post-item-title"\s+href="([^"]+)"[^>]*>([^<]+)</a>',
                            "zh", 25)
        time.sleep(0.2)
    # 去重
    seen, uniq = set(), []
    for r in out:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    return uniq


def deep_oschina() -> list[dict]:
    """开源中国：新闻列表多页。"""
    out = []
    for p in range(1, 6):
        out += _scrape_list(f"https://www.oschina.net/news?p={p}", "开源中国", "",
                            r'<a\s+href="(https://www\.oschina\.com/news/\d+[^"]+)"[^>]*\s+class="[^"]*"[^>]*>([^<]{6,})</a>',
                            "zh", 30)
        time.sleep(0.2)
    # 备用更宽松匹配
    if len(out) < 20:
        try:
            html = _get("https://www.oschina.net/news", timeout=15).decode("utf-8", "ignore")
            seen = {r["id"] for r in out}
            for m in re.finditer(r'href="(https://www\.oschina\.com/news/\d+/[^"]+)"[^>]*>([^<]{8,})</a>', html):
                if m.group(1) not in seen:
                    out.append(_rec("开源中国", "html", m.group(1),
                                    _strip_html(m.group(2)), m.group(1), "", "", "", [], "", "zh"))
                    seen.add(m.group(1))
        except Exception:
            pass
    seen, uniq = set(), []
    for r in out:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    return uniq


def fetch_full_for(items: list[dict], source: str, cap: int = 60) -> int:
    """对抓到的列表项补全文。"""
    got = 0
    for it in items[:cap]:
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
    return got


def main():
    SDIR.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("dev.to", deep_devto, False),
        ("HackerNews", deep_hackernews, False),
        ("博客园", deep_cnblogs, True),
        ("开源中国", deep_oschina, True),
    ]
    for name, fn, do_full in jobs:
        try:
            items = fn()
            if do_full:
                g = fetch_full_for(items, name, cap=50)
                print(f"  [{name}] 全文补 {g}")
            path = SDIR / f"{name}.jsonl"
            with path.open("w", encoding="utf-8") as f:
                for it in items:
                    f.write(json.dumps(it, ensure_ascii=False) + "\n")
            nfull = sum(1 for it in items if len(it.get("content", "")) > 200)
            print(f"  [{name}] 深采 {len(items)} 条（含正文 {nfull}）-> {path.name}")
        except Exception as e:
            print(f"  [{name}] ERR {e}")


if __name__ == "__main__":
    main()
