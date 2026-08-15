"""
CS329Z HW1 Part A - 完整 mini-Agent 演示
跑通：LLM + RAG + Tools + ReAct 主循环
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent import LLMClient, ToolRegistry, SimpleRAG, Document, ReActAgent


def main():
    print("=" * 70)
    print("🚀 CS329Z HW1 Part A - mini-Agent v0.1 完整演示")
    print("=" * 70)

    # 1. 初始化组件
    print("\n📦 初始化组件...")
    llm = LLMClient(model="mock", verbose=False)
    tools = ToolRegistry()
    rag = SimpleRAG(chunk_size=30, chunk_overlap=10)
    print("   ✅ LLM Client (mock 模式)")
    print("   ✅ Tool Registry (calculator + search + read_file)")
    print("   ✅ RAG (mock embedding)")

    # 2. 添加知识库
    print("\n📚 添加知识库...")
    docs = [
        Document(id="transformer", content=(
            "The Transformer architecture was introduced in 'Attention is All You Need' "
            "by Vaswani et al. in 2017. It uses self-attention mechanism to process tokens "
            "in parallel, replacing recurrent layers. BERT uses the encoder, GPT uses the decoder."
        )),
        Document(id="rag", content=(
            "Retrieval-Augmented Generation (RAG) combines retrieval with generation. "
            "Introduced by Lewis et al. NeurIPS 2020. RAG grounds LLM responses in retrieved "
            "documents, reducing hallucination significantly."
        )),
        Document(id="react", content=(
            "ReAct was proposed by Yao et al. ICLR 2023. The key idea is to interleave "
            "reasoning (Thought) with acting (Action). The agent uses tools, observes results, "
            "and continues reasoning until a final answer is reached."
        )),
    ]
    n = rag.add_documents(docs)
    print(f"   ✅ 添加 {len(docs)} 篇文档，切分为 {n} chunks")

    # 3. 创建 agent
    agent = ReActAgent(llm=llm, tools=tools, rag=rag, max_iterations=3, verbose=True)

    # 4. 测试用例
    test_cases = [
        {
            "name": "数学计算（用 calculator 工具）",
            "query": "请计算 (15 + 27) * 4 等于多少？",
        },
        {
            "name": "知识检索（用 RAG）",
            "query": "Transformer 架构是什么？谁提出的？",
        },
        {
            "name": "工具 + 检索混合",
            "query": "RAG 是哪一年提出的？同时计算 2024 - 那一年 等于多少年。",
        },
    ]

    results = []
    for i, tc in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"📝 测试 {i}: {tc['name']}")
        print(f"🔍 Query: {tc['query']}")
        print(f"{'='*70}")

        trace = agent.run(tc["query"])
        print(f"\n📋 Trace:\n{trace}")
        results.append({"test": tc["name"], "answer": trace.final_answer})

    # 5. 总结
    print(f"\n{'='*70}")
    print("📊 测试总结")
    print(f"{'='*70}")
    for r in results:
        print(f"  • {r['test']}")
        print(f"    答案: {r['answer'][:100]}")

    print(f"\n✅ mini-Agent v0.1 跑通！")
    print(f"\n💡 下一步（Stage 2-3）:")
    print(f"  - 配置真实 LLM（OPENAI_API_KEY 等）")
    print(f"  - 添加更多工具（HTTP / Python REPL / 邮件）")
    print(f"  - 实现 DSPy 重写（CS329Z HW1 Part B）")
    print(f"  - 实现 4-tuple Eval（CS329Z HW3）")


if __name__ == "__main__":
    main()
