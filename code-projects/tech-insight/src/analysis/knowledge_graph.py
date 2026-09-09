"""知识图谱构建器 - 从文章中提取实体、关系，构建技术领域知识图谱"""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from ..storage.database import get_cursor, get_analysis_cache, save_analysis_cache
from ..storage.models import Article, Entity, Relation
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = """你是一位资深技术分析师，擅长从技术文章中提取结构化的知识图谱。
你需要识别技术领域的关键实体和它们之间的关系，输出严格的 JSON。"""

_EXTRACT_PROMPT = """分析以下技术文章，提取知识图谱实体和关系。

文章标题: {title}
文章内容: {content}

请提取：
1. 实体(entities): 文章中提到的关键技术概念
   每个实体包含: name(名称), type(类型), description(简短描述)
   类型范围: 技术、公司、人物、产品、概念、框架、语言、事件

2. 关系(relations): 实体之间的关系
   每个关系包含: source(源实体名), target(目标实体名), type(关系类型), confidence(0-1)
   关系类型: 使用、开发、竞争、依赖、属于、影响、替代、集成

请返回 JSON:
{{
  "entities": [
    {{"name": "...", "type": "...", "description": "..."}}
  ],
  "relations": [
    {{"source": "...", "target": "...", "type": "...", "confidence": 0.9}}
  ]
}}"""


class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self):
        self.llm = LLMClient()
        cfg = _get_analysis_cfg()
        self.entity_types = cfg["knowledge_graph"]["entity_types"]
        self.relation_types = cfg["knowledge_graph"]["relation_types"]
        self.min_confidence = cfg["knowledge_graph"]["min_confidence"]
        self.top_entities = cfg["knowledge_graph"]["top_entities"]
        self._entity_index: Counter = Counter()

    def build_from_articles(self, articles: list[dict]) -> dict:
        """从文章列表构建知识图谱"""
        all_entities: dict[str, Entity] = {}
        all_relations: list[Relation] = []
        processed = 0

        for article in articles:
            content = article.get("content", "")[:800]
            if len(content) < 50:
                continue
            result = self._extract_from_article(article["title"], content)
            if not result:
                continue
            article_id = article.get("id", article.get("url", ""))
            for ent_data in result.get("entities", []):
                name = ent_data.get("name", "").strip()
                if not name:
                    continue
                etype = ent_data.get("type", "概念")
                if name not in all_entities:
                    all_entities[name] = Entity(
                        name=name,
                        entity_type=etype,
                        description=ent_data.get("description", ""),
                        source_articles=[article_id],
                    )
                else:
                    all_entities[name].mentions += 1
                    all_entities[name].source_articles.append(article_id)
                self._entity_index[name] += 1

            for rel_data in result.get("relations", []):
                conf = rel_data.get("confidence", 0.8)
                if conf < self.min_confidence:
                    continue
                all_relations.append(Relation(
                    source_entity=rel_data.get("source", ""),
                    target_entity=rel_data.get("target", ""),
                    relation_type=rel_data.get("type", "关联"),
                    confidence=conf,
                    source_articles=[article_id],
                ))
            processed += 1

        logger.info(f"知识图谱提取完成: {processed} 篇文章, "
                     f"{len(all_entities)} 实体, {len(all_relations)} 关系")

        graph = self._build_graph(all_entities, all_relations)
        self._save_to_db(all_entities, all_relations)
        return graph

    def _extract_from_article(self, title: str, content: str) -> dict:
        """用 LLM 从单篇文章提取知识图谱"""
        if not self.llm._available():
            return self._keyword_fallback(title, content)
        prompt = _EXTRACT_PROMPT.format(title=title, content=content)
        result = self.llm.chat_json(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
        )
        return result if isinstance(result, dict) else {}

    def _keyword_fallback(self, title: str, content: str) -> dict:
        """无 LLM 时使用关键词频率作为 fallback"""
        import re
        tech_keywords = [
            "大模型", "GPT", "LLM", "RAG", "Agent", "微服务", "Kubernetes", "Docker",
            "React", "Vue", "Python", "Java", "Go", "Rust", "TypeScript",
            "TensorFlow", "PyTorch", "Transformer", "向量数据库", "RAG",
            "Serverless", "云原生", "DevOps", "CI/CD", "微前端",
            "Kafka", "Redis", "MySQL", "PostgreSQL", "MongoDB",
        ]
        found = {}
        for kw in tech_keywords:
            count = content.count(kw) + title.count(kw)
            if count > 0:
                found[kw] = count
        entities = [
            {"name": kw, "type": "技术", "description": f"在文章中出现{c}次"}
            for kw, c in sorted(found.items(), key=lambda x: -x[1])
        ]
        return {"entities": entities, "relations": []}

    def _build_graph(self, entities: dict[str, Entity], relations: list[Relation]) -> dict:
        """构建图谱数据结构"""
        top_names = set(
            name for name, _ in self._entity_index.most_common(self.top_entities)
        )
        nodes = []
        for name, ent in entities.items():
            if name in top_names or ent.mentions > 1:
                nodes.append({
                    "id": name,
                    "label": name,
                    "type": ent.entity_type,
                    "mentions": ent.mentions,
                    "description": ent.description,
                })
        node_ids = {n["id"] for n in nodes}
        edges = []
        for rel in relations:
            if rel.source_entity in node_ids and rel.target_entity in node_ids:
                edges.append({
                    "source": rel.source_entity,
                    "target": rel.target_entity,
                    "type": rel.relation_type,
                    "weight": rel.confidence,
                })
        communities = self._detect_communities(nodes, edges)
        return {
            "nodes": nodes,
            "edges": edges,
            "communities": communities,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "by_type": dict(Counter(n["type"] for n in nodes)),
            },
        }

    def _detect_communities(self, nodes: list[dict], edges: list[dict]) -> list[list[str]]:
        """简单的社区检测（基于共享邻居）"""
        adjacency: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])
        visited: set[str] = set()
        communities: list[list[str]] = []
        for node in nodes:
            nid = node["id"]
            if nid in visited:
                continue
            community = {nid}
            queue = [nid]
            while queue:
                current = queue.pop(0)
                for neighbor in adjacency.get(current, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        community.add(neighbor)
                        queue.append(neighbor)
            visited.add(nid)
            if len(community) > 1:
                communities.append(list(community))
        return communities[:20]

    def _save_to_db(self, entities: dict[str, Entity], relations: list[Relation]):
        """保存到数据库"""
        now = datetime.now().isoformat()
        with get_cursor() as cur:
            for ent in entities.values():
                cur.execute(
                    """INSERT INTO entities (name, entity_type, description, mentions, source_articles, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name, entity_type)
                    DO UPDATE SET mentions=mentions+?, source_articles=source_articles""",
                    (ent.name, ent.entity_type, ent.description, ent.mentions,
                     json.dumps(ent.source_articles), now, ent.mentions),
                )
            for rel in relations:
                cur.execute(
                    """INSERT INTO relations (source_entity, target_entity, relation_type, confidence, source_articles, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (rel.source_entity, rel.target_entity, rel.relation_type,
                     rel.confidence, json.dumps(rel.source_articles), now),
                )


def _get_analysis_cfg() -> dict:
    return Config.settings().get("analysis", {})


from ..config import Config  # noqa: E402
