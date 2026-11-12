# 03 · VisualGen 视觉生成：扩散竖线与五家 DiT 的推理落地

## 角色定位

VisualGen 是与 LLM 并立的第二条产品竖线：Diffusion-Transformer（DiT）图像/视频生成。它**不是 LLM 后端**（AGENTS.md 明言）——自有引擎（DiffusionExecutor）、自有参数（VisualGenArgs）、自有输出，但与 LLM 共享注意力/量化/并行算子。公共 API 在 `tensorrt_llm/visual_gen/`（用户面，`VisualGen` 主类 visual_gen.py:189，`generate`/`generate_async` :344/:368，配置 args.py:686），实现全部沉在 `_torch/visual_gen/`。

## 内部结构（五家模型谱系）

**Cosmos3 世界模型**（models/cosmos3/）：最大件是 3218 行管线 `Cosmos3OmniMoTPipeline`（pipeline_cosmos3.py:431，文本/图像/动作/音频多模态生成）与 2058 行主干 `Cosmos3VFMTransformer`（transformer_cosmos3.py:1071）。独特点是**复用 Qwen3-VL 语言域**：Qwen3VLTextRMSNorm（transformer_cosmos3.py:224）、Qwen3VLTextRotaryEmbedding（transformer_cosmos3.py:949）、MRoPE，配 `DomainAwareLinear`（transformer_cosmos3.py:393）分域投影。动作条件化在 action.py：`EMBODIMENT_TO_DOMAIN_ID`（action.py:25）与 `EMBODIMENT_TO_RAW_ACTION_DIM`（action.py:56）把本体名映射到 domain id 与动作宽度（本体属性而非超参）。音频走 Oobleck 解码器（sound_tokenizer.py）。

**FLUX.1/FLUX.2 文生图**（models/flux/）：FLUX.1 是移植版 `FluxTransformer2DModel`（transformer_flux.py:560，939 行，MMDiT 双流块+AdaLayerNorm）；FLUX.2 是**原生重写** `Flux2Transformer2DModel`（transformer_flux2.py:440，886 行，`Flux2Modulation` transformer_flux2.py:141）。注意力 `FluxJointAttention`（attention.py:39）处理文本+图像双流 QKV 拼接，FLUX.2 变体 `Flux2ParallelSelfAttention`（attention.py:315）继承它。

**LTX-2 两阶段视频**（models/ltx2/）：单阶段 `LTX2Pipeline`（pipeline_ltx2.py:630，2131 行，TeaCache+扰动指纹进 CUDA graph key）；两阶段 `LTX2TwoStagesPipeline`（pipeline_ltx2_two_stages.py:1017）=低分辨率去噪+`LatentUpsampler`（ltx2_core/upsampler.py:159）升 latent 再精化。主干 `LTXModel`（transformer_ltx2.py:1515，2556 行）的 BasicAVTransformerBlock 一个块同时初始化视频/音频/跨模态三组模块；瓦片并行 VAE 用 LPT 贪心 `assign_tiles_lpt`（parallel_vae.py:43）。

**WAN 视频+NVFP4 VAE**（models/wan/）：`wan_vae.py`（1849 行，wc -l 实证）——`NVFP4WanCausalConv3d`（wan_vae.py:780，FP4 因果卷积含预量化/反量化与 SiLU/norm 吸收）+`swap_wan_convs_to_fp4`（wan_vae.py:1022）整网替换入口；`load_wan_vae`（vae_loader.py:335）按 checkpoint 特征选 diffusers 或原生实现。dup_up3d.py 融合通道复制与 pixel-shuffle，`_supports_triton_indexing`（dup_up3d.py:21）守住 int32 偏移 2^31 硬边界并自动回退。

**MiniMax-H3 音视频**（models/minimax_h3/）：FL2VA checkpoint 落地——`MiniMaxH3Pipeline`（pipeline_minimax_h3.py:130，824 行）+`MiniMaxH3Transformer3DModel`（transformer_minimax_h3.py:430，877 行）；`build_packed_sequence`（packing.py:250）把视频+音频 token 打包进单序列。

## 外部连接

- **执行引擎**：`_torch/visual_gen/executor.py` 的 `DiffusionExecutor`（executor.py:447）在 worker 进程加载 pipeline 循环消费请求，`DiffusionRemoteClient`（executor.py:840）是协调侧代理（ZeroMq IPC）；单节点自 spawn、多节点对接外部启动器。
- **注意力后端独立成系**：`attention_backend/` 六后端（cuDNN/CuTe DSL/FA4/FlashInfer/TRTLLM/Vanilla）+三种序列并行包装（Ulysses/2D/Ring），工厂（attention_backend/utils.py:33）全部延迟导入；稀疏线 VSA/SOL 各有预测器+双后端。
- **与 LLM 线共享**：`VisualGenMapping`（mapping.py）一张 DeviceMesh 覆盖 CFG/TP/CP/Ulysses 全轴并可 `to_llm_mapping` 复用进程组；量化算子互通。服务走 `trtllm-serve <HF id> --visual_gen_args <YAML>`（openai_video_routes.py TYPE_CHECKING 隔离）。

## 数据流

`VisualGen(model, args)` → AutoPipeline 按 checkpoint 探测组件 →（远程模式）spawn DiffusionExecutor worker → `generate(prompt, params)`：文本编码出条件嵌入 → 去噪循环（DiT 前向 × N 步，每步注意力按 timestep 切 dense/sparse 相）→ latent 交 VAE 解码（WAN 可整网 FP4，LTX-2 两阶段升采样）→ VisualGenOutput 落盘。WAN 逐 token AdaLN（utils_wan.py 的 WanPerTokenAdaLN 六参数拆三组 gate）与激活+量化融合（fp4_fused_quant.py）是 decode 热路径两大融合点。

## 设计决策

1. **用户面/实现面硬隔离**：`tensorrt_llm/visual_gen/` 是冻结 API（改动须向用户确认），实验沉 `_torch/visual_gen/`；ENGINEERING_CRITERIA.md 区分 lossy/lossless 变更门槛。
2. **移植 vs 原生的分界**：LTX-2 core 与 FLUX.1 保留移植痕迹（版权头/键重映射），FLUX.2 按 TRT-LLM 原生算子重写——以"能否吃到原生融合"为准。
3. **量化做到卷积层**：WAN 把 NVFP4 做进 CausalConv3d 而非只做 Linear——VAE 解码带宽才是视频生成大头。

## 新人提示

- 入口顺序：visual_gen.py:189 → args.py:686 → executor.py:447 → 挑一家管线。视频先读 WAN（DiT+VAE+蒸馏最典型），再读 LTX-2 学两阶段与瓦片并行。
- 勘误：图谱把 executor 说成"引擎"——真名 DiffusionExecutor，且单节点也走子进程（自 spawn worker），非进程内调用。
