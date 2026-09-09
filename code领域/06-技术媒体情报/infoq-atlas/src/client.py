"""InfoQ CN public API 客户端：带重试、节流、原始落盘。

已确认的端点（均 POST，JSON）：
- topic/getList   {}                          -> 全部 topic 树（含子 topic）
- article/getList {id,size,type?:1,score?}    -> 按 topic 的文章列表（score 为向后游标）
- article/getDetail {uuid}                    -> 文章元数据 + content_url
正文：GET content_url -> ProseMirror JSON {"type":"doc","content":[...]}
"""
from __future__ import annotations
import json
import time
import random
import urllib.request
import urllib.error
from typing import Any

from . import config as C


class InfoQClient:
    def __init__(self):
        self._headers = {
            "User-Agent": C.USER_AGENT,
            "Content-Type": "application/json",
            "Referer": f"{C.SITE}/",
            "Origin": C.SITE,
            "Accept": "application/json, text/plain, */*",
        }

    # ---- low level --------------------------------------------------------
    def _post(self, path: str, body: dict, delay: float) -> Any:
        url = C.API_BASE + path
        data = json.dumps(body).encode("utf-8")
        last_err = None
        for attempt in range(C.MAX_RETRIES):
            try:
                req = urllib.request.Request(
                    url, data=data, headers=self._headers, method="POST")
                with urllib.request.urlopen(req, timeout=C.HTTP_TIMEOUT) as r:
                    time.sleep(delay + random.uniform(0, 0.08))
                    return json.loads(r.read().decode("utf-8"))
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, ConnectionResetError) as e:
                last_err = e
                wait = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(wait)
        raise RuntimeError(f"POST {path} failed after {C.MAX_RETRIES}: {last_err}")

    def _get(self, url: str, delay: float, referer: str = C.SITE + "/") -> bytes:
        hdr = dict(self._headers)
        hdr.pop("Content-Type")
        hdr.pop("Origin")
        hdr["Referer"] = referer
        last_err = None
        for attempt in range(C.MAX_RETRIES):
            try:
                req = urllib.request.Request(url, headers=hdr, method="GET")
                with urllib.request.urlopen(req, timeout=C.HTTP_TIMEOUT) as r:
                    raw = r.read()
                    time.sleep(delay + random.uniform(0, 0.05))
                    return raw
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, ConnectionResetError) as e:
                last_err = e
                time.sleep((2 ** attempt) + random.uniform(0, 0.5))
        raise RuntimeError(f"GET {url} failed: {last_err}")

    # ---- high level -------------------------------------------------------
    def get_topics(self) -> list[dict]:
        r = self._post("topic/getList", {}, delay=0.3)
        return r.get("data", []) or []

    def get_article_list(self, topic_id: int, size: int = C.LIST_PAGE_SIZE,
                         score: int | None = None) -> list[dict]:
        body: dict[str, Any] = {"id": int(topic_id), "size": int(size)}
        if score is not None:
            body["score"] = int(score)
        r = self._post("article/getList", body, delay=C.LIST_DELAY)
        return r.get("data", []) or []

    def get_article_detail(self, uuid: str) -> dict:
        r = self._post("article/getDetail", {"uuid": uuid}, delay=C.DETAIL_DELAY)
        return r.get("data", {}) or {}

    def get_article_via_ssr(self, uuid: str) -> dict:
        """绕过 detail API（常被 451 限流）：抓 /article/{uuid} HTML，
        从中正则提取 content_url 与关键元数据。返回 dict。"""
        import re as _re
        url = f"{C.SITE}/article/{uuid}"
        html = self._get(url, delay=0.35,
                         referer=f"{C.SITE}/").decode("utf-8", "ignore")
        out: dict[str, Any] = {"uuid": uuid}
        m = _re.search(
            r'(https://[^\s"\'\\]+geekbang\.org/resource/article/'
            r'[^\s"\'\\]+content\.json[^\s"\'\\]*)', html)
        if m:
            # HTML 里可能有转义 \/ ，还原
            out["content_url"] = m.group(1).replace("\\/", "/")
        for field, pat in [
            ("article_title", r'"article_title"\s*:\s*"((?:[^"\\]|\\.)*)"'),
            ("article_summary", r'"article_summary"\s*:\s*"((?:[^"\\]|\\.)*)"'),
            ("publish_time", r'"publish_time"\s*:\s*(\d+)'),
            ("word_count", r'"word_count"\s*:\s*(\d+)'),
        ]:
            mm = _re.search(pat, html)
            if mm:
                out[field] = mm.group(1).encode().decode("unicode_escape") \
                    if field.startswith("article_") else int(mm.group(1))
        return out

    def get_article_content(self, content_url: str,
                            referer: str = C.SITE + "/") -> Any:
        raw = self._get(content_url, delay=C.CONTENT_DELAY, referer=referer)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {"type": "raw", "content": raw.decode("utf-8", "ignore")}


def crawl_topic_articles(client: InfoQClient, topic_id: int,
                         max_pages: int | None = None,
                         seen: set[str] | None = None) -> list[dict]:
    """穷尽某个 topic 的全部文章（游标分页 + 去重）。返回文章列表项。"""
    if seen is None:
        seen = set()
    out: list[dict] = []
    score: int | None = None
    pages = 0
    while True:
        page = client.get_article_list(topic_id, size=C.LIST_PAGE_SIZE, score=score)
        pages += 1
        if not page:
            break
        new = []
        for a in page:
            aid = str(a.get("aid") or a.get("aidint") or a.get("uuid"))
            if not aid or aid in seen:
                continue
            seen.add(aid)
            new.append(a)
        out.extend(new)
        # 推进游标：用最后一条的 score/publish_time
        last = page[-1]
        score = int(last.get("score") or last.get("publish_time") or 0)
        if not new:
            # 本页全是已见（游标已到尽头仍重复）
            break
        if max_pages and pages >= max_pages:
            break
    return out
