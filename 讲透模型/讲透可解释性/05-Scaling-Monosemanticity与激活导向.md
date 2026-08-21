# 05 · Scaling Monosemanticity 与激活导向：在大模型里"开车"

> 承接 [04-Attribution与梯度方法](./04-Attribution与梯度方法.md)。04 解释了为什么 attribution（输入归因）这条路在大模型上越走越窄——单步梯度对深非线性几乎没判别力。本章是 mechanistic 路线对它的"超越答复"：**别再问输入哪部分重要，直接进模型内部，找到具体的概念特征，然后人为调它**。这就是 2024 年 Anthropic 的 Scaling Monosemanticity 和 steering vectors 给出的工程答案。
>
> 配套：[`02-稀疏自编码器SAE`](./02-稀疏自编码器SAE.md) + [`03-Circuits与超级可解释性`](./03-Circuits与超级可解释性.md)

---

## 直觉层

### 一个具体时刻

> 2024 年 5 月 21 日，Anthropic 的 Transformers Circuits Thread 团队把 Scaling Monosemanticity 挂出来。Templeton 团队做了一件之前没人做成的事——**在 Claude 3 Sonnet（一个生产级大模型）的中间层训了一个有十亿维字典的 sparse autoencoder**。
>
> 他们找到的特征让人头皮发麻：有"金鱼"特征，有"背叛"特征，有" bugs in code"特征，有"萨特"特征——甚至有**"德克萨斯州奥斯汀市"这种地理概念**，还有**"安全隐患 / 欺骗"这种抽象特征**。更关键的是：人为把"金鱼"特征乘个系数往残差里加，模型回答就**强制带金鱼**。人为抑制"背叛"特征，模型就**真的不写背叛了**。
>
> 这就是 steering vector（激活导向向量）。第一次，我们能在生产级 LLM 内部"开车"——不只是解释，而是**因果地操纵**。

**角色**：Templeton（Anthropic 研究者）。**冲突**：02 章的 SAE 之前只在 toy model 和小模型上成立——能不能 scale 到 Claude 3 这种几百亿参数的模型，没人敢打包票；很多研究者赌它不能。**时刻**：第一个十亿维 SAE 收敛、抽出"背叛"特征并能 steering 它的那一秒。

### Scaling SAE 把什么验证了

02 章的核心赌注：**monosemanticity 不只是小模型现象**。Templeton 2024 给了三档证据：

1. **字典能 scale**：把 $N_{\text{feat}}$ 从 100 万加到 10 亿，loss 还在降——没到瓶颈。
2. **特征数随模型规模超线性增长**：模型翻倍，可命名特征数远不止翻倍。
3. **steering 真的成立**：人为放大某特征 → 输出被因果地改变。

第 3 条是质变——它把 SAE 从"描述性工具"升级成"控制工具"。

### Steering Vector 的直觉

不再训新模型，也不改权重——**在推理时把一个向量加进残差流**，模型回答就被引导。形式上：

$$h^{(L)}_{\text{steered}} = h^{(L)} + \alpha \cdot v_{\text{feature}}$$

其中 $v_{\text{feature}}$ 通常就是 SAE decoder 的某一列（即某个特征的方向），$\alpha$ 是强度系数。这是**机制可解释性的第一个实际应用**。

---

## 数学层

### SAE Scaling Loss

02 章的标准 SAE 损失：

$$\mathcal{L}_{\text{SAE}} = \|h - \hat{h}\|_2^2 + \lambda \|z\|_1$$

Templeton 2024 在 Claude 3 Sonnet 上观察到：当 $N_{\text{feat}}$ 增大，**reconstruction loss 的下降与 $N_{\text{feat}}$ 近似成幂律**：

$$\mathcal{L}_{\text{recon}}(N_{\text{feat}}) \approx A \cdot N_{\text{feat}}^{-\beta}, \quad \beta \approx 0.2 \text{ to } 0.4$$

且没有"特征饱和"的拐点。**这说明模型内部的可解释概念密度比想象中高得多**——继续 scale 还能找到更多。

### Steering Vector 的几何操作

设 SAE decoder 的第 $i$ 列为 $W_{\text{dec}}[:, i] \in \mathbb{R}^d$（即特征 $i$ 在残差空间的方向）。给定一个 token 位置 $t$ 的残差激活 $h^{(L)}_t$：

$$h^{(L), \text{steered}}_t = h^{(L)}_t + \alpha \cdot W_{\text{dec}}[:, i]$$

更稳的版本是**clamp**——直接强制 $z_i = c$：

$$z_i^{\text{clamped}} = c, \quad \text{其他 } z_j \text{ 不变}$$

$$\hat{h}^{\text{steered}} = W_{\text{dec}} z^{\text{clamped}} + b_{\text{dec}}$$

clamp 比 additive 稳的原因是它直接在 SAE 特征空间操作，不与正交方向混叠。

### Multi-feature Steering

当同时操纵多个特征，合成方向是它们的**和**（前提是近似正交）：

$$v_{\text{combo}} = \sum_{i \in S} \alpha_i \cdot W_{\text{dec}}[:, i]$$

Anthropic 2024 的"persona"实验就是这么构造的——把"诚实"、"金鱼"、"代码 bug"三个特征按不同权重组合，得到不同人格的输出。

---

## 代码层

```python
import torch
import torch.nn as nn
from transformer_lens import HookedTransformer

model = HookedTransformer.from_pretrained("gpt2-small")  # 演示用小模型；真实验用 Claude 3 Sonnet 的内部 checkpoint

# === 1. Steering：往残差流加方向向量 ===
def make_steering_hook(feature_vec: torch.Tensor, layer: int, alpha: float = 10.0):
    """返回一个 forward hook：在第 layer 层残差上加 alpha * feature_vec"""
    def hook(resid, hook):
        # resid: [batch, seq, d_model]，对所有 token 加同一个向量
        resid[:, :, :] = resid + alpha * feature_vec.to(resid.device)
        return resid
    return hook

# 假设我们已经从一个 SAE 拿到了 "金鱼" 特征方向
goldfish_feature_vec = torch.randn(model.cfg.d_model)   # 实际：sae.W_dec[feature_idx]

prompt = "Once upon a time there was"
with model.hooks(fwd_hooks=[("blocks.6.hook_resid_post",
                              make_steering_hook(goldfish_feature_vec, 6, alpha=15.0))]):
    out = model.generate(prompt, max_new_tokens=40)
print(out)   # 故事会强制出现金鱼 / 鱼 / 水 等元素

# === 2. Clamp 模式：通过 SAE 强制某特征值 ===
sae = ...  # 假设已加载训好的 SAE（W_enc: [n_feat, d_model], W_dec: [d_model, n_feat]）
def clamp_feature_hook(resid, hook, sae, target_feat: int, target_val: float = 20.0):
    # 1) encode → 2) 强制 z[target_feat] = target_val → 3) decode → 4) 替换 resid
    z = torch.relu(sae.encoder(resid))                  # [batch, seq, n_feat]
    z[:, :, target_feat] = target_val
    resid_modified = sae.decoder(z)
    return resid_modified

# === 3. Inference-time 参数：alpha 的取值很重要 ===
# 经验（Anthropic 2024）：alpha 太小（<1×）几乎没效果；太大（>50×）模型崩。
# 建议从 5× 开始 sweep，监控 KL(prompted_output || steered_output) < 0.3。
```

**反直觉数字**：Anthropic 2024 报告——**单个特征 clamp 后**，模型输出在该概念上的概率密度可以从 base rate 的 ~0.1% 飙到 30%+，但**整体 perplexity 几乎不动**。也就是说，steering 是"高精度但低扰动"的——这是它能进生产的关键性质。

---

## 不足层

- **已证明**：
  - SAE 在 Claude 3 Sonnet 上找到了**数千万到数十亿**可命名特征（Templeton 2024）。
  - Steering vectors 因果改变模型行为（同上，对照实验 + KL 监控）。
  - 在 SAE 字典维度上的幂律曲线**没有饱和拐点**——继续 scale 还能找到更多特征。

- **经验**：
  - **steering 不普适**：低阶概念（"金鱼"）steering 成功率高；高阶抽象概念（"诚实"、"诚实人格"）效果不稳，需要组合多个特征。
  - **clamped 特征会"漂"**：长 prompt 里 clamp 一个特征，模型有时会**绕过**它（其他特征代偿）——这是 deceptive alignment 的潜在通道。
  - **跨语言 / 跨模态一致**：金鱼特征在英文 / 中文 / 法文 prompt 上都触发，部分印证 universal feature 假设。

- **未解**：
  1. **特征空间覆盖率**：SAE 找到 10 亿特征，占模型"全部概念"多少？无人测过。可能 1%，可能 50%——这是 SAE 路线最大未知数。
  2. **steering 的可预测性**：clamp 强度 $\alpha$ 与输出概率变化之间没有解析关系——纯经验调参。
  3. **steering 与对齐鲁棒性**：bad actor 也可以用 steering 强行触发"背叛 / 欺骗"特征——interp 工具是双刃的。
  4. **interpretability illusion 在 scale 上更严重**：大模型 SAE 找到的特征，有多少是模型真正用的、有多少是 SAE 自造的？消融实验只能部分回答。

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：第一稿把 steering 写成"改模型权重"——错。steering 是**推理时**在残差流加向量，权重冻结。改权重是 ROME（[01 章](./01-探针与表征几何.md)），改激活是 steering——两个完全不同的层。
- **F3 术语翻译**：
  - "scaling monosemanticity" → 把 SAE 字典越扩越大，看"可命名特征"是否随模型规模继续涨——Anthropic 2024 在 Claude 3 上验证了。
  - "steering vector" → 在模型中间层激活里加一个方向，模型输出就被因果地引导——加"金鱼"特征就强制写金鱼。
  - "clamp" → 直接把某 SAE 特征值设为常数（不是加偏置），比 additive 更稳，因为它在 SAE 空间操作不混叠。
- **F4 回炉**：v1 把 steering 写成"已成熟技术"——读了 Templeton 后续 report 后改成"**对小概念稳，对高阶抽象概念不稳，且可被恶意使用**"。补上"长 prompt 里会漂"这个反模式。

---

## 🔗 跨系列引用

- 上游：[`02-稀疏自编码器SAE`](./02-稀疏自编码器SAE.md)（SAE 是 steering 的前提）
- 上游：[`03-Circuits与超级可解释性`](./03-Circuits与超级可解释性.md)（找到 circuit 才知道往哪个位置加向量）
- 对照：[`01-探针与表征几何`](./01-探针与表征几何.md)（ROME 改权重 vs steering 改激活——两种知识编辑）
- 下游：[`06-应用安全审计与幻觉debug`](./06-应用安全审计与幻觉debug.md)（steering 直接用于"消除欺骗倾向"和"幻觉 debug"）
- 理论支柱：Templeton et al. 2024 "Scaling Monosemanticity" + Subramanian et al. 2024 "Steering Llama 2 via Contrastive Activation Addition"
