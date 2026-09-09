# Mamba / SSM 数学精读：选择性状态空间模型

> 参照：Gu & Dao 2023 (Mamba) / Gu 2022 (S4) / S4ND / Jamba
>
> csdiy 对应：attention-variants精读 + transformer-attention-deep + tinytransformer

---

## 一、Mamba 要解决什么问题

Transformer 的 Attention 是 O(N²)：
```
序列长度 N=100K → attention matrix = 100K×100K = 10GB
→ 无法扩展到超长序列
```

Mamba 的目标：**O(N) 复杂度 + Transformer 级别的质量 + 推理时 O(1)**。

---

## 二、状态空间模型（SSM）基础

### 连续时间 SSM

```
状态方程: h'(t) = A·h(t) + B·x(t)
输出方程: y(t)  = C·h(t)

h(t): 隐状态（记忆）
x(t): 输入
y(t): 输出
A, B, C: 可学习参数矩阵
```

直觉：SSM 是一个**线性时不变系统**（LTI），类似 RNN 但数学更清晰。

### 离散化（ZOH）

```
用零阶保持（Zero-Order Hold）把连续 SSM 离散化:

Ā = exp(Δ·A)
B̄ = (Δ·A)^{-1} · (exp(Δ·A) - I) · Δ·B

离散递推:
h_t = Ā · h_{t-1} + B̄ · x_t
y_t = C · h_t
```

### 两种计算模式

```
① 递推模式（推理用，O(N)）:
  h_0 = 0
  h_1 = Ā·h_0 + B̄·x_1; y_1 = C·h_1
  h_2 = Ā·h_1 + B̄·x_2; y_2 = C·h_2
  ...
  → 每步 O(d²)，总计 O(N·d²)
  → 推理时 O(1) per token（只维护 h）

② 卷积模式（训练用，可并行，O(N log N)）:
  因为 LTI 系统等价于卷积:
  y = K * x （K 是从 A,B,C 推导的卷积核）
  → FFT 卷积 → O(N log N)
  → 训练时可并行！
```

**关键优势**：训练时并行（卷积），推理时 O(1)（递推）→ 两全其美。

---

## 三、S4 → Mamba：选择性机制

### S4 的问题

```
S4 是 LTI（线性时不变）→ A, B, C 对所有输入都一样
→ 无法根据输入内容"选择性记忆"
→ 类似一个固定滤波器 → 表达力不如 Attention
```

### Mamba 的创新：选择性 SSM（SSM = Selective SSM）

```
让 B, C 依赖输入 x_t:

  B_t = Linear_B(x_t)    ← B 从输入生成
  C_t = Linear_C(x_t)    ← C 从输入生成
  Δ_t = softplus(Linear_Δ(x_t))  ← 步长也从输入生成

→ 不同位置的 token 有不同的 B, C, Δ
→ 模型可以"选择性"地记住重要信息、忘记不重要的

→ 但不再是 LTI → 不能用卷积了！
```

### 解决：硬件感知的并行扫描

```
Mamba 用并行扫描（Parallel Scan）算法:
  → GPU 上的前缀和 → O(N log N) 但常数极小
  → 配合 SRAM 感知（类似 Flash Attention）→ 不频繁读写 HBM
```

---

## 四、Mamba Block 架构

```python
class MambaBlock:
    def forward(self, x):
        # ① 输入投影
        x_proj = Linear_in(x)  # → [B, L, D_inner + 2*D_state + 1]

        # ② 分离: x_branch 和 SSM 参数
        x_branch = x_proj[:, :, :D_inner]
        B = x_proj[:, :, D_inner : D_inner + D_state]
        C = x_proj[:, :, D_inner + D_state : -1]
        delta = softplus(x_proj[:, :, -1:])  # 步长

        # ③ 离散化（用输入相关的 Δ）
        A_bar = exp(delta * A)  # A 是固定参数
        B_bar = delta * B       # 简化的 ZOH

        # ④ 选择性 SSM 递推（并行扫描）
        h = 0; ys = []
        for t in range(L):
            h = A_bar[t] * h + B_bar[t] * x_branch[t]
            y = C[t] * h
            ys.append(y)

        # ⑤ 门控 + 输出投影
        gate = silu(Linear_gate(x))  # SiLU 激活
        return Linear_out(ys * gate)
```

---

## 五、Mamba vs Transformer

| 维度 | Transformer | Mamba |
|------|------------|-------|
| 训练复杂度 | O(N²d) | **O(Nd²)** |
| 推理/token | O(Nd)（KV Cache） | **O(d²)（O(1) 不依赖 N）** |
| 长序列 | OOM（N²） | **线性**（O(N)） |
| 质量（<8K） | 最好 | 接近 |
| 质量（>32K） | 需要复杂优化 | **天然支持** |
| KV Cache | 需要（O(Nd)） | **不需要**（O(d) 状态） |
| 并行训练 | ✅ | ✅（scan） |
| 代表 | GPT/LLaMA/Qwen | Mamba/Jamba/RecurrentGemma |

---

## 六、Mamba 的变体

| 模型 | 创新 | 架构 |
|------|------|------|
| S4 | 固定参数 SSM | LTI + 卷积训练 |
| S5 | 多输入多输出 SSM | 向量化 S4 |
| Mamba | 选择性 + 并行扫描 | 输入相关参数 |
| Mamba-2 | 状态对偶性 | A, B, C 可大 → 更快 |
| Jamba | Mamba + Transformer 混合 | 8:1 层比例 |
| RecurrentGemma | Mamba 变体 (Griffin) | Google 的线性模型 |

---

## 七、Mamba-2 的改进

```
Mamba-1: A 是 d×d 矩阵 → h 是 d 维 → 每步 O(d²)
Mamba-2: 利用状态空间对偶性（SSD）
  → 可以用更大的状态（d_state >> d_model）
  → 类似 Attention 的 O(N²) 可以写成矩阵形式
  → 训练更快（类似 Flash Attention 的分块计算）

效果: Mamba-2 比 Mamba-1 快 2-8x（训练）
```

---

## 八、一句话总结

> Mamba = 选择性 SSM：输入相关参数 + 并行扫描 → O(N) 训练 + O(1) 推理。
>
> **推理时不需要 KV Cache** → 状态只有 d 维（vs Transformer 的 Nd 维）。
>
> Mamba-2 用状态空间对偶性 → 更大状态 + 更快训练。
>
> **Mamba 是 Attention 的有力竞争者——在长序列上已经超越 Transformer。**

---

*配套：attention-variants精读（`attention-variants-精读.md`） | transformer-attention-deep（`transformer-attention-deep-精读.md`） | flash-attention精读（`flash-attention-精读.md`）*
