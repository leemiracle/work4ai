# 自测题：60 题检验理解

> 覆盖音乐 + 视频全 6 层金字塔。每题给考点 + 答案。
> 建议先答再看答案。

---

## 一、音乐 · 物理声学（8 题）

**Q1.** 为什么人耳对响度的感知是对数的（Weber-Fechner 律）？
<details><summary>答</summary>
进化压力：环境声音强度跨越 10⁶ 量程（耳语 vs 飞机）。对数压缩让有限的神经元动态范围能覆盖全量程。</details>

**Q2.** 泛音列的第 2、3、4 项对应什么音程？为什么所有文化的"协和音程"都在前几项？
<details><summary>答</summary>
八度（2f）、纯五度（3f）、再八度（4f）。协和感来自基底膜共振 + Plomp-Levelt 粗糙度曲线，是物理 + 生物决定的，不是任意文化约定。</details>

**Q3.** FFT 复杂度？为什么音频压缩用 MDCT 而不是 FFT？
<details><summary>答</summary>
FFT 是 O(N log N)。MDCT 有 **TDAC（时域混叠对消）**：相邻块重叠 50%，块边界噪声抵消 → 适合分块编码。MP3/AAC/Opus 全用 MDCT。</details>

**Q4.** MP3 128kbps 听起来"差不多"，为什么？
<details><summary>答</summary>
心理声学掩蔽：扔掉的是**人耳听不到的**（同时掩蔽 + 前/后向掩蔽 + 临界带宽外）。SMR 决定每个子带丢多少。</details>

**Q5.** 短时傅里叶（STFT）的"时频权衡"为什么存在？
<details><summary>答</summary>
Heisenberg 不确定性原理同样适用信号：长窗频率准但时间糊（适合低音）；短窗时间准但频率糊（适合瞬态如鼓）。</details>

**Q6.** CQT 和 FFT 的区别？为什么音乐分析用 CQT？
<details><summary>答</summary>
FFT 频率轴线性等分；CQT 每八度固定 bin 数（对数等分），完美对齐音阶。Spotify chroma 特征、和弦识别都用 CQT。</details>

**Q7.** CD 采样率为什么是 44.1 kHz 而不是 40 kHz？
<details><summary>答</summary>
Nyquist：人耳最高 ~20 kHz，需 ≥ 40 kHz；44.1 kHz 留余量给抗混叠滤波器（transition band）。历史原因：和录像带时代兼容。</details>

**Q8.** Dither（抖动）为什么能在量化前加噪声反而改善音质？
<details><summary>答</summary>
量化失真与信号相关（刺耳）；dither 让它变成与信号无关的白噪声（可被掩蔽）。是数字音频的精彩细节。</details>

---

## 二、音乐 · 数学（8 题）

**Q9.** 毕达哥拉斯五度相生律为什么会有"狼五度"？
<details><summary>答</summary>
$(3/2)^{12} = 129.746 \neq 2^7 = 128$，差一个 Pythagorean comma ≈ 23.46 音分。12 个五度回不到 7 个八度，必有一个调里的五度特别难听。</details>

**Q10.** 朱载堉 1584 算出的 $2^{1/12}$ 解决了什么问题？代价是什么？
<details><summary>答</summary>
12 平均律：所有调完全对称，可任意转调。代价：除八度外所有音程都微微弄脏（平均律纯五度 1.4983 < 真纯五度 1.5）。这是西方音乐征服世界的数学基础。</details>

**Q11.** Plomp-Levelt 协和曲线和 12-TET 是什么关系？
<details><summary>答</summary>
PL 曲线峰值位置与简单整数比吻合，**与是否 12-TET 无关**。但 12-TET 的音程最接近 PL 曲线协和峰，所以 12 是"自然选择"的结果。</details>

**Q12.** Tymoczko 的 orbifold $T^n/S_n$ 有什么奇怪性质？
<details><summary>答</summary>
① 边界"反弹"（B→C 时从另一侧弹回，因为模八度）；② 中点穿过自己（增三和弦在中点）。在这个空间里 voice leading = 几何最短路径。</details>

**Q13.** Toussaint 发现 Euclidean rhythm E(7,12) 对应哪个文化的节奏？
<details><summary>答</summary>
西非/古鲁巴 bell pattern（最经典的跨文化节奏）。E(3,8) 是古巴 tresillo / 巴西 samba。</details>

**Q14.** 为什么大三和弦 4:5:6 听起来"最协和"？
<details><summary>答</summary>
三个频率比都是小整数 → 在 PL 粗糙度曲线上都是低点 → 基底膜激活区不相互干涉 → 没有"拍"。</details>

**Q15.** 印度古典音乐为什么没有"和声"？
<details><summary>答</summary>
他们的美学是**水平线性**：单旋律 raga + drone（持续低音），不垂直叠加。印度音乐家会觉得"叠两个不同 raga"是混乱。</details>

**Q16.** 大调 = 快乐、小调 = 悲伤 是天然的还是文化的？
<details><summary>答</summary>
**主要是文化的**（Jacoby 2019 Nature Hum Beh，Tsimané 人对大调-小调情感判断几乎随机）。部分物理（大三度比小三度"亮"）。但节奏情感跨文化普适。</details>

---

## 三、音乐 · 神经 + 进化（8 题）

**Q17.** 为什么说耳蜗是"活体傅里叶分析仪"？
<details><summary>答</summary>
基底膜从底到顶**刚度递减**，某频率 f 在膜某位置最大共振。膜本身就把声音分解到频率位置（place coding）。Békésy 1961 诺奖。</details>

**Q18.** Salimpoor 2011 Nature Neuroscience 发现了什么？
<details><summary>答</summary>
PET+fMRI 显示：音乐高潮前的战栗时，**伏隔核多巴胺释放峰值提前高潮几秒**——大脑在"期待"中被奖赏。验证 Meyer 1956 期待理论。</details>

**Q19.** Huron 的 ITPRA 模型拆几个相位？
<details><summary>答</summary>
5 个：Imagination（事前想象）/ Tension（即将发生）/ Prediction（发生瞬间）/ Reaction（0.5s 后本能）/ Appraisal（几秒后理性）。所有音乐情绪工程都是这 5 相位的把玩。</details>

**Q20.** 音乐性 frisson（鸡皮疙瘩）和什么人格特质相关？约多少人能体验？
<details><summary>答</summary>
与 **Openness to experience** 强相关。约 **50%** 的人能稳定体验。前扣带回 + 右侧壳核激活，与社交/性/食物奖赏**共用回路**。</details>

**Q21.** 为什么失语症患者仍能唱歌？
<details><summary>答</summary>
Patel SHARE 模型：音乐和语言共享一些资源（句法加工），但有分离。Melodic Intonation Therapy 用唱歌帮助失语症康复。</details>

**Q22.** Pinker 1997 说音乐是"听觉奶酪蛋糕"，2024 年学界怎么看？
<details><summary>答</summary>
多数进化心理学家**已放弃** Pinker 的"副产品"说。音乐的普遍性、跨文化结构相似、对大脑强重塑、深度劫持奖赏回路，都指向**多效性适应**。Mehr & Krasnow 2021 "music as credible signal" 是新主流。</details>

**Q23.** Wiltermuth & Heath 2009 Science 实验证明了什么？
<details><summary>答</summary>
陌生人分组同步走路 vs 不同步，之后合作游戏——**同步组明显更合作、更信任**。给现场演唱会、宗教仪式的凝聚力提供神经-进化解释。</details>

**Q24.** "歌声选择性神经元"是什么时候发现的？
<details><summary>答</summary>
Norman-Haignere et al. (2022)，在癫痫患者颅内电极记录中发现人听皮层有专门响应"歌声"的神经元群——和语音、乐器声分开。是音乐神经科学的"人脸纺锤体"发现。</details>

---

## 四、音乐 · 技术与 AI（10 题）

**Q25.** RVQ（Residual Vector Quantization）相对单一 VQ 的优势？
<details><summary>答</summary>
多级残差堆叠：第一级编主要信息，第二级编残差，第 N 级编更细的残差。按码率灵活选择级数（1.5-24 kbps）。是 EnCodec / 所有音频 LLM 的基础。</details>

**Q26.** Karplus-Strong 算法为什么这么简单（一个延迟线 + 低通）就能合成拨弦？
<details><summary>答</summary>
延迟线长度 = 一个周期（决定音高）；平均运算 = 低通滤波（高频先衰减 → 自然拨弦音色）。是 Stanford CCRMA 数字波导理论的鼻祖。</details>

**Q27.** FM 合成公式 $y=\sin(2\pi f_c t + I\sin(2\pi f_m t))$ 中，fm/fc 决定什么？
<details><summary>答</summary>
**泛音结构**：整数比 → 泛音都是 fc 倍数（和谐，电钢琴）；非整数比（如 √2）→ 非整数倍泛音（不和谐，钟声/铜管）。I 决定泛音丰富度。</details>

**Q28.** Opus 编解码器为什么能在低延迟下同时处理语音和音乐？
<details><summary>答</summary>
**动态切换 SILK（语音 CELP）和 CELT（音乐 MDCT）**：语音段用 SILK 低码率清晰，音乐段用 CELT 保质量。WebRTC/Zoom/Discord 全用 Opus。</details>

**Q29.** WaveNet 慢的根本原因？
<details><summary>答</summary>
每秒 16k 个采样点，**逐点自回归**预测 μ-law 256 类。1 秒音频要几十秒生成。后续 parallel WaveNet / Jukebox 解决。</details>

**Q30.** MusicGen 的 "delay pattern" 解决什么问题？
<details><summary>答</summary>
EnCodec 多码本（典型 4-8 个），每步同时预测所有码本会破坏自回归因果。Delay pattern：第 c 个码本延迟 c 步，确保每步只预测一个新 token，统一 attention。</details>

**Q31.** Suno v4 和 MusicGen 的核心差别？
<details><summary>答</summary>
MusicGen 单段 ~30s、无歌词；Suno **3-4 分钟完整歌曲**（verse-chorus 反复）+ 歌词驱动。Suno 据信是大规模多码本自回归 + 长上下文 + 数百万小时训练数据。</details>

**Q32.** Demucs v4 用什么架构分离人声/鼓/贝斯？
<details><summary>答</summary>
时间域 U-Net + Transformer。分离质量已接近专业 stems，是 Karaoke、remix 工具的算法基础。</details>

**Q33.** MFCC 提取的 4 步是什么？
<details><summary>答</summary>
FFT → Mel 滤波器组（对数频率）→ log → DCT。前 13 维通常足够。是语音/音乐识别通用特征。</details>

**Q34.** 音频 LLM 当前最大未解难题？
<details><summary>答</summary>
① 长结构（Transformer context 有限，几十秒后漂走）；② 可解释控制（改"这里换小调"）；③ 模型真懂乐理吗？多数证据否定。</details>

---

## 五、视频 · 物理 + 信号（6 题）

**Q35.** 为什么人眼对蓝色细节不敏感？这导致什么视频压缩技术？
<details><summary>答</summary>
S 锥细胞少，且 L/M 锥密集。导致 **YCbCr + 4:2:0 色彩子采样**：Y 全分辨率，Cb/Cr 减半 → 砍 50% 数据肉眼几乎看不出。</details>

**Q36.** 电影为什么是 24 fps？180° 快门法则做什么？
<details><summary>答</summary>
1920s 妥协（便宜 + 临界融合）。180° 法则：曝光时间 = 帧间隔一半 → 自然运动模糊 → 大脑读为"虚构叙事"。高帧率（48fps《霍比特人》）反而像肥皂剧。</details>

**Q37.** Phi 现象是什么？和电影的关系？
<details><summary>答</summary>
Wertheimer 1912：两光点 < 60 ms 间隔闪 → 大脑感知移动。**电影成立的最基本神经机制**——大脑被骗了。</details>

**Q38.** 2D DCT 后能量集中在哪里？JPEG 怎么利用？
<details><summary>答</summary>
左上角（DC + 低频）。JPEG：8×8 块 DCT → 量化矩阵除（高频除以大数 → 多变成 0）→ zigzag + RLE + Huffman。</details>

**Q39.** 视频压缩利用哪四种冗余？
<details><summary>答</summary>
① 空间冗余（一帧内平滑）→ DCT/帧内预测；② 时间冗余（相邻帧相似）→ 运动补偿；③ 统计冗余（高频符号）→ 熵编码；④ 心理视觉冗余（人眼看不到的高频）→ 量化。</details>

**Q40.** MT/V5 区神经元做什么？和视频编码的关系？
<details><summary>答</summary>
**运动方向选择性放电**——光流的硬件。视频编码的"运动估计"和 CV 的"光流"算法在数学上是同一件事，在生物学上对应同一群神经元。</details>

---

## 六、视频 · 编码算法（12 题）

**Q41.** I / P / B 帧的区别？GOP 是什么？
<details><summary>答</summary>
I 帧：独立编码（像 JPEG）；P 帧：前向预测（存 MV+残差）；B 帧：双向预测。GOP = 一个 I + 一串 P/B。短 GOP 利于 seek/低延迟；长 GOP 高压缩率。</details>

**Q42.** 运动估计中 SAD vs SATD 的区别？
<details><summary>答</summary>
SAD = Sum of Absolute Differences（简单）；SATD = Hadamard 变换后的绝对值和（更准但慢，更接近实际编码失真）。</details>

**Q43.** 亚像素运动估计（1/4 像素）为什么能省码率？
<details><summary>答</summary>
真实运动不一定整数像素对齐。1/4 像素精度需 Wiener 插值滤波器，让 H.264 比 H.263 节省 ~20% 码率。</details>

**Q44.** H.264 的核心创新？
<details><summary>答</summary>
16×16 宏块 + 子块分割；整数 DCT（避免浮点误差）；1/4 像素 ME；CABAC；多参考帧（最多 16）；环路去块滤波。比 MPEG-2 省 ~50%。</details>

**Q45.** HEVC 的 CTU 64×64 四叉树分割解决什么问题？
<details><summary>答</summary>
H.264 宏块固定 16×16 不能适应不同复杂度区域。CTU 递归分割：平滑区域用大块（64×64），复杂区域细分到 8×8。比 H.264 又省 ~50%。</details>

**Q46.** AV1 为什么选 rANS 而不是 CABAC？
<details><summary>答</summary>
CABAC 强串行（每步依赖前一步）；**rANS 状态机式整数编码，GPU/并行友好**。AV1 选 rANS 适合硬件加速。</details>

**Q47.** AV1 的 CDEF 是什么？
<details><summary>答</summary>
Constrained Directional Enhancement Filter — 方向性增强滤波，沿图像边缘方向去块。比 HEVC 的 SAO 更智能。</details>

**Q48.** AV1 的 Film Grain Synthesis 解决什么问题？
<details><summary>答</summary>
胶片颗粒是高频随机噪声 → 难压缩。AV1 把颗粒剥离后参数化（mean, variance），解码端用参数合成。省码率同时保留质感。</details>

**Q49.** 神经视频压缩（NVC, DCVC 系列）的核心思路？
<details><summary>答</summary>
端到端神经网络：编码器 CNN 把帧 + 参考特征 → latent；hyperprior 神经熵模型 + 自回归上下文 → 比特流；多帧特征检索（DCVC-DC/FM）。低码率超 VVC，但慢。</details>

**Q50.** HEVC 专利问题为什么催生 AV1？
<details><summary>答</summary>
HEVC 有 3 个专利池（MPEG LA、HEVC Advance、Technicolor）几百专利，授权复杂昂贵。Google/Netflix/Amazon/MS 等成立 AOMedia 推 AV1 免版税。</details>

**Q51.** VVC 的 AFFINE 运动模型相比传统块匹配的优势？
<details><summary>答</summary>
传统假设块刚性平移（一个 MV）。AFFINE 用 6 参数模型（旋转、缩放、剪切）—— 适合 zoom、旋转镜头、波浪等非刚性运动。</details>

**Q52.** 帧间预测和光流的区别？
<details><summary>答</summary>
运动估计是**块级、离散 MV**（编码友好，码率小）；光流是**逐像素连续**（更细但码率大）。HEVC AFFINE 介于两者之间。</details>

---

## 七、视频 · 流媒体 + AI 生成（8 题）

**Q53.** BOLA 算法的核心思想？为什么简单但理论最优？
<details><summary>答</summary>
**只看缓冲区水位**：满 → 选高码率；空 → 选低码率。Lyapunov 优化证明接近最优（BOLA-BASIC 是 dash.js 默认）。</details>

**Q54.** Pensieve 为什么是 ABR 算法里程碑？
<details><summary>答</summary>
MIT Mao et al. SIGCOMM 2017：**首次用 RL（A3C）学 ABR 策略**，在所有测试场景超越 BOLA/MPC/BB。证明 RL 在生产级网络问题上有用。</details>

**Q55.** Puffer 比 Pensieve 进一步做了什么？
<details><summary>答</summary>
**真实在线学习**：Stanford 部署真实流媒体 6+ 年，每天收集数据 + 在线更新。Fugu（2020）用 Bayesian NN 建模吞吐量不确定性。数据全开放。</details>

**Q56.** Per-title 编码解决什么问题？
<details><summary>答</summary>
动画和动作片用相同码率 ladder 是浪费。Netflix 2015：每部片单独训练"码率-分辨率"曲线选最优 ladder。后续升级 per-shot + AV1 per-shot。</details>

**Q57.** 为什么视频生成用 3D causal VAE 而不是 2D VAE？
<details><summary>答</summary>
2D VAE 只压空间。视频需**时空联合压缩**（典型 4×8×8 = 256× 压比）。**因果卷积**只用过去帧，避免训练时未来泄漏 → 保证自回归长视频生成可行。</details>

**Q58.** Flow Matching 相比 DDPM 的优势？
<details><summary>答</summary>
① 训练更稳（无 schedule 敏感性）；② 推理步数少（rectified flow 几步即可）；③ 数学简洁（学 vector field 而非噪声）。所有 2024-2025 主流视频模型用。</details>

**Q59.** Classifier-Free Guidance 的公式？
<details><summary>答</summary>
$\epsilon_{\text{guided}} = \epsilon_{\text{cond}} + w(\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})$。训练时随机 drop 文本 10-20%；推理时混合条件和无条件预测。$w$ 越大越服从文本，但多样性下降。</details>

**Q60.** Sora 失败案例（玻璃杯穿过桌面）说明什么？
<details><summary>答</summary>
**视频模型学的是"像素相关"，不是"物理因果"**。这是"视频模型 ≠ 真世界模型"的核心证据。LeCun 因此反对生成式世界模型，主张 JEPA 预测抽象 latent。</details>

---

## 评分

- 55-60：大师级 ✨
- 45-54：扎实 🎯
- 30-44：入门 📚
- <30：建议从 §一 物理声学开始重读

## 错题复习建议

- 错物理题（1-8, 35-40）：重读 `code/audio/01_fourier_stft_mdct.py` 和 `code/video/01_dct_jpeg.py`
- 错神经题（17-24）：读 Huron《Sweet Anticipation》、Patel《Music, Language, and the Brain》
- 错编码题（41-52）：跑 `code/video/02_motion_estimation.py`、`04_h264_pipeline.py`
- 错 AI 题（25-34, 53-60）：跑 `code/audio/09_encodec_rvq.py`、`code/video/09_dit_block.py`、`12_wan2_inference.py`
