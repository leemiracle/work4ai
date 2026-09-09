# Softmax 温度与采样策略精读

> 参照：HuggingFace sampling / tinyllm/infer.py / GPT 生成策略
>
> csdiy 对应：tinyllm + nanoGPT精读 + tinyloss

---

## 一、Softmax：从 logits 到概率

```
logits = [2.0, 1.0, 0.5, -1.0]  # 模型原始输出
softmax(logits) = [0.64, 0.24, 0.09, 0.03]  # 归一化为概率分布
```

公式：
```
softmax(x_i) = exp(x_i) / Σ exp(x_j)
```

数值稳定版（减最大值）：
```python
def softmax(x):
    mx = max(x)
    exps = [math.exp(v - mx) for v in x]
    s = sum(exps)
    return [e / s for e in exps]
```

---

## 二、温度参数（Temperature）

### 效果

```
Temperature = 0.1（冷酷/确定）:
  logits / T = [20, 10, 5, -10]
  softmax → [0.9999, 0.0001, 0, 0]  → 几乎只选 top-1

Temperature = 1.0（标准）:
  softmax → [0.64, 0.24, 0.09, 0.03]  → 正常分布

Temperature = 5.0（热情/随机）:
  logits / T = [0.4, 0.2, 0.1, -0.2]
  softmax → [0.32, 0.26, 0.23, 0.19]  → 接近均匀分布
```

### 数学解释

```
P(x_i) = exp(logits_i / T) / Σ exp(logits_j / T)
```

- T → 0：softmax 变成 argmax（贪心）
- T → ∞：softmax 变成均匀分布
- T = 1：原始 softmax

---

## 三、Top-K 采样

只从概率最高的 K 个 token 中采样，其余设为 0。

```
原始: [0.64, 0.24, 0.09, 0.03]
Top-2: [0.73, 0.27, 0, 0]  ← 只保留 top-2，重新归一化
```

效果：过滤掉低概率的"噪声 token"。

---

## 四、Top-P（Nucleus）采样

动态选择：累计概率 ≤ P 的最小 token 集合。

```
排序后: [0.64, 0.24, 0.09, 0.03]
P = 0.9: 0.64 < 0.9 → 加入
         0.64+0.24=0.88 < 0.9 → 加入
         0.88+0.09=0.97 ≥ 0.9 → 停止
结果: 只从 [0.64, 0.24, 0.09] 中采样（占 97% 概率）
```

效果：比 Top-K 更灵活——概率集中时少选几个，分散时多选几个。

---

## 五、策略组合

生产环境的 LLM 通常组合使用：

```
logits = model(input)
logits = logits / temperature      # ① 温度调整
logits = top_k_filter(logits, K)   # ② Top-K 过滤
logits = top_p_filter(logits, P)   # ③ Top-P 过滤
probs = softmax(logits)            # ④ 归一化
token = sample(probs)              # ⑤ 采样
```

### 推荐参数

| 场景 | Temperature | Top-K | Top-P | 效果 |
|------|------------|-------|-------|------|
| 代码生成 | 0.2 | 50 | 0.95 | 确定、精确 |
| 创意写作 | 0.9 | 100 | 0.95 | 有创造力 |
| 聊天 | 0.7 | 50 | 0.9 | 平衡 |
| 数学推理 | 0.1 | 10 | 0.9 | 严格 |

---

## 六、你的 tinyllm/infer.py 的实现

```python
def _sample(self, logits, strategy, temperature, top_k, top_p):
    if strategy == "greedy":
        return argmax(logits)  # T=0

    # Temperature
    logits = [l / temperature for l in logits]

    # Softmax → 概率
    probs = softmax(logits)

    # Top-K：保留 K 个最高概率的 token
    if top_k > 0:
        top_indices = sorted(range(len(probs)), key=lambda i: -probs[i])[:top_k]
        probs = [p if i in set(top_indices) else 0 for i, p in enumerate(probs)]

    # Top-P（nucleus）：累计概率 ≤ P 的 token
    if top_p < 1.0:
        sorted_idx = sorted(range(len(probs)), key=lambda i: -probs[i])
        cumsum = 0; nucleus = set()
        for idx in sorted_idx:
            nucleus.add(idx); cumsum += probs[idx]
            if cumsum >= top_p: break
        probs = [p if i in nucleus else 0 for i, p in enumerate(probs)]

    # 重新归一化 + 采样
    return sample_from(probs)
```

---

## 七、一句话总结

> Temperature 控制确定性（T→0 贪心，T→∞ 随机）。Top-K 硬截断。Top-P 动态截断。
>
> 生产 LLM = Temperature + Top-K + Top-P 三重过滤。
>
> **生成的"创造力"本质 = 在概率分布的"确定性"和"随机性"之间找到平衡。**

---

*配套：[tinyllm/infer.py](../projects/tinyllm/infer.py) | [transformer-attention-deep-精读](transformer-attention-deep-精读.md)*
