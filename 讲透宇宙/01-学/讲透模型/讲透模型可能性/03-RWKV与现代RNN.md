# 03 — RWKV：RNN 的推理效率 + Transformer 的训练并行

> 01 讲 SSM（线性动力系统路线），02 讲 Linear Attention（核近似路线）。本篇讲第三条 O(n) 路线——**RWKV**（BlinkDL/RWKV，2023起）：它**看起来像 RNN**（推理 O(1) 内存），但**训练能并行**（不像传统 RNN）。靠的是"**线性注意力写成递推形式**"的数学技巧。

---

## 1. 灵魂：RWKV = 可并行的 RNN

$$
\boxed{\text{RWKV 的 WKV} = \frac{\sum_{i=1}^{t-1} e^{-(t-1-i)w + k_i \cdot v} \cdot v_i + e^{u + k_t \cdot v_t} \cdot v_t}{\sum_{i=1}^{t-1} e^{-(t-1-i)w + k_i} + e^{u + k_t}}}
$$

看起来复杂，核心思想一句：**把 attention 的"对所有历史 token 加权求和"改写成"累积统计量递推"**——每步只需维护一个固定大小的"记忆状态"，推理 O(1)。

---

## 2. 直觉层：attention vs RNN vs RWKV

| 范式 | 推理 | 训练 | 记忆 |
|---|---|---|---|
| **Transformer** | O(n) 每步（看全部历史）| 并行 | 全历史（KV Cache 越来越大）|
| **传统 RNN** | O(1) 每步（只看隐状态）| **不可并行**（时序依赖）| 压缩进固定隐状态（会忘）|
| **RWKV** | **O(1) 每步** | **可并行**（线性递推可展开）| 固定状态，但"线性注意力"让记忆更持久 |

RWKV 的魔法：**它本质是 Linear Attention（02 章）写成 RNN 形式**。

---

## 3. 数学层：WKV 机制

### 3.1 拆解公式

RWKV 每步的输出基于三个量：$w$（时间衰减）、$k$（键）、$v$（值）。

**分子**：$\sum_i \underbrace{e^{-(t-1-i)w}}_{\text{越老越衰减}} \cdot \underbrace{e^{k_i \cdot v}}_{\text{相关性加权}} \cdot v_i$

- $(t-1-i)w$：时间距离 × 衰减率——**老 token 指数遗忘**
- $k_i \cdot v$：相关性——**像 attention 一样按内容加权**

**关键**：这个求和可以**递推**——维护"累积加权和"与"累积权重和"，每步只做 O(1) 更新。

### 3.2 为什么能并行训练

传统 RNN：$h_t = \tanh(W h_{t-1} + U x_t)$——非线性 $\tanh$ 让 $h_t$ 不能写成 $h_{t-1}$ 的线性组合，**必须按顺序算**。

RWKV：递推是**线性的**（累积和 + 指数衰减），可以展开成**前缀和**——用 parallel-scan 算法 $O(n \log n)$ 并行。这就是"RNN 形式 + Transformer 训练效率"的来源。

---

## 4. RWKV 的架构组件

### 4.1 时间混合（Time Mixing）

每层的核心：用 WKV 把"过去的信息"和"当前输入"混合。

### 4.2 通道混合（Channel Mixing）

类似 FFN，但用"门控 + 过去状态"——不是纯前馈，而是**带记忆的 FFN**。

### 4.3 与 Transformer 的对应

| Transformer | RWKV |
|---|---|
| Self-Attention | Time Mixing（WKV）|
| FFN | Channel Mixing |
| LayerNorm | LayerNorm（相同）|
| 位置编码 | 用 $w$（时间衰减）隐式编码 |

---

## 5. RWKV 的优势与局限

### 5.1 优势

- **推理 O(1) 内存**：不像 Transformer 的 KV Cache 线性增长，RWKV 固定状态——**超长上下文推理友好**
- **训练可并行**：不像传统 RNN 必须顺序，RWKV 用 parallel-scan
- **开源生态**：RWKV 有完整开源模型（0.1B-14B），社区活跃

### 5.2 局限

- **表达力弱于 Attention**：WKV 的"时间衰减 + 相关性"不如 softmax attention 的"动态聚焦"灵活
- **长程检索弱**：信息压缩进固定状态，"找第 5000 个 token 的精确事实"不如 KV Cache
- **生态规模小**：vs Transformer/Mamba 的论文和工程投入，RWKV 是"小众精品"

---

## 6. RWKV vs Mamba vs Linear Attention

三条 O(n) 路线的对比：

| 维度 | Linear Attention（02）| **RWKV** | Mamba（01）|
|---|---|---|---|
| 数学本质 | 核近似 softmax | 线性注意力递推 | 连续动力系统离散 |
| 记忆机制 | 隐式（核展开）| **显式累积状态** | 选择性状态空间 |
| 推理 | O(n) | **O(1)** | O(1) |
| 训练 | 并行 | 并行 | 并行（卷积/scan）|
| 表达力 | 中 | 中 | 中高（选择性）|
| 工程成熟度 | 低 | 中（有开源模型）| 高（Mamba-2/Hazal）|

> **洞察**：三条路线殊途同归——都是"把 attention 的全局加权改成可递推的累积"。Mamba 靠 SSM 理论，RWKV 靠线性注意力，Linear Attention 靠核近似。

---

## 7. 批判性

- **RWKV 是"工程艺术"**：它证明了 RNN 范式没死，但**是否值得投入**取决于生态——Transformer 的工程优势太大
- **"O(1) 推理"的代价是检索能力**：固定状态记不住精确事实，长文档问答不如 KV Cache
- **未来在混合架构**：纯 RWKV 可能不如 RWKV + Attention 混合（06 章）

> **诚实结论**：RWKV 是 O(n) 探索里"最有 RNN 美感"的方案，但它的市场窗口正在被 Mamba 和混合架构挤压。

---

## 📌 下一步

[04-长卷积Hyena](04-长卷积Hyena.md)讲第四条 O(n) 路线（长卷积）。或跳 [06-混合架构](06-混合架构Jamba.md)——看 Jamba/Hawk/Griffin 怎么把 Mamba 和 Attention 混合，取两者之长。

## ✍️ 练习

1. RWKV 的推理 O(1) 内存意味着什么？（提示：生成 100K token 不需要 100K 的 KV Cache。）
2. RWKV 的"时间衰减 w"和 Transformer 的位置编码什么关系？哪个更灵活？
3. 为什么 RWKV 在"精确事实检索"上弱于 Transformer？（提示：固定状态是有损压缩。）
