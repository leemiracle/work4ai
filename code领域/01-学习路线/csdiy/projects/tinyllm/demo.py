#!/usr/bin/env python3
"""
tinyllm/demo.py — LLM 系统端到端演示

演示 4 个阶段：
  1. Tokenizer 训练 + 编码
  2. 模型前向传播
  3. 推理引擎（KV Cache + 多种采样策略）
  4. 性能统计
"""
import time, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyllm.model import GPT
from tinyllm.tokenizer import BPETokenizer
from tinyllm.infer import LLMInference

def main():
    print("=" * 60)
    print("  tinyllm — LLM 系统 端到端演示")
    print("  参照 nanoGPT + vLLM + tiktoken")
    print("=" * 60)

    # 1. Tokenizer
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 1: Tokenizer             │")
    print("└─────────────────────────────────┘\n")
    tok = BPETokenizer()
    corpus = ["hello world how are you doing today",
              "the quick brown fox jumps over the lazy dog",
              "machine learning is fun and interesting",
              "tiny language model for education"]
    vocab_size = tok.train(corpus, vocab_size=100)
    print(f"  词表大小: {vocab_size}")
    test = "hello world"
    ids = tok.encode(test)
    decoded = tok.decode(ids)
    print(f"  encode('{test}') → {ids[:15]}... ({len(ids)} tokens)")
    print(f"  decode → '{decoded}'")

    # 2. Model
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 2: Model Forward         │")
    print("└─────────────────────────────────┘\n")
    model = GPT(vocab_size=256, d_model=32, n_heads=4, n_layers=2, max_seq=64)
    prompt = [1, 5, 10, 15, 20, 25]
    print(f"  模型: vocab=256, d_model=32, heads=4, layers=2")
    print(f"  参数: ~{model.param_count():,}")
    logits = model.forward(prompt)
    print(f"  forward({prompt}) → {len(logits)}×{len(logits[0])} logits")
    pred = max(range(len(logits[-1])), key=lambda i: logits[-1][i])
    print(f"  next token prediction: {pred}")

    # 3. Inference Engine
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 3: Inference + Sampling  │")
    print("└─────────────────────────────────┘\n")
    engine = LLMInference(model)
    # Greedy
    tokens_greedy, stats_g = engine.generate(prompt, max_tokens=10, strategy="greedy")
    print(f"  Greedy: {stats_g['generated_tokens']} tokens in {stats_g['total_ms']:.1f}ms ({stats_g['tokens_per_sec']:.0f} tok/s)")
    # Temperature
    tokens_temp, stats_t = engine.generate(prompt, max_tokens=10, strategy="temperature", temperature=0.8)
    print(f"  Temp=0.8: {stats_t['generated_tokens']} tokens in {stats_t['total_ms']:.1f}ms")
    # Top-K
    tokens_topk, stats_k = engine.generate(prompt, max_tokens=10, strategy="top_k", top_k=5)
    print(f"  Top-K=5: {stats_k['generated_tokens']} tokens in {stats_k['total_ms']:.1f}ms")

    # 4. Performance
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 4: Performance           │")
    print("└─────────────────────────────────┘\n")
    # Prefill vs Decode 延迟对比
    long_prompt = list(range(1, 33))  # 32 tokens prompt
    _, s = engine.generate(long_prompt, max_tokens=20)
    print(f"  Prompt: {s['prompt_tokens']} tokens")
    print(f"  Prefill: {s['prefill_ms']:.1f}ms (一次处理整个 prompt)")
    print(f"  Decode: {s['decode_avg_ms']:.1f}ms/token (逐 token 生成)")
    print(f"  KV Cache: {'✅ 启用' if s['kv_cache'] else '❌ 未用'}")

    # 批处理
    print(f"\n  批处理（3 个 prompt 并行）:")
    prompts = [list(range(1, 6)), list(range(10, 16)), list(range(20, 26))]
    batch_results = engine.batch_generate(prompts, max_tokens=5)
    for i, r in enumerate(batch_results):
        print(f"    prompt {i}: {r['prompt_len']}→{r['output_len']} tokens, {r['total_ms']:.1f}ms")

    print(f"\n{'='*60}")
    print(f"  tinyllm = model.py + tokenizer.py + infer.py + serve.py")
    print(f"  完整 LLM 系统栈: 架构 → 分词 → 推理 → API 服务")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
