# 音乐 & 视频：全视角深度讲解

> 把"音乐"和"视频"这两个看似无关的主题，用 **物理 → 数学/信号 → 神经/感知 → 进化/心理 → 文化 → 工程压缩 → AI 生成** 七层金字塔讲透。
> 每层都给「直觉 → 数学/算法 → 可运行代码」。覆盖**所有核心算法**（FFT/MDCT/CABAC/rANS/RVQ/DiT/Flow Matching/3D-RoPE/BOLA/Pensieve 等）。

## 目录结构

```
notes/music-video-deep-dive/
├── README.md                       ← 本文件（导航）
├── full-text.md                    ← 完整 6 篇长文（音乐3篇 + 视频3篇 + 总结对照）
├── code/
│   ├── README.md                   ← 代码运行说明
│   ├── audio/                      ← 10 个音频算法（零外部依赖，可独立跑）
│   │   ├── 01_fourier_stft_mdct.py
│   │   ├── 02_psychoacoustic_masking.py
│   │   ├── 03_karplus_strong.py
│   │   ├── 04_fm_synthesis.py
│   │   ├── 05_subtractive_synth.py
│   │   ├── 06_pitch_consonance.py
│   │   ├── 07_euclidean_rhythm.py
│   │   ├── 08_mfcc_chroma.py
│   │   ├── 09_encodec_rvq.py
│   │   └── 10_musicgen_call.py
│   └── video/                      ← 12 个视频算法
│       ├── 01_dct_jpeg.py
│       ├── 02_motion_estimation.py
│       ├── 03_chroma_subsampling.py
│       ├── 04_h264_pipeline.py
│       ├── 05_abr_bola.py
│       ├── 06_pensieve_abr.py
│       ├── 07_3d_causal_vae.py
│       ├── 08_flow_matching.py
│       ├── 09_dit_block.py
│       ├── 10_3d_rope.py
│       ├── 11_optical_flow_lk.py
│       └── 12_wan2_inference.py
├── architectures/
│   ├── hunyuanvideo_dual_stream_dit.md   ← 双流 DiT 深入拆解
│   ├── wan21_architecture.md             ← Wan 2.1 架构分析（含 arXiv:2503.20314）
│   ├── sora_what_we_know.md              ← Sora 已知信息汇总
│   └── musicgen_vs_suno.md               ← 音乐生成模型对比
├── quiz/
│   └── self_test.md                ← 60 道自测题（含答案与考点）
└── refs.md                         ← 参考文献 + 进一步学习路径
```

## 快速开始

```bash
# 1. 阅读全文
$EDITOR full-text.md

# 2. 跑音频算法（零额外依赖，numpy/scipy 即可）
cd code/audio
python3 03_karplus_strong.py     # 拨弦物理建模 → 写出 karplus.wav
python3 06_pitch_consonance.py   # 画出 Plomp-Levelt 协和曲线
python3 07_euclidean_rhythm.py   # 打印世界音乐的 Euclidean 节奏

# 3. 跑视频算法（torch + numpy）
cd ../video
python3 02_motion_estimation.py  # 块匹配运动估计
python3 09_dit_block.py          # DiT block 前向
python3 10_3d_rope.py            # 3D RoPE 实现

# 4. 自测
cd ../..
cat quiz/self_test.md
```

## 七层金字塔（贯穿音乐 + 视频）

```
物理波动 ──→ 感知换能 ──→ 大脑预测编码 ──→ 文化语法 ──→ 工程压缩 ──→ AI 生成
 (FFT/DCT)   (耳蜗/视网膜)  (Friston/MT)    (调式/蒙太奇) (CABAC/rANS) (DiT/RVQ)
```

## 一句话总结

> 音乐和视频，都是人类用生物硬件感知、用文化语法编码、用工程算法压缩、用生成模型复刻的"时间序列信号"。它们共享同一个数学骨架：**傅里叶 + 信息论 + 概率**。
