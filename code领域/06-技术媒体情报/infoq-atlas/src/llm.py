"""智谱 Z.AI (BigModel) GLM 客户端 —— OpenAI 兼容。

key 从 ~/.config/opencode/opencode.json 的 zai-mcp-server.env 读取（不硬编码）。
支持 chat completions（glm-4-flash 快速 / glm-4 高质量）。
"""
from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from typing import Any

API_BASE = "https://open.bigmodel.cn/api/paas/v4"
_DEFAULT_MODEL = os.environ.get("GLM_MODEL", "glm-4-flash")
_key_cache: str | None = None


def get_key() -> str:
    global _key_cache
    if _key_cache:
        return _key_cache
    for path in ["~/.config/opencode/opencode.json",
                 os.path.expanduser("~/.config/opencode/opencode.json")]:
        p = os.path.expanduser(path)
        if os.path.exists(p):
            try:
                d = json.load(open(p))
                k = d["mcp"]["zai-mcp-server"]["environment"]["Z_AI_API_KEY"]
                _key_cache = k
                return k
            except Exception:
                pass
    k = os.environ.get("Z_AI_API_KEY", "")
    _key_cache = k
    return k


def chat(messages: list[dict], model: str = _DEFAULT_MODEL,
         temperature: float = 0.2, max_tokens: int = 700,
         retries: int = 3, timeout: int = 60) -> str:
    key = get_key()
    if not key:
        raise RuntimeError("无 Z_AI_API_KEY")
    body = {"model": model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens}
    data = json.dumps(body).encode("utf-8")
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                API_BASE + "/chat/completions", data=data,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read().decode("utf-8"))
                return resp["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, ConnectionResetError) as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GLM chat 失败: {last}")


def _lenient_parse(txt: str) -> Any:
    """容错解析（应对推理模型截断/夹带说明文本）。"""
    import re
    # 截取首个 { 起
    s = txt.find("{")
    if s < 0:
        return {}
    chunk = txt[s:]
    # 尝试直接解析（若有完整 }）
    e = chunk.rfind("}")
    if e >= 0:
        try:
            return json.loads(chunk[:e + 1])
        except json.JSONDecodeError:
            pass
    # 截断修复：逐层补全 ] 和 }
    out = {"summary": "", "concepts": [], "triples": []}
    m = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', chunk)
    if m:
        out["summary"] = m.group(1).encode().decode("unicode_escape", "ignore")
    cm = re.search(r'"concepts"\s*:\s*\[(.*?)\]', chunk, re.S)
    if cm:
        out["concepts"] = re.findall(r'"((?:[^"\\]|\\.)*)"', cm.group(1))
    tm = re.search(r'"triples"\s*:\s*\[(.*?)\]', chunk, re.S)
    if tm:
        # 每个 triple 是 ["a","b","c"]
        for tr in re.finditer(r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]', tm.group(1)):
            out["triples"].append([tr.group(1), tr.group(2), tr.group(3)])
    return out


def chat_json(messages: list[dict], model: str = _DEFAULT_MODEL,
              **kw) -> Any:
    """要求模型返回 JSON，容错解析（去围栏/截断修复/正则回退）。"""
    txt = chat(messages, model=model, **kw)
    txt = txt.strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1]
        if txt.lower().startswith("json"):
            txt = txt[4:]
    txt = txt.strip()
    # 找首个 { 到末尾 }
    start = txt.find("{")
    end = txt.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(txt[start:end + 1])
        except json.JSONDecodeError:
            pass
    return _lenient_parse(txt)


if __name__ == "__main__":
    print(chat([{"role": "user", "content": "用一句话介绍 InfoQ"}]))
