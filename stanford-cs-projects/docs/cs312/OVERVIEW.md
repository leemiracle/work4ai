# CS312: Deep Learning Alchemy

> Stanford University（研究生研讨课）
> Instructors: **Mike Lam** + **Tatsunori Hashimoto**（Stanford NLP 领袖，HELM/RLHF 先驱）
> Format: 研究生研讨 + 大规模训练实战
> Prerequisites: CS230 / CS224N + PyTorch 熟练 + Linux/集群基础
> Difficulty: ⭐⭐⭐⭐⭐（"Alchemy"——深度学习的炼金术）
> 官网: http://cs312.stanford.edu/（内容随季度更新）

---

## 📚 课程定位

**CS312 的名字本身就是宣言**——"Deep Learning Alchemy"（深度学习炼金术）。

在学术界，训练大模型常常被戏称为"炼丹"：同样的架构、同样的数据，为什么有的能收敛、有的发散？为什么换个随机种子结果差 10 个点？CS312 正是要**把这种"玄学"变成工程**。

> **核心问题**：不是"深度学习是什么"，而是"**怎么把 loss 真正跑下来**"。

这门课填补了一个关键空白：CS230/CS224N 教你写模型代码，但**不教你如何让它在 GPU 集群上高效训练**。CS312 聚焦于：

- **训练不稳定**的根因与诊断（loss 爆炸、NaN、plateau）
- **优化器内部机制**（AdamW vs Adam、学习率调度、warmup）
- **大规模分布式训练**（DDP、FSDP、Pipeline 并行、ZeRO）
- **混合精度训练**（fp16/bf16、Loss Scaling）
- **训练监控与调试**（梯度直方图、激活值分布、权重统计）

### 讲师背景
- **Tatsunori Hashimoto**——Stanford NLP 组核心，研究方向涵盖 RLHF、指令微调、大规模评估（HELM）、可控文本生成。他的团队深度参与大模型训练实践
- **Mike Lam**——系统与 AI 交叉领域，关注训练基础设施

---

## 🎯 学习目标

完成 CS312 后，学生应能够：

1. **诊断** 训练过程中的各种病理现象（loss 不降、爆炸、NaN、plateau、震荡）
2. **实现** 生产级优化器（AdamW 含 warmup + 梯度裁剪 + 解耦权重衰减）
3. **设计** 学习率调度策略（cosine、linear warmup、step decay）
4. **掌握** 分布式训练范式（数据并行 vs 模型并行 vs 流水线并行）
5. **运用** 混合精度训练（AMP、bf16 的数值稳定性）
6. **构建** 完整的训练监控仪表盘（TensorBoard/W&B 的关键指标）
7. **复现** 顶会论文的训练设置（从 config 到 checkpoint）

---

## 📅 完整模块（推断版，基于课程主题）

### Part 1: 优化器深潜
- **M1** — SGD 家族回顾（SGD → Momentum → Nesterov）
- **M2** — 自适应优化器（AdaGrad → RMSprop → Adam）
- **M3** — **AdamW 与解耦权重衰减** ⭐
  - 为什么 Adam + L2 ≠ AdamW（Loshchilov & Hutter 2019）
  - 权重衰减的正则化与学习率缩放
- **M4** — 学习率调度（warmup → cosine/linear decay）

### Part 2: 训练稳定性
- **M5** — 梯度裁剪（by norm vs by value）
- **M6** — 初始化策略（Xavier → He → 0.02 std for Transformers）
- **M7** — 数值稳定性（LayerNorm vs BatchNorm vs RMSNorm）
- **M8** — Loss Scaling 与混合精度（fp16 溢出问题）

### Part 3: 分布式训练
- **M9** — 数据并行（DDP，AllReduce 通信）
- **M10** — 模型并行与 ZeRO 优化（DeepSpeed）
- **M11** — FSDP（Fully Sharded Data Parallel）
- **M12** — Pipeline 并行与张量并行（Megatron-LM）

### Part 4: 训练诊断与调试
- **M13** — **Loss 曲线诊断学** ⭐（课程核心特色）
- **M14** — 梯度/激活值监控（梯度消失/爆炸的检测）
- **M15** — 过拟合 vs 欠拟合 vs 优化困难的三分法
- **M16** — Checkpoint 管理与训练恢复

### Part 5: 大模型训练实战
- **M17** — Scaling Laws（Chinchilla、计算最优训练）
- **M18** — 预训练数据管道（tokenization、去重、混合配比）
- **M19** — 微调技术（全参 vs LoRA/QLoRA）
- **M20** — 课程项目：从零训练一个小型语言模型

---

## 🧮 核心算法

### 1. AdamW 优化器（课程核心）

Adam 的更新规则（带偏差校正）：
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t \quad \text{(一阶矩)}$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \quad \text{(二阶矩)}$$
$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t} \quad \text{(偏差校正)}$$

**Adam** 的权重衰减（与 L2 正则不等价）：
$$\theta_t = \theta_{t-1} - \eta \left( \frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon} + \lambda \theta_{t-1} \right) \quad \text{(耦合，错误)}$$

**AdamW** 的解耦权重衰减：
$$\theta_t = \theta_{t-1} - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon} - \eta \lambda \theta_{t-1} \quad \text{(解耦，正确)}$$

> **关键洞察**：在 Adam 中，L2 正则的梯度会被自适应缩放，而 AdamW 的权重衰减不经过自适应缩放，因此正则强度更可控。

### 2. 学习率 Warmup
$$\eta_t = \eta_{\max} \cdot \min\left(\frac{t}{T_{\text{warmup}}}, \frac{1}{2}\left(1 + \cos\left(\pi \frac{t - T_{\text{warmup}}}{T - T_{\text{warmup}}}\right)\right)\right)$$

Warmup 的必要性：训练初期二阶矩 $v_t$ 接近 0，偏差校正后步长极大，容易发散。

### 3. 梯度裁剪
- **按值裁剪**: $g_i \leftarrow \text{clip}(g_i, -c, c)$
- **按范数裁剪**（推荐）: 若 $\|g\|_2 > c$，则 $g \leftarrow \frac{c}{\|g\|_2} g$

### 4. Loss Scaling（混合精度）
$$\text{loss}_{\text{scaled}} = \text{loss} \times S$$
反向传播后梯度乘以 $1/S$ 恢复，避免 fp16 下梯度下溢为零。

---

## 💻 项目代码（本仓库）

📁 `supplementary/grad_projects.py::cs312_demo`

**实现内容**：
1. ✅ **AdamW 优化器**——完整实现一阶/二阶矩、偏差校正、解耦权重衰减
2. ✅ **Warmup 学习率**——线性 warmup 调度
3. ✅ **梯度裁剪**——按值裁剪（可扩展为范数裁剪）
4. ✅ **训练诊断器**——`diagnose_loss()` 函数自动检测 5 种病理：

| 诊断项 | 检测条件 | 可能原因 |
|--------|---------|---------|
| `loss_not_decreasing` | 末期 loss ≥ 初期 95% | lr 太小 / 数据问题 / 容量不足 |
| `loss_explosion` | max loss > 10× 初期 | lr 太大 / 梯度未裁剪 / 数值不稳定 |
| `loss_nan` | 含 NaN | log(0) / 除零 / fp16 溢出 |
| `loss_plateau` | 末期标准差 < 1e-4 | lr 已衰减 / 陷入局部最优 |
| `loss_oscillating` | 波动 > 末值 5% | lr 太大 / batch_size 太小 |

```bash
cd supplementary
python3 grad_projects.py
```

**输出示例**:
```
📋 CS312: Deep Learning Alchemy
   真实参数: w=2.0, b=1.0
   学到参数: w=1.987, b=0.994
   Loss: 1.234 → 0.012
   诊断: {'final_loss': 0.012, 'reduction_pct': 99.0, 'issues': []}
```

> 💡 这个 `diagnose_loss()` 函数是 CS312 精神的浓缩——**训练出问题时，第一步永远是看 loss 曲线**。

---

## 📊 关键论文

### 🔴 必读（P0）
1. **Loshchilov & Hutter 2019** "Decoupled Weight Decay Regularization" (AdamW, ICLR)
2. **Kingma & Ba 2015** "Adam: A Method for Stochastic Optimization" (ICLR)
3. **Hoffmann et al. 2022** "Training Compute-Optimal Large Language Models" (Chinchilla, NeurIPS)

### 🟡 推荐（P1）
4. **Goyal et al. 2017** "Accurate, Large Minibatch SGD" (Facebook 大 batch 训练，warmup 起源)
5. **Rajbhandari et al. 2020** "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"
6. **Narang et al. 2022** "Transformer Math 101"（EleutherAI 训练工程指南）
7. **You et al. 2020** "Large Batch Optimization for Deep Learning: Training BERT in 76 Minutes"

### 🟢 选读（P2）
8. **Micikevicius et al. 2018** "Mixed Precision Training" (NVIDIA, fp16)
9. **Chen et al. 2016** "Training Deep Nets with Sublinear Memory Cost" (梯度检查点)
10. Hu et al. 2022 "LoRA: Low-Rank Adaptation"（高效微调）

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **想训大模型** | CS230（基础）→ CS312（训练工程）→ CS224N（NLP 深入）|
| **想做 MLSys** | CS312 + CS149（并行计算）→ Megatron/DeepSpeed 源码 |
| **想复现论文** | CS312（训练技巧）+ 论文附录的 "Training Details" 章节 |
| **RLHF 工程** | CS312 + CS329H（理论）→ DeepSpeed-Chat / TRL 实践 |

### CS312 的独特价值
在斯坦福的课程矩阵中，CS312 占据一个**不可替代的位置**：

| 课程 | 教什么 | CS312 的差异 |
|------|--------|-------------|
| CS230 | DL 基础算法 | CS312 教**怎么训练**它们 |
| CS224N | NLP 模型设计 | CS312 教**怎么在大规模跑** |
| CS149 | 并行计算系统 | CS312 聚焦 **DL 特有的并行策略** |
| CS229 | ML 理论 | CS312 是**工程经验**而非理论 |

---

## 💡 反思

### 课程优势
1. **填补关键空白**——多数课程教"模型是什么"，CS312 教"怎么让它工作"
2. **工业级实用性**——内容直接来自大模型训练的前沿实践
3. **Hashimoto 的研究视角**——结合 NLP 组的实际训练经验（HELM eval、RLHF）
4. **诊断思维培养**——教的是系统性排错方法论，而非碎片技巧

### 潜在挑战
1. **硬件门槛高**——真正实践需要多 GPU 集群，个人难以复现
2. **经验性强**——部分内容是"best practice"而非严格理论，可能过时
3. **文档稀少**——cs312.stanford.edu 内容稀疏，主要靠课堂与讲义
4. **知识更新快**——训练技术每年迭代（如 2023→2024 的 bf16 普及、ZeRO-3 成熟）

---

## 🚀 扩展阅读

完成 CS312 后推荐：
1. **DeepSpeed 文档**——微软的大规模训练框架，ZeRO 系列的实现
2. **Megatron-LM**——NVIDIA 的张量并行实现
3. **CS149** — 并行计算基础，理解通信开销
4. **NVIDIA "Transformer Math 101"** — 训练算力估算的工程指南
5. **HuggingFace TRL 文档**——RLHF/LoRA 训练工具链
6. Karpathy 的 "nanoGPT"——从零实现 GPT 训练，最好的 CS312 补充练习

---

**最后更新**: 2026-08-11
**对应代码**: `supplementary/grad_projects.py::cs312_demo`（AdamW + 训练诊断）
**数据来源**: 课程主题推断 + Hashimoto Lab 研究 + 工业训练实践
