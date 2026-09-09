"""RSS Feed 采集器"""

from __future__ import annotations

import logging
from typing import Any

from ..storage.models import Article
from .base import BaseCollector

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """RSS/Atom Feed 采集器"""

    def collect(self) -> list[Article]:
        articles: list[Article] = []
        feeds = self.config.get("feeds", [])
        for feed_cfg in feeds:
            endpoint = feed_cfg["endpoint"]
            category = feed_cfg.get("category", "")
            logger.info(f"[{self.name}] 采集 RSS: {endpoint}")
            resp = self._make_request(endpoint)
            if resp is None:
                continue
            items = self._parse_feed(resp.content, category)
            logger.info(f"[{self.name}] RSS 解析到 {len(items)} 篇文章")
            articles.extend(items)
        return articles

    def _parse_feed(self, content: bytes, category: str) -> list[Article]:
        """解析 RSS/Atom，优先用 feedparser，否则 fallback 到 xml.etree"""
        try:
            import feedparser

            parsed = feedparser.parse(content)
            articles = []
            entries = parsed.entries or []
            for entry in entries:
                link = str(entry.get("link", "") or "")
                title = str(entry.get("title", "") or "")
                if not link or not title:
                    continue
                summary = str(entry.get("summary", "") or "")
                content_text = ""
                if entry.get("content"):
                    content_text = str(entry.content[0].get("value", "") or "")
                elif summary:
                    content_text = summary
                author = ""
                if entry.get("author"):
                    author = str(entry.author)
                elif entry.get("authors"):
                    author = str(entry.authors[0].get("name", ""))
                published = str(entry.get("published", entry.get("updated", "")) or "")
                tags = [str(t.get("term", "")) for t in entry.get("tags", []) if t.get("term")]
                uuid = ""
                if "infoq.cn" in link:
                    import re
                    m = re.search(r"/article/([a-zA-Z0-9]+)", link)
                    if m:
                        uuid = m.group(1)
                article = self._create_article(
                    title=title,
                    url=link,
                    uuid=uuid,
                    summary=self._strip_html(summary)[:500],
                    content=self._strip_html(content_text),
                    category=category,
                    author=author,
                    published_at=published,
                    tags=tags,
                )
                articles.append(article)
            return articles
        except ImportError:
            logger.warning("feedparser 未安装，使用 fallback XML 解析")
            return self._parse_xml_fallback(content, category)

    def _parse_xml_fallback(self, content: bytes, category: str) -> list[Article]:
        import xml.etree.ElementTree as ET

        articles: list[Article] = []
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            logger.error(f"XML 解析失败: {e}")
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//atom:entry", ns)

        for item in items:
            def _find(tag: str) -> str:
                el = item.find(tag)
                if el is None:
                    el = item.find(f"atom:{tag}", ns)
                return el.text.strip() if el is not None and el.text else ""

            title = _find("title")
            link = _find("link")
            if not link:
                link_el = item.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
            if not title or not link:
                continue
            summary = _find("description") or _find("summary")
            published = _find("pubDate") or _find("published") or _find("updated")
            author = _find("author") or _find("dc:creator")
            article = self._create_article(
                title=title,
                url=link,
                summary=self._strip_html(summary)[:500],
                content=self._strip_html(summary),
                category=category,
                author=author,
                published_at=published,
            )
            articles.append(article)
        return articles

    @staticmethod
    def _strip_html(text: str) -> str:
        import re

        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
