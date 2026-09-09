"""报告生成器 - 将分析结果渲染为高质量 Markdown 报告"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, BaseLoader

from ..config import Config
from ..storage.database import get_stats

logger = logging.getLogger(__name__)

_ENV = Environment(loader=BaseLoader(), trim_blocks=True, lstrip_blocks=True, autoescape=False)


class ReportGenerator:
    """多类型报告生成器"""

    def __init__(self):
        settings = Config.settings()
        self.output_dir = Config.base_dir() / settings["storage"]["reports_path"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.language = settings.get("report", {}).get("language", "zh-CN")

    def generate_all(self, analysis_results: dict[str, Any]) -> dict[str, str]:
        """生成所有报告，返回 {report_name: file_path}"""
        generated: dict[str, str] = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report_map = {
            "content_digest": (self._tpl_digest, "content_digest"),
            "knowledge_graph": (self._tpl_knowledge_graph, "knowledge_graph"),
            "trend_report": (self._tpl_trend, "trend_report"),
            "architecture_map": (self._tpl_architecture, "architecture_map"),
            "industry_insight": (self._tpl_industry, "industry_insight"),
            "ai_opportunity": (self._tpl_opportunity, "ai_opportunity"),
        }

        for name, (template_fn, key) in report_map.items():
            data_key = key
            data = analysis_results.get(data_key, {})
            if not data:
                continue
            content = template_fn(data, analysis_results)
            filename = f"{timestamp}_{name}.md"
            filepath = self.output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            generated[name] = str(filepath)
            logger.info(f"生成报告: {filepath}")

        master = self._generate_master(generated, analysis_results)
        master_path = self.output_dir / f"{timestamp}_MASTER_report.md"
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(master)
        generated["master"] = str(master_path)
        return generated

    # ==================== 报告模板 ====================

    def _tpl_digest(self, data: dict, all_data: dict) -> str:
        stats = get_stats()
        tpl = _ENV.from_string(_DIGEST_TEMPLATE)
        return tpl.render(stats=stats, timestamp=datetime.now(), data=data)

    def _tpl_knowledge_graph(self, data: dict, all_data: dict) -> str:
        tpl = _ENV.from_string(_KG_TEMPLATE)
        return tpl.render(data=data, timestamp=datetime.now())

    def _tpl_trend(self, data: dict, all_data: dict) -> str:
        tpl = _ENV.from_string(_TREND_TEMPLATE)
        return tpl.render(data=data, timestamp=datetime.now())

    def _tpl_architecture(self, data: dict, all_data: dict) -> str:
        tpl = _ENV.from_string(_ARCH_TEMPLATE)
        return tpl.render(data=data, timestamp=datetime.now())

    def _tpl_industry(self, data: dict, all_data: dict) -> str:
        trend = all_data.get("trend_report", {})
        graph = all_data.get("knowledge_graph", {})
        arch = all_data.get("architecture_map", {})
        tpl = _ENV.from_string(_INDUSTRY_TEMPLATE)
        return tpl.render(
            trend=trend, graph=graph, arch=arch,
            data=data, timestamp=datetime.now(),
        )

    def _tpl_opportunity(self, data: dict, all_data: dict) -> str:
        tpl = _ENV.from_string(_OPPORTUNITY_TEMPLATE)
        return tpl.render(data=data, timestamp=datetime.now())

    def _generate_master(self, generated: dict[str, str], all_data: dict) -> str:
        stats = get_stats()
        tpl = _ENV.from_string(_MASTER_TEMPLATE)
        return tpl.render(
            stats=stats,
            generated=generated,
            timestamp=datetime.now(),
            analysis=all_data,
        )


# ==================== Jinja2 模板 ====================

_MASTER_TEMPLATE = """# 技术媒体洞察报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}
> 数据源: InfoQ + 掘金 + SegmentFault + 开源中国 + 博客园 + V2EX + 机器之心 + 量子位 + 36氪 + HackerNews + Dev.to 等

---

## 数据概览

| 指标 | 数值 |
|------|------|
| 采集文章总数 | {{ stats.total_articles }} |
| 已分析文章 | {{ stats.analyzed_articles }} |
| 知识图谱实体 | {{ stats.entities }} |
| 知识图谱关系 | {{ stats.relations }} |

### 各数据源采集量

{% for source, count in stats.by_source.items() %}
- {{ source }}: {{ count }} 篇
{% endfor %}

---

## 报告索引

{% if 'content_digest' in generated %}
1. **内容摘要报告** - `{{ generated['content_digest'] }}`
{% endif %}
{% if 'knowledge_graph' in generated %}
2. **知识图谱报告** - `{{ generated['knowledge_graph'] }}`
{% endif %}
{% if 'trend_report' in generated %}
3. **技术趋势报告** - `{{ generated['trend_report'] }}`
{% endif %}
{% if 'architecture_map' in generated %}
4. **架构全景报告** - `{{ generated['architecture_map'] }}`
{% endif %}
{% if 'industry_insight' in generated %}
5. **行业洞察报告** - `{{ generated['industry_insight'] }}`
{% endif %}
{% if 'ai_opportunity' in generated %}
6. **AI时代个人机会报告** - `{{ generated['ai_opportunity'] }}`
{% endif %}

---

## 四层分析框架

本报告遵循四层递进分析框架:

### 第一层：内容结构化（穷尽式采集与处理）
对 InfoQ 及 12+ 技术媒体进行系统化采集，通过 RSS/API 合规获取，
将非结构化内容转为结构化数据，建立完整的技术内容知识库。

### 第二层：知识图谱构建（建立架构思维）
从内容中提取实体（技术、公司、人物、产品、概念）和关系（使用、依赖、竞争、影响），
构建技术领域知识图谱，揭示技术间的深层关联。

### 第三层：行业洞察（洞悉行业秘密）
通过趋势分析、架构全景、跨平台对比，识别技术周期、人才流动、资本动向，
洞察行业不为人知的秘密。

### 第四层：个人机会（AI 时代的行动指南）
将以上洞察转化为具体的、可操作的个人发展机会，
涵盖技术趋势、人才缺口、创业方向、个人成长、变现路径五个维度。
"""

_DIGEST_TEMPLATE = """# 内容摘要报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}

---

## 采集概况

- 文章总数: {{ stats.total_articles }}
- 已分析: {{ stats.analyzed_articles }}
- 实体数: {{ stats.entities }}
- 关系数: {{ stats.relations }}

{% if data.hot_topics %}
## 热门内容 TOP 20

| # | 标题 | 来源 | 热度 | 时间 |
|---|------|------|------|------|
{% for item in data.hot_topics[:20] %}
| {{ loop.index }} | {{ item.title[:50] }} | {{ item.source }} | {{ item.score }} | {{ item.published_at[:10] if item.published_at else '-' }} |
{% endfor %}
{% endif %}

{% if data.by_source %}
## 各源内容分布

{% for source, count in data.by_source.items() %}
- **{{ source }}**: {{ count }} 篇
{% endfor %}
{% endif %}
"""

_KG_TEMPLATE = """# 知识图谱分析报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}

---

## 图谱概览

- 实体总数: {{ data.stats.total_nodes }}
- 关系总数: {{ data.stats.total_edges }}
- 社区数: {{ data.communities | length }}

### 实体类型分布

| 类型 | 数量 |
|------|------|
{% for type, count in data.stats.by_type.items() %}
| {{ type }} | {{ count }} |
{% endfor %}

---

## 核心实体（按提及频率）

| 实体 | 类型 | 提及次数 |
|------|------|----------|
{% for node in data.nodes[:30] %}
| {{ node.label }} | {{ node.type }} | {{ node.mentions }} |
{% endfor %}

---

## 关键关系

| 源实体 | 关系 | 目标实体 | 强度 |
|--------|------|----------|------|
{% for edge in data.edges[:30] %}
| {{ edge.source }} | {{ edge.type }} | {{ edge.target }} | {{ "%.2f" | format(edge.weight) }} |
{% endfor %}

---

{% if data.communities %}
## 技术社区（关联技术集群）

{% for community in data.communities[:10] %}
### 集群 {{ loop.index }}
{{ community | join(", ") }}
{% endfor %}
{% endif %}
"""

_TREND_TEMPLATE = """# 技术趋势分析报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}
> 分析窗口: 近 {{ data.time_windows[0] }} 天 vs 前 {{ data.time_windows[0] }} 天

---

## 趋势叙述

{{ data.narrative }}

---

## 热门技术 TOP 20

| 排名 | 技术 | 当前热度 | 增长率 | 首次出现 |
|------|------|----------|--------|----------|
{% for t in data.trends[:20] %}
| {{ loop.index }} | {{ t.keyword }} | {{ t.current_count }} | {{ "%+.0f%%" | format(t.growth_rate * 100) }} | {{ t.first_seen[:10] if t.first_seen else '-' }} |
{% endfor %}

---

## 新兴技术（快速增长）

| 技术 | 增长率 | 当前热度 |
|------|--------|----------|
{% for e in data.emerging[:15] %}
| {{ e.keyword }} | {{ "%+.0f%%" | format(e.growth_rate * 100) }} | {{ e.current_count }} |
{% endfor %}

---

{% if data.declining %}
## 衰退技术

| 技术 | 变化率 | 上期热度 | 本期热度 |
|------|--------|----------|----------|
{% for d in data.declining %}
| {{ d.keyword }} | {{ "%+.0f%%" | format(d.growth_rate * 100) }} | {{ d.previous_count }} | {{ d.current_count }} |
{% endfor %}
{% endif %}

---

## 热门内容

{% for topic in data.hot_topics[:15] %}
- [{{ topic.title }}]({{ topic.url }}) ({{ topic.source }}, 热度: {{ topic.score }})
{% endfor %}
"""

_ARCH_TEMPLATE = """# 架构全景报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}

---

## 架构模式概览

共识别 {{ data.stats.total_patterns }} 种架构模式。

### 模式类型分布

| 类型 | 数量 |
|------|------|
{% for type, count in data.stats.by_type.items() %}
| {{ type }} | {{ count }} |
{% endfor %}

---

## 主要架构模式

{% for pattern in data.patterns[:15] %}
### {{ loop.index }}. {{ pattern.name }} ({{ pattern.type }})

{{ pattern.description }}

{% if pattern.technologies %}
**使用技术**: {{ pattern.technologies | join(", ") }}
{% endif %}
{% if pattern.pros %}
**优点**:
{% for pro in pattern.pros %}
- {{ pro }}
{% endfor %}
{% endif %}
{% if pattern.cons %}
**缺点**:
{% for con in pattern.cons %}
- {{ con }}
{% endfor %}
{% endif %}
{% if pattern.use_cases %}
**适用场景**:
{% for uc in pattern.use_cases %}
- {{ uc }}
{% endfor %}
{% endif %}
> 引用 {{ pattern.source_count }} 篇文章

---
{% endfor %}

## 技术栈全景

{% for category, techs in data.tech_stacks.items() %}
### {{ category }}

{% for tech in techs[:10] %}
- {{ tech.name }} ({{ tech.count }}次)
{% endfor %}
{% endfor %}
"""

_INDUSTRY_TEMPLATE = """# 行业洞察报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}

---

## 一、行业格局判断

{% if trend.narrative %}
{{ trend.narrative }}
{% endif %}

---

## 二、技术资本流向

### 增长最快的技术（资本+人才涌入方向）

{% if trend.emerging %}
{% for e in trend.emerging[:10] %}
- **{{ e.keyword }}**: 增长 {{ "%+.0f%%" | format(e.growth_rate * 100) }}
{% endfor %}
{% endif %}

### 正在衰退的技术（资本+人才退出方向）

{% if trend.declining %}
{% for d in trend.declining[:8] %}
- **{{ d.keyword }}**: 衰退 {{ "%+.0f%%" | format(d.growth_rate * 100) }}
{% endfor %}
{% endif %}

---

## 三、技术选型暗线

{% if arch.landscape and arch.landscape.top_technologies %}
### 行业实际使用最多的技术（非营销热度）

| 技术 | 出现频次 |
|------|----------|
{% for tech in arch.landscape.top_technologies[:15] %}
| {{ tech.name }} | {{ tech.count }} |
{% endfor %}

> 注：营销热度和实际使用频次之间的差异，往往揭示了行业"说一套做一套"的秘密。
{% endif %}

---

## 四、行业"不为人知"的秘密

{% if graph.stats %}
### 核心权力节点

以下实体在知识图谱中拥有最多连接，是行业的"权力中心":

| 实体 | 类型 | 连接数 |
|------|------|--------|
{% for node in graph.nodes[:10] %}
| {{ node.label }} | {{ node.type }} | {{ node.mentions }} |
{% endfor %}
{% endif %}

### 跨平台一致性

当同一技术在多个独立技术媒体中同时出现，说明这不是偶然。
以下技术在 3+ 平台同时热门，代表行业级共识:

{% for t in trend.trends[:10] %}
- {{ t.keyword }} ({{ t.current_count }}次)
{% endfor %}

---

## 五、对从业者的启示

1. **跟资本走，不跟热度走**: 关注增长的技术，而非最热的技术
2. **看实际使用，不看营销**: 技术栈频次比文章数量更反映真相
3. **提前布局新兴**: 新兴技术通常 6-12 个月后成为主流
4. **及时退出衰退**: 衰退技术领域的机会正在快速消失
"""

_OPPORTUNITY_TEMPLATE = """# AI 时代个人机会报告

> 生成时间: {{ timestamp.strftime("%Y-%m-%d %H:%M") }}
> 基于 {{ data.opportunities | length }} 个识别机会的综合分析

---

## 总结

{{ data.summary }}

---

## 机会全景（按维度）

{% for dimension, opps in data.by_dimension.items() %}
### {{ dimension }}

{% for opp in opps %}
#### {{ loop.index }}. {{ opp.title }}

- **置信度**: {{ "%.0f%%" | format(opp.confidence * 100) }}
- **时间窗口**: {{ opp.time_horizon }}
- **描述**: {{ opp.description }}

{% if opp.evidence %}
**数据证据**:
{% for e in opp.evidence %}
- {{ e }}
{% endfor %}
{% endif %}

{% if opp.skills_needed %}
**所需技能**:
{% for s in opp.skills_needed %}
- {{ s }}
{% endfor %}
{% endif %}

{% if opp.market_signal %}
**市场信号**: {{ opp.market_signal }}
{% endif %}

{% if opp.action_items %}
**行动计划**:
{% for action in opp.action_items %}
{{ loop.index }}. {{ action }}
{% endfor %}
{% endif %}

---
{% endfor %}
{% endfor %}

---

## 机会优先级矩阵

| 机会 | 维度 | 置信度 | 时间窗口 |
|------|------|--------|----------|
{% for opp in data.opportunities %}
| {{ opp.title[:30] }} | {{ opp.dimension }} | {{ "%.0f%%" | format(opp.confidence * 100) }} | {{ opp.time_horizon }} |
{% endfor %}

---

## 立即行动清单

### 本周可做的（短期）
{% for opp in data.opportunities if '1-3个月' in opp.time_horizon or '3-6个月' in opp.time_horizon %}
- [ ] {{ opp.title }}: {{ opp.action_items[0] if opp.action_items else '' }}
{% endfor %}

### 本季度规划（中期）
{% for opp in data.opportunities if '6-12个月' in opp.time_horizon %}
- [ ] {{ opp.title }}: {{ opp.action_items[0] if opp.action_items else '' }}
{% endfor %}

### 长期布局（1年+）
{% for opp in data.opportunities if '1-2年' in opp.time_horizon or '2年' in opp.time_horizon %}
- [ ] {{ opp.title }}: {{ opp.action_items[0] if opp.action_items else '' }}
{% endfor %}

---

> 本报告由 TechInsight 自动生成，基于多源技术媒体数据 + LLM 深度分析。
> 配置更强的 LLM 模型可获得更精准的机会识别。
"""
