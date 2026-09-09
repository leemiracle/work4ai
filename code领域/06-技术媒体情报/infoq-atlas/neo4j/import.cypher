// InfoQ Atlas 知识图谱 - Neo4j 导入
// 方式1（推荐）: 用 neo4j-admin database import full 批量导入 CSV（见 README.md）
// 方式2: 浏览器粘贴下面 LOAD CSV 语句

// 概念节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_concept.csv' AS row
MERGE (c:Concept {id: row[':ID']}) SET c.name = row.name;

// 概念关系
LOAD CSV WITH HEADERS FROM 'file:///rels_concept.csv' AS row
MATCH (a:Concept {id: row[':START_ID']}), (b:Concept {id: row[':END_ID']})
MERGE (a)-[r:REL {type: row.relation}]->(b);

// 文章-主题
LOAD CSV WITH HEADERS FROM 'file:///nodes_topic.csv' AS row
MERGE (t:Topic {id: row[':ID']}) SET t.name = row.name;
LOAD CSV WITH HEADERS FROM 'file:///nodes_article.csv' AS row
MERGE (a:Article {id: row[':ID']}) SET a.aid = row.aid, a.title = row.title;
LOAD CSV WITH HEADERS FROM 'file:///rels_article_topic.csv' AS row
MATCH (a:Article {id: row[':START_ID']}), (t:Topic {id: row[':END_ID']})
MERGE (a)-[:IN_TOPIC]->(t);

// 探索查询示例:
// MATCH (c:Concept)-[r:REL]->(d) WHERE c.name CONTAINS 'Agent' RETURN c,r,d LIMIT 50;
// MATCH (c:Concept)-[r:REL]->(d) RETURN c,r,d LIMIT 300;
