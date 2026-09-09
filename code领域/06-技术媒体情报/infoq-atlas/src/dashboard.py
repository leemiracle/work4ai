"""构建静态 HTML 仪表盘（ECharts）。数据内联，避免 f-string 花括号冲突：
先把所有 JS 数据对象用 Python json.dumps 预计算成字符串常量，再注入。
"""
from __future__ import annotations
import json
from . import config as C


def build():
    g = json.loads((C.PROCESSED / "stats_global.json").read_text(encoding="utf-8"))
    kg = {}
    p = C.DASHBOARD / "kg.json"
    if p.exists():
        kg = json.loads(p.read_text(encoding="utf-8"))

    # ---- 预计算 ECharts option（纯 Python dict）----
    pt = sorted(g["per_topic"], key=lambda z: z["count"], reverse=True)
    opt_topic_bar = {
        "tooltip": {"trigger": "axis"}, "grid": {"left": 90, "right": 30, "top": 20},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category",
                  "data": [x["name"] for x in pt]},
        "series": [{"type": "bar", "data": [x["count"] for x in pt],
                    "itemStyle": {"color": "#4ea1d3"}}],
    }
    by = g["by_year"]
    yrs = sorted(by.keys(), key=lambda x: str(x))
    opt_year = {
        "tooltip": {"trigger": "axis"}, "grid": {"left": 50, "right": 20, "top": 20},
        "xAxis": {"type": "category", "data": [str(y) for y in yrs]},
        "yAxis": {"type": "value"},
        "series": [{"type": "line", "smooth": True,
                    "data": [by[y] for y in yrs],
                    "areaStyle": {"opacity": 0.3},
                    "itemStyle": {"color": "#7ee787"}}],
    }
    lb = g["top_labels"][:25][::-1]
    opt_label = {
        "grid": {"left": 100, "right": 30, "top": 20},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": [x["label"] for x in lb]},
        "series": [{"type": "bar", "data": [x["count"] for x in lb],
                    "itemStyle": {"color": "#f0a868"}}],
    }
    au = g["top_authors"][:20][::-1]
    opt_author = {
        "grid": {"left": 110, "right": 30, "top": 20},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": [x["name"] for x in au]},
        "series": [{"type": "bar", "data": [x["count"] for x in au],
                    "itemStyle": {"color": "#d2a8ff"}}],
    }
    opt_graph = {}
    tt = kg.get("topic_topic_graph", {})
    if tt.get("nodes"):
        opt_graph = {
            "tooltip": {},
            "series": [{"type": "graph", "layout": "force", "roam": True,
                "force": {"repulsion": 220, "edgeLength": [40, 130]},
                "label": {"show": True, "color": "#e6e6e6", "fontSize": 11},
                "data": [{"name": n["name"], "value": n["weight"],
                          "symbolSize": 10 + n["weight"] / 250}
                         for n in tt["nodes"]],
                "links": [{"source": e["sname"], "target": e["tname"],
                           "value": e["weight"]} for e in tt["edges"][:90]],
                "lineStyle": {"color": "#3a4a5d", "curvature": 0.1}}],
        }
    # 知识图谱（概念关系，来自全量三元组）
    opt_concept = {}
    cg_path = C.DASHBOARD / "concept_graph.json"
    if cg_path.exists():
        cg = json.loads(cg_path.read_text(encoding="utf-8"))
        cnodes = cg.get("nodes", [])[:80]
        cset = set(cnodes)
        clinks = [{"source": e["s"], "target": e["t"], "value": e["w"]}
                  for e in cg.get("edges", [])
                  if e["s"] in cset and e["t"] in cset][:140]
        opt_concept = {
            "tooltip": {},
            "series": [{"type": "graph", "layout": "force", "roam": True,
                "force": {"repulsion": 120, "edgeLength": [30, 90]},
                "label": {"show": True, "color": "#ffd6a8", "fontSize": 10},
                "data": [{"name": n, "symbolSize": 14} for n in cnodes],
                "links": clinks,
                "lineStyle": {"color": "#5a4a3d", "curvature": 0.1},
                "itemStyle": {"color": "#f0a868"}}],
        }

    # 阅读量表格
    tv = g["top_viewed_all"][:20]
    rows = "".join(
        f"<tr><td>{i+1}</td><td>{a['title'][:42]}</td><td>{a['year']}</td>"
        f"<td>{a['views']:,}</td></tr>" for i, a in enumerate(tv))

    def opt(o):
        return json.dumps(o, ensure_ascii=False)

    cards = []
    cards.append(('c1', '各 Topic 文章分布', 'full', opt(opt_topic_bar)))
    cards.append(('c2', '全站年度发文趋势', '', opt(opt_year)))
    cards.append(('c3', '高频标签 Top25', 'tall', opt(opt_label)))
    cards.append(('c4', '高产作者 Top20', 'tall', opt(opt_author)))
    if opt_graph:
        cards.append(('c5', 'Topic 共现网络', 'full tall', opt(opt_graph)))
    if opt_concept:
        cards.append(('c6', '知识概念关系图（全量三元组）', 'full tall', opt(opt_concept)))

    grid_html = ""
    for cid, title, cls, optjson in cards:
        tall = "tall" in cls
        grid_html += (f'<div class="card {cls}"><h3>{title}</h3>'
                      f'<div id="{cid}" class="chart {"tall" if tall else ""}"></div></div>\n')
    grid_html += (f'<div class="card full"><h3>全站阅读量 Top20</h3>'
                  f'<table><tr><th>#</th><th>标题</th><th>年</th>'
                  f'<th>阅读</th></tr>{rows}</table></div>')

    init_js = "\n".join(
        f'echarts.init(document.getElementById("{cid}")).setOption({optjson});'
        for cid, _, _, optjson in cards)

    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>InfoQ Atlas · 全景仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#0f1419;color:#e6e6e6}}
h1{{margin:0;padding:24px 32px 8px;font-size:24px;background:linear-gradient(90deg,#1b2735,#2a4a6b)}}
.sub{{padding:0 32px 16px;color:#8aa0b6;font-size:13px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:16px 32px 40px}}
.card{{background:#1a2029;border:1px solid #2a3340;border-radius:10px;padding:16px}}
.card h3{{margin:0 0 8px;font-size:15px;color:#9fb3c8}}
.full{{grid-column:1/3}}
.chart{{width:100%;height:320px}}.tall{{height:440px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td,th{{padding:5px 8px;text-align:left;border-bottom:1px solid #243040}}
th{{color:#9fb3c8}}tr:hover{{background:#222b36}}
</style></head><body>
<h1>📊 InfoQ Atlas 全景仪表盘</h1>
<div class="sub">总文章 {g['total_articles']:,} · 含全文 {g['with_full_text']:,} · Topic 数 {len(g['per_topic'])} · 跨 topic 关联 200,656</div>
<div class="grid">{grid_html}</div>
<script>window.addEventListener('load',function(){{{init_js}}});</script>
</body></html>"""
    out = C.DASHBOARD / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"[dashboard] -> {out}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    build()
