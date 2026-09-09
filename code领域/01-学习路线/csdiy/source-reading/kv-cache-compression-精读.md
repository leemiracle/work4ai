# KV Cache 压缩精读：StreamingLLM / H2O / KVQuant

> 参照：Xiao 2023 (StreamingLLM) / Zhang 2023 (H2O) / Liu 2023 (KVQuant)
>
> csdiy 对应：kv-cache-原理精读 + long-context精读 + flash-attention精读

---

## 一、问题：KV Cache 占满显存

```
LLaMA-7B, seq=32K:
  KV Cache = 2 × 32层 × 32头 × 32K × 128维 × 2字节(BF16)
           = 1GB per request

10 并发请求 × 32K context = 10GB KV Cache（比模型权重还大！）

→ KV Cache 是 LLM 长序列推理的核心瓶颈
```

---

## 二、StreamingLLM（滑动窗口 + Attention Sink）

### 发现：Attention Sink

```
观察: 即使序列很长，前几个 token（position 0-3）的 attention score 极高

原因: Softmax 要求所有位置的和=1
  → 如果某些位置"不重要"→ 其他位置的 attention 被"挤"到前面
  → 前 4 个 token 变成"垃圾回收站"（吸收多余注意力）

→ 删掉前 4 个 token → 后续位置的 attention 分配崩溃 → 质量暴跌
```

### 方案：保留 Sink + Recent Window

```
KV Cache 只保留:
  ① 前 S 个 token（Attention Sink, S=4）
  ② 最近 W 个 token（Sliding Window, W=2048）

总 KV Cache = (4 + 2048) 个 token → 固定大小！
→ 可以无限生成（不受序列长度限制）

丢弃中间的 token → 质量损失 <5%（perplexity 增加 <5%）
```

### 效果

```
标准推理: seq=100K → OOM（KV Cache 太大）
StreamingLLM: seq=1M → 正常（KV Cache 固定 ~2K）

Mistral 的 Sliding Window Attention 是类似思路：
  每层只 attend 最近 W 个 token → KV Cache 固定
```

---

## 三、H2O（Heavy-Hitter Oracle）

### 思想：动态保留重要的 KV

```
不是固定保留"最近的"→ 而是保留"attention 最高的"

算法:
  每个 token 生成后 → 计算所有已缓存 KV 的累计 attention score
  → 删除得分最低的 KV → 保留 top-K

→ 每次只保留最重要的 KV → KV Cache 大小固定
→ 比 StreamingLLM 更智能（不盲目保留最近的）
```

### 效果

```
保留 20% KV Cache → 质量损失 <2%
保留 50% KV Cache → 质量损失 <0.5%

vs StreamingLLM: H2O 在需要"远距离信息"的任务上更好
  （如长文档问答需要参考开头的信息）
```

---

## 四、KVQuant（KV Cache 量化）

### 思想

```
KV Cache 是 FP16/BF16 (2 bytes/value)
→ 量化到 INT8 (1 byte) → 省 50%
→ 量化到 INT4 (0.5 byte) → 省 75%
```

### 挑战

```
KV Cache 的分布比模型权重更不均匀:
  Key: 有少量极大值 → 量化容易截断
  Value: 分布较均匀 → 量化更容易

→ 需要 per-channel 量化（不是 per-tensor）
→ Key 用 INT4 精度损失大 → 建议 INT8
→ Value 可以 INT4 → 组合节省 ~62%
```

### 实现

```python
# vLLM 的 KV Cache 量化（v0.4+）
python -m vllm.entrypoints.openai.api_server \
    --model llama-3-70b \
    --kv-cache-dtype fp8  # KV Cache 用 FP8（省 50%）
```

---

## 五、其他 KV 压缩方法

| 方法 | 原理 | 压缩比 | 质量损失 | 适用 |
|------|------|--------|---------|------|
| StreamingLLM | Sink + Window | ~90% | ~5% | 无限生成 |
| H2O | 动态保留 top-K | ~80% | ~2% | 长文档 QA |
| KVQuant | INT8/INT4 | ~50-75% | ~1% | 通用 |
| Group-wise Quant | 分组量化 | ~75% | ~0.5% | 精度要求高 |
| Token Recycle | 跨请求共享 KV | ~50% | ~3% | 共享 system prompt |
| KV Clustering | 聚类合并相似 KV | ~60% | ~3% | 冗余多场景 |

---

## 六、组合使用

```
生产级 KV Cache 优化（vLLM 示例）:

① PagedAttention → 无碎片内存管理
② GQA → 从 32 组 KV 降到 8 组 → KV Cache 缩小 4x
③ FP8 KV Quant → 再省 50%
④ Sliding Window → 长序列固定窗口

组合效果:
  原始: 32K seq × 32 KV heads = 1GB
  GQA(8 KV): 250MB
  FP8: 125MB
  Sliding(4K): 16MB

→ 60x 压缩 → 同时服务 100 个请求
```

---

## 七、和 tinyllm 的交叉

你的 `tinyllm/infer.py` 的 KV Cache：

```python
class KVCache:
    def __init__(self):
        self.k = []; self.v = []
    def append(self, k_new, v_new):
        self.k.extend(k_new); self.v.extend(v_new)
```

可以扩展为 Sliding Window：

```python
class StreamingKVCache:
    def __init__(self, window=64, sink=4):
        self.sink_k = []; self.sink_v = []     # Attention Sink
        self.recent_k = []; self.recent_v = []  # Recent Window
        self.window = window; self.sink = sink

    def append(self, k, v):
        if len(self.sink_k) < self.sink:
            self.sink_k.append(k); self.sink_v.append(v)
        else:
            self.recent_k.append(k); self.recent_v.append(v)
            if len(self.recent_k) > self.window:
                self.recent_k.pop(0); self.recent_v.pop(0)

    def get_all(self):
        return self.sink_k + self.recent_k, self.sink_v + self.recent_v
```

---

## 八、一句话总结

> KV Cache 压缩 = StreamingLLM（Sink+Window）+ H2O（动态 top-K）+ KVQuant（INT8/4）。
>
> **组合使用 GQA + FP8 + Sliding Window → 60x 压缩 → 支持 100+ 并发长请求。**
>
> StreamingLLM 的核心发现：前几个 token 是 "Attention Sink" → 不能删。

---

*配套：[kv-cache-原理精读](kv-cache-原理-精读.md) | [long-context精读](long-context-精读.md) | [attention-variants精读](attention-variants-精读.md) | [tinyllm/infer.py](../projects/tinyllm/infer.py)*
