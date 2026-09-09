"""采集器基类 - 定义统一接口、限流、重试、合规检查"""

from __future__ import annotations

import abc
import hashlib
import logging
import time
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from ..config import Config
from ..storage.models import Article

logger = logging.getLogger(__name__)


class BaseCollector(abc.ABC):
    """所有采集器的抽象基类"""

    def __init__(self, source_key: str, source_config: dict):
        self.source_key = source_key
        self.config = source_config
        self.name = source_config.get("name", source_key)
        self.url = source_config.get("url", "")
        self.collection_cfg = Config.sources().get("collection", {})
        self._robots_cache: Optional[RobotFileParser] = None
        self._robots_checked = False

    @abc.abstractmethod
    def collect(self) -> list[Article]:
        """执行采集，返回文章列表"""
        ...

    @property
    def user_agent(self) -> str:
        return self.collection_cfg.get(
            "user_agent", "TechInsight-Research-Bot/1.0"
        )

    @property
    def delay(self) -> float:
        return self.collection_cfg.get("default_delay_seconds", 3)

    def can_fetch(self, url: str) -> bool:
        """检查 robots.txt 是否允许抓取"""
        if not self.collection_cfg.get("respect_robots_txt", True):
            return True
        if self._robots_cache is None:
            parsed = urlparse(self.url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = RobotFileParser()
            try:
                rp.set_url(robots_url)
                rp.read()
                self._robots_cache = rp
            except Exception as e:
                logger.warning(f"无法读取 robots.txt ({robots_url}): {e}")
                self._robots_cache = None
        if self._robots_cache is None:
            return True
        return self._robots_cache.can_fetch(self.user_agent, url)

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        json_body: Optional[dict] = None,
        headers: Optional[dict] = None,
        retries: Optional[int] = None,
    ) -> Optional[requests.Response]:
        """带重试和限流的 HTTP 请求"""
        retries = retries or self.collection_cfg.get("max_retries", 3)
        timeout = self.collection_cfg.get("timeout_seconds", 30)
        default_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        source_headers = self.config.get("headers", {})
        if source_headers:
            default_headers.update(source_headers)
        if headers:
            default_headers.update(headers)

        for attempt in range(retries):
            try:
                time.sleep(self.delay)
                resp = requests.request(
                    method=method,
                    url=url,
                    json=json_body,
                    headers=default_headers,
                    timeout=timeout,
                )
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                logger.warning(
                    f"请求失败 [{attempt+1}/{retries}] {url}: {e}"
                )
                time.sleep(self.delay * (attempt + 1))
        logger.error(f"采集失败（重试耗尽）: {url}")
        return None

    def _create_article(
        self,
        title: str,
        url: str,
        **kwargs: Any,
    ) -> Article:
        """创建标准 Article 对象"""
        article_id = hashlib.md5(f"{self.source_key}:{url}".encode()).hexdigest()
        defaults = {
            "id": article_id,
            "source": self.source_key,
            "source_name": self.name,
            "title": title,
            "url": url,
            "collected_at": datetime.now().isoformat(),
            "language": "zh-CN",
        }
        defaults.update(kwargs)
        return Article(**defaults)
