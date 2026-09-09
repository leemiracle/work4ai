"""LLM Service - Interface to various language models."""

from typing import List, Dict, Any, Optional, AsyncIterator
import json
import httpx
from .config import AISettings


class LLMService:
    """Unified interface for LLM providers."""

    def __init__(self, settings: Optional[AISettings] = None):
        self.settings = settings or AISettings()
        self._configure_provider()

    def _configure_provider(self):
        """Configure the selected LLM provider."""
        if self.settings.LLM_PROVIDER == "openai":
            self._configure_openai()
        elif self.settings.LLM_PROVIDER == "anthropic":
            self._configure_anthropic()
        elif self.settings.LLM_PROVIDER == "ollama":
            self._configure_ollama()

    def _configure_openai(self):
        """Configure OpenAI client."""
        if not self.settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    def _configure_anthropic(self):
        """Configure Anthropic client."""
        if not self.settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

    def _configure_ollama(self):
        """Configure Ollama client."""
        self.base_url = self.settings.OLLAMA_BASE_URL
        self.headers = {"Content-Type": "application/json"}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Send chat completion request."""

        model = model or self.settings.DEFAULT_MODEL
        temperature = temperature if temperature is not None else self.settings.TEMPERATURE
        max_tokens = max_tokens or self.settings.MAX_TOKENS

        if self.settings.LLM_PROVIDER == "openai":
            return await self._chat_openai(messages, model, temperature, max_tokens, stream)
        elif self.settings.LLM_PROVIDER == "anthropic":
            return await self._chat_anthropic(messages, model, temperature, max_tokens, stream)
        elif self.settings.LLM_PROVIDER == "ollama":
            return await self._chat_ollama(messages, model, temperature, max_tokens, stream)
        else:
            raise ValueError(f"Unsupported provider: {self.settings.LLM_PROVIDER}")

    async def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str | AsyncIterator[str]:
        """OpenAI chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            if stream:
                return self._stream_openai(response)
            else:
                data = response.json()
                return data["choices"][0]["message"]["content"]

    async def _stream_openai(self, response):
        """Stream OpenAI responses."""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
                except json.JSONDecodeError:
                    continue

    async def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Anthropic chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.text}")

            data = response.json()
            return data["content"][0]["text"]

    async def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str | AsyncIterator[str]:
        """Ollama chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")

            if stream:
                return self._stream_ollama(response)
            else:
                data = response.json()
                return data["message"]["content"]

    async def _stream_ollama(self, response):
        """Stream Ollama responses."""
        async for line in response.aiter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
                except json.JSONDecodeError:
                    continue

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""

        if self.settings.EMBEDDING_PROVIDER == "openai":
            return await self._embed_openai(text)
        elif self.settings.EMBEDDING_PROVIDER == "ollama":
            return await self._embed_ollama(text)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.settings.EMBEDDING_PROVIDER}")

    async def _embed_openai(self, text: str) -> List[float]:
        """OpenAI embedding."""
        payload = {
            "model": "text-embedding-ada-002",
            "input": text
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI embedding error: {response.text}")

            data = response.json()
            return data["data"][0]["embedding"]

    async def _embed_ollama(self, text: str) -> List[float]:
        """Ollama embedding."""
        payload = {
            "model": self.settings.EMBEDDING_MODEL,
            "input": text
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embed",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Ollama embedding error: {response.text}")

            data = response.json()
            return data["embeddings"][0]

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough estimation: 1 token ≈ 4 characters for English
        return len(text) // 4
