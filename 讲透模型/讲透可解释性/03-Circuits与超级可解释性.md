# 03 · Circuits 与超级可解释性：找模型内部的功能回路

> 承接 [02-稀疏自编码器SAE](./02-稀疏自编码器SAE.md)。02 把单个神经元/激活分解成 monosemantic 特征——但模型**不是靠单个特征计算**，而是靠**特征之间的连线**。本章讲 circuits：怎么找这些连线，superposition 为什么让它难，induction head 这个最经典的 circuit 是怎么被发现的。
>
> 配套：[`00-为什么AI是黑箱`](./00-为什么AI是黑箱.md) + [`讲透Transformer`](../讲透Transformer/)

---

## 直觉层

### 一个具体时刻

> 2022 年 3 月，Anthropic 的 Catherine Olsson 在 Transformer Circuits Thread 发表了一篇没投会议的长文："In-context Learning and Induction Heads"。她跑遍 40 多个 transformer，发现一个**普适规律**：**只要模型有 2 层以上 attention，几乎所有模型都长出了一个叫 induction head 的回路**。
>
> induction head 干的事很简单——**复制匹配模式**：看到 `[A][B]...[A]` 就预测 `[B]`。但 Olsson 证明了这个小小的 circuit **是 in-context learning（ICL）的物理基础**——所有 prompt 里"few-shot 学新任务"的能力，本质都是 induction head 在工作。

**角色**：Olsson（Anthropic 研究者）。**冲突**：以前所有人都在猜"ICL 是怎么实现的"——是 attention？是 MLP？是涌现？没人有定论。**时刻**：跨 40 个模型看到同一个 circuit 出现，意识到它**不是偶然**而是 ICL 的物理实现。

### Circuit 是什么

**Circuit = 一组神经元/attention head + 它们之间的连线，共同实现某个功能**。类比生物神经科学：

| 神经科学 | Interpretability |
|---|---|
| 神经元（neuron） | 模型神经元 / SAE 特征 |
| 突触（synapse） | 权重 / attention pattern |
| 神经回路（neural circuit） | circuit |
| 视觉皮层 V1 的方向选择性细胞 | GPT-2 里的 induction head |

Circuit 是**功能层面的最小单位**——单个神经元没有"功能"，只有神经元组合起来才有。

### Anthropic 的 Circuits Thread 计划（2021-至今）

Chris Olah 主导的长线研究项目，目标：**逆向工程 transformer**。第一阶段（2020-2022）在小模型上找到了几个经典 circuit：

- **Induction head**（2022）—— ICL 的基础
- **Indirect Object Identification, IOI**（Wang 2022）—— "John gave the book to Mary, then he gave it to ___"怎么填
- **Successor head**（Gould 2024）—— 数字/字母的"下一个"：1→2, a→b

这是 mechanistic interpretability 的**地基**——证明"找 circuit"在小模型上是可行的。

---

## 数学层

### Circuit 的形式化

一个 circuit 可以表示为一个**子计算图**：

$$\mathcal{C} = (V_{\mathcal{C}}, E_{\mathcal{C}})$$

其中 $V_{\mathcal{C}}$ 是参与计算的神经元/attention head 集合，$E_{\mathcal{C}}$ 是它们之间的信息流（权重 / QK / OV pattern）。

**判定一个 circuit $\mathcal{C}$ 实现"功能 $f$"** 需要满足两个条件：

1. **必要性（ablation）**：从模型中删除 $\mathcal{C}$ → 功能 $f$ 大幅下降。
   $$\text{ablation\_effect}(\mathcal{C}, f) = f(\text{full\_model}) - f(\text{model} \setminus \mathcal{C})$$

2. **充分性（sufficiency）**：只用 $\mathcal{C}$（其他部件归零）→ 功能 $f$ 基本保留。
   $$\text{sufficiency}(\mathcal{C}, f) = f(\mathcal{C} \text{ alone})$$

两个条件都满足才算"找到了对的 circuit"。

### Induction Head 的精确公式

Induction head 是**两个 attention head 的协作**：

```
输入：  [A][B]  ...  [A]
位置：   1  2       t

Step 1: Previous Token Head（在 layer L）
  把 token $t-1$ 的内容信息复制到 token $t$ 的 position。
  即：position $t$ 的 K vector 里现在有 "前面是 [A]" 的信息。

Step 2: Induction Head（在 layer L+1）
  Q: "我在找前面是 [A] 的位置"
  K: 匹配 Previous Token Head 写入的信息
  V: 把匹配位置的**下一个** token（即 [B]）复制到当前位置。
```

形式化（简化）：设 $h^{(L)}_{\text{prev}}$ 是 previous token head 的输出，$h^{(L+1)}_{\text{ind}}$ 是 induction head 的输出：

$$h^{(L+1)}_{\text{ind}} = \text{Attn}\left(Q = W_Q \cdot x_t, \; K = W_K \cdot h^{(L)}_{\text{prev}}, \; V = W_V \cdot h^{(L)}_{\text{prev}}\right)$$

关键是 $K$ 用的是**前一层 prev head 的输出**，不是当前 token——这就实现了"匹配前一个 token"的模式。

**Prefix matching score**（Olsson 2022 提出，用来检测 induction head）：

$$\text{prefix\_score}(h) = \frac{\mathbb{E}_{[A][B]...[A] \to [B]}[\text{logit}_{[B]}]}{\mathbb{E}_{\text{random prefix}}[\text{logit}_{[B]}]}$$

高于阈值的 head 就是 induction head。

### Superposition：为什么找 circuit 难

如果在 00 章基础上加一层：**单个 circuit 可能不是"局部几个神经元"**——它可能在 superposition 中**分散在全模型**。

设真实功能 $\phi$ 对应一个概念向量 $v_\phi \in \mathbb{R}^N$，模型把它编码进 $d$ 维激活空间（$d \ll N$）：

$$v_\phi \approx \sum_{i \in S_\phi} W_{i \to h} \cdot \text{neuron}_i$$

其中 $S_\phi$ 是涉及 $\phi$ 的神经元集合，可能跨多层。**当 superposition 严重时 $S_\phi$ 可能是全模型的 30%**——这时"找 circuit"就接近"找全模型的所有相关连接"。

---

## 代码层

```python
import torch
from transformer_lens import HookedTransformer
from transformer_lens.utils import get_act_name

model = HookedTransformer.from_pretrained("gpt2-small")

# === 检测 induction head（prefix matching score）===
def compute_prefix_score(model, head: tuple[int, int], seq_len: int = 64, n_samples: int = 200):
    """Olsson 2022 的检测方法：
    构造 [random_tokens][random_repeat_first_half] → 测模型对"重复段的下一个 token"的预测置信度
    """
    layer, head_idx = head
    scores = []
    for _ in range(n_samples):
        # 构造 [A B C | A B ?] 类型的序列
        first_half = torch.randint(0, model.cfg.d_vocab, (seq_len // 2,))
        seq = torch.cat([first_half, first_half[:-1]])  # [A B C A B]
        # 目标：第二个 A 之后应该预测 B（induction head 应该会做对）
        with torch.no_grad():
            logits = model(seq.unsqueeze(0))  # [1, seq_len, d_vocab]
        # 检测倒数第二个位置（第二个 B 出现的位置）的 head 是否 attend 到第一个 B
        _, cache = model.run_with_cache(seq.unsqueeze(0))
        pattern = cache["pattern", layer][0, head_idx]  # [seq_len, seq_len]
        # induction head 的 pattern：position t attend 到 "前一个 token 等于 seq[t-1]" 的位置
        target_pos = seq_len - 2
        attended = pattern[target_pos]  # 该位置对前面所有位置的 attention 权重
        # 正确的 attended 位置：前面 token 等于 seq[target_pos - 1] 的位置 + 1
        target_token = seq[target_pos - 1].item()
        correct_positions = [i + 1 for i in range(seq_len - 1) if seq[i].item() == target_token]
        if correct_positions:
            score = sum(attended[p].item() for p in correct_positions)
            scores.append(score)
    return sum(scores) / len(scores)

# 扫所有 head，找 induction head
def find_induction_heads(model):
    candidates = []
    for layer in range(model.cfg.n_layers):
        for head in range(model.cfg.n_heads):
            score = compute_prefix_score(model, (layer, head))
            if score > 0.3:  # 经验阈值
                candidates.append(((layer, head), score))
    return sorted(candidates, key=lambda x: -x[1])

# === Ablation：验证 circuit 必要性 ===
def ablate_head(model, head: tuple[int, int], prompt: str):
    """把某 head 的输出置零，测模型行为变化"""
    layer, head_idx = head
    def hook(module, input, output):
        # output: [batch, seq, n_heads, d_head] → 把指定 head 置零
        output[:, :, head_idx, :] = 0
        return output
    hook_handle = model.blocks[layer].attn.hook_z.register_forward_hook(hook)
    logits = model(prompt)
    hook_handle.remove()
    return logits

# === SAE × Circuits：用 SAE 特征代替神经元重新找 circuit ===
def circuit_with_sae_features(sae, model, prompt: str, target_feature_idx: int):
    """现代做法（2024+）：不再用单个神经元，用 SAE 特征找 circuit
    步骤：
    1. 跑模型 + SAE，拿到所有层的 SAE 特征激活
    2. 对目标特征 target_feature_idx，找出"激活它需要哪些上游特征"
    3. 这些上游特征 + 它们的连线 = circuit
    """
    _, cache = model.run_with_cache(prompt)
    circuit = {target_feature_idx: []}
    for layer in range(model.cfg.n_layers):
        h = cache["resid_post", layer][0, -1]  # 简化：只看最后一个 token
        _, _, z = sae(h.unsqueeze(0))
        active_features = (z[0] > 0).nonzero().flatten().tolist()
        if target_feature_idx in active_features:
            # 这层的其他激活特征是上游候选
            circuit[target_feature_idx].append((layer, active_features))
    return circuit
```

**反直觉数字**：Olsson 2022 发现 **induction head 在几乎所有 2+ 层 transformer 上都自发出现**——包括只训了 100M token 的小模型。这说明它是**最基础的计算原语**，模型一有能力就先长出它。这也解释了为什么 ICL（few-shot 学习）在 transformer 上**几乎是免费的**——它的物理基础太容易出现了。

---

## 不足层

- **已证明**：
  - **Induction head 在小模型上的存在性**（Olsson 2022）：跨 40+ 模型，2 层以上 transformer 几乎都有。ablation 实验证明它的必要性。
  - **IOI circuit**（Wang 2022）在 GPT-2 small 上找到了 26 个 head 的完整回路，ablation 验证充分性。
  - **Superposition 几何**（Elhage 2022 toy model）：在 toy setting 严格证明了稀疏→叠加。

- **经验**：
  - **Circuit 在大模型上更难找**——GPT-4 级别几乎没找到完整 circuit，只在 SAE 特征层面找到局部。
  - **Automated circuit discovery**（Conmy 2023 ACDC，Syed 2023 EAP）能半自动找 circuit，但精度和召回都不如手工。

- **未解**：
  1. **Superposition 下的 circuit 完整性**：当 circuit 分散在全模型 30% 的神经元上，怎么找？SAE 提供了部分工具但不够。
  2. **大模型上 circuit 的尺度**：GPT-4 级别，一个 reasoning 行为可能涉及几百万神经元——还是能分解成局部 circuit 吗？还是 circuit 概念本身在大模型上失效？**这是 mechanistic interpretability 的最大开放问题**。
  3. **Circuit 与涌现的关系**：大规模涌现的能力（复杂推理、长程 planning）是局部 circuit 还是分布式的？没人知道。
  4. **"Universal circuit"假设**：induction head 在所有 transformer 上都出现——其他功能（如 reasoning）也有 universal circuit 吗？只有零星证据（successor head、copy head），没系统结论。
  5. **Circuit 的组合性**：找到 induction head 和 IOI circuit，能预测它们组合起来的行为吗？目前只能 case-by-case 验证，没有组合代数。

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：我一开始把 induction head 写成"单个 attention head"——错了。它**至少是两个 head 协作**：previous token head（把前一个 token 信息写到当前位置）+ induction head（用这个信息做匹配）。重写时强制突出**2 层 circuit**结构。这是为什么 induction head 至少需要 2 层 transformer——单层做不到。
- **F3 术语翻译**：
  - "circuit" → 模型内部几个神经元 + 它们之间的连线，一起干一件具体的事（像大脑里"识别方向的细胞群"）。
  - "induction head" → 看到 [A][B]...[A] 就预测 [B] 的回路——它是 ICL（few-shot 学习）的物理基础。
  - "superposition" → 模型把 1000 个概念挤进 100 维空间，靠"几乎正交"勉强不混——代价是单个神经元表示多个概念。
  - "ablation" → 把某个神经元/head 置零，看模型哪个能力消失——是"它真的在做这件事"的金标准。
- **F4 回炉**：v1 把 circuits 描述成"已经被理解的领域"——读 Anthropic 2024 报告后改成"**小模型上有几个经典 circuit，但大模型上 circuit 概念本身可能失效**"。这是 v2 的诚实标注：superposition 在大模型上严重得多，"局部 circuit"假设可能不成立。

---

## 🔗 跨系列引用

- 上游：[`00-为什么AI是黑箱`](./00-为什么AI是黑箱.md) §3.3（mechanistic interpretability 总览）
- 上游：[`02-稀疏自编码器SAE`](./02-稀疏自编码器SAE.md)（SAE 找特征，circuits 找特征之间的连线）
- Transformer 架构基础：[`讲透Transformer`](../讲透Transformer/)（不懂 attention 做不了 circuits）
- ICL 的认知科学对应：[`cogsci/`](../cogsci/)（人类 few-shot 学习 vs induction head）
- 元理论：[`故事即世界迭代器-元理论.md`](../故事即世界迭代器-元理论.md) §断言 3（找 circuit = 把模型计算"翻译成人类故事"的迭代）
- 理论支柱：Transformer Circuits Thread（Olah 2020-至今）+ "In-context Learning and Induction Heads"（Olsson 2022）+ "Toy Models of Superposition"（Elhage 2022）
