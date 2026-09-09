# Speculative Decoding 精读：用小模型加速大模型推理

> 参照：Leviathan 2023 / Chen 2023 / Medusa / EAGLE
>
> csdiy 对应：kv-cache-原理 + softmax-temperature + tinyllm/infer.py

---

## 一、问题：LLM 推理的内存瓶颈

### Decode 阶段是 Memory-Bound

```
生成 1 个 token:
  加载模型权重: 14GB（7B 模型 BF16）
  计算量: ~14 GFLOPS
  时间: 14GB / 1.5TB/s ≈ 10ms

→ GPU 算力利用率 < 5%！
→ 瓶颈是内存带宽，不是计算
```

**洞察**：如果能一次加载权重生成多个 token → 利用率提高。

---

## 二、Speculative Decoding 原理

### 核心思想：小模型猜，大模型验

```
① Draft（小模型/草稿模型）快速生成 K 个候选 token
   小模型 1B → 生成 5 个 token，每步 1ms → 5ms

② Verify（大模型/目标模型）一次性验证这 K 个 token
   大模型 7B → forward(5 tokens) → 5 个概率分布
   → 大模型一次 forward 处理 5 个 token（prefill 模式，计算密集）

③ Accept/Reject
   如果大模型同意 → 接受（免费得到多个 token）
   如果大模型不同意 → 拒绝并重新采样
```

### 速度提升

```
朴素推理: 5 个 token × 10ms = 50ms
Speculative: 草稿 5ms + 验证 10ms + 1ms（补充） = 16ms
→ 3x 加速（如果接受率高）
```

---

## 三、接受/拒绝采样

### 算法（参照 Leviathan 2023）

```python
def speculative_decode(prompt, draft_model, target_model, K=4):
    tokens = list(prompt)

    while not done:
        # ① 草稿模型生成 K 个候选
        draft_tokens = []
        for _ in range(K):
            draft_logits = draft_model.forward(tokens + draft_tokens)
            draft_token = sample(draft_logits[-1])
            draft_tokens.append(draft_token)

        # ② 目标模型一次性验证
        target_logits = target_model.forward(tokens + draft_tokens)

        # ③ 逐个检查接受/拒绝
        accepted = 0
        for i, dt in enumerate(draft_tokens):
            target_prob = softmax(target_logits[len(tokens) + i - 1])[dt]
            draft_prob = softmax(draft_logits[len(tokens) + i - 1])[dt]

            if target_prob >= draft_prob:
                # 接受（目标模型给的概率更高 → 直接接受）
                tokens.append(dt); accepted += 1
            else:
                # 以 target_prob/draft_prob 的概率接受
                if random.random() < target_prob / draft_prob:
                    tokens.append(dt); accepted += 1
                else:
                    # 拒绝 → 从 (target_prob - draft_prob) 的残差分布中采样
                    residual = normalize(softmax(target_logits[i]) - softmax(draft_logits[i]))
                    tokens.append(sample(residual))
                    break  # 拒绝后停止验证剩余候选

        # 补充 1 个 token（保证至少生成 1 个）
        if accepted == K:
            tokens.append(sample(target_logits[-1]))

    return tokens
```

### 关键数学保证

```
接受概率: min(1, q(x)/p(x))
  q = 草稿模型概率
  p = 目标模型概率

拒绝时从残差分布采样:
  residual ∝ max(0, p(x) - q(x))

→ 最终输出的分布 = 目标模型的精确分布！
→ 无损加速（结果和直接用大模型完全一样）
```

---

## 四、草稿模型的选择

| 草稿模型 | 大小 | 加速比 | 说明 |
|---------|------|--------|------|
| 同模型更少层 | 1-2B | 2-3x | 最常见（如 7B + 1B） |
| 同模型量化版 | INT4 7B | 1.5-2x | 量化模型更快 |
| 自回归草稿 | Medusa heads | 2-4x | 不需要单独模型 |
| 训练的推测头 | EAGLE | 3-5x | 最先进的方案 |

### Medusa（不用单独草稿模型）

```
在 LLM 上加 K 个"Medusa Head"（额外的 LM Head）：
  Head 1: 预测下一个 token（标准）
  Head 2: 预测下下个 token
  Head 3: 预测下下下个 token

→ 一次 forward 生成 K 个候选 → 无需草稿模型
→ 但准确率较低（Head 2/3 的预测不如标准自回归）
```

### EAGLE（当前最优）

```
训练一个轻量级"推测网络"：
  输入: 当前 token 的 hidden state
  输出: 下一个 token 的 hidden state（不是 token 本身）

→ 在 hidden state 空间推测 → 准确率更高
→ 接受率 60-80% → 3-5x 加速
```

---

## 五、什么场景适合 Speculative Decoding

### 适合

```
✅ 单请求推理（batch=1）→ memory-bound 最明显
✅ 草稿模型和大模型分布接近 → 接受率高
✅ 生成任务（而非理解任务）→ token 间依赖性强
```

### 不适合

```
❌ 大 batch 推理 → 已经 compute-bound，推测无优势
❌ 草稿模型很差 → 接受率低 → 反而更慢
❌ 延迟极低要求 → 草稿模型的额外延迟可能不划算
```

---

## 六、各方案的加速比

| 方案 | 加速比 | 额外显存 | 实现复杂度 |
|------|--------|---------|-----------|
| Vanilla Speculative | 2-3x | 草稿模型大小 | 中 |
| Medusa | 2-4x | Medusa heads | 低 |
| EAGLE | 3-5x | 推测网络 | 高 |
| Lookahead | 1.5-2x | 无 | 最低 |
| Self-Speculative | 1.5-2x | 无 | 中 |

---

## 七、一句话总结

> Speculative Decoding = 小模型猜 → 大模型验 → 接受/拒绝采样。
>
> **无损加速**（输出分布 = 大模型精确分布），2-5x 加速。
>
> EAGLE = 当前最优方案（3-5x，hidden state 空间推测）。
>
> **核心洞察：LLM 推理是 memory-bound → 加载一次权重多算几个 token 就赚到。**

---

*配套：[kv-cache-原理](kv-cache-原理-精读.md) | [softmax-temperature](softmax-temperature-精读.md) | [tinyllm/infer.py](../projects/tinyllm/infer.py)*
