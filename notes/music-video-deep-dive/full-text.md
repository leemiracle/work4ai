# 音乐 & 视频：全视角深度长文

> 把"音乐"和"视频"用 6 层金字塔讲透：**物理 → 数学/信号 → 神经/感知 → 进化/心理 → 文化 → 工程 → AI 生成**。
> 每层给「直觉 → 数学/算法 → 代码」三层。覆盖所有核心算法。
> 信息日期：2025–2026 视角整理。引用论文用 arXiv ID 或年份标注。

---

## 导论：为什么把音乐和视频放在一起讲？

它们在数学结构、感知机制、工程方法上**共享同一套骨架**：

```
物理世界波动 (空气振动 / 电磁波)
        ↓
感觉换能 (耳蜗基底膜傅里叶 / 视网膜光化学)        ← 生物硬件
        ↓
大脑预测编码 (Predictive Coding / Friston)        ← 认知算法
  音高/调性  ·  运动/光流
        ↓
文化编码系统 (调式-节奏 / 镜头-蒙太奇)              ← 约定俗成
        ↓
采样 → 压缩 (PCM/Opus/EnCodec  ·  H.264/AV1)       ← 工程算法
        ↓
生成模型 (MusicGen/Suno  ·  Sora/Wan/Veo3)         ← AI 前沿
```

**6 层金字塔，6 个视角**。一句话总纲：

> 音乐和视频本质都是**在时间维度上对感知预测的精准把玩**——艺术家玩的是预测误差，工程师玩的是冗余消除，AI 玩的是分布建模。三者指向同一个数学骨架：**信息 + 信号 + 概率**。

---

# 第一篇：音乐 · 物理声学

## 1.1 声音 = 空气的纵波

拨一根弦，你听到的不是弦——是空气被反复推挤。简谐波：

$$x(t) = A \sin(2\pi f t + \varphi)$$

- $A$ 振幅 → 响度（对数感知，SPL dB）
- $f$ 频率 → 音高（对数感知，每翻倍高一个八度）
- $\varphi$ 相位（人耳几乎不敏感）

两个"对数"决定了后续一切：响度用分贝、音高用音分、人耳是个对数仪器。这是 Weber-Fechner 律：感觉强度 ∝ 物理强度的对数——一种让生物能跨越 10⁶ 量程的进化压缩。

## 1.2 泛音列：万物的音色指纹

真实乐器几乎不发出纯正弦。一根弦振动时同时存在 $f, 2f, 3f, \dots$ 的驻波模式（边界条件），这串叫**泛音列（harmonic series）**。

同样的 440 Hz，泛音权重不同 → 音色不同。Helmholtz 1862 定义：音色 = 泛音谱。

**巧合还是必然？** 泛音列的第 2、3、4 项正好是八度、纯五度、再八度——所有文化的协和音程都出现在泛音列前几项里。这预示：协和感是物理 + 生物的交集。

## 1.3 傅里叶：声音的频域等价

$$X(f) = \int_{-\infty}^{\infty} x(t)\, e^{-i2\pi f t}\, dt$$

工程上用 **FFT（Cooley-Tukey 1965）**，$O(N \log N)$。是 20 世纪最重要的算法之一。

但 FFT 假设信号平稳。音乐时变 → 用 **STFT（短时傅里叶）**：滑窗 + FFT。

$$X(t, f) = \int x(\tau)\, w(\tau - t)\, e^{-i2\pi f\tau}\, d\tau$$

窗口大小要做时频权衡（Heisenberg 不确定性原理同样适用）。

## 1.4 MDCT 与 CQT：音频压缩的核心变换

**MDCT（Modified Discrete Cosine Transform, Princen 1987）**：
1. **时域混叠对消（TDAC）**：相邻块重叠 50%，块边界噪声抵消
2. **能量集中**：MP3/AAC/Opus/AC-3 全靠它

**心理声学模型**（MP3 的真正魔法）：
- **同时掩蔽**：强音盖住邻近频率弱音
- **前/后向掩蔽**：强音前几 ms / 后 200 ms 内的弱音听不见
- 由掩蔽曲线算每子带 **SMR**，分配比特

→ **MP3 = MDCT + 心理声学掩蔽 + Huffman**。

**CQT（Constant-Q Transform）**：频率轴对数等分，每八度固定 bin 数。Spotify chroma、Spleeter 分离都用它。

## 1.5 音高的对数感知

$$f = 440 \cdot 2^{(p-69)/12}$$

每升半音 = 频率乘 $2^{1/12} \approx 1.0595$。

---

# 第二篇：音乐 · 数学

## 2.1 毕达哥拉斯：协和 = 简单整数比

- 弦长比 **2:1** → 八度；**3:2** → 纯五度；**4:3** → 纯四度
- **五度相生律**：从 1 出发反复乘 3/2 模 2 折回
- 硬伤：$(3/2)^{12} = 129.746 \neq 2^7 = 128$，差一个 **Pythagorean comma ≈ 23.46 音分** → 狼五度

## 2.2 纯律 vs 平均律：千年之争

**纯律**：大三度也用 5/4。大三和弦 = 4:5:6 最纯净。代价：换调就崩。

**十二平均律（12-TET）**：每半音 $2^{1/12}$，所有调对称，可任意转调。**朱载堇（明万历 1584）**首次精确算出，**Bach《平均律键盘曲集》(1722)**用音乐证明可行。代价：除八度外所有音程都微微弄脏。这是西方音乐征服世界的数学基础。

## 2.3 协和感 = Plomp-Levelt 曲线

**Helmholtz 粗糙度理论**：两音频率差 < 临界带宽时，基底膜激活区相互干涉产生拍，听为"粗糙"。

**Plomp & Levelt (1965)** 量化得到"粗糙度曲线"，倒过来即"协和度曲线"。令人震惊：峰值位置与简单整数比高度吻合，**且与是否 12-TET 无关**。

→ 12 半音是被自然"挑选"出来的——12-TET 的音程最接近粗糙度曲线的协和峰。

## 2.4 和声的几何：Tymoczko 的 Orbifold

**Dmitri Tymoczko, *A Geometry of Music* (2011)** 把和弦变成几何空间：n 个音的和弦形成 orbifold $T^n / S_n$（n 维环面除以置换对称）。

- 边界"反弹"：B→C 时从另一侧弹回
- 中点穿过自己：增三和弦在中点

在这个空间里 **voice leading = 几何最短路径**。新里曼理论（Neo-Riemannian）的 R、P、L 变换是 orbifold 上的反射对称。21 世纪音乐理论最大突破：音乐分析的"语法"变成可计算几何。

## 2.5 节奏的数学：欧几里得算法

**Toussaint (2005)** 发现跨文化奇迹：巴西 samba、古鲁巴 bell pattern、马其顿 7/8、印度 tala——**全部是欧几里得算法的副产品**。把 k 个 onset 用 Bjorklund 算法尽可能均匀放进 n 槽 = **Euclidean rhythm E(k,n)**。

→ 人类对"好节奏"的直觉 = 数学上的最大分散。

---

# 第三篇：音乐 · 神经科学

## 3.1 耳蜗 = 活体 FFT

声波 → 鼓膜 → 三块听小骨（杠杆放大 ~22×）→ 耳蜗。基底膜从底到顶刚度递减，某频率 f 在某位置共振最大——**膜本身是机械傅里叶分析仪**。

- 高频 → 底部；低频 → 顶部
- 毛细胞把振动变神经放电
- **place coding**（频率 → 位置）+ **temporal coding**（< 5kHz 时锁相放电）

→ **Georg von Békésy 1961 诺贝尔奖**：证明基底膜是活体频谱仪。

## 3.2 音乐激活全脑，不只是听觉皮层

fMRI 显示听喜欢的音乐时听觉皮层只是入口。真正亮起来：

| 脑区 | 在音乐里做什么 |
|------|----------------|
| 伏隔核 / 腹侧纹状体 | 多巴胺，愉悦感核心 |
| 杏仁核 | 情绪，战栗 |
| 小脑 + 基底节 | 节奏，跟着打拍子 |
| 海马 | 情节记忆 |
| 默认网络 DMN | 心流、神游 |
| 运动前区 / SMA | 即便不动也"跟着动" |

**Salimpoor et al. (Nature Neuroscience, 2011)** 用 PET + fMRI 拍到：受试者感到"音乐高潮前战栗"时，**伏隔核多巴胺释放峰值提前高潮几秒**——大脑在"期待"中被奖赏。验证了 Meyer 1956 期待理论。

## 3.3 预测编码框架

**Karl Friston 自由能原理**：大脑 = 贝叶斯预测机，生成对下一输入的预测，用预测误差更新模型。目标是把误差控制在合理区间——既不太少（无聊）也不太多（混乱）。

音乐是完美玩具：形成"下一个和弦应该是 V→I"预测；作曲家给 vi 假终止 → 预测被违反但可理解 → 多巴胺。

**David Huron ITPRA 模型**（*Sweet Anticipation*, 2006）拆 5 相位：Imagination / Tension / Prediction / Reaction / Appraisal。**所有音乐情绪工程都是这 5 相位的精细把玩**。

## 3.4 Frisson（音乐起鸡皮疙瘩）

约 50% 的人能稳定体验。与人格特质 **Openness to experience** 强相关。前扣带回 + 右侧壳核激活，**与社交/性/食物奖赏共用回路**。

## 3.5 绝对音高与训练可塑性

- 约 1/10000 的人；遗传 + 7 岁前早期窗口；音调语言者概率更高
- **音乐训练重塑大脑**（Schlaug, Nat Rev Neurosci 2015）：胼胝体前部增厚、听皮层灰质增加、听觉-运动耦合
- **歌声选择性神经元**（Norman-Haignere et al., 2022）：人听皮层有专门响应"歌声"的神经元群

## 3.6 音乐 vs 语言：SHARE 模型

**Patel (2008)** SHARE：Shared 一些资源 + Separated。共享句法加工（Broca 区附近）；分离：语言指称语义，音乐不指称。**失语症患者仍能唱歌**（Melodic Intonation Therapy 用此康复）。

---

# 第四篇：音乐 · 进化

## 4.1 Pinker 的"奶酪蛋糕"挑战

Pinker (1997): "音乐是听觉奶酪蛋糕……纯享乐技术，利用已有听觉/情绪/语言回路偏好。" 进化论挑战：音乐不是适应，怎么来的？

## 4.2 五大假说

| 假说 | 提出者 | 核心 |
|------|--------|------|
| A. 性选择 | Darwin 1871 | 类比鸟鸣，求偶展示 |
| B. 母婴联结 | Falk 2004 | 直立行走后远距安抚 → 母亲语 → 音乐 |
| C. 社会凝聚 | Dunbar | 替代理毛，触发内啡肽 |
| D. 行动协调 | — | 劳动号子、船歌、行军 |
| E. 诚实信号 | Zahavi | handicap principle |

## 4.3 最新辩论

**Mehr & Krasnow (2021, Nature Hum Beh)** "music as a credible signal"：母亲唱歌 = "我在认真照顾"的可信信号；战歌 = "我们团结"信号。统一 B/C/D/E。

**Cross / Honing** 反驳：多功能性恰恰说明是适应。

**Patel (2021)** "声音学习假说"：音乐能力搭便车于声音学习（人类是少数有此能力的动物）。

> 截至 2024，多数进化心理学家放弃 Pinker 的"奶酪蛋糕"——音乐的普遍性、跨文化结构相似、对大脑强重塑、深度劫持奖赏回路，都指向**多效性适应**。

## 4.4 实证：节奏同步增强合作

**Wiltermuth & Heath (2009, Science)**：陌生人分组同步走路 vs 不同步，之后合作游戏——**同步组明显更合作、更信任**。给现场演唱会、宗教仪式、军队行军提供神经-进化解释：**音乐是同步化的化学-社会技术**。

---

# 第五篇：音乐 · 心理与文化

## 5.1 大调 vs 小调：天然还是约定？

部分是物理（大三度比小三度"亮"），主要还是文化。

**Jacoby et al. (Nature Hum Beh, 2019)** 用 Tsimané 人（无西方音乐接触）：他们对"大调=快"判断**几乎随机**。→ **大调-小调情感映射主要是文化学习**。

但节奏情感跨文化一致（Jacoby 2017, PNAS）：所有文化都把"快/规律"判为"快乐"。→ **节奏普适，调式情感文化**。

## 5.2 世界音乐体系

| 文化 | 音高组织 | 和声 | 节奏 |
|------|---------|------|------|
| 西方 | 12-TET，垂直和声 | 主调，和弦堆叠 | 拍子 |
| 印度 | 22 shruti，raga 框架 | **无和声**，单旋律+drone | tala 循环 |
| 阿拉伯 | 24 平均律，1/4 音 | 单旋律+即兴 | iqa |
| 中国 | 五声（无半音）| 支声复调 | 板眼 |
| 印尼甘美兰 | slendro(5均)/pelog(7不均) | kotekan 层叠 | 多层节奏 |
| 撒哈拉以南非洲 | 五声/七声 | **复节奏** | cross-beat 3对2 |

**重要观察**：和声（垂直叠加）是**西方独有**，源自中世纪教堂多声部。其他高文明传统都是单旋律 + 装饰 + 复节奏。

## 5.3 情感的多维空间

Russell 环形模型（1980）：**arousal × valence** 二维。Spotify Valence/Arousal 算法（Echo Nest 2014）即用音频特征预测。

---

# 第六篇：音乐 · 技术与 AI（含所有算法）

## 6.1 数字音频根基：采样定理

**Nyquist-Shannon**：带限信号最高频 $f_{max}$，则采样率 $\geq 2f_{max}$ 完美重建。
- CD = 44.1 kHz（人耳 ~20 kHz × 2 + 余量）
- 16-bit = 96 dB 动态范围；24-bit = 144 dB
- **Dither**：量化前加白噪声，把刺耳的量化失真变成可掩蔽的白噪声

## 6.2 音频编码算法谱系

| 编码 | 算法核心 |
|------|---------|
| **PCM/WAV** | 原始采样 |
| **MP3** (1993) | 多相滤波器组 + MDCT + 心理声学 + Huffman |
| **AAC** | 纯 MDCT + TNS，更好低码率 |
| **Opus** (2012) | SILK（语音 CELP）+ CELT（音乐 MDCT）动态切换，超低延迟 |
| **FLAC/ALAC** | 线性预测 + Rice 编码，无损 |
| **EnCodec** (Meta 2023) | CNN + **RVQ（残差向量量化）** + GAN 对抗 loss |
| **SoundStream / DAC** | 同 RVQ 思路 |

**RVQ 是神经音频编码核心创新**：多码本残差堆叠，让少量 codebook 表达丰富音频，是后续所有音频 LLM 基础。

## 6.3 合成器算法大全

- **减法合成**（Moog）：丰富谐波振荡器 → 低通滤波 → ADSR 包络
- **加法合成**：多正弦波叠加（Fourier）
- **FM 合成**（Chowning 1973, Yamaha DX7）：$y=\sin(2\pi f_c t + I\sin(2\pi f_m t))$
- **Wavetable**（Serum/Massive）：多波形间插值
- **物理建模**：Karplus-Strong（拨弦延迟线+低通）、Digital Waveguide（Smith）、DDSP（Google 可微 DSP）
- **粒度合成**（Roads）：10-100 ms 颗粒独立处理

## 6.4 MIR（音乐信息检索）算法

| 特征 | 算法 | 用途 |
|------|------|------|
| MFCC | FFT→Mel 滤波→log→DCT | 通用音频特征 |
| Chroma | CQT→12 bin | 和弦识别、cover 检测 |
| Tempo | onset→自相关 | 推荐、混音 |
| Source separation | NMF / U-Net（Demucs v4, 2023）| 提取人声/鼓/贝斯 |

## 6.5 音乐生成 AI 时间线

**符号音乐**：DeepBach (2017), Music Transformer (2018), MuseNet (2019)

**波形自回归**：
- **WaveNet** (DeepMind 2016)：因果空洞卷积自回归 μ-law 256 类
- **Jukebox** (OpenAI 2020)：分层 VQ-VAE + 3 个 Transformer

**扩散 + Latent**：AudioLDM (2023), AudioLDM 2

**Token 自回归**（当前主流）：
- **MusicGen** (Meta 2023)：EnCodec tokenize → Transformer 自回归（delay pattern 多码本展平）+ T5 文本条件 + CFG
- **Jasco** (Meta 2024)：可控和弦/节拍/旋律生成
- **Stable Audio Open** (2024)：扩散路线

**商业王者**：
- **Suno v3/v3.5/v4** (2023.12–2024)：大规模 autoregressive + 多码本 + 歌词条件 + 长结构
- **Udio** (2024.4)：扩散 + 自回归混合，现场感

**2025 开源前沿**：YuE、ACE-Step（歌曲生成）；MERT/MusicFM（自监督表征）

## 6.6 未解难题

1. **长结构**：Transformer context 有限，几十秒后漂走
2. **可解释控制**：改"这里换小调"等
3. **音乐理解**：模型真懂乐理吗？多数证据否定
4. **音乐世界模型**：在 latent 中"演奏"

---

# 第七篇：视频 · 物理光学与视觉感知

## 7.1 光：380–740 nm 电磁波

可见光只是电磁波谱极小一段。视频本质：用传感器采样光的时空分布，再用显示器复现。

## 7.2 人眼：杆 + 三种锥

- 视杆 ~1.2 亿，单色亮度，低光工作
- 视锥 ~600 万，**L/M/S 三类**（560/530/420 nm）

**三色理论**（Young-Helmholtz）：颜色 = (L,M,S) 三维。显示器只需 RGB 三磷光体即可骗出全色彩。

L 和 M 锥非常靠近（绿/黄难分），S 锥少 → 人眼对蓝色细节不敏感 → **YCbCr + 4:2:0** 的物理根据。

## 7.3 色彩空间

- **CIE 1931 XYZ**：所有色彩空间祖父
- **sRGB** (1996)：消费显示器
- **YCbCr/YUV**：$Y=0.299R+0.587G+0.114B$，视频压缩核心
- **HDR**：PQ（Dolby, 0–10000 nit 对数）/ HLG（BBC 兼容 SDR）；Rec.2020 广色域

## 7.4 时间采样与临界融合频率

CFF ~60 Hz（个体 60–90）。帧率权衡：24 fps（电影，180° 快门法则配运动模糊）、30/60/120 fps。**Phi 现象**（Wertheimer 1912）：两光点 < 60 ms 间隔闪 → 大脑感知移动——电影成立的神经基础。

## 7.5 视觉皮层与运动

视网膜 → LGN → V1（边缘）→ V2 → **MT/V5**（运动方向选择性放电）→ MST。MT 是光流的硬件。

---

# 第八篇：视频 · 信号处理与编码算法全集

## 8.1 视频是 3D 信号 $f(x,y,t)$

奈奎斯特三维都成立：空间不足 → 摩尔纹；时间不足 → 车轮反转。

## 8.2 四种冗余

| 冗余 | 算法 |
|------|------|
| 空间冗余 | DCT、帧内预测 |
| 时间冗余 | 运动补偿 |
| 统计冗余 | 熵编码（CABAC/rANS）|
| 心理视觉冗余 | 量化（有损）|

## 8.3 色彩子采样 4:2:0

Y 全分辨率，Cb/Cr 水平垂直都减半 → 数据量砍 50%，肉眼几乎看不出。所有主流视频编码默认。

## 8.4 2D DCT（JPEG 的魔法）

$$X_{k,l} = \sum_{i,j} x_{i,j}\cos\frac{(2i+1)k\pi}{2N}\cos\frac{(2j+1)l\pi}{2N}$$

**核心性质**：自然图像能量集中在低频。8×8 块 DCT 后右下角（高频）系数接近 0。

JPEG 流程：RGB→YCbCr → 8×8 块 DCT → 量化矩阵除（高频丢掉）→ zigzag + RLE + Huffman。

## 8.5 帧类型与 GOP

- **I 帧**：独立编码（像 JPEG）
- **P 帧**：前向预测，存运动矢量 + 残差
- **B 帧**：双向预测，压缩率最高
- **GOP**：I + 一串 P/B。短 GOP 利于 seek/低延迟；长 GOP 高压缩率

## 8.6 运动估计 / 运动补偿（ME/MC）★

对当前块在参考帧找最相似块，记录**运动矢量（MV）+ 残差**。

**块匹配**：SAD（Sum of Absolute Differences）作代价
**搜索算法**：全搜索 / 三步搜索 / 菱形搜索 / **TZ Search（HEVC）** / x264 HEX/DIA
**亚像素**：1/4 像素（H.264）需插值滤波器 → 节省 ~20% 码率

## 8.7 H.264/AVC (2003) 划时代

16×16 宏块 + 子块分割；整数 DCT（4×4/8×8）；1/4 像素 ME；CABAC；多参考帧（最多 16）；环路去块滤波。比 MPEG-2 省 ~50%。YouTube/Netflix/Blu-ray 基础。

## 8.8 H.265/HEVC (2013)

**编码树单元 CTU 64×64 递归四叉树**；35 种帧内预测方向；SAO；WPP/Tiles 并行；12-bit 支持。比 H.264 又省 ~50%。但专利池贵（3 池几百专利）→ 业界转 AV1。

## 8.9 VP9 (2013) 和 AV1 (2018)

**AV1**（AOMedia：Google/Netflix/Amazon/MS/Cisco）免版税：
- 递归到 4×4 多类型分割
- **64-point + Asymmetric + Identity 变换**
- **56 种帧内方向** + palette + recursive
- **rANS（asymmetric numeral systems, Jarek Duda）**熵编码——比 CABAC 更并行友好
- **CDEF** + **LR (Wiener)** 滤波
- **Film grain synthesis**：胶片颗粒剥离后参数化合成

比 HEVC 省 ~30%。YouTube/Netflix 4K 主力。

## 8.10 VVC / H.266 (2020)

比 HEVC 再省 ~50%。三叉树分割、**AFFINE 运动模型**（非刚性）、IBC+Palette 增强。专利问题仍在 → AV1 更受欢迎。

## 8.11 熵编码对比

| 编码 | 用在 |
|------|------|
| VLC/Huffman | JPEG, H.263 |
| Arithmetic | H.264 早期 |
| **CABAC** | H.264/HEVC 主力（强串行但效率高）|
| **rANS / FSE** | AV1（GPU 并行友好）|
| **Neural entropy model** | 神经视频压缩 |

## 8.12 神经视频压缩（NVC）★

端到端神经编码。**DCVC 系列**（Li et al. 2020–2024）：编码器 CNN + hyperprior 神经熵模型 + 自回归上下文 + 多帧特征检索（DCVC-DC/FM）。低码率超 VVC，但慢——研究前沿。

## 8.13 编码算法谱系全景

```
JPEG (1992)        图像
MPEG-1 (1993) VCD → MPEG-2/H.262 (1995) DVD → H.263 (1996)
MPEG-4 Part 2 (DivX 2000)
  ↓
H.264/AVC (2003) ★ YouTube/Netflix 一代
  ├─ VP8 (2010)
  └─ HEVC/H.265 (2013) ★ 四叉树 CTU
        ├─ VP9 (2013)
        ├─ AV1 (2018) ★ 免版税
        ├─ VVC/H.266 (2020)
        └─ 神经视频压缩 (2020+)
```

---

# 第九篇：视频 · 流媒体与 ABR

## 9.1 分块编码 + ABR

视频切 2–10 秒 chunk，每段多码率版本（ladder：240p/480p/720p/1080p/4K），客户端动态切换 = **ABR（Adaptive Bitrate）**。

## 9.2 协议

| 协议 | 拥有者 | 容器 |
|------|--------|------|
| **HLS** | Apple (2009) | .ts/fMP4 + .m3u8 |
| **DASH** | MPEG (2012) | .mp4 + .mpd |
| **CMAF** | MPEG (2017) | 统一 fMP4，HLS+DASH 共用 |

都基于 HTTP → 利用 CDN 缓存 → 2010 后视频爆炸基础。

## 9.3 ABR 算法谱系

**Throughput-based**：测过去下载速度预测。YouTube 早期默认。

**BOLA** (2016, INFOCOM 最佳)：Lyapunov 优化证明只看缓冲区水位即接近最优。dash.js 默认。

**MPC** (MIT 2015 SIGCOMM)：滚动优化未来 N 段码率组合。

**Pensieve** (MIT 2017 SIGCOMM) ★：A3C 强化学习 ABR——首次证明 RL 在生产级网络问题有用。

**Puffer** (Stanford 2019–) ★：真实在线学习 + **Fugu** Bayesian NN（2020）。数据全开放。

## 9.4 Per-title 编码（Netflix 2015）

每部片单独训练"码率-分辨率"曲线选 ladder。后续升级 per-shot + AV1 per-shot。

## 9.5 CDN

视频占互联网 80%+ 流量。Netflix Open Connect / Akamai / Cloudflare / 阿里 CDN。

---

# 第十篇：视频 · AI 生成（所有架构与算法）

## 10.1 范式演化

```
GAN 视频 (VGAN 2016, MoCoGAN 2018) → 自回归 (VPN 2017)
→ 扩散图像 (DDPM 2020) → 图像 LDM (SD 2022)
→ 视频 LDM (SVD 2023.11) → 视频 DiT (Sora 2024.2) ★
→ 音视频同步 (Veo 3, 2025.5) ★ → 世界模型 (Genie 2)
```

## 10.2 核心范式：Latent Diffusion + DiT

**为什么 latent**：5s 720p60 = 8 亿数值，直接扩散不可行 → VAE 压到 latent。

**为什么 DiT**：**DiT (Peebles & Xie, ICCV 2023)** 把 U-Net 换 Transformer，scaling law 友好。**Sora 2024.2 首次大规模用 DiT for video**——视频生成 GPT 时刻。

## 10.3 视频生成专属技术栈（所有算法）

### ① 3D causal VAE
图像 VAE 只压空间。视频需**时空联合压缩**：空间 H/8, W/8 + 时间 T/4 = 256× 压比。**因果卷积**只用过去帧，避免训练时未来泄漏 → 保证自回归长视频可行。CogVideoX/HunyuanVideo/Wan 都用。

### ② Flow Matching / Rectified Flow
**Flow Matching**（Lipman et al., ICLR 2023）把扩散"加噪去噪"换成"沿直线从噪声流到数据"。训练更稳、推理步数少、数学简洁（学 vector field）。**所有 2024–2025 主流视频模型用**（SD3/Wan/HunyuanVideo）。

### ③ 3D 注意力 + 位置编码
- Spatial-only（早期 SVD）：时间一致性差
- **Full 3D attention**（Sora/Wan）：$O((T\cdot H\cdot W)^2)$ 显存爆炸
- **3D RoPE**：把 RoPE 扩展到 3D 时空——HunyuanVideo/Wan 用
- Window attention + shift：省显存

### ④ 文本条件
T5-XXL（Sora/CogVideoX/Wan）/ CLIP / 多语言 LLM（HunyuanVideo）。Cross-attention。

### ⑤ Classifier-Free Guidance (CFG)
训练时随机 drop 文本 10–20%，推理：
$$\epsilon_{\text{guided}} = \epsilon_{\text{cond}} + w(\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})$$

### ⑥ 长视频生成
自回归扩展：前 N 帧 clean latent 作条件 → 加噪后帧 → DiT 去噪 → 滑动窗口续写。Wan/Kling 用 hierarchical noise schedule。

### ⑦ 运动控制
Wan motion score：数值控制运动强度。

## 10.4 代表模型时间线（2023–2025）

| 模型 | 发布 | 参数 | 架构亮点 | 开源 |
|------|------|------|----------|------|
| SVD | Stability 2023.11 | ~1B | 图像 LDM + 时间层 | ✓ |
| **Sora** | OpenAI 2024.2 | 未公开 | DiT + 时空 patch + 世界模型叙事 | ✗ |
| **CogVideoX** | 智谱 2024.8 | 5B/30B | **专家 Transformer**（T+V 双分支）+ 3D VAE | ✓ |
| Open-Sora 1.x/2.0 | HPC-AI 2024–25 | 0.7–20B | 开源复刻 Sora | ✓ |
| Mochi-1 | Genmo 2024.11 | 10B | Asymm DiT | ✓ |
| LTX-Video | Lightricks 2024 | 2B | 实时（秒级推理）| ✓ |
| **HunyuanVideo** | 腾讯 2024.12 | **13B** | **双流 DiT**（文本+视频 token 联合）| ✓ 最大开源 |
| Kling 1.x/2.0 | 快手 2024.6+ | 未公开 | 闭源 SOTA | ✗ |
| **Wan 2.1** | 阿里 2025.3 | **1.3B+14B** | **scaling law 实证**，1.3B 仅 8.19GB VRAM | ✓ |
| Wan 2.2 | 阿里 2025.5+ | 14B+ | 音视频同步（参考 Veo 3）| ✓ |
| Veo/Veo 2 | Google 2024.5 | 未公开 | 4K 电影级 | ✗ |
| **Veo 3** | Google 2025.5 | 未公开 | **同步生成音频**（对白/拟音/音乐）| 部分 |
| **Genie 2** | DeepMind 2024.12 | 未公开 | **可交互世界模型** | ✗ |

**Wan 2.1 关键证据**（arXiv:2503.20314, 已抓取）：
- 主流 diffusion transformer paradigm
- 14B 在亿级图文+视频上训练，**验证视频生成 scaling law**
- 1.3B 仅需 **8.19 GB VRAM**（消费级 GPU 友好）
- 覆盖 8 个下游任务：T2V/I2V/视频编辑/个性化生成
- 创新：novel VAE、可扩展预训练、数据筛选、自动评估

## 10.5 推理加速算法

视频 DiT 推理极慢（5s 视频要分钟级）——产品化核心瓶颈。

**蒸馏**：ADD/SFvM（50 步→4 步）、Consistency Models（1 步）

**缓存**★：扩散去噪中多数步注意力输出变化小
- DeepCache / **PAB（Pyramid Attention Broadcast）** / **TeaCache** / DGCache

**量化**：INT8/FP8 DiT（W8A8）→ 显存减半、2–3× 速度

**VAE 加速**：3D VAE 解码占 30%+ → tiled VAE 分块解码

## 10.6 未解难题

1. 时间一致性长视频（>1 min 变形）
2. 物理正确性（Sora "杯穿桌" → 学的是相关不是因果）
3. 精确可控（镜头/动作/lip sync）
4. 音频同步（Veo 3 突破但远未成熟）
5. 真世界模型（Genie 2 早期）

## 10.7 评估指标

VBench（复旦 2024）/ VBench-2.0 / FVD / CLIP-Sim / EvalCrafter。

---

# 第十一篇：视频 · CV 算法 + 世界模型

## 11.1 经典 CV

**光流**：Lucas-Kanade (1981) / Horn-Schunck (1981) / **RAFT (ECCV 2020)** 循环 all-pairs correlation / GMFlow (2022) Transformer global

**检测+跟踪**：YOLO v8/v9/v10/v11/**v12 (2025)** 单阶段实时；DETR (2020) Transformer 端到端；RT-DETR；ByteTrack (2022)；BoT-SORT/DeepSORT

**视频分割**：SAM (2023) → **SAM 2 (2024)** memory bank 跨帧记忆 mask

**视频理解**：VideoMAE (NeurIPS 2022) masked AE；TimeSformer；InternVideo/2

## 11.2 世界模型叙事

Sora 团队定位为"world simulators"；**Genie 2**（DeepMind 2024.12）可玩 3D 世界；**LeCun JEPA** 反对生成式、主张预测抽象 latent。**争议**：当前视频模型学的是"像素相关"，不是"物理因果"。

---

# 总结：音乐 × 视频 技术对照

| 维度 | 音乐 | 视频 |
|------|------|------|
| 物理量 | 空气纵波 | 电磁波（光）|
| 传感器 | 耳蜗（活体 FFT）| 视网膜（杆+3 锥）|
| 采样 | 44.1 kHz (CD) | 60 Hz 帧 + 1080×1920 |
| 维度 | 1D 信号+频率 | 3D (H×W×T) |
| 核心变换 | MDCT/CQT | DCT + 运动估计 |
| 熵编码 | Huffman (MP3) | CABAC/rANS |
| 关键压缩 | 心理声学掩蔽 | 运动补偿 + DCT |
| 流媒体 | 低延迟 Opus WebRTC | ABR (BOLA/Pensieve) |
| 神经编码 | EnCodec (RVQ) | DCVC (neural entropy) |
| 生成范式 | autoregressive token (MusicGen/Suno) | DiT + flow matching (Sora/Wan) |
| 生成难点 | 长结构 + 可控 | 时间一致性 + 物理 |
| 进化压力 | 社会凝聚/内啡肽 | 运动检测/捕食逃避 |
| 认知基础 | 预测编码 + 多巴胺 | MT/V5 + 注意机制 |

**惊人相似**：两域都是"**采样 → 压缩（去除人感知不到的冗余）→ 传输（自适应）→ 生成（统计建模）**"。在数学上同构。

## 一句话回答"音乐和视频是什么"

> 音乐和视频，都是人类用生物硬件感知、用文化语法编码、用工程算法压缩、用生成模型复刻的"时间序列信号"。在物理层是波动；在神经层是预测误差；在工程层是去冗余；在 AI 层是分布建模。**所有视角共享同一个数学骨架：傅里叶 + 信息论 + 概率。**

## 关键算法清单

**音乐**：FFT、STFT、MDCT、心理声学掩蔽、Huffman、Rice、Karplus-Strong、FM、减法/加法/wavetable/granular 合成、MFCC、Chroma、NMF、Demucs/U-Net、VQ-VAE、RVQ、WaveNet、Music Transformer、Jukebox、AudioLDM、MusicGen、Jasco、Suno/Udio（多码本自回归）、ACE-Step、MERT。

**视频**：DCT、运动估计（菱形/TZ/三步）、运动补偿、亚像素插值、CABAC、rANS、环路滤波（deblocking/SAO/CDEF）、H.264/265/AV1/VVC、Per-title、HLS/DASH/CMAF、BOLA、MPC、Pensieve (A3C)、Puffer（在线 RL + Bayesian NN）、3D causal VAE、DiT、Flow Matching、3D RoPE、CFG、TeaCache/PAB、RAFT、YOLO、ByteTrack、SAM 2、VideoMAE、VBench。

## 进一步学习路径

- **神经科学**：Huron《Sweet Anticipation》、Patel《Music, Language, and the Brain》
- **音乐理论数学**：Tymoczko《A Geometry of Music》、Toussaint《The Geometry of Musical Rhythm》
- **编码标准**：Richardson《Video Codec Design》、Iain Richardson HEVC 教程
- **AI 生成**：读 Sora/Veo/Wan/HunyuanVideo 技术报告；HuggingFace Daily Papers (cs.SD/cs.CV)
- **开源代码**：跑 MusicGen、Wan2.1-1.3B（仅需 8GB VRAM）、Demucs、SAM 2

## 三大开放研究方向（2025–2026）

1. 长视频一致性 + 长结构音乐
2. 音视频同步生成（Veo 3 / Wan 2.2 方向）
3. 真正的世界模型（超越像素相关，达物理因果）
