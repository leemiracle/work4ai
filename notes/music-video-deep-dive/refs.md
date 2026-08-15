# 参考文献 + 进一步学习路径

## 一、奠基性书籍

### 音乐
- **Huron, D. (2006). *Sweet Anticipation: Music and the Psychology of Expectation*.** MIT Press. — 预测编码 + ITPRA 模型，必读。
- **Patel, A. (2008). *Music, Language, and the Brain*.** Oxford. — SHARE 模型，音乐 vs 语言。
- **Tymoczko, D. (2011). *A Geometry of Music*.** Princeton. — 和声的 orbifold 几何。
- **Toussaint, G. (2013). *The Geometry of Musical Rhythm*.** CRC. — Euclidean rhythms。
- **Sacks, O. (2007). *Musicophilia*.** Knopf. — 临床神经科学故事。
- **Levitin, D. (2006). *This Is Your Brain on Music*.** Dutton. — 大众科普。

### 视频 / 信号
- **Richardson, I. (2010). *The H.264 Advanced Video Compression Standard*.** Wiley.
- **Richardson, I. (2017). *Video Codec Design: Developing Image and Video Compression Systems*.**
- **Sayood, K. (2017). *Introduction to Data Compression*.** 5th ed. Morgan Kaufmann.
- **Bovik, A. (2010). *Handbook of Image and Video Processing*.**

### 数学
- **Strang, G. (1993). Wavelet transforms versus Fourier transforms.** Bull. AMS.
- **Oppenheim, A. & Schafer, R. (2010). *Discrete-Time Signal Processing*.** Pearson.

## 二、关键论文（按主题）

### 音乐神经科学
- Blood, A.J. & Zatorre, R.J. (2001). *Intensely pleasurable responses to music correlate with activity in brain regions implicated in reward and emotion*. PNAS.
- Salimpoor, V.N. et al. (2011). *Anatomically distinct dopamine release during anticipation and experience of peak emotion to music*. Nature Neuroscience.
- Norman-Haignere, S. et al. (2022). *A neural population selective for song in human auditory cortex*. Current Biology.
- Jacoby, N. et al. (2019). *Universal and cultural-specific features of music perception*. Nature Human Behaviour.
- Schlaug, G. (2015). *Musicians and music making as a model for the study of brain plasticity*. Nature Reviews Neuroscience.

### 音乐进化
- Pinker, S. (1997). *How the Mind Works*. — "auditory cheesecake"
- Mehr, S.A. et al. (2021). *Origins of music in credible signaling*. Nature Human Behaviour.
- Patel, A. (2018). *Music as a transformative technology of the mind*. 
- Wiltermuth, S.S. & Heath, C. (2009). *Synchrony and cooperation*. Psychological Science.

### 音乐数学
- Plomp, R. & Levelt, W. (1965). *Tonal consonance and critical bandwidth*. JASA.
- Tymoczko, D. (2006). *The geometry of musical chords*. Science.
- Toussaint, G. (2005). *The Euclidean algorithm generates traditional musical rhythms*. BRICS.

### 音频编码
- Princen, J. & Bradley, A. (1987). *Analysis/synthesis filter bank design based on time domain aliasing cancellation*. IEEE TASSP. — MDCT.
- Painter, T. & Spanias, A. (2000). *Perceptual coding of digital audio*. Proc. IEEE.
- Défossez, A. et al. (2023). *High Fidelity Neural Audio Compression*. — EnCodec + RVQ.
- Valin, J.-M. et al. (2012). *Definition of the Opus Audio Codec*. IETF RFC 6716.

### 音频生成
- van den Oord, A. et al. (2016). *WaveNet: A Generative Model for Raw Audio*. DeepMind.
- Dhariwal, P. et al. (2020). *Jukebox: A Generative Model for Music*. OpenAI.
- Copet, J. et al. (2023). *Simple and Controllable Music Generation* (MusicGen). Meta.
- Huang, Q. et al. (2023). *MusicLM: Generating Music From Text*. Google.
- Evans, Z. et al. (2024). *Stable Audio Open*.
- Fu, Y. et al. (2024). *Jasco: Joint Audio Conditioning for Music Generation*. Meta.

### 视频编码
- Sullivan, G.J. et al. (2004). *The H.264/AVC Advanced Video Coding Standard*. IEEE TCSVT.
- Sullivan, G.J. et al. (2012). *Overview of the High Efficiency Video Coding (HEVC) Standard*. IEEE TCSVT.
- Hannuksela, M. et al. (2019). *Overview of the Versatile Video Coding (VVC) Standard*.
- Bossen, F. et al. (2017). *AV1 Video Codec*.
- Li, J. et al. (2021-2024). *Deep Contextual Video Compression* series (DCVC, DCVC-HEVC, DCVC-DC, DCVC-FM, DCVC-RT).

### 流媒体 / ABR
- Spiteri, K. et al. (2016). *BOLA: Near-optimal bitrate adaptation for online videos*. INFOCOM.
- Mao, H. et al. (2017). *Pensieve: Learning-based ABR streaming*. SIGCOMM.
- Fegers, F. et al. (2019-2024). *Puffer: Practical RL for streaming*. Stanford.
- Watson, A. et al. (2015). *Per-title encode optimization*. Netflix Tech Blog.

### 视频生成
- Peebles, X. & Xie, S. (2023). *Scalable Diffusion Models with Transformers* (DiT). ICCV.
- Lipman, Y. et al. (2023). *Flow Matching for Generative Modeling*. ICLR.
- OpenAI (2024.2). *Sora 抢先看* blog.
- Yang, Z. et al. (2024). *CogVideoX: Text-to-Video Diffusion Models*. 智谱.
- Kong, W. et al. (2024). *HunyuanVideo: A Systematic Framework For Large Video Generation Models*. 腾讯.
- Team Wan (2025). *Wan: Open and Advanced Large-Scale Video Generative Models*. arXiv:2503.20314.
- Blattmann, R. et al. (2023). *Stable Video Diffusion*. Stability.
- Brooks, T. et al. (2024). *Video generation models as world simulators* (Sora).

### CV / 光流
- Lucas, B. & Kanade, T. (1981). *An iterative image registration technique*. IJCAI.
- Teed, Z. & Deng, J. (2020). *RAFT: Recurrent All-Pairs Field Transforms for Optical Flow*. ECCV.
- Kirillov, A. et al. (2023). *Segment Anything* (SAM). Meta.
- Ravi, N. et al. (2024). *SAM 2: Segment Anything in Images and Videos*. Meta.

## 三、进一步学习路径

### 入门路径（4 周）
1. **第 1 周**：跑 `code/audio/03_karplus_strong.py`、`code/audio/06_pitch_consonance.py`、`code/video/02_motion_estimation.py`。读 Huron《Sweet Anticipation》第 1-3 章。
2. **第 2 周**：跑 `code/audio/09_encodec_rvq.py`、`code/audio/10_musicgen_call.py`。读 MusicGen 论文。
3. **第 3 周**：跑 `code/video/07_3d_causal_vae.py`、`code/video/09_dit_block.py`。读 DiT 原论文。
4. **第 4 周**：跑 `code/video/12_wan2_inference.py`（需 GPU）。读 Wan / HunyuanVideo 论文。

### 深入方向

#### 想做音频生成研究
- 必读：EnCodec、MusicGen、Jasco、AudioLDM 2 论文
- 数据：MTG-Jamendo、FMA、MusicCaps
- 开源基线：MusicGen、Stable Audio Open、YuE

#### 想做视频生成研究
- 必读：DiT、CogVideoX、HunyuanVideo、Wan 论文
- 开源基线：Wan 2.1、HunyuanVideo、CogVideoX、Open-Sora
- 评估：VBench、EvalCrafter、FVD

#### 想做视频编码研究
- 必读：HEVC、AV1、VVC 标准 + DCVC 系列
- 开源编码器：x264、x265、SVT-AV1、VVENC
- 神经压缩：DCVC、DCVC-DC

#### 想做 ABR / 流媒体工程
- 必读：BOLA、Pensieve、Puffer 论文
- 开源：dash.js、Shaka Player、Puffer（数据开放）
- Netflix / YouTube 技术博客

#### 想做音乐认知研究
- 必读：Huron、Patel、Blood-Zatorre、Salimpoor 论文
- 实验工具：PsychoPy、EEGLAB、SPM

## 四、关键人物 / 实验室

### 音乐神经科学
- **Robert Zatorre** (McGill)：音乐愉悦的脑机制
- **David Huron** (Ohio State)：预测编码 + ITPRA
- **Aniruddh Patel** (Tufts)：音乐 vs 语言
- **Nina Kraus** (Northwestern)：音乐训练与大脑可塑性

### 音乐数学
- **Dmitri Tymoczko** (Princeton)：和声几何
- **Godfried Toussaint** (McGill, 已故)：节奏几何

### 音频生成
- **Alexandre Défossez** (Meta)：EnCodec、MusicGen
- **Jade Copet** (Meta)：MusicGen

### 视频生成
- **Sora 团队** (OpenAI)：Tim Brooks, Bill Peebles
- **Wan 团队** (阿里)：Shiwei Zhang 等
- **Hunyuan 团队** (腾讯)
- **Sora 复刻**：Open-Sora (HPC-AI Tech)、CogVideoX (智谱)

### CV / 视频
- **Jia Deng** (Princeton)：RAFT
- **Ross Girshick** 等：YOLO/SAM 系列

### 编码理论
- **Jarek Duda**：rANS（asymmetric numeral systems）
- **Gisle Bjøntegaard**：BD-rate 评估

## 五、社区与跟踪

- **HuggingFace Daily Papers**（cs.SD、cs.CV、cs.MM）
- **AK (@_akhaliq)** Twitter：每日前沿
- **机器之心 / 量子位**：中文报道
- **arXiv**：cs.SD（声音）、cs.CV（视觉）、cs.MM（多媒体）、eess.AS（音频信号）
- **顶会**：NeurIPS、ICML、ICLR、CVPR、ICCV、ECCV、ACL、ISMIR（音乐）、DCC（数据压缩）、SIGCOMM（网络）

## 六、开源模型清单（截至 2025.5）

### 音频生成
- MusicGen small/medium/large（Meta）
- Jasco（Meta）
- Stable Audio Open（Stability）
- YuE（m-a-p）
- ACE-Step
- Demucs v4（分离）
- EnCodec / DAC（编码）

### 视频生成
- Wan 2.1 1.3B / 14B（阿里）
- HunyuanVideo 13B（腾讯）
- CogVideoX 5B / 30B（智谱）
- Open-Sora 2.0（HPC-AI Tech）
- Mochi-1 10B（Genmo）
- LTX-Video 2B（Lightricks）
- Stable Video Diffusion（Stability）

### CV
- YOLO v8/v11/v12（Ultralytics）
- RT-DETR（百度）
- SAM 2（Meta）
- RAFT（Princeton）
- VideoMAE / VideoMAE V2（上海 AI Lab）

### 流媒体
- dash.js（参考播放器）
- Shaka Player（Google）
- Puffer（Stanford，数据开放）
- SVT-AV1（开源 AV1 编码器）
- x264 / x265 / VVENC
