#!/usr/bin/env python3
"""
tinyllm/serve.py — OpenAI 兼容 API 服务

参照：vLLM OpenAI server / text-generation-inference (TGI) / Ollama
csdiy 对应：tinyinfer + tinyhttpd + tinyrpc + AI核心

端点：
  POST /v1/chat/completions  — 对话补全（OpenAI 兼容）
  POST /v1/completions       — 文本补全
  GET  /v1/models            — 模型列表
  GET  /health               — 健康检查
"""
import asyncio, json, time, uuid, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyllm.model import GPT
from tinyllm.infer import LLMInference

class TinyLLMServer:
    """OpenAI 兼容 API（参照 vLLM entrypoints/openai/api_server.py）"""
    def __init__(self, model=None):
        self.model = model or GPT(vocab_size=256, d_model=32, n_heads=4, n_layers=2, max_seq=64)
        self.engine = LLMInference(self.model)
        self.requests = 0; self.start_time = time.time()

    async def handle(self, reader, writer):
        """HTTP 请求处理"""
        client = writer.get_extra_info("peername")
        req_line = await reader.readline()
        if not req_line: writer.close(); return
        method, path, _ = req_line.decode().strip().split(" ", 2)
        headers = {}
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""): break
            if b":" in line:
                k, v = line.decode().split(":", 1); headers[k.strip().lower()] = v.strip()
        body = b""
        if "content-length" in headers:
            body = await reader.readexactly(int(headers["content-length"]))
        self.requests += 1
        # 路由
        if method == "POST" and "/v1/chat/completions" in path:
            resp = self._chat_completions(body)
        elif method == "POST" and "/v1/completions" in path:
            resp = self._completions(body)
        elif method == "GET" and path == "/v1/models":
            resp = self._list_models()
        elif method == "GET" and path == "/health":
            resp = json.dumps({"status": "ok", "model": "tinyllm", "uptime": time.time() - self.start_time})
        else:
            resp = json.dumps({"error": "Not found"})
        status_code = 200
        http_resp = (f"HTTP/1.1 {status_code} OK\r\nContent-Type: application/json\r\n"
                     f"Content-Length: {len(resp)}\r\nConnection: close\r\n\r\n{resp}")
        writer.write(http_resp.encode()); await writer.drain(); writer.close()

    def _chat_completions(self, body):
        """POST /v1/chat/completions（OpenAI 格式）"""
        data = json.loads(body) if body else {}
        # 提取最后一条消息作为 prompt
        messages = data.get("messages", [])
        prompt_text = messages[-1]["content"] if messages else "hello"
        prompt_ids = [ord(c) % self.model.vocab_size for c in prompt_text[:32]]
        # 生成
        max_tokens = data.get("max_tokens", 20)
        strategy = data.get("temperature", 1.0) > 0.5 and "greedy" or "greedy"
        tokens, stats = self.engine.generate(prompt_ids, max_tokens=max_tokens, strategy=strategy)
        # 解码（简化版：token → char）
        output_text = "".join(chr(t % 128) if t < 128 else "?" for t in tokens[len(prompt_ids):])
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data.get("model", "tinyllm-1b"),
            "choices": [{"index": 0, "message": {"role": "assistant", "content": output_text},
                        "finish_reason": "stop"}],
            "usage": {"prompt_tokens": stats["prompt_tokens"], "completion_tokens": stats["generated_tokens"],
                      "total_tokens": stats["prompt_tokens"] + stats["generated_tokens"]},
        }
        return json.dumps(response)

    def _completions(self, body):
        data = json.loads(body) if body else {}
        prompt = data.get("prompt", "hello")
        prompt_ids = [ord(c) % self.model.vocab_size for c in prompt[:32]]
        max_tokens = data.get("max_tokens", 20)
        tokens, stats = self.engine.generate(prompt_ids, max_tokens=max_tokens)
        output = "".join(chr(t % 128) if t < 128 else "?" for t in tokens[len(prompt_ids):])
        response = {
            "id": f"cmpl-{uuid.uuid4().hex[:8]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "tinyllm",
            "choices": [{"text": output, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": stats["prompt_tokens"], "completion_tokens": stats["generated_tokens"],
                      "total_tokens": stats["prompt_tokens"] + stats["generated_tokens"]},
        }
        return json.dumps(response)

    def _list_models(self):
        return json.dumps({"object": "list", "data": [
            {"id": "tinyllm", "object": "model", "created": int(self.start_time),
             "owned_by": "csdiy", "permission": []}
        ]})

async def main():
    print("tinyllm — OpenAI 兼容 API（参照 vLLM/TGI）\n")
    server = TinyLLMServer()
    srv = await asyncio.start_server(server.handle, "0.0.0.0", 8000)
    addr = srv.sockets[0].getsockname()
    print(f"  tinyllm serving on http://{addr[0]}:{addr[1]}")
    print(f"  模型参数: ~{server.model.param_count():,}")
    print(f"\n  测试:")
    print(f"    curl http://localhost:8000/v1/chat/completions \\")
    print(f"      -H 'Content-Type: application/json' \\")
    print(f"      -d '{{\"messages\":[{{\"role\":\"user\",\"content\":\"hello\"}}]}}'")
    print(f"\n  兼容: OpenAI Python SDK / LangChain / 任何 OpenAI 客户端")
    async with srv:
        await srv.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
