"""Web 爬虫采集器 - 用于无 RSS/API 的站点，基于 requests + selectolax"""

from __future__ import annotations

import logging
import re
from typing import Any

from ..storage.models import Article
from .base import BaseCollector

logger = logging.getLogger(__name__)


class WebCollector(BaseCollector):
    """HTML 页面采集器"""

    def collect(self) -> list[Article]:
        articles: list[Article] = []
        feeds = self.config.get("feeds", [])
        for feed_cfg in feeds:
            endpoint = feed_cfg["endpoint"]
            category = feed_cfg.get("category", "")
            logger.info(f"[{self.name}] 采集网页: {endpoint}")
            resp = self._make_request(endpoint)
            if resp is None:
                continue
            parsed = self._dispatch_parse(resp.text, endpoint, category)
            logger.info(f"[{self.name}] 网页解析到 {len(parsed)} 篇文章")
            articles.extend(parsed)
        return articles

    def _dispatch_parse(self, html: str, base_url: str, category: str) -> list[Article]:
        parser = getattr(self, f"_parse_{self.source_key}", None)
        if parser:
            return parser(html, base_url, category)
        return self._parse_rss_as_web(html, base_url, category)

    def _parse_rss_as_web(self, content: str, base_url: str, category: str) -> list[Article]:
        """很多 web 类型站点实际提供了 RSS XML，用 feedparser 解析"""
        from .rss_collector import RSSCollector

        rss = RSSCollector(self.source_key, self.config)
        return rss._parse_feed(content.encode("utf-8"), category)

    def _parse_generic_html(self, html: str, base_url: str, category: str,
                            item_selector: str = "article",
                            title_selector: str = "h2 a, h1 a, .title a, .article-title a") -> list[Article]:
        """通用 HTML 解析（需要 selectolax）"""
        try:
            from selectolax.parser import HTMLParser
        except ImportError:
            logger.warning("selectolax 未安装，跳过 HTML 解析")
            return []

        tree = HTMLParser(html)
        articles: list[Article] = []
        for node in tree.css(item_selector):
            title_node = node.css_first(title_selector)
            if not title_node:
                continue
            title = title_node.text(strip=True)
            link = title_node.attributes.get("href", "")
            if not title or not link:
                continue
            if link.startswith("/"):
                from urllib.parse import urljoin
                link = urljoin(base_url, link)
            summary_node = node.css_first("p, .summary, .description, .excerpt")
            summary = summary_node.text(strip=True) if summary_node else ""
            article = self._create_article(
                title=title,
                url=link,
                summary=summary,
                content=summary,
                category=category,
            )
            articles.append(article)
        return articles

    @staticmethod
    def _strip_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
