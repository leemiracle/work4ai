# ④ 整流流世界模型：Text2World/Video2World RF 与 LAM 隐动作注入

## 角色定位

`models/text2world_model_rectified_flow.py`（1264 行）是 DreamDojo 预训练的**主模型**：文生视频为训练目标，同时是后续动作条件/交互/蒸馏一切变体的父类。`models/video2world_model_rectified_flow.py`（346 行）在其上加"首帧替换"式视频续生条件；camera 线三变体（`camera/models/multiview_camera_video2world_model.py:45` 等）又继承 video2world。命名勘误：真正叫 `Text2WorldModel` 的类在 `models/text2world_model.py:133`，名为 **`DiffusionModel`**——全仓十几处以 `import DiffusionModel as Text2WorldModel` 引用（如 `configs/text2world/defaults/model.py:19`、`action/models/action_conditioned_video2world_model.py:33`），读代码时"Text2WorldModel"可能指 RF 版、基类版或别名，须看 import 行。

## 内部结构

**配置与装配**：`Text2WorldModelRectifiedFlowConfig`（76 行 attrs dataclass）持有 tokenizer/text_encoder/net/conditioner 的 LazyDict。`__init__`（127）里五步：precision 三档映射 tensor_kwargs → `FlowUniPCMultistepScheduler` 采样器（56 import 自 `models/fm_solvers_unipc.py`）→ HSDP device mesh → `set_up_model`（266：build_net lazy 实例化 + FSDP `fully_shard`）→ `RectifiedFlow`（121，`schedulers/rectified_flow.py:76`，velocity_field 直接传 self.net）。**LAM 装配**（104-111）：`self.lam = LAM(lam_model_dim=1024, lam_latent_dim=32, lam_patch_size=16, lam_enc_blocks=24, lam_dec_blocks=24, lam_num_heads=16)`——70 行 `from external.lam.model import LAM`。

**RF 训练前向**（`forward`，856-937）：①在线 reason embeddings（858-861）；②**LAM 隐动作注入**（863-869）：`data_batch["lam_video"]` 重排成 `(b p) t h w c` 的帧对 → `torch.no_grad` 下 `self.lam.lam({"videos":...})` → 取 `outputs["z_rep"]` → `data_batch["action"][:,:,-32:] *= latent_action`——动作向量末 32 维被 LAM 隐动作逐元素缩放（与 proprioceptive 动作拼接语义）；③VAE encode x0 → `sample_train_time` 采 t（877，全帧共享 sigma）→ CP 切分（880）→ `get_interpolation(eps,x0,sigmas)` 得 (xt,vt)（909）→ DiT 预测 velocity（911-916）→ **损失 = MSE + 0.1×运动一致性**（919-925：相邻帧 velocity 差的对齐项，DreamDojo 特有）。高 sigma 策略（885-900）按 `high_sigma_ratio` 概率把 timestep 重采样到指定区间——加强低噪区训练。

**推理闭包**：`get_velocity_fn_from_batch`（463）返回 `velocity_fn(noise,noise_x,timestep)`，内部 cond/uncond 两次 denoise + CFG：`uncond_v + guidance*(cond_v-uncond_v)`（508）。`generate_samples_from_batch`（514）串 scheduler 多步积分；`generate_samples_from_batch_lora`（618）与 `_dmd2`（750）服务后训练两分支。

**Video2World 层**（`video2world_model_rectified_flow.py`）：`ConditioningStrategy.FRAME_REPLACE`（37-38）唯一策略；`denoise`（77）把条件帧用 mask 混回 xt（105-107），`denoise_replace_gt_frames`（52）再把 GT 帧 velocity 直写回输出（131-136，训练时保证条件帧零损失）；`conditional_frame_timestep`（48，默认 -1 不生效）可为条件帧单独设噪声级（109-122）。`get_velocity_fn_from_batch`（140）多一步 `set_video_condition` + `edit_for_inference`。

**camera RF 基类**：`CameraConditionedVideo2WorldModelRectifiedFlow`（`multiview_camera_video2world_model.py:45`）覆写 `get_data_and_condition`：把多相机视频沿 batch 维拆块逐段 encode（`_cond` 后缀输入），`IS_PREPROCESSED_KEY`（37）短路重复编码（124/138）；AR 变体（`multiview_camera_ar_video2world_model.py`）与 FrameInit 变体再各加滚动条件。

**LAM 双副本**（`external/`）：研究版 `external/lam`（DreamDojo 消费）——`modules/lam.py:57` `assert T == 2` 只吃帧对，`z_rep = z_mu.reshape(...)`（72）**确定性取后验均值**，无重建头 forward；生产副本 `external/lam_project`（独立包前缀 `lam.*`，含 `main.py`/`dataset.py`/`train.sh`/osmo·ray 双分布式启动器）——`lam/modules/lam.py:74-76` 推理取均值、训练从后验采样 `z_mu+randn*exp(0.5*z_var)`，`mu_record` 缓存跨步拼接（53-54），且 forward 里做 video_patches+action_patches 相加再解码重建（96-109，`F.sigmoid` 输出）。两者差异本质：研究版是"取隐动作的编码器"，生产版是完整自监督训练工程。

## 外部连接

父类链：`DiffusionModel`（`text2world_model.py:133`）→ `Text2WorldModelRectifiedFlow` → `Video2WorldModelRectifiedFlow` → camera/action 变体 → `Video2WorldModelDistillDMD2TrigFlow`（蒸馏）→ `ActionVideo2WorldModelTrigflowSelfForcingDMD2`（自强迫，⑤篇）。LAM 上游：训练入口 `external/lam_project/main.py`（`docs/LAM.md` 工作流）；权重消费即本篇 forward 863-869。conditioner 侧 `TextAttr`（`conditioner.py:240`）默认从内网 s3 拉 reason1 空串嵌入（246 行路径）做 CFG 空条件。

## 数据流

预训练一步：dataloader 出 `{video, t5_text_embeddings, lam_video, action, ...}` → forward ①②③ → loss 反传只进 DiT（LAM 冻结在 no_grad）。推理一段视频：`Inference.generate`（`cosmos_predict2/inference.py`）→ `get_velocity_fn_from_batch(guidance=1.5)` → scheduler 从纯噪声积分到 x0 → VAE decode。视频续生：首 1-2 潜在帧作 gt_frames，mask 混入每步去噪起点，剩余帧自由生成。

## 设计决策

1. **整流流而非 DDPM/EDM 作预训练目标**：velocity 参数化 + 直线路径让少步蒸馏（后接 DMD2/sCM）天然友好——`scaling_from_time` 同时备好 `RectifiedFlow_sCMWrapper`（`modules/denoiser_scaling.py:46`）给 sCM 线复用。
2. **LAM 输出乘法注入而非拼接**：动作通道末 32 维乘 z_rep（869），保持 GR00T proprioceptive 维度语义不破坏，隐动作只调制。
3. **条件帧 velocity 直写**（video2world 131-136）：条件帧不需要模型预测，训练时以真值 velocity 替换省算力且稳条件。
4. **运动一致性 0.1 权重**（925）：对相邻帧 velocity 差施加一致性，抑制帧间抖动——世界模型滚动稳定性的直接正则。
5. **camera 线 IS_PREPROCESSED 短路**：多相机逐段 encode 昂贵，一次预处理标记后复用。

## 新人提示

- **勘误（源码实证）**：①两处 CFG 公式不一致——`text2world_model_rectified_flow.py:508` 是标准 `uncond+g*(cond-uncond)`，`video2world_model_rectified_flow.py:209` 却写 `cond+g*(cond-uncond)`（引导强度语义不同，引用/改动前先确认用的是哪份）；②`Text2WorldModel` 与 `DiffusionModel` 是同物异名（import 别名），文档口述时要落到 import 行；③LAM 双副本别混用——研究版 `external.lam.*` 断言 T==2 且只出均值，若你想对 T>2 视频段直接提隐动作会 AssertionError，应改用生产副本逻辑。
- 调 guidance 看 `generate_samples_from_batch` 的 `guidance` 形参（默认 1.5）；负提示路径走 `is_negative_prompt=True` 分支（167-170）。
- 高 sigma 策略只在 `use_high_sigma_strategy=True` 时生效，区间由 `high_sigma_timesteps_min/max` 控制（885-900），后训练域适配常用。
