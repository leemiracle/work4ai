# 讲透 NeMo-Speech.cpp

> NVIDIA NeMo C++ 语音 SDK：**ggml 推理运行时上的 ASR/TTS/S2S 全家**——engine_registry 引擎注册+cublas_shim WMMA 替身+flashlight_decoder+FastConformer+MagpieTTS（C++ 主体+四 CUDA 融合内核+NanoCodec 声码器）+S2S VoiceChat 80ms 步进流水线+NMT 翻译+riva gRPC/HTTP/Realtime 服务层+mandarin G2P+ggml 19 补丁群。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-12 | 仓内 `.understand-anything/knowledge-graph.json`：**1037n/1513e/16 层/16 步 tour**，双 validate 0/0，fingerprints 460@e680fc30 |
| onboarding | ✅ 2026-11-12 | `onboarding/ONBOARDING.md`（8 节 6998 字不计空格，63 锚） |
| explain 12 篇 | ✅ 2026-11-12 | `explain/01-12` 合计 **51460 字符**，426 锚（两组写手；组 2 204 锚全量终验 0 坏；主会话抽验 shim 符号表/补丁数/soname 3/3） |

## 战况（35 批，双 worker 分段，跨 1308）

前段 worker 死于终验锚抽验期（死前 18 批全落盘并自验 675n/984e）；后段 worker 完成 19-35（362n/561e）。merge 1037n/1513e，6 条悬空全为前缀错位（`file:→config:CMakeLists.txt`×4+`config:config/` 双前缀×2）手工回补 5 条。**scanner 对 C++ 几乎全盲**：imports 140 条全为 worker 源码重扫；flashlight_decoder.cpp 570 行/MagpieTTS 四 .cu 1212-1473 行完全零提取手工补齐。

## 甄别精选（源码级实证）

1. **cublas_shim**：in-tree drop-in cuBLAS 替身（native GEMM 无 cuBLASLt）——Linux 用 `kernels/ver_cublas.map` 生成符号 map+匹配 SONAME，Windows 走 dllexport；release 构建可替换真 cuBLAS 缩运行时闭包
2. **ggml 19 补丁群"patch 而非 fork"**：patches/series 16 ggml+3 llama，keep_cuda_graphs_resident/planar Q8 等运行时隐式依赖三主题分类+Upstream 回流状态
3. **MagpieTTS 四 CUDA 融合内核**：26→11 launch 合并/环形 KV/cub top-k/chain_common（1212-1473 行 .cu/.cuh）
4. **S2S VoiceChat**：七 GGUF 装配+80ms 步进循环+双 RNN-T 预测器+CFG 槽位连续升序约束+Q=31 静音码+turn-taking 状态机
5. **Silero VAD 一次推理双消费**（掩码+端点）；Sortformer v2/v3+AOSC；profanity→ITN→PnC 链序+BERT 双头 PnC
6. **mandarin G2P**：jieba/pypinyin 蒸馏成四张 LFS 表+最长词组匹配+HMM 回退——本地零 Python 依赖
7. **ASR 测试矩阵 23 个 test_*.cpp**（"17 文件"为旧口径，盘上实证 23）
8. riva_server Auto 三态+优雅停机；OpenAI 风格 HTTP+双 realtime WebSocket 端点
9. flashlight_decoder 的 BoostedLm 对称校准/OOV 克隆（570 行 scanner 全盲代表作）

## 分层速览（16 层，484 文件节点）

构建/CI/容器(46) → ggml 运行时与引擎注册(14) → 公共库与 C ABI SDK(26) → ASR 核心(12) → VAD/diar/后处理(28) → TTS 门面(7) → MagpieTTS 主体(20) → CUDA 内核+NanoCodec(12) → S2S VoiceChat(32) → NMT/服务层(32) → CLI/示例(40) → 解码器算法层(21) → 分词器与数据(22) → 转换/补丁/工具(67) → 文档(34) → 测试矩阵(71)

*2026-11-12 · cuda-stack-第七轮会话（舰队夜战 · 1308 双杀恢复轮收官）*
