# 音乐生成模型对比：MusicGen vs Suno vs Udio

> 截至 2025 年三大主流音乐生成路线对比。
> MusicGen 完全开源；Suno/Udio 闭源但架构可推测。

## 1. 路线图

```
符号音乐 (MIDI)
  DeepBach (2017) / Music Transformer (2018) / MuseNet (2019)
        ↓
波形自回归（端到端，慢）
  WaveNet (2016) → SampleRNN → Jukebox (2020)
        ↓
扩散 + Latent
  AudioLDM / AudioLDM 2 (2023)
        ↓
Token 自回归（当前主流）
  MusicGen (Meta, 2023) → Jasco (2024) → Suno v3/v4 → YuE/ACE-Step (2025)
        ↓
扩散 + Autoregressive 混合
  Udio (2024)
```

## 2. MusicGen（Meta, 2023）— 开源 SOTA

### 架构
```
prompt → [T5/FLAN-T5 文本编码器]
              ↓
              ↓ text_emb
              ↓
[EnCodec] → audio tokens (RVQ 多码本)
              ↓
[Transformer decoder 自回归]
   "delay pattern" 把多码本展平成单序列
   每步同时预测所有码本 token
              ↓
[EnCodec decoder] → 波形
```

### 关键技术
- **EnCodec tokenize**：把连续音频 → 离散 token（RVQ）
- **Delay pattern**：第 c 个码本延迟 c 步，统一 attention
- **多码本并行**：每步输出所有码本
- **Classifier-Free Guidance**

### 模型规模
- small: 300M
- medium: 1.5B
- large: 3.3B
- **训练数据**：20k 小时内部音乐（licensed）

### 优点
- 完全开源（代码 + 权重）
- 24/48 kHz 输出
- 文本可控（genre、instrument、mood）

### 局限
- 单段（最长 ~30s）
- 不支持歌词
- 无 verse-chorus 长结构

## 3. Suno v3/v3.5/v4（2023.12–2024）— 商业王者

### 架构（推测，未公开）
```
歌词 + prompt（多模态条件）
              ↓
[multimodal encoder]
              ↓
[大规模 autoregressive Transformer]
   多码本 EnCodec-style tokenizer
   据信数百万小时训练数据
              ↓
[audio decoder]
              ↓
完整歌曲（含人声 + 伴奏 + 长结构）
```

### 关键能力
- **完整歌曲**：3-4 分钟，含 verse-chorus 反复
- **歌词驱动**：直接给歌词，模型决定旋律
- **多语言**（中、英、日、韩等）
- **多风格**（流行、摇滚、爵士、电子、古典）

### 推测技术
- 多码本自回归（人声 + 鼓 + 贝斯 + 旋律独立 codebook）
- 长上下文 Transformer（context > 100k tokens）
- 歌词条件 + 音乐结构 token（[verse]、[chorus]）

### 商业模式
- 免费试用 + 订阅（$10-30/月）
- 版权分成给艺术家
- 与唱片公司合作

## 4. Udio（2024.4）— 现场感最强

### 架构（推测）
**扩散 + autoregressive 混合**：
```
prompt + optional reference audio
              ↓
[扩散 latent audio model]
   类似 Stable Audio Open 思路
   但加 autoregressive 长结构
              ↓
完整歌曲
```

### 特点
- **音质"现场感"**：人声、混音、空间感强
- **戏剧化**：擅长情感强烈的人声
- **更细可控**：可以指定"female vocalist, belt, with reverb"

### 团队背景
由前 Stability AI Stable Audio 团队（创建者）创立，公司 un(x)lab。

## 5. 三者对比表

| 维度 | MusicGen | Suno v4 | Udio |
|------|----------|---------|------|
| 开源 | ✓ | ✗ | ✗ |
| 架构 | Token AR | Token AR (推测) | Diffusion + AR |
| 时长 | ~30s | 3-4 min | 2-15 min |
| 歌词 | ✗ | ✓（核心）| ✓ |
| 长结构 | ✗ | ✓ | ✓ |
| 音质 | 中等 | 流行录音水准 | 录音室水准 |
| 控制 | prompt | prompt + lyrics | prompt + 多参数 |
| 训练数据 | 20k 小时（已说） | 数百万小时（推测） | 未公开 |
| 模型规模 | 300M-3.3B | 未公开 | 未公开 |
| 商业可用 | 免费研究 | $10-30/月 | $10-30/月 |

## 6. 2025 开源追赶

### YuE（m-a-p, 2025）
- 开源歌曲生成（含人声 + 长结构）
- 多码本 autoregressive
- 接近 Suno v3 水准

### ACE-Step（2025）
- 开源歌曲生成
- 强调可控性

### MERT / MusicFM（2024）
- 不是生成，而是**自监督音乐表征**
- 类比 LLM 预训练，给下游任务（分类、检索、推荐）用
- 未来可能 + MusicGen 形成基础模型

## 7. 未解难题

1. **长结构**：verse-chorus 反复需要 >100k context
2. **可控性**：改"这里换小调"、"延长 4 小节"
3. **音乐理解**：模型真懂乐理吗？多数证据否定
4. **版权**：训练数据来源 + 生成内容归属
5. **音乐世界模型**：在 latent 中"演奏"

## 8. 选择建议

| 用例 | 推荐 |
|------|------|
| 研究/学习 | **MusicGen**（开源可控）|
| 快速创作歌曲 | **Suno**（最易用）|
| 高质量专业音乐 | **Udio**（音质最佳）|
| 开源歌曲生成 | **YuE / ACE-Step** |
| 音乐表征（下游任务）| **MERT / MusicFM** |

## 9. 复现路径（开源）

1. **EnCodec**：理解音频 tokenize + RVQ
2. **MusicGen small**：跑通 300M 模型
3. **改造**：加歌词条件、加长 context
4. **训练数据**：用公开数据集（MTG-Jamendo、FMA）小规模试训

## 10. 关键论文

- Copet et al. 2023 *Simple and Controllable Music Generation* (MusicGen)
- Agostinelli et al. 2023 *MusicLM*
- Huang et al. 2023 *Noise2Music*
- Defossez et al. 2023 *EnCodec*
- Evans et al. 2024 *Stable Audio Open*
- Huang et al. 2024 *Jasco* (Meta)
