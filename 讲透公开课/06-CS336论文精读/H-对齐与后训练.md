# H · 对齐与后训练（9 篇）

> **CS336 2026 最新模块**——让"会续写"的预训练模型变成"会回答/会推理"的助手。
> 对应讲座：**L15（SFT/RLHF）、L16（RLVR）**｜ 作业：**A5（GRPO 训推理）**

---

## H1. Schulman et al. – PPO / Proximal Policy Optimization (2017) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1707.06347](https://arxiv.org/pdf/1707.06347.pdf) · OpenAI

**核心问题**：策略梯度（REINFORCE）方差大；Trust Region Policy Optimization (TRPO) 太复杂（解 KL 约束的二次规划）。能否简单又稳定？

**方法**：**截断重要性采样**。用旧策略 $\pi_{\theta_{old}}$ 采样数据，但用新策略 $\pi_\theta$ 计算梯度，比率 $r_t(\theta) = \pi_\theta(a_t|s_t)/\pi_{\theta_{old}}(a_t|s_t)$。为防止新策略偏离太远，**截断**目标：

$$L^{CLIP}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta)\hat A_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat A_t\right)\right]$$

$\epsilon \approx 0.2$，$\hat A_t$ 是优势函数估计。

**💡 工程经验**：
1. **PPO 是 RLHF 的标准 RL 算法**（InstructGPT 用它），直到 2024 年被 GRPO 部分取代。
2. PPO 需要**4 个模型**同时在线：actor（策略）、critic（价值网络）、reference（KL 约束）、reward model——显存压力极大（70B 模型 RL 要 4 倍）。
3. **clip 的直觉**：如果新策略比旧策略好太多（$r > 1+\epsilon$）或差太多（$r < 1-\epsilon$），就不再奖励这个方向——防止单步贪心导致崩溃。
4. CS336 2024 版用 PPO 做 A5，2026 版改 GRPO（见 H6）——因为 GRPO 省掉 critic，更省显存。

**📍 CS336 角色**：L15 RLHF 的算法基础。

---

## H2. Ouyang et al. – InstructGPT / RLHF (2022) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2203.02155](https://arxiv.org/pdf/2203.02155.pdf) · OpenAI

**核心问题**：GPT-3 会"续写"但不会"回答指令"——你问"法国首都"，它可能续写成"……是巴黎。下一段我们讨论……"而非直接答"巴黎"。如何让模型**遵循指令**？

**方法**：**三阶段对齐**：

1. **SFT (Supervised Fine-Tuning)**：用人类标注的（指令, 回答）对微调，让模型学会"指令 → 回答"格式。数据量小但贵（~13k 条）。

2. **RM (Reward Model)**：让模型对同一指令生成多个回答，人类**排序**偏好。训一个 RM 预测排序：
$$\text{loss} = -\log\sigma(r(x,y_{chosen}) - r(x,y_{rejected}))$$

3. **PPO**：用 RM 的分数当奖励，PPO 优化策略，**加 KL 惩罚**防止偏离 SFT 模型太远：
$$\max_\theta \mathbb{E}[r_\phi(x,y)] - \beta \cdot D_{KL}(\pi_\theta \| \pi_{SFT})$$

**关键结果**：1.3B 的 InstructGPT 的回答被人类偏好**胜过 175B 的 GPT-3**——证明对齐比堆参数更有效。

**💡 工程经验**：
1. **"对齐 > 规模"** 是这篇的核心洞察——小模型 + 对齐能打败大模型。催生了整个 instruction-tuning 浪潮。
2. **人类偏好数据是瓶颈**——贵、慢、有偏见。后来 DPO/GRPO 都在减少对它的依赖。
3. **KL 惩罚至关重要**——不加的话 PPO 会"reward hacking"（RM 的漏洞被利用，输出乱码但高分）。
4. **三阶段至今是对齐标准范式**，DPO 把 2+3 合并成一步。

**📍 CS336 角色**：L15 核心。

---

## H3. Taori et al. – Alpaca (2023) ⭐⭐

- **链接**：[crfm.stanford.edu/2023/03/13/alpaca.html](https://crfm.stanford.edu/2023/03/13/alpaca.html) · Stanford CRFM（Percy Liang 团队）

**核心**：**Self-Instruct**——用 text-davinci-003 自动生成 52k 条（指令, 回答）对，SFT LLaMA-7B。成本仅 ~$500。

**关键结果**：Alpaca-7B 在简单指令上**打平 text-davinci-003**——震惊业界（$500 复刻 GPT-3.5 的指令能力）。

**💡 工程经验**：
1. **"蒸馏即对齐"** 的廉价路线——用强模型生成数据，SFT 弱模型。但**有版权和蒸馏伦理问题**（OpenAI ToS 禁止用其输出训竞争模型）。
2. 52k 数据就能对齐——**质量 >> 数量**（呼应 LIMA H4）。
3. Alpaca 暴露的问题：**幻觉严重、不安全**（会教做炸弹）。纯 SFT 不够，需要 RLHF/DPO。

**📍 CS336 角色**：Percy 自己团队的成果，L15 案例。

---

## H4. Zhou et al. – LIMA / Less Is More for Alignment (2023) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2305.11206](https://arxiv.org/pdf/2305.11206.pdf)

**核心论点**：**对齐 = 知识激活，不是知识注入**。预训练已经给了知识，对齐只是"教模型用什么格式输出"。所以**1000 条精心筛选的数据就够了**，不需要 RLHF。

**方法**：手工筛选 **1000 条**高质量（指令, 回答），SFT LLaMA-65B。无 RL，无偏好数据。

**关键结果**：LIMA 在盲测中**接近 GPT-4 水平**（部分任务）——用 1/1000 的数据量。

**💡 工程经验**：
1. **"对齐是浅层的"** 这个假说极具启发性——但后来被质疑（RL 确实能提升推理等深层能力，见 R1）。
2. **数据质量是王道**——LIMA 的 1000 条全部来自社区论坛精帖 + 专家撰写，每条都是"范本"。
3. 实践启示：**先做高质量 SFT，再决定要不要 RL**。很多场景 SFT 就够了。

**📍 CS336 角色**：L15。

---

## H5. Rafailov et al. – DPO / Direct Preference Optimization (2023) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2305.18290](https://arxiv.org/pdf/2305.18290.pdf)

**核心问题**：RLHF 的 RM + PPO 太复杂（4 个模型、训练不稳、超参敏感）。能否直接用偏好数据训练？

**方法**：**数学洞察**——RLHF 的最优解有闭式形式。可以推导出：策略 $\pi^*$ 和 reward 满足 $r(x,y) = \beta\log\frac{\pi^*(y|x)}{\pi_{ref}(y|x)} + \text{const}$。把这个代回偏好排序的 Bradley-Terry 模型，得到一个**纯分类损失**（不需要 RM）：

$$\mathcal{L}_{DPO} = -\log\sigma\!\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)$$

其中 $(y_w, y_l)$ 是偏好对（chosen/rejected），$\beta$ 控制偏离参考模型的程度。

**💡 工程经验**：
1. **DPO 把 RLHF 从 3 步简化成 1 步**——直接用偏好对训练，无需训 RM、无需 PPO。**只需 2 个模型**（policy + reference，reference 冻结）。
2. **稳定性远好于 PPO**——是分类损失，梯度平滑。
3. **超参 $\beta$ 很敏感**：太小 → 过度偏离（崩溃）；太大 → 几乎不学。典型 0.1。
4. DPO 的局限：①依赖偏好数据质量；②对"伪标注"（如用强模型标注偏好）敏感；③不如 RL 在探索新策略上有效（所以 DeepSeek-R1 仍用 GRPO）。
5. CS336 A5 可选 Part 2 用 DPO 做 safety RLHF。

**📍 CS336 角色**：L15 + A5 Part 2。

---

## H6. Shao et al. – GRPO / DeepSeek-Math (2024) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2402.03300](https://arxiv.org/pdf/2402.03300.pdf) · DeepSeek

**核心问题**：PPO 需要 critic（value network）估计优势 $\hat A_t$——又一个和 policy 同样大的模型，显存翻倍。能否去掉？

**方法**：**Group Relative Policy Optimization**。对每个 prompt $x$，**采样 $G$ 个回答** $\{y_1...y_G\}$，用**组内相对奖励**当优势：

$$\hat A_i = \frac{r_i - \text{mean}(r_1...r_G)}{\text{std}(r_1...r_G)}$$

不再需要 critic 预测每个回答的"绝对价值"，而是用同组其他回答做参照系。

**💡 工程经验**：
1. **省掉 critic，显存减半**——这是 GRPO 最大的工程价值。70B 模型 RL 时，少一个 70B value network 是巨大的节省。
2. **组内归一化是关键**——绝对奖励数值难调（不同任务难度不同），归一化后自动适应。
3. GRPO 配合**规则奖励**（答案对/错，可验证）特别有效——这就是 RLVR（Reinforcement Learning from Verifiable Rewards），DeepSeek-R1 的核心。
4. **CS336 2026 版 A5 主线就是 GRPO**（测试文件 `test_grpo.py`）——从 2024 版的 PPO 切换过来，跟上 reasoning RL 浪潮。

**📍 CS336 角色**：**L16 + A5 核心**。

---

## H7. DeepSeek-AI – DeepSeek-R1 (2025) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2501.12948](https://arxiv.org/pdf/2501.12948.pdf)

**核心问题**：OpenAI o1 展示了"推理模型"（会反思、验证、长链思考）的强大能力，但没开源训练方法。能否复现？

**方法**：**两阶段**：

1. **R1-Zero（纯 RL，无 SFT 冷启动）**：直接在基座模型上用 GRPO + 规则奖励（数学/代码答案对错）+ 语言一致性奖励训练。**惊人地涌现出**长链推理、自我反思、验证行为。

2. **R1（SFT 冷启动 + RL）**：先用少量高质量推理数据 SFT（解决 R1-Zero 的可读性差、语言混杂问题），再 RL。

**关键结果**：R1 在数学/代码上**打平 o1**，且**完全开源**。催生整个 reasoning model 开源浪潮。

**💡 工程经验**：
1. **🔴 "推理能力可由 RL 涌现"** 是最大冲击——以前认为必须 SFT 蒸馏强模型的推理轨迹，R1-Zero 证明纯 RL + 可验证奖励就够。
2. **可验证奖励是关键**——数学/代码有客观对错，奖励信号干净。开放域对话没有，所以 RLVR 在推理任务上最有效。
3. **R1-Zero 的问题**：输出可读性差（中英混杂、格式乱）——说明纯 RL 优化的是奖励，不优化可读性。R1 加 SFT 解决。
4. **蒸馏路线**：R1 团队还用 R1 生成推理数据，SFT 小模型（1.5B-70B），效果惊人——**"大模型推理能力可蒸馏到小模型"**。
5. CS336 L16 RLVR + A5 GRPO = **让学生复现迷你 R1**。

**📍 CS336 角色**：**L16 核心**，A5 的思想源头。

---

## H8. Kimi Team – Kimi 1.5 (2025) ⭐⭐

- **链接**：[arxiv.org/abs/2501.12599](https://arxiv.org/pdf/2501.12599.pdf) · Moonshot

**核心**：另一个开源 reasoning model 报告。与 R1 互补地揭示了：**长 context + RL** 是推理能力的关键——把推理过程放到长上下文里，模型能"想得更久"。

**💡 工程经验**：与 R1 互相印证 RLVR 路线有效；提供了不同工程取舍的参考。

---

## H 类总结：对齐方法的进化树

```
预训练模型（会续写，不会回答）
   │
   ├─ SFT 路线（廉价、浅层）
   │   ├─ InstructGPT-SFT（人工标注）
   │   ├─ Alpaca（self-instruct 蒸馏，$500）
   │   └─ LIMA（1000 条精品，"对齐是浅层激活"）
   │
   ├─ RLHF 路线（深、贵）
   │   └─ InstructGPT（SFT→RM→PPO，3阶段）
   │           ↓ 简化
   ├─ DPO（去 RM，1步分类损失）
   │
   └─ RLVR 路线（推理涌现，2025最新）
       ├─ GRPO（去 critic，DeepSeek-Math）
       └─ DeepSeek-R1（纯RL涌现推理 + 可验证奖励）
              ↓
       CS336 A5 = 复现迷你 R1
```

> **核心经验**：对齐不是单一技术，是**从浅到深的谱系**。SFT 解决格式，DPO 解决偏好，RLVR 解决推理。选哪个取决于目标——做聊天助手用 SFT/DPO，做推理模型必须 RLVR。
