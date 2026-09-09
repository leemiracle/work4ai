# Transformer 推理优化精读：Prefill / Decode / Chunked Prefill

> 参照：vLLM / SARATHI / TensorRT-LLM / DeepSpeed-FastGen
>
> csdiy 对应：kv-cache-原理 + speculative-decoding + llm-deployment + tinyllm/infer.py

---

## 一、推理的两个阶段：特征完全不同

```
Prefill（首 token 延迟，TTFT）:
  输入: prompt（如 512 tokens）
  计算: 512×512 attention → dense 矩阵乘法
  瓶颈: GPU 计算（compute-bound）
  延迟: ~50-200ms
  目标: 降低 TTFT

Decode（逐 token 生成，TPOT）:
  输入: 1 个新 token
  计算: 1×N attention → sparse 向量乘法
  瓶颈: GPU 内存带宽（memory-bound）
  延迟: ~5-30ms/token
  目标: 降低 TPOT + 提高吞吐
```

### 为什么 Decode 是 memory-bound

```
生成 1 个 token 需要加载:
  模型权重: 14GB（7B BF16）
  KV Cache: 0.5GB（如 4K context）
  总计: ~14.5GB

计算量:
  只有 1×N 的 attention + 1 次 FFN
  ≈ 14 GFLOPS

GPU 利用率:
  计算: 14 GFLOPS / 312 TFLOPS = 0.005%
  内存: 14.5GB / 2TB/s = 7.25ms
  → 算力利用率 < 1%！完全浪费了 A100 的计算能力

解法: batching → 一次加载权重处理多个请求
```

---

## 二、Continuous Batching（连续批处理）

### 朴素 batching 的问题

```
请求 A (10 tokens): ████████████████ done
请求 B (50 tokens): ███████████████████████████████████████ done
请求 C (5 tokens):  ██████ done

→ 请求 A 和 C 完成后，GPU 空闲等 B
→ GPU 利用率随 batch 长度方差增大而降低
```

### Continuous Batching（vLLM 核心）

```
时间步 →    1    2    3    4    5    6    7    8
请求 A:    [P][D][D][D][D] done
请求 B:       [P][D][D][D][D][D][D] done
请求 C:          [P][D][D][D] done
请求 D:                [P][D][D][D][D][D] done

→ 每个时间步都可以:
  ① 移除已完成的请求
  ② 加入新请求（只要有 GPU 空间）
  → GPU 始终满载
```

### 实现

```python
# vLLM Scheduler 的核心逻辑（简化）
def schedule_step(self):
    running = []
    # ① 移除完成的请求
    for req in self.running:
        if req.is_finished():
            self.free_kv_cache(req)
        else:
            running.append(req)
    # ② 加入新请求（如果有空间）
    while self.waiting and self.has_kv_space():
        new_req = self.waiting.pop(0)
        self.allocate_kv_cache(new_req)
        running.append(new_req)
    # ③ 这一步的 batch = running
    self.running = running
    return self.running
```

---

## 三、Chunked Prefill（分块预填充）

### 问题

```
一个长 prompt（如 32K tokens）的 Prefill:
  计算: 32K×32K attention → 计算量大 → 阻塞 GPU
  → 在这期间 Decode 的请求全部等待
  → 吞吐量下降

更糟: 多个请求同时 Prefill → GPU 被抢满
```

### 解法：把 Prefill 分成小块

```
SARATHI / DeepSpeed-FastGen 的方案:

32K Prefill → 分成 8 个 4K chunk

时间步:    1        2        3        4
Prefill: [4K-1]  [4K-2]  [4K-3]  [4K-4] ...
Decode:   [ReqA]  [ReqA]  [ReqA]  [ReqA]
          [ReqB]          [ReqB]

→ 每个 chunk 只占一部分 GPU
→ Decode 请求同时运行 → 不被阻塞
→ 吞吐量提升 2-10x（取决于 prompt 长度分布）
```

### 效果

```
场景: 70% 短请求（<500 tokens）+ 30% 长请求（>4K tokens）

朴素 batching: GPU 利用率 ~40%（长请求阻塞短请求）
Chunked Prefill: GPU 利用率 ~85%
→ 吞吐量提升 2.1x
```

---

## 四、Prefill-Decode 分离（Disaggregated Serving）

### 思想

```
不同阶段的瓶颈不同:
  Prefill: compute-bound → 用计算强的 GPU
  Decode:  memory-bound → 用带宽大的 GPU

→ 把 Prefill 和 Decode 放到不同的 GPU 上！
```

### 架构

```
用户请求 → Prefill Worker (A100, 计算强)
              ↓ KV Cache 传输
           Decode Worker (L40S, 带宽好)
              ↓ 生成 tokens
           返回用户
```

### 优势

```
① Prefill GPU 不被 Decode 占用 → 吞吐提升
② Decode GPU 可以用更便宜的低端 GPU
③ KV Cache 传输是顺序的 → 网络开销可控

代表: Splitwise / DistServe / Mooncake（月之暗面）
```

---

## 五、CUDA Graph（Kernel 融合）

### 问题

```
每生成 1 个 token → 数百次 GPU kernel 调用
  matmul → bias → activation → layernorm → matmul → ...
  
每个 kernel 启动有 ~5μs 开销
数百个 kernel → 1ms 纯启动开销
```

### CUDA Graph

```
# 把整个 decode step 录制成一个 CUDA Graph
with torch.cuda.graph(graph):
    output = model(input)

# 之后只需一次 graph.replay() → 省掉所有 kernel 启动开销
graph.replay()
→ 延迟降低 20-40%
```

---

## 六、各技术叠加效果

```
基础推理（HuggingFace generate）:
  吞吐: ~100 tokens/s

+ Flash Attention:        → +30%（减少 IO）
+ Continuous Batching:    → +10x（多请求并发）
+ Chunked Prefill:        → +2x（减少 Prefill 阻塞）
+ GQA:                    → +1.5x（减少 KV Cache）
+ KV Quant (FP8):         → +1.5x（省内存）
+ CUDA Graph:             → +1.3x（减少启动开销）
+ Speculative Decoding:   → +3x（小模型加速）

总计: ~100 × 1.3 × 10 × 2 × 1.5 × 1.5 × 1.3 × 3
     ≈ 22,800 tokens/s（A100 理论峰值）

实际 vLLM: ~10,000-15,000 tokens/s（已经很接近理论极限）
```

---

## 七、选择优化策略

```
你的场景？
├── 单请求低延迟（如聊天）
│   → Speculative Decoding（EAGLE）+ CUDA Graph
├── 高吞吐批量（如文档处理）
│   → Continuous Batching + Chunked Prefill
├── 长序列（如 RAG >32K）
│   → Sliding Window + GQA + KV Compression
├── 多 GPU 大模型
│   → Tensor Parallel + Pipeline Parallel
└── 成本敏感
    → INT4 量化 + 小 batch + CPU offload
```

---

## 八、一句话总结

> Prefill 是 compute-bound，Decode 是 memory-bound → 优化策略完全不同。
>
> Continuous Batching = 吞吐量提升 10x。Chunked Prefill = 减少 2x 阻塞。
> CUDA Graph = 延迟降低 30%。Speculative Decoding = 3x 加速。
>
> **vLLM 把这些技术全打包了 → 它是当前开源推理的事实标准。**

---

*配套：[kv-cache-原理精读](kv-cache-原理-精读.md) | [speculative-decoding精读](speculative-decoding-精读.md) | [llm-deployment精读](llm-deployment-精读.md) | [tinyllm/infer.py](../projects/tinyllm/infer.py)*
