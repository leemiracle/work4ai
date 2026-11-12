"""
论文检索 —— 直接调用 arXiv + Crossref 公开 API (绕过受限的 firecrawl)
验证 2023-2026 管理学前沿文献是否可达, 并抓取真实标题/作者/年份/摘要。
"""
import urllib.request, urllib.parse, json
import xml.etree.ElementTree as ET

UA = {"User-Agent": "research-bot/1.0 (mailto:none@example.com)", "Accept": "application/json"}


def arxiv_search(query, max_results=6):
    url = "http://export.arxiv.org/api/query"
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}", "start": 0, "max_results": max_results,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    req = urllib.request.Request(f"{url}?{params}", headers=UA)
    try:
        data = urllib.request.urlopen(req, timeout=30).read().decode()
        root = ET.fromstring(data)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        out = []
        for e in root.findall("a:entry", ns):
            title = " ".join(e.find("a:title", ns).text.split())
            date = e.find("a:published", ns).text[:10]
            summ = " ".join(e.find("a:summary", ns).text.split())[:280]
            authors = [a.find("a:name", ns).text for a in e.findall("a:author", ns)][:3]
            out.append((date, title, ", ".join(authors), summ, e.find("a:id", ns).text))
        return out
    except Exception as ex:
        return [("ERR", str(ex), "", "", "")]


def crossref_search(query, rows=6):
    url = "https://api.crossref.org/works"
    params = urllib.parse.urlencode({"query": query, "rows": rows,
                                     "filter": "from-pub-date:2023"})
    req = urllib.request.Request(f"{url}?{params}", headers=UA)
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        out = []
        for it in data["message"]["items"][:rows]:
            title = (it.get("title") or ["(no title)"])[0]
            dp = it.get("published", {}).get("date-parts", [[None]])
            yr = dp[0][0] if dp and dp[0] else "?"
            authors = [f'{a.get("given", "")} {a.get("family", "")}'.strip()
                       for a in it.get("author", [])][:3]
            venue = (it.get("container-title") or [""])[0]
            out.append((yr, title, ", ".join(authors), venue, it.get("DOI", "")))
        return out
    except Exception as ex:
        return [("ERR", str(ex), "", "", "")]


queries = [
    ("algorithmic management worker", "algorithmic management worker"),
    ("dynamic capabilities Teece", "dynamic capabilities Teece"),
    ("bullwhip effect supply chain", "bullwhip effect supply chain"),
    ("Vickrey auction mechanism design", "Vickrey auction mechanism design"),
]

for human, q in queries:
    print("\n" + "#" * 72)
    print(f"# 主题: {human}")
    print("#" * 72)
    print("\n--- arXiv (最新, 按提交日期倒序) ---")
    for d, t, a, s, link in arxiv_search(q):
        print(f"  [{d}] {t}")
        print(f"    {a}")
        if s and s != "ERR":
            print(f"    {s}...")
        print(f"    {link}")
    print("\n--- Crossref (期刊/会议, 2023+) ---")
    for y, t, a, v, doi in crossref_search(q):
        print(f"  [{y}] {t}")
        print(f"    {a} — {v}  (DOI: {doi})")
