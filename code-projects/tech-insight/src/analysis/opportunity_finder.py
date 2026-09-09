"""机会识别器 - 结合趋势、知识图谱、行业洞察，识别 AI 时代的个人机会"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..storage.models import Opportunity
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = """你是一位顶尖的科技行业战略顾问和职业规划专家，擅长从技术趋势和行业动态中识别个人发展机会。
你的分析基于真实的技术媒体数据，客观、有洞察力、可操作。"""

_OPPORTUNITY_PROMPT = """基于以下来自技术媒体的深度分析数据，识别 AI 时代的个人机会。

## 技术趋势数据
最热技术: {top_trends}
新兴技术: {emerging_tech}
衰退技术: {declining_tech}

## 知识图谱洞察
核心实体: {key_entities}
热门关系: {key_relations}

## 架构全景
主流架构: {arch_patterns}
热门技术栈: {tech_stacks}

## 热门内容
{hot_topics}

请从以下 5 个维度识别机会，每个维度 2-3 个具体机会，返回 JSON 数组:
{{
  "opportunities": [
    {{
      "title": "机会标题（具体明确）",
      "dimension": "技术趋势/人才缺口/创业方向/个人成长/变现路径",
      "description": "详细描述（为什么这是机会）",
      "evidence": ["数据证据1", "数据证据2"],
      "skills_needed": ["需要的技能1", "技能2"],
      "market_signal": "市场信号",
      "action_items": ["可执行的行动步骤1", "步骤2"],
      "confidence": 0.0-1.0,
      "time_horizon": "1-3个月/3-6个月/6-12个月/1-2年"
    }}
  ]
}}

要求：
- 机会必须基于上面的真实数据，不要泛泛而谈
- 每个机会必须有具体、可操作的行动步骤
- 区分短期机会和长期机会
- 考虑中国大陆市场的实际情况
- 重点关注 AI 相关但非纯算法研究的机会（如 AI 工程、AI 产品、AI 应用等）
"""


class OpportunityFinder:
    """AI 时代个人机会识别器"""

    def __init__(self):
        self.llm = LLMClient()

    def find(self, trend_data: dict, graph_data: dict, arch_data: dict,
             hot_topics: list[dict]) -> dict:
        """综合所有分析数据识别机会"""
        if not self.llm._available():
            return self._fallback_opportunities(trend_data, graph_data)

        top_trends = ", ".join(
            f"{t['keyword']}({t.get('current_count', 0)}次)"
            for t in trend_data.get("trends", [])[:15]
        )
        emerging_tech = ", ".join(
            e["keyword"] for e in trend_data.get("emerging", [])[:10]
        )
        declining_tech = ", ".join(
            d["keyword"] for d in trend_data.get("declining", [])[:8]
        )
        key_entities = ", ".join(
            f"{n['label']}({n['type']})"
            for n in graph_data.get("nodes", [])[:20]
        )
        key_relations = "; ".join(
            f"{e['source']}→{e['target']}({e['type']})"
            for e in graph_data.get("edges", [])[:15]
        )
        arch_patterns = ", ".join(
            f"{p['name']}({p['type']})"
            for p in arch_data.get("patterns", [])[:10]
        )
        tech_stacks = ", ".join(
            t["name"] for t in arch_data.get("landscape", {}).get("top_technologies", [])[:15]
        )
        hot_topics_text = "\n".join(
            f"- {t['title']} ({t['source']}, 热度:{t.get('score', 0)})"
            for t in hot_topics[:10]
        )

        prompt = _OPPORTUNITY_PROMPT.format(
            top_trends=top_trends,
            emerging_tech=emerging_tech,
            declining_tech=declining_tech,
            key_entities=key_entities,
            key_relations=key_relations,
            arch_patterns=arch_patterns,
            tech_stacks=tech_stacks,
            hot_topics=hot_topics_text,
        )

        result = self.llm.chat_json(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
            model=self.llm.deep_model,
            max_tokens=8192,
        )
        opportunities = result.get("opportunities", []) if isinstance(result, dict) else []
        parsed = [self._parse_opportunity(o) for o in opportunities]
        parsed = [o for o in parsed if o is not None]
        parsed.sort(key=lambda o: o["confidence"], reverse=True)

        return {
            "opportunities": parsed,
            "by_dimension": self._group_by_dimension(parsed),
            "summary": self._generate_summary(parsed, trend_data),
        }

    def _parse_opportunity(self, data: dict) -> dict | None:
        try:
            return {
                "title": data.get("title", ""),
                "dimension": data.get("dimension", "其他"),
                "description": data.get("description", ""),
                "evidence": data.get("evidence", []),
                "skills_needed": data.get("skills_needed", []),
                "market_signal": data.get("market_signal", ""),
                "action_items": data.get("action_items", []),
                "confidence": float(data.get("confidence", 0.5)),
                "time_horizon": data.get("time_horizon", "6-12个月"),
            }
        except Exception:
            return None

    def _group_by_dimension(self, opportunities: list[dict]) -> dict[str, list[dict]]:
        groups: dict[str, list[dict]] = {}
        for o in opportunities:
            dim = o["dimension"]
            groups.setdefault(dim, []).append(o)
        return groups

    def _generate_summary(self, opportunities: list[dict], trend_data: dict) -> str:
        if not self.llm._available() or not opportunities:
            return self._summary_fallback(opportunities)
        dims = ", ".join(
            f"{dim}({len(items)}个)"
            for dim, items in self._group_by_dimension(opportunities).items()
        )
        top_opps = "\n".join(
            f"- {o['title']} (置信度:{o['confidence']:.0%}, {o['time_horizon']})"
            for o in opportunities[:8]
        )
        prompt = f"""基于以下识别出的 {len(opportunities)} 个 AI 时代个人机会，写一段 500 字的总结：

维度分布: {dims}
核心机会:
{top_opps}

请用犀利、有洞察力的语言总结：
1. 整体格局判断
2. 最值得关注的 3 个机会
3. 最紧迫的行动建议
4. 风险提示

直接输出分析文本。"""
        return self.llm.chat(
            [{"role": "system", "content": _SYSTEM},
             {"role": "user", "content": prompt}],
            model=self.llm.deep_model,
        )

    def _fallback_opportunities(self, trend_data: dict, graph_data: dict) -> dict:
        """无 LLM 时的基础机会列表"""
        emerging = trend_data.get("emerging", [])
        opps = []
        for e in emerging[:5]:
            opps.append({
                "title": f"掌握 {e['keyword']} 技术栈",
                "dimension": "技术趋势",
                "description": f"{e['keyword']} 正在快速增长（增长率 {e.get('growth_rate', 0):+.0%}），"
                               f"是值得投入学习的技术方向。",
                "evidence": [f"近期出现 {e.get('current_count', 0)} 次"],
                "skills_needed": [e["keyword"]],
                "market_signal": "技术热度上升",
                "action_items": [
                    f"系统学习 {e['keyword']}",
                    f"在 GitHub 上做相关项目",
                    "在技术社区分享实践",
                ],
                "confidence": 0.5,
                "time_horizon": "3-6个月",
            })
        return {
            "opportunities": opps,
            "by_dimension": {"技术趋势": opps},
            "summary": self._summary_fallback(opps),
        }

    def _summary_fallback(self, opportunities: list[dict]) -> str:
        lines = ["## AI 时代个人机会总结（基础版）\n"]
        for o in opportunities[:5]:
            lines.append(f"### {o['title']}")
            lines.append(f"- 维度: {o['dimension']}")
            lines.append(f"- 时间: {o['time_horizon']}")
            lines.append(f"- 描述: {o['description']}\n")
        lines.append("\n> 配置 LLM API Key 后可获得更深入的机会分析。")
        return "\n".join(lines)
