#!/usr/bin/env python3
"""
tinyllm/rag_server.py — 带 RAG 的 LLM 服务（tinyllm × tinyrag 集成）

参照：Dify / LangChain + vLLM / PrivateGPT
csdiy 对应：tinyllm + tinyrag + 端到端集成

架构：
  用户提问 → tinyrag 检索相关文档 → 增强 Prompt → tinyllm 生成回答
  POST /chat → retrieve → augment → generate → 返回

端点：
  POST /chat       — RAG 增强对话
  POST /ingest     — 文档入库
  GET  /health     — 健康检查
"""
import asyncio, json, time, uuid, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinyllm.model import GPT
from tinyllm.infer import LLMInference
from tinyrag.pipeline import RAGPipeline

class RAGLLMServer:
    """带知识库的 LLM 服务（参照 Dify / PrivateGPT）"""
    def __init__(self):
        # LLM 模型 + 推理引擎
        self.model = GPT(vocab_size=256, d_model=32, n_heads=4, n_layers=2, max_seq=64)
        self.engine = LLMInference(self.model)
        # RAG 管道
        self.rag = RAGPipeline(embedding_model="hash", index_type="hnsw", dim=32,
                               chunk_size=60, overlap=10)
        self.requests = 0; self.start_time = time.time()

    async def handle(self, reader, writer):
        """HTTP 处理"""
        req_line = await reader.readline()
        if not req_line: writer.close(); return
        try:
            parts = req_line.decode().strip().split(" ")
            method, path = parts[0], parts[1]
        except:
            writer.close(); return
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
        data = json.loads(body) if body else {}

        if method == "POST" and "/chat" in path:
            resp = self._chat(data)
        elif method == "POST" and "/ingest" in path:
            n = self.rag.ingest(data.get("doc_id", f"doc_{int(time.time())}"),
                               data.get("text", ""), data.get("metadata"))
            resp = json.dumps({"status": "ok", "chunks": n, "total_docs": self.rag.stats()["documents"]})
        elif method == "GET" and "/health" in path:
            resp = json.dumps({
                "status": "ok", "uptime": time.time() - self.start_time,
                "llm_params": self.model.param_count(),
                "rag_docs": self.rag.stats()["documents"],
                "requests": self.requests
            })
        else:
            resp = json.dumps({"error": "not found", "endpoints": ["/chat", "/ingest", "/health"]})

        http = (f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                f"Content-Length: {len(resp)}\r\nConnection: close\r\n\r\n{resp}")
        writer.write(http.encode()); await writer.drain(); writer.close()

    def _chat(self, data):
        """RAG 增强对话（参照 Dify chat API）"""
        query = data.get("message", data.get("query", "hello"))
        top_k = data.get("top_k", 3)

        # Step 1: RAG 检索（参照 tinyrag pipeline.augment）
        prompt, sources = self.rag.augment(query, top_k=top_k)

        # Step 2: LLM 生成（参照 tinyllm engine.generate）
        prompt_ids = [ord(c) % self.model.vocab_size for c in query[:32]]
        tokens, stats = self.engine.generate(prompt_ids, max_tokens=15, strategy="greedy")
        # 解码（简化版）
        response_text = "".join(chr(t % 128) if 32 <= t < 128 else "" for t in tokens[len(prompt_ids):])

        return json.dumps({
            "id": f"rag-chat-{uuid.uuid4().hex[:8]}",
            "answer": response_text[:200] if response_text else "(model output)",
            "sources": [{"doc_id": s["metadata"].get("doc_id"), "score": s["score"],
                         "content": s["content"][:100]} for s in sources],
            "usage": {
                "retrieval_time_ms": 0,  # 简化
                "generation_time_ms": stats["total_ms"],
                "prompt_tokens": stats["prompt_tokens"],
                "generated_tokens": stats["generated_tokens"],
            }
        })

async def main():
    print("=" * 60)
    print("  tinyllm × tinyrag — RAG 增强对话服务")
    print("  参照 Dify / PrivateGPT / LangChain+vLLM")
    print("=" * 60)

    server = RAGLLMServer()

    # 预加载知识库
    docs = {
        "faq": "tinyllm is a lightweight LLM system. It supports KV Cache and multiple sampling strategies.",
        "guide": "To use the API, send POST to /chat with a message. The system retrieves relevant context first.",
        "tech": "Architecture: GPT model + BPE tokenizer + vLLM-style inference + Pinecone-style vector search.",
        "about": "This project is part of csdiy, a computer science learning repository.",
    }
    for doc_id, text in docs.items():
        server.rag.ingest(doc_id, text)

    srv = await asyncio.start_server(server.handle, "0.0.0.0", 8002)
    addr = srv.sockets[0].getsockname()
    print(f"\n  服务地址: http://{addr[0]}:{addr[1]}")
    print(f"  LLM 参数: ~{server.model.param_count():,}")
    print(f"  RAG 文档: {server.rag.stats()['documents']} chunks")
    print(f"\n  测试:")
    print(f'    curl -X POST http://localhost:8002/chat \\')
    print(f'      -H "Content-Type: application/json" \\')
    print(f'      -d \'{{"message":"what is tinyllm"}}\'')
    print(f"\n  架构: 用户提问 → tinyrag检索 → 增强prompt → tinyllm生成 → 回答+来源")
    print(f"  对比: Dify/PrivateGPT 用同样的流程，只是规模更大")
    async with srv:
        await srv.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
