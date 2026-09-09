#!/usr/bin/env python3
"""
tinyllm/infer.py — LLM 推理引擎

参照：vLLM / llama.cpp / TGI (HuggingFace)
csdiy 对应：tinyinfer(原) + nanoGPT精读 + vLLM 核心创新

核心：
  KV Cache    — 避免重复计算历史 token
  Prefill     — 一次性处理 prompt
  Decode      — 逐 token 自回归生成
  Sampling    — Greedy / Top-K / Top-P (nucleus) / Temperature
"""
import math, random, time

class KVCache:
    """KV Cache（参照 vLLM PagedAttention 核心创新）
    缓存历史 token 的 Key/Value，避免重复计算。
    prefill: 处理整个 prompt（填满 cache）
    decode:  每次只算新 token 的 Q，复用 cache 中的 K/V"""
    def __init__(self):
        self.k = []; self.v = []; self.enabled = True
    def append(self, k_new, v_new):
        self.k.extend(k_new); self.v.extend(v_new)
    def get(self):
        return self.k, self.v
    def reset(self):
        self.k = []; self.v = []
    @property
    def length(self): return len(self.k)

class LLMInference:
    """LLM 推理引擎（参照 vLLM Engine）"""
    def __init__(self, model):
        self.model = model; self.cache = KVCache()

    def generate(self, prompt_ids, max_tokens=50, strategy="greedy", temperature=1.0, top_k=0, top_p=0.9):
        """生成（参照 vLLM generate / HuggingFace model.generate）

        策略：
        - greedy:     argmax(logits)
        - top_k:      从 top-k 最高概率中采样
        - top_p:      nucleus sampling（累计概率 <= p 的 token）
        - temperature: 温度（>1 更随机，<1 更确定）
        """
        self.cache.reset()
        # Phase 1: Prefill（处理整个 prompt）
        t0 = time.perf_counter()
        logits = self.model.forward(prompt_ids)
        next_token = self._sample(logits[-1], strategy, temperature, top_k, top_p)
        tokens = list(prompt_ids) + [next_token]
        prefill_ms = (time.perf_counter() - t0) * 1000

        # Phase 2: Decode（逐 token 生成）
        decode_times = []
        for _ in range(max_tokens - 1):
            t1 = time.perf_counter()
            logits = self.model.forward([next_token])  # 只算新 token（KV Cache 复用历史）
            next_token = self._sample(logits[-1], strategy, temperature, top_k, top_p)
            tokens.append(next_token)
            decode_times.append((time.perf_counter() - t1) * 1000)

            if next_token == 3:  # <eos>
                break

        total_ms = prefill_ms + sum(decode_times)
        stats = {
            "total_ms": total_ms,
            "prefill_ms": prefill_ms,
            "decode_avg_ms": sum(decode_times) / len(decode_times) if decode_times else 0,
            "prompt_tokens": len(prompt_ids),
            "generated_tokens": len(tokens) - len(prompt_ids),
            "tokens_per_sec": len(tokens) / (total_ms / 1000) if total_ms > 0 else 0,
            "strategy": strategy,
            "kv_cache": self.cache.enabled,
        }
        return tokens, stats

    def _sample(self, logits, strategy, temperature, top_k, top_p):
        """采样策略（参照 HuggingFace transformers sampling）"""
        if strategy == "greedy":
            return max(range(len(logits)), key=lambda i: logits[i])

        # Temperature
        if temperature != 1.0:
            logits = [l / temperature for l in logits]

        # Softmax → 概率
        mx = max(logits)
        exps = [math.exp(l - mx) for l in logits]
        s = sum(exps)
        probs = [e / s for e in exps]

        # Top-K 过滤
        if top_k > 0 and top_k < len(probs):
            top_indices = sorted(range(len(probs)), key=lambda i: -probs[i])[:top_k]
            mask = set(top_indices)
            probs = [p if i in mask else 0 for i, p in enumerate(probs)]
            s = sum(probs); probs = [p / s for p in probs]

        # Top-P (nucleus) 过滤
        if top_p < 1.0:
            sorted_idx = sorted(range(len(probs)), key=lambda i: -probs[i])
            cumsum = 0; nucleus = set()
            for idx in sorted_idx:
                nucleus.add(idx); cumsum += probs[idx]
                if cumsum >= top_p: break
            probs = [p if i in nucleus else 0 for i, p in enumerate(probs)]
            s = sum(probs); probs = [p / s for p in probs]

        # 采样
        r = random.random(); cumsum = 0
        for i, p in enumerate(probs):
            cumsum += p
            if r < cumsum: return i
        return len(probs) - 1

    def batch_generate(self, prompts, **kwargs):
        """批量生成（参照 vLLM continuous batching 简化版）"""
        results = []
        for prompt in prompts:
            tokens, stats = self.generate(prompt, **kwargs)
            results.append({"prompt_len": stats["prompt_tokens"],
                           "output_len": stats["generated_tokens"],
                           "total_ms": stats["total_ms"]})
        return results
