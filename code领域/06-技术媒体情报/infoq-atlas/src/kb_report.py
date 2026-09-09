"""知识库报告 + 三元组入库（消费 knowledge_all.jsonl，含全量自动+精抽）。

820 条全量入库；报告：精抽5条详列 + 全量聚合统计（概念/关系 Top）。
"""
from __future__ import annotations
import json
import sqlite3
from collections import Counter
from . import config as C


def load_kb():
    # 优先 GLM-5.1 高质量层；出错/缺失的用自动层补齐
    llm_path = C.PROCESSED / "knowledge_llm.jsonl"
    auto_path = C.PROCESSED / "knowledge_all.jsonl"
    primary = []
    if llm_path.exists():
        for line in llm_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if e.get("triples") and not e.get("error"):
                        primary.append(e)
                except json.JSONDecodeError:
                    continue
    fallback = []
    # 目录 NLP 层（覆盖 GLM 未处理的全部文章）
    cat_path = C.PROCESSED / "knowledge_catalog.jsonl"
    if cat_path.exists():
        llm_aids = {e.get("aid") or e.get("id") for e in primary}
        for line in cat_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("aid") in llm_aids or e.get("id") in llm_aids:
                continue
            fallback.append(e)
    # 经典站 GLM 知识
    sites = []
    sites_path = C.PROCESSED / "knowledge_sites.jsonl"
    if sites_path.exists():
        for line in sites_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if e.get("triples") and not e.get("error"):
                        sites.append(e)
                except json.JSONDecodeError:
                    continue
    return primary + sites + fallback


def main():
    kb = load_kb()
    curated = [e for e in kb if not e.get("auto")]
    conn = sqlite3.connect(C.DB_PATH)
    conn.executescript("""
    DROP TABLE IF EXISTS knowledge_triples;
    CREATE TABLE knowledge_triples(id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT, predicate TEXT, object TEXT, source TEXT);
    DROP TABLE IF EXISTS knowledge_concepts;
    CREATE TABLE knowledge_concepts(concept TEXT PRIMARY KEY, count INTEGER);
    """)
    ccount = {}
    pred_c = Counter()
    for e in kb:
        for s, p_, o in e.get("triples", []):
            conn.execute("INSERT INTO knowledge_triples(subject,predicate,object,source) VALUES(?,?,?,?)",
                         (s, p_, o, e["id"]))
            pred_c[p_] += 1
        for c in e.get("concepts", []):
            ccount[c] = ccount.get(c, 0) + 1
    for c, n in ccount.items():
        conn.execute("INSERT OR REPLACE INTO knowledge_concepts VALUES(?,?)", (c, n))
    conn.commit()
    n_triples = conn.execute("SELECT COUNT(*) FROM knowledge_triples").fetchone()[0]
    n_concepts = conn.execute("SELECT COUNT(*) FROM knowledge_concepts").fetchone()[0]
    top_concepts = conn.execute(
        "SELECT concept,count FROM knowledge_concepts ORDER BY count DESC LIMIT 30").fetchall()
    # 涉及技术 Top（object 维度）
    top_tech = conn.execute(
        "SELECT object, COUNT(*) c FROM knowledge_triples WHERE predicate LIKE '涉及%' "
        "GROUP BY object ORDER BY c DESC LIMIT 25").fetchall()
    conn.close()

    # 报告
    L = ["# InfoQ Atlas · 知识库（大模型抽取 + 全量结构化）\n",
         f"> **{len(kb)}** 知识条目（{len(curated)} 篇大模型精抽 + {len(kb)-len(curured if False else curated)} 自动）"
         f" · **{n_triples}** 三元组 · **{n_concepts}** 概念\n"]

    L.append("## 一、全量知识聚合\n")
    L.append(f"- 知识条目：**{len(kb)}**（覆盖 {len([e for e in kb if e.get('source','').startswith('InfoQ')])} 篇 InfoQ 全文）")
    L.append(f"- 三元组：**{n_triples:,}**")
    L.append(f"- 概念：**{n_concepts}**\n")

    L.append("### Top 30 核心概念\n")
    L.append("| 概念 | 出现条目数 |")
    L.append("|------|-----------|")
    for c, n in top_concepts:
        L.append(f"| {c} | {n} |")
    L.append("")

    L.append("### Top 25 涉及技术（跨全文）\n")
    L.append("| 技术 | 涉及文章数 |")
    L.append("|------|-----------|")
    for o, c in top_tech:
        L.append(f"| {o} | {c} |")
    L.append("")

    L.append("### 关系类型分布\n")
    L.append("| 关系 | 三元组数 |")
    L.append("|------|----------|")
    for p_, c in pred_c.most_common(12):
        L.append(f"| {p_} | {c} |")
    L.append("")

    L.append("## 二、大模型精抽（高价值全文深度知识）\n")
    for e in curated:
        L.append(f"### {e['title']}")
        L.append(f"*领域：{e.get('domain','-')} · 来源：{e.get('source','-')}*\n")
        L.append(f"**摘要**：{e['summary']}\n")
        L.append("**核心概念**：" + " · ".join(f"`{c}`" for c in e.get("concepts", [])[:12]) + "\n")
        L.append("| 主体 | 关系 | 客体 |")
        L.append("|------|------|------|")
        for s, p_, o in e.get("triples", []):
            L.append(f"| {s} | {p_} | {o} |")
        L.append("")

    L.append("## 三、检索示例\n")
    L.append("```python\nimport sqlite3\nconn=sqlite3.connect('data/processed/infoq.db')\n"
             "# 查某技术的所有关联\nfor r in conn.execute(\n"
             "  \"SELECT subject,predicate,object FROM knowledge_triples WHERE object LIKE '%DeepSeek%' LIMIT 20\"):\n"
             "  print(r)\n```\n")
    L.append("---\n*大模型精抽 + 全量 NLP 结构化抽取*\n")
    (C.REPORT_GLOBAL / "KNOWLEDGE_BASE.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[kb_report] {len(kb)} 条目(精抽{len(curated)}), {n_triples} 三元组, "
          f"{n_concepts} 概念 -> KNOWLEDGE_BASE.md + DB")


if __name__ == "__main__":
    main()
