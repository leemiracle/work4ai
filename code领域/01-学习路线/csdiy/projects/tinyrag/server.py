#!/usr/bin/env python3
"""
tinyrag/server.py — RAG HTTP API

参照：LangChain Serve / Dify / FastAPI RAG
csdiy 对应：tinyhttpd + tinyrpc + tinyrag/pipeline

端点：
  POST /ingest     — 文档入库
  POST /query      — RAG 查询
  POST /search     — 纯向量搜索
  GET  /stats      — 索引统计
  GET  /health     — 健康检查
"""
import asyncio, json, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyrag.pipeline import RAGPipeline

class TinyRAGServer:
    def __init__(self):
        self.rag = RAGPipeline(embedding_model="hash", index_type="hnsw", dim=64)
        self.requests = 0; self.start_time = time.time()

    async def handle(self, reader, writer):
        req_line = await reader.readline()
        if not req_line: writer.close(); return
        try: method, path, _ = req_line.decode().strip().split(" ", 2)
        except: writer.close(); return
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
        # 路由
        if method == "POST" and "/ingest" in path:
            n = self.rag.ingest(data.get("doc_id", f"doc_{int(time.time())}"),
                               data.get("text", ""), data.get("metadata"))
            resp = json.dumps({"status": "ok", "chunks": n})
        elif method == "POST" and "/query" in path:
            prompt, results = self.rag.augment(data.get("query", ""), top_k=data.get("top_k", 3))
            resp = json.dumps({"prompt": prompt[:500], "sources": results,
                              "context_count": len(results)})
        elif method == "POST" and "/search" in path:
            results = self.rag.retrieve(data.get("query", ""), top_k=data.get("top_k", 5),
                                       filter=data.get("filter"))
            resp = json.dumps({"results": results, "count": len(results)})
        elif method == "GET" and "/stats" in path:
            resp = json.dumps(self.rag.stats())
        elif method == "GET" and "/health" in path:
            resp = json.dumps({"status": "ok", "uptime": time.time() - self.start_time,
                              "requests": self.requests})
        else:
            resp = json.dumps({"error": "not found", "endpoints": ["/ingest", "/query", "/search", "/stats", "/health"]})
        http = (f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                f"Content-Length: {len(resp)}\r\nConnection: close\r\n\r\n{resp}")
        writer.write(http.encode()); await writer.drain(); writer.close()

async def main():
    print("tinyrag — RAG HTTP API（参照 LangChain/Dify）\n")
    server = TinyRAGServer()
    # 预加载示例文档
    docs = {"faq_1": "What is tinyrag? Tinyrag is a RAG system built with Python.",
            "faq_2": "How does embedding work? It converts text to fixed-length vectors.",
            "guide_1": "To ingest documents, POST to /ingest with doc_id and text.",
            "guide_2": "To query, POST to /query with your question. It retrieves relevant chunks."}
    for doc_id, text in docs.items():
        server.rag.ingest(doc_id, text)
    srv = await asyncio.start_server(server.handle, "0.0.0.0", 8001)
    addr = srv.sockets[0].getsockname()
    print(f"  tinyrag on http://{addr[0]}:{addr[1]}")
    print(f"  索引: {server.rag.stats()}")
    print(f"\n  测试:")
    print(f"    curl -X POST http://localhost:8001/query -d '{{\"query\":\"how embedding\"}}'")
    print(f"    curl http://localhost:8001/stats")
    async with srv: await srv.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
