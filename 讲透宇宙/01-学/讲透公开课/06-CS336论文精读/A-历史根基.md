# A · 历史根基与序列建模前史（10 篇）

> CS336 的"地基"——理解 Transformer 之前的世界为什么长那样。
> 对应讲座：**L1（tokenization）、L3（architectures）**

---

## A1. Shannon – Prediction and Entropy of Printed English (1950) ⭐⭐⭐

- **链接**：[princeton.edu/refs/shannon_51.pdf](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf)
- **作者**：Claude Shannon（信息论之父）

**核心问题**：英语文本有多"可预测"？能否量化语言的信息量？

**方法**：让人类猜下一个字母，统计猜对所需次数。提出**熵** $H$ 衡量每个字符的平均信息量。英语的熵约 **1.0-1.3 bits/字符**（远小于 $\log_2 26 \approx 4.7$），说明语言高度冗余。

**关键洞察**：语言建模的本质就是**预测下一个符号**——这个 1950 年的思想，到 2026 年的 GPT 仍是核心范式（next-token prediction）。Shannon 还给出了**交叉熵**的雏形：用模型分布 $q$ 近似真实分布 $p$ 时，$H(p,q) = H(p) + D_{KL}(p\|q)$，多出来的部分就是模型的"无知"。

**💡 工程经验**：
1. **困惑度 (perplexity) = $2^{H}$**——至今仍是预训练 loss 的标准报告方式。一个英文 LLM 的 PPL 若降到 ~3-4，意味着它"平均在 3-4 个词里犹豫"。
2. 训练 loss 不会降到 0——下界是英语本身的熵（不可压缩部分）。这解释了为什么 loss 曲线会"平台化"。
3. Shannon 用 n-gram 估算熵的方法，是今天所有 scaling law 实验（用小模型拟合 loss）的思想源头。

**📍 CS336 角色**：L1 开篇。Percy 用它讲"为什么 LM = 预测下一个 token"是 76 年前就定下的范式。

---

## A2. Hochreiter & Schmidhuber – Long Short-Term Memory (1997) ⭐⭐

- **链接**：[bioinf.jku.at/older/2604.pdf](https://www.bioinf.jku.at/publications/older/2604.pdf)

**核心问题**：vanilla RNN 训练时梯度会随时间步指数级消失/爆炸（**梯度消失问题**，Hochreiter 1991 自己先发现的），无法学习长距离依赖。

**方法**：引入 **cell state** $c_t$——一条贯穿时间、加法更新的"高速公路"。三个门控制信息流：
- 遗忘门 $f_t = \sigma(W_f[h_{t-1},x_t])$ 决定丢弃多少旧记忆
- 输入门 $i_t$ + 候选 $\tilde c_t$ 决定写入多少新信息
- 输出门 $o_t$ 决定输出多少

$c_t = f_t \odot c_{t-1} + i_t \odot \tilde c_t$，**梯度沿 $c_t$ 的路径是加法而非乘法**，所以不消失。

**💡 工程经验**：
1. LSTM 统治了 2014-2018 的 NLP（机器翻译、语音），但被 Transformer 取代——因为 **LSTM 必须串行**（$h_t$ 依赖 $h_{t-1}$），无法并行。
2. LSTM 的"门控"思想（gating）延续到今天：**SwiGLU 的 FFN 门控**、**MoE 的路由门控**都是这个思路的后代。
3. 理解 LSTM 的梯度流，才能理解 Transformer 为什么用**残差连接 + LayerNorm** 来解决同样的"深网络训练难"问题。

**📍 CS336 角色**：L3 架构讲座的"前 Transformer 时代"对照——讲清楚 RNN 的病，才知道 Transformer 解决了什么。

---

## A3. Bengio – A Neural Probabilistic Language Model (2003) ⭐⭐⭐

- **链接**：[jmlr.org/bengio03a.pdf](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf)
- **作者**：Yoshua Bengio（图灵奖）

**核心问题**：n-gram 模型的**维度灾难**——词表 V=10000 时，2-gram 就有 $10^8$ 种组合，大量未见过的组合概率被估为 0。

**方法**：用一个**前馈神经网络**取代查表。每个词映射为**分布式向量**（词嵌入的起源！），取最后 $n$ 个词的向量拼接，过 MLP + softmax 预测下一个词。**未见过的组合因为共享词向量而获得合理概率**（泛化）。

$$P(w_t | w_{t-n+1}...w_{t-1}) = \text{softmax}(W_2 \cdot \tanh(W_1 x + b_1))$$

**关键洞察**：这是**第一次把"学习"引入语言建模**，也是**词嵌入（word embedding）概念的诞生**——后来 word2vec (2013)、BERT、GPT 的 token embedding 全部源于此。

**💡 工程经验**：
1. **分布式表示** 是深度学习的根基——把离散符号映射成连续向量，让相似语义的词在向量空间靠近。今天 LLM 的 embedding matrix 就是这个思想的极致放大。
2. Bengio 论文里已经讨论了**计算瓶颈在 softmax**（词表大时归一化昂贵）——这个 2003 年的问题到 2026 年仍存在，催生了 hierarchical softmax、negative sampling、直到现在的 **Aux-Free / T-Free**（见 B 类）。
3. 论文训练用了 **GPU（当时还叫"显卡"）加速**——Bengio 是最早用 GPU 做深度学习的人之一，比 AlexNet 早了近 10 年。

**📍 CS336 角色**：L1/L3 的"神经语言模型"起点。理解了 NPLM，就知道 GPT 只是把"前馈网络"换成"Transformer"，把"看 n 个词"换成"看整个上下文"。

---

## A4. Brants et al. (Google) – Language Models in Machine Translation (2007) ⭐⭐

- **链接**：[aclanthology.org/D07-1090.pdf](https://aclanthology.org/D07-1090.pdf)

**核心问题**：机器翻译需要巨大语言模型，但 n-gram 在大规模数据上计算和存储都吃不消。

**方法**：Google 在 **2 万亿（2T）tokens** 上训练 5-gram 模型，用分布式 MapReduce。这是 2007 年——深度学习还没火，但 Google 已经在用"暴力堆数据"的思路。

**💡 工程经验**：
1. **"scale 就是一切"的最早工业证据**——2T tokens 的 n-gram 把翻译质量推到当时新高。今天 LLaMA-3 训 15T tokens，本质是同一条路的延续。
2. **数据规模 > 模型精巧**：这个结论在 2007（n-gram）和 2020（Scaling Laws）被反复验证。CS336 的 A3 作业（拟合 scaling law）就是在量化这个规律。
3. 论文第一作者是 **Thorsten Brants**，合作者有 **Jeffrey Dean**（Google MapReduce/BigTable 作者）——大模型训练从一开始就是"系统 + ML"的交叉学科。

**📍 CS336 角色**：L1 讲"数据规模"的历史背景，铺垫 L9-11 的 Scaling Laws。

---

## A5. Glorot & Bengio – Understanding the Difficulty of Training Deep FFNNs (2010) ⭐⭐

- **链接**：[proceedings.mlr.press/glorot10a.pdf](https://proceedings.mlr.press/v9/glorot10a/glorot10a.pdf)

**核心问题**：为什么深层网络难训？初始化如何影响训练？

**方法**：分析前向信号方差和反向梯度方差在各层的传播。提出 **Xavier 初始化**：让每层权重的方差 $\text{Var}(W) = \frac{2}{n_{in}+n_{out}}$，使前向/反向方差都不爆炸也不消失。

**💡 工程经验**：
1. **初始化极重要**——差的初始化让深层网络根本训不动。CS336 A1 手写 Transformer 时，学生必须正确初始化（通常用 Xavier 或 Kaiming），否则 loss 不降。
2. Xavier 适合 **tanh/sigmoid**（线性区对称）；ReLU 要用 **Kaiming/He 初始化**（$\text{Var}(W)=2/n_{in}$）。现代 LLM 的 embedding 和 linear 层大多用截断正态 + 缩放。
3. 这个分析框架（追踪各层方差）是调试"loss 不降"的标准手段——打印每层激活值的统计量（mean/std/min/max）。

**📍 CS336 角色**：L2 PyTorch 讲座 + A1 实现细节。

---

## A6. Duchi et al. – AdaGrad (2011) ⭐

- **链接**：[jmlr.org/duchi11a.pdf](https://www.jmlr.org/papers/volume12/duchi11a/duchi11a.pdf)

**核心**：第一个**自适应学习率**优化器。为每个参数维护历史梯度平方和 $G_t$，更新时除以 $\sqrt{G_t}$——**梯度大（频繁更新）的参数降学习率，梯度小的参数保持**。

**💡 工程经验**：
1. 稀疏特征（如 rare word 的 embedding）天然适合 AdaGrad——它们梯度出现少，AdaGrad 让它们获得更大有效步长。
2. **致命缺陷**：$G_t$ 单调递增，学习率会一直衰减到 0，后期完全停止学习 → 被 **RMSProp**（加衰减平均）和 **Adam** 取代。
3. Adam 的核心思想（自适应 lr）直接继承自 AdaGrad。

**📍 CS336 角色**：L2 优化器背景，Adam 的祖宗。

---

## A7. Sutskever et al. – Sequence to Sequence Learning (2014) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1409.3215](https://arxiv.org/pdf/1409.3215.pdf) · Google

**核心问题**：机器翻译输入输出长度不同，怎么建模？

**方法**：**编码器**（LSTM）把整个输入句子读成一个**固定长度的向量** $v$；**解码器**（另一个 LSTM）从 $v$ 逐词生成翻译。整句 → 一个向量 → 整句。

**关键结果**：在 WMT 英译法上首次接近 SOTA，且**反转输入句子**（让句尾靠近 decoder 起点）显著提升——因为 LSTM 记忆最近的输入更好。

**💡 工程经验**：
1. seq2seq 的"encoder-decoder"范式延续至今：**T5**、**BERT 的 [CLS]**、**T5 的 text-to-text** 都是这个范式。但 GPT 走了不同的路——**decoder-only**，统一理解和生成。
2. **"压缩成固定向量"是瓶颈**——长句子信息丢失严重。这直接催生了 Bahdanau Attention（下一篇），再催生 Transformer。
3. CS336 L3 讲架构时，seq2seq 是"为什么需要 attention"的故事起点。

**📍 CS336 角色**：L3 架构史。理解 encoder-decoder vs decoder-only 的分化，才能理解为什么 LLaMA 选 decoder-only。

---

## A8. Kingma & Ba – Adam (2014) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1412.6980](https://arxiv.org/pdf/1412.6980.pdf)

**核心**：结合 **Momentum**（指数移动平均梯度方向）+ **RMSProp**（指数移动平均梯度平方做自适应 lr）。

$$m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$$
$$\hat m_t = m_t/(1-\beta_1^t), \quad \hat v_t = v_t/(1-\beta_2^t) \quad \text{(bias correction)}$$
$$\theta_t = \theta_{t-1} - \eta \cdot \hat m_t / (\sqrt{\hat v_t} + \epsilon)$$

**💡 工程经验**：
1. **Adam 是 LLM 训练的事实标准**——CS336 A1 作业明确要求实现 AdamW。默认 $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$。
2. **bias correction 很关键**——初期 $m_t, v_t$ 从 0 开始，会严重低估，必须除以 $(1-\beta^t)$ 修正，否则前期学习率虚高、训练发散。
3. Adam 的 $\epsilon$ 不是越小越好——大 $\epsilon$（如 $10^{-6}$）能提升训练稳定性（特别是 fp16/bf16 训练）。LLaMA 用 $\epsilon=10^{-8}$。
4. **Adam ≠ AdamW**：原版 Adam 把权重衰减（L2 正则）加到梯度上，AdamW（2017）解耦了它（见 G2）——大模型训练**必须用 AdamW**，否则泛化变差。

**📍 CS336 角色**：L2 + A1。学生手写 AdamW 作为 A1 的第一个组件（`test_adamw.npz`）。

---

## A9. Bahdanau et al. – Neural Machine Translation by Jointly Learning to Align and Translate (2015) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1409.0473](https://arxiv.org/pdf/1409.0473.pdf)

**核心问题**：seq2seq 把整句压成一个向量，长句翻译质量崩塌。

**方法**：解码每个词时，让 decoder **"回头看" encoder 的所有隐状态**，学习一个**对齐权重** $\alpha_{ij}$（source 第 $i$ 个词对 target 第 $j$ 个词的重要性），加权求和得到**动态上下文向量** $c_j = \sum_i \alpha_{ij} h_i$。

$$\alpha_{ij} = \text{softmax}(\text{score}(h_i, s_{j-1})), \quad c_j = \sum_i \alpha_{ij} h_i$$

score 函数 Bahdanau 用的是 **additive**（小 MLP）；后来 Lucono 用 **dot-product**（更高效，Transformer 采用）。

**💡 工程经验**：
1. **这是"注意力机制"的诞生**——"让模型自己决定看哪里"的核心思想。Transformer 的 self-attention 是把它从"decoder 看 encoder"推广到"每个词看所有词"。
2. 注意力的**可解释性副产品**：$\alpha$ 权重可视化能展示模型"在看哪里"，至今是分析工具（如 BertViz）。
3. Bahdanau attention 证明了**软选择（soft attention，加权求和）比硬选择（hard attention，选一个）更易训练**——因为可微。

**📍 CS336 角色**：L3。讲 Transformer 之前的"注意力从哪来"。理解 additive vs dot-product，才能理解 Transformer 为什么选后者。

---

## A10. Sennrich et al. – Neural Machine Translation of Rare Words with Subword Units (2016) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1508.07909](https://arxiv.org/abs/1508.07909)

**核心问题**：词表大小固定时，rare word（出现次数少）学不好；扩大词表又让 softmax 计算爆炸。如何兼顾？

**方法**：**BPE (Byte Pair Encoding)**——原本是 1994 年的数据压缩算法。先初始化为字符级词表，然后**贪心地合并出现频率最高的相邻字符对**，直到词表达到目标大小。

```
初始: l o w </w> (4个字符)
合并 'l','o' → 'lo':  lo w </w>
合并 'lo','w' → 'low': low </w>
```

**关键结果**：rare word（如人名、拼错词、词形变化）被拆成已知子词片段，模型能处理**任何词**，包括训练时没见过的（OOV 问题基本解决）。

**💡 工程经验**：
1. **BPE 是所有现代 LLM 的 tokenizer 基础**——GPT-2/3、LLaMA、Mistral 全用 BPE 变体。CS336 **A1 作业的第一个组件就是手写 BPE**（`test_train_bpe_special_tokens.pkl`）。
2. **词表大小的 trade-off**：太小 → 序列变长（多 token）、训练慢；太大 → embedding 参数多、softmax 慢。GPT-2 用 50257，LLaMA-2 用 32000，LLaMA-3 扩到 128256（为多语言）。
3. BPE 的**已知缺陷**：①对拼写变体不鲁棒（"dog." 和 "dog" 是不同 token）；②数字切分不规律（"1234" 可能切成 "12"+"34"）；③多语言不均衡。这催生了 **SentencePiece**、**WordPiece**、以及 2024 年的 **T-Free / BLT**（见 B 类）。
4. **special tokens**（`<|endoftext|>` 等）必须加入 BPE 词表——A1 明确测试这个。

**📍 CS336 角色**：**L1 的核心 + A1 的第一个组件**。Percy 在 L1 深入讲 tokenization，因为它是 LM 的"第一道门"。

---

## A 类总结：从 1950 到 2016 的思想脉络

```
Shannon (1950): "语言 = 预测下一个符号" + 熵
   ↓ 50年
Bengio (2003): 用神经网络做预测 → 词嵌入诞生
   ↓
seq2seq (2014): encoder-decoder 压成向量
   ↓ 瓶颈
Bahdanau (2015): 别压成向量，让 decoder 动态看 → 注意力诞生
   ↓ 推广
Transformer (2017): 每个词看所有词 (B类)

平行线: Adam (2014) 让训练变稳 + BPE (2016) 解决词表
```

> **核心经验**：Transformer 不是凭空发明的，它是**把 Bahdanau attention 推到极致**（去掉 RNN，纯靠注意力）的结果。理解这条脉络，才能理解每个设计决策的"为什么"。
