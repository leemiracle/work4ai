# 04 FFN 与激活变体：从 ReLU 到 GELU 到 SwiGLU

> FFN (前馈网络) 是 Transformer Block 的"第二公民", 却占了模型 **2/3 的参数**。
> 激活函数的选择在 2017-2023 完成了一次迁移: ReLU → GELU → **SwiGLU** (现代标准)。

---

## FFN 在 Transformer 里的角色

每个 Block = Attention (词之间混合) + **FFN (每个位置独立做非线性变换)**:
$$\text{FFN}(x) = W_2 \cdot \sigma(W_1 x + b_1) + b_2$$

**直觉**: Attention 负责"信息在词之间流动", FFN 负责"每个词的特征变换/记忆存储"。FFN 的中间维度通常是 $4 d_{model}$, 所以它**参数量最大** (约 2/3)。

---

## 激活函数演化

```
ReLU  (2017 原版)    简单快, 但死 ReLU + 0 点不可导
  │
  ▼
GELU  (BERT/GPT)     处处可导, 概率门控, 训练更稳
  │
  ▼
SwiGLU (2020, PaLM)  门控版 GLU, 现代标准, 需配 8/3 扩展维度
```

### 1. ReLU (原版 Transformer)

$$\text{ReLU}(x) = \max(0, x)$$

原版用 ReLU。问题: 0 点不可导, 死 ReLU (你学过的激活函数课)。

### 2. GELU (BERT/GPT-2 时代)

$$\text{GELU}(x) = x \cdot \Phi(x) \approx 0.5x\left(1 + \tanh\left[\frac{\sqrt{2}}{\pi}(x + 0.044715 x^3)\right]\right)$$

直觉: "以 x 为正的概率作为权重"。处处可导, 平滑, 比 ReLU 训练更稳。BERT/GPT-2/GPT-3 全用它。你实验里的 mini-GPT 也是 GELU。

### 3. SwiGLU — 现代标准 🔥

Shazeer 2020 发现: 把 FFN 第一层的激活换成**门控线性单元 (GLU)**, 效果显著提升:
$$\text{SwiGLU}(x) = \text{Swish}(x W_1) \odot (x W_2), \quad \text{Swish}(x) = x \cdot \sigma(\beta x)$$

- 两个并行投影 $W_1, W_2$, 一个用 Swish 激活, 一个作"门"逐元素相乘。
- **门控机制**: 模型能动态决定哪些特征通过, 表达力更强。

**维度调整**: GLU 有 3 个权重矩阵 (不是 2 个), 为保持参数量不变, 中间维度从 $4d$ 调成 $\frac{8}{3}d$ (向上取整到 256 的倍数)。

**谁用**: LLaMA 全家、PaLM、Qwen、DeepSeek、Mistral、Mixtral——**2023+ 几乎所有主流模型**。

---

## 2023-2026 的"LLaMA 配方"

jytan.net 统计 53 个模型发现, FFN 部分高度收敛:
$$\boxed{\text{SwiGLU} + \frac{8}{3} \text{ 扩展维度} + \text{无 bias}}$$

> **为什么无 bias**: bias 项贡献小但破坏量化/加速 kernel, 现代模型基本砍掉所有 bias (有时只保留 QKV 的 bias)。

---

## MoE: FFN 的革命 (06 篇详谈)

当 FFN 占 2/3 参数, 稀疏化它收益最大。**MoE 把单个 FFN 换成 N 个"专家 FFN"**, 每次只激活少数几个:
$$\text{FFN}_{\text{MoE}}(x) = \sum_{i \in \text{top-k}} g_i(x) \cdot \text{Expert}_i(x)$$

这就是 Mixtral / DeepSeek-V3 / Llama 4 的核心。详见 06 篇。

---

## 速查

| 激活 | 公式特征 | 代表 | 时代 |
|------|---------|------|------|
| ReLU | $\max(0,x)$ | 原版 Transformer | 2017 |
| GELU | $x\Phi(x)$ | BERT, GPT-2/3 | 2018-2020 |
| **SwiGLU** | 门控 Swish | **LLaMA/PaLM/Qwen/DeepSeek** | 2020+ (现代标准) |

---

## 参考文献
- Hendrycks & Gimpel 2016, *Gaussian Error Linear Units* (GELU)
- Shazeer 2020, *GLU Variants Improve Transformer* (SwiGLU)
- jytan.net 2025, *The Crystallization of Transformer Architectures*
