# Ch 15 — 自动语音识别 (ASR)：HMM → CTC → Attention → Whisper 的演化

> 这是「讲透NLP」语音三件套的第二篇。上一篇（Ch 14）讲了语音的物理特征——MFCC、语谱图怎么提取。这一篇回答：**拿到特征之后，怎么把它变成文字？**
>
> 答案的演化本身就是一部浓缩的深度学习史：**HMM-GMM → CTC → Attention (LAS) → Conformer/Whisper**。你会看到，"用更多数据暴力解决一切"这个 LLM 时代的信仰，在语音领域由 Whisper 给出了最终证明。

**对应 SLP3 第 15 章**：https://web.stanford.edu/~jurafsky/slp3/15.pdf

---

## 0. 这一章解决什么问题？

**自动语音识别 (Automatic Speech Recognition, ASR)** 的任务定义极简：

$$\hat{Y} = \arg\max_{Y} P(Y \mid X)$$

输入 $X = (x_1, x_2, \ldots, x_t)$ 是 $t$ 个声学特征向量（每 10 ms 一帧），输出 $Y = (y_1, y_2, \ldots, y_m)$ 是文字序列。把它映射到字符集上（英语 26 个字母 + 空格 + 标点），或者 BPE token。

**为什么这极难？** 四重困难叠在一起：

| 困难 | 直觉例子 | 后果 |
|------|---------|------|
| **变长对齐** | 说 "dinner" 持续 0.5 s = 50 帧，但只有 6 个字母 | 不知道哪帧对应哪个字母 |
| **说话速度** | 同一句话快说慢说帧数差 3 倍 | 对齐关系不稳定 |
| **口音/说话人** | "about" 在加拿大口音里接近 "aboot" | 同词不同音 |
| **同音/噪声** | "their/there"、"下雨了/下鱼了" | 单靠声学无法消歧 |

前三条是**声学问题**（怎么把声波映射到音素/字符），第四条是**语言问题**（怎么用上下文消歧）。整个 ASR 的演化，就是**如何把这两件事用一个统一的端到端模型一起做掉**。

---

## 1. 直觉：把声音变成文字——为什么难

### 1.1 核心矛盾：输入长，输出短

英语里一个词平均 5 个字母、约 250 ms 发音时长。250 ms = 25 帧（10 ms/帧）。所以声学输入和文字输出的长度比大约是：

$$\frac{\text{输入帧数}}{\text{输出字符数}} \approx \frac{25}{5} = 5 \quad\text{到}\quad \frac{25}{1.3} \approx 19 \text{（BPE token 视角）}$$

**输入比输出长 5～19 倍。** 这是 ASR 和 MT（机器翻译，长度比接近 1:1）最本质的差异。所有 ASR 架构设计的核心问题就是：**怎么处理这个长度不匹配？**

### 1.2 三个历史答案

1. **HMM 时代（1980s–2010s）**：把长度不匹配拆成两步——先用声学模型估每帧是哪个音素的概率，再用 Viterbi 在所有可能的对齐路径里搜索最优路径。**手工拆分声学/语言模型，各训各的。**

2. **CTC 时代（2006–2018）**：Graves 提出一个巧妙的损失函数——让网络每帧都输出一个字符（包括"blank"），然后用折叠规则把重复字符和 blank 去掉，得到最终文字。**一次 softmax 解决对齐问题，但假设帧间条件独立。**

3. **Attention 时代（2014–至今）**：直接用 encoder-decoder + cross-attention，让 decoder 自己学会"听哪个时间段的音频"。**端到端，不假设独立，但不能流式。** Whisper 是这一路线的极致——用 68 万小时多语言数据，把所有技巧弱化为"暴力 scale"。

---

## 2. 数学：四代 ASR 架构

### 2.1 第一代：HMM-GMM（经典统计语音识别）

**思想**：用贝叶斯法则把 ASR 拆成三个独立部件。

$$\hat{W} = \arg\max_{W} \underbrace{P(X \mid W)}_{\text{声学模型}} \cdot \underbrace{P(W)}_{\text{语言模型}}$$

- **声学模型 $P(X \mid W)$**：给定文字 $W$，观察到声学特征 $X$ 的概率。用 HMM 建模：每个音素是一个隐状态，帧是观测。状态转移概率用 GMM（高斯混合模型）拟合。
- **语言模型 $P(W)$**：文字序列的先验概率。用 N-gram（见 Ch 3）或 RNN LM。
- **解码 (decoding)**：在所有可能的 $W$ 和所有可能的对齐路径里，找到联合概率最大的那个。用 **Viterbi 算法**（动态规划，见附录 A）。

**HMM 三问题**（SLP3 附录 A 的核心）：

| 问题 | 算法 | 用途 |
|------|------|------|
| 评估：$P(O \mid \lambda) = ?$ | Forward 算法 | 算观测序列概率 |
| 解码：最可能的隐状态序列？ | **Viterbi 算法** | **ASR 解码的核心** |
| 学习：估计参数 $A, B$？ | Forward-Backward (Baum-Welch) | EM 训练 |

**为什么被淘汰？**

1. **手工流水线**：音素词典要人工编（CMUdict 之类的），GMM 和 LM 各训各的，误差累积。
2. **GMM 表达力弱**：高斯分布拟合不了复杂声学特征。
3. **DNN-HMM 混合**：2012 年后用 DNN 替代 GMM 估 $P(\text{state} \mid x_t)$，但框架还是 HMM。直到端到端模型出现才彻底改变。

> 💡 **历史锚点**：HMM-GMM 主导语音 30 年。2012 年 Hinton 用 DNN 替换 GMM（DNN-HMM），WER 暴降 30%。但真正的革命是 2014 年的 CTC 和 Attention——把 HMM 也一起干掉。

---

### 2.2 第二代：CTC — Connectionist Temporal Classification

**核心思想**（Graves et al., 2006）：**不再需要知道每帧对齐到哪个字符。**

#### 2.2.1 Blank 的天才设计

CTC 引入一个特殊符号 $\text{blank}$（记作 $\epsilon$ 或 `-`）。网络每帧输出一个符号（字符或 blank），然后通过**折叠函数 $\mathcal{B}$** 把它变成最终文字：

$$\mathcal{B}(\text{对齐序列}) = \text{先合并连续重复字符，再去掉所有 blank}$$

**例子**（SLP3 图 15.13，说 "dinner"）：

```
原始对齐:  d d - i i - n n - e e r
           ↓ 合并连续重复
           d - i - n - e r
           ↓ 去掉 blank
           d i n e r          ← 错！丢了双写 n

正确对齐:  d - i - n - - n - e r    ← 两个 n 之间必须有 blank！
           ↓ 折叠
           d i n n e r          ← 对！
```

**反直觉点**：blank 不是"空"——它是**分隔符**。没有它，"nn" 会被折叠成 "n"。blank 让 CTC 能区分"这个字符延续"和"这是一个新字符"。

#### 2.2.2 CTC 损失函数

给定输入 $X$ 和目标 $Y$，CTC 损失是对所有能折叠成 $Y$ 的对齐路径 $\pi$（alignment path）的概率取负对数：

$$\boxed{\mathcal{L}_{\text{CTC}}(X, Y) = -\log \sum_{\pi \in \mathcal{B}^{-1}(Y)} \prod_{t=1}^{T} p(\pi_t \mid X)}$$

其中 $\mathcal{B}^{-1}(Y)$ 是所有能被 $\mathcal{B}$ 映射到 $Y$ 的对齐路径集合。

**为什么用求和而不是取 max？** 因为训练时要**最大化 $P(Y \mid X)$**，而 $P(Y \mid X) = \sum_{\pi \in \mathcal{B}^{-1}(Y)} P(\pi \mid X)$——所有可能的对齐都对最终概率有贡献。取 max（Viterbi 式）会忽略其他对齐路径的概率，训练不稳定。

**条件独立假设**：上式中 $\prod_t p(\pi_t \mid X)$ 假设每帧的输出**只依赖于输入 $X$（全局），与其他帧的输出条件独立**：

$$p(\pi_1, \ldots, \pi_T \mid X) = \prod_{t=1}^{T} p(\pi_t \mid X)$$

这是 CTC 最强的假设，也是它最大的弱点（见批判部分）。

#### 2.2.3 动态规划求和（前向算法）

对齐路径数是指数级的，直接求和不可行。CTC 用动态规划（类似 HMM 的 forward 算法）高效计算：

定义展开序列 $Z = (\epsilon, y_1, \epsilon, y_2, \epsilon, \ldots, y_M, \epsilon)$（在目标 $Y$ 的每个字符间插入 blank）。

前向变量 $\alpha_j(t)$ = 时刻 $t$、到 $Z$ 的第 $j$ 个位置为止，所有合法对齐路径的概率之和：

$$\alpha_j(t) = \begin{cases} [\alpha_{j-1}(t\!-\!1) + \alpha_j(t\!-\!1)] \cdot p_t(z_j \mid X) & \text{if } z_j = \epsilon \text{ or } z_j = z_{j-2} \\ [\alpha_{j-2}(t\!-\!1) + \alpha_{j-1}(t\!-\!1) + \alpha_j(t\!-\!1)] \cdot p_t(z_j \mid X) & \text{otherwise} \end{cases}$$

最终 $P(Y \mid X) = \alpha_{|Z|-1}(T) + \alpha_{|Z|}(T)$。这个递推可以在 $O(T \times |Z|)$ 时间内算完。

> 💡 **HMM 的回响**：这个动态规划和 HMM 的 forward 算法几乎一模一样——CTC 本质上就是一个特殊的 HMM，只不过发射概率由神经网络给出，状态结构由 blank 设计固定。**历史螺旋上升。**

#### 2.2.4 CTC 解码

**Greedy decode**（最简单）：每帧取 argmax，然后折叠。

$$\hat{Y} = \mathcal{B}\left(\arg\max_{\pi_t} p(\pi_t \mid X)\right)_{t=1}^{T}$$

**Beam search decode**（更好但复杂）：维护 top-$k$ 个候选路径，在折叠后合并相同输出的路径概率。**关键**：合并是 CTC beam search 的精髓——多条不同的对齐路径可能折叠成同一个输出，要汇总它们的概率。

**语言模型 rescoring**（实战必备）：因为 CTC 条件独立，不隐含语言模型，所以必须外接：

$$\hat{W} = \arg\max_W \left[\log P_{\text{CTC}}(Y \mid X) + \lambda \log P_{\text{LM}}(W) + \eta L(W)\right]$$

其中 $L(W)$ 是长度惩罚（防止太短），$\lambda, \eta$ 在验证集调。

---

### 2.3 第三代：Attention-based Encoder-Decoder (LAS)

**Listen, Attend and Spell (LAS)**（Chan et al., 2016; Chorowski et al., 2014）：

和机器翻译的 encoder-decoder 完全同构（见 Ch 12），只是输入从 token embedding 变成声学特征序列。

#### 2.3.1 架构

```
声学特征 X = (x₁,...,xₙ)
        ↓ [压缩: subsampling / 卷积下采样]
    Encoder (Transformer/RNN)
        ↓
    H_enc = (h₁,...,hₙ)
        ↓                ↑ cross-attention
    Decoder              │  (query from decoder, key/value from encoder)
        ↓
    Y = (y₁,...,yₘ)  逐字符生成
```

#### 2.3.2 数学

解码每一步：

$$P(y_i \mid y_1, \ldots, y_{i-1}, X) = \text{softmax}(\text{MLP}(s_i, c_i))$$

其中 $s_i$ 是 decoder 隐状态，$c_i$ 是由 attention 计算的 context vector：

$$c_i = \sum_{t=1}^{n} \alpha_{it} h_t^{\text{enc}}, \qquad \alpha_{it} = \text{Attention}(s_i, h_t^{\text{enc}})$$

**和 CTC 的根本区别**：

| | CTC | Attention (LAS) |
|---|---|---|
| 输出依赖 | 只依赖输入 $X$，帧间条件独立 | 依赖 $X$ **和已生成的 $y_1...y_{i-1}$** |
| 隐含 LM | ❌ 没有（需外接） | ✅ 有（decoder 本身是条件 LM） |
| 流式 | ✅ 可以 | ❌ 需要完整输入才能 attention |
| 准确率 | 较低（独立假设限制） | 较高 |

#### 2.3.3 压缩：为什么必须 subsampling

语音的输入输出比太大（5-19 倍），直接让 Transformer attention 处理几百帧太慢。解决方法：

- **Low frame rate**（Pundak & Sainath, 2016）：把每 3 帧拼接成 1 帧，序列缩短 3 倍。
- **卷积下采样**：在 encoder 前加几层 strided CNN（步长 > 1），降采样 4-8 倍。
- **Pyramid encoder**（LAS 原文）：每层 RNN 时间分辨率减半，3 层减 8 倍。

---

### 2.4 现代汇总：CTC + Attention + LM + 大数据

#### 2.4.1 混合损失：CTC + Attention 联合训练

两者各有优劣，所以现代系统常**联合训练**（SLP3 图 15.16）：

$$\mathcal{L}_{\text{total}} = \lambda \cdot \mathcal{L}_{\text{CTC}} + (1 - \lambda) \cdot \mathcal{L}_{\text{CE}}^{\text{attention}}$$

$\lambda$ 在验证集调（通常 0.3-0.7）。CTC 帮助收敛和对齐，Attention 保证精度。

#### 2.4.2 RNN-T：让 CTC 也能流式

RNN-Transducer（Graves, 2012）在 CTC 基础上加一个 **prediction network**（子词级 LM），去掉条件独立假设：

$$\text{RNN-T} = \text{CTC encoder} + \text{prediction network}(y_{u-1}) + \text{joint network}$$

这是 **2023 年前手机端 ASR 的主力**（Google Pixel 用 RNN-T）。能流式 + 有语言模型 + 端到端。

#### 2.4.3 Conformer：卷积 + Attention 的集大成

Conformer（Gulati et al., 2020）= Transformer encoder + 卷积模块：

```
Conformer block = FFN → [Multi-Head Self-Attention] → [Convolution] → FFN → LayerNorm
```

**直觉**：Attention 擅长捕捉全局依赖（长距离上下文），卷积擅长捕捉局部模式（音素级别的频率特征）。两者结合在语音任务上长期 SOTA（LibriSpeech WER < 2%）。

#### 2.4.4 自监督预训练：Wav2Vec2.0 / HuBERT

- **Wav2Vec2.0**（Baevski et al., 2020）：对原始波形做对比学习预训练，再接 CTC fine-tune。
- **HuBERT**（Hsu et al., 2021）：类似 BERT 的掩码预测，对声学特征做自监督。

**SLP3 的观点**：这些是语音领域的 "BERT"——先用无标注音频学通用表示，再用少量标注数据 fine-tune。它们通常搭配 CTC 损失做下游 ASR。

#### 2.4.5 Whisper：68 万小时数据的降维打击

**Whisper**（Radford et al., 2023）的架构没有什么新东西——就是标准的 Transformer encoder-decoder。它的革命在数据：

- **68 万小时**多语言音频-文本对（从互联网爬取 + 人工标注过滤）
- 覆盖 99 种语言
- 多任务训练：ASR + 翻译 + 语言识别

**Whisper 的核心教训**：当数据量大到一定程度，架构细节（CTC vs Attention vs Conformer）的差异被**淹没**了。Whisper 用最朴素的 encoder-decoder，靠数据量打败了所有精巧设计的系统。**这是 LLM 时代 "scale is all you need" 信仰在语音领域的验证。**

---

## 3. 评估：Word Error Rate (WER)

ASR 的标准评估指标是**词错误率**：

$$\text{WER} = \frac{S + D + I}{N} = \frac{\text{替换} + \text{删除} + \text{插入}}{\text{参考词数}}$$

通过**最小编辑距离**（Levenshtein distance，见 Ch 2）对齐假设和参考文本后统计。

**参考标尺**（LibriSpeech test-clean）：

| 系统 | WER |
|------|-----|
| HMM-GMM (2010) | ~9% |
| CTC (2014) | ~5% |
| LAS (2016) | ~5% |
| Conformer (2020) | **~1.9%** |
| 人类转录 | ~1.8% |

Conformer 已经**达到人类水平**（在干净朗读语音上）。但在嘈杂/远场/口音场景，最好的系统 WER 仍在 10-20%。

---

## 4. 代码：CTC 解码实战

配 `experiments/15_ctc_decode.py`。三个部分：

1. **模拟训练好的 ASR 输出**：构造一个帧级概率矩阵（模拟说 "HELLO" 的 18 帧输出）。
2. **实现 CTC greedy decode 和 beam search**：纯 NumPy，从零写。
3. **两个反直觉发现**：
   - **发现 1**：blank 是 CTC 的灵魂——去掉它，CER 从 0% 飙升到 120%（双字母丢失、静音段乱出字符）。
   - **发现 2**：beam search 加宽 (5→10→20) 不仅不提升反而略差 (-9.7%)，但词典 LM rescoring 将 CER 从 22.8% 降到 0.5% (97.8% 降低)。**CTC 的瓶颈不在解码算法，在条件独立假设。**

```bash
cd /data/usershare/ai/work4ai/讲透NLP
python3 -u experiments/15_ctc_decode.py
```

---

## 5. 批判：CTC 的天花板与 Whisper 的暴力美学

### 5.1 CTC 的条件独立假设是结构性缺陷

CTC 假设 $p(\pi_t \mid X)$ 独立于 $\pi_{t-1}$。这意味着：

- **不知道前一个字符是什么** → 无法避免输出 "HELLO" 中间乱插入 "X"（因为某一帧碰巧 "X" 概率高）。
- **不隐含语言模型** → 必须外接 LM，增加系统复杂度。
- **beam search 提升有限** → 因为 beam search 只在"选哪条路径"上优化，而路径内的每帧决策仍然是独立的。**真正的信息损失发生在概率分解阶段，不在解码阶段。**

> 💡 **反直觉铁证**：跑实验你会发现，beam search (beam=20) 相比 greedy 不仅没提升，反而 CER 更差 (-9.7%)——因为条件独立假设下，beam search 的路径合并反而引入了噪声。而一个简单的词典 LM rescoring 将 CER 从 22.8% 降到 0.5% (97.8% 降低)。**解码算法的优化空间远小于语言知识的注入。**

### 5.2 Attention 模型也不能流式

LAS/Whisper 需要**完整输入**才能开始解码（因为 cross-attention 要看全部 encoder 输出）。这在实时场景（语音助手、字幕、会议记录）不可接受。

**解决方案**：
- RNN-T（能流式但精度不如 LAS）
- 在线 attention（限制 attention 窗口，但精度损失）
- Conformer + 流式解码（工程折中）

### 5.3 Whisper 用数据碾压一切技巧

Whisper 的成功传达了一个不舒服的信息：**ASR 的架构创新可能已经到头了。**

| 因素 | 传统系统 | Whisper |
|------|---------|---------|
| 架构 | 精心设计（CTC+Attention+Conformer+LM） | 普通 encoder-decoder |
| 数据 | 数千-数万小时 | **68 万小时** |
| 语言模型 | 必须外接 | 内化在 decoder 里 |
| 多语言 | 各语言单独建模型 | 一个模型管 99 种语言 |

**批评**：
1. **不可复现**：68 万小时数据只有大公司能搞到。学术界的小模型创新被碾压。
2. **推理慢**：encoder-decoder 不能流式，延迟高。
3. **幻觉**：Whisper 在静音段会"编"出文字（因为 decoder 是 LM，倾向于生成流畅但不准确的内容）。
4. **低资源语言仍然差**：虽然有 99 种语言，但分布极不均匀，小语种 WER 仍高。

### 5.4 ASR 还没解决的问题

- **鸡尾酒会问题**（cocktail party）：多人重叠说话的分离 + 识别。
- **重口音/方言**：训练数据覆盖不足的口音。
- **代码切换**（code-switching）：中英混说、印地语-英语混说。
- **儿童语音**：音高和共振峰与成人差异大，数据少。
- **零样本新词**：人名、专业术语、新造词。

---

## 6. 一张图总结 ASR 演化

```
1980s-2010s          2006           2014-2016          2020              2022+
HMM-GMM              CTC            LAS (Attention)    Conformer         Whisper
  │                   │                │                 │                 │
  │ 拆成声学+语言      │ blank+折叠     │ cross-attention │ CNN+Attn混合     │ 68万小时
  │ 各训各的           │ 条件独立       │ 隐含LM          │ SOTA精度         │ 暴力scale
  │ Viterbi解码        │ 需外接LM       │ 不能流式         │ 达人类水平       │ 多语言统一
  ▼                   ▼                ▼                 ▼                 ▼
精度低               精度中           精度高            精度极高           精度高+通用
流水线复杂           端到端但需LM      端到端            端到端             端到端
                     能流式            不能流式          工程折中流式       不能流式
```

**核心趋势**：从"手工拆分 + 各部件最优"到"端到端 + 整体最优"，再到"数据驱动 + 架构淡化"。**和 NLP 从 pipeline NER→Parser→MT 到 LLM 的演化完全同构。**

---

## 📌 下一步

- **Ch 16 语音合成 (TTS)**：ASR 的逆问题——从文字生成语音。你会发现 encoder-decoder 架构几乎对称。
- **附录 A 隐马尔可夫模型**：CTC 的动态规划本质是 HMM forward 算法的变体，深度理解 CTC 需要先吃透 HMM。
- **Ch 13 RNN/LSTM**：CTC 和 LAS 的 encoder 历史上都是 RNN，理解 LSTM 对理解早期 ASR 论文必要。

## ✍️ 练习

**练习 15.1**（CTC 对齐计数）：对于目标序列 "AB" 和输入长度 T=4，手动列出所有合法的 CTC 对齐路径（使用 blank=`-`）。提示：合法路径必须保持 A 在 B 前面，且 A 和 B 之间不能没有 blank（否则折叠不了，除非 AA...AB...B 但那会合并）。答案应该有 6 条。

**练习 15.2**（blank 的必要性）：修改 `15_ctc_decode.py`，在 greedy decode 中**不做 blank 处理**（直接每帧 argmax），看看输出变成什么样。你会理解为什么"去掉 blank，CTC 就崩了"。

**练习 15.3**（beam width 实验）：在实验脚本中把 beam width 从 1 增加到 50，画一张 WER（字符错误率）随 beam width 变化的曲线。你会看到收益迅速递减——**这是 CTC 条件独立假设的数学必然**。

**练习 15.4**（LM rescoring 的威力）：实现一个极简的字符级 bigram LM（用随机生成的转移矩阵模拟），对 beam search 的候选做 rescoring。对比 greedy / beam / beam+LM 三者的准确率，量化"语言知识比解码算法重要多少"。

**练习 15.5**（思考题）：RNN-T 和 CTC 的区别是什么？为什么 RNN-T 能流式而 LAS 不能？用一句话概括"流式 ASR 需要满足什么数学条件"。

---

> 配套实验：`experiments/15_ctc_decode.py`。姊妹章节：`14-语音学与特征提取.md`（上游特征提取）、`16-语音合成-TTS.md`（下游逆问题）、`appendix/A-隐马尔可夫模型.md`（HMM 深度推导）。
