# A01 · JEPA 数学与 LeCun 路线

> **博士级目标**：基础层 [03 LeCun 的 JEPA 路线](../README.md) 给你直觉——JEPA = latent 空间预测，反对像素生成。本篇**严格化**：
> - 推导 JEPA 的能量函数形式
> - 对比 VICReg / BYOL / SimSiam 等 self-supervised loss
> - **LeCun 反对像素生成的数学论据**——为什么他说 "generative models are doomed"
> - JEPA 路线的当前进展与开放问题
>
> 预备：基础层 [00](../00-什么是世界模型.md) + 信息论（KL/entropy）+ 自监督学习基础。

---

## 一、JEPA 是什么——精确陈述

### 1.1 命名

**JEPA** = **J**oint **E**mbedding **P**redictive **A**rchitecture（联合嵌入预测架构）

**三个关键词**：
- **Joint**：两个 encoder 共同训练（context encoder + target encoder）
- **Embedding**：预测在 latent/embedding 空间，**不**在像素空间
- **Predictive**：核心是"从 context 预测 target"

### 1.2 架构（简化）

```
输入 x（图像/视频/音频）
    │
    ├── context x_c（部分观察）    target x_t（剩余部分）
    │       ↓                            ↓
    │   context encoder f_θ        target encoder g_φ（stop-gradient）
    │       ↓                            ↓
    │   s_c = f_θ(x_c)             s_t = g_φ(x_t)
    │       ↓                            ↓
    │   predictor h_θ(s_c, z)      ← latent 预测
    │       ↓
    │   ŝ_t = h_θ(s_c, z)
    │       ↓
    └── loss(ŝ_t, s_t)  ← 在 latent 空间最小化
```

**关键设计**：
1. **两个 encoder**：context encoder $f_\theta$ 和 target encoder $g_\phi$
2. **target encoder stop-gradient + EMA 更新**（防 collapse）
3. **predictor**：给定 context latent + mask token $z$，预测 target latent
4. **latent loss**：不重建像素，只匹配 latent

### 1.3 与生成模型的对比

| | **生成模型**（如 MAE、扩散）| **JEPA** |
|---|---|---|
| 预测对象 | 像素 | latent |
| Loss | 重建误差 | latent 距离 |
| 输出 | 可视化 | 不可视 |
| 关注 | "细节准不准" | "抽象对不对" |
| 风险 | 浪费算力学不可预测细节 | collapse 风险 |

---

## 二、能量函数视角（LeCun 的核心数学）

### 2.1 Energy-Based Model（EBM）框架

LeCun 长期推崇 EBM。world model 可表述为：

$$E(x, y) = \text{模型给出的"组合 }(x, y)\text{ 的不可信度"}$$

- $x$：当前状态
- $y$：候选下一状态（或预测）
- $E(x, y)$ 低 → 组合可信（"合理"）
- $E(x, y)$ 高 → 组合不可信（"违反 world 规律"）

### 2.2 JEPA 的能量函数

JEPA 的能量函数定义为：

$$E(x, y) = \|f_\theta(x) - g_\phi(y)\|^2$$

或更一般：

$$E(x, y) = \|h_\theta(f_\theta(x), z) - g_\phi(y)\|^2$$

其中 $h_\theta$ 是 predictor。

**直觉**：$f_\theta(x)$ 是 context 的 latent，$g_\phi(y)$ 是 target 的 latent，能量 = 它们的距离。

### 2.3 训练目标

**对比损失（contrastive loss）**——拉低正样本能量，推高负样本能量：

$$\mathcal{L} = \mathbb{E}_{(x, y^+) \sim \text{真实}}\left[E(x, y^+)\right] + \mathbb{E}_{y^- \sim \text{负样本}}\left[\max(0, m - E(x, y^-))\right]$$

其中 $m$ 是 margin。

**问题**：负样本怎么选？太难（near-positive）训不动，太简单（明显不对）学不到。

### 2.4 非对比方法——避免负样本

**VICReg** / **BYOL** / **SimSiam** 等**不用负样本**，靠 architectural tricks 防 collapse：

| 方法 | trick |
|---|---|
| **BYOL** | predictor + stop-gradient + EMA target |
| **SimSiam** | stop-gradient + EMA |
| **VICReg** | 显式约束 variance + invariance + covariance |

JEPA 系列主要用 BYOL/VICReg 风格。

---

## 三、VICReg 的数学（JEPA 常用 loss）

### 3.1 三个 loss 项

VICReg（Bardes et al. 2021, arXiv:2105.04906）的 loss：

$$\mathcal{L} = \lambda \mathcal{L}_{\text{invariance}} + \mu \mathcal{L}_{\text{variance}} + \nu \mathcal{L}_{\text{covariance}}$$

**1. Invariance（不变性）**：

$$\mathcal{L}_{\text{inv}} = \|f_\theta(x) - g_\phi(y)\|^2$$

让同一图像的两个 view 的 latent 接近。

**2. Variance（方差）**：

$$\mathcal{L}_{\text{var}} = \frac{1}{d}\sum_{i=1}^d \max(0, \gamma - \sqrt{\text{Var}(z_i) + \epsilon})$$

让每个 latent 维度的标准差 ≥ $\gamma$。**防 collapse 到一个点**。

**3. Covariance（协方差）**：

$$\mathcal{L}_{\text{cov}} = \frac{1}{d}\sum_{i \neq j} [C(z)]_{ij}^2$$

让 latent 不同维度**去相关**。**防 collapse 到一条线**。

### 3.2 为什么 VICReg 防 collapse

collapse 是 self-supervised 的最大风险——所有 latent 都变成同一个点，loss 也很低。

VICReg 三项分别防：
- variance → 防 point collapse
- covariance → 防 subspace collapse
- invariance → 学有用表示

### 3.3 在 JEPA 中用 VICReg

JEPA 把 invariance 项替换为 **prediction loss**（带 predictor），保留 variance + covariance 防 collapse。

---

## 四、为什么反对像素生成——LeCun 的论据

### 4.1 论据一：预测的不可预测性

**像素级世界大量不可预测**——树叶摇动、波浪、人群细节……即使最好的预测器也预测不准。

```
像素生成模型：
    给定当前帧 → 预测下一帧每个像素的颜色
    但下一帧哪些叶子动、动多少 —— 不可预测
    → loss 永远不会低，模型把算力浪费在不可预测的细节
```

### 4.2 论据二：抽象才是认知

**人类不预测视网膜每个光子**——大脑预测**概念级**未来：
- "球会滚下坡"
- "他会生气"
- "天要下雨"

这些是抽象预测，不是像素预测。JEPA 的 latent 预测更接近这种认知方式。

### 4.3 论据三：mode collapse vs diversity

**像素生成模型**面对不确定性时：
- GAN：mode collapse（生成单一答案）
- 扩散：sample 多样，但每次 sample 都"像幻觉"（不是真预测）

**JEPA**：latent 空间天然允许抽象，"球会到哪里"可以模糊。

### 4.4 反对声音

Sora 团队 / OpenAI 反驳：
- 像素生成虽然不完美，但**视觉上能模拟大量物理**（杯子会摔碎、布料会皱）
- "可预测性"假说**没有严格证明**——可能大模型就能预测
- 抽象 latent **不可视、难评估**

> 🎯 **这是 2024-2026 最热的争论**——详见 [A02](./03-视频生成是世界模型吗.md)。

---

## 五、JEPA 的演进（2022-2026）

### 5.1 I-JEPA（2023, arXiv:2301.08243）

**图像 JEPA**——Masked Image Modeling 的 JEPA 版本。

**结果**：
- 在 ImageNet linear probing 上**超过 MAE**
- 用 ~10% 算力达到掩码自监督相当的效果

### 5.2 V-JEPA（2024, arXiv:2404.02787）

**视频版 JEPA**——在视频上做 masked latent prediction。

**结果**：
- 在 action recognition 上达到 SOTA
- 在 video probing 任务上表现强

### 5.3 V-JEPA 2（2025）

进一步 scaling + 加入 downstream tasks（zero-shot）。

### 5.4 H-JEPA / Multimodal JEPA（探索中）

hierarchical JEPA——多层抽象（低层像素 → 高层概念）。

---

## 六、博士级练习题

### 6.1 推导题

**Q1**：从 EBM 视角，证明 VICReg 的三 loss 项在防止 collapse 上的作用（每项对应哪种 collapse）。

**Q2**：JEPA 的 predictor 为什么必须存在？如果直接最小化 $\|f_\theta(x) - g_\phi(y)\|^2$ 会怎样？（提示：BYOL 论文有讨论）

### 6.2 实验题

**Q3**：写一段 PyTorch 实现 VICReg loss（10-20 行），在小数据集（CIFAR-10）上跑通。

**Q4**：复现 I-JEPA 的核心：masked latent prediction。给定 ResNet-18 encoder +一个小 predictor，能学到有用表示吗？

### 6.3 批判题

**Q5**：LeCun 说"像素生成 doomed"——但 Sora 看起来很 work。LeCun 的论据成立吗？给出至少 2 个反例。

**Q6**：JEPA 的 latent 不可视——怎么评估它真的学到了 world model？这和 [`讲透可解释性`](../../讲透可解释性/) 是同一个问题吗？

**Q7**：VICReg vs BYOL vs SimSiam——在 JEPA 上哪个最好？为什么？

### 6.4 思考题（开放）

**Q8**：JEPA 在 latent 空间预测，但 latent 是哪一层？浅层（接近像素）还是深层（接近概念）？这影响什么？

**Q9**：人类大脑是 JEPA 风格吗？有神经科学证据吗？

**Q10**：如果有一天像素生成派（Sora 类）做出真 world model，LeCun 的论点怎么办？

---

## 七、关键引用

```bibtex
@article{lecun2022path,
  title={A Path Towards Autonomous Machine Intelligence},
  author={LeCun, Yann},
  journal={OpenReview},
  year={2022}
}

@article{assran2023ijepa,
  title={Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture},
  author={Assran, Mahmoud and others},
  journal={arXiv:2301.08243},
  year={2023}
}

@article{bardes2021vicreg,
  title={VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning},
  author={Bardes, Adrien and others},
  journal={arXiv:2105.04906 (ICLR 2022)},
  year={2021}
}
```

---

## 八、一句话总结

> 🎯 **博士级五句话**：
> 1. **JEPA = Joint Embedding Predictive Architecture**——在 latent 空间预测，反对像素生成。
> 2. **数学核心**：能量函数 $E(x, y) = \|f_\theta(x) - g_\phi(y)\|^2$ + VICReg 三项（invariance/variance/covariance）防 collapse。
> 3. **LeCun 反对像素生成的论据**：不可预测的细节浪费算力、抽象才是认知、mode collapse 风险。
> 4. **当前进展**：I-JEPA / V-JEPA / V-JEPA 2——在自监督任务上效果 SOTA，但"是不是 world model"未定论。
> 5. **博士级核心**：JEPA vs 像素生成是**方法论分歧**——抽象预测 vs 具体重建，**没有定论，看 [A02](./03-视频生成是世界模型吗.md) 的另一面**。

---

📌 **下一步**

1. **做 Q1-Q4**：VICReg 推导 + PyTorch 实现（CPU 即可）。
2. **深读 I-JEPA + VICReg 原文**：按 [A00 论文清单](./05-论文清单.md) 的 L3 标准。
3. **进入 [A02 视频生成是世界模型吗](./03-视频生成是世界模型吗.md)**：另一派的论据。
4. **思考 Q8-Q10**：每个都是博士论文级方向，特别是 Q10（如果 LeCun 错了）。
