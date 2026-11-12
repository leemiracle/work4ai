"""重试 Crossref —— 补 algorithmic management / dynamic capabilities 两主题"""
import urllib.request, urllib.parse, json, time

def crossref(query, rows=6, retries=4):
    url = "https://api.crossref.org/works"
    params = urllib.parse.urlencode({"query": query, "rows": rows,
                                     "filter": "from-pub-date:2023"})
    for i in range(retries):
        try:
            req = urllib.request.Request(f"{url}?{params}", headers={
                "User-Agent": "research/1.0", "Accept": "application/json"})
            data = json.loads(urllib.request.urlopen(req, timeout=45).read())
            return data["message"]["items"]
        except Exception as e:
            print(f"   (retry {i+1}: {type(e).__name__})")
            time.sleep(3)
    return []

for q in ["algorithmic management worker autonomy fairness",
          "dynamic capabilities Teece sensing seizing reconfiguring",
          "remote hybrid work productivity",
          "platform ecosystem strategy governance"]:
    print("\n" + "=" * 72)
    print(q)
    print("=" * 72)
    items = crossref(q)
    if not items:
        print("  (网络超时, 跳过)")
        continue
    for it in items[:6]:
        t = (it.get("title") or ["(no title)"])[0]
        dp = it.get("published", {}).get("date-parts", [[None]])
        y = dp[0][0] if dp and dp[0] else "?"
        a = ", ".join(f'{x.get("given","")} {x.get("family","")}'.strip()
                      for x in it.get("author", [])[:3])
        v = (it.get("container-title") or [""])[0]
        doi = it.get("DOI", "")
        print(f"  [{y}] {t[:92]}")
        print(f"       {a} — {v}  (DOI: {doi})")
