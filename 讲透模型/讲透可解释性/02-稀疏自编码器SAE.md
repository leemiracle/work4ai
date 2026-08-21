# 02 · 稀疏自编码器（SAE）：把稠密激活拆成可解释特征

> 承接 [01-探针与表征几何](./01-探针与表征几何.md)。01 的探针有个根本限制：**只能测你预设的概念**——你问"第 8 层知不知道词性"，它说知道；但它永远不会主动告诉你"第 8 层里还有个' Arabic 数字 vs 罗马数字'的特征"。SAE 就是用来**发现新概念**的工具。
>
> 配套：[`讲透基础模型`](../讲透基础模型/) + [`03-Circuits与超级可解释性`](./03-Circuits与超级可解释性.md)

---

## 直觉层

### 一个具体时刻

> 2023 年 10 月，Anthropic 的 "Towards Monosemanticity" 论文挂出来。研究者让一个 SAE 在单层 transformer 的 MLP 输出上跑了一晚上，第二天早上一看——**字典里的第 1327 号特征对"阿拉伯数字"反应，第 4521 号对" DNA 序列"反应，第 712 号对"形容词比较级"反应**。每一个特征都对应一个**人类能命名**的语义概念。
>
> 这是 interpretability 史上第一次**用无监督方法从模型里挖出可解释概念**。研究者给它起名：**monosemantic feature**（单语义特征）。

**角色**：Anthropic 研究者。**冲突**：神经元 #42 同时编码"法国+首都+蓝色+..."（superposition 叠加），你没法指着单个神经元说"它在算什么"。**时刻**：字典学习跑完，第一个特征被命名的那一秒。

### SAE 要解决什么

00 章和 03 章都讲了 **superposition**：模型把 N 个概念挤进 d 维（d << N）的激活空间里——单个神经元是**多语义的**（polysemantic），同时参与多个概念。

```
神经元 #42 激活值 0.7
    这个 0.7 可能同时表示：
        "法国" 权重 0.3 + "首都" 权重 0.2 + "蓝色" 权重 0.15 + ...
```

**SAE 的赌注**：虽然单个神经元是 polysemantic 的，但**存在一个更大的稀疏特征空间**——每个特征是 monosemantic 的。SAE 就是把这个稀疏空间解出来。

### 直觉：SAE = 字典学习

把激活 $h$ 表示为**少量原子特征的加权和**：

$$h \approx \sum_{i=1}^{N_{\text{feat}}} c_i \cdot f_i, \quad c_i \in \mathbb{R}, \; f_i \in \mathbb{R}^d$$

其中绝大多数 $c_i = 0$（稀疏）。每个 $f_i$ 就是一个**可解释特征向量**，每个非零的 $c_i$ 是"这个特征被激活了多少"。

---

## 数学层

### SAE 的目标函数

SAE 是一个**单层 autoencoder**，由 encoder 和 decoder 组成：

$$\text{Encoder}: \; z = \sigma(W_{\text{enc}} h + b_{\text{enc}})$$
$$\text{Decoder}: \; \hat{h} = W_{\text{dec}} z + b_{\text{dec}}$$

其中 $z \in \mathbb{R}^{N_{\text{feat}}}$，$N_{\text{feat}} \gg d$（overcomplete，比如 $d=768$，$N_{\text{feat}}=4096$）。$\sigma$ 通常用 ReLU 或 TopK。

损失函数：

$$\mathcal{L}_{\text{SAE}} = \underbrace{\|h - \hat{h}\|_2^2}_{\text{重建损失}} + \lambda \underbrace{\|z\|_1}_{\text{L1 稀疏惩罚}}$$

- 重建损失：保证 SAE 没有丢失信息。
- L1 稀疏：强迫大部分 $z_i = 0$，只有少数特征被激活。
- $\lambda$ 是权衡系数（典型 $10^{-3}$ 到 $10^{-2}$）。

2024 年 OpenAI / Anthropic 倾向用 **TopK SAE**：直接强制只有 top-K 个 $z_i$ 非零（如 K=32），比 L1 更稳。

### Monosemanticity 的形式定义

一个特征 $f_i$ 是 monosemantic 的，当且仅当存在一个**可命名的语义概念 $c$**，使得：

$$\mathbb{P}(c \mid z_i > 0) \approx 1 \quad \text{且} \quad \mathbb{P}(z_i > 0 \mid c) \approx 1$$

即特征 $i$ 激活 ⟺ 概念 $c$ 出现。Anthropic 2023 在 toy model 上**经验性地观察到**很多特征接近这个标准，但**没有理论证明**。

### Toy model：叠加的几何

Anthropic 2022 的 toy model（"Toy Models of Superposition"）是 SAE 理论的支柱。给模型 $d=2$ 个隐藏维、$N=5$ 个稀疏特征，看模型怎么编码：

- 当特征稀疏时（每个特征出现概率 < 0.01），模型把 $N$ 个特征**几乎正交地**塞进 $d$ 维——叫 **superposition**。
- 当特征密集时，模型只保留 $d$ 个最重要特征，把其他"丢失"——叫 **feature dropout**。

形式上，最优编码是求解：

$$\min_W \mathbb{E}\left[\|x - W^\top W x\|^2\right] \quad \text{s.t. } x \text{ 稀疏}, W \in \mathbb{R}^{d \times N}$$

这个优化问题的解对应**几何上的对称结构**（如五边形、超立方体顶点）。这是 superposition 现象的**数学骨架**。

---

## 代码层

```python
import torch
import torch.nn as nn

class SparseAutoencoder(nn.Module):
    """单层 SAE，overcomplete + L1 稀疏"""
    def __init__(self, d_model: int, n_features: int, sparsity_lambda: float = 1e-3):
        super().__init__()
        self.encoder = nn.Linear(d_model, n_features)
        self.decoder = nn.Linear(n_features, d_model)
        # decoder 列向量归一化，避免特征模长作弊
        self.register_pre_forward_hook(self._normalize_decoder)
        self.lambda_sparsity = sparsity_lambda

    def _normalize_decoder(self, *args):
        with torch.no_grad():
            W = self.decoder.weight  # [d_model, n_features]
            W.div_(W.norm(dim=0, keepdim=True) + 1e-8)

    def forward(self, h):
        z = torch.relu(self.encoder(h))    # [batch, n_features]
        h_hat = self.decoder(z)
        recon_loss = (h - h_hat).pow(2).sum(dim=-1).mean()
        sparsity_loss = z.abs().sum(dim=-1).mean()
        return h_hat, recon_loss + self.lambda_sparsity * sparsity_loss, z

# 训练循环（简化）
def train_sae(sae, activations, epochs=10000, lr=1e-3):
    """activations: 从真实模型某层收集的 [N_samples, d_model]"""
    opt = torch.optim.Adam(sae.parameters(), lr=lr)
    for step in range(epochs):
        batch = activations[torch.randint(0, len(activations), (4096,))]
        _, loss, z = sae(batch)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 1000 == 0:
            # 稀疏度：平均每个样本激活多少特征
            sparsity = (z > 0).float().mean(dim=-1).mean().item()
            print(f"step {step}: loss={loss.item():.4f}, avg_active={sparsity:.1f}/{z.shape[-1]}")
    return sae

# TopK SAE 变体（2024 主流）
class TopKSAE(nn.Module):
    def __init__(self, d_model, n_features, k=32):
        super().__init__()
        self.encoder = nn.Linear(d_model, n_features)
        self.decoder = nn.Linear(n_features, d_model)
        self.k = k

    def forward(self, h):
        z_pre = self.encoder(h)
        # 只保留 top-K 个最大激活，其他置零
        topk_vals, topk_idx = torch.topk(z_pre, self.k, dim=-1)
        z = torch.zeros_like(z_pre).scatter_(-1, topk_idx, torch.relu(topk_vals))
        h_hat = self.decoder(z)
        return h_hat, (h - h_hat).pow(2).sum(-1).mean(), z

# 特征命名（需要外部人类标注或自动解释，Anthropic 2024 的方法）
def label_feature(sae, feature_idx: int, probe_prompts: list):
    """对 feature_idx 找出最激活它的 prompts，让人类或 LLM 命名它"""
    activations = []
    for p in probe_prompts:
        h = model.get_activation(p)
        _, _, z = sae(h.unsqueeze(0))
        activations.append(z[0, feature_idx].item())
    top_prompts = sorted(zip(probe_prompts, activations), key=lambda x: -x[1])[:20]
    # 把 top_prompts 喂给 LLM，让它总结"这些 prompt 共同提到的是什么概念"
    return llm_summarize(top_prompts)  # 伪代码
```

**反直觉数字**：Anthropic 2024 在 Claude 3 Sonnet 上训的 SAE 找到了**上千万个 monosemantic 特征**——包括"背叛"、"萨特"、"金鱼"、"代码 bug"等高阶抽象概念。但相对 Claude 的几百亿参数，仍是冰山一角。

---

## 不足层

- **已证明**：
  - **Toy model 的 superposition 几何**（Elhage 2022）：在 toy setting 下严格证明了稀疏→叠加的几何结构（对称多边形/超立方体）。
  - **SAE 重建损失可优化**：标准字典学习的收敛性已知。

- **经验**：
  - **Scaling monosemanticity**（Anthropic 2023-2024）：在 toy model → small transformer → Claude 3 Sonnet 上，**SAE 都能找到可命名的特征**，且特征数随模型规模超线性增长。
  - **Steering 实验成立**（Templeton 2024）：人工激活"金鱼"特征，模型回答里强制出现金鱼——**部分**证明特征是因果的。

- **未解**（SAE 当前最大问题）：
  1. **字典学习没有理论保证**：SAE 找到的特征是否对应模型**真正使用**的概念？还是 SAE 自己造的解释？这就是 **interpretability illusion**。Bricken 2023 用"消融实验"部分反驳——消融某特征后对应能力下降——但不完备。
  2. **特征空间的完整性**：SAE 找到 1000 万个特征，覆盖模型能力多少？没人测过。可能是 1%，可能是 50%。
  3. **死特征问题**：训练中很多特征从不激活（"死特征"），无法解释。TopK 部分缓解，但没根治。
  4. **scaling 到 GPT-4 / Claude 3 Opus 级别未完成**：算力需求和调参难度巨大。

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：我一开始把 SAE 写成"降维工具"——错了。SAE 是 **overcomplete + 稀疏**，特征维度 $N_{\text{feat}} \gg d_{\text{model}}$，是**升维**但**稀疏化**。重写时强制突出 $N_{\text{feat}} / d$ 比例（典型 4-16 倍）。
- **F3 术语翻译**：
  - "superposition" → 模型把 100 个概念塞进 10 维空间，靠"几乎不重叠"勉强存下——像把 100 本书立着塞进窄书架。
  - "monosemantic" → 一个特征只表示一个意思（不像神经元 #42 表示 5 个意思）。
  - "overcomplete dictionary" → 字典比词还多——故意让 SAE 多备很多"概念槽位"，逼稀疏。
- **F4 回炉**：v1 把"SAE 能找到所有概念"作为结论——读了 Bricken 2023 和 interpretability illusion 争论后，改成"**SAE 找到的特征需要消融实验交叉验证**，否则可能是 SAE 自造的解释"。这是 v2 的硬限定。

---

## 🔗 跨系列引用

- 上游：[`01-探针与表征几何`](./01-探针与表征几何.md)（probing 是有监督找预设概念，SAE 是无监督找新概念）
- 下游：[`03-Circuits与超级可解释性`](./03-Circuits与超级可解释性.md)（SAE 找特征，circuits 找特征之间的连线）
- 元理论：[`故事即世界迭代器-元理论.md`](../故事即世界迭代器-元理论.md) §断言 3（SAE = 把稠密表征分解成可命名故事的迭代器）
- 理论支柱：Anthropic "Toy Models of Superposition"（Elhage 2022）+ "Towards Monosemanticity"（Bricken 2023）+ "Scaling Monosemanticity"（Templeton 2024）
- 模型架构基础：[`讲透基础模型`](../讲透基础模型/)（理解 MLP 才能理解为什么 SAE 接在 MLP 输出上）
