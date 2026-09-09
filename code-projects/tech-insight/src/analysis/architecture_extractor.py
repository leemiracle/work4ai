"""架构提取器 - 从文章中提取架构模式、技术栈、最佳实践"""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from typing import Any

from ..storage.models import ArchitecturePattern
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = """你是一位资深软件架构师，擅长从技术文章中提炼架构模式、技术选型和最佳实践。"""

_EXTRACT_PROMPT = """从以下技术文章中提取架构相关信息。

文章标题: {title}
文章内容: {content}

请提取并返回 JSON:
{{
  "patterns": [
    {{
      "name": "架构/模式名称",
      "type": "类型（微服务/单体/事件驱动/分层/CQRS/DDD/云原生/Serverless等）",
      "description": "简述",
      "technologies": ["使用的技术"],
      "pros": ["优点"],
      "cons": ["缺点"],
      "use_cases": ["适用场景"]
    }}
  ],
  "tech_stacks": [
    {{
      "category": "前端/后端/数据库/中间件/DevOps/AI",
      "technologies": ["技术名"]
    }}
  ]
}}"""


class ArchitectureExtractor:
    """架构模式提取器"""

    def __init__(self):
        self.llm = LLMClient()

    def extract(self, articles: list[dict]) -> dict:
        """从文章列表提取架构信息"""
        all_patterns: dict[str, ArchitecturePattern] = {}
        all_stacks: dict[str, Counter] = defaultdict(Counter)
        processed = 0

        for article in articles:
            content = article.get("content", "")[:800]
            if len(content) < 100:
                continue
            result = self._extract_from_article(article["title"], content)
            if not result:
                continue
            article_id = article.get("id", article.get("url", ""))
            for p_data in result.get("patterns", []):
                name = p_data.get("name", "").strip()
                if not name:
                    continue
                if name not in all_patterns:
                    all_patterns[name] = ArchitecturePattern(
                        name=name,
                        pattern_type=p_data.get("type", "通用"),
                        description=p_data.get("description", ""),
                        technologies=p_data.get("technologies", []),
                        pros=p_data.get("pros", []),
                        cons=p_data.get("cons", []),
                        use_cases=p_data.get("use_cases", []),
                        source_articles=[article_id],
                    )
                else:
                    all_patterns[name].source_articles.append(article_id)
            for stack in result.get("tech_stacks", []):
                cat = stack.get("category", "其他")
                for tech in stack.get("technologies", []):
                    all_stacks[cat][tech] += 1
            processed += 1

        logger.info(f"架构提取完成: {processed} 篇文章, "
                     f"{len(all_patterns)} 架构模式, {sum(len(v) for v in all_stacks.values())} 技术栈")

        landscape = self._build_landscape(all_patterns, all_stacks)
        return {
            "patterns": [self._pattern_to_dict(p) for p in all_patterns.values()],
            "tech_stacks": {
                cat: [{"name": t, "count": c} for t, c in techs.most_common(20)]
                for cat, techs in all_stacks.items()
            },
            "landscape": landscape,
            "stats": {
                "total_patterns": len(all_patterns),
                "by_type": dict(Counter(p.pattern_type for p in all_patterns.values())),
                "total_technologies": sum(len(v) for v in all_stacks.values()),
            },
        }

    def _extract_from_article(self, title: str, content: str) -> dict:
        if not self.llm._available():
            return {}
        prompt = _EXTRACT_PROMPT.format(title=title, content=content)
        result = self.llm.chat_json(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
        )
        return result if isinstance(result, dict) else {}

    def _build_landscape(self, patterns: dict, stacks: dict) -> dict:
        """构建技术全景图"""
        all_tech: Counter = Counter()
        for cat_tech in stacks.values():
            all_tech.update(cat_tech)
        top_tech = all_tech.most_common(30)
        pattern_groups: dict[str, list[str]] = defaultdict(list)
        for p in patterns.values():
            pattern_groups[p.pattern_type].append(p.name)
        return {
            "top_technologies": [{"name": t, "count": c} for t, c in top_tech],
            "pattern_groups": {
                k: v for k, v in pattern_groups.items()
            },
        }

    @staticmethod
    def _pattern_to_dict(p: ArchitecturePattern) -> dict:
        return {
            "name": p.name,
            "type": p.pattern_type,
            "description": p.description,
            "technologies": p.technologies,
            "pros": p.pros,
            "cons": p.cons,
            "use_cases": p.use_cases,
            "source_count": len(p.source_articles),
        }
