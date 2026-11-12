# ③ minimal_v4_dit 骨干与 VAE/文本编码器三件套

## 角色定位

`networks/minimal_v4_dit.py`（1989 行）是 DreamDojo 全部生成模型的**共同 DiT 基座**：预训练 text2world、动作条件 action、交互式 Self-Forcing 学生、多相机 camera 变体全部由 `MiniTrainDIT`（1418 行类）或其子类驱动（`interactive/networks/dit_action_causal.py:38` 的因果版、`camera/networks/dit_multiview_camera.py` 的多相机版）。配套三件套：`tokenizers/` 把视频压进 Wan VAE 潜空间，`text_encoders/`、`networks/clip.py`、`inference/get_umt5_emb.py` 提供文本条件，经 `conditioner.py:397` `GeneralConditioner` 统一注入。

## 内部结构

**注意力算子可插拔**（minimal_v4_dit 独有的关键设计）：三个自由函数 `torch_attention_op`（268，torch SDPA 兜底）、`flex_attention_op`（292，FlexAttention+128 对齐 padding，307-308 行 `((S+127)//128)*128-S`）、`i4_attention_op`（363，直通 imaginaire 统一前端 `attention()`）由 `Attention` 模块（389）按 `backend` 参数五选一（439 行断言：transformer_engine/torch/torch-flex/minimal_a2a/i4）。q/k 各配 `te.pytorch.RMSNorm`（455），Wan 兼容路径 `use_wan_fp32_strategy` 在 RoPE 前强制 q/k 升 fp32。交叉注意力子类 `I2VCrossAttention`（596）复用同一模块（context_dim 非 None 即交叉态）。

**3D RoPE**：`VideoRopePosition3DEmb`（685）把 head_dim 按 2:1 切给 H/W/T（709-711：`dim_h=dim//6*2`，时间维拿剩下 `dim-2*dim_h`）；每维独立 NTK 外推因子（727-729 `extrapolation_ratio**(dim/(dim-2))`）；`generate_embeddings`（744）按 fps 调制时间轴（784-795：`seq[:T]/fps*base_fps`，非均匀 fps 断言 batch=1 或 T=1），输出 `(t h w) 1 1 d` 直接喂 TE 的 `apply_rotary_pos_emb`（53-55 行按 transformer_engine 版本选 import 路径）。

**选择性激活检查点（SAC）**：`CheckpointMode` 枚举（182）九档——NONE/MM_ONLY/BLOCK_WISE 之上叠加五个逐硬件调优档（PREDICT2_2B_720、14B_720、2B_AGGRESSIVE、2B_AGGRESSIVE_V2、14B_AGGRESSIVE）。每个档对应一个 policy 工厂（69-165）：如 `predict2_2B_720_context_fn`（69）对 `torch.ops.aten.mm.default` 计数取模 16（79 行，对应 6+4+4+2=16 个 block），前 8 个 mm 重算、后 8 个 MUST_SAVE（80-81）；`aggressive_v2`（113）干脆全重算。`selective_activation_checkpoint.py:34` 还有第三份只含基础三值的 `CheckpointMode`——**全仓四处平行定义**（另两处 camera 版 171/172），改枚举须四处同步。

**模型主体 MiniTrainDIT**（1418）：patch embed（992）→ timestep/Fourier 嵌入（873/897/937）→ AdaLN-LoRA 调制（`modulate` 869）→ 28+ 个 `Block`（1144，self-attn+cross-attn+GPT2FeedForward 238）→ `FinalLayer`（1062）。构造参数（1479-1522）里 `n_dense_blocks`（1517）与 `natten_parameters`（1518）控制稀疏注意力替换：`replace_selfattn_op_with_sparse_attn_op`（1919）把指定层换成 `NeighborhoodAttention`（`modules/neighborhood_attn.py`）。FSDP2 的 `fully_shard`（42 import）与 `ptd_checkpoint_wrapper`（43）都在此文件接线。

**VAE 侧**：`tokenizers/interface.py:25` `VideoTokenizerInterface` 定契约（encode/decode/latent 帧数换算/压缩因子八属性）；两实现 `wan2pt1.py`（Wan2.1 VAE，1064 行）与 `wan2pt2.py`（Wan2.2，1133 行），另有 930 行的 `wan2pt1_2d_plugins.py` 图像 2D 插件。**勘误**：`tokenizers/cosmos.py`（28 行）不是 Cosmos VAE，只是 LazyCall 配置注册表（22-28 行注册 `Wan2pt1VAEConfig` 等，含一个指向内网 s3 的 GCP 变体）。

**文本编码器三系**：①Reason1（主力）：`text_encoders/text_encoder.py:69` `TextEncoder` 包装 `text_encoders/reason1.py:31` `QwenVLBaseModel`（文件头 17-19 行明言"从 reason1/models/vlm_qwen.py 改造，主要变更是返回 hidden states"）；`compute_text_embeddings_online`（131）：chat 模板 tokenize → 512 token pad/截断（34 行 `NUM_EMBEDDING_PADDING_TOKENS=512`）→ 逐层 mean_normalize（196-198）→ 三种拼接策略 FULL_CONCAT/MEAN_POOLING/POOL_EVERY_N（201-216）；meta device 实例化+FSDP 广播加载（75-110）。②UMT5：`inference/get_umt5_emb.py` 自带全套 T5 栈（T5Encoder 327、T5Model 410、`umt5_xxl` 482、`UMT5EncoderModel` 542），支持 DCP/S3 加载（509/517）。③CLIP：`networks/clip.py` 手写 OpenCLIP 移植（XLMRobertaCLIP 309、CLIPModel 503、Wan2pt1CLIPEmb 541），服务 Wan2pt1 文生图线。

## 外部连接

`MiniTrainDIT` 的消费方矩阵：`models/text2world_model_rectified_flow.py`（build_net 211 行 lazy 实例化）、`action/models/` 的 `ActionChunkConditionedMinimalV1LVGDiT`（`action/networks/action_conditioned_minimal_v1_lvg_dit.py`，因果版基类）、`interactive/networks/dit_action_causal.py:38`（KV cache+CUDA graph 扩展）、camera 三变体。上下文并行经 `networks/a2a_cp.py` 的 `MinimalA2AAttnOp/NattenA2AAttnOp`（63 行 import）。tokenizer 被 `Text2WorldModelRectifiedFlow` 以 `lazy_instantiate(config.tokenizer)` 装配并强校验 `latent_ch==state_ch`（`text2world_model_rectified_flow.py` __init__ 段）。

## 数据流

训练前向：视频 `[B,3,T,H,W]` → VAE encode → `[B,48,T',H',W']` 潜变量（Wan VAE 4×8×8 压缩）；文本 → Reason1 各层 hidden states（MEAN_POOLING 默认）→ crossattn_emb。DiT 内：patchify（patch_spatial×patch_temporal）成 token → 3D RoPE（H/W/T 独立频率）→ N 个 Block（AdaLN-LoRA + self-attn[可稀疏] + cross-attn + FFN）→ FinalLayer 出 velocity。`kv_cache_cfg` 贯穿 Attention.compute_attention（状态化返回 `(output, new_kv_state)`）——交互线靠它免重算历史帧。

## 设计决策

1. **算子五后端而非一后端**：训练用 TE/FlexAttention 拿编译优化，交互推理换 minimal_a2a/KV cache 路径——同一权重多执行形态。
2. **SAC 逐型号调档**：激活检查点粒度按 2B/14B×720p 四组合离线 profile 定 policy（计数器魔数 16 与 block 数强耦合，68 行注释警告"改网络结构 policy 会失配"）。
3. **RoPE 维度 2:1 切分**（H=W 权重两倍于 T）：视频 token 里空间维占大头，频率预算向空间倾斜。
4. **潜空间复用 Wan VAE 而非自训**：省一条 VAE 训练线，代价是 8× 空间压缩下 480×640 输入的 token 数与文本条件长度都受 Wan 先验约束。
5. **文本编码器可离线可在线**：`compute_online` 开关（`TextEncoderConfig:43`）决定 t5_text_embeddings 是数据集预存还是 forward 里现场算——大规模预存省算力，reason embeddings 阶段实验（`configs/video2world/experiment/reason_embeddings/`）则必须在线。

## 新人提示

- 看 2B/14B 差异最快入口：`configs/{2b,14b}_480_640_*.yaml` 的 `model.config.net` 覆盖（model_channels/num_blocks），骨干代码零分叉。
- `CheckpointMode` 改动是全仓雷区（四处定义），新档位先在 `selective_activation_checkpoint.py` 测试对拍显存/速度。
- RoPE 外推：输入超过 max_img_h/w 直接断言失败（778-780），长视频推理要么提 `rope_*_extrapolation_ratio` 要么滑窗。
- 勘误实证汇总：`tokenizers/cosmos.py` 名实不符（Wan 配置表）；`text_encoder.py:46` 默认 ckpt_path 是内网 s3 路径（`s3://bucket/cosmos_reasoning1/...`），开源环境必须显式覆盖。
