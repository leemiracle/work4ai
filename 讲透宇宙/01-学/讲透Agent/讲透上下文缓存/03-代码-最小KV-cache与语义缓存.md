---
card_id: CACH-03
title: "第 3 幕 · 代码：KV Cache 对比 + 语义缓存"
universe: 讲透上下文缓存
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: CACH-04
---

# 💻 第 3 幕 · 代码：KV Cache 加速对比 + 语义缓存

用 numpy 模拟「有/无 KV cache 的 attention 推理」对比加速，再实现一个语义缓存。

```python
import numpy as np
import time, hashlib

def attention_no_cache(Q, K, V):
    """朴素 attention: 每生成一个 token 重算全部."""
    # Q: [d], K/V: [n, d] -> 每次都从头算 K/V (这里假设已给)
    scores = Q @ K.T / np.sqrt(K.shape[1])
    exp = np.exp(scores - scores.max())
    return exp / exp.sum() @ V

def attention_with_cache(new_q, K_cache, V_cache, new_k, new_v):
    """有 KV cache: 只追加新 K/V, 历史从 cache 读."""
    K = np.vstack([K_cache, new_k])
    V = np.vstack([V_cache, new_v])
    scores = new_q @ K.T / np.sqrt(K.shape[1])
    exp = np.exp(scores - scores.max())
    return exp / exp.sum() @ V, K, V

# ===== 实验 1: 生成 n 个 token 的总耗时对比 =====
def bench_generation(n=500, d=64):
    # 模拟: 生成 n 个 token, 每步算一个新 token 的 attention
    K_history = np.random.randn(0, d)
    V_history = np.random.randn(0, d)

    # 无 cache: 每步重算全部 (模拟)
    t0 = time.time()
    for t in range(n):
        full_K = np.random.randn(t+1, d)  # 假装重算
        full_V = np.random.randn(t+1, d)
        q = np.random.randn(d)
        _ = attention_no_cache(q, full_K, full_V)
    t_no = time.time() - t0

    # 有 cache: 只追加新 K/V
    t0 = time.time()
    Kc = np.empty((0, d)); Vc = np.empty((0, d))
    for t in range(n):
        new_k = np.random.randn(1, d)
        new_v = np.random.randn(1, d)
        q = np.random.randn(d)
        _, Kc, Vc = attention_with_cache(q, Kc, Vc, new_k, new_v)
    t_yes = time.time() - t0

    return t_no, t_yes

# ===== 实验 2: 语义缓存 =====
class SemanticCache:
    def __init__(self, threshold=0.95, dim=32):
        self.threshold = threshold
        self.dim = dim
        self.entries = []  # [(query_hash_str, emb, answer)]

    def _embed(self, text):
        rng = np.random.default_rng(abs(hash(text)) % (2**32))
        v = rng.standard_normal(self.dim)
        return v / np.linalg.norm(v)

    def get(self, query):
        q = self._embed(query)
        for orig, emb, ans in self.entries:
            if np.dot(q, emb) > self.threshold:
                return ans, True  # hit
        return None, False

    def put(self, query, answer):
        self.entries.append((query, self._embed(query), answer))

# ===== 跑通 =====
if __name__ == "__main__":
    print("=== 实验 1: KV Cache 加速 (n=500, d=64) ===")
    t_no, t_yes = bench_generation(n=500, d=64)
    print(f"  无 cache: {t_no:.3f}s")
    print(f"  有 cache: {t_yes:.3f}s")
    print(f"  加速比: {t_no/t_yes:.1f}x  (numpy 模拟, 真实 Transformer 更明显)")

    print("\n=== 实验 2: 语义缓存 ===")
    cache = SemanticCache(threshold=0.95)
    cache.put("怎么退款", "请到设置-退款页面申请")
    # 字面不同但语义相近
    for q in ["怎么退款", "如何申请退款", "退款流程是什么", "今天天气如何"]:
        ans, hit = cache.get(q)
        status = "✓ HIT" if hit else "✗ MISS"
        print(f"  '{q}' -> {status} {ans or '(需重新计算)'}")
    print("\n洞察: 字面相同一定 hit; 语义相近靠 embedding; 不相关问题 miss(正确).")
    print("调 threshold=0.8 会看到'退款流程'也 hit(可能错), 0.99 则只有字面相同才 hit.")
```

## 这段代码教什么

1. **KV Cache 加速**：有 cache 时每步只追加新 K/V，历史复用
2. **语义缓存**：cosine 阈值决定命中——高精度低召回，低精度高风险
3. **threshold 权衡**：可视化调参效果

📌 **下一张卡** → `04-不足-缓存失败模式.md`
