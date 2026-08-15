# 音乐 · WaveNet 与 AI 作曲数学

> **博士级**：音频生成 + 音乐创作的数学。

## 一、音频数据

### 1.1 表示

- **波形**（waveform）：16 bit × 44.1 kHz = ~88 KB/s
- **频谱图**（spectrogram）：STFT
- **MIDI**（符号）

### 1.2 挑战

- **超长序列**（秒级音频 = 万级采样）
- **多尺度**（瞬时 + 长期结构）

## 二、WaveNet（van den Oord 2016）

### 2.1 核心：因果空洞卷积

$$y(t) = f(x(t), x(t-1), ..., x(t-L))$$

- **因果**：只用过去
- **空洞**（dilation）：指数增长感受野
- 自回归生成

### 2.2 数学

- 每个采样条件于过去
- **256 个 μ-law 量化级别**
- softmax 分类

### 2.3 改进

- Parallel WaveNet（概率蒸馏）
- WaveGlow（flow）

## 三、符号音乐

### 3.1 MIDI 表示

- 音符（pitch + velocity + time）
- 类似文本 token
- **Music Transformer**（Huang 2018）

### 3.2 Transformer 作曲

- 长 structure（奏鸣曲式 / 流行歌）
- 相对注意力
- **MuseNet / Music Transformer**

### 3.3 局限

- MIDI 没有真实音色
- 表现力有限

## 四、现代 AI 音乐

### 4.1 MusicLM（Google 2023）

- 文本 → 高质量音乐
- 多阶段（语义 → 音乐 → 音频）
- **AudioLM**

### 4.2 MusicGen（Meta 2023）

- 开源
- EnCodec + Transformer
- 可控

### 4.3 Suno / Udio（2024）

- 完整歌曲（歌词 + 旋律 + 人声）
- 端到端
- 商业化

## 五、音乐信息检索（MIR）

### 5.1 任务

- **节拍检测**（beat tracking）
- **和弦识别**（chord recognition）
- **流派分类**（genre）
- **乐器分离**（source separation）

### 5.2 工具

- **librosa**（Python）
- **Essentia**（MTG）
- **Spotify API**

### 5.3 推荐

- **协同过滤** + 音频特征
- Spotify / Apple Music

## 六、博士级练习

1. 训练简单 WaveNet（小数据）
2. 实现节拍检测
3. 分析 Suno / Udio 作品

## 关键引用

- van den Oord 2016 *WaveNet*
- Huang 2018 *Music Transformer*
- Agostinelli 2023 *MusicLM*
- Copet 2023 *MusicGen*
