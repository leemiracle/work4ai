"""RAG 检索增强问答 - 基于向量检索 + LLM"""

from __future__ import annotations

import hashlib
import logging
from typing import Optional

from ..analysis.llm_client import LLMClient
from ..storage.database import get_all_articles, get_stats
from ..storage.vectorstore import VectorStore

logger = logging.getLogger(__name__)

_SYSTEM = """你是一位技术知识助手，基于技术媒体文章库回答问题。
请严格基于提供的参考资料回答，如果资料不足以回答，请说明。
引用信息时请标注来源。"""


class RAGEngine:
    """RAG 问答引擎"""

    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
        self._indexed = False

    def index_articles(self, batch_size: int = 20, max_articles: int = 500):
        """将文章内容向量化入库"""
        articles = get_all_articles(limit=max_articles)
        existing_ids = {item["id"] for item in self.vector_store._index}
        new_articles = [a for a in articles if a["id"] not in existing_ids]
        if not new_articles:
            logger.info("无需索引新文章")
            self._indexed = True
            return

        logger.info(f"开始索引 {len(new_articles)} 篇文章...")
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i:i + batch_size]
            texts = [
                f"标题: {a['title']}\n摘要: {a.get('summary', '')}\n内容: {a.get('content', '')[:1000]}"
                for a in batch
            ]
            ids = [a["id"] for a in batch]
            vectors = self.llm.embed(texts)
            if vectors and len(vectors) == len(batch):
                self.vector_store.add(ids, texts, vectors)
            else:
                logger.warning(f"批次 {i} embedding 失败或数量不匹配")
        self._indexed = True
        logger.info(f"索引完成，共 {self.vector_store.size} 条向量")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """检索相关文章"""
        if not self._indexed:
            self.index_articles()
        query_vec = self.llm.embed([query])
        if not query_vec:
            return []
        return self.vector_store.search(query_vec[0], top_k=top_k)

    def answer(self, question: str, top_k: int = 5) -> dict:
        """RAG 问答"""
        results = self.search(question, top_k=top_k)
        if not results:
            if not self.llm._available():
                return {
                    "answer": "知识库为空且 LLM 未配置，请先采集数据并配置 LLM。",
                    "sources": [],
                }
            return {
                "answer": self.llm.chat(
                    [{"role": "user", "content": question}],
                ),
                "sources": [],
            }

        context_parts = []
        sources = []
        for i, r in enumerate(results):
            context_parts.append(f"[参考{i+1}] (相关度:{r['score']:.2f})\n{r['text']}")
            sources.append({"text": r["text"][:200], "score": r["score"]})

        context = "\n\n---\n\n".join(context_parts)
        prompt = f"""参考资料:
{context}

问题: {question}

请基于以上参考资料回答问题。"""

        answer = self.llm.chat(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
            model=self.llm.deep_model,
        )
        return {"answer": answer, "sources": sources}
