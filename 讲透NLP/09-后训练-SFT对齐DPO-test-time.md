# 09 — 后训练：SFT、对齐、DPO 与 Test-Time Compute

> **基座模型会预测下一个 token，但不会"听话"。** 这一章讲怎么把一个只会续写文本的基座模型，变成一个会回答问题、遵循指令、拒绝有害请求的助手——SFT 教它"说什么"，RLHF/DPO 教它"什么更好"。
>
> 配套实验：`experiments/09_dpo_vs_sft.py`——在 tiny GPT 上对比 SFT 与 DPO，揭示两个反直觉发现。

---

## 0. 开篇：基座模型的两宗罪

基座模型（base model）经过了海量预训练（pretraining），拥有了惊人的语言能力。但 SLP3 开篇就给出两个翻车案例（来自早期 GPT）：

> **Prompt:** Explain the moon landing to a six year old in a few sentences.
> **Output:** Explain the theory of gravity to a 6 year old.

> **Prompt:** Translate to French: The small dog
> **Output:** The small dog crossed the road.

模型没有"理解"指令——它只是**续写**了一段看起来差不多的文本。SLP3 总结了两宗罪：

| 罪状 | 表现 | 根因 |
|------|------|------|
| **不够有用** (not helpful) | 不遵循指令、续写而非回答 | 预训练目标 = 预测下一个 token，与"帮助用户"不对齐 |
| **不够安全** (not harmless) | 生成有害/有毒/有偏见的内容 | 互联网文本本身包含这些内容 |

这两个问题统称为**对齐问题**（alignment problem）：预训练目标与人类需求之间存在鸿沟。后训练（post-training）就是填补这个鸿沟的工程。

```mermaid
graph LR
    A[Pretraining<br/>预测下一个 token] -->|预训练| B[Base Model<br/>会续写, 不会听话]
    B -->|SFT| C[Instruction-Tuned<br/>会遵循指令]
    C -->|RLHF / DPO| D[Aligned Model<br/>有用 + 无害]
    D -.->|Test-Time Compute<br/>CoT / Best-of-N| E[更强的推理能力]
```

SLP3 将后训练分为三个层次：

1. **指令微调（Instruction Tuning / SFT）**——在"指令-回答"对上继续训练，教模型遵循指令
2. **偏好对齐（Preference Alignment / RLHF / DPO）**——用人类偏好数据，教模型区分好坏
3. **测试时计算（Test-Time Compute）**——推理阶段用更多计算换取更好输出（CoT、Best-of-N）

---

## 1. SFT：监督微调

### 1.1 直觉

> **SFT = 在"指令-好回答"数据上继续做 next-token prediction。**

就这么简单。预训练时模型看到的是海量互联网文本；SFT 时模型看到的是精心标注的"问题-回答"对。训练目标完全相同——交叉熵损失（cross-entropy loss）——只是**数据变了**。

这就像一个读过整个图书馆的人（预训练），现在被送进客服培训学校（SFT），虽然培训内容只是"看到这个问题，应该这样回答"，但他突然就学会了"对话"。

**为什么叫"监督"微调？** 因为每条数据都有正确答案（人类标注的回答），不同于预训练的自监督（self-supervised）性质。

**与其他微调的区别**（SLP3 Fig 9.1）：

| 微调类型 | 数据 | 训练对象 | 目标 |
|---------|------|---------|------|
| 继续预训练 | 新领域文本 | 全部参数 | 域适配 |
| PEFT (LoRA) | 新领域文本 | 仅新增小参数 (A, B 矩阵) | 高效域适配 |
| 任务微调 | 特定任务标注 | 仅分类头 (+部分参数) | 单任务优化 |
| **指令微调 (SFT)** | **多样指令-回答** | **全部参数** | **学会遵循指令** |

### 1.2 数学

SFT 的损失就是标准的负对数似然（negative log-likelihood），对回答部分的每个 token 计算：

$$\mathcal{L}_{\text{SFT}} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log p_\theta(y_t \mid x, y_{<t})$$

其中 $x$ 是指令/提示（prompt），$y$ 是期望的回答（response），$y_{<t}$ 是回答中第 $t$ 个 token 之前的所有 token。

**关键细节**：prompt 部分的 loss 被屏蔽（masked）——我们不对 prompt token 计算 loss，只对 response token 计算。这在实践中通过 loss mask 实现。

### 1.3 指令数据的来源

SLP3 列出了四种创建指令数据的方法：

1. **人工撰写**：如 Aya 数据集——3000 名标注者用 65 种语言手写了 204K 条指令-回答对
2. **现有 NLP 数据集转换**：将 SQuAD、摘要等任务数据用模板（template）包装成指令格式
3. **标注指南复用**：把 crowdworker 的标注指南直接当作指令
4. **LLM 辅助生成**：用已有 LLM 生成新的指令-回答对（如 Bianchi et al. 2024 用 LLM 生成安全回答）

**评估方法**：留一法（leave-one-out）——在大量任务上训练，在留出的任务簇（task cluster）上测试。例如 SuperNatural Instructions 有 76 个任务簇，覆盖 1600 个数据集。

### 1.4 SFT 的局限

SFT 让模型学会了"好回答长什么样"，但有两个根本局限：

1. **没有对比信号**：SFT 只告诉模型"这是好回答"，不告诉它"这是坏回答"。模型的注意力全在模仿好回答上，对坏回答的概率变化是**附带效应**——这正是我们实验要揭示的反直觉发现 2。

2. **无法覆盖所有好坏判断**：SFT 数据有限，但"什么是好回答"的空间是无限的。模型可能在 SFT 数据上表现完美，但面对新的、微妙的场景时仍然翻车。

> 🧪 **反直觉发现 2（实验验证）**：SFT 在好回答上 P 上升时，坏回答的 P 也在变——而且可能**先升后降**。因为好回答和坏回答可能共享 token（如都以 EOS 结尾、共享首词），SFT 抬高共享 token 的概率时，坏回答的概率也被附带抬高了。SFT 完全不知道哪个回答是"坏"的。

---

## 2. 从偏好学习：RLHF 的框架

### 2.1 为什么需要偏好信号？

SFT 之后，模型已经会对话了。但"会对话"不等于"说得好"。偏好学习（preference-based learning）的核心理念是：

> **你不需要知道怎么做，只需要知道什么更好。**

人类标注者不需要写出完美的回答（SFT 需要这个），只需要在两个候选回答中**选出更好的一个**。这让标注成本大大降低，覆盖面大大增加。

### 2.2 偏好数据

偏好数据的格式是三元组 $(x, y_w, y_l)$：给定 prompt $x$，回答 $y_w$（chosen/winner）比 $y_l$（rejected/loser）更好，记作 $(y_w \succ y_l \mid x)$。

数据来源（SLP3 列举三种）：
- **人工标注**：训练标注员对模型输出排序（如 InstructGPT 让标注员对 4 个输出排序，产生 $\binom{4}{2} = 6$ 个偏好对）
- **隐式偏好**：Reddit 点赞、StackExchange 高票回答 → 偏好信号
- **LLM 辅助**：用 GPT-4 给输出打分/排序（如 UltraFeedback 数据集）

### 2.3 Bradley-Terry 模型：把偏好变成概率

**核心问题**：我们有一个偏好判断 "$y_w$ 比 $y_l$ 好"，但怎么把它变成一个可以优化的概率？

SLP3 使用 **Bradley-Terry 模型**（1952）——一个经典的偏好概率模型：

假设每个回答 $y$ 都有一个隐含的标量分数 $z = r(x, y)$（即 reward），偏好的概率是分数差的 sigmoid：

$$P(y_w \succ y_l \mid x) = \sigma(r(x, y_w) - r(x, y_l)) = \frac{1}{1 + e^{-(r(x,y_w) - r(x,y_l))}}$$

**为什么是 sigmoid？** 推导和逻辑回归完全一样——把分数差 $\delta = r(x, y_w) - r(x, y_l)$ 当作 logit（log-odds）：

$$\delta = \log \frac{P(y_w \succ y_l \mid x)}{1 - P(y_w \succ y_l \mid x)}$$

反解即得 sigmoid 形式。Bradley-Terry 的优点：
- 分数接近时 $P \approx 0.5$（弱偏好）
- 分数差距大时 $P \to 1$ 或 $P \to 0$（强偏好）
- 导数友好，可用交叉熵直接优化

### 2.4 奖励模型（Reward Model）

有了 Bradley-Terry 框架，下一步是学习奖励函数 $r(x, y)$。

**方法**：用一个预训练 LLM，去掉语言建模头（LM head），换成一个线性层输出标量。用偏好数据训练，损失是负对数似然：

$$\mathcal{L}_{\text{RM}} = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[\log \sigma(r(x, y_w) - r(x, y_l))\right]$$

训练后的奖励模型可以给任意 (prompt, response) 打分——这就是 RLHF 中"人类偏好的代理"。

> **奖励模型的工程价值**（SLP3 指出）：不只是用于对齐。还可以用于 Best-of-N 采样（从 $N$ 个候选中选奖励最高的）和指令数据筛选。

### 2.5 RLHF：用 PPO 优化策略

有了奖励模型 $r_\phi(x, y)$，就可以用强化学习优化 LLM 策略 $\pi_\theta$。SLP3 给出的 RL 映射：

| RL 概念 | LLM 对齐中的含义 |
|---------|-----------------|
| Action（动作） | 选择下一个 token |
| State（状态） | 当前已生成的上下文 |
| Policy（策略） | LLM 的概率分布 $\pi_\theta$ |
| Reward（奖励） | 奖励模型 $r_\phi(x, y)$ 的评分 |

**朴素目标**：最大化期望奖励：

$$\pi^* = \arg\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot \mid x)} [r_\phi(x, y)]$$

**问题**：如果只优化奖励，模型会**忘记预训练学到的一切**——它会发现某个固定回答在所有 prompt 上都有高奖励，于是永远输出那个回答（reward hacking）。

**解法**：加 KL 散度惩罚，防止策略偏离参考模型太远：

$$\pi^* = \arg\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta} \left[r_\phi(x, y) - \beta \log \frac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)}\right]$$

其中 $\pi_{\text{ref}}$ 是 SFT 后的参考模型（冻结），$\beta$ 是 KL 惩罚强度。

> **PPO 的工程痛点**（SLP3 9.3.1 在此 draft 中标记为 "TBD"，但实践已知）：
> - 需要同时维护 **4 个模型**：policy $\pi_\theta$、value network $V_\phi$、reference model $\pi_{\text{ref}}$、reward model $r_\phi$
> - 需要在训练中**在线采样**（online sampling）——从 $\pi_\theta$ 生成回答再评估奖励
> - 训练**不稳定**——RL 的方差大，超参数敏感
> - 显存翻倍——4 个模型同时在 GPU 上

这就是 DPO 诞生的动机。

---

## 3. DPO：直接偏好优化

### 3.1 核心洞察

DPO（Rafailov et al., 2023）的论文标题点明了核心洞察：

> **Your Language Model Is Secretly a Reward Model.**
> （你的语言模型暗地里就是一个奖励模型。）

DPO 的思路是：我们不需要显式地训练一个奖励模型，再用 PPO 去优化策略。**RL 目标有一个闭式解（closed-form solution），可以把奖励函数重写为策略的函数**，从而直接从偏好数据优化策略，一阶段搞定。

### 3.2 完整推导

**Step 1：从 RL 目标到闭式解**

KL 约束下的奖励最大化是一个带约束的优化问题。根据凸优化理论，最优策略有闭式解：

$$\pi^*(y \mid x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y \mid x) \exp\left(\frac{r(x, y)}{\beta}\right)$$

其中 $Z(x) = \sum_y \pi_{\text{ref}}(y \mid x) \exp\left(\frac{r(x,y)}{\beta}\right)$ 是配分函数（partition function），保证 $\pi^*$ 是合法的概率分布。

> 直觉：最优策略 = 参考策略被 $\exp(r/\beta)$ 重新加权后归一化。奖励越高的回答，概率被放大越多；$\beta$ 越大，放大越温和。

**Step 2：反解奖励函数**

把闭式解重排，用策略表示奖励：

$$r(x, y) = \beta \log \frac{\pi^*(y \mid x)}{\pi_{\text{ref}}(y \mid x)} + \beta \log Z(x)$$

> 直觉：奖励 = 策略相对于参考模型的对数概率比 $\times \beta$ + 一个仅依赖 prompt 的常数。

**Step 3：代入 Bradley-Terry，配分函数消去**

将 Step 2 的奖励代入 Bradley-Terry 模型 $P(y_w \succ y_l \mid x) = \sigma(r(x, y_w) - r(x, y_l))$：

$$r(x, y_w) - r(x, y_l) = \beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}$$

注意 $\beta \log Z(x)$ 项在作差时**消去了**！这正是 DPO 的魔法——我们不需要计算无法处理的配分函数。

$$\boxed{P(y_w \succ y_l \mid x) = \sigma\left(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\right)}$$

**Step 4：DPO 损失 = 负对数似然**

$$\boxed{\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\right)\right]}$$

**没有奖励模型，没有 RL 采样，没有 PPO。** 只需要一个冻结的参考模型 $\pi_{\text{ref}}$ 和偏好数据 $(x, y_w, y_l)$。

### 3.3 DPO 损失在做什么？

操作性地理解 DPO 梯度的行为：

- **增大** $\log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)}$——提高好回答相对于参考模型的概率
- **减小** $\log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}$——压低坏回答相对于参考模型的概率
- **β 控制**偏离参考模型的幅度——β 大 = 保守（慢但安全），β 小 = 激进（快但危险）

典型 β 值：0.01 ~ 0.5（SLP3 指出 0.01-0.1）。

### 3.4 DPO vs PPO

| | PPO (RLHF) | DPO |
|---|---|---|
| 奖励模型 | 需要，显式训练 | **不需要** |
| 在线采样 | 需要，从 $\pi_\theta$ 生成 | **不需要** |
| 训练阶段 | 两阶段（RM + PPO） | **一阶段** |
| 模型数量 | **4 个**（policy + value + ref + RM） | **2 个**（policy + ref） |
| 稳定性 | 不稳定（RL 方差大） | 稳定（类似 SFT） |
| 探索性 | **强**（在线采样探索新回答） | **弱**（只能优化已有偏好对） |
| 典型 β | ~0.01-0.1 | ~0.1-0.5 |

> **DPO 的代价**：DPO 省掉了在线采样，但这也意味着它**无法发现训练数据中不存在的新回答**。PPO 可以通过探索发现"模型从没生成过但奖励很高"的回答，DPO 只能在已有回答之间做偏好排序。

---

## 4. Test-Time Compute：推理时多花钱，输出更聪明

### 4.1 一个新维度

SLP3 在本章末尾引入了一个全新的概念：**测试时计算**（test-time compute）。

传统观点：模型训练好之后，参数固定，推理就是简单的前向传播。能力上限由训练决定。

新范式（2024-2025）：**在推理阶段花更多计算，可以换取更好的输出**。这不是改变模型参数，而是改变**推理策略**。

> 这正是 OpenAI o1（2024.09）和 DeepSeek R1（2025.01）的核心思想：让模型在输出最终答案之前，先"思考"很长时间。

### 4.2 Chain-of-Thought (CoT)

**思路**：让模型在给出答案前，先输出中间推理步骤。

**Zero-shot CoT**（Kojima et al., 2022）：在 prompt 末尾加上一句魔法咒语：

> "Let's think step by step."

**Few-shot CoT**（Wei et al., 2022）：在 few-shot 示例中展示推理过程：

```
Q: Roger has 5 balls. He buys 2 more cans...
A: Let's think step by step.
   Roger started with 5 balls. 2 cans × 3 balls = 6 balls.
   5 + 6 = 11. The answer is 11.
```

SLP3 引用了 BIG-Bench-Hard 的实验结果：CoT 让 Codex 在 23 个推理任务中的 17 个上超过人类标注者（标准 prompting 只有 5 个）。

### 4.3 Self-Consistency

**问题**：CoT 的推理路径可能出错。

**解法**：生成 $N$ 条不同的推理链（用 temperature > 0 采样），取**多数投票**（majority vote）作为最终答案。

$$\hat{a} = \text{majority\_vote}\{a_1, a_2, \ldots, a_N\}$$

直觉：如果多条不同的推理路径都得到相同答案，这个答案更可能是对的。

### 4.4 Best-of-N

**思路**：用奖励模型（或 LLM 评判）从 $N$ 个候选回答中选最好的。

$$y^* = \arg\max_{y_i} r(x, y_i), \quad y_i \sim \pi_\theta(\cdot \mid x), \ i = 1, \ldots, N$$

**计算-质量权衡**：$N$ 越大，质量越好，但计算成本线性增长。

### 4.5 Tree-of-Thoughts (ToT)

**思路**：把推理建模为**树搜索**——在每一步生成多个候选思路，评估后选择最有前途的继续展开，可以回溯。

```
                    [问题]
                   /  |  \
              思路A  思路B  思路C     ← 生成多个候选
              / \    |      \
           A1  A2   B1      C1       ← 评估、剪枝、展开
           ✓        ✓
```

ToT 适合需要**规划**和**回溯**的任务（如数学证明、24点游戏），但对简单问答开销过大。

### 4.6 Test-Time Compute 的意义

| 方法 | 计算开销 | 适用场景 | 代表系统 |
|------|---------|---------|---------|
| Direct | 1× | 简单问答 | 标准 LLM |
| CoT | ~3-10× | 多步推理 | GPT + "step by step" |
| Self-Consistency | $N$× | 数学/逻辑 | Wang et al. 2022 |
| Best-of-N | $N$× | 开放生成 | RM + 采样 |
| ToT | 指数级 | 规划/搜索 | Yao et al. 2023 |
| **Long CoT (RL-trained)** | **100-1000×** | **复杂数学/编程** | **o1, R1** |

> **o1/R1 的突破**：不是在推理时加 prompt 技巧，而是用 RL **训练模型学会长时间思考**。模型学会了何时回溯、何时验证、何时换思路——这些"思考策略"被 RL 奖励信号内化到了模型参数中。test-time compute 从一种"技巧"变成了模型的一种"能力"。

---

## 5. 代码层：从零实现 SFT 和 DPO

完整实验见 `experiments/09_dpo_vs_sft.py`。这里展示核心实现。

### 5.1 响应概率计算

无论是 SFT 还是 DPO，核心操作都是计算 $\log p_\theta(y \mid x)$：

```python
def response_logprobs(model, prompts, responses):
    """批量计算 log P(response | prompt)"""
    full = torch.cat([prompts, responses], dim=1)      # (B, prompt_len + resp_len)
    logits = model(full)                                 # (B, T, vocab_size)
    plen = prompts.size(1)
    # logits 位置 plen-1 预测 response[0], plen 预测 response[1], ...
    pred = logits[:, plen-1:plen-1+responses.size(1), :] # (B, resp_len, V)
    logp = F.log_softmax(pred, dim=-1)
    # 取出 response token 对应的 log prob
    return logp.gather(2, responses.unsqueeze(-1)).squeeze(-1).sum(1)  # (B,)
```

### 5.2 SFT 损失

```python
def sft_loss_fn(model, prompts, chosens):
    """SFT = 负对数似然 of chosen responses"""
    logp = response_logprobs(model, prompts, chosens)   # (B,)
    return -logp.mean()                                   # 标量
```

就这么简单——标准的 next-token prediction loss，只在回答 token 上计算。

### 5.3 DPO 损失

```python
def dpo_loss_fn(model, ref_model, prompts, chosens, rejecteds, beta):
    """DPO loss = -log σ(β·[log(π(yw)/πref(yw)) - log(π(yl)/πref(yl))])"""
    logp_w   = response_logprobs(model,     prompts, chosens)    # log π(yw|x)
    logp_l   = response_logprobs(model,     prompts, rejecteds)  # log π(yl|x)
    with torch.no_grad():
        logp_w_ref = response_logprobs(ref_model, prompts, chosens)   # log πref(yw|x)
        logp_l_ref = response_logprobs(ref_model, prompts, rejecteds) # log πref(yl|x)

    logratio_w = logp_w - logp_w_ref     # log[π(yw)/πref(yw)]
    logratio_l = logp_l - logp_l_ref     # log[π(yl)/πref(yl)]

    return -F.logsigmoid(beta * (logratio_w - logratio_l)).mean()
```

注意参考模型 `ref_model` 是冻结的（`no_grad`），只提供基线概率。

### 5.4 实验设计

```
模型: TinyGPT (vocab=14, d_model=64, 2层, 4头, ~50K 参数)
数据: 6 组偏好对
  - 前 4 组: chosen 用 token 7-9, rejected 用 token 10-12 (无共享)
  - 后 2 组: chosen 和 rejected 共享首 token (展示 SFT 盲区)
```

**反直觉发现 1——DPO 训太狠，KL 爆炸**：

```
β=0.05 (约束弱), 训练 500 步, lr=5e-3:
  Step    0: loss=0.6931  KL=0.057   entropy=2.584/2.639  ← 接近均匀(健康)
  Step  100: loss=0.0090  KL=1.431   entropy=1.208/2.639
  Step  499: loss=0.0004  KL=1.893   entropy=0.716/2.639  ← 熵占比 27.1%, 退化!

β=0.5 (约束强), 训练 500 步, lr=5e-3:
  Step    0: loss=0.6931  KL=0.057   entropy=2.584/2.639
  Step  499: loss=0.0000  KL=1.486   entropy=1.166/2.639  ← 熵占比 44.2%, 更稳
```

β 越小（约束弱），熵坍塌越严重（27% vs 44%），KL 增长越快（1.89 vs 1.49），模型越快退化为只能输出少数序列。

**反直觉发现 2——SFT 无对比信号，坏回答概率失控**：

```
SFT 训练中 (chosen 与 rejected 在后2组共享首 token + eos):
  Step 0(前): logP(chosen)=-8.049  logP(rejected)=-7.926  ← 近均匀
  Step    1: logP(chosen)=-6.540  logP(rejected)=-7.446  ← P(rejected) 先升!
                                                       P(rej): 0.036%→0.058% (+62%)
  Step   50: logP(chosen)=-0.046  logP(rejected)=-16.546
  Step  299: logP(chosen)=-0.003  logP(rejected)=-22.391

⚠️ 第一步 P(rejected) 反而上升了 62%
   因为 chosen 和 rejected 共享 token (首 token 7/8 + eos),
   SFT 抬高共享 token 概率时, 坏回答概率被附带抬高
   SFT 没有"这是坏回答"的信号
```

---

## 6. 局限与争议

### 6.1 DPO 的隐患

| 问题 | 说明 |
|------|------|
| **过拟合偏好数据** | DPO 是离线方法（offline），只在已有偏好对上优化。偏好数据有偏（annotator bias、LLM judge bias），DPO 会放大这些偏差 |
| **概率漂移** | 训太狠时，$\log[\pi_\theta/\pi_{\text{ref}}]$ 趋向 $\pm\infty$，模型偏离参考模型太远，丧失通用能力。实验中 KL 从 0 飙到 4+ |
| **缺乏探索** | DPO 无法发现训练数据中不存在的好回答。PPO 通过在线采样可以探索新的回答空间 |
| **分布外泛化差** | DPO 在训练分布内表现好，但面对分布外的 prompt 时，偏好可能不迁移 |

### 6.2 RLHF/PPO 仍有优势

尽管 DPO 在工程上更简单，但 RLHF/PPO 在以下方面仍有不可替代的优势：

1. **探索性**：PPO 在线从 $\pi_\theta$ 采样，可以发现模型从未生成过的高奖励回答。这在创造性任务（如写作、代码生成）中很重要。
2. **奖励信号的及时性**：PPO 的奖励模型可以随策略更新不断评估新回答，形成闭环反馈。DPO 的偏好数据是静态的。
3. **细粒度控制**：PPO 的 KL 惩罚可以在训练过程中动态调整，DPO 的 β 是固定的。

> **2025 年的共识**：DPO 和 RLHF 不是替代关系，而是互补。实践中常见的 pipeline 是 SFT → DPO（快速对齐）→ 可选 RLHF（精细调优）。DeepSeek R1 使用了 GRPO（一种 PPO 变体）来实现推理能力的 RL 训练。

### 6.3 Test-Time Compute 的争议

- **成本问题**：o1/R1 的"思考"需要 100-1000 倍的推理计算。对于高频低价值任务，这个成本是否值得？
- **可解释性**：模型的"思考过程"是否真的反映了推理？还是只是生成了看起来合理的推理链？
- **评估困难**：如何评估 test-time compute 的边际收益？什么时候应该停止思考？

### 6.4 对齐的根本困难

所有后训练方法都面临一个更深层的问题：**我们真的知道什么是"对齐"吗？**

- **偏好数据的主观性**：不同标注者对"好"的定义不同（annotator skew，SLP3 9.1.1 详细讨论）
- **文化偏差**：英文标注者的偏好未必适用于其他语言和文化
- **奖励黑客**：模型可能学会"看起来好"而非"真的好"——例如输出更长、更礼貌但实质内容空洞的回答
- **价值观漂移**：社会价值观在变化，今天的"对齐"明天可能就过时

---

## 7. 现代 LLM 后训练 Pipeline 总览

```
预训练 (Pretraining)
  │  数据: 万亿 token 互联网文本
  │  目标: next-token prediction
  │  产出: Base Model (会续写, 不会听话)
  │
  ▼
SFT (Supervised Fine-Tuning)
  │  数据: 数万~数百万 指令-回答对
  │  目标: next-token prediction (在回答部分)
  │  产出: Instruction-Tuned Model (会遵循指令)
  │  成本: ~1% 预训练成本
  │
  ▼
偏好对齐 (Preference Alignment)
  │  方法: DPO (简单稳定) 或 RLHF/PPO (灵活但复杂)
  │  数据: 数万~数十万 偏好对
  │  目标: 增大 P(好回答)/P(坏回答)
  │  产出: Aligned Model (有用 + 无害)
  │  β: 0.01~0.5
  │
  ▼ (可选)
Test-Time Compute
  │  方法: CoT / Self-Consistency / Best-of-N / Long CoT (RL-trained)
  │  不改变参数, 只改变推理策略
  │  代表: o1, R1
```

---

## 📌 下一步

- **Ch 10** 掩码语言模型与 BERT：SFT 教 GPT 遵循指令，BERT 走了完全不同的路——双向编码器
- **Ch 11** 信息检索与 RAG：后训练让模型变聪明，RAG 让模型"查资料"——两者互补
- 深入版：`../讲透微调/`（LoRA/QLoRA/PEFT 的工程细节）、`../讲透Prompt/`（CoT/prompt engineering 的系统化方法）

**推荐阅读**：
- Rafailov et al. (2023) *Direct Preference Optimization* NeurIPS — DPO 原论文，推导极其优雅
- Ouyang et al. (2022) *Training language models to follow instructions with human feedback* NeurIPS — InstructGPT，RLHF 的里程碑
- Wei et al. (2022) *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* NeurIPS — CoT 原论文

---

## ✍️ 练习

**练习 9.1**（SFT 的 loss mask）：在 SFT 中，prompt 部分的 loss 被屏蔽。如果把 prompt 部分也计入 loss，会发生什么？在实验中修改 `response_logprobs` 函数，让它计算全序列的 loss，观察模型行为的差异。

**练习 9.2**（DPO 的 β）：在实验中，尝试 β = {0.01, 0.05, 0.1, 0.3, 0.5, 1.0}，绘制 KL 散度随训练步数的变化曲线。找到"KL 开始指数增长"的临界 β 值。

**练习 9.3**（Bradley-Terry 推导）：从 $\delta = \log \frac{P(y_w \succ y_l)}{1 - P(y_w \succ y_l)}$ 出发，推导 $P(y_w \succ y_l) = \sigma(\delta)$。（提示：与逻辑回归的 sigmoid 推导完全相同。）

**练习 9.4**（DPO 梯度分析）：对 DPO loss 求关于 $\log \pi_\theta(y_w \mid x)$ 的梯度。证明梯度会同时增大 $\log \pi_\theta(y_w \mid x)$ 和减小 $\log \pi_\theta(y_l \mid x)$。（提示：对 sigmoid 求导。）

**练习 9.5**（SFT vs DTO 的本质区别）：为什么 SFT 无法区分"好回答比坏回答好"，而 DPO 可以？用一句话概括答案。（提示：SFT 的损失函数里根本没有 $y_l$。）

**练习 9.6**（Test-Time Compute 思考题）：Best-of-N 采样需要 $N$ 次前向传播 + $N$ 次奖励模型评估。假设每次前向传播成本为 $C$，奖励评估成本为 $c$，写出总成本表达式。如果质量与 $\log N$ 成正比，$N$ 设为多少最经济？

---

> 配套实验：`experiments/09_dpo_vs_sft.py`
> 姊妹章节：`10-掩码语言模型-BERT.md`（下一个）、`08-Transformer.md`（前置）
