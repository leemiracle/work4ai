# Neo4j 图谱导入

节点: Concept(36683) / Article(25801) / Topic(88)
关系: 概念语义三元组 / Article-IN_TOPIC-Topic(200,656)

## 方式1：neo4j-admin 批量导入（最快，新建库）

```bash
# 把 nodes_*.csv rels_*.csv 放到 Neo4j import 目录，然后:
neo4j-admin database import full infoqkg \
  --nodes=Concept=nodes_concept.csv \
  --nodes=Article=nodes_article.csv \
  --nodes=Topic=nodes_topic.csv \
  --relationships=rels_concept.csv \
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
