# MoE 路由精读：Mixtral 8x7B 的稀疏激活

> 参照：Shazeer 2017 / Switch Transformer / Mixtral / DeepSeek-MoE
>
> csdiy 对应：tinymoe(原) + transformer-attention-deep + model-parallel

---

## 一、MoE 的核心思想

### 密集模型 vs 稀疏模型

```
密集 FFN（标准 Transformer）:
  每个 token 经过完整的 FFN → 全部参数参与计算

MoE FFN（混合专家）:
  每个 token 只激活 K 个专家（如 8 选 2）
  → 总参数多（8×FFN）但计算量少（只用 2×FFN）
```

**用参数量换效率**：47B 总参数，14B 活跃参数 → 7B 的计算成本，70B 的效果。

---

## 二、路由机制

### Top-K 路由（Mixtral 方式）

```python
def route(token_embedding, router_weight, n_experts=8, top_k=2):
    # 计算每个专家的分数
    logits = token_embedding @ router_weight  # [d_model] × [d_model, n_experts]
    weights = softmax(logits)                 # [n_experts]

    # 选 Top-K 个专家
    top_k_indices = argsort(weights)[-top_k:] # 如 [2, 5]
    top_k_weights = weights[top_k_indices]    # 如 [0.6, 0.4]

    # 重新归一化
    top_k_weights = top_k_weights / sum(top_k_weights)

    return top_k_indices, top_k_weights
```

### 加权组合

```
output = Σ_i (weight_i × Expert_i(token))

例：专家 2 权重 0.6 + 专家 5 权重 0.4
output = 0.6 × Expert_2(x) + 0.4 × Expert_5(x)
```

---

## 三、负载均衡问题

### 路由崩塌（Routing Collapse）

```
问题：路由器可能总是选同几个"强"专家
→ 其他专家不训练 → 退化

症状：
  Expert 0: 80% 的 token
  Expert 1-7: 各 2-3% 的 token
→ MoE 退化成密集模型
```

### 辅助损失（Auxiliary Loss）

```
# 参照 Switch Transformer §2.2
L_aux = α × n_experts × Σ (f_i × P_i)

f_i = 分配给专家 i 的 token 比例
P_i = 路由器给专家 i 的平均概率

目标：f_i × P_i 均匀分布（每个专家被选频率相等）
→ 加到训练损失中，强制负载均衡
```

### 容量因子（Capacity Factor）

```
每个专家最多处理 capacity = (N_tokens / N_experts) × capacity_factor

例：1000 tokens, 8 experts, capacity_factor=1.25
→ 每个专家最多处理 156 tokens
→ 超出的 token 被丢弃或传递给下一个专家
```

---

## 四、DeepSeek-MoE 的创新

### 细粒度专家

```
标准 MoE: 8 个大专家（每个 = 完整 FFN）
DeepSeek: 64 个小专家（每个 = 1/8 FFN）+ 2 个共享专家

→ Top-6 路由：选 6 个小专家 + 2 个共享专家
→ 更灵活的组合 + 共享专家保证基础能力
```

### 共享专家（Shared Expert）

```
某些专家始终被激活（不参与路由）：
  output = Shared_Expert(x) + Σ routed_experts(x)

→ 共享专家学习"通用知识"
→ 路由专家学习"专业知识"
```

---

## 五、MoE 的工程挑战

### 显存

```
Mixtral 8x7B:
  总参数: 47B → BF16 = 94GB（一张 80GB A100 放不下）
  活跃参数: 14B → 推理时只需 28GB 的计算量
  → 需要张量并行或多卡部署
```

### 训练通信

```
Token 路由到不同 GPU 上的专家：
  GPU 0 有 Expert 0-3
  GPU 1 有 Expert 4-7

  → Token 需要跨 GPU 发送（All-to-All 通信）
  → 通信开销大
```

### 推理吞吐

```
MoE 推理的 batch 处理更复杂：
  batch 中不同 token 路由到不同专家
  → 需要 reshape + dispatch + compute + combine
  → vLLM/TGI 有专门的 MoE 调度优化
```

---

## 六、MoE 模型对比

| 模型 | 总参数 | 活跃参数 | 专家数 | Top-K | 特点 |
|------|--------|---------|--------|-------|------|
| GShard | 600B | ? | 2048 | 2 | 首个超大规模 MoE |
| Switch | 1.6T | ? | 2048 | 1 | Top-1 路由 |
| Mixtral | 47B | 14B | 8 | 2 | 开源 LLM MoE 标杆 |
| DeepSeek-V2 | 236B | 21B | 160 | 6 | 细粒度+共享专家 |
| Grok-1 | 314B | ? | 8 | 2 | xAI 的 MoE |
| Qwen-MoE | 14B | 2.7B | 60 | 4 | 中文 MoE |

---

## 七、选择指南

```
你应该用 MoE 吗？
├── 训练预算 > $10M → MoE（参数效率高）
├── 推理延迟敏感 → 密集模型（MoE 调度有开销）
├── 显存有限 → 密集模型（MoE 总参数大）
└── 研究实验 → 密集模型（MoE 工程复杂度高）
```

---

## 八、一句话总结

> MoE = Top-K 路由器选择专家 → 总参数多但计算量少。
>
> 关键挑战：负载均衡（auxiliary loss）+ 跨 GPU 通信（All-to-All）+ 推理调度。
>
> DeepSeek 创新：细粒度专家 + 共享专家 → 更灵活 + 更稳定。
>
> **Mixtral 8x7B = 47B 参数 / 14B 计算 → 开源 MoE 的里程碑。**

---

*配套：[transformer-attention-deep](transformer-attention-deep-精读.md) | [model-parallel精读](model-parallel-精读.md) | [mixed-precision精读](mixed-precision-精读.md)*
