# 附录 A — 隐马尔可夫模型（HMM）：看不见的状态，看得见的线索

> 对应 SLP3 附录 A。HMM 是序列标注（POS tagging、NER）和语音识别的前神经网络时代王者。虽然 LLM 已接管这些任务，但 HMM 的三个核心算法——前向、Viterbi、Baum-Welch——仍然是理解概率推理的最佳教材。
>
> 配套实验：`experiments/A_hmm_viterbi.py`

---

## 1. 直觉：看不见的天气，看得见的冰淇淋

你住在一个没有窗户的房间里，想知道外面天气（**热 H / 冷 C**），但只能通过室友每天吃的冰淇淋数量（**1、2、3 个**）来推断。

```
天气（隐藏）：    H    →    C    →    C    →    H    →    H
                      ↓         ↓         ↓         ↓         ↓
冰淇淋（观测）：       3        1        1        2        3
```

这就是 HMM 的本质：**有一条你看不见的状态链在驱动一切，每个状态以一定概率“发射”一个你能看到的观测**。

为什么叫“马尔可夫”？因为假设：**明天的天气只依赖今天的天气**，不看更早的历史（一阶马尔可夫假设）。为什么叫“隐”？因为状态序列本身是隐藏的——你只看到冰淇淋数量。

### HMM 的五个要素

| 符号 | 含义 | 例子 |
|------|------|------|
| $Q = \{q_1, \ldots, q_N\}$ | $N$ 个隐藏状态 | {N(名词), V(动词)} |
| $V = \{v_1, \ldots, v_M\}$ | $M$ 个可能的观测 | {fly, duck, fish, birds} |
| $A = [a_{ij}]$ | 转移概率 $a_{ij} = P(q_t = j \mid q_{t-1} = i)$ | $P(\text{V} \mid \text{N}) = 0.4$ |
| $B = [b_j(k)]$ | 发射概率 $b_j(k) = P(o_t = v_k \mid q_t = j)$ | $P(\text{fly} \mid \text{V}) = 0.40$ |
| $\pi = [\pi_i]$ | 初始概率 $\pi_i = P(q_1 = i)$ | $P(\text{句子首词是名词}) = 0.7$ |

模型记为 $\lambda = (A, B, \pi)$。

---

## 2. 三大问题

HMM 的一切用途都归结为三个问题。理解了这三个问题，就理解了 HMM 的全部。

### 问题 1：评估（Evaluation）—— 前向算法

> 给定模型 $\lambda$ 和观测序列 $O = o_1 o_2 \cdots o_T$，求 $P(O \mid \lambda)$。

**直白说**：这条观测序列有多“合理”？

朴素想法：遍历所有可能的状态序列 $Q$（共 $N^T$ 种），算每种的概率，求和。但 $N^T$ 是指数级——$N=2, T=50$ 就有 $2^{50} \approx 10^{15}$ 种。

**前向算法**用动态规划把它降到 $O(N^2 T)$。定义前向变量：

$$\alpha_t(j) = P(o_1, o_2, \ldots, o_t, q_t = j \mid \lambda)$$

含义：在时刻 $t$ 处于状态 $j$，且到 $t$ 为止看到了观测 $o_1 \ldots o_t$ 的**联合概率**。

**递推**：

$$\alpha_1(j) = \pi_j \cdot b_j(o_1), \quad j = 1, \ldots, N$$

$$\alpha_t(j) = \Bigg[\sum_{i=1}^{N} \alpha_{t-1}(i) \cdot a_{ij}\Bigg] \cdot b_j(o_t), \quad t = 2, \ldots, T$$

$$P(O \mid \lambda) = \sum_{j=1}^{N} \alpha_T(j)$$

**怎么理解这个递推？** 在时刻 $t$ 到达状态 $j$，必须先在 $t-1$ 处于某个状态 $i$，再按 $a_{ij}$ 转移过来。所有可能的“上一状态”求和就是 $\sum_i \alpha_{t-1}(i) a_{ij}$——即“从各条路径到达 $j$ 的总概率”。最后乘上 $b_j(o_t)$，因为到了 $j$ 还得发射出 $o_t$。

### 问题 2：解码（Decoding）—— Viterbi 算法

> 给定 $\lambda$ 和 $O$，求最可能的隐藏状态序列 $Q^* = \arg\max_Q P(Q \mid O, \lambda)$。

这是 **POS tagging 的核心**：给定一句话（观测），找出每个词最可能的词性（状态）。

Viterbi 和前向算法几乎一样，唯一的区别：**把求和换成取最大值**，外加一个回溯指针。

$$\delta_1(j) = \pi_j \cdot b_j(o_1)$$

$$\boxed{\delta_t(j) = \max_{i=1}^{N} \big[\delta_{t-1}(i) \cdot a_{ij}\big] \cdot b_j(o_t)}$$

$$\psi_t(j) = \arg\max_{i=1}^{N} \big[\delta_{t-1}(i) \cdot a_{ij}\big]$$

$\delta_t(j)$ = 在时刻 $t$ 处于状态 $j$ 的**最优路径**概率；$\psi_t(j)$ 记录这条最优路径在上一时刻来自哪个状态。

**回溯**：

$$q_T^* = \arg\max_j \delta_T(j), \quad q_t^* = \psi_{t+1}(q_{t+1}^*), \quad t = T-1, \ldots, 1$$

> **为什么取 max 而不是 sum 就从“概率”变成了“最可能路径”？** 因为 sum 考虑了**所有**到 $j$ 的路径（有些路径状态序列不同但都会经过 $j$），而 max 只保留**最好的一条**。前向算法回答“这条观测序列总体多可能”（所有路径贡献之和），Viterbi 回答“哪条具体路径最可能”（最优单条路径）。

### 问题 3：学习（Learning）—— Baum-Welch 算法（EM）

> 给定观测序列 $O$，如何训练出最优参数 $\lambda = (A, B, \pi)$？

这是最难的。EM（Expectation-Maximization）在这里叫 **Baum-Welch 算法**：

1. **E 步**：用当前参数算“在每个时刻处于各状态的概率”（需要后向变量 $\beta$）
2. **M 步**：用这些概率重新估计 $A, B, \pi$
3. 重复直到收敛

需要后向变量：

$$\beta_T(i) = 1, \quad \beta_t(i) = \sum_{j=1}^{N} a_{ij} \cdot b_j(o_{t+1}) \cdot \beta_{t+1}(j)$$

定义：

$$\gamma_t(i) = \frac{\alpha_t(i) \cdot \beta_t(i)}{P(O \mid \lambda)} \quad \text{（时刻 $t$ 处于状态 $i$ 的后验概率）}$$

$$\xi_t(i, j) = \frac{\alpha_t(i) \cdot a_{ij} \cdot b_j(o_{t+1}) \cdot \beta_{t+1}(j)}{P(O \mid \lambda)} \quad \text{（$t$ 时刻 $i \to j$ 的后验概率）}$$

**重估公式**（M 步）：

$$\bar{\pi}_i = \gamma_1(i), \quad \bar{a}_{ij} = \frac{\sum_{t=1}^{T-1} \xi_t(i, j)}{\sum_{t=1}^{T-1} \gamma_t(i)}, \quad \bar{b}_j(k) = \frac{\sum_{t: o_t = v_k} \gamma_t(j)}{\sum_{t=1}^{T} \gamma_t(j)}$$

直觉：$\bar{a}_{ij}$ = （从 $i$ 到 $j$ 的期望转移次数）/（在 $i$ 的期望停留次数）。就是“数数”，但用软概率而非硬标签。

---

## 3. Viterbi 的工程实现：log 空间

实际代码中连乘 $T$ 个小概率会下溢。标准做法是取 $\log$，把乘法变加法：

$$\log \delta_t(j) = \max_{i} \big[\log \delta_{t-1}(i) + \log a_{ij}\big] + \log b_j(o_t)$$

所有运算变成加法和取 max，数值稳定且高效。

---

## 4. 代码跑通：Viterbi 做 POS 标注

```bash
python3 experiments/A_hmm_viterbi.py
```

实验设计了一个微型 HMM（2 个状态 N/V，4 个词），对 "birds fly duck" 做 Viterbi 解码。

**反直觉发现**：`duck` 这个词的发射概率是 $P(\text{duck} \mid \text{V}) = 0.21 > P(\text{duck} \mid \text{N}) = 0.19$，逐词贪心会判它为 V。但 Viterbi 判它为 **N（名词）**——因为前面的 `fly` 被解码为 V，而转移概率 $a_{\text{V,N}} = 0.8 \gg a_{\text{V,V}} = 0.2$。转移优势 4× 完全压过发射劣势 1.11×。**上下文（转移概率）完全压过了词本身（发射概率）**。

---

## 5. HMM 在 NLP 中的应用

| 应用 | 状态 | 观测 | 备注 |
|------|------|------|------|
| POS tagging | 词性标签 | 单词 | 经典 HMM tagger（Ch 17） |
| 语音识别 | 音素序列 | 声学特征 | HMM-DNN 混合系统（Ch 15） |
| NER | BIO 标签 | 单词/特征 | 后来被 CRF 取代 |
| 中文分词 | BMES 标签 | 汉字 | HMM/CRF 分词器 |

---

## 6. 局限与批判

1. **一阶马尔可夫假设太强**：只看前一个状态，无法建模长距离依赖。"$n$-gram HMM"可以推广但状态空间指数爆炸。

2. **发射概率独立假设**：HMM 假设观测只依赖当前状态，与历史无关。但 "I saw a saw" 里两个 `saw` 的词性依赖上下文，不是只看当前位置。

3. **生成式模型的结构限制**：HMM 是生成式 $P(Q, O) = \prod P(q_t \mid q_{t-1}) P(o_t \mid q_t)$，不能灵活地融合任意特征（前后词、词缀、大小写、词表……）。这正是 **CRF（条件随机场）** 取代它的原因：CRF 直接建模 $P(Q \mid O)$，可以加任意特征函数。

4. **被神经网络完全取代**：BiLSTM-CRF（2015-2018）→ BERT 微调（2018-）→ LLM in-context（2022-），POS tagging 的 HMM 已纯属教学遗产。

5. **但 HMM 思想没死**：LLM 的自回归生成本质上是“状态=已生成 token 序列，观测=下一个 token”的退化 HMM。GPT 的隐藏状态可以看成连续版本的 HMM 状态。

---

## 7. 在 LLM 时代的地位

HMM 作为**工程工具**已退出主流，但作为**教学工具**无可替代：

- 它是理解**生成式概率模型**的最佳入口
- 前向算法是**变分推断**和**信念传播**的离散特例
- Baum-Welch 是 **EM 算法**的经典案例
- Viterbi 是**动态规划**在概率推理中的教科书级应用
- 理解了 HMM，再看 CRF 和 BiLSTM-CRF 就只是“换了个特征提取器”

---

## 📌 下一步

- → `17-序列标注-POS与NER.md`：HMM tagger 的完整版，CRF 如何改进
- → `15-自动语音识别-ASR.md`：HMM 在语音中的角色（HMM-GMM → HMM-DNN → CTC → Attention）
- → `../讲透概率图模型/`：HMM 作为最简单的动态贝叶斯网络

---

## ✍️ 练习

**练习 A.1**：手动跑一遍前向算法，计算 "birds fly duck" 的 $P(O \mid \lambda)$。然后跑 Viterbi，对比两者数值。

**练习 A.2**：把 $\pi$ 改为 $[0.3, 0.7]$（首词更可能是动词），重跑 Viterbi。结果变了吗？为什么？

**练习 A.3**：扩展到 3 个状态（加 D=限定词），重新设计转移矩阵和发射矩阵，实现一个能标注 "the birds fly" 的 mini HMM tagger。

**练习 A.4**：实现后向算法 $\beta$，验证 $\sum_j \alpha_t(j) \beta_t(j) = P(O \mid \lambda)$ 对所有 $t$ 成立（这是 HMM 的一个不变量）。

---

> 配套实验：`experiments/A_hmm_viterbi.py`。姊妹章节：`17-序列标注-POS与NER.md`、`15-自动语音识别-ASR.md`。
