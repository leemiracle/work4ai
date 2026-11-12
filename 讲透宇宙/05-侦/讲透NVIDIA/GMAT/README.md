# 讲透 GMAT

> **NVIDIA GMAT = "GPU toolkit on Multimedia, AI and Transcoding"**（前身 ffmpeg-gpu-demo，README.md:5 一手信源实证——非社区误传的"内存分析工具"）。ffmpeg-gpu（FFmpeg 5.1.2 Riemann LTS 全库 fork）+metrans（AvToolkit header-only C++ 封装=GMAT 本体）。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**24261n/42011e/16 层/16 步 tour**，fingerprints 4450@b1aea742——**understand 系列历史第一大图谱**（超 ogkm 16795n） |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 8495 字不计空格，58 锚） |
| explain 12 篇 | ✅ 2026-11-07 | `explain/01-12` 实测 **55311 字符**，387 锚（双组合计），主会话抽验 70 锚 0 坏 |

## 战况（201 批，80 分钟）

四 worker 大段滚动（1-50/51-100/101-150/151-201），一次 1308（写作期，双代理死前全落盘+复活完成质量修正）。merge 143 悬空边=100% 前缀错位，三态改写批量回补；522 件终验 24261 ID 唯一/4450 文件全覆盖零缺失。

## 甄别精选（源码级实证）

1. **GMAT 定位勘误**："GPU toolkit on Multimedia, AI and Transcoding"（README.md:5）非内存分析——layers/tour 全部按正确口径重写
2. **GMAT 本体=metrans/include/AvToolkit**（header-only C++ FFmpeg 封装；VidFilt 走 hwcontext_cuda+cudaBufferFree 零拷贝 GPU 帧）
3. **GMAT 相对上游 FFmpeg 增量收敛为四处**：滤镜群（tensorrt/cvcuda/cuda 三插槽+dnn 三后端=主战场）/SWS_HWACCEL_CUDA/configure 口子/doc+Dockerfile；5.1.2 Riemann LTS 基线 squash 单 commit 导入薄增量模式
4. **cnpy 子模块全仓零代码引用**（唯一消费者 doc/3DDFA_filter.md）；"ffmpeg_g"是链接产物非源码
5. FrameSelect.h:12 硬编码 `select_gpu` 与 fork 注册名 `select_cuda`（vf_select_cuda.c:604）不匹配——疑跨版本遗留
6. **SIMD 五架构大军**：x86 198/ARM 系 207/MIPS 120/LoongArch LSX+PPC+死架构遗存 101（avr32/bfin/sh4/sparc 墓碑 README 交接协议）；LoongArch LSX 大 __asm__ 文件 tree-sitter 全盲自研补扫器
7. libavcodec 根 1630 文件三分为框架 102/视频 1168/音频 360（aac 51/dca 30/opus 21 家族）；libavformat 341 demuxer/175 muxer

## 分层速览（16 层，4450 文件节点）

根构建(6) → NvCodec(44) → AvToolkit(49) → HevcParser(52) → metrans samples(102) → **视频编解码巨群(1168)** → libavformat(635) → libavfilter(198) → fftools(207) → x86 SIMD(120) → 死架构遗存(101) → 框架层(637→修正 102) → ARM SIMD(721) → libavutil(65) → MIPS/LSX/PPC(313) → tests 残留(307)

*2026-11-07 · cuda-stack-第七轮会话（舰队夜战）*
