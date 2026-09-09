"""#1 主题聚类与演化：复用 content_intel.json + #3 知识三元组（不重扫全文）。

产出每 topic 的 THEMES 报告 + 全局概念演化图：
- 主题演化时间线：各年热门实体（rise/fall 判断）
- 命名子主题簇（来自关键短语聚合）
- 概念关系图：从 #3 三元组 + 各 topic 实体构建跨 topic 概念网络
"""
from __future__ import annotations
import json
import sqlite3
from collections import Counter, defaultdict
from . import config as C


def load_content():
    return json.loads((C.PROCESSED / "content_intel.json").read_text("utf-8"))


def detect_trend(evolution: dict) -> dict:
    """根据各年提及次数判断实体是 上升/稳定/下降/新起。"""
    years = sorted(int(y) for y in evolution.keys() if str(y).isdigit())
    if len(years) < 2:
        return {}
    # 取近 3 年 vs 更早
    recent = years[-3:]
    earlier = [y for y in years if y not in recent]
    ent_recent = Counter()
    ent_earlier = Counter()
    for y in recent:
        for n, c in evolution.get(str(y), evolution.get(y, [])):
            ent_recent[n] += c
    for y in earlier:
        for n, c in evolution.get(str(y), evolution.get(y, [])):
            ent_earlier[n] += c
    trend = {}
    for n, rc in ent_recent.most_common(30):
        ec = ent_earlier.get(n, 0)
        if ec == 0 and rc >= 2:
            trend[n] = "🆕新起"
        elif rc > ec * 2 and rc >= 3:
            trend[n] = "📈上升"
        elif rc >= 3 and ec > rc * 2:
            trend[n] = "📉下降"
        elif rc >= 3:
            trend[n] = "➡️稳定"
    return trend


def _safe(name):
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name


def render_topic_themes(t: dict) -> str:
    L = [f"# {t['name']} · 主题聚类与演化\n",
         f"> 复用内容情报层结果 + 大模型知识抽取 · 全文 {t['n_fulltext']} 篇\n"]
    # 演化
    ev = t.get("concept_evolution", {})
    trend = detect_trend(ev)
    L.append("## 1. 概念演化时间线（各年热门技术）\n")
    for y in sorted(ev, key=lambda x: str(x))[-8:]:
        line = " · ".join(f"{n}({c})" for n, c in ev[y][:6])
        L.append(f"- **{y}**：{line}")
    L.append("")
    if trend:
        L.append("## 2. 趋势判断（基于年度提及变化）\n")
        for n, tr in sorted(trend.items(), key=lambda x: x[1]):
            L.append(f"- {tr} **{n}**")
        L.append("")
    # 子主题簇
    L.append("## 3. 命名子主题簇（关键短语聚合）\n")
    for st in t.get("subthemes", [])[:10]:
        L.append(f"- **{st['theme']}**（权重 {st['weight']}，约 {st['n_articles']} 篇）")
    L.append("")
    # 头部实体
    L.append("## 4. 该 Topic 的核心技术栈\n")
    for cat, items in sorted(t.get("top_entities_by_cat", {}).items(),
                             key=lambda x: -sum(c for _, c in x[1]))[:5]:
        L.append(f"- **{cat}**：" + " · ".join(f"{n}({c})" for n, c in items[:8]))
    L.append("\n---\n*复用 content_intel + 知识抽取*\n")
    return "\n".join(L)


def concept_graph(conn) -> dict:
    """从 #3 三元组 + 各 topic 头部实体构建跨 topic 概念关系。"""
    # 三元组里的实体对作为边
    edges = Counter()
    nodes = set()
    for s, p, o in conn.execute("SELECT subject,predicate,object FROM knowledge_triples"):
        nodes.add(s); nodes.add(o)
        edges[(s, o)] += 1
    # 加入各 topic 头部实体（按 topic 内共现连边）
    content = load_content()
    for t in content["topic_digests"]:
        ents = []
        for cat, items in t.get("top_entities_by_cat", {}).items():
            for n, _ in items[:3]:
                ents.append(n)
        for i in range(len(ents)):
            for j in range(i + 1, len(ents)):
                edges[(ents[i], ents[j])] += 1
                nodes.add(ents[i]); nodes.add(ents[j])
    return {"nodes": list(nodes),
            "edges": [{"s": s, "t": t, "w": w}
                      for (s, t), w in edges.most_common(120) if w >= 1][:120]}


def render_global_themes(content, trend_all, g) -> str:
    L = ["# InfoQ 全局 · 主题演化与概念图谱\n",
         "> 复用内容情报层 + 大模型知识三元组（#3）\n"]
    L.append("## 1. 各 Topic 主题趋势速览\n")
    L.append("| Topic | 上升概念 | 新起概念 |")
    L.append("|-------|---------|---------|")
    for t in content["topic_digests"]:
        tr = detect_trend(t.get("concept_evolution", {}))
        up = ", ".join(n for n, x in tr.items() if "上升" in x)[:60]
        new = ", ".join(n for n, x in tr.items() if "新起" in x)[:60]
        L.append(f"| {t['name']} | {up or '-'} | {new or '-'} |")
    L.append("")
    # 全局上升/新起
    rise = Counter()
    newc = Counter()
    for t in content["topic_digests"]:
        for n, x in detect_trend(t.get("concept_evolution", {})).items():
            if "上升" in x:
                rise[n] += 1
            if "新起" in x:
                newc[n] += 1
    L.append("## 2. 🔥 全站上升 / 新起技术（跨多个 topic 出现）\n")
    L.append("**上升中**（在多个 topic 同步走高）：" +
             " · ".join(f"{n}({c}topic)" for n, c in rise.most_common(15)) + "\n")
    L.append("**新起**（近年才涌现）：" +
             " · ".join(f"{n}({c}topic)" for n, c in newc.most_common(15)) + "\n")
    # 概念图谱
    L.append("## 3. 跨 Topic 概念关系图（融合 #3 知识三元组）\n")
    L.append(f"共 {len(g['nodes'])} 概念节点、{len(g['edges'])} 关系边。Top 关系：\n")
    L.append("| 概念A | — | 概念B | 强度 |")
    L.append("|-------|---|-------|------|")
    for e in g["edges"][:25]:
        L.append(f"| {e['s']} | — | {e['t']} | {e['w']} |")
    L.append("\n---\n*复用 content_intel + knowledge_triples 生成*\n")
    return "\n".join(L)


def main():
    content = load_content()
    conn = sqlite3.connect(C.DB_PATH)
    for t in content["topic_digests"]:
        md = render_topic_themes(t)
        (C.REPORT_TOPICS / f"{t['topic_id']}_{_safe(t['name'])}_THEMES.md").write_text(md, encoding="utf-8")
    g = concept_graph(conn)
    (C.DASHBOARD / "concept_graph.json").write_text(json.dumps(g, ensure_ascii=False), encoding="utf-8")
    trend_all = {}
    gmd = render_global_themes(content, trend_all, g)
    (C.REPORT_GLOBAL / "THEMES_EVOLUTION.md").write_text(gmd, encoding="utf-8")
    conn.close()
    print(f"[cluster_evolve] {len(content['topic_digests'])} topic THEMES + 全局演化 + "
          f"概念图({len(g['nodes'])}节点/{len(g['edges'])}边)")


if __name__ == "__main__":
    main()
