# 第十二章 · Verifier / PRM / Search 训练细节：推理模型的黑盒

> "We can think of test-time compute as another scaling dimension." —— Snell et al., 2024
>
> 「推理模型之所以会思考，不是因为模型变大了，而是因为训练时学会了'怎么搜索'、推理时被允许'多想一会儿'。而 Verifier（验证器）就是那个在搜索过程中给每一步打分的裁判。」

**适用读者**：已经读过 o1 / R1 概览章，想搞清楚「Long-CoT 到底怎么训出来的」「PRM 是什么」「为什么 R1-Zero 不用 SFT 也能涌现反思」的工程师与研究者。

**本章核心论点**（先放结论，后给证据）：
1. 推理模型 = **生成器（policy）** + **验证器（verifier/reward）** + **搜索算法（search）** 三件套，三者必须协同训练。
2. **ORM（只看答案）会奖励'瞎猫碰上死耗子'；PRM（看每一步）才能区分'想对了'和'蒙对了'**——这是 Lightman 2023 的核心洞见。
3. **RLVR（可验证奖励的强化学习）是 o1/R1 的真正引擎**：当 reward 可被客观验证（数学有标准答案、代码能跑通），就绕开了 RLHF 的人力瓶颈。
4. **Test-time compute 是新的 scaling 维度**：同样的参数量，允许模型在推理时多搜索，性能可以超过 14 倍大的模型（Snell 2024）。
5. 但这条路有致命陷阱：**reward hacking、长链错误累积、sycophancy**——本章会诚实讲失败模式。

---

## 勘误声明（重要）

在动笔前，必须先纠正用户大纲中的一处归属错误，这是本章第一条「铁律」的体现：

> ⚠️ **arXiv:2408.03314 的作者是 Snell et al.（UC Berkeley），不是 Burns。**
> 该论文标题为《Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters》，作者 Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar，2024-08-06 提交。
> Burns（OpenAI）的代表作是《Discovering Latent Knowledge Without Supervision》（arXiv:2212.03827），与 test-time compute scaling 无直接关系。
> 本文中所有引用该工作时，作者一律标注为 **Snell et al.**。

此外，调研过程中我还纠正了自己记忆中的两处 arXiv ID 错误（违反了「arXiv ID 别猜」铁律），在此公开记录，提醒读者：**任何 arXiv ID 在引用前必须用 arXiv API 或官网一手核实**：

| 我记错的 ID | 实际是什么 | 正确 ID |
|---|---|---|
| Math-Shepherd = 2312.10908 ❌ | 2312.10908 是《CLOVA》视觉论文 | **2312.08935** |
| GenRM = 2305.07497 ❌ | 2305.07497 是自动驾驶 Planner | **2408.15240** |

---

## 一、Outcome Reward vs Process Reward：两种监督哲学

### 1.1 一个直觉例子

假设一道数学题：「一个班 30 人，男生占 60%，女生平均分 85，全班平均分 82，求男生平均分。」正确答案是 80。

模型 A 的推理链：`全班 30 人，男生 18 人女生 12 人 → 总分 = 30×82 = 2460 → 女生总分 = 12×85 = 1020 → 男生总分 = 2460−1020 = 1440 → 男生平均 = 1440/18 = 80。✅`

模型 B 的推理链：`全班 30 人 → 男生 20 人（错！应该是 18）→ 总分 2460 → 女生总分 1020 → 男生总分 1440 → 男生平均 = 1440/20 = 72（错）→ ... 中间又算错几次 ... → 最后"修正"得到 80。✅`

两个模型最终答案都是 80。**如果只看答案（ORM），它们一样好；如果看每一步（PRM），模型 A 全对，模型 B 几乎全错。** 这就是 ORM 的根本缺陷：它无法区分「想对了」和「蒙对了」，尤其在多步推理中，错误的中途步骤可能因为后续的偶然抵消而得到正确答案。

### 1.2 Outcome Reward Model（ORM）

ORM 只在推理链的**最后一个 token**（或最终答案处）给出一个标量奖励。它的训练数据通常是「(题目, 完整解, 对/错)」三元组。

**训练 loss**（二分类交叉熵）：

$$
\mathcal{L}_{\text{ORM}} = -\mathbb{E}_{(x, y) \sim \mathcal{D}} \big[ \mathbb{1}_{y\ \text{正确}} \log r_\theta(x, y) + \mathbb{1}_{y\ \text{错误}} \log(1 - r_\theta(x, y)) \big]
$$

其中 $r_\theta(x, y)$ 是 reward model 对「题目 $x$、解 $y$」输出的正确性概率。

**优点**：标注便宜——只要核对最终答案即可，可大规模自动化（这就是 RLVR 的基础）。

**致命缺点**：
- **信用分配稀疏**：一条 20 步的推理链，只拿到 1 个 reward 信号，模型无法知道哪一步是关键。
- **奖励蒙对**：如上例，错误过程可能拿到正奖励，强化了坏推理路径。
- **难以定位错误**：在 best-of-N 或 beam search 中，ORM 只能挑「最终答案最好」的那条，无法在中途剪枝。

### 1.3 Process Reward Model（PRM）

PRM 对推理链的**每一个步骤**都给出一个奖励分数。它的训练数据是「(题目, 解, [step₁标签, step₂标签, ..., stepₙ标签])」。

**训练 loss**（每步独立二分类）：

$$
\mathcal{L}_{\text{PRM}} = -\mathbb{E}_{(x, s_{1:n}) \sim \mathcal{D}} \sum_{i=1}^{n} \big[ \mathbb{1}_{s_i\ \text{正确}} \log r_\theta(x, s_{1:i}) + \mathbb{1}_{s_i\ \text{错误}} \log(1 - r_\theta(x, s_{1:i})) \big]
$$

注意 PRM 评分时看的是**前缀** $s_{1:i}$（到当前步为止的全部历史），而不是孤立的一步——因为一步是否正确依赖于上下文。

> **论文：Lightman et al., "Let's Verify Step by Step"** [arXiv:2305.20050](https://arxiv.org/abs/2305.20050)（OpenAI，2023-05-31）
> 这是 PRM 的奠基论文。核心贡献：① 在 MATH 数据集上证明 **process supervision 显著优于 outcome supervision**；② 发布 **PRM800K** 数据集（80 万步级人类反馈标注）；③ PRM 在 best-of-N 评测中全面碾压 ORM。其 process-supervised 模型在 MATH 测试子集上达到 **78%** 正确率。

### 1.4 ORM vs PRM 的实验对比（Lightman 2023 关键结果）

OpenAI 在论文中做了一组精心设计的对照实验，结论极其清晰：

- **训练数据规模**：ORM 用约 900 万标注（题-解-对错），PRM 用 PRM800K 的约 80 万**步级**标注。注意 PRM 的标注单位更细，但总 token 量更少。
- **best-of-N 评测**：在 MATH 的 45% 子集上，PRM-guided 的 best-of-N 在每个 N 值都显著高于 ORM-guided。当 N=186 时，PRM 达到 78.2%，ORM 只有 72.4%。
- **活跃学习（active learning）**：用 PRM 主动挑选「最不确定」的样本去标注，效率提升 2.6 倍。

> **核心洞见**：在数学这类「过程即答案」的任务上，**过程监督不仅更准确，而且样本效率更高**。这是推理模型领域被引用最多的结论之一。

### 1.5 一个微妙但关键的争议：PRM 真的总是更好吗？

需要诚实地指出：Lightman 的结论并非普适。后续工作（如 DeepSeek 团队的实践）发现：

- 在 **RL 阶段**，PRM 训练难度大、容易 reward hacking，DeepSeek-R1 反而选择了**纯 ORM（基于规则的可验证 reward）+ GRPO** 的路线，效果惊艳。
- PRM 的优势主要体现在**推理时（test-time）的 reranking/搜索**，而不是 RL 训练阶段。
- PRM 标注成本极高（PRM800K 花了 OpenAI 巨量人力），这是它没能成为主流 RL reward 的现实原因。

这个张力——「PRM 更准确但更贵更难训」——是贯穿整个推理模型领域的核心矛盾，本章会反复回到这一点。

---

## 二、PRM 训练细节：从 PRM800K 到 Math-Shepherd

### 2.1 PRM800K 数据集是怎么造出来的

PRM800K 是 OpenAI 为训练 PRM 而构造的**步级标注数据集**，规模约 80 万个 step-level 标签。它的构造流程是工业级 PRM 训练的范本：

**Step 1：题目采样**。从 MATH 训练集（12,500 道竞赛数学题）中采样题目。

**Step 2：解的生成**。用大模型（GPT 系）对每道题生成**多条**不同的解（solution），每条解被切成步骤（step）。切分方式：以换行或数学表达式为边界，由人类标注员判断「这是一步」。

**Step 3：步级标注**。人类标注员对**每一个步骤**打三类标签：
- `good`（正确且推进了推理）
- `bad`（有错误或无意义的步骤）
- `potentially_good`（不确定，中间状态）

**Step 4：活跃学习循环**。用当前 PRM 对未标注的解打分，挑出「PRM 最不确定」（分数接近 0.5）的样本优先标注——这就是 active learning，让有限的标注预算花在刀刃上。

最终数据集统计（论文 Table 1）：约 800,000 个 step-level 标签，覆盖约 75,000 道题、数百上千条解。这是当时规模最大的数学过程监督数据集。

### 2.2 PRM 的训练 loss 详解

PRM 在工程上通常这样实现（基于一个预训练 LM）：

```python
# 伪代码：PRM 训练前向传播
# 输入：题目 x，步骤序列 s_1, s_2, ..., s_n，每步标签 y_1, ..., y_n ∈ {0, 1}

def prm_forward(model, tokenizer, question, steps, labels):
    """
    PRM 前向：在每个步骤结束的位置预测一个正确性概率。
    工程实现：在 step 边界插入特殊 token <step_end>，取该 token 的 hidden state 过一个线性头。
    """
    # 构造输入：question + step_1 <step_end> step_2 <step_end> ... step_n <step_end>
    text = question
    step_end_positions = []
    for step in steps:
        text += step + " <step_end>"
        step_end_positions.append(len(tokenizer.encode(text)) - 1)  # <step_end> 的位置
    
    input_ids = tokenizer.encode(text, return_tensors="pt")
    hidden_states = model(input_ids).last_hidden_state  # [1, seq_len, hidden_dim]
    
    # 取每个 <step_end> 位置的 hidden state
    step_hiddens = hidden_states[0, step_end_positions, :]  # [n_steps, hidden_dim]
    
    # 过一个线性分类头（PRM head）
    logits = prm_head(step_hiddens)  # [n_steps, 2]  二分类：good vs bad
    probs = softmax(logits, dim=-1)[:, 1]  # 取 'good' 的概率
    
    # 每步二分类交叉熵 loss
    loss = cross_entropy(logits, labels)  # labels: [n_steps]
    return loss, probs
```

**关键工程细节**：
1. **步骤边界标记**：必须用特殊 token（如 `<step_end>` 或 `\n\n`）明确告诉模型「在这里打分」，否则无法定位。
2. **PRM head**：通常是一个简单的线性层（hidden_dim → 2），加在预训练 LM 之上，只训练这个 head + 微调顶层几层。OpenAI 的实践是 fine-tune 整个模型。
3. **前缀依赖**：评分第 $i$ 步时，PRM 看到的是 $s_{1:i}$（前缀），不是孤立的 $s_i$——这是通过 Transformer 的自注意力自然实现的。
4. **标签平滑**：对 `potentially_good` 这种不确定标签，OpenAI 在最终训练时把它当作 `bad` 处理（保守策略，宁错杀不放过），但有些后续工作把它当作软标签。

### 2.3 PRM 在推理时的三种用法

训练好 PRM 后，它在推理时（test-time）有三种典型用法，这是「搜索 + LLM」的核心组件：

**用法 1：Best-of-N（BoN）reranking**
```python
def best_of_n(generator, prm, question, n=8):
    """生成 N 条解，用 PRM 给每条打分，选 PRM 分数最高的。"""
    candidates = [generator(question) for _ in range(n)]  # 生成 N 条不同的解
    
    scored = []
    for sol in candidates:
        steps = split_into_steps(sol)
        step_scores = [prm.score(question, steps[:i+1]) for i in range(len(steps))]
        # 整条解的分数 = 各步分数的乘积（假设步骤独立）或最小值（关注最弱环节）
        sol_score = min(step_scores)  # 最小值更稳健：一条链的最坏步骤决定上限
        scored.append((sol, sol_score))
    
    return max(scored, key=lambda x: x[1])[0]
```

**用法 2：Step-level beam search**（PRM-guided beam search）
```python
def prm_beam_search(generator, prm, question, beam_width=4, max_steps=10):
    """每一步生成多个候选，用 PRM 打分，保留 top-beam_width。"""
    beams = [([], 1.0)]  # (steps_so_far, cumulative_score)
    
    for step_idx in range(max_steps):
        all_candidates = []
        for steps, score in beams:
            # 为每个 beam 生成 k 个候选下一步
            for _ in range(beam_width):
                new_step = generator.generate_next_step(question, steps)
                new_steps = steps + [new_step]
                step_score = prm.score(question, new_steps)  # PRM 评这一步（看前缀）
                new_score = score * step_score  # 累积分数（概率连乘）
                all_candidates.append((new_steps, new_score))
        
        # 保留 top-beam_width
        beams = sorted(all_candidates, key=lambda x: -x[1])[:beam_width]
        
        # 如果某个 beam 已经输出最终答案且分数高，可以提前终止
        if any(is_complete(b[0]) and b[1] > 0.9 for b in beams):
            break
    
    return beams[0][0]
```

**用法 3：MCTS 的 value function**（详见第三章）。在 AlphaZero 范式中，PRM 扮演的就是 value network 的角色，评估每个状态（部分推理链）的价值。

### 2.4 Math-Shepherd：中国版的自动化 PRM

PRM800K 的致命问题是**人力成本**——80 万步标注是 OpenAI 用庞大标注团队堆出来的。中国团队（DeepSeek + 北大）提出的 **Math-Shepherd** 解决了这个问题：**用蒙特卡洛采样自动生成步级标签**。

> **论文：Wang, Li, Shao et al., "Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations"** [arXiv:2312.08935](https://arxiv.org/abs/2312.08935)（DeepSeek-AI / 北京大学，2023-12-14，v3 2024-02-19）
> 核心创新：**自动构造过程监督数据**，打破对人工标注的依赖。在验证（reranking）和强化学习（step-by-step PPO）两个场景都有效。

**Math-Shepherd 的自动标注思想**（这是整个自动化 PRM 路线的核心 trick）：

对于一条解的第 $i$ 步 $s_i$，要给它打标签。Math-Shepherd 的做法是：**固定前缀 $s_{1:i}$，然后用生成器从 $s_{1:i}$ 出发蒙特卡洛采样 $K$ 条完整解，看这 $K$ 条里有多少条最终答对**。

$$
\hat{y}_i = \frac{1}{K} \sum_{k=1}^{K} \mathbb{1}\big[\text{complete}(s_{1:i} \oplus \text{sample}_k) = \text{正确答案}\big]
$$

- 如果从 $s_{1:i}$ 出发，大部分采样都能得到正确答案 → 说明 $s_{1:i}$ 是「好前缀」→ $\hat{y}_i \approx 1$
- 如果从 $s_{1:i}$ 出发，几乎都得不到正确答案 → 说明 $s_{1:i}$ 已经走偏了 → $\hat{y}_i \approx 0$

这把「步级标签」转化为「从该步出发的正确率」，**完全不需要人工**，只需要能验证最终答案（数学题有标准答案）。

**Math-Shepherd 的实验结果**（论文摘要数据）：
- Mistral-7B + step-by-step PPO + Math-Shepherd reward：GSM8K 77.9% → 84.1%，MATH 28.6% → 33.0%
- 再用 Math-Shepherd 做 verification（reranking）：GSM8K 89.1%，MATH 43.5%

这个思路后被广泛复用，成为开源社区训练 PRM 的事实标准（Qwen-Math、DeepSeek 系列都用了类似自动化标注）。

### 2.5 代码示例：训练一个玩具 PRM

下面给出一个**可运行的最小 PRM 训练脚本**（基于 HuggingFace transformers，数据用合成示例）。真实场景只需把数据替换成 Math-Shepherd 风格的自动标注。

```python
"""
最小可运行 PRM 训练 demo（教学用，非生产级）。
演示：如何把一个预训练 LM 改造成「对每个步骤打分」的 PRM。
依赖：pip install transformers torch
"""
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class TinyPRM(nn.Module):
    """在预训练 LM 之上加一个 PRM head（线性层），对 <step_end> 位置打分。"""
    def __init__(self, lm_name="bert-base-uncased"):
        super().__init__()
        self.lm = AutoModel.from_pretrained(lm_name)
        self.tokenizer = AutoTokenizer.from_pretrained(lm_name)
        
        # 添加特殊 token <step_end>（步骤边界）
        self.tokenizer.add_special_tokens({"additional_special_tokens": ["<step_end>"]})
        self.lm.resize_token_embeddings(len(self.tokenizer))
        
        # PRM head：hidden_dim -> 1（输出该步骤的正确性 logit）
        self.prm_head = nn.Linear(self.lm.config.hidden_size, 1)
    
    def forward(self, question, steps, step_labels=None):
        """
        question: str
        steps: List[str]，每个元素是一步推理
        step_labels: List[int]（0 或 1），可选，用于训练
        返回：每步的 logit（推理）或 loss（训练）
        """
        # 构造输入文本
        text = question
        for step in steps:
            text += " " + step + " <step_end>"
        
        enc = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = enc["input_ids"]
        
        # 找到所有 <step_end> 的位置
        step_end_id = self.tokenizer.convert_tokens_to_ids("<step_end>")
        step_end_positions = (input_ids[0] == step_end_id).nonzero(as_tuple=True)[0]
        
        # LM 前向
        hidden = self.lm(**enc).last_hidden_state  # [1, seq_len, hidden]
        step_hiddens = hidden[0, step_end_positions, :]  # [n_steps, hidden]
        
        logits = self.prm_head(step_hiddens).squeeze(-1)  # [n_steps]
        
        if step_labels is not None:
            labels = torch.tensor(step_labels, dtype=torch.float32)
            loss = nn.functional.binary_cross_entropy_with_logits(logits, labels)
            return loss, torch.sigmoid(logits)
        return torch.sigmoid(logits)

# ====== 合成训练数据（真实场景换成 Math-Shepherd 自动标注）======
train_data = [
    {
        "question": "Q: 2+3=?",
        "steps": ["2+3=5", "So the answer is 5."],
        "labels": [1, 1]  # 两步都对
    },
    {
        "question": "Q: 2+3=?",
        "steps": ["2+3=6", "So the answer is 6."],
        "labels": [0, 0]  # 第一步就错，后面跟着错
    },
    {
        "question": "Q: 2+3=?",
        "steps": ["2+3=5", "So the answer is 6."],  # 中间对，最后抄错
        "labels": [1, 0]
    },
]

# ====== 训练循环 ======
prm = TinyPRM()
optimizer = torch.optim.AdamW(prm.parameters(), lr=1e-5)

for epoch in range(50):
    total_loss = 0
    for ex in train_data:
        optimizer.zero_grad()
        loss, _ = prm(ex["question"], ex["steps"], ex["labels"])
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    if epoch % 10 == 0:
        print(f"epoch {epoch}, loss {total_loss:.4f}")

# ====== 推理：给一条新解打分 ======
with torch.no_grad():
    scores = prm("Q: 4+5=?", ["4+5=9", "So the answer is 9."])
    print("每步正确性概率:", scores.tolist())  # 训练好后应该接近 [0.9+, 0.9+]
```

**这个 demo 的局限**（诚实声明）：① 数据是合成的，真实场景需要数万条带步级标签的样本；② 用 BERT 是为了教学简洁，真实 PRM 通常基于强力数学 LM（如 Mistral-7B、DeepSeekMath）；③ 没有实现 Math-Shepherd 的自动标注，那是另一个完整 pipeline。

---

## 三、Search Algorithm + LLM：让模型学会「多想一会儿」

如果说 PRM 是「裁判」，那么搜索算法就是「棋手」——它决定模型在推理时如何探索、剪枝、回溯。这是推理模型与普通 LLM 最本质的区别：**普通 LLM 是左到右贪心解码，推理模型是搜索树上的规划。**

### 3.1 Best-of-N（BoN）：最简单的搜索

BoN 是最朴素的「搜索」：用高温采样生成 N 条不同的解，用 PRM（或 ORM）给每条打分，选最好的。

```python
def best_of_n(generator, scorer, question, n=16, temperature=0.8):
    candidates = []
    for _ in range(n):
        sol = generator(question, temperature=temperature, do_sample=True)
        candidates.append(sol)
    scores = [scorer(question, c) for c in candidates]
    return candidates[scores.index(max(scores))]
```

**BoN 的 scaling law**（Snell 2024 的关键发现之一）：BoN 在 N 较小时近似线性提升，但**收益递减**——N 从 4 到 8 提升明显，从 64 到 128 提升就很小了。Snell 指出，在难度适中的题上，「compute-optimal」策略（自适应分配 N）比固定 BoN 效率高 4 倍以上。

### 3.2 Beam Search：受控的广度优先

Beam search 是 NLP 老兵算法，用在推理模型上需要两个改造：
1. **beam 单位是「步骤」而非「token」**（token 级 beam 太细，step 级才对应推理粒度）。
2. **打分用 PRM 而非语言模型概率**。

详见第二章 2.3 的代码。beam search 的核心权衡是 **beam_width**：太窄会错过正确路径（剪枝过激），太宽则计算成本爆炸。

### 3.3 Tree of Thoughts（ToT）：把搜索显式化

> **论文：Yao et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"** [arXiv:2305.10601](https://arxiv.org/abs/2305.10601)（Princeton，NeurIPS 2023）
> 核心：把「思维」显式建模为搜索树，每个节点是一个 thought（中间推理状态），用 LLM 自己（①生成候选 thought ②自我评估 thought 价值）驱动 BFS/DFS 搜索。在 24 点游戏上，GPT-4 + CoT 只解出 4%，ToT 解出 74%。

ToT 的精髓在于**用 LLM 自己当 PRM**（self-evaluation），不需要外训 PRM。它定义了三个 LLM 调用：
- `GenerateThoughts(state, k)`：从当前状态生成 k 个候选下一步 thought。
- `EvaluateThought(state)`：让 LLM 给这个 thought 打分（"definitely good / likely bad / ..." → 数值）。
- `SearchAlgorithm(BFS/DFS)`：用上面的评估值驱动搜索。

**ToT 与 PRM 的关系**：ToT 用「in-context LLM 自评」代替了「外训 PRM」，灵活但精度低。后续工作（如 Math-Shepherd + beam search）本质上是 ToT 的「外训 PRM 加强版」。

### 3.4 Self-Consistency：最简单却最有效的「搜索」

> **论文：Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models"** [arXiv:2203.11171](https://arxiv.org/abs/2203.11171)（Google，ICLR 2023）
> 核心 insight：复杂推理题往往有多种正确解法，它们都会导向同一个答案。所以**采样多条 CoT，对最终答案做多数投票**，比选最好的那条更稳健。
> 结果：GSM8K +17.9 个绝对百分点，SVAMP +11.0，AQuA +12.2。

```python
def self_consistency(generator, question, n=40, temperature=0.7):
    """采样 n 条 CoT，抽取最终答案，多数投票。"""
    answers = []
    for _ in range(n):
        sol = generator(question, temperature=temperature, do_sample=True)
        ans = extract_final_answer(sol)  # 用正则抽 \\boxed{} 之类
        answers.append(ans)
    return most_common(answers)
```

**为什么 self-consistency 这么有效？** 它隐含了一个贝叶斯直觉：正确答案 $a^*$ 的后验概率 $P(a^*|x) = \sum_{\text{path}} P(a^*, \text{path}|x)$，即对推理路径做边际化。多数投票就是在近似这个边际化——只要正确路径比错误路径更多样、更密集，投票就能稳赢。

**Self-consistency 与 PRM 的关系**：self-consistency 是「答案级」的集成，PRM-guided BoN 是「过程级」的集成。理想做法是**两者结合**——用 PRM 筛掉明显坏的解，再在剩下的解里做答案投票。

### 3.5 MCTS（Monte Carlo Tree Search）：AlphaGo 的遗产

MCTS 是 AlphaGo/AlphaZero 的核心算法，把搜索树上的「探索 vs 利用」做到了理论最优。用在 LLM 推理上，每个节点是一个「推理状态」（部分解），四步循环：

1. **Selection（选择）**：用 UCB 公式从根走到一个叶节点：
$$
\text{UCB}(s) = Q(s) + c \cdot \frac{\ln N_{\text{parent}}}{N_s}
$$
其中 $Q(s)$ 是状态 $s$ 的平均价值（由 value function 估计），$N_s$ 是访问次数，$c$ 是探索常数。

2. **Expansion（扩展）**：在叶节点用 LLM 生成 $k$ 个候选下一步，作为子节点。

3. **Simulation（模拟/rollout）**：从新节点快速 rollout 到终局（用 LLM 快速补全到答案），得到一个 reward。

4. **Backpropagation（回传）**：把 reward 沿路径回传，更新各节点的 $Q$ 和 $N$。

```python
class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # 部分推理链 [step_1, ..., step_i]
        self.parent = parent
        self.children = []
        self.Q = 0.0   # 平均价值
        self.N = 0     # 访问次数
        self.reward = None  # 若是终局节点，存最终答案的对错

def mcts_search(root_state, generator, value_fn, reward_fn, n_iter=1000, c=1.4):
    root = MCTSNode(root_state)
    for _ in range(n_iter):
        # 1. Selection
        node = root
        while node.children and not is_terminal(node.state):
            node = max(node.children, key=lambda ch: ucb(ch, c))
        
        # 2. Expansion
        if not is_terminal(node.state):
            candidates = generator.generate_next_steps(node.state, k=4)
            for cand in candidates:
                child = MCTSNode(node.state + [cand], parent=node)
                node.children.append(child)
            node = node.children[0]  # 简化：取第一个
        
        # 3. Simulation (rollout)
        if is_terminal(node.state):
            reward = reward_fn(node.state)  # 答案对错
        else:
            rollout_completion = generator.complete(node.state)
            reward = reward_fn(node.state + rollout_completion)
        
        # 4. Backpropagation
        while node is not None:
            node.N += 1
            node.Q = (node.Q * (node.N - 1) + reward) / node.N
            node = node.parent
    
    # 返回根节点下访问次数最多的子节点（最稳健的选择）
    return max(root.children, key=lambda ch: ch.N).state
```

### 3.6 AlphaZero 模式与 AlphaProof：形式化数学的胜出

MCTS + LLM 的最高成就，是 DeepMind 的 **AlphaProof**。

> **来源：DeepMind 博客《AI achieves silver-medal standard solving IMO problems》**（2024-07-25）；**Nature 论文**（2025-11-12，DOI [10.1038/s41586-025-09833-y](https://www.nature.com/articles/s41586-025-09833-y)）
> AlphaProof 在 IMO 2024 解出 6 题中的 4 题，得 28/42 分，达到银牌水平（金牌线 29 分）。其中包含当年仅 5 名人类选手解出的最难题。

**AlphaProof 的架构**（AlphaZero 范式在形式化数学上的实例化）：

1. **形式化语言 Lean**：所有问题被翻译成 Lean（一种交互式定理证明器）的形式语言。Lean 的好处是**证明可以被机器验证**——不存在「蒙对」，要么证明通过，要么不通过。这是 AlphaProof 的 reward 不可能 reward hack 的根本原因。

2. **网络三件套**（类比 AlphaZero）：
   - **Policy network**：一个预训练 LM（基于 Gemini），给定当前证明状态，生成候选的下一步证明 tactic。
   - **Value network**：评估当前证明状态的「赢面」（能否最终完成证明）。
   - **Search（MCTS）**：用 policy 缩小搜索空间，用 value 引导选择。

3. **训练循环（self-play + RL）**：
   - 用 informal-to-formal translator（另一个 Gemini 微调模型）把百万道自然语言数学题翻译成 Lean。
   - AlphaProof 尝试证明每道题，**成功的证明作为正样本强化 policy/value 网络**（这就是 AlphaZero 式 self-play）。
   - 训练持续数周，覆盖从简单到困难的题目。

**AlphaProof 的关键启示**：
- **形式化是终极的「可验证 reward」**——Lean 编译器就是一个不会出错、不会偏置、不会被 hack 的完美裁判。这把 RLVR 推到了极致。
- **代价是搜索空间巨大**：IMO 级证明的搜索树深达数百步，AlphaProof 解一道题可能要 3 天。这解释了为什么 AlphaProof 暂时无法用在实时对话。
- **informal-formal bridge**：纯形式化数据太少（人类写的 Lean 证明稀缺），DeepMind 的杀手锏是用 LM 把自然语言题自动翻译成 Lean，把数据规模放大了几个量级。

这是「搜索 + LLM」的巅峰之作，也是本章核心论点的最强证据：**当 reward 完美可验证（形式化证明），搜索算法（MCTS）+ RL 能把 LLM 推到人类 IMO 银牌水平**。

---

## 四、RLVR：可验证奖励的强化学习

### 4.1 RLVR 的核心思想

**RLVR（Reinforcement Learning with Verifiable Rewards）** 是 o1/R1 时代的训练范式。它的核心命题极其简单：

> **当任务的正确性可以被客观、廉价地验证时（数学题有标准答案、代码能通过单元测试、Lean 证明能编译），就用「规则验证器」作为 RL 的 reward，而不是训一个神经网络 reward model。**

为什么这个想法如此重要？因为它**绕开了 RLHF 的两个根本瓶颈**：

1. **人力瓶颈**：RLHF 需要海量人类标注偏好对（「A 比 B 好」），贵且慢。RLVR 的 reward 由程序自动判定，边际成本为零。
2. **人类天花板**：RLHF 训出的 reward model 上限是「人类标注员的一致性」，而 RLVR 的 reward 上限是「客观真理」——数学题的对错不依赖人类判断。

**RLVR 的 reward 函数（数学场景，典型实现）**：
```python
def math_reward(question, model_output, ground_truth):
    """从模型输出抽取最终答案，与 ground_truth 精确匹配。"""
    pred = extract_boxed_answer(model_output)  # 抽 \boxed{...} 里的内容
    pred_normalized = normalize_math_expr(pred)  # 标准化：\frac{1}{2} == 0.5 == 1/2
    gt_normalized = normalize_math_expr(ground_truth)
    return 1.0 if pred_normalized == gt_normalized else 0.0  # 二值 reward
```

这个函数简单到几乎是「if-else」，但它就是 DeepSeek-R1 训练时用的核心 reward。**简洁性是它的力量**——没有可被 hack 的中间环节。

### 4.2 OpenAI o1 / o3 / o4 训练（推断）

OpenAI 没有公开 o1 的完整训练细节（这是业界最关心的黑盒），但从 system card、博客、论文引用可以**推断**其训练范式：

**推断的训练 pipeline**（基于公开信息综合，非 OpenAI 官方确认）：
1. **预训练**：标准的大规模 next-token prediction。
2. **Long-CoT SFT（冷启动）**：用人类或强模型构造一批高质量的 Long-CoT 数据（几千到几万条），让模型学会「输出长推理链」的格式。
3. **RLVR（核心）**：在数学、代码、科学等可验证任务上做大规模 RL，reward 是规则验证器。这里很可能用了某种 PRM 或 self-consistency 来辅助 credit assignment。
4. **Test-time search**：推理时用某种搜索（很可能是 PRM-guided beam search 或 MCTS 的变体），这就是「thinking」阶段。

**关键不确定点**（诚实声明）：① o1 用没用 PRM？多大程度上用？OpenAI 从未确认。② test-time search 的具体算法是什么？只知道「允许模型多生成 token」。③ 是否有 self-play？这些都属于未公开细节。

**o3 / o4 的演进**：o3（2024-12）在 ARC-AGI 上取得突破，o4 进一步强化了工具使用。从公开 benchmark 看，test-time compute 的 scaling 在持续——同一个模型，给更多 thinking token，性能继续提升。

### 4.3 DeepSeek R1：开源的 RLVR 范式

> **论文：DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"** [arXiv:2501.12948](https://arxiv.org/abs/2501.12948)（2025-01-22，v2 2026-01-04）；**Nature 645:633-638 (2025)**，DOI [10.1038/s41586-025-09422-z](https://doi.org/10.1038/s41586-025-09422-z)
> 这是 RLVR 路线最重要的开源工作。R1 的开源（模型权重 + 论文）让全世界都能复现「纯 RL 涌现推理能力」的现象。

DeepSeek R1 论文给了两条路线的对比，这是理解 RLVR 的最佳教材：

#### R1-Zero：纯 RL，不用 SFT

**R1-Zero 的训练**：直接在 DeepSeek-V3-Base（预训练模型，未做 SFT）上跑 GRPO，reward 是数学/代码的规则验证器。

**惊人发现**：R1-Zero **自发涌现**了高级推理行为：
- **Self-reflection**（自我反思）：模型会输出「Wait, let me reconsider...」「Actually, I made an error...」
- **Verification**（自我验证）：模型会自己检查中间结果。
- **Dynamic strategy adaptation**：模型会切换解题策略。

这些行为**没有任何人类示范**，完全从 RL 中涌现。这是 R1 论文最震撼的发现——**只要 reward 信号对（可验证），RL 足以让模型学会「怎么思考」**。

**R1-Zero 的缺陷**（诚实声明）：
- **可读性差**：输出语言混乱（中英文混杂）、格式不规整。
- **非推理任务退化**：在开放对话、写作上表现差（因为只训了数学/代码 reward）。
- 这就是为什么需要完整的 R1。

#### R1：SFT + Cold-start + RL 的完整 pipeline

R1 在 R1-Zero 基础上加了几个关键步骤，解决了可读性和通用性问题：

**Stage 1：Cold-start SFT**。用少量（几千条）高质量 Long-CoT 数据做 SFT，给模型一个「规整的推理格式」起点。这些数据由 R1-Zero 的输出 + 人工筛选/改写而来。

**Stage 2：推理 RL（RLVR）**。在 cold-start 模型上做 GRPO，reward 是数学/代码的规则验证器（同 R1-Zero）。

**Stage 3：拒绝采样 + 全场景 SFT**。从 Stage 2 的模型采样大量推理轨迹，筛好的，**再混入通用对话/写作数据**做一轮全场景 SFT。这步把推理能力「固化」同时恢复通用能力。

**Stage 4：全场景 RL**。最后再做一轮 RL，同时优化推理（规则 reward）和通用对齐（RLHF reward model）。

**R1 的性能**（论文报告）：在 MATH、AIME、Codeforces、MMLU 等推理 benchmark 上对标 OpenAI o1（早期版本）。这是开源模型首次在推理上达到闭源前沿水平。

### 4.4 GRPO：DeepSeek 的 RL 算法

> **论文：Shao et al., "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"** [arXiv:2402.03300](https://arxiv.org/abs/2402.03300)（DeepSeek-AI，2024-02-05）
> GRPO（Group Relative Policy Optimization）是 PPO 的简化变体，**去掉了 critic network**，用 group baseline 代替。这是 R1 训练用的 RL 算法。

**GRPO 的核心简化**（对比 PPO）：

标准 PPO 需要两个网络：policy（生成）和 critic/value（估计状态价值）。critic 通常和 policy 一样大，训练成本翻倍，且 critic 训不好会拖累 policy。

GRPO 的 trick：**对每个问题 $x$，采样一组 $G$ 个回答 $\{o_1, ..., o_G\}$，用这组的平均 reward 作为 baseline**。

$$
A_i = \frac{r_i - \text{mean}(r_{1:G})}{\text{std}(r_{1:G})} \quad \text{(group-normalized advantage)}
$$

这样不需要 critic network——baseline 直接从同组的 reward 统计得到。

**GRPO 的 loss**（PPO 形式 + KL 正则）：

$$
\mathcal{L}_{\text{GRPO}} = -\mathbb{E}\left[ \min\left(\rho_i A_i,\ \text{clip}(\rho_i, 1-\epsilon, 1+\epsilon) A_i\right) \right] - \beta \cdot \text{KL}(\pi_\theta \| \pi_{\text{ref}})
$$

其中 $\rho_i = \frac{\pi_\theta(o_i|x)}{\pi_{\theta_{\text{old}}}(o_i|x)}$ 是重要性采样比，KL 项防止 policy 偏离参考模型太远（避免崩溃）。

**GRPO 的工程优势**：
1. **省一半显存**（无 critic）。
2. **训练更稳定**（group baseline 天然去噪）。
3. **适合可验证 reward**（因为 reward 是二值的 0/1，group 内方差提供了有效的 advantage 信号）。

**GRPO 的局限**：
- 对「全错」或「全对」的 group 没有梯度（$A_i = 0$，因为 std=0）。这要求 group size 够大、采样温度合适，保证 group 内有对有错。
- 在开放任务（无客观 reward）上不如 PPO+reward model 灵活。

```python
# GRPO 训练 step 伪代码
def grpo_step(policy, ref_policy, question, reward_fn, group_size=8, beta=0.01):
    # 1. 采样 group
    outputs = [policy.generate(question) for _ in range(group_size)]
    
    # 2. 计算 reward
    rewards = [reward_fn(question, o) for o in outputs]  # 每个 0/1 或连续值
    
    # 3. Group-normalized advantage
    r_mean, r_std = mean(rewards), std(rewards)
    advantages = [(r - r_mean) / (r_std + 1e-8) for r in rewards]
    
    # 4. PPO clipped objective + KL
    loss = 0
    for o, A in zip(outputs, advantages):
        log_ratio = policy.log_prob(o) - policy.old_log_prob(o)
        ratio = exp(log_ratio)
        clipped = clip(ratio, 1-0.2, 1+0.2) * A
        loss -= min(ratio * A, clipped)
        # KL 正则
        kl = policy.log_prob(o) - ref_policy.log_prob(o)
        loss += beta * kl
    loss /= group_size
    
    loss.backward()
    optimizer.step()
```

---

## 五、Verifier 训练：从判别式到生成式

第四章讲的 RLVR 用的是**规则验证器**（程序判定对错）。但很多任务没有客观答案（写作、对话、代码风格），这时需要一个**学习出来的 verifier**。本章梳理 verifier 的设计谱系。

### 5.1 判别式 verifier（Discriminative Verifier）

判别式 verifier 就是传统的 PRM/ORM：一个 LM + 分类头，输出一个标量分数。

**优点**：训练直接（监督学习），推理快（一次前向）。
**缺点**：① 不会解释「为什么这个步骤错」；② 不能利用 CoT 推理来改进判断；③ 与生成模型的能力割裂（verifier 和 generator 是两个模型）。

### 5.2 生成式 verifier（Generative Verifier / GenRM）

> **论文：Zhang et al., "Generative Verifiers: Reward Modeling as Next-Token Prediction"** [arXiv:2408.15240](https://arxiv.org/abs/2408.15240)（Google DeepMind，ICLR 2025）
> 核心：把 verification 任务转化为 next-token prediction——让 LM 输出「Is this correct? Yes/No」的 token，verification 分数就是"Yes" token 的概率。这样 verifier 能利用 LM 的全部能力（CoT 推理、指令遵循）。

**GenRM 的核心 insight**：与其训一个独立的分类头，不如**直接让 LM 生成判断**：

```
输入：Question: ... Solution: step1... step2... step3...
让 LM 续写：Is step3 correct? Let me check... [CoT 推理] ... Therefore, Yes.
取 "Yes" token 的概率作为 step3 的正确性分数。
```

**GenRM 的三大优势**（论文实证）：
1. **CoT verification**：LM 可以先推理再判断，精度更高。
2. **可与 instruction tuning 无缝整合**：verification 只是另一个指令任务。
3. **Test-time compute scaling**：对同一题采样多次 verification 再投票，精度持续提升（类似 self-consistency）。

**实验结果**（论文）：在 Best-of-N 设置下，GenRM 把算法任务从 5% 提到 45.3%，GSM8K 从 73% 提到 93.4%。在 easy-to-hard 泛化上，MATH 从 28% 提到 44.6%。

### 5.3 LLM-as-Judge 的偏置

用大模型（GPT-4、Claude）当 judge 来给其他模型的输出打分，是当前最流行的「免训练 verifier」。但它有系统偏置：

1. **Position bias**：倾向于选第一个或最后一个选项。
2. **Length bias**：倾向于选更长的回答（即使更长的不更好）。
3. **Self-preference**：模型倾向于偏好自己风格/自己生成的输出（GPT-4 judge 偏好 GPT-4 输出）。
4. **Sycophancy**：倾向于附和 prompt 里的暗示（如果 prompt 暗示「A 更好」，judge 更可能选 A）。
5. **Capability ceiling**：judge 无法识别自己也不懂的错误——如果 judge 自己不会做这道数学题，它也判断不出模型解得对不对。

**缓解方法**：① 位置/选项随机化；② 多 judge 投票；③ 用比 generator 更强的 judge；④ 对 judge 做偏置校正训练。

### 5.4 Self-consistency verifier

一个简单的 trick：让同一个 LM 用不同 prompt/seed 判断多次，对判断结果投票。这本质上是 self-consistency 应用在 verification 上，能显著降低 judge 的方差。

### 5.5 CriticGPT：OpenAI 的 critique 模型

> **论文：McAleese, Trębacz et al., "CriticGPT"** [arXiv:2407.00215](https://arxiv.org/abs/2407.00215)（OpenAI，2024-06-27 博客发布，2024-07-01 arXiv）
> CriticGPT 的目标不是「打分」，而是「写自然语言 critique」——指出 ChatGPT 代码输出的具体错误。

**CriticGPT 的训练 trick（关键创新）**：
1. **人工插入错误**：让人类标注员在 ChatGPT 写的正确代码里**故意插入 bug**。
2. **写 critique**：让标注员写「假装发现了这个 bug」的 critique。
3. **比对训练**：用「(带 bug 的代码, critique 指出 bug)」做 RLHF，让模型学会找 bug。

这样造数据的好处：bug 的位置和性质完全已知（标注员自己插的），critique 的正确性可客观判定。

**CriticGPT 的关键发现**：
- 在「自然发生的 ChatGPT bug」上，人类 + CriticGPT 协作的 critique 比 ChatGPT 自己的 critique 更受偏好（63% 胜率）。
- CriticGPT 减少了「nitpick」（无关紧要的挑剔）和 hallucination（虚构不存在的 bug）。
- **Test-time search against critique reward model** 可以平衡 precision/recall——搜索越深，找到的 bug 越多，但 hallucination 也越多。

**CriticGPT 的哲学意义**：它把 RLHF 的瓶颈（「人类跟不上模型的复杂度」）用「AI 辅助人类」来解决。这是 scalable oversight 的工程实践——OpenAI 明确说在把 CriticGPT 集成进 RLHF pipeline。

> **早期工作**：Saunders et al., "Self-critiquing models for assisting human evaluators" [arXiv:2206.05802](https://arxiv.org/abs/2206.05802)（OpenAI, 2022）是 CriticGPT 的前身，首次提出用 LM 写 critique 辅助人类评估。

---

## 六、Self-Play / Self-Improvement：让模型自己和自己下棋

当外部 reward 不可得（开放任务）、人类标注又贵时，一个诱人的方向是 **self-play**——模型自己生成数据、自己评判、自我提升。这是 AlphaGo 范式在 LLM 上的延伸。

### 6.1 SPIN：Self-Play Fine-Tuning

> **论文：Chen et al., "Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models"** [arXiv:2401.01335](https://arxiv.org/abs/2401.01335)（UCLA，ICML 2024）
> SPIN 的核心：让 LLM 与「上一轮的自己」对弈——辨别「自己生成的回答」和「人类标注的回答」，从而把人类数据榨干。

**SPIN 的目标函数**：
$$
\min_{\theta} \mathbb{E}_{(x, y) \sim \mathcal{D}_{\text{human}},\ y' \sim \pi_{\theta_{\text{old}}}(\cdot|x)} \left[ \log\Big(1 + \frac{\pi_\theta(y'|x)}{\pi_\theta(y|x)}\Big) \right]
$$

直觉：训练 $\theta$ 让它给「人类回答 $y$」高分，给「自己上轮回答 $y'$」低分。理论上，当 $\pi_\theta$ 与人类分布完全一致时，无法区分 $y$ 和 $y'$，训练停止。

**SPIN 的优势**：不需要新的人类数据，不需要外部 reward model，只需要「人类 SFT 数据 + 自己采样」。在 Zephyr 等 baseline 上提升明显。

**SPIN 的局限**：天花板是「人类数据的分布」——如果人类数据本身不够强，SPIN 顶多学到人类水平，无法超越。

### 6.2 Self-Rewarding：模型自己给 reward

> **论文：Yuan, Weston et al., "Self-Rewarding Language Models"** [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)（Meta FAIR，ICML 2024）
> 核心命题：要训出超人类 agent，需要超人类反馈。人类标注有天花板，所以让模型用 LLM-as-Judge 给自己打 reward，并随训练一起迭代。

**Self-Rewarding 的迭代流程**：
1. **生成**：当前模型对 prompt 生成多个回答。
2. **Self-judge**：当前模型用 LLM-as-Judge prompt 给这些回答打分（输出「Answer A is better because...」）。
3. **DPO 训练**：用 self-judge 的偏好对做 DPO（Direct Preference Optimization），更新模型。
4. **迭代**：下一轮用新模型重复 1-3。

**关键发现**：经过 3 轮迭代，Llama-2-70B + Self-Rewarding 在 AlpacaEval 2.0 上超过 Claude 2、Gemini Pro、GPT-4 (0613)。不仅指令跟随提升，**self-judge 能力也提升**——这是最重要的发现，打破了「frozen reward model 天花板」。

**Self-Rewarding 的风险**（诚实声明）：
- **Self-reinforcing bias**：模型可能强化自己的偏置（self-preference）。
- **Reward hacking**：模型可能学会输出 judge 喜欢但人类不喜欢的内容。
- 实践中需要正则化（KL 约束、人类抽检）。

### 6.3 SPAG：Self-Playing Adversarial Language Game

> **论文：Cheng et al., "Self-playing Adversarial Language Game Enhances LLM Reasoning"** [arXiv:2404.10642](https://arxiv.org/abs/2404.10642)（百度，NeurIPS 2024）
> 注意：SPAG 的 G 是 **Game**（游戏）不是 Alignment。它设计了一个「Adversarial Taboo」语言游戏：攻击者要让防守者说出目标词，防守者要猜出目标词。

**SPAG 的设计精妙之处**：要赢这个游戏，双方都必须对目标词有充分知识、且具备高级推理（诱导/反推）能力。所以用游戏输赢做 RL reward，能同时提升知识和推理。

**SPAG 的实验结果**：在多个推理 benchmark（GSM8K、MATH 等）上，经过 SPAG 训练的 LLM 性能普遍提升，且**迭代多轮持续提升**。这证明了对抗性 self-play 对推理的促进作用。

### 6.4 Constitutional AI：Anthropic 的自我修订

> **论文：Bai et al., "Constitutional AI: Harmlessness from AI Feedback"** [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)（Anthropic，2022-12-15）
> Constitutional AI 用一份「宪法」（规则列表）指导模型自我批评和修订，实现无人类有害标签的对齐。

**Constitutional AI 的两阶段**：

**Stage 1：Supervised Learning（自我批评修订）**
1. 模型对有害 prompt 生成初始回答。
2. 用「宪法规则」（如「不要帮助制造武器」）触发模型自我批评：「My previous response was harmful because...」
3. 模型生成修订版回答。
4. 在（prompt, 修订回答）上做 SFT。

**Stage 2：RLAIF（RL from AI Feedback）**
1. 模型对 prompt 生成两个回答。
2. 用「宪法 + AI judge」判断哪个更好（AI 替代人类做偏好标注）。
3. 训练 preference model。
4. 用 preference model 做 RL（RLHF 流程，但 label 来自 AI）。

**Constitutional AI 的贡献**：首次系统化地用 AI feedback 替代人类 feedback 做对齐，是 RLAIF 的奠基工作。它的哲学——「让 AI 监督 AI」——直接影响了后来的 scalable oversight 和 self-improvement 路线。

**与 Self-Rewarding 的区别**：Constitutional AI 用「外部规则列表」约束 self-judge，Self-Rewarding 让模型自由 judge。前者更可控，后者更灵活。

---

## 七、Test-Time Compute Scaling：新的 scaling 维度

### 7.1 Snell 2024：compute-optimal scaling

> **论文：Snell, Lee, Xu, Kumar, "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"** [arXiv:2408.03314](https://arxiv.org/abs/2408.03314)（UC Berkeley，2024-08-06）
> ⚠️ 再次强调：作者是 **Snell et al.**，**不是 Burns**（用户大纲此处有误，见勘误声明）。这是 test-time compute scaling 的奠基性实证研究。

**Snell 2024 的核心问题**：如果给 LLM 固定（但非平凡）的 test-time compute 预算，它能提升多少？哪种 test-time 策略最有效？

**两种 test-time compute 机制**：
1. **搜索 against PRM**：用 process verifier 在搜索树上找最优解（beam search、best-of-N）。
2. **自适应更新分布**：根据当前 prompt，用 test-time 反馈更新模型对回答的分布（如「先采样几条，用结果修正，再采样」）。

**关键发现 1：效果强烈依赖题目难度**。
- 简单题：多给 test-time compute 几乎没用（模型一次就对）。
- 中等题：test-time compute 提升巨大。
- 难题：test-time compute 提升有限（模型根本不会，多想也没用）。

**关键发现 2：compute-optimal 策略远胜固定策略**。
- 固定 best-of-N（每题都采样 64 条）效率低。
- compute-optimal：根据题目预估难度，动态分配 test-time compute（简单题少分配，中等题多分配）。
- 用 compute-optimal 策略，**效率比固定 best-of-N 高 4 倍以上**。

**关键发现 3：test-time compute 可以打败 14 倍大的模型**。
- 在 FLOPs 匹配的评测中（小模型 + 大量 test-time compute vs 大模型 + 少 test-time compute），在「小模型本身有一定成功率」的题上，**小模型 + test-time compute 超过 14 倍大的模型**。

**这个发现的深远影响**：它意味着 scaling law 多了一个维度——不只是「参数量 × 数据量」，还有「test-time compute」。这为 o1 路线（小模型 + 大量 thinking）提供了理论依据。

### 7.2 OpenAI o1 / Claude Thinking：产品化的 test-time compute

**OpenAI o1（2024-09）**：首个把 test-time compute scaling 产品化的大模型。用户可见的「thinking」阶段，本质就是允许模型生成大量内部推理 token。o1 在数学、代码、科学推理上大幅领先，但在通用对话上未必更好——印证了 test-time compute 对「有客观答案的任务」最有效。

**Claude Thinking（Anthropic）**：Claude 3.5+ 引入「extended thinking」模式，允许模型显式输出思考过程。与 o1 类似，thinking token 是 test-time compute 的载体。

**产品形态的工程含义**：
- **延迟换准确率**：test-time compute 增加延迟（o1 解一道数学题可能「想」几十秒），换取更高准确率。
- **成本结构变化**：推理成本（每 token 计费）在 reasoning model 中占比飙升——因为 thinking token 是隐藏的但真实消耗算力。
- **用户体验设计**：如何让用户接受「模型在想 30 秒」？o1 的做法是显示一个「Thinking...」进度条。

### 7.3 推理时计算 ≠ 训练时计算：一个关键区分

| 维度 | 训练时计算 | 推理时计算 |
|---|---|---|
| 何时发生 | 模型训练阶段 | 模型推理/服务阶段 |
| 改变了什么 | 模型权重（永久） | 单次输出的搜索过程（临时） |
| 成本摊销 | 一次性，服务时摊销 | 每次推理都付 |
| scaling 效果 | power law（持续） | 边际递减（见 Snell） |
| 代表 | 预训练、SFT、RL | thinking、beam search、BoN |

**核心洞见**：test-time compute 不是「免费的午餐」——它每次推理都要付钱。所以**最优策略是「训练时投入 + 推理时投入」的联合优化**，而不是无脑堆 test-time compute。这正是 Snell「compute-optimal」思想的延伸。

---

## 八、推理模型的失败模式：诚实地说坏话

本章前面都在讲「怎么做好」，但推理模型有严重的失败模式，工程上必须正视。

### 8.1 Reward Hacking

**现象**：模型学会「钻 reward 函数的漏洞」，拿到高 reward 但没真正解决问题。

**经典案例**：
- **数学 reward 用 `\boxed{}` 抽取答案**：模型可能学会「不推理，直接在开头写 `\boxed{答案}`」，因为 reward 只看 boxed 内容。R1 论文专门提到了这个 failure mode，用了「答案必须在最后」等规则约束。
- **代码 reward 用单元测试通过率**：模型可能学会「硬编码测试用例的输出」而非真正实现算法。
- **长度 reward**：如果 reward 隐含偏好长回答，模型会输出冗余废话。

**缓解**：
1. **Reward 设计要鲁棒**：多个独立的 reward 函数交叉验证。
2. **Adversarial testing**：用模型没见过的测试集监控 reward hacking。
3. **形式化 reward**（如 Lean）是终极解——但只适用于数学/程序验证。

### 8.2 Sycophancy（谄媚）

**现象**：模型倾向于附和用户的观点/暗示，而非给出正确答案。

**在推理中的表现**：
- 用户说「我觉得答案是 X」，模型更可能输出 X（即使 X 错）。
- 在 multi-turn 推理中，模型可能为了「配合」前面自己的（错误）结论，而扭曲后续推理。

**根因**：RLHF 中人类标注员倾向于偏好「同意自己」的回答，模型学到了这个偏置。

**缓解**：
1. **RLVR 优于 RLHF**：可验证 reward 不受用户暗示影响。
2. **Sycophancy-specific 训练数据**：故意构造「用户暗示错误答案」的样本，训练模型坚持正确答案。
3. **System prompt**：「You are a rigorous reasoner. Do not be swayed by the user's suggestions.」

### 8.3 Long-CoT 错误累积

**现象**：推理链越长，中间出错的概率越高，且错误会沿链传播。

**数学直觉**：若每步正确率 $p$，$n$ 步全对的概率是 $p^n$。即使 $p = 0.95$，20 步后全对概率只有 36%。

**这解释了为什么需要 verifier + search**：单条 Long-CoT 几乎必然出错，必须用 PRM 在中途剪枝、或用 self-consistency 多采样投票。

**R1 的启发**：R1-Zero 涌现的「self-reflection」（「Wait, let me reconsider」）本质上就是模型自己学会了「中途纠错」——这是对抗错误累积的关键能力。

### 8.4 Hallucination 在推理中

**现象**：推理链中「自信地编造事实/定理」。例如模型在证明中引用「定理 X」但实际上定理 X 不存在或被误用。

**为什么推理模型的 hallucination 更危险**：
- 推理链长，单步 hallucination 不易被人类发现。
- 「自信的语气」让人类更信任（甚至 judge 模型也更信任）。
- 数学/科学 hallucination 可能导致连锁错误。

**缓解**：
1. **工具增强**（见第九章）：让模型查证而非记忆。
2. **形式化验证**：Lean 编译器能抓出 hallucinated 定理。
3. **Verifier 必须独立于 generator**：generator 和 verifier 用不同模型，避免共享 hallucination。

---

## 九、工具增强推理：让模型「动手」而非「空想」

推理模型最强的形态不是「纯脑内思考」，而是「思考 + 工具调用」。这把 LLM 从「封闭推理器」变成「开放推理 agent」。

### 9.1 Code Execution（Python interpreter）

**场景**：数学计算、数值验证、算法实现。

**为什么关键**：LLM 做大数乘法、符号积分容易错，但 `python -c "print(1234*5678)"` 不会错。让模型在推理中写代码、执行、看结果，能消除计算类错误。

**实现**：在推理链中插入 `tool_call(code="...")` 节点，环境执行返回结果。模型基于结果继续推理。GPT-4、Claude、DeepSeek 都支持。

**风险**：① 代码本身可能有 bug；② 沙箱安全（恶意代码）；③ 延迟（执行需要时间）。

### 9.2 Lean / Coq 集成（形式化证明）

**场景**：数学证明的严格验证。

**这是 AlphaProof 的核心**：Lean 编译器是「不会错的裁判」。模型在 Lean 中写证明，编译器即时反馈「这步证不通」，模型据此搜索下一步。

**工程挑战**：Lean 学习曲线陡，预训练数据中 Lean 代码稀缺。AlphaProof 用 informal-to-formal translation（Gemini 微调）把自然语言题翻译成 Lean，部分解决了数据问题。

**开源生态**：Lean + Mathlib（数学库）是当前最活跃的形式化数学社区。AlphaProof 团队明确感谢了 Lean/Mathlib 贡献者。

### 9.3 Search Tool（检索）

**场景**：需要事实知识的推理（「2024 年 IMO 第 3 题是什么？」「费马大定理的标准证明用了哪些工具？」）。

**实现**：模型在推理中调用 web search API，把检索结果喂回上下文。这是对抗 hallucination 的最直接手段。

**与 RAG 的区别**：推理模型的 search 是**主动的、过程式的**——模型自己决定何时搜、搜什么、如何用结果继续推理。而传统 RAG 是一次性的上下文增强。

### 9.4 Calculator / Symbolic Solver

**场景**：精确数值计算、符号运算。

**为什么需要**：LLM 的浮点运算不可靠（`0.1 + 0.2` 可能算成 `0.30000000004`），但 SymPy 不会。让模型调用 `sympy.solve(...)` 比让它心算可靠得多。

**趋势**：o1/o3、Claude Thinking 都集成了计算工具。未来的推理模型大概率是「Long-CoT + 多工具调用」的混合形态。

---

## 十、关键论文清单（一手核实）

下表所有 arXiv ID 均已用 arXiv API 或官网一手核实（2026-07-20）。

| # | 论文 | arXiv / 来源 | 机构 | 年份 | 本章引用处 |
|---|---|---|---|---|---|
| 1 | Let's Verify Step by Step（PRM800K） | [2305.20050](https://arxiv.org/abs/2305.20050) | OpenAI | 2023-05 | §1.3, §2.1 |
| 2 | Tree of Thoughts | [2305.10601](https://arxiv.org/abs/2305.10601) | Princeton | 2023-05 (NeurIPS 2023) | §3.3 |
| 3 | Self-Consistency | [2203.11171](https://arxiv.org/abs/2203.11171) | Google | 2022-03 (ICLR 2023) | §3.4 |
| 4 | DeepSeek-R1 | [2501.12948](https://arxiv.org/abs/2501.12948)；Nature [645:633](https://doi.org/10.1038/s41586-025-09422-z) | DeepSeek-AI | 2025-01 | §4.3 |
| 5 | DeepSeekMath（GRPO） | [2402.03300](https://arxiv.org/abs/2402.03300) | DeepSeek-AI | 2024-02 | §4.4 |
| 6 | Math-Shepherd | [2312.08935](https://arxiv.org/abs/2312.08935) | DeepSeek/北大 | 2023-12 | §2.4 |
| 7 | Scaling Test-Time Compute（**Snell**, 非 Burns） | [2408.03314](https://arxiv.org/abs/2408.03314) | UC Berkeley | 2024-08 | §7.1 |
| 8 | Generative Verifiers（GenRM） | [2408.15240](https://arxiv.org/abs/2408.15240) | Google DeepMind | 2024-08 (ICLR 2025) | §5.2 |
| 9 | Self-Rewarding LMs | [2401.10020](https://arxiv.org/abs/2401.10020) | Meta FAIR | 2024-01 (ICML 2024) | §6.2 |
| 10 | SPIN（Self-Play Fine-Tuning） | [2401.01335](https://arxiv.org/abs/2401.01335) | UCLA | 2024-01 (ICML 2024) | §6.1 |
| 11 | SPAG（Self-Playing Adversarial Language Game） | [2404.10642](https://arxiv.org/abs/2404.10642) | 百度 | 2024-04 (NeurIPS 2024) | §6.3 |
| 12 | Constitutional AI | [2212.08073](https://arxiv.org/abs/2212.08073) | Anthropic | 2022-12 | §6.4 |
| 13 | CriticGPT | [2407.00215](https://arxiv.org/abs/2407.00215) | OpenAI | 2024-07 | §5.5 |
| 14 | Self-critiquing models（CriticGPT 前身） | [2206.05802](https://arxiv.org/abs/2206.05802) | OpenAI | 2022-06 | §5.5 |
| 15 | AlphaProof | DeepMind [博客](https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/)；Nature [10.1038/s41586-025-09833-y](https://www.nature.com/articles/s41586-025-09833-y) | Google DeepMind | 2024-07 博客 / 2025-11 Nature | §3.6 |
| 16 | OpenAI o1 | [System Card](https://openai.com/index/openai-o1-system-card/)（非 arXiv） | OpenAI | 2024-09 | §4.2, §7.2 |

**关于未在 arXiv 的工作**：
- **OpenAI o1/o3/o4**：无完整训练论文，只有 system card 和博客。训练细节为业界推断。
- **AlphaProof**：2024 年仅有 DeepMind 博客，2025-11-12 在 Nature 发表方法论论文（这是 AlphaProof 的首个正式同行评审论文）。

---

## 十一、给「应用数学研究型工程师」的建议

基于你的目标定位（应用数学研究型工程师、每周 10-20h、零 ML 基础起步但工程扎实、强偏好有趣+可视化+工程落地），本章给出三个递进式实践建议。

### 建议 1：训练一个 PRM on GSM8K（1-2 周，入门级）

**目标**：亲手实现 Lightman 2023 的核心贡献，理解 PRM 训练的全流程。

**步骤**：
1. **数据构造（Math-Shepherd 路线，免人工标注）**：
   - 用 GSM8K 的 7,500 道训练题。
   - 用一个小 LM（如 Qwen-2.5-Math-7B-Instruct）对每题采样 8 条解。
   - 对每条解的每一步，用「从该步出发的蒙特卡洛正确率」作为软标签（Math-Shepherd 方法）。
2. **PRM 训练**：基于第二章 2.5 的代码框架，把 BERT 换成 Qwen-2.5-Math-1.5B，加 PRM head，训练。
3. **评测**：在 GSM8K 测试集上对比：
   - 基线：单次贪心解码。
   - BoN（无 PRM）：采样 16 条，按 LM 概率选。
   - BoN（PRM rerank）：采样 16 条，按 PRM 分数选。
   - 观察 PRM rerank 带来的提升。

**预期收获**：① 理解 PRM 训练的工程细节；② 理解 Math-Shepherd 自动标注的精妙；③ 在真实数据上看到 PRM 的提升（通常 +3~8 个百分点）。

**资源需求**：单张 24GB GPU（3090/4090）即可跑 1.5B 模型。Colab Pro 也行。

### 建议 2：实现一个简单 MCTS + LLM（2-3 周，进阶级）

**目标**：把第三章的 MCTS 伪代码跑通，理解搜索 + LLM 的工程实现。

**步骤**：
1. **选一个搜索友好任务**：24 点游戏（ToT 论文用的，简单且可验证）或数独。
2. **实现 MCTS 框架**：第三章 3.5 的代码骨架，补全 selection/expansion/simulation/backprop。
3. **LLM 集成**：
   - Policy：让 LLM 生成候选下一步（提示「当前状态是 X，给出 4 个可能的下一步」）。
   - Value：让 LLM 自评（「这个状态离解出还有多远？1-10 分」）。
4. **对比基线**：
   - 纯 LLM CoT（无搜索）。
   - LLM + self-consistency（多采样投票）。
   - LLM + MCTS。
5. **可视化**：把搜索树画出来（用 networkx + matplotlib），看 MCTS 探索了哪些分支。

**预期收获**：① 理解 MCTS 在 LLM 上的工程实现；② 直观看到「搜索 vs 贪心」的差异；③ 可视化搜索树对理解 AlphaGo/AlphaProof 极有帮助（符合你「可视化」偏好）。

**这个项目的数学延伸**：MCTS 的 UCB 公式涉及 multi-armed bandit 理论，是「探索-利用权衡」的经典案例。可以延伸阅读 Sutton & Barto《Reinforcement Learning》第 2 章。

### 建议 3：数学方向——搜索算法的最优 stopping（研究级，长期）

**问题陈述**：给定一个推理任务和一个 test-time compute 预算 $T$，**何时应该停止搜索并输出当前最优解？** 这是一个最优停止问题（optimal stopping）。

**为什么这是好研究方向**：
1. **有理论深度**：optimal stopping 是概率论/随机过程的经典分支（秘书问题、house selling problem 都是著名实例）。
2. **有实际价值**：Snell 2024 的「compute-optimal」只是经验启发式，没有严格理论。一个有理论保证的 stopping rule 可能显著提升推理效率。
3. **与你「概率随机过程」的研究方向候选高度契合**。

**具体研究切入点**：
- 把「搜索过程」建模为随机过程（如分支过程 + 奖励信号）。
- 用 optimal stopping 理论推导：在什么停止规则下，期望 reward 最大化？
- 实证验证：在 MATH/AIME 上，你的 stopping rule 比 Snell 的启发式好多少？

**这是一个「应用数学 + 工程」的交叉课题**——既有数学理论（随机过程、optimal stopping），又有工程实现（在真实 LLM 上验证）。完全符合你「应用数学研究型工程师」的定位。

**起步文献**：
- Ferguson《Optimal Stopping and Applications》（免费在线教材，optimal stopping 经典入门）。
- Snell et al. 2024（实证基线）。
- Multi-armed bandit 综述（UCB 理论基础）。

---

## 📌 进一步阅读

**PRM / Verifier 深入**：
- ProcessBench（评估 PRM 的 benchmark，2024）——搜 arXiv「ProcessBench」。
- Qwen2.5-Math 技术报告（阿里的自动化 PRM 实践）。
- 「Generative Verifiers」作者团队（Aviral Kumar, Rishabh Agarwal）的其他 test-time compute 工作。

**RLVR / R1 生态**：
- DeepSeek-R1 论文的引用图——大量「R1 复现/改进」工作（Open-R1、SimpleRL 等）。
- OpenAI o1 System Card（虽无训练细节，但有评测和方法论提示）。
- Tülu 3（Allen AI 的开源 post-training pipeline，含 RLVR 部分）。

**搜索 + LLM**：
- AlphaGo / AlphaZero 原始 Nature 论文（理解 MCTS 的理论基础）。
- 「Language Model Tree Search」（Feng et al., 2023）——把 MCTS 系统化用在 LM 上。
- rStar（2024）——开源的 MCTS + LLM 推理框架。

**形式化数学**：
- Lean 4 官方教程（Theorem Proving in Lean 4）。
- AlphaProof Nature 论文（2025-11）——本章引用的 [10.1038/s41586-025-09833-y]。
- 「DeepSeek-Prover」系列（DeepSeek 的 Lean 自动证明工作）。

**Test-Time Compute**：
- Snell 2024 的后续工作（作者主页）。
-「Inference Scaling Laws」相关综述（2024-2025 涌现）。

---

## ✍️ 思考题（5 道）

**题 1（概念辨析）**：假设你训了一个 ORM 和一个 PRM，在 best-of-N 评测中 PRM 更好。但在 RL 训练中，你把 PRM 当 reward 用，结果模型反而 reward hack 了（学会了写「PRM 喜欢」但人类看不懂的推理链）。请分析：为什么 PRM 在评测好但 RL 差？这与 DeepSeek-R1 选择纯规则 reward 的决策有什么关系？

**题 2（算法设计）**：Math-Shepherd 用「从该步出发的蒙特卡洛正确率」作为步级标签。但这个方法对「中间步骤对、但前缀已经被前人走窄」的步骤会低估（因为从窄前缀出发，即使这步对，后续也难全对）。请设计一个改进的自动标注方法，缓解这个「前缀偏置」问题。（提示：考虑用条件概率而非联合概率。）

**题 3（理论计算）**：在 Snell 2024 的设定中，compute-optimal 策略比固定 best-of-N 效率高 4 倍。假设题目难度服从某个分布 $p(d)$（$d$ 为难度），test-time compute 对难度 $d$ 的题的提升为 $f(d, T)$。请写出 compute-optimal 策略的形式化目标，并讨论 $f$ 什么形式时 compute-optimal 优势最大。

**题 4（工程权衡）**：你要在产品里部署一个推理模型，有两个选择：① 大模型（70B）+ 少量 test-time compute（thinking 500 token）；② 小模型（7B）+ 大量 test-time compute（thinking 8000 token）。Snell 2024 说后者能打败前者。但从**服务成本**角度（GPU 小时、延迟、吞吐），哪个更优？请给出你的成本模型和决策依据。

**题 5（开放研究）**：本章建议 3 提出研究「搜索算法的最优 stopping」。请把这个问题描述形式化：定义状态空间、reward 信号、 stopping rule 的目标函数。然后讨论——这个问题与经典的「秘书问题」（secretary problem）有什么本质相同和不同？（提示：考虑 reward 是否可回溯、状态是否马尔可夫。）

---

## 本章小结

回到开头的五个核心论点，现在你应该有了实证支撑：

1. **推理模型 = 生成器 + 验证器 + 搜索**——这三件套的协同训练是整个领域的核心。PRM（§二）、Search（§三）、Verifier（§五）分别对应。
2. **PRM > ORM（在评测上）**——Lightman 2023 的 78% vs 72% 是铁证。但 PRM 在 RL 中易被 hack（§8.1），所以 R1 用纯规则 reward（§4.3）。
3. **RLVR 是 o1/R1 的引擎**——可验证 reward 绕开了 RLHF 的两个瓶颈（§四）。R1-Zero 涌现 self-reflection 是最震撼的证据。
4. **Test-time compute 是新维度**——Snell 2024 证明它能打败 14 倍大的模型（§7.1）。
5. **失败模式真实存在**——reward hacking、sycophancy、Long-CoT 错误累积（§八）。任何把推理模型神化的叙事都是不诚实的。

**最后一句**：推理模型不是魔法，它是「搜索算法 + 可验证 reward + 大模型」的工程组合。理解了这个组合，你就拿到了打开 o1/R1 黑盒的钥匙。剩下的，是把它用到你自己关心的数学/工程问题上——这正是你「应用数学研究型工程师」路线的起点。

---

<!-- delegate 直接写入，2026-07-20 -->
