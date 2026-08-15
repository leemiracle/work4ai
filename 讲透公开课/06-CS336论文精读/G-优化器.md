# G · 优化器与训练技巧（8 篇）

> 从 Adam 到 2024 年的 Muon/SOAP——训练大模型用什么优化器。
> 对应讲座：**L2（PyTorch + 优化器）**

> 📌 **基础优化器已在前面讲过**：Adam（[A8](./A-历史根基.md#a8)）、AdamW（[B9](./B-Transformer架构.md#b9)）、AdaGrad（[A6](./A-历史根基.md#a6)）、Xavier 初始化（[A5](./A-历史根基.md#a5)）。本文件专注 **2022 年之后的新优化器** 和补充技巧。

---

## G1. Adafactor (2018, Shazeer) ⭐⭐

- **链接**：原论文 [arxiv.org/abs/1804.04235](https://arxiv.org/abs/1804.04235)；PaLM 论文 §3 用它

**核心**：Adam 的 $v_t$（二阶矩）对每个参数存一个值，大模型上**显存巨大**。Adafactor 用**矩阵分解**——对二维权重 $W$，只存行统计和列统计，重构出近似的 $v$。显存从 $O(N)$ 降到 $O(\sqrt{N})$。

**💡 工程经验**：
1. **PaLM (540B) 用 Adafactor**——因为 Adam 的 optimizer state 在 540B 上要 ~2TB 显存，Adafactor 省一半。
2. 但 Adafactor 比 Adam 不稳定——需要更小学习率、更仔细调参。现代训练大多仍用 AdamW（显存靠 ZeRO/FSDP 解决，不靠优化器）。
3. **教训**：省显存的优化器往往牺牲稳定性。除非显存真不够，否则优先 AdamW。

---

## G2. LAMB (2019, You et al.) ⭐

- **链接**：[arxiv.org/abs/1904.00962](https://arxiv.org/abs/1904.00962)

**核心**：**Layer-wise Adaptive Moments**——为每一层单独缩放学习率（信任比例），支持**超大 batch**（64K+）训练。

**💡 工程经验**：Megascale（字节）训练用 LAMB 配合超大 batch。但 LLaMA 等仍用 AdamW——LAMB 的超大 batch 收益在现代 MFU 优化下不再明显。

---

## G3. SOAP – Speeding Up Adam via Shampoo (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2409.11321](https://arxiv.org/abs/2409.11321)

**核心**：结合 **Shampoo**（二阶优化器，用预条件矩阵）和 Adam 的效率。对权重的梯度做矩阵预条件（用左右统计的逆平方根），提升收敛速度。

**💡 工程经验**：在固定 token 预算下，SOAP 比 AdamW 收敛更快（少 ~20-30% 步数）。但每步计算更贵，总 FLOPs 收益取决于场景。Muon 是它的简化推广。

---

## G4. Muon – An Optimizer for Hidden Layers (2024) ⭐⭐⭐

- **链接**：[kellerjordan.github.io/posts/muon](https://kellerjordan.github.io/posts/muon/) · Keller Jordan

**核心**：**Muon（MomentUm Orthogonalized by Newton-Schulz）**——为**隐藏层的二维权重矩阵**设计的优化器。核心 trick：对动量更新矩阵做**正交化**（用 Newton-Schulz 迭代近似矩阵的逆平方根 $\approx$ 正交化），让更新方向更"均匀"分布在所有奇异方向上。

```
momentum = β·momentum + gradient
update = Newton-Schulz(momentum)   # 近似正交化
W -= lr · update
```

**💡 工程经验**：
1. **🔴 2024 年底最火的优化器**——在 ModularBrains 竞赛里，Muon 让小模型（数千万参数）训得比 AdamW 快得多。
2. **只用于隐藏层权重**（二维矩阵），embedding / 一维参数仍用 AdamW。
3. **直觉**：正交化让每个奇异方向的步长一致，避免"某些方向走太快、某些几乎不动"——类似二阶优化但便宜得多。
4. Muon 的争议：是否在**大模型**（>10B）上仍有效，尚未充分验证。CS336 关注但谨慎采用。
5. **Moonshot Kimi K2 系列** 据报道用 Muon 变体训练——这是 2025 工业验证的早期信号。

**📍 CS336 角色**：L2 前沿扩展。

---

## G5. GDN – Gradient Data Normalization (2024) ⭐

- **链接**：[arxiv.org/abs/2412.06464](https://arxiv.org/abs/2412.06464)

**核心**：训练稳定性的新技巧——对梯度做额外的归一化，缓解超大模型训练的 loss spike（突然飙升）问题。

**💡 工程经验**：超大模型（100B+）训练时 loss spike 是头号敌人（一次 spike 可能毁掉几天训练）。GDN、Z-loss、gradient clipping 都是应对手段。LLaMA-3 报告专门讨论了如何处理 spike。

---

## G6. 数值稳定性技巧合集（综合经验）⭐⭐

虽然不是单篇论文，但 CS336 L2 强调以下**训练稳定性必备技巧**：

| 技巧 | 作用 | 实践值 |
|------|------|--------|
| **Gradient clipping** | 防梯度爆炸 | clip 到 norm 1.0 |
| **Z-loss** | 防 logits 层 scale 爆炸 | 加 $10^{-4}\cdot\log^2 Z$ 到 loss |
| **BF16 训练** | 比 FP16 稳（无 loss scaling） | 现代默认 |
| **QK-Norm** (B12) | 防 attention logit 爆炸 | 大模型/长序列 |
| **Embedding 缩放** | 防 embedding 输出过大 | 乘 $\sqrt{d}$ |

**💡 核心经验**：**大模型训练 = 50% 算法 + 50% 数值工程**。LLaMA-3 技术报告花大量篇幅讲如何处理 spike——这说明即使顶级团队也常被稳定性折磨。

---

## G7. WRAP / 数据重复 (已在 D9) ⭐

见 [D9](./D-Scaling-Laws.md)。重复训练在某些场景有益。

---

## G8. 学习率调度的实践选择 ⭐⭐

| 调度 | 优点 | 缺点 | 代表模型 |
|------|------|------|---------|
| **Cosine** (D8) | 平滑收敛 | 须预定总步数 | LLaMA/GPT-3 |
| **WSD** (D7) | 可中途加数据 | decay 时机要调 | MiniCPM |
| **Linear decay** | 简单 | 收敛不如 cosine | 部分早期模型 |
| **Constant + decay** | 灵活 | 超参多 | Chinchilla |

**💡 经验**：默认用 cosine + warmup（前 1-2% 步线性升温）。如果训练中途可能加数据/改配置，用 WSD。

---

## G 类总结：优化器选择决策树

```
要不要省显存?
├─ 是 → Adafactor (但更不稳)
└─ 否 → AdamW (默认)

隐藏层二维权重?
├─ 是 → 试试 Muon (2024新, 可能更快)
└─ embedding/一维 → AdamW

需要超大 batch (64K+)?
└─ LAMB

训练不稳 / loss spike?
└─ 加 gradient clipping + Z-loss + QK-Norm + BF16
```

> **核心经验**：AdamW 仍是 2026 年的稳健默认。Muon/SOAP 是有前景的新选手，但工业大模型验证还不充分。**别为追新而换优化器**——稳定性 > 速度。
