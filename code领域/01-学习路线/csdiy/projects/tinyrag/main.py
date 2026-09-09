#!/usr/bin/env python3
"""tinyrag — 参照 LangChain/LlamaIndex 的 RAG 检索增强生成
参照：LangChain / LlamaIndex / RAG from scratch
csdiy 对应：tinyvector + tinysearch + tinyinfer + AI核心
核心：文档切片 → 嵌入 → 向量检索 → 上下文拼接 → 生成"""
import hashlib,re,math
from collections import Counter

def text_to_embedding(text,dim=64):
    """简化嵌入（用字符频率 → 固定维度向量）
    真实场景用 sentence-transformers/bge/embedding API"""
    h=hashlib.sha256(text.encode()).digest()
    return [(h[i%len(h)]/255.0-0.5)*2 for i in range(dim)]

def cosine_sim(a,b): return sum(x*y for x,y in zip(a,b))/(math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b)) or 1)

class TinyRAG:
    """RAG 系统（参照 LangChain RAG pipeline）"""
    def __init__(self,dim=64,chunk_size=100,overlap=20):
        self.dim=dim; self.chunk_size=chunk_size; self.overlap=overlap
        self.chunks=[]; self.embeddings=[]; self.metadata=[]
    def ingest(self,doc_id,text):
        """文档入库：切分 → 嵌入 → 存储"""
        # 1. 切分（参照 LangChain RecursiveCharacterTextSplitter）
        chunks=[]
        for i in range(0,len(text),self.chunk_size-self.overlap):
            chunk=text[i:i+self.chunk_size]
            if len(chunk)>10: chunks.append(chunk)
        # 2. 嵌入 + 存储
        for i,chunk in enumerate(chunks):
            emb=text_to_embedding(chunk,self.dim)
            self.chunks.append(chunk); self.embeddings.append(emb)
            self.metadata.append({"doc_id":doc_id,"chunk_idx":i,"text":chunk})
        return len(chunks)
    def retrieve(self,query,top_k=3):
        """检索（参照 LlamaIndex VectorStoreRetriever）"""
        q_emb=text_to_embedding(query,self.dim)
        scored=sorted([(cosine_sim(q_emb,emb),meta) for emb,meta in zip(self.embeddings,self.metadata)],key=lambda x:-x[0])
        return scored[:top_k]
    def augment_prompt(self,query,top_k=3):
        """构建增强 Prompt（参照 RAG 的 Context Injection）"""
        results=self.retrieve(query,top_k)
        context="\n\n".join([f"[{i+1}] {m['text'][:200]}" for i,(_,m) in enumerate(results)])
        prompt=f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        return prompt,results

def main():
    print("tinyrag — RAG 检索增强生成（参照 LangChain/LlamaIndex）\n")
    rag=TinyRAG(chunk_size=80,overlap=20)
    docs={"api_doc":"The API endpoint /v1/chat returns completions. Rate limit is 60 req/min. Auth via Bearer token.",
          "faq":"Q: How to retry? A: Use exponential backoff. Q: Pricing? A: $0.002 per 1K tokens.",
          "guide":"To get started: 1. Create API key 2. Call /v1/chat 3. Parse JSON response 4. Handle errors with retry."}
    for doc_id,text in docs.items():
        n=rag.ingest(doc_id,text); print(f"  ingested '{doc_id}': {n} chunks")
    query="What is the rate limit?"
    prompt,results=rag.augment_prompt(query,top_k=2)
    print(f"\n  Query: '{query}'")
    print(f"  Retrieved:")
    for score,meta in results: print(f"    [{meta['doc_id']}] score={score:.3f} → {meta['text'][:60]}...")
    print(f"\n  Augmented Prompt (前300字符):\n  {prompt[:300]}...")
    print(f"\n  RAG 流程: ingest(split+embed) → retrieve(similarity) → augment(context) → generate(LLM)")

if __name__=="__main__": main()
