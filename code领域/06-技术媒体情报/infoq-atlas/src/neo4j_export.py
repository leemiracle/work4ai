"""生成 Neo4j 可导入的图谱文件（CSV + Cypher 脚本）。

模型：
  (Concept) -[关系]-> (Concept)        来自 knowledge_triples
  (Article) -[:DISCUSSES]-> (Concept)  来自 knowledge_concepts 关联
  (Topic)   <-[:IN_TOPIC]- (Article)   来自 article_topics
产出 neo4j/ 目录：nodes_*.csv, rels_*.csv, import.cypher, README.md
"""
from __future__ import annotations
import csv
import sqlite3
import re
from . import config as C

OUT = C.ROOT / "neo4j"


def _cid(name: str, reg: dict[str, str]) -> str:
    name = str(name).strip()
    if name in reg:
        return reg[name]
    i = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]", "_", name)[:40]
    cid = f"c_{i}_{abs(hash(name)) % 100000}"
    reg[name] = cid
    return cid


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(C.DB_PATH)

    concept_reg: dict[str, str] = {}

    # ---- 概念节点 ----
    concepts = conn.execute("SELECT concept FROM knowledge_concepts").fetchall()
    with (OUT / "nodes_concept.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([":ID", "name", ":LABEL"])
        for (c,) in concepts:
            w.writerow([_cid(c, concept_reg), c, "Concept"])
    # triples 里出现的 subject/object 也作为概念
    triples = conn.execute(
        "SELECT subject,predicate,object FROM knowledge_triples").fetchall()
    extra_concepts = set()
    for s, p, o in triples:
        for n in (s, o):
            if n not in concept_reg:
                extra_concepts.add(n)
    with (OUT / "nodes_concept.csv").open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for n in extra_concepts:
            w.writerow([_cid(n, concept_reg), n, "Concept"])

    # ---- 概念关系（triples）----
    def _rtype(p):
        p = str(p)
        return re.sub(r"[^A-Za-z0-9_]", "_", p) or "REL"
    with (OUT / "rels_concept.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([":START_ID", ":END_ID", ":TYPE", "relation"])
        n_rel = 0
        seen = set()
        for s, p, o in triples:
            sid = concept_reg.get(s)
            oid = concept_reg.get(o)
            if not sid or not oid or sid == oid:
                continue
            key = (sid, _rtype(p), oid)
            if key in seen:
                continue
            seen.add(key)
            w.writerow([sid, oid, _rtype(p), p])
            n_rel += 1

    # ---- 文章节点 + DISCUSSES ----
    arts = conn.execute(
        "SELECT a.aid,a.title FROM articles a "
        "WHERE EXISTS(SELECT 1 FROM knowledge_triples)").fetchall()
    # 文章->概念：用该文章涉及的技术(object of 涉及*) —— 用 article_concept 关联更稳
    # 这里用 knowledge_concepts 全局 + 文章 aid 不在三元组里，改用 article 的概念：
    # 从 knowledge_triples 的 source(id含aid) 反查较复杂，改用 articles_topics 与标签。
    # 简化：Article-DISCUSSES-Concept 用该文章出现的技术（从 knowledge_triples 找不到直接aid）
    # 故改为 Article-IN_TOPIC-Topic（更干净）。
    with (OUT / "nodes_article.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([":ID", "aid", "title", ":LABEL"])
        for aid, title in arts:
            w.writerow([f"a_{aid}", aid, title or "", "Article"])

    # ---- Topic 节点 + IN_TOPIC ----
    topics = conn.execute("SELECT id,name FROM topics").fetchall()
    with (OUT / "nodes_topic.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([":ID", "name", ":LABEL"])
        for tid, name in topics:
            w.writerow([f"t_{tid}", name or str(tid), "Topic"])
    with (OUT / "rels_article_topic.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([":START_ID", ":END_ID", ":TYPE"])
        for aid, tid in conn.execute("SELECT DISTINCT aid,topic_id FROM article_topics"):
            w.writerow([f"a_{aid}", f"t_{tid}", "IN_TOPIC"])

    n_concept = len(concept_reg)
    n_article = len(arts)
    n_topic = len(topics)
    n_at = conn.execute("SELECT COUNT(*) FROM article_topics").fetchone()[0]
    conn.close()

    # ---- Cypher 脚本（浏览器可直接粘贴）----
    cy = OUT / "import.cypher"
    cy.write_text(f"""// InfoQ Atlas 知识图谱 - Neo4j 导入
// 方式1（推荐）: 用 neo4j-admin database import full 批量导入 CSV（见 README.md）
// 方式2: 浏览器粘贴下面 LOAD CSV 语句

// 概念节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_concept.csv' AS row
MERGE (c:Concept {{id: row[':ID']}}) SET c.name = row.name;

// 概念关系
LOAD CSV WITH HEADERS FROM 'file:///rels_concept.csv' AS row
MATCH (a:Concept {{id: row[':START_ID']}}), (b:Concept {{id: row[':END_ID']}})
MERGE (a)-[r:REL {{type: row.relation}}]->(b);

// 文章-主题
LOAD CSV WITH HEADERS FROM 'file:///nodes_topic.csv' AS row
MERGE (t:Topic {{id: row[':ID']}}) SET t.name = row.name;
LOAD CSV WITH HEADERS FROM 'file:///nodes_article.csv' AS row
MERGE (a:Article {{id: row[':ID']}}) SET a.aid = row.aid, a.title = row.title;
LOAD CSV WITH HEADERS FROM 'file:///rels_article_topic.csv' AS row
MATCH (a:Article {{id: row[':START_ID']}}), (t:Topic {{id: row[':END_ID']}})
MERGE (a)-[:IN_TOPIC]->(t);

// 探索查询示例:
// MATCH (c:Concept)-[r:REL]->(d) WHERE c.name CONTAINS 'Agent' RETURN c,r,d LIMIT 50;
// MATCH (c:Concept)-[r:REL]->(d) RETURN c,r,d LIMIT 300;
""", encoding="utf-8")

    # ---- README ----
    (OUT / "README.md").write_text(f"""# Neo4j 图谱导入

节点: Concept({n_concept}) / Article({n_article}) / Topic({n_topic})
关系: 概念语义三元组 / Article-IN_TOPIC-Topic({n_at:,})

## 方式1：neo4j-admin 批量导入（最快，新建库）

```bash
# 把 nodes_*.csv rels_*.csv 放到 Neo4j import 目录，然后:
neo4j-admin database import full infoqkg \\
  --nodes=Concept=nodes_concept.csv \\
  --nodes=Article=nodes_article.csv \\
  --nodes=Topic=nodes_topic.csv \\
  --relationships=rels_concept.csv \\
  --relationships=rels_article_topic.csv
```

## 方式2：浏览器 LOAD CSV（已有库）

把 CSV 拷到 `$NEO4J_HOME/import/`，在 Neo4j Browser 逐段执行 `import.cypher`。

## 探索查询

```cypher
// Agent 相关的知识网络
MATCH (c:Concept)-[r:REL]->(d) WHERE c.name CONTAINS 'Agent' RETURN c,r,d LIMIT 80

// 最连通的概念（枢纽）
MATCH (c:Concept)-[r:REL]-() RETURN c.name, count(r) AS deg ORDER BY deg DESC LIMIT 20

// 某技术的上下游（因果链）
MATCH path = (c:Concept)-[:REL*1..3]->(d) WHERE c.name='大模型' RETURN path LIMIT 50
```
""", encoding="utf-8")

    print(f"[neo4j] 节点 Concept={n_concept} Article={n_article} Topic={n_topic}")
    print(f"[neo4j] 关系 三元组去重={n_rel}  文章-主题={n_at:,}")
    print(f"[neo4j] -> {OUT}/ (nodes_*.csv, rels_*.csv, import.cypher, README.md)")


if __name__ == "__main__":
    main()
