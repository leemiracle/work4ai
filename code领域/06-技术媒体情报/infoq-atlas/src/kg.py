"""跨 topic 知识图谱：构建 topic-tag / topic-topic 共现 / author-topic 网络，
输出 dashboard/kg.json 供可视化，以及 reports/global/knowledge_graph.md。
"""
from __future__ import annotations
import json
import sqlite3
from collections import Counter, defaultdict
from . import config as C


def build():
    conn = sqlite3.connect(C.DB_PATH)
    # topic-topic 共现（基于同一篇文章出现的多个 topic）
    pairs = Counter()
    topic_deg = Counter()
    for (aid,) in conn.execute("SELECT DISTINCT aid FROM article_topics"):
        ts = [r[0] for r in conn.execute(
            "SELECT DISTINCT topic_id FROM article_topics WHERE aid=?", (aid,))]
        ts = sorted(set(ts))
        for i in range(len(ts)):
            topic_deg[ts[i]] += 1
            for j in range(i + 1, len(ts)):
                pairs[(ts[i], ts[j])] += 1

    tname = {r[0]: r[1] for r in conn.execute("SELECT id,name FROM topics")}
    nodes = [{"id": int(tid), "name": tname.get(int(tid), str(tid)),
              "weight": topic_deg[tid]} for tid in topic_deg]
    edges = [{"source": int(a), "target": int(b), "weight": w,
              "sname": tname.get(int(a), str(a)), "tname": tname.get(int(b), str(b))}
             for (a, b), w in pairs.most_common(200) if w >= 3]
    topic_topic = {"nodes": nodes, "edges": edges}

    # tag 频率
    labels = [{"label": l, "count": c} for l, c in conn.execute(
        "SELECT label, COUNT(*) c FROM article_labels GROUP BY label "
        "ORDER BY c DESC LIMIT 60") if l]

    # author-topic（高产作者在各 topic 分布）
    author_topic = defaultdict(list)
    author_cnt = Counter()
    for name, tid in conn.execute(
            "SELECT ap.name, at.topic_id FROM article_people ap "
            "JOIN article_topics at ON ap.aid=at.aid WHERE ap.role='author'"):
        author_topic[name].append(tid)
        author_cnt[name] += 1
    top_authors = [n for n, _ in author_cnt.most_common(20)]
    author_nodes = []
    for n in top_authors:
        tids = Counter(author_topic[n]).most_common(6)
        author_nodes.append({"author": n, "total": author_cnt[n],
                             "topics": [{"id": t, "name": tname.get(t, str(t)),
                                         "count": c} for t, c in tids]})

    conn.close()

    kg = {"topic_topic_graph": topic_topic, "top_labels": labels,
          "author_topic": author_nodes}
    out = C.DASHBOARD / "kg.json"
    out.write_text(json.dumps(kg, ensure_ascii=False, indent=2), encoding="utf-8")

    # markdown 摘要
    md = ["# 跨 Topic 知识图谱\n"]
    md.append("## Topic 共现网络（Top 关联）\n")
    md.append("| Topic A | Topic B | 共现文章数 |")
    md.append("|---------|---------|-----------|")
    for e in edges[:30]:
        md.append(f"| {e['sname']} | {e['tname']} | {e['weight']} |")
    md.append("\n## 高频标签 Top 40\n")
    md.append("| 标签 | 频次 |")
    md.append("|------|------|")
    for l in labels[:40]:
        md.append(f"| {l['label']} | {l['count']} |")
    md.append("\n## 高产作者 × Topic 偏好\n")
    for a in author_nodes:
        tline = ", ".join(f"{t['name']}({t['count']})" for t in a["topics"])
        md.append(f"- **{a['author']}**（{a['total']} 篇）→ {tline}")
    md.append("\n---\n*由 InfoQ Atlas 自动生成*\n")
    (C.REPORT_GLOBAL / "knowledge_graph.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[kg] nodes={len(nodes)} edges={len(edges)} labels={len(labels)} "
          f"authors={len(author_nodes)} -> {out}")
    return kg


if __name__ == "__main__":
    build()
