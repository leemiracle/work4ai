# 04 · Attribution 与梯度方法：被自己打脸的"看图说话"

> 承接 [03-Circuits与超级可解释性](./03-Circuits与超级可解释性.md)。03 走的是 mechanistic 路线（找内部 circuit），本章补全 00 章里的第二条路径——**attribution**（归因）：给一个输入 $x$ 和模型输出 $y$，问"输入的哪一部分让模型给出了 $y$"。看起来最朴素、工程上用得最广（SHAP 出现在每一个风控团队里），但也是**被自己打脸最狠**的一条路。
>
> 配套：[`00-为什么AI是黑箱`](./00-为什么AI是黑箱.md) §3.2 + [`讲透Transformer`](../讲透Transformer/)

---

## 直觉层

### 一个具体时刻

> 2017 年 NeurIPS，MIT 的 Adebayo 拿着海报走进会场。海报标题像一记耳光：**"Sanity Checks for Saliency Maps"**。他做了三件让全场安静下来的事：
>
> 1. 把模型的**最后一层权重随机化**——saliency map 几乎不变。
> 2. 把**上面几层全随机化**——saliency map 还是不变。
> 3. 把**整个模型换成另一个数据**训出来的——saliency map 看上去**还是那张热力图**。
>
> 结论只有一句：**你看到的"模型在关注眼睛和鼻子"那张图，跟模型实际在算什么可能根本没关系**。那张图很大一部分来自输入图像本身的边缘结构，不是模型学到的判别依据。

**角色**：Adebayo（MIT 博士生）。**冲突**：2013 Simonyan 提出 saliency map 以来，整个 CV 社区把它当作"模型在想什么"的窗口——医疗影像、自动驾驶、法律举证都在用。**时刻**：cascading randomization 那张图出来的瞬间，整个 saliency 子领域被宣判"你的主要证据无效"。

### Attribution 在问什么

设模型 $f: \mathbb{R}^d \to \mathbb{R}$，输入 $x$，输出 $f(x)$。Attribution 方法返回一个**和输入同形状**的得分 $\phi(x) \in \mathbb{R}^d$，要求：

- $\phi_i(x)$ 大 → 第 $i$ 维（像素 / token）"对 $f(x)$ 贡献大"。
- $\sum_i \phi_i(x) \approx f(x) - f(\text{baseline})$（完整性约束）。

直觉很简单：**对输入求梯度，梯度大的地方就是模型敏感的地方**。Saliency 就是 $\phi(x) = \nabla_x f(x)$ 的逐元素符号化。SHAP / IG 都是这个思想的精修版。

### 三代方法

| 代 | 代表 | 核心 |
|---|---|---|
| 1 · Saliency（2013）| Simonyan | $\|\nabla_x f\|$ |
| 2 · Integrated Gradients（2017）| Sundararajan | 沿路径积分梯度，满足完整性 |
| 3 · SHAP（2017）| Lundberg | 博弈论 Shapley 值的唯一化 |

工程上 SHAP 几乎是工业默认——但它**不解决**下面 Adebayo 揭示的问题，只是满足了一组公理。

---

## 数学层

### Integrated Gradients 公式

给定 baseline $x_0$（图像常用黑图，文本用 zero embedding），IG 对第 $i$ 维定义为：

$$\text{IG}_i(x) = (x_i - x_{0,i}) \cdot \int_0^1 \frac{\partial f(x_0 + \alpha (x - x_0))}{\partial x_i}\Big|_{x_0 + \alpha(x-x_0)} \, d\alpha$$

数值实现取 $m$ 步黎曼和：

$$\text{IG}_i(x) \approx \frac{x_i - x_{0,i}}{m} \sum_{k=1}^{m} \frac{\partial f(x_0 + \tfrac{k}{m}(x - x_0))}{\partial x_i}$$

**完整性公理**（Completeness）：

$$\sum_i \text{IG}_i(x) = f(x) - f(x_0)$$

这是 IG 相对 Saliency 的最大卖点——归因能"对得上账"。

### SHAP 的 Shapley 值

把每一维当博弈论里的"玩家"，模型输出增量当"联盟价值"，SHAP 用 Shapley 公式给每个玩家分一个**唯一**的归因：

$$\phi_i^{\text{SHAP}} = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|! (|N|-|S|-1)!}{|N|!} \left[ f(S \cup \{i\}) - f(S) \right]$$

唯一性来自 Shapley 的四条公理（效率 / 对称 / 虚拟 / 可加）。**但**：精确计算是 NP-hard，所有"快 SHAP"都是近似，且对 baseline 选择极其敏感。

### Sanity Check 的形式化

Adebayo 2017 的**cascading randomization**：从顶到底逐层把权重 $W^{(L)}, W^{(L-1)}, \dots$ 替换为随机矩阵 $\tilde W$，比较 attribution 的相似度：

$$\text{sim}(\phi(x; W), \phi(x; \tilde W)) = \text{Spearman}\big(\phi(x; W), \phi(x; \tilde W)\big)$$

**期望**：随机化后归因应该剧烈变化（因为模型计算完全变了）。**实测**：对 Vanilla Saliency / Grad-CAM 的多数配置，sim 持续保持高位——说明这些方法**与模型参数弱相关**。

---

## 代码层

```python
import torch
import torch.nn as nn
from captum.attr import IntegratedGradients, Saliency, GradientShap

# 一个文本分类器： embedding → mean pool → linear
class TinyClassifier(nn.Module):
    def __init__(self, vocab, d=32, n_classes=2):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.cls = nn.Linear(d, n_classes)
    def forward(self, ids):
        return self.cls(self.emb(ids).mean(dim=1))  # [B, n_classes]

model = TinyClassifier(vocab=1000)
ids = torch.tensor([[1, 5, 9, 12, 3]])          # 输入 token 序列
target = torch.tensor([1])                       # 想解释的类别

# === Saliency：最朴素的梯度归因 ===
sal = Saliency(model)
attr_sal = sal.attribute(ids, target=target)     # [1, seq_len]

# === Integrated Gradients：满足完整性 ===
ig = IntegratedGradients(model)
baseline = torch.zeros_like(ids)                  # zero embedding baseline
attr_ig = ig.attribute(ids, target=target, baselines=baseline, n_steps=64)

# === Sanity Check: cascading randomization（Adebayo 2017）===
def cascade_randomize(model, top_to_bottom=True):
    """逐层随机化权重，看 attribution 是否变"""
    layers = list(model.modules())
    if top_to_bottom:
        layers = layers[::-1]
    sims = []
    phi_ref = attr_ig.clone()
    for mod in layers:
        if hasattr(mod, "weight") and mod.weight is not None:
            with torch.no_grad():
                mod.weight.copy_(torch.randn_like(mod.weight) * mod.weight.std())
            phi_new = ig.attribute(ids, target=target, baselines=baseline, n_steps=64)
            # Spearman 相关：相似度
            sims.append(torch.corrcoef(torch.stack([phi_ref.flatten(), phi_new.flatten()]))[0, 1].item())
    return sims   # 期望急剧下降；若保持高位 = sanity check 失败
```

**反直觉数字**：Adebayo 论文 Table 1 报告：在 ImageNet 上，Grad-CAM 在权重随机化后与原图 attribution 的 Spearman 相关常保持 **0.4-0.7**；理论期望是接近 0。**也就是说，你看到的"热力图"里至少有一半信息与模型无关**。

---

## 不足层

- **已证明**：
  - IG 满足完整性与实现不变性（Sundararajan 2017 定理）。
  - SHAP 是同时满足 Shapley 四公理的**唯一**归因（Lundberg 2017）。

- **经验**：
  - **Sanity Check 失败**（Adebayo 2017）：vanilla Saliency、Guided Backprop、Grad-CAM 在 cascading randomization 下归因变化远小于预期。**这意味着它们更接近"输入边缘检测器"而非"模型决策依据"**。
  - **Input × Gradient 现象**：很多 saliency 热力图其实等于"原图 × 边缘梯度"——换任何模型看上去都差不多。
  - IG + 平滑（SmoothGrad）能通过 sanity check，但代价是 50-100× 算力。

- **未解**：
  1. **"正确的归因"如何定义**？SHAP 满足一组公理但仍是 baseline-dependent；不存在 baseline-invariant 唯一归因（Lundberg 自己承认）。
  2. **Attribution 与因果的关系**：高归因不代表"删掉就坏"，因为模型可能在非线性边界附近。Sundararajan 自己也没给出归因与 ablation 一致的保证。
  3. **大模型上 attribution 退化**：LLM 是 autoregressive、多层、深度非线性——单步梯度对长 prompt 几乎没有判别力。
  4. **被滥用作"举证"**：医疗、法律场景把 SHAP 当成"AI 透明度证据"——sanity check 已证明这种用法**建立在错误前提上**。

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：第一稿把 IG 写成"更稳定的梯度"——错。IG 不是"稳定"，而是**满足完整性公理**（$\sum \phi_i = f(x) - f(x_0)$）。稳定性是 SmoothGrad 加的，不是 IG 本身的卖点。
- **F3 术语翻译**：
  - "saliency map" → 对输入像素求梯度染的热力图——好看，但和模型实际在想什么可能无关。
  - "Integrated Gradients" → 从空白图到真图沿直线走，把沿途每一步的梯度加起来——保证"加起来等于模型输出的变化"。
  - "Sanity Check" → Adebayo 2017 的体检：把模型权重随机化，归因该剧烈变化；不变 → 说明归因没在测模型。
- **F4 回炉**：v1 默认把 attribution 当"模型解释的事实标准"——读了 Adebayo 之后改成"**attribution 是必要但不充分的诊断，必须与 ablation 交叉验证**"。整章的核心反模式就是"信 attribution 而不做 sanity check"。

---

## 🔗 跨系列引用

- 上游：[`00-为什么AI是黑箱`](./00-为什么AI是黑箱.md) §3.2（attribution 三条路径之一）
- 对照：[`01-探针与表征几何`](./01-探针与表征几何.md)（probing 测"模型知道什么"，attribution 测"输入哪部分被用"——都偏弱）
- 下游：[`05-Scaling-Monosemanticity与激活导向`](./05-Scaling-Monosemanticity与激活导向.md)（mechanistic 路线绕过 attribution 的根本限制）
- 工业陷阱：[`06-应用安全审计与幻觉debug`](./06-应用安全审计与幻觉debug.md)（为什么不能拿 SHAP 当监管证据）
- 理论支柱：Adebayo et al. 2018 "Sanity Checks for Saliency Maps" + Sundararajan et al. 2017 "Axiomatic Attribution for Deep Networks" + Lundberg & Lee 2017 "A Unified Approach to Interpreting Model Predictions"
