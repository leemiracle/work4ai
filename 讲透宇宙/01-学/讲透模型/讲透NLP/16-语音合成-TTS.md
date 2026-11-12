# 16 — 语音合成 TTS：从共振峰到声音克隆

> 让计算机"说话"。从 1961 年 Bell Labs 的电路共振峰合成器，到 2023 年用 3 秒音频克隆任意人声——TTS 的六十年演化，是 AI 从"手动调参"到"端到端学习"的完美缩影。
>
> 配套实验：`experiments/16_formant_tts.py` — 用 NumPy + stdlib `wave` 实现最简单的共振峰合成器，合成 /a/ /i/ /u/ 三个元音。**反直觉发现**：3 个共振峰频率 + 1 个脉冲源 = 可辨别的元音。

---

## 目录

- [0. 这章在讲什么](#0-这章在讲什么)
- [1. 直觉：让计算机"说话"](#1-直觉让计算机说话)
- [2. 前端：从文本到语言学特征](#2-前端从文本到语言学特征)
- [3. 声学模型：从音素到频谱](#3-声学模型从音素到频谱)
- [4. 声码器：从频谱到波形](#4-声码器从频谱到波形)
- [5. VITS：端到端 TTS](#5-vits端到端-tts)
- [6. Zero-shot 声音克隆](#6-zero-shot-声音克隆)
- [7. 中文 TTS 特殊问题](#7-中文-tts-特殊问题)
- [8. 批判性视角](#8-批判性视角)
- [📌 下一步](#-下一步)
- [✍️ 练习](#-练习)

---

## 0. 这章在讲什么

TTS（Text-to-Speech）是 ASR 的逆问题：

| | ASR (Ch 15) | TTS (Ch 16) |
|---|---|---|
| 输入 | 语音波形 | 文本字符串 |
| 输出 | 文本字符串 | 语音波形 |
| 难点 | 一个音对应多个可能词（歧义） | 一段文对应无数种可能的说话方式（一多映射） |
| 数据 | 多说话、大语料、speaker-independent | 单说话人、小语料、speaker-dependent |
| 典型数据量 | 数千小时 | 24 小时（LJ Speech） |

> **ASR 是"多对一"——多种声音 → 同一段文字；TTS 是"一对多"——同一段文字 → 无数种声音。** 这从根本决定了两个任务的技术路线不同。

SLP3 Ch 16 的结构是按历史顺序展开的：拼接合成 → HMM 参数合成 → 神经 TTS（Tacotron/FastSpeech）→ 神经声码器（WaveNet/HiFi-GAN）→ 端到端（VITS）→ 声音克隆（VALL-E）。你能看到每一代解决了什么、遗留了什么。

---

## 1. 直觉：让计算机"说话"

### 1.1 语音产生的 source-filter 模型

理解 TTS 的第一把钥匙不是任何神经网络，而是 Fant（1960）的**源-滤波模型**（source-filter model）：

```
  人发声 = 声源(声带振动) → 声道(口腔/鼻腔) → 嘴唇辐射

  信号视角:   s(t) = e(t) * v(t) * r(t)
  频域视角:   S(f) = E(f) · V(f) · R(f)

  其中:
    e(t) / E(f) = 声门激励 (浊音: 周期脉冲串; 清音: 白噪声)
    v(t) / V(f) = 声道传递函数 (共振峰 F1, F2, F3, ...)
    r(t) / R(f) = 嘴唇辐射 (~ +6dB/oct 高频提升)
```

**核心洞察**：声道像一个可变滤波器。你发不同元音时，舌头位置变了 → 声道形状变了 → 共振频率（formant）变了 → 听感变了。**但声源（声带振动）几乎不变——它的基频 f0 决定音高，不决定"是哪个元音"。**

```
  元音差异 = 共振峰频率差异 (F1, F2, F3)

  /a/ (ah):  F1=730   F2=1090  F3=2440   ← 低F1+低F2
  /i/ (ee):  F1=270   F2=2290  F3=3010   ← 低F1+高F2
  /u/ (oo):  F1=300   F2=870   F3=2240   ← 低F1+低F2但F2更低
```

> **★ 反直觉**：你不需要精确模拟整个声道形状。只需要 3 个共振峰频率 + 1 个脉冲源 = 可辨别的元音。这就是我们实验 `16_formant_tts.py` 要验证的。

### 1.2 六十年简史

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                        TTS 技术六十年演化                              │
  ├──────────┬──────────────────┬────────────────┬───────────────────────┤
  │ 年代      │ 方法              │ 代表系统        │ 质量                  │
  ├──────────┼──────────────────┼────────────────┼───────────────────────┤
  │ 1961     │ 共振峰合成        │ Bell Labs      │ 机器声，但可懂        │
  │ 1980s    │ Diphone 拼接     │ MITalk/DECtalk │ 自然度↑但机械         │
  │ 1990s    │ Unit Selection   │ AT&T Natural   │ 很自然但有拼接痕      │
  │ 2000s    │ HMM 参数合成      │ HTS (HTS2005)  │ 灵活但闷              │
  │ 2016     │ WaveNet          │ DeepMind       │ ★质量飞跃(慢)        │
  │ 2017     │ Tacotron 2       │ Google         │ ★接近真人(端到端)     │
  │ 2019     │ FastSpeech 2     │ Microsoft      │ ★快270×+鲁棒          │
  │ 2020     │ HiFi-GAN         │ Kakao          │ ★实时+高质量          │
  │ 2021     │ VITS             │ Kakao          │ ★端到端单模型         │
  │ 2023     │ VALL-E           │ Microsoft      │ ★3秒克隆任意人声      │
  └──────────┴──────────────────┴────────────────┴───────────────────────┘
```

每一代的**核心驱动问题**：

| 驱动 | 从→到 | 为什么 |
|------|-------|--------|
| 可懂度 | 无→共振峰合成 | 解决"能不能听懂" |
| 自然度 | 共振峰→拼接合成 | 解决"听起来像不像人" |
| 灵活性 | 拼接→HMM 合成 | 解决"能不能变声调/语速/情感" |
| 质量 | HMM→神经 TTS | 解决"闷/机械"的"罐头感" |
| 速度 | Tacotron→FastSpeech | 解决"生成一句话要几秒" |
| 泛化 | 多说话人→Zero-shot 克隆 | 解决"每个声音都要重训" |

### 1.3 现代 TTS 的三段式管线

2017–2022 年的主流 TTS 系统都是**级联管线**（cascaded pipeline）：

```
  ┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐
  │  文本    │ ──→ │   前端        │ ──→ │  声学模型  │ ──→ │  声码器   │ ──→ 波形
  │  "Hello" │     │ Frontend     │     │ Acoustic  │     │ Vocoder  │
  └──────────┘     └──────────────┘     └──────────┘     └──────────┘
                    文本正则化            mel 频谱图        波形采样
                    G2P 音素转换          80 维 × T 帧      1 维 × N 样本
                    韵律预测
```

三个阶段的分工：

| 阶段 | 输入 → 输出 | 本质任务 | 代表方法 |
|------|------------|---------|---------|
| **前端** | "Hello world" → `["HH","AH","L","OW",...]` | 文字 → 音素 + 韵律 | 规则 + 序列模型 |
| **声学模型** | 音素序列 → mel 频谱图 (T×80) | 语言学特征 → 声学特征 | Tacotron 2 / FastSpeech 2 |
| **声码器** | mel 频谱图 → 波形 (N×1) | 频域 → 时域（补回相位/声源细节） | Griffin-Lim / WaveNet / HiFi-GAN |

> **为什么中间用 mel 频谱图而不直接波形？** 因为 mel 频谱图是 80 维/帧（每 12.5ms 一帧），而波形是 16000 维/秒。80 维 >> 16000 维的降维比 = 200×，让声学模型从"预测每个波形采样"的噩梦变成"预测每帧的低维特征向量"。

下面三节分别拆解这三个阶段。

---

## 2. 前端：从文本到语言学特征

前端（frontend）是 TTS 管线的第一步，也是传统语音学和自然语言处理的交叉点。它的任务是把**原始文本**变成**语言学特征序列**。

### 2.1 文本正则化（text normalization）

原始文本里有大量非标准词（non-standard words, NSW），需要先转成可发音的文字：

| 原始文本 | 正则化后 | 问题类型 |
|---------|---------|---------|
| `$3.50` | three dollars fifty cents | 货币 |
| `1/2` | a half | 分数 |
| `Jan 1` | January first | 日期缩写 |
| `100°C` | one hundred degrees Celsius | 单位 |
| `Dr. Smith` | Doctor Smith | 缩写 |
| `2026` | twenty twenty-six (年份) / two thousand twenty-six | 歧义！ |
| `12:30` | twelve thirty | 时间 |
| `U.S.A.` | U S A | 首字母 |

> **难点不是规则本身，而是歧义**：`1/2` 在食谱里是"a half"，在日期里是"January second"，在体育比分里是"one to two"。商业 TTS 系统在这上面花了大量工程。

### 2.2 分词（tokenization）

正则化后的文本需要切成 TTS 的输入单元。两种选择：

1. **字符级（character-level）**：`"hello"` → `['h','e','l','l','o']`
   - Tacotron 2 默认用字符
   - 优点：词表极小（~70 个）；缺点：序列长
2. **音素级（phoneme-level）**：`"hello"` → `['HH','AH','L','OW']`
   - FastSpeech 2 默认用音素
   - 优点：消除"同一字母不同发音"的歧义；缺点：需要 G2P

> **趋势**：现代系统越来越多用 **音素输入**，因为字符到发音的映射太不规则（英语尤其严重：`read` 可以是 /ɹiːd/ 也可以是 /ɹɛd/）。

### 2.3 G2P：字位→音素（grapheme-to-phoneme）

G2P 的任务是把文字转成音素序列。这是前端的**核心技术难点**。

**方法一：基于规则（rule-based）**

英语有数千条拼读到发音的规则（如"e 在词尾让前元音发长音"）。经典系统如 CMUdict（词典）+ 规则兜底：

```
  规则示例 (英语):
    "c" + "e/i/y" → /s/    (city, cent, cycle)
    "c" + 其他     → /k/    (cat, cut)
    "gh" 词中     → /ɡ/ 或不发音 (ghost vs through)
    元音+r+e      → 长元音+r   (here, fire, more)
```

**方法二：统计模型（统计 G2P）**

用联合序列模型（joint-sequence model），把字母和音素的对齐建模成一个有限状态自动机：

$$P(\text{phonemes} | \text{letters}) = \sum_{\text{alignments}} P(\text{align})$$

经典方法：Phonetisaurus（基于 WFST 的 n-gram 模型）。

**方法三：神经网络 G2P**

用序列到序列模型（BiLSTM 或 Transformer）直接从字符序列生成音素序列：

$$\text{phoneme}_t = \text{argmax}_p \, P(p | \text{phoneme}_{<t}, \text{chars})$$

> **G2P 的真正挑战是歧义消解**（homograph disambiguation）。见 § 2.5。

### 2.4 韵律预测（prosody prediction）

韵律（prosody）是"声音中的旋律"——音高（F0 轮廓）、时长、能量。它们决定了一句话"听起来是陈述还是疑问""是愤怒还是平静"。

```
  韵律三要素:
    F0 (基频轮廓):   声带振动频率随时间变化 → 音高
    Duration:        每个音素的持续时间 → 节奏
    Energy:          每帧的能量 → 重音/轻读

  例: "你吃饭了吗？"
    陈述: F0 在句末下降  ↘
    疑问: F0 在句末上升  ↗
    愤怒: 整体 F0 升高 + 能量增大 + 语速快
```

韵律预测通常是一个**序列标注**任务：给定音素序列，预测每个音素的持续时间和 F0 目标值。可以用 HMM、DNN 或 Transformer。

> **★ 关键认知**：韵律信息在 mel 频谱图中**隐式存在**——声学模型通过学习频谱模式间接编码了韵律。FastSpeech 2 把 F0、时长、能量作为**显式条件**输入（variance adaptor），使韵律可控制。

### 2.5 同形异音消解（homograph disambiguation）

这是 G2P 最难的子问题：**同一个拼写，不同语境下不同发音**。

| 单词 | 语境 A | 语境 B |
|------|--------|--------|
| `read` | /ɹiːd/ (现在时) | /ɹɛd/ (过去时) |
| `live` | /lɪv/ (动词) | /laɪv/ (形容词 "live broadcast") |
| `record` | /ˈɹɛkɚd/ (名词) | /ɹɪˈkɔɚd/ (动词) |
| `present` | /ˈpɹɛzənt/ (名词) | /pɹɪˈzɛnt/ (动词) |
| `use` | /juːs/ (名词) | /juːz/ (动词) |

**方法**：词性标注（POS tagging）+ 规则/分类器。如 `record` 作为名词重音在第一音节，作为动词重音在第二音节。

> 中文的多音字问题更严重，见 § 7.1。

---

## 3. 声学模型：从音素到频谱

声学模型是 TTS 管线的核心——把语言学特征序列变成 mel 频谱图。这是 TTS 质量飞跃的关键。

### 3.1 中间表示：Mel 频谱图

几乎所有现代 TTS 系统都用 **log-mel 频谱图**（log-mel spectrogram）作为中间表示。

**Mel 尺度**：人耳对频率的感知不是线性的，而是近似对数的：

$$\text{mel}(f) = 2595 \cdot \log_{10}\left(1 + \frac{f}{700}\right)$$

```
  线性频率 700Hz → mel 尺度: 1000 mel
  线性频率 1400Hz → mel 尺度: 1500 mel  (不是 2000!)
  
  → 低频被"拉宽", 高频被"压缩" → 模拟人耳分辨率
```

**Mel 频谱图的计算**：

$$X_{\text{mel}}(m, k) = \log\left(\sum_{f} |X(m, f)|^2 \cdot H_k(f)\right)$$

其中：
- $|X(m, f)|^2$ 是第 $m$ 帧的功率谱（STFT 结果）
- $H_k(f)$ 是第 $k$ 个 mel 滤波器（三角窗，中心频率等距分布在 mel 尺度上）
- $k = 1, \ldots, 80$（典型：80 个 mel bin）

**Tacotron 2 的参数**：50ms 帧长（window size），12.5ms 帧移（hop size），Hann 窗，80 通道 mel 滤波器（125Hz–7600Hz），log 动态范围压缩。

> **为什么用 mel 而不是线性频谱？** 因为 mel 尺度更接近人耳感知——低频分辨率高（人耳对低频敏感），高频分辨率低（人耳对高频相对不敏感）。用 mel 表示意味着模型不需要"浪费"维度在高频细节上。

### 3.2 Tacotron 2：自回归声学模型

**Tacotron 2**（Shen et al., 2018）是神经 TTS 的里程碑——第一个达到接近真人质量的端到端 TTS 系统。

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                    Tacotron 2 架构                                    │
  │                                                                       │
  │  字符序列 → [字符Embedding] → [3×Conv1D] → [BiLSTM] → 编码器隐层 h    │
  │                                                                       │
  │                    ↓ location-sensitive attention                     │
  │                                                                       │
  │  [Pre-net(瓶颈)] → [2×LSTM] → [Linear→80维] → mel帧_t                │
  │       ↑                    ↑                                          │
  │  mel帧_{t-1}         attention context                               │
  │                                                                       │
  │  mel帧_t → [Post-net(5×Conv)] → mel帧_t (残差修正)                   │
  │  mel帧_t → [Linear→sigmoid] → stop token (是否结束)                   │
  └─────────────────────────────────────────────────────────────────────┘
```

**编码器（Encoder）**：
1. 字符嵌入：每个字符 → 512 维向量
2. 3 层 Conv1D（512 滤波器，核宽 5）——建模局部上下文（类似 N-gram）
3. 1 层 BiLSTM（512 单位）——双向编码

**注意力（Attention）**：location-sensitive attention（位置敏感注意力）

$$\alpha_{t,i} = \frac{\exp(e_{t,i})}{\sum_j \exp(e_{t,j})}$$

$$e_{t,i} = \text{score}(s_{t-1}, h_i) + \sum_{j} \alpha_{t-1,j} \cdot F_{i-j}$$

其中 $F$ 是一个卷积滤波器，把上一步的注意力权重 $\alpha_{t-1}$ 变成"位置特征"。**这让注意力"知道自己在输入的什么位置"，鼓励单调推进**，防止跳词或重复。

**解码器（Decoder）**——自回归：
1. 上一帧 mel 谱 → Pre-net（2 层全连接 256→瓶颈 256）——信息瓶颈帮助注意力学习
2. Pre-net 输出 + attention context 拼接 → 2 层 LSTM（1024 单位）
3. LSTM 输出 → Linear → 80 维 mel 帧（预测当前帧）
4. Post-net（5 层 Conv）→ 残差修正（细化预测）
5. Stop token 预测（sigmoid）——决定何时停止生成

> **自回归的代价**：生成一句 2 秒的话，mel 频谱图有 160 帧，需要 160 步串行解码 → 慢。

### 3.3 FastSpeech 2：非自回归声学模型

FastSpeech（Ren et al., 2019）和 FastSpeech 2（Ren et al., 2020）解决了 Tacotron 的两大痛点：**慢**和**不鲁棒**。

```
  ┌───────────────────────────────────────────────────────────────────┐
  │                    FastSpeech 2 架构                               │
  │                                                                     │
  │  音素序列 → [字符Embedding] → [音素Positional Encoding]           │
  │           → [Encoder: N×FFT Block(自注意力+FFN)]                   │
  │                                                                     │
  │           → [Variance Adaptor]                                     │
  │              ├─ Duration Predictor → Length Regulator (时长扩展)    │
  │              ├─ Pitch Predictor → F0 条件                           │
  │              └─ Energy Predictor → 能量条件                         │
  │                                                                     │
  │           → [Decoder: N×FFT Block] → 80维mel帧 (全部并行输出)      │
  └───────────────────────────────────────────────────────────────────┘
```

**核心创新 1：Length Regulator（长度调节器）**

Tacotron 用 attention 决定"每个音素占多少帧 mel"——这是隐式的。FastSpeech 用**显式的时长预测器**（duration predictor）：

$$d_i = \text{DurationPredictor}(\text{encoder output}_i)$$

然后把第 $i$ 个音素的特征**复制** $d_i$ 次：

```
  音素:    "HH"  "AH"  "L"  "OW"
  时长:      3     2    1     4
  展开:  HH HH HH AH AH L OW OW OW OW
         ←── frame 0-2 ──→        ←── frame 7-10 ──→
```

**关键**：展开后，所有帧可以**同时**送入 decoder → 完全并行，无需自回归！

**核心创新 2：Variance Adaptor（方差适配器）**

FastSpeech 2 在时长之外，还显式预测 **F0（音高）** 和 **energy（能量）**：

```
  encoder output → duration predictor → 展开后的特征
                 → pitch predictor → F0 embedding (加到特征上)
                 → energy predictor → energy embedding
```

这让用户可以**精确控制**：
- 调整 duration → 改变语速
- 调整 pitch → 改变情感（升调=兴奋/疑问）
- 调整 energy → 改变重音

**核心创新 3：无需 attention**

FastSpeech **完全没有 attention 机制**——时长预测器取代了 attention 的对齐功能。这消除了 Tacotron 的两个致命问题：

| 问题 | Tacotron (attention-based) | FastSpeech (duration-based) |
|------|---------------------------|----------------------------|
| 慢 | 160 帧串行解码 | 全部并行 |
| 跳词/重复 | attention 偶尔"迷路" | 时长预测确定性强 |
| 不可控 | 无法指定语速/音高 | 显式 duration/pitch/energy |

> **★ 速度对比**：FastSpeech 的 mel 生成比 Tacotron 快 **270×**，最终波形生成快 **38×**。

### 3.4 自回归 vs 非自回归

| 维度 | 自回归 (Tacotron 2) | 非自回归 (FastSpeech 2) |
|------|-------------------|----------------------|
| 生成方式 | 一帧一帧预测 | 全部帧同时生成 |
| 速度 | 慢（O(T) 串行） | 快（O(1) 并行） |
| 对齐 | attention（隐式） | duration predictor（显式） |
| 鲁棒性 | 可能跳词/重复 | 确定性强 |
| 可控性 | 难以精确控制 | duration/pitch/energy 可调 |
| 质量 | 略高（帧间依赖更细） | 接近（variance adaptor 补偿） |

> **类比**：Tacotron 像一个口述者一字一字念（慢但流畅）；FastSpeech 像一个排字工人（快但需要提前知道每个字占多宽）。工业部署几乎全用 FastSpeech 系。

---

## 4. 声码器：从频谱到波形

声码器（vocoder）是 TTS 管线的最后一步——把 mel 频谱图转回时域波形。这是从**频域表示**到**时域波形**的逆过程。

### 4.1 为什么需要声码器？

Mel 频谱图只包含了**幅度信息**（spectral envelope），丢弃了两样东西：

1. **相位信息**（phase）：STFT 有幅度和相位，mel 只保留了幅度
2. **声源细节**（fine structure）：mel 滤波器把谐波"模糊"了

声码器的任务就是**从 mel 频谱图重建完整的波形**——补回相位和细节。

### 4.2 Griffin-Lim：经典算法

**Griffin-Lim**（Griffin & Lim, 1984）是唯一的**无训练**声码器——纯数学迭代。

**原理**：给定幅度谱 $|X(f)|$，迭代估计最可能的相位 $\phi(f)$，然后用逆 STFT（ISTFT）转回波形。

```
  Griffin-Lim 算法:
    1. 随机初始化相位 φ
    2. 用 |X| 和 φ 做逆 STFT → 波形 x
    3. 对 x 做 STFT → 得到新的 |X'| 和 φ'
    4. 用原始 |X| 和新的 φ' 做逆 STFT → 更好的 x
    5. 重复 3-4 约 60 次
```

**问题**：质量差——声音"金属化""罐头感"。因为 mel 频谱图的信息量太少，纯数学方法恢复的波形有大量伪影。

> Griffin-Lim 现在只用于**快速原型/调试**，商业系统绝不用。

### 4.3 WaveNet：自回归波形生成

**WaveNet**（van den Oord et al., 2016）是声码器的革命——**直接建模每一个波形采样的概率分布**。

```
  WaveNet 的核心公式:
    p(x_t | x_1, ..., x_{t-1}, c) = softmax(f(x_{t-1}, x_{t-2}, ..., c))

  其中:
    x_t = 第 t 个波形采样 (16-bit, 或 mu-law 量化为 256 类)
    c   = 条件信息 (mel 频谱图上采样到采样率)
    f   = 因果膨胀卷积网络 (causal dilated convolution)
```

**膨胀因果卷积（dilated causal convolution）**：

```
  因果: 只看过去 (x_{t-k}, k>0), 不看未来
  膨胀: 跳跃采样, 指数扩大感受野

  层 0 (dilation=1):   x[t] ← x[t-1]                感受野 = 2
  层 1 (dilation=2):   x[t] ← x[t-2]                感受野 = 4
  层 2 (dilation=4):   x[t] ← x[t-4]                感受野 = 8
  层 3 (dilation=8):   x[t] ← x[t-8]                感受野 = 16
  ...
  层 k (dilation=2^k): x[t] ← x[t-2^k]              感受野 = 2^{k+1}

  → 10 层膨胀卷积, 感受野 = 1024 samples ≈ 64ms @ 16kHz
  → 30 层 = 感受野 ≈ 2^31 samples (理论上覆盖整段音频)
```

> **★ 为什么膨胀卷积如此重要？** 在 16kHz 采样率下，1 秒音频 = 16000 个采样。普通因果卷积要覆盖 1 秒需要 16000 层——不可能。膨胀卷积只需 ~14 层（$2^{14} = 16384$）就能覆盖 1 秒。**指数增长的感受野是 WaveNet 的灵魂。**

**WaveNet 的致命弱点**：极慢。生成 1 秒音频需要 16000 次串行采样 → 在 GPU 上约几分钟。

> 这催生了后续工作：Parallel WaveNet（蒸馏加速）、WaveRNN（轻量化）、LPCNet（结合线性预测）。

### 4.4 HiFi-GAN：GAN 声码器

**HiFi-GAN**（Kong et al., 2020）是声码器的**速度与质量兼顾**的突破——用 GAN 做并行波形生成。

```
  HiFi-GAN 三部分:

  1. Generator (生成器 G):
     mel频谱图 → [转置卷积上采样] → [Multi-Receptive Field Fusion] → 波形

     上采样: 把 80维/12.5ms帧 → 1维/采样 (上采样 ~128×)
     MRF:    多个不同膨胀率的残差块并行 → 融合

  2. Multi-Period Discriminator (MPD):
     把波形 reshape 成不同周期 → 每个周期独立判别
     (捕捉波形在不同时间尺度上的结构)

  3. Multi-Scale Discriminator (MSD):
     在不同下采样率上判别波形
     (捕捉不同频率分辨率上的真实性)
```

**训练目标**（GAN loss + 辅助 loss）：

$$\mathcal{L}_G = \underbrace{\sum_k \mathcal{L}_{\text{adv}}(D_k, G)}_{\text{对抗损失}} + \lambda_{\text{fm}} \underbrace{\sum_k \mathcal{L}_{\text{fm}}(D_k, G)}_{\text{特征匹配}} + \lambda_{\text{mel}} \underbrace{\mathcal{L}_{\text{mel}}(G)}_{\text{mel L1}}$$

- $\mathcal{L}_{\text{adv}}$：让判别器无法区分真实/生成波形
- $\mathcal{L}_{\text{fm}}$（feature matching）：让生成器中间特征接近真实——稳定 GAN 训练
- $\mathcal{L}_{\text{mel}}$：让生成波形的 mel 频谱接近输入 mel——保证内容正确

> **★ 速度对比**：HiFi-GAN 比 WaveNet 快 **数千倍**——WaveNet 生成 1 秒音频需要几分钟，HiFi-GAN 在普通 GPU 上 **实时**（RTF < 1，real-time factor < 1）。

### 4.5 声码器对比

| 声码器 | 年份 | 类型 | 速度 | 质量 | 训练复杂度 |
|--------|------|------|------|------|-----------|
| Griffin-Lim | 1984 | 迭代 | 快 | 差（金属化） | 无需训练 |
| WaveNet | 2016 | 自回归 | ★极慢 | ★极好 | 高 |
| WaveRNN | 2018 | 自回归(轻量) | 慢 | 好 | 中 |
| WaveGlow | 2019 | 归一化流 | 中 | 好 | 高 |
| HiFi-GAN | 2020 | GAN | ★实时 | ★极好 | 中 |
| VITS vocoder | 2021 | 流+GAN | ★实时 | ★极好 | 中 |

> **2024+ 的共识**：HiFi-GAN 和 VITS 的声码器组件统治了工业部署。WaveNet 系列因速度问题已退出实用。

---

## 5. VITS：端到端 TTS

### 5.1 为什么端到端？

前面的级联管线有一个根本问题：**声学模型和声码器分别训练**。

```
  级联训练:
    Step 1: 训练声学模型 (音素 → mel频谱图), 用真实mel做监督
    Step 2: 训练声码器   (mel频谱图 → 波形),   用真实mel+真实波形做监督

  问题: 推理时, 声学模型输出的mel ≠ 训练mel的分布
       → 声码器遇到"没见过的mel" → 质量下降
       → 误差累积 (error propagation)
```

VITS（Kim et al., 2021）把两步合成**一个模型**——直接从音素到波形，端到端联合优化。

### 5.2 VITS 架构

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                          VITS 架构                                    │
  │                                                                        │
  │  ┌─ Encoder ─┐         ┌── Variational ──┐        ┌── Flow ──┐       │
  │  │ 音素→隐层  │ → 对齐 → │ z ~ q(z|x_audio)│ → f(z) → │ w = f(z) │       │
  │  └───────────┘         │ (后验采样)       │         └────┬─────┘       │
  │                        └─────────────────┘              │              │
  │                                                         ↓              │
  │                            ┌── Generator ──────────────────┐           │
  │                            │ 波形 ← mel特征 ← z_prior       │           │
  │                            └──────────┬────────────────────┘           │
  │                                       ↓                                  │
  │                   ┌─────── Discriminators ──────┐                      │
  │                   │ MPD (多周期) + MSD (多尺度)   │                      │
  │                   └─────────────────────────────┘                      │
  └──────────────────────────────────────────────────────────────────────┘
```

**VITS 的三重创新**：

**创新 1：变分后验编码器（variational posterior encoder）**

训练时，VITS 从**真实音频**中提取一个隐变量 $z$：

$$z \sim q_\phi(z | x_{\text{audio}}) = \mathcal{N}(\mu_\phi, \sigma_\phi)$$

这让模型学到"音频中有哪些变异"（说话人、情感、呼吸声等），而不是把它们丢掉。

**创新 2：归一化流（normalizing flow）**

用可逆变换 $f$ 把隐变量 $z$ 映射到波形域：

$$w = f_\theta(z), \quad z = f_\theta^{-1}(w)$$

流保证变换可逆，使对数似然可以精确计算。

**创新 3：对抗训练 + 变分推断联合优化**

$$\mathcal{L}_{\text{VITS}} = \underbrace{\mathcal{L}_{\text{adv}}}_{\text{GAN}} + \lambda \underbrace{\mathcal{L}_{\text{fm}}}_{\text{特征匹配}} + \underbrace{\mathcal{L}_{\text{ELBO}}}_{\text{变分下界}} + \underbrace{\mathcal{L}_{\text{dur}}}_{\text{时长预测}}$$

> **VITS 的意义**：一个模型、一次训练、端到端优化。不再有"mel 频谱分布不匹配"的误差累积问题。质量与 Tacotron 2 + HiFi-GAN 相当，但推理更简单。

---

## 6. Zero-shot 声音克隆

### 6.1 问题定义

传统 TTS 系统**为每个说话人单独训练**——你想合成张三的声音，就需要张三录几十小时音频。这在工程上极度受限。

**Zero-shot TTS** 的目标：给模型 **3 秒钟**的目标说话人音频，就能用那个人的声音合成**任意**文本。

```
  输入: 3秒注册音频 (enrollment) + 目标文本
  输出: 目标说话人声音念目标文本的波形
```

> **这本质上是"声音版的 few-shot learning"**——跟 LLM 的 in-context learning 完全一致。

### 6.2 VALL-E：TTS 作为条件语言模型

**VALL-E**（Wang et al., 2023，Microsoft）是 SLP3 2026 版新增的重点内容——**把 TTS 变成语言建模任务**。

**关键思想**：用神经音频编解码器（neural audio codec，如 EnCodec）把波形变成**离散 token 序列**，然后像 LLM 一样建模。

```
  VALL-E 流程:

  Step 1: 神经音频编解码 (EnCodec/SoundStream)
    波形 → [编码器] → 离散token矩阵 C ∈ ℤ^{T×K}
    (T帧, K个量化器, 每帧K个离散码)

  Step 2: 条件 codec 语言建模
    给定: 注册音频的codec码 C_prompt + 目标文本 x
    生成: 目标音频的codec码 C_target

    P(C_target | x, C_prompt) = 自回归LLM
```

**层级结构（Hierarchical: AR + NAR）**：

RVQ（Residual Vector Quantization）产生的多码本有一个层级结构：第一个量化器包含最主要的声学信息，后续量化器包含残差细节。VALL-E 利用这个结构：

| 模型 | 生成方式 | 作用 |
|------|---------|------|
| AR（自回归）模型 | 串行生成第一个码本 $c_{:,0}$ | 预测音频长度和内容（质量高但慢） |
| NAR（非自回归）模型 | 并行生成剩余码本 $c_{:,1}, \ldots, c_{:,K-1}$ | 补充声学细节（快） |

**AR 模型用因果 attention（causal mask），NAR 模型用全 attention（full mask）**——与 GPT/BERT 的关系完全对应。

> **★ VALL-E 的本质洞察**：TTS ≈ 条件语言建模。把"从文本生成波形"变成"从文本+提示生成离散 token"——和 ChatGPT 从提示生成文本 token 完全同构。LLM 的所有技术（few-shot prompting、in-context learning、scaling）可以直接迁移到语音。

**训练数据**：LibriHeavy（LibriLight 的标注版），50K 小时英语，7000+ 说话人。远超传统 TTS 的 24 小时单说话人数据。

### 6.3 NaturalSpeech 3

NaturalSpeech 3（Ju et al., 2024）走了不同的路线——**分解语音的各个因子**（factorization）：

```
  语音 = 语音内容(prosody) + 音色(timbre) + 音高(pitch) + 节奏(rhythm)

  NaturalSpeech 3 分别编码:
    内容: speech codec tokens
    音色: 全局说话人向量 (speaker embedding)
    音高: F0 轨迹
    节奏: 时长序列

  → 可以单独替换任意因子 (如换音色=声音克隆, 换音高=情感控制)
```

这比 VALL-E 的"全部塞进一个 LLM"更有控制力。

### 6.4 产业影响与伦理

Zero-shot 声音克隆正在**颠覆 TTS 产业**：

| 变化 | 从 | 到 |
|------|----|----|
| 录音成本 | 每个声音录几十小时 | 3 秒样本 |
| 开发周期 | 每个声音训练数天 | 几秒推理 |
| 个性化 | 不可能 | 任意用户自定义声音 |
| 有声书 | 配音演员逐本录 | 批量克隆名优声音 |

**伦理风险**：
- **深度伪造语音诈骗**：2024 年已有用 AI 克隆 CEO 声音骗走 $243K 的案例
- **身份冒用**：用名人声音做未授权广告/政治言论
- **版权**：声音是否受版权保护？目前法律灰区

> SLP3 在这一节明确讨论了伦理问题——这是少有的教材主动讨论技术风险的章节。

---

## 7. 中文 TTS 特殊问题

中文 TTS 面临英文 TTS 没有的几个独特挑战。SLP3 以英语为主，这里补充中文视角。

### 7.1 多音字（polyphonic character）

中文有大量**一字多音**，G2P 必须根据上下文消歧：

| 字 | 读音 A | 例词 A | 读音 B | 例词 B |
|----|--------|--------|--------|--------|
| 行 | xíng | 行走/银行(错误!) | háng | 银行/行列 |
| 长 | cháng | 长短 | zhǎng | 生长/长辈 |
| 重 | zhòng | 重要 | chóng | 重复 |
| 了 | le | 好了 | liǎo | 了解 |
| 得 | dé | 得到 | děi | 得去 |
| 乐 | lè | 快乐 | yuè | 音乐 |

**特别注意**："银行" = yínháng，不是 yínxíng；"行李" = xíngli，不是 hángli。

> **消歧方法**：中文多音字消歧本质是一个**序列分类**任务——给定上下文（词/词性/前后字），预测每个多音字的读音。BiLSTM-CRF 或 BERT 系模型是当前主流。现代系统通常直接用词表查表 + 模型消歧兜底。

### 7.2 轻声（neutral tone）

普通话四声（阴平/阳平/上声/去声）之外，还有**轻声**——某些字在特定位置失去原声调，读得又轻又短：

| 词语 | 原调 | 实际读法 |
|------|------|---------|
| 妈妈 | mā mā | mā ma (第二个"妈"变轻声) |
| 桌子 | zhuō zǐ | zhuō zi ("子"变轻声) |
| 看了 | kàn le | kàn le ("了"变轻声) |
| 我们 | wǒ mén | wǒ men ("们"变轻声) |

轻声没有固定 F0，其音高由前一个字的声调决定。这给韵律预测带来了复杂性。

### 7.3 儿化（erhua）

北京话的儿化音——在词尾加 /ɚ/ 尾音，同时前面的元音可能发生变化：

| 原词 | 儿化后 | 音变 |
|------|--------|------|
| 小孩 | 小孩儿 | háir → /xaɪɚ/ |
| 花儿 | — | huār → /huɐɚ/ |
| 冰棍 | 冰棍儿 | gùnr → /kuɚ/ |

**TTS 处理**：前端需要识别儿化标记（"儿"字或"r"后缀），在 G2P 阶段将主元音和 /ɚ/ 合并。

### 7.4 句调（sentence intonation）

中文是声调语言（tone language）——每个字有自己的声调。但在句子层面，声调会受**句调**调制：

```
  陈述句 "他明天来" → 整体 F0 轮廓略降 (↘)
  疑问句 "他明天来？" → 句末 F0 上升 (↗), 尤其最后一个字
  感叹句 "太好了！" → 整体 F0 升高, 能量增大

  关键: 句调 × 字调 的叠加
    字调决定微观 F0 形状 (如三声"来"=降升)
    句调决定宏观 F0 趋势 (升降)
    两者叠加, 不是简单相加, 有复杂的调制关系
```

> 中文 TTS 的韵律建模比英文难——因为字调和句调要同时处理，不能像英文那样只管句调。

---

## 8. 批判性视角

### 8.1 TTS 被 LLM 收编了吗？

**部分是。** VALL-E 的出现证明 TTS 可以被重新表述为条件语言建模：

```
  传统 TTS:    文本 → [前端] → [声学模型] → [声码器] → 波形
  VALL-E:     文本+提示 → [一个 Transformer LLM] → codec码 → 解码 → 波形
```

但 VALL-E 仍然需要**音频编解码器**（EnCodec）作为离散化前端——这不是纯语言模型。而且 VALL-E 的质量在 2026 年仍不如精心调优的级联系统（如 NaturalSpeech 3）。

> **判断**：TTS 正在被 LLM 技术栈**渗透**（discrete token + LLM），但"纯 LLM 做 TTS"还没有完全取代专用管线。类似 ASR：Whisper 用 Transformer 但不是纯 LLM。

### 8.2 级联管线 vs 端到端

| | 级联 (Tacotron 2 + HiFi-GAN) | 端到端 (VITS) | LLM-based (VALL-E) |
|---|---|---|---|
| 质量 | ★最高（各阶段精调） | ★高 | 中（zero-shot 泛化换取） |
| 速度 | 中（两阶段） | 快（单模型） | 慢（AR + 大模型） |
| 部署复杂度 | 高（两个模型） | 低（一个模型） | 高（需要 codec + LLM） |
| 可控性 | 中（FastSpeech 2 可控） | 中 | 低（黑盒） |
| zero-shot | ✗ | ✗ | ★3秒克隆 |
| 数据需求 | 24h 单说话人 | 24h 单说话人 | 60K h 多说话人 |

> **2026 年现实**：商业部署主力仍是 **FastSpeech 2 + HiFi-GAN**（可控、稳定、实时）。VITS 用于追求极致质量的场景。VALL-E/NaturalSpeech 用于声音克隆/个性化。

### 8.3 评估难题

TTS 评估至今没有统一的**客观指标**——不像 ASR 有 WER，MT 有 BLEU。

| 指标 | 类型 | 问题 |
|------|------|------|
| MOS（Mean Opinion Score） | 主观（人评 1-5 分） | 昂贵、慢、主观偏差 |
| CMOS（Comparison MOS） | 主观（AB 对比） | 只能比较，不绝对 |
| MCD（Mel Cepstral Distortion） | 客观 | 与人感不完全相关 |
| PESQ / STOI | 客观 | 为通信质量设计，非 TTS |

> **根本困难**：TTS 的输出空间是"无数种合理的声音"——没有唯一正确答案。这导致客观指标（MCD）与人感相关性低。**MOS 至今仍是金标准，但贵且慢。**

### 8.4 情感 TTS 的瓶颈

现有 TTS 系统在**中性语音**（neutral speech，如新闻播报）上已接近完美，但在**情感表达**（expressive speech，如演戏、讲故事）上差距巨大：

- **情感标注困难**：训练数据需要人工标注情感类别和强度
- **情感=韵律+音色+语速**的复合：不是调一个 F0 就能解决
- **同一句话多种情感**：同样是"真的吗"，可以是惊讶/愤怒/讽刺/开心——歧义远超文本能携带的信息

> 这是 TTS 的**下一个前沿**——从"能听懂"到"能演好"。2024+ 的研究方向包括参考音频情感迁移（reference-based emotion transfer）和 LLM prompt 控制。

### 8.5 端侧 TTS 的崛起

大模型 TTS（VALL-E）需要数十 GB 参数和大量算力，**不适合手机/嵌入式**。相反，轻量级 TTS（如 VITS 的蒸馏版、FastSpeech 的量化版）正在成为**端侧部署**的主流——让 AI 助手在没有网络的情况下也能说话。

> 这与 LLM 端侧部署趋势一致——不是所有任务都需要云端大模型，TTS 更适合"小而精"的端侧模型。

---

## 📌 下一步

- **回看 Ch 14**（语音学）：共振峰、音素、声学特征——本章前端和声码器的物理学基础
- **回看 Ch 15**（ASR）：TTS 是 ASR 的逆问题——对比两者看语音 AI 的完整图景
- **回看 Ch 8**（Transformer）：VALL-E 把 TTS 变成 Transformer 语言建模——attention 是连接点
- **跳到 Ch 17**（POS 标注）：前端 G2P 中的同形异音消解本质是序列标注——POS/NER 的技术栈直接适用
- **跨系列**：`../讲透生成模型/` — VITS 的变分推断 + 对抗训练是生成模型的核心技术

---

## ✍️ 练习

**练习 16.1（共振峰实验）**：运行 `experiments/16_formant_tts.py`。用任意音频播放器打开生成的 `vowel_a.wav`、`vowel_i.wav`、`vowel_u.wav`。你能听出区别吗？如果听不出，检查 F1/F2 值是否正确。

**练习 16.2（改变基频）**：在实验脚本中，把 `F0 = 120`（男性基频）改成 `F0 = 220`（女性基频）。重新生成元音——你应该听到音高升高，但元音仍然是 /a/ /i/ /u/。**这验证了 source-filter 模型：F0 决定音高，formants 决定元音——两者独立。**

**练习 16.3（共振峰数量）**：修改实验脚本，只用 2 个共振峰（去掉 F3），对比用 3 个共振峰的效果。你应该发现 F3 主要影响"自然度"而非"可懂度"。

**练习 16.4（G2P 思考）**：英语中 `bow` 有两种发音——/baʊ/（弓）和 /boʊ/（鞠躬）。设计一个最小的规则集（不超过 5 条规则）来消歧。提示：考虑词性。

**练习 16.5（架构对比）**：Tacotron 2 用 attention 对齐，FastSpeech 2 用 duration predictor 对齐。用一句话解释：为什么 duration-based 方法消除了"跳词/重复"问题？（提示：考虑 attention 的随机性 vs duration 的确定性。）

**练习 16.6（中文多音字）**：用 Python 写一个最简单的多音字消歧函数——给定一个含"行"的句子和其前后字，返回 xíng 或 háng。你的准确率能达到多少？（测试词：银行、行走、行列、行李、行业、自行车。）

**练习 16.7（声码器选择）**：你被要求为一个手机助手 app 选择 TTS 声码器。设备 CPU 有限，内存 2GB。你会选 Griffin-Lim、WaveNet 还是 HiFi-GAN？给出理由（参考 § 4.5 的速度/质量/复杂度对比表）。

---

> 配套实验：`experiments/16_formant_tts.py`
>
> 姊妹章节：`14-语音学与特征提取.md`（共振峰物理基础）、`15-自动语音识别-ASR.md`（逆问题）
