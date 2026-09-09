"""向量存储 - 基于文件系统的简单向量检索（可选 numpy/faiss）"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Optional

import numpy as np

from ..config import Config

logger = logging.getLogger(__name__)


class VectorStore:
    """基于 numpy 的简单向量存储与检索"""

    def __init__(self):
        settings = Config.settings()
        self.store_path = Config.base_dir() / settings["storage"]["vector_path"]
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.store_path / "index.json"
        self.vectors_file = self.store_path / "vectors.npy"
        self._index: list[dict] = []
        self._vectors: Optional[np.ndarray] = None
        self._load()

    def _load(self):
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self._index = json.load(f)
        if self.vectors_file.exists():
            self._vectors = np.load(self.vectors_file)

    def _save(self):
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self._index, f, ensure_ascii=False)
        if self._vectors is not None:
            np.save(self.vectors_file, self._vectors)

    def add(self, ids: list[str], texts: list[str], vectors: list[list[float]]):
        """添加向量"""
        new_vectors = np.array(vectors, dtype=np.float32)
        for i, (aid, text) in enumerate(zip(ids, texts)):
            self._index.append({"id": aid, "text": text[:500]})
        if self._vectors is None:
            self._vectors = new_vectors
        else:
            self._vectors = np.vstack([self._vectors, new_vectors])
        self._save()
        logger.info(f"向量存储: 新增 {len(ids)} 条, 总计 {len(self._index)} 条")

    def search(self, query_vec: list[float], top_k: int = 5) -> list[dict]:
        """余弦相似度搜索"""
        if self._vectors is None or len(self._index) == 0:
            return []
        q = np.array(query_vec, dtype=np.float32)
        norms = np.linalg.norm(self._vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        normalized = self._vectors / norms
        q_normalized = q / q_norm
        scores = normalized @ q_normalized
        top_indices = np.argsort(scores)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.1:
                results.append({
                    **self._index[idx],
                    "score": float(scores[idx]),
                })
        return results

    @property
    def size(self) -> int:
        return len(self._index)
