"""采集器工厂 - 根据 source type 创建对应采集器"""

from __future__ import annotations

import logging

from ..config import Config
from ..storage.models import Article
from .api_collector import APICollector
from .base import BaseCollector
from .rss_collector import RSSCollector
from .web_collector import WebCollector

logger = logging.getLogger(__name__)

_COLLECTOR_MAP: dict[str, type[BaseCollector]] = {
    "rss": RSSCollector,
    "api": APICollector,
    "web": WebCollector,
}


def create_collector(source_key: str) -> BaseCollector:
    sources = Config.sources()["sources"]
    if source_key not in sources:
        raise ValueError(f"未知数据源: {source_key}")
    cfg = sources[source_key]
    source_type = cfg.get("type", "web")
    collector_cls = _COLLECTOR_MAP.get(source_type, WebCollector)
    return collector_cls(source_key, cfg)


def collect_from(source_key: str) -> list[Article]:
    """从单个源采集"""
    collector = create_collector(source_key)
    return collector.collect()


def collect_all(priority: int | None = None) -> dict[str, list[Article]]:
    """从所有源采集，可按优先级过滤"""
    sources = Config.sources()["sources"]
    results: dict[str, list[Article]] = {}
    for key, cfg in sources.items():
        if priority is not None and cfg.get("priority", 5) > priority:
            continue
        try:
            articles = collect_from(key)
            results[key] = articles
            logger.info(f"[{key}] 采集完成: {len(articles)} 篇")
        except Exception as e:
            logger.error(f"[{key}] 采集异常: {e}")
            results[key] = []
    return results


def get_all_source_keys() -> list[str]:
    return list(Config.sources()["sources"].keys())
