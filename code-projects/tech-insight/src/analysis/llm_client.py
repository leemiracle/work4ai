"""LLM 客户端 - 统一封装多模型调用，支持 OpenAI 兼容接口"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

import requests

from ..config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI 兼容的 LLM 客户端（支持智谱GLM、OpenAI、月之暗面等）"""

    def __init__(self):
        cfg = Config.settings().get("llm", {})
        self.base_url = cfg.get("base_url", "").rstrip("/")
        self.api_key = cfg.get("api_key", "")
        self.model = cfg.get("model", "glm-4-flash")
        self.deep_model = cfg.get("deep_model", "glm-4")
        self.temperature = cfg.get("temperature", 0.3)
        self.max_tokens = cfg.get("max_tokens", 4096)
        self.interval = cfg.get("request_interval", 0.5)

    def _available(self) -> bool:
        if not self.base_url or not self.api_key:
            return False
        return True

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[dict] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """发送聊天请求，返回文本"""
        if not self._available():
            logger.warning("LLM 未配置（缺少 base_url 或 api_key），跳过分析")
            return ""

        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(3):
            try:
                if attempt == 0:
                    time.sleep(min(self.interval, 0.2))
                resp = requests.post(url, json=payload, headers=headers, timeout=45)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"LLM 请求失败 [{attempt+1}/3]: {e}")
                time.sleep(1.5 * (attempt + 1))
        logger.error("LLM 请求失败（重试耗尽）")
        return ""

    def chat_json(self, messages: list[dict], model: Optional[str] = None) -> dict | list:
        """请求并解析 JSON 响应"""
        text = self.chat(
            messages,
            model=model,
            response_format={"type": "json_object"},
        )
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}\n{text[:200]}")
                return {}

    def chat_json_array(self, prompt: str, system: str = "", model: Optional[str] = None) -> list[dict]:
        """请求返回 JSON 数组（某些模型不支持 json_object 返回数组）"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        text = self.chat(messages, model=model)
        if not text:
            return []
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                for key in ("data", "items", "results", "entities", "list"):
                    if key in result and isinstance(result[key], list):
                        return result[key]
                return [result]
            return []
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            logger.error(f"JSON 数组解析失败: {text[:200]}")
            return []

    def embed(self, texts: list[str]) -> list[list[float]]:
        """文本向量化"""
        cfg = Config.settings().get("embedding", {})
        base_url = cfg.get("base_url", self.base_url).rstrip("/")
        api_key = cfg.get("api_key", self.api_key)
        model = cfg.get("model", "embedding-3")
        if not base_url or not api_key:
            return []
        url = f"{base_url}/embeddings"
        payload = {"model": model, "input": texts}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.error(f"Embedding 请求失败: {e}")
            return []
