# 13 — RNN 与 LSTM：attention 之前的序列建模王者

> 「讲透NLP」第十三篇。在 Transformer 统治天下之前，处理"变长序列"（一句话、一段语音、一时间序列）的主力是 **RNN（循环神经网络）**，以及治好它梯度病的大功臣 **LSTM**。这一篇讲透三件事：RNN 怎么用"隐状态"记忆历史、为什么它的梯度会消失/爆炸、LSTM 的门控如何用"加法更新"破解这个顽疾。
>
> 对应 SLP3 第 7 章（Recurrent Neural Networks）。配套实验：`experiments/13_rnn_lm.py`。

---

## 0. 为什么 2026 年还要学 RNN

Transformer 出来后（2017），RNN 在 NLP 主战场几乎被淘汰。但有三条理由你仍需懂它：

1. **它是理解"序列"的最简模型**——只用一个隐状态向量就把"任意长的历史"压缩进来。这个思想是 attention 的前置（attention 是"别压缩，全保留，加权取"）。
2. **梯度消失/爆炸**是深度学习的核心病理——RNN 把这个问题暴露得最尖锐，LSTM 的解法（门控 + 加法残差）是现代架构（包括 Transformer 的残差连接、GRU、Mamba 的选择性状态）的共同祖先。
3. **它仍在边缘场景活跃**——实时语音识别、设备端小模型、时序预测，RNN/LSTM 因"推理恒定内存"仍优于 Transformer。

> 🎯 **核心叙事**：RNN 的故事是一个"压缩信息 → 压缩过头 → 用门控抢救"的三幕剧。读完你能理解为什么 Transformer 的"不压缩、全 attention"是它的自然下一站。

---

## 1. 直觉层：用一个"隐状态"记全部历史

**问题**：怎么让网络处理变长输入 $x_1, x_2, \dots, x_T$（比如一句话的 T 个词）？前馈网络固定输入长度，搞不定。

**RNN 的回答**：维护一个固定大小的**隐状态**向量 $h_t$，每一步把它和当前输入融合，更新成新隐状态。这样无论序列多长，"记忆"始终是一个向量。

```
x_1 ──┐   x_2 ──┐        x_T ──┐
      ▼         ▼              ▼
   ┌─────┐  ┌─────┐   ...   ┌─────┐
h_0│RNN  │→│RNN  │→  ...  →│RNN  │→ h_T
   └─────┘  └─────┘         └─────┘
      ↓         ↓              ↓
     y_1       y_2            y_T
```

**类比**：RNN 像一个边读边记的读者——每读一个词，脑里的"理解状态"更新一次；读完整个句子，$h_T$ 就是他对整句的压缩记忆。隐状态是**所有历史的有损压缩**。

---

## 2. 数学层：RNN 的递推与 BPTT

### 2.1 RNN cell（一个时间步）

$$\boxed{\;h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h)\;}$$
$$y_t = \mathrm{softmax}(W_{hy} h_t + b_y)$$

- $h_t \in \mathbb{R}^H$：时刻 $t$ 的隐状态
- $x_t \in \mathbb{R}^V$：时刻 $t$ 的输入（如 one-hot 词向量）
- $W_{hh} \in \mathbb{R}^{H \times H}$：**隐状态自循环权重**（最关键，梯度病的源头）
- $W_{xh}, W_{hy}$：输入/输出权重

**三个权重矩阵 + 一个 tanh**，就是整个 RNN cell。所有时间步**共享同一组参数**（这是"循环"的本质——同一个函数反复应用）。

### 2.2 BPTT：沿时间反向传播

RNN 的损失是所有时间步损失之和：$L = \sum_{t=1}^{T} \ell(y_t, \hat{y}_t)$。

要更新 $W_{hh}$，得对它求梯度。链式法则**沿时间展开**（Back-Propagation Through Time, BPTT）：

$$\frac{\partial L}{\partial W_{hh}} = \sum_{t=1}^{T} \frac{\partial \ell_t}{\partial h_t} \cdot \frac{\partial h_t}{\partial W_{hh}}$$

关键项是 $\frac{\partial h_T}{\partial h_0}$——从序列末尾一路传到开头。对 $h_t = \tanh(W_{hh} h_{t-1} + \dots)$ 反复用链式法则：

$$\frac{\partial h_T}{\partial h_0} = \prod_{t=1}^{T} \underbrace{\mathrm{diag}(1 - h_t^2)}_{\tanh' \in [0,1]} \cdot W_{hh}$$

**这是 T 个矩阵的连乘**。问题就在这里——见下一节。

---

## 3. RNN 的核心病：梯度消失/爆炸

### 3.1 数学病因

连乘 $\prod_{t=1}^{T} D_t W_{hh}$（其中 $D_t = \mathrm{diag}(1-h_t^2)$），其范数大致按 $(\rho \cdot \bar{d})^T$ 缩放，其中 $\rho$ 是 $W_{hh}$ 的**谱半径**（最大特征值绝对值），$\bar{d} \in [0,1]$ 是 tanh 导数的平均。

- $\rho < 1$：$(\rho\bar{d})^T \to 0$（梯度**消失**，长程依赖学不到）
- $\rho > 1$：$(\rho\bar{d})^T \to \infty$（梯度**爆炸**，训练发散）

tanh 的导数 $\in [0,1]$ 让"消失"更严重——即使 $\rho \approx 1$，连乘 T 次也会衰减。

### 3.2 实验铁证（Part A）

实测三种 $W_{hh}$ 初始化下，$\|\partial h_{25}/\partial h_0\|$ 的轨迹（$T=25$ 步）：

| 初始化 | $W_{hh}$ 谱半径 | $\|\partial h_{25}/\partial h_0\|$ | 诊断 |
|---|:---:|:---:|---|
| 小权重 ×0.3 | 0.83 | **1.0e-2**（从 2.8 衰减 280 倍）| 🟡 梯度消失 |
| 临界 ×0.9 | 2.50 | **3.1e+2**（爆炸 100 倍）| 🟠 勉强（靠裁剪）|
| 大权重 ×1.5 | 5.33 | **2.1e-27**（彻底坍塌）| 🔴 严重消失/数值病 |

> 🤯 **反直觉**：③ 大权重反而比①小权重消失得更狠（1e-27 vs 1e-2）！因为大权重让 $h_t$ 迅速饱和到 ±1，tanh 导数 $1-h_t^2$ 趋近 0，雅可比几乎归零——**权重太大导致激活饱和，饱和又把梯度压死**。这是 RNN 训练最阴险的坑。

**结论**：普通 RNN 在 $T > 20$ 的序列上几乎学不到长程依赖。这就是 LSTM 登场的契机。

---

## 4. LSTM：用"门控 + 加法残差"治梯度病

Hochreiter & Schmidhuber (1997) 的洞察：**梯度消失的根因是 $h_t$ 用乘法+非线性反复变换**。如果能给梯度一条"线性高速公路"，它就能不衰减地回流。

### 4.1 LSTM cell 的四个组件

LSTM 引入一个**细胞状态** $c_t$，与隐状态 $h_t$ 分离。每步用三个**门**（gate，都是 sigmoid 输出 $\in [0,1]$）控制信息流：

$$
\begin{aligned}
f_t &= \sigma(W_f [h_{t-1}, x_t] + b_f) \quad \text{遗忘门: 旧记忆保留多少} \\
i_t &= \sigma(W_i [h_{t-1}, x_t] + b_i) \quad \text{输入门: 新信息写入多少} \\
g_t &= \tanh(W_g [h_{t-1}, x_t] + b_g) \quad \text{候选值: 新信息内容} \\
c_t &= \underbrace{f_t \odot c_{t-1}}_{\text{旧记忆}} + \underbrace{i_t \odot g_t}_{\text{新写入}} \quad \text{细胞状态更新} \\
o_t &= \sigma(W_o [h_{t-1}, x_t] + b_o) \quad \text{输出门} \\
h_t &= o_t \odot \tanh(c_t)
\end{aligned}
$$

### 4.2 为什么这能治梯度消失

关键在 $c_t = f_t \odot c_{t-1} + i_t \odot g_t$——这是**加法更新**（带门控的残差）。

求 $\partial c_T / \partial c_0$：

$$\frac{\partial c_T}{\partial c_0} = \prod_{t=1}^{T} \big(f_t + (\text{其他项})\big)$$

只要遗忘门 $f_t$ 接近 1（"记住"），这条路径就是**接近 1 的连乘**，梯度不衰减。门控让网络**学会**何时保留（$f_t \to 1$）何时遗忘（$f_t \to 0$），梯度高速路动态开关。

> 🎯 **一句话**：RNN 把所有历史**乘性压缩**进 $h_t$，梯度连乘衰减；LSTM 把"重要的事"**加性累积**进 $c_t$，梯度线性回流。门控决定加什么、丢什么。

### 4.3 门的功能直觉

| 门 | 作用 | 何时激活 |
|---|---|---|
| **遗忘门** $f_t$ | 清空细胞里的旧内容 | 句子主题切换、段落边界 |
| **输入门** $i_t$ | 把新信息写入细胞 | 遇到关键名词、数字、事件 |
| **输出门** $o_t$ | 决定细胞状态多少暴露给 $h_t$ | 只在"需要用"时输出 |

实验分析（Karpathy 的 famous blog *The Unreasonable Effectiveness of RNNs*）显示：LSTM 的 cell 里确实有可解释的"记忆槽位"——某个 cell 专门记"是否在引号内"，另一个记"当前行缩进"。

---

## 5. GRU：LSTM 的简化表亲

Cho et al. (2014) 的 **GRU（Gated Recurrent Unit）** 把 LSTM 的 3 门简化成 2 门，合并了细胞状态和隐状态：

$$
\begin{aligned}
z_t &= \sigma(W_z [h_{t-1}, x_t]) \quad \text{更新门} \\
r_t &= \sigma(W_r [h_{t-1}, x_t]) \quad \text{重置门} \\
\tilde{h}_t &= \tanh(W [r_t \odot h_{t-1}, x_t]) \\
h_t &= (1-z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t
\end{aligned}
$$

GRU 参数少 1/3、速度快，效果通常和 LSTM 持平。**选择 LSTM 还是 GRU 像选 Vim 还是 Emacs——见仁见智**，工业上两者都被用。

---

## 6. 代码：字符级 RNN 学 "hello"（BPTT）

```bash
cd 讲透NLP
python3 -u experiments/13_rnn_lm.py
```

实验 Part B：纯 NumPy 实现字符级 RNN，BPTT 训练它预测 `h→e→l→l→o`。**关键工程细节**：正交初始化 $W_{hh}$（谱半径=1 防爆炸）+ 梯度裁剪（gnorm>5 时缩放）。

```
epoch   0: loss=4.933 | 输入'hell' → 预测'eeoo' (目标'ello')
epoch  50: loss=0.163 | 输入'hell' → 预测'ello' (目标'ello')  ← 学到了!
epoch 100: loss=0.107 | 输入'hell' → 预测'ello' (目标'ello')
epoch 199: loss=0.216 | 输入'hell' → 预测'ello' (目标'ello')

loss 轨迹: 4.933 → 0.216 (下降 ✓)
```

**解读**：
- 第 0 步预测乱码（`eeoo`），loss 高；
- 50 步内就收敛到正确序列 `ello`，loss 从 4.9 降到 0.16；
- 这证明 RNN **能** 学短序列（T=4）的时序依赖——BPTT 在小尺度有效。

> ⚠️ **但注意 Part A 的警告**：把序列长度从 4 加到 25+，普通 RNN 就开始学不到长程依赖（梯度衰减到 1e-2）。这就是为什么真实任务要用 LSTM/GRU，以及最终为什么 attention 取代了 RNN。

**两个工程铁律（实验里都用到了）**：
1. **正交初始化 $W_{hh}$**：`np.linalg.qr(randn(H,H))[0]`，保证谱半径=1，避免一开始就梯度爆炸。
2. **梯度裁剪**：`if gnorm > 5: grad *= 5/gnorm`，RNN 训练的标准护具。这两个技巧让 RNN 在中等长度序列上勉强可训。

---

## 7. 双向 / 多层 RNN

实际 NLP 任务常用两个增强：

- **双向 RNN（BiRNN）**：一个 RNN 从左到右读，另一个从右到左读，两个隐状态拼接。**让每个位置同时看到左右上下文**——这对 POS/NER 等需要完整句子的任务至关重要（[`17-序列标注`](./17-序列标注-POS与NER.md) 会用）。
- **多层 RNN（stacked/deep RNN）**：把一层 RNN 的输出叠给下一层。深层捕捉更抽象的特征，但层数 >3 后梯度病更严重。

---

## 8. 局限与争议：RNN 被取代了吗

### 8.1 作为 NLP 主力：已 100% 被 Transformer 取代

2017 年 *Attention is All You Need* 后，RNN 在机器翻译、语言模型、文本分类等主战场迅速被 Transformer 取代。原因：

| 维度 | RNN/LSTM | Transformer |
|---|---|---|
| **长程依赖** | 门控缓解但 T>50 仍吃力 | attention 直接全连，任意距离 1 跳可达 |
| **并行** | 必须串行（$h_t$ 依赖 $h_{t-1}$）| 全位置并行，GPU 友好 |
| **训练速度** | 慢（串行瓶颈）| 快（几倍~几十倍）|

### 8.2 RNN 仍活跃的角落

1. **实时流式处理**：语音识别流式解码、实时翻译——RNN 的"恒定内存 + 增量更新"对延迟敏感场景仍优于需要重算 attention 的 Transformer。
2. **边缘 / 小模型**：LSTM 参数效率高（无 attention 的 $O(T^2)$ 矩阵），适合塞进手机/嵌入式。
3. **时序预测**：金融、气象、生理信号——非语言序列，attention 不一定更优。
4. **状态空间模型的灵感源**：Mamba (2023)、RWKV 等"线性 RNN 复兴"正是吸取 RNN 的恒定推理成本 + attention 的并行训练，是 2024 年的热门方向。

> 📌 **2024+ 的"RNN 复兴"**：Mamba 的选择性状态空间、RWKV 的线性注意力、Griffin 的递归——都在用新方法重做"RNN 式的恒定内存序列建模"。所以**别把 RNN 当死历史**，它的思想正在以新形态回来。

---

## 9. 与 work4ai 的对接

| 本篇讲透的 | 深度版 |
|---|---|
| RNN cell / BPTT | [`讲透反向传播`](../讲透PyTorch/01-Autograd与计算图.md)（BPTT 是反向传播的时间展开）|
| LSTM 门控 + 残差思想 | [`讲透基础模型`](../讲透基础模型/)（残差连接是 Transformer 的标配）|
| attention 为什么取代 RNN | [`08-Transformer`](./08-Transformer.md) / [`讲透Transformer`](../讲透Transformer/) |
| RNN 在序列标注的应用 | [`17-序列标注-POS与NER`](./17-序列标注-POS与NER.md)（BiLSTM-CRF）|
| Mamba/RWKV 等线性 RNN 复兴 | [`讲透基础模型`](../讲透基础模型/)（架构前沿）|

---

## 📌 下一步

- **理解 RNN 的继任者**：[`08-Transformer`](./08-Transformer.md)（attention 如何解决长程依赖 + 并行）
- **看 RNN 的经典应用**：[`17-序列标注-POS与NER`](./17-序列标注-POS与NER.md)（BiLSTM-CRF 是 NER 的事实标准之一）
- **动手深读**：Karpathy 的 char-rnn（[`../Karpathy经典代码精读/`](../Karpathy经典代码精读/)，Lua 版）是 RNN 教学的祖师级项目

## ✍️ 练习

1. **（验证梯度消失）** 改实验 Part A 的序列长度 T 从 25 扫到 100，画 $\|\partial h_T/\partial h_0\|$ 随 T 的曲线。它是指数衰减吗？衰减率和你估计的谱半径×tanh 导数匹配吗？
2. **（加梯度裁剪）** Part B 里把梯度裁剪阈值从 5 改成 0.5，看训练还能收敛吗？太大太小分别什么后果？
3. **（实现 LSTM）** 把 Part B 的 RNN cell 换成 LSTM cell（4 个门），在长度 30 的随机序列上训练，对比 RNN 是否真的能学长序列而 LSTM 能。
4. **（思考）** Transformer 用"全 attention + 残差连接"也解决了梯度消失。残差连接和 LSTM 的细胞状态加法更新，在"保梯度"的原理上有什么共同点？
5. **（开放）** Mamba（2023）号称"在语言建模上打平 Transformer 且推理恒定内存"。它本质是用什么机制替代了 RNN 的门控？查一篇 Mamba 博客，用本篇的"加法残差保梯度"视角解读它。

---

> 配套实验：[`experiments/13_rnn_lm.py`](./experiments/13_rnn_lm.py)（梯度消失/爆炸铁证 + 字符级 RNN BPTT）。姊妹章节：[`08-Transformer`](./08-Transformer.md)（继任者）、[`17-序列标注-POS与NER`](./17-序列标注-POS与NER.md)（BiLSTM-CRF 应用）。
