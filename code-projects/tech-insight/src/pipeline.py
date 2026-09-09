"""管道编排 - 串联采集→存储→分析→报告的全流程"""

from __future__ import annotations

import logging
import time
from typing import Any

from .analysis.architecture_extractor import ArchitectureExtractor
from .analysis.knowledge_graph import KnowledgeGraphBuilder
from .analysis.opportunity_finder import OpportunityFinder
from .analysis.trend_analysis import TrendAnalyzer
from .collectors.enricher import ContentEnricher
from .collectors.factory import collect_all, collect_from, get_all_source_keys
from .config import Config
from .reports.generator import ReportGenerator
from .storage.database import (
    get_all_articles,
    get_stats,
    get_unanalyzed_articles,
    init_db,
    mark_analyzed,
    save_article,
)

logger = logging.getLogger(__name__)


def run_collection(source: str | None = None, priority: int | None = None,
                   enrich: bool = True) -> dict:
    """阶段1：数据采集"""
    logger.info("=" * 60)
    logger.info("阶段 1/4: 数据采集")
    logger.info("=" * 60)
    init_db()

    if source:
        articles = collect_from(source)
        if enrich:
            articles = _enrich_articles(articles)
        saved = _save_all(articles)
        return {"source": source, "collected": len(articles), "saved": saved}
    else:
        results = collect_all(priority=priority)
        total_collected = 0
        total_saved = 0
        for src_key, articles in results.items():
            if enrich:
                articles = _enrich_articles(articles, source_filter=src_key)
            saved = _save_all(articles)
            total_collected += len(articles)
            total_saved += saved
            logger.info(f"  [{src_key}] 采集 {len(articles)} 篇, 新增 {saved} 篇")
        logger.info(f"采集完成: 共 {total_collected} 篇, 新增 {total_saved} 篇")
        return {
            "total_collected": total_collected,
            "total_saved": total_saved,
            "by_source": {k: len(v) for k, v in results.items()},
        }


def _enrich_articles(articles: list, source_filter: str | None = None,
                     limit: int = 10) -> list:
    """增强文章内容（仅对摘要级文章获取全文，限制数量避免过度请求）"""
    enricher = ContentEnricher()
    enriched_count = 0
    for article in articles:
        if enriched_count >= limit:
            break
        if len(article.content) < 200:
            full_text = enricher.enrich_article(article)
            if full_text and len(full_text) > len(article.content):
                article.content = full_text
                if not article.summary:
                    article.summary = full_text[:500]
                enriched_count += 1
                logger.debug(f"  增强内容: {article.title[:40]}")
    if enriched_count:
        logger.info(f"  内容增强: {enriched_count} 篇")
    return articles


def run_analysis_pipeline(max_articles: int = 300) -> dict[str, Any]:
    """阶段2-4：分析管道（知识图谱→趋势→架构→机会→报告）"""
    logger.info("=" * 60)
    logger.info("阶段 2/4: 深度分析")
    logger.info("=" * 60)

    articles = get_all_articles(limit=max_articles)
    if not articles:
        logger.warning("数据库中没有文章，请先运行采集")
        return {"error": "no_articles"}

    logger.info(f"分析 {len(articles)} 篇文章...")

    # 知识图谱
    logger.info("[1/4] 构建知识图谱...")
    t0 = time.time()
    kg_builder = KnowledgeGraphBuilder()
    graph_data = kg_builder.build_from_articles(articles)
    logger.info(f"  知识图谱完成: {graph_data['stats']['total_nodes']} 实体, "
                 f"{graph_data['stats']['total_edges']} 关系 ({time.time()-t0:.1f}s)")

    # 趋势分析
    logger.info("[2/4] 趋势分析...")
    t0 = time.time()
    trend_analyzer = TrendAnalyzer()
    trend_data = trend_analyzer.analyze(articles)
    logger.info(f"  趋势分析完成: {trend_data['stats']['total_keywords']} 关键词, "
                 f"{trend_data['stats']['emerging_count']} 新兴 ({time.time()-t0:.1f}s)")

    # 架构提取
    logger.info("[3/4] 架构提取...")
    t0 = time.time()
    arch_extractor = ArchitectureExtractor()
    arch_data = arch_extractor.extract(articles)
    logger.info(f"  架构提取完成: {arch_data['stats']['total_patterns']} 模式 "
                 f"({time.time()-t0:.1f}s)")

    # 机会识别
    logger.info("[4/4] AI 时代个人机会识别...")
    t0 = time.time()
    opp_finder = OpportunityFinder()
    opportunity_data = opp_finder.find(
        trend_data=trend_data,
        graph_data=graph_data,
        arch_data=arch_data,
        hot_topics=trend_data.get("hot_topics", []),
    )
    logger.info(f"  机会识别完成: {len(opportunity_data.get('opportunities', []))} 个机会 "
                 f"({time.time()-t0:.1f}s)")

    # 标记已分析
    mark_analyzed([a["id"] for a in articles if a.get("id")])

    logger.info("=" * 60)
    logger.info("阶段 3/4: 生成报告")
    logger.info("=" * 60)

    analysis_results = {
        "content_digest": {
            "by_source": get_stats()["by_source"],
            "hot_topics": trend_data.get("hot_topics", []),
        },
        "knowledge_graph": graph_data,
        "trend_report": trend_data,
        "architecture_map": arch_data,
        "industry_insight": {},
        "ai_opportunity": opportunity_data,
    }

    report_gen = ReportGenerator()
    reports = report_gen.generate_all(analysis_results)
    logger.info(f"报告生成完成: {len(reports)} 份")
    for name, path in reports.items():
        logger.info(f"  - {name}: {path}")

    return {
        "reports": reports,
        "stats": {
            "articles_analyzed": len(articles),
            "entities": graph_data["stats"]["total_nodes"],
            "relations": graph_data["stats"]["total_edges"],
            "trends": trend_data["stats"]["total_keywords"],
            "emerging": trend_data["stats"]["emerging_count"],
            "patterns": arch_data["stats"]["total_patterns"],
            "opportunities": len(opportunity_data.get("opportunities", [])),
        },
    }


def run_full_pipeline(source: str | None = None, max_articles: int = 300) -> dict:
    """运行完整管道：采集→分析→报告"""
    logger.info("启动 TechInsight 完整管道")
    collection_result = run_collection(source=source)
    analysis_result = run_analysis_pipeline(max_articles=max_articles)
    return {"collection": collection_result, "analysis": analysis_result}


def _save_all(articles: list) -> int:
    saved = 0
    for article in articles:
        try:
            save_article(article)
            saved += 1
        except Exception as e:
            logger.warning(f"保存失败 {article.url}: {e}")
    return saved
