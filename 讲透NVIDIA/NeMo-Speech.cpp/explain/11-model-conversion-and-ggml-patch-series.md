# 11 · 模型转换器群与 ggml 19 补丁系列（L13 · 67 节点群）

## 角色定位

L13 是全仓最大的外围层（67 节点）：Python 侧 `conversion/` 13 文件 + `convert_model.py` 统一入口，把 NeMo/HF checkpoint 转成运行时 GGUF；C/C++ 侧 `patches/` 19 个补丁 + `scripts/llama-patches.sh`，对 pinned llama.cpp submodule 施加 NVIDIA 定制。两者互为表里：转换器决定 GGUF 里存什么（张量命名/量化布局），补丁决定 ggml 怎么高效算它——如 `--q8-layout planar`（convert_model.py:41-44）对应 `ggml-cuda-skinny-q8_0-gemm-with-planar-weights.patch`，运行时再由 `keep_skinny_q8_weights_separate()` 兜底。

## 内部结构

**统一转换器**：`convert_model.py` 是唯一 CLI（source 位置参数 + 必选 --outfile，convert_model.py:18-24），`conversion/registry.py` 持 8 架构元组 `(asr, diarization, pnc, vad, tts, codec, nmt, s2s)`（registry.py:17）。自动探测双路：s2s 整仓源先用 `is_s2s_source/is_s2s_file_list` 特判（registry.py:95-105），其余读 .nemo 里的 model_config.yaml 按 target 字符串分发——sortformer→diarization、punctuationcapitalization→pnc、magpietts→tts、audiocodecmodel→codec、encoder+decoder/joint/labels→asr（registry.py:38-51）；nmt 不自研，委托 llama.cpp 的 `convert_hf_to_gguf.py`（checkout 由 `ensure_llama_checkout` 保证，registry.py:141-158）。五件主转换器 asr.py(740 行)/tts.py(476)/diarization.py(444)/codec.py(412)/s2s.py(565) 加 pnc/vad 小件、quantization.py 共享量化、source.py 下载解包。

**asr.py 的输出契约**（注释即规范，asr.py:6-28）：`general.architecture="asr"`、元数据命名空间 `asr.*`、`asr.head_type∈{ctc,rnnt,tdt}` 判别器；卷积权重保原生 3D 形状由运行时懒 reshape；RNNT LSTM 张量从 PyTorch `weight_ih_l0` 改名 `ih_l0.weight` 让 Linear 模块直接认领；位置编码解析预计算不拷 checkpoint。head 自动判定：config 有 `joint` 块⇒RNNT、仅 `labels`⇒CTC（asr.py:31-32）。

**量化矩阵**（quantization.py:23-33）：DEPLOYMENT_WEIGHT_TYPES 八档 bf16/fp16/q8_0/q6_k/q5_k/q4_k/mxfp4(38)/nvfp4(39)；量化路径优先 python gguf.quants，缺则 ctypes 回落 libggml（quantization.py:13-16、quantization.py:46）。逐架构默认 asr q8_0、diarization/vad f32、tts q8_0、codec f16、nmt f16、s2s q4_k_m（registry.py:110-122），越集即 ValueError 报全候选（registry.py:127-141）。s2s 是整仓转换：按组件钉格式（perception q8_0/llm_aux bf16/eartts_side q8_0/codec f32/tts_prompt f32，s2s.py:28-34），profile 别名 q4→q4_k_m、repro→bf16（s2s.py:35-40），并自动构建 quantizer（ConversionRequest.auto_build_quantizer=True，registry.py:34）。

**19 补丁系列**：series 按序列 19 文件——ggml-cuda 13 + ggml 3 + ggml-cpu 1 + llama 3（patches/series 全文）。主题三类：融合算子（fused attention for FastConformer/MagpieTTS、LayerNorm+scale+bias 融合、sigmoid GLU、SiLU→BF16 融合）；新硬件/新格式（Jetson Thor SM110、NVFP4 量化、F16 depthwise conv 权重）；基础设施（CUDA graph cache keys 与驱逐旋钮、backend stream 暴露、PAD 超过 65535 grid 限制的展平、tiled 1D im2col、vectorized set_rows、两列 MMVF epilogue、NanoCodec 卷积核、CPU F16C 标量路径）。每补丁带 `Upstream:` 行：10 个 candidate（缺基准/测试）、4 个 not planned（模型特定，如 NanoCodec/BF16 仿真）、1 个已有 open PR #29064 同改动。

## 外部连接

CMake 在 `NEMO_SPEECH_GGML_PATCHED=ON`（默认与 cuda-*/cpu-* preset）时把 submodule 拷到 `<build>/_deps/llama.cpp`、按序打补丁再编译，只在补丁或 pin 变化时刷新、只重写变更文件（patches/README.md:11-16）；metal-*/vulkan-* preset 用 OFF 走原味源（patches/README.md:17-18）。`scripts/llama-patches.sh` 五命令 edit/export/rebase/check/diff 维护系列（llama-patches.sh:16-31 usage 块）。转换器产物被 `tests/conversion/` 四契约测试锁死（converter_contract/tts_index_layout/tts_speaker_names/tts_tokenizer_profiles）；`models/index.json` 记录 sha256 供下载校验。

## 数据流

checkpoint（.nemo/HF repo/本地目录）→ source.py 拉取解包 → registry 探测架构 → 各转换器读 config+权重 → quantize → GGUFWriter 落盘（s2s 走多文件整仓）。补丁流：patches/series → CMake `git apply`（跳过 diff 前的提交头，patches/README.md:41-42）→ 编译进 build 树，源 submodule 始终 pristine。

## 设计决策——为什么 patch 而非 fork

README 第一段就钉死哲学："submodule pinned to an upstream commit and never modified"（patches/README.md:3-5）。三个理由：①**跟上上游**——每月 rebase 一次 pin，上游吸收的补丁变空自动删除（patches/README.md:89-94），fork 会漂成孤岛；②**审计与复用**——每个补丁是 format-patch 导出、带完整 blob index 支持 `git apply -3` 三方合并（patches/README.md:33-38），Upstream 行把"candidate/not planned"的回流状态显式化，一半以上以回流上游为目标；③**增量构建**——只重写被改文件，单补丁修改只触发受影响编译（patches/README.md:14-16）。配套纪律：禁止手编 patch 文件，一切经 worktree 提交 + `export` 重生成，CI 用 `check` 做字节级复现校验（patches/README.md:52-54）；两分支同加补丁时刻意让 series 末尾冲突（patches/README.md:83-85）。补丁命名带 area 前缀（ggml:/ggml-cuda:/ggml-cpu:/llama:，patches/README.md:45）。

## 新人提示

加新模型支持的正确路径：先在 registry 的 target 分发加判别（registry.py:38），再确认输出契约与 C++ 侧模块的命名约定对齐（参考 asr.py:6-28 的契约写法）。改补丁必须走 `scripts/llama-patches.sh edit` → worktree 里 `git commit --fixup` + `rebase -i --autosquash` → `export`（patches/README.md:59-72），直接改 .patch 文件会被 CI check 拒。rebase pin 后必跑 `test-backend-ops` 与 `check_backend_coverage`——上游收窄 `supports_op` 时被补丁的算子会**静默回落 CPU**（patches/README.md:96-100）。诊断环境变量（各补丁读取的）集中在 docs/development/diagnostics.md。`.deps/llama.cpp-patches` worktree 的提交永不离开本地（llama-patches.sh:8-13 头注释），放心实验。
