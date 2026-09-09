"""趋势分析器 - 识别技术趋势、增长率、新兴概念"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

from ..storage.database import get_cursor
from ..storage.models import TechTrend
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = """你是一位敏锐的技术趋势分析师，擅长从技术媒体内容中识别新兴趋势和行业方向。"""


class TrendAnalyzer:
    """技术趋势分析器"""

    def __init__(self):
        self.llm = LLMClient()
        from ..config import Config
        cfg = Config.settings().get("analysis", {})
        self.windows = cfg.get("trend", {}).get("time_windows", [7, 14, 30])
        self.top_n = cfg.get("trend", {}).get("keywords_top_n", 50)
        self.growth_threshold = cfg.get("trend", {}).get("growth_rate_threshold", 0.3)

    def analyze(self, articles: list[dict]) -> dict:
        """分析技术趋势"""
        keyword_timeline = self._build_keyword_timeline(articles)
        trends = self._compute_trends(keyword_timeline)
        emerging = self._identify_emerging(trends)
        declining = self._identify_declining(trends)
        hot_topics = self._get_hot_topics(articles)
        trend_narrative = self._generate_narrative(trends, emerging, hot_topics)
        return {
            "trends": [t.__dict__ for t in trends[:self.top_n]],
            "emerging": emerging,
            "declining": declining,
            "hot_topics": hot_topics,
            "narrative": trend_narrative,
            "time_windows": self.windows,
            "stats": {
                "total_keywords": len(trends),
                "emerging_count": len(emerging),
                "declining_count": len(declining),
            },
        }

    def _build_keyword_timeline(self, articles: list[dict]) -> dict[str, dict]:
        """构建关键词时间线"""
        timeline: dict[str, dict] = defaultdict(lambda: defaultdict(int))
        tech_lexicon = self._build_tech_lexicon(articles)
        for article in articles:
            text = f"{article.get('title', '')} {article.get('content', '')} {article.get('tags', '')}"
            published = article.get("published_at", article.get("collected_at", ""))
            try:
                date = datetime.fromisoformat(published.replace("Z", "")).strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                date = datetime.now().strftime("%Y-%m-%d")
            for kw in tech_lexicon:
                if kw in text:
                    timeline[kw][date] += 1
        return timeline

    def _build_tech_lexicon(self, articles: list[dict]) -> list[str]:
        """构建技术词汇表（结合预设词库 + LLM 抽取高频词）"""
        base_lexicon = {
            "大模型", "LLM", "GPT", "GPT-4", "Claude", "Gemini", "RAG", "Agent",
            "微服务", "云原生", "Kubernetes", "Docker", "Serverless",
            "React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt",
            "Python", "Java", "Go", "Rust", "TypeScript", "Kotlin", "Swift",
            "TensorFlow", "PyTorch", "Transformer", "扩散模型", "多模态",
            "向量数据库", "Milvus", "Pinecone", "Weaviate",
            "DevOps", "CI/CD", "可观测性", "Service Mesh",
            "Kafka", "Redis", "MySQL", "PostgreSQL", "Elasticsearch",
            "WebAssembly", "WASM", "Edge Computing", "边缘计算",
            "低代码", "NoCode", "AIGC", "文生图", "文生视频",
            "MoE", "推理优化", "量化", "蒸馏", "RLHF", "DPO",
            "LangChain", "LlamaIndex", "AutoGen", "CrewAI",
            "微前端", "BFF", "DDD", "事件驱动", "CQRS",
            "鸿蒙", "HarmonyOS", "Flutter", "React Native",
            "DataOps", "MLOps", "LLMOps", "Feature Store",
            "隐私计算", "联邦学习", "差分隐私",
        }
        text_combined = " ".join(
            a.get("title", "") for a in articles[:200]
        )
        freq: Counter = Counter()
        for kw in base_lexicon:
            count = text_combined.count(kw)
            if count > 0:
                freq[kw] = count
        return list(freq.keys()) if freq else list(base_lexicon)[:30]

    def _compute_trends(self, timeline: dict[str, dict]) -> list[TechTrend]:
        """计算各关键词的增长趋势"""
        now = datetime.now()
        recent_end = now
        recent_start = now - timedelta(days=self.windows[0])
        prev_end = recent_start
        prev_start = prev_end - timedelta(days=self.windows[0])

        trends: list[TechTrend] = []
        for kw, date_counts in timeline.items():
            recent_count = sum(
                c for d, c in date_counts.items()
                if recent_start.strftime("%Y-%m-%d") <= d <= recent_end.strftime("%Y-%m-%d")
            )
            prev_count = sum(
                c for d, c in date_counts.items()
                if prev_start.strftime("%Y-%m-%d") <= d <= prev_end.strftime("%Y-%m-%d")
            )
            growth = ((recent_count - prev_count) / max(prev_count, 1)) if prev_count > 0 else (
                float(recent_count) if recent_count > 0 else 0.0
            )
            dates = sorted(date_counts.keys())
            trends.append(TechTrend(
                keyword=kw,
                category="技术",
                current_count=recent_count,
                previous_count=prev_count,
                growth_rate=round(growth, 2),
                first_seen=dates[0] if dates else None,
                last_seen=dates[-1] if dates else None,
            ))
        trends.sort(key=lambda t: (t.current_count, t.growth_rate), reverse=True)
        self._save_trends(trends)
        return trends

    def _save_trends(self, trends: list[TechTrend]):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with get_cursor() as cur:
            for t in trends:
                cur.execute(
                    """INSERT OR REPLACE INTO trends
                    (keyword, category, current_count, previous_count, growth_rate,
                     first_seen, last_seen, related_entities, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (t.keyword, t.category, t.current_count, t.previous_count,
                     t.growth_rate, t.first_seen, t.last_seen,
                     json.dumps(t.related_entities), now),
                )

    def _identify_emerging(self, trends: list[TechTrend]) -> list[dict]:
        """识别新兴趋势"""
        emerging = [
            {
                "keyword": t.keyword,
                "growth_rate": t.growth_rate,
                "current_count": t.current_count,
                "first_seen": t.first_seen,
            }
            for t in trends
            if t.growth_rate >= self.growth_threshold and t.current_count >= 2
        ]
        return emerging[:20]

    def _identify_declining(self, trends: list[TechTrend]) -> list[dict]:
        """识别衰退趋势"""
        declining = [
            {
                "keyword": t.keyword,
                "growth_rate": t.growth_rate,
                "previous_count": t.previous_count,
                "current_count": t.current_count,
            }
            for t in trends
            if t.growth_rate <= -self.growth_threshold and t.previous_count >= 3
        ]
        return declining[:15]

    def _get_hot_topics(self, articles: list[dict]) -> list[dict]:
        """获取热门话题（按互动数据排序）"""
        scored = []
        for a in articles:
            score = (
                a.get("view_count", 0) * 1
                + a.get("like_count", 0) * 5
                + a.get("comment_count", 0) * 10
                + a.get("bookmark_count", 0) * 3
            )
            scored.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source_name", ""),
                "score": score,
                "published_at": a.get("published_at", ""),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:30]

    def _generate_narrative(self, trends: list[TechTrend], emerging: list[dict],
                            hot_topics: list[dict]) -> str:
        """用 LLM 生成趋势叙述"""
        if not self.llm._available():
            return self._narrative_fallback(trends, emerging)
        top_keywords = ", ".join(t.keyword for t in trends[:15])
        emerging_kw = ", ".join(e["keyword"] for e in emerging[:10])
        prompt = f"""基于以下技术媒体趋势数据，生成一份简洁的趋势分析叙述（800字以内）：

最热技术关键词（按热度）: {top_keywords}
新兴技术（增长率高）: {emerging_kw}

请分析：
1. 当前技术格局（哪些技术占据主导）
2. 新兴趋势（哪些技术在快速崛起）
3. 可能的原因和背景
4. 未来6个月预测

直接输出分析文本，不要 markdown 代码块。"""
        return self.llm.chat(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
            model=self.llm.deep_model,
        )

    def _narrative_fallback(self, trends: list[TechTrend], emerging: list[dict]) -> str:
        lines = ["## 技术趋势概述（基于关键词统计）\n"]
        lines.append("### 当前热门技术 TOP 10")
        for t in trends[:10]:
            lines.append(f"- **{t.keyword}**: 出现 {t.current_count} 次，增长率 {t.growth_rate:+.0%}")
        lines.append("\n### 新兴技术（快速增长）")
        for e in emerging[:10]:
            lines.append(f"- **{e['keyword']}**: 增长 {e['growth_rate']:+.0%}")
        return "\n".join(lines)
