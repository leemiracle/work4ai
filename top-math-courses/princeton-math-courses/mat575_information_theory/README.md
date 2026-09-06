# Princeton MAT 575 — Information Theory

> **学校**：Princeton | **学期**：Spring (研究生)
> **一手来源**：[math.princeton.edu/graduate](https://www.math.princeton.edu/graduate)

## 课程信息
- **编号**：MAT 575
- **先修**：MAT 514 概率（或同等）
- **教材**：Cover & Thomas, *Elements of Information Theory* (2nd ed, Wiley)
- **特色**：**Princeton 罕见的信息论研究生课**

## 教学大纲
1. **Entropy & mutual information** ★
2. **Asymptotic equipartition property (AEP)**
3. **Data compression**（信源编码、Huffman、Arithmetic coding）
4. **Channel capacity**（信道容量、Shannon 定理）
5. **Differential entropy**
6. **Maximum entropy principle**
7. **Rate-distortion theory**
8. **Network information theory 入门**

## 与 ML 的关联（**信息论 = ML 理论的另一只手**）
- **Cross-entropy loss** 的本质
- **KL divergence**：VAE / diffusion models
- **互信息**：representation learning、InfoNCE
- **学完本课后**：能解释为什么 ML 训练用 cross-entropy

## 参考资源
- **教材**：Cover & Thomas, *Elements of Information Theory* (2006) — 必读经典
- **替代**：MacKay, *Information Theory, Inference, and Learning Algorithms* (Cambridge, 2003, 免费 PDF)
- **MIT 对照**：MIT 18.424 Seminar in Information Theory

## 学习建议
- **节奏**：每周 5-6 小时，12 周
- **Cover & Thomas 第 2、7、8、9 章是 ML 必读**

---

## 📍 在数学全景中的位置

```
概率论基础                         信息论                          ML 信息论应用
──────────                        ──────                          ────────────
MAT 514 概率 ──→  MAT 575 信息论 ──→  VAE ELBO / cross-entropy loss
(测度论概率)       (Cover & Thomas)     diffusion model (KL 退化)
                                       RLHF (KL 正则化)
                                       DPO (隐式 KL 约束)
```

- **前置**：[MAT 514 概率](../mat514_probability/)（概率公理、期望、收敛定理）
- **本课**：Shannon 熵、互信息、KL 散度、信道编码定理、率失真理论
- **后续**：ML 中的信息论方法（信息瓶颈、表示学习 InfoNCE、信息论泛化界）

---

## 🔬 理论联系实际

| 信息论概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Shannon 熵** $H(X)$ | 决策树 / 模型压缩 | $H(X) = -\sum_x p(x)\log p(x)$ → ID3/C4.5 选择信息增益最大的特征分裂 |
| **Cross-entropy loss** | 分类损失函数 | $\mathcal{L} = -\sum_y p_{\text{true}}(y)\log q_\theta(y) = H(p) + \text{KL}(p\|q)$ |
| **KL 散度** | VAE ELBO / RLHF / DPO | $\text{ELBO} = \mathbb{E}_q[\log p(x|z)] - \text{KL}(q(z|x)\|p(z))$ → 变分推断 |
| **互信息** $I(X;Y)$ | 表示学习 / InfoNCE | $I(X;Y) = H(X) - H(X|Y) = \text{KL}(p(x,y)\|p(x)p(y))$ → 对比学习的理论基础 |
| **数据压缩** $L \geq H$ | 模型量化 / 剪枝 | Huffman 编码平均码长 $\bar{L} \in [H, H+1)$ → LLM 中的权重压缩 |
| **信道容量** $C$ | 通信理论 / 多任务瓶颈 | $C = \max_{p(x)} I(X;Y)$ → 信息瓶颈方法 $\min I(Z;X) - \beta I(Z;Y)$ |
| **微分熵** $h(X)$ | 连续 VAE / 正则化 | $h(\mathcal{N}(0,\sigma^2)) = \frac{1}{2}\log(2\pi e \sigma^2)$ → VAE 中高斯先验 |
| **率失真** $R(D)$ | 有损压缩 / 模型蒸馏 | $R(D) = \min_{p(\hat{x}|x): E[d] \leq D} I(X;\hat{X})$ → 知识蒸馏的信息论视角 |

**核心洞察**：KL 散度是 VAE / diffusion / RLHF / DPO 的**统一语言**——
- VAE：最大化 ELBO = 最小化 $\text{KL}(q(z|x)\|p(z|x))$
- Diffusion：正向加噪最小化 $\text{KL}(q(x_{t-1}|x_t,x_0)\|p_\theta(x_{t-1}|x_t))$
- RLHF：$\max_\theta \mathbb{E}[r] - \beta \text{KL}(\pi_\theta\|\pi_{\text{ref}})$
- DPO：$\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \geq 0$（隐式 KL 约束）

---

## 🆕 2024-2026 最新研究

1. **Diffusion model 的信息论基础** ⭐
   - 扩散模型可理解为**逐步降噪的率失真优化**：每一步的 KL 散度对应一个率失真码
   - 2024 进展：Consistency Models（Song et al., arXiv:2303.01469）将多步扩散压缩为单步生成，信息论上等价于跳过中间 KL 项
   - **与本课关联**：正向 SDE 的每步 KL = $D_{\text{KL}}(q(x_{t-1}|x_t) \| p_\theta(x_{t-1}|x_t))$，总 ELBO = 重建项 + KL 退化项之和

2. **信息瓶颈（Information Bottleneck）用于深度学习可解释性** ⭐
   - Tishby 学派：训练动态 = "拟合阶段"（$I(Z;X) \uparrow$）→ "压缩阶段"（$I(Z;X) \downarrow$）
   - 2024-2025 争议：信息瓶颈是否普遍描述泛化？大规模实验给出混合结论
   - **与本课关联**：信息瓶颈目标 $\min_{p(z|x)} I(Z;X) - \beta I(Z;Y)$ = 率失真的推广

3. **信息论泛化界（Information-theoretic generalization bounds）** ⭐
   - 2024 热点：用**互信息** $I(W;S)$（算法输出与训练数据的互信息）控制泛化
   - PAC-Bayes 的信息论推广：$R(h) \leq \hat{R}(h) + \sqrt{\frac{\text{KL}(Q\|P) + \ln(2\sqrt{n}/\delta)}{2n}}$
   - **与本课关联**：Pinsker 不等式 $\text{TV}(P,Q) \leq \sqrt{\text{KL}(P\|Q)/2}$ 连接 KL 与泛化

📌 **下一步**：→ [Berkeley Math 218](../../berkeley-math-courses/math218_probability_graduate/) 或 [MIT 18.175](../../mit-math-courses/18_175_probability/)
