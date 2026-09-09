"""内容增强器 - 获取文章全文（InfoQ详情页、通用网页正文提取）"""

from __future__ import annotations

import logging
import re
from typing import Optional

import requests

from ..config import Config

logger = logging.getLogger(__name__)


class ContentEnricher:
    """获取文章全文，增强摘要级内容"""

    def __init__(self):
        self.collection_cfg = Config.sources().get("collection", {})
        self.headers = {
            "User-Agent": self.collection_cfg.get("user_agent", "Mozilla/5.0"),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    def enrich_infoq(self, uuid: str) -> str:
        """通过 InfoQ API 获取文章全文"""
        if not uuid:
            return ""
        endpoint = "https://www.infoq.cn/public/v1/article/getDetail"
        headers = {
            **self.headers,
            "Referer": "https://www.infoq.cn/",
            "Origin": "https://www.infoq.cn",
            "Content-Type": "application/json",
        }
        try:
            import time
            time.sleep(self.collection_cfg.get("default_delay_seconds", 2))
            resp = requests.post(
                endpoint,
                json={"uuid": uuid},
                headers=headers,
                timeout=self.collection_cfg.get("timeout_seconds", 15),
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            content = data.get("content", "")
            if content:
                return self._strip_html(content)
            return data.get("summary", "")
        except Exception as e:
            logger.debug(f"InfoQ详情获取失败 {uuid}: {e}")
            return ""

    def enrich_webpage(self, url: str) -> str:
        """通用网页正文提取（selectolax）"""
        try:
            import time
            time.sleep(self.collection_cfg.get("default_delay_seconds", 2))
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return self._extract_main_text(resp.text)
        except Exception as e:
            logger.debug(f"网页正文提取失败 {url}: {e}")
            return ""

    def _extract_main_text(self, html: str) -> str:
        """从HTML提取正文"""
        try:
            from selectolax.parser import HTMLParser
        except ImportError:
            return self._strip_html(html)[:2000]

        tree = HTMLParser(html)
        for selector in ["article", ".article-content", ".post-content",
                         ".entry-content", "#article", ".content", "main"]:
            node = tree.css_first(selector)
            if node:
                text = node.text(separator="\n", strip=True)
                if len(text) > 100:
                    return text[:5000]
        paragraphs = [p.text(strip=True) for p in tree.css("p") if p.text(strip=True)]
        if paragraphs:
            return "\n".join(paragraphs)[:5000]
        return self._strip_html(html)[:2000]

    @staticmethod
    def _strip_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&[a-z]+;", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def enrich_article(self, article) -> str:
        """根据文章来源增强内容"""
        source = article.source
        if source == "infoq" and article.uuid:
            return self.enrich_infoq(article.uuid)
        if len(article.content) < 200 and article.url:
            return self.enrich_webpage(article.url)
        return ""
