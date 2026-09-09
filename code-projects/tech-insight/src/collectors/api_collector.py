"""API 采集器 - 支持 InfoQ、掘金、V2EX、HackerNews 等 JSON API"""

from __future__ import annotations

import logging
from typing import Any

from ..storage.models import Article
from .base import BaseCollector

logger = logging.getLogger(__name__)


class APICollector(BaseCollector):
    """JSON API 采集器，按 source_key 分派到对应的解析器"""

    def collect(self) -> list[Article]:
        articles: list[Article] = []
        feeds = self.config.get("feeds", [])
        for feed_cfg in feeds:
            endpoint = feed_cfg["endpoint"]
            method = feed_cfg.get("method", "GET").upper()
            body = feed_cfg.get("body")
            category = feed_cfg.get("category", "")
            logger.info(f"[{self.name}] 采集 API: {endpoint}")
            resp = self._make_request(endpoint, method=method, json_body=body)
            if resp is None:
                continue
            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"[{self.name}] JSON 解析失败: {e}")
                continue
            parsed = self._dispatch_parse(data, category)
            logger.info(f"[{self.name}] API 解析到 {len(parsed)} 篇文章")
            articles.extend(parsed)
        return articles

    def _dispatch_parse(self, data: dict, category: str) -> list[Article]:
        parser = getattr(self, f"_parse_{self.source_key}", None)
        if parser:
            return parser(data, category)
        return self._parse_generic(data, category)

    # ==================== 各站点专用解析器 ====================

    def _parse_infoq(self, data: dict, category: str) -> list[Article]:
        articles: list[Article] = []
        items = data.get("data", {}).get("data", [])
        if not items:
            items = data.get("data", [])
        for item in items:
            uuid = item.get("uuid", "")
            title = item.get("article_title") or item.get("title", "")
            url = f"https://www.infoq.cn/article/{uuid}" if uuid else item.get("url", "")
            if not title or not url:
                continue
            article = self._create_article(
                title=title,
                url=url,
                uuid=uuid,
                summary=item.get("article_summary", ""),
                content=item.get("article_summary", ""),
                category=category,
                author=item.get("author_name", ""),
                author_id=item.get("author_id", ""),
                published_at=item.get("publish_time", ""),
                cover_image=item.get("article_cover", ""),
                view_count=item.get("view_count", 0),
            )
            articles.append(article)
        return articles

    def _parse_juejin(self, data: dict, category: str) -> list[Article]:
        articles: list[Article] = []
        items = data.get("data", [])
        for item in items:
            if item.get("type") != "article":
                continue
            info = item.get("article_info", {})
            aid = info.get("article_id", "")
            title = info.get("title", "")
            url = f"https://juejin.cn/post/{aid}" if aid else ""
            if not title or not url:
                continue
            user = item.get("author_user_info", {})
            article = self._create_article(
                title=title,
                url=url,
                uuid=aid,
                summary=info.get("brief_content", ""),
                content=info.get("brief_content", ""),
                category=category,
                author=user.get("user_name", ""),
                author_id=user.get("user_id", ""),
                published_at=str(info.get("ctime", "")),
                cover_image=info.get("cover_image", ""),
                view_count=item.get("article_info", {}).get("view_count", 0),
                like_count=item.get("article_info", {}).get("digg_count", 0),
                comment_count=item.get("article_info", {}).get("comment_count", 0),
            )
            articles.append(article)
        return articles

    def _parse_v2ex(self, data: list, category: str) -> list[Article]:
        articles: list[Article] = []
        if isinstance(data, list):
            for item in data:
                tid = item.get("id", "")
                title = item.get("title", "")
                url = item.get("url", f"https://www.v2ex.com/t/{tid}")
                if not title:
                    continue
                article = self._create_article(
                    title=title,
                    url=url,
                    uuid=str(tid),
                    summary=item.get("content", "")[:500],
                    content=item.get("content", ""),
                    category=category,
                    author=item.get("member", {}).get("username", ""),
                    published_at=str(item.get("created", "")),
                )
                articles.append(article)
        return articles

    def _parse_hackernews(self, data: list, category: str) -> list[Article]:
        """HackerNews 返回的是 ID 列表，需逐条请求详情"""
        articles: list[Article] = []
        detail_template = self.config.get(
            "detail_template", "https://hacker-news.firebaseio.com/v0/item/{id}.json"
        )
        ids = data[:20] if isinstance(data, list) else []
        for item_id in ids:
            detail_url = detail_template.format(id=item_id)
            resp = self._make_request(detail_url)
            if resp is None:
                continue
            try:
                item = resp.json()
            except Exception:
                continue
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={item_id}")
            if not title:
                continue
            article = self._create_article(
                title=title,
                url=url,
                uuid=str(item_id),
                summary=item.get("text", "") or item.get("title", ""),
                content=item.get("text", "") or item.get("title", ""),
                category=category,
                author=item.get("by", ""),
                published_at=str(item.get("time", "")),
                view_count=item.get("score", 0),
                comment_count=item.get("descendants", 0),
                language="en",
            )
            articles.append(article)
        return articles

    def _parse_devto(self, data: list, category: str) -> list[Article]:
        articles: list[Article] = []
        if isinstance(data, list):
            for item in data:
                title = item.get("title", "")
                url = item.get("url", "")
                if not title or not url:
                    continue
                article = self._create_article(
                    title=title,
                    url=url,
                    uuid=str(item.get("id", "")),
                    summary=item.get("description", ""),
                    content=item.get("description", ""),
                    category=category,
                    author=item.get("user", {}).get("username", ""),
                    published_at=item.get("published_at", ""),
                    cover_image=item.get("cover_image", ""),
                    view_count=item.get("page_views_count", 0),
                    like_count=item.get("positive_reactions_count", 0),
                    comment_count=item.get("comments_count", 0),
                    tags=item.get("tag_list", []),
                    language="en",
                )
                articles.append(article)
        return articles

    def _parse_generic(self, data: Any, category: str) -> list[Article]:
        """通用兜底解析：尝试多种常见结构"""
        articles: list[Article] = []
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("data", "items", "results", "articles", "list"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            if not items and isinstance(data.get("data"), dict):
                for key in ("data", "items", "list", "results"):
                    if key in data["data"] and isinstance(data["data"][key], list):
                        items = data["data"][key]
                        break
        for item in items:
            if not isinstance(item, dict):
                continue
            title = (
                item.get("title")
                or item.get("article_title")
                or item.get("name")
                or ""
            )
            url = item.get("url") or item.get("link") or ""
            if not title or not url:
                continue
            article = self._create_article(
                title=title,
                url=url,
                summary=item.get("summary", item.get("description", "")),
                content=item.get("content", item.get("summary", "")),
                category=category,
                author=item.get("author", item.get("author_name", "")),
                published_at=item.get("published_at", item.get("publish_time", "")),
            )
            articles.append(article)
        return articles
