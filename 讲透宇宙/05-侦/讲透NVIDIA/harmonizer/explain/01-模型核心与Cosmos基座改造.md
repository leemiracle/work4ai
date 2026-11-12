# 01 · 模型核心与 Cosmos 基座改造

## 角色定位

`src/model/` 四件（`text2image_dit.py`/`pipeline.py`/`denoiser_scaling.py`/`__init__.py`）回答一个问题：如何把 Cosmos-Predict2 文生图基座（0.6B，`README.md:44`）改造成**单步、时序条件**的图像增强器。训练双变体、推理三态、ONNX 导出全建立在其 `MiniTrainDIT`+Fast 三组件之上。

## 内部结构

`text2image_dit.py`（1657 行）是 Cosmos DiT 的独立可训练移植：`MiniTrainDIT`（`:1198`）自带 Attention（`:285`，MinimalA2A/NattenA2A 两种 window attention 算子，`:371/375`，import 自 `cosmos_predict2.module.a2a_cp`，`:29`）与双位置编码：`build_pos_embed`（`:1411`）支持 Rope3D/Learnable 注册表（`LearnablePosEmbAxis`，`:635`）。选择性 activation checkpoint 有三套按层名分派的预设工厂：`predict2_2B_720_context_fn`（`:102`）、`predict2_14B_720_context_fn`（`:125`）、`linear_selfattn_context_fn`（`:148`），分派逻辑在 `:169-185`。单步低延迟路径用 `create_cuda_graph`（`:1559`）。

`pipeline.py`（311 行）三组件：`FastTokenizer`（`:70`）持 VAE 编解码状态（`encode/decode`，`:84/88`）；`FastDenoiser`（`:144`）的 `compute_caching`（`:150`）预计算并缓存条件与缩放张量（委托 `dit.compute_caching`，`:195`），`forward`（`:198`）/`denoise`（`:216`）执行单步去噪；`FastUnconditioner`（`:18`）造无条件嵌入（默认 544×960，`:28`）。`denoiser_scaling.py` 的 `RectifiedFlowScaling.__call__`（`:36`）给出 EDM 式四系数：`t=sigma/(sigma+1)`，`c_skip=1-t`、`c_out=-t`、`c_in=1-t`、`c_noise=t·t_scaling_factor`（`:38-41`）。

## 外部连接

上接被 patch 的基库：`Dockerfile.cosmos:70` 在镜像内 patch dist-packages 的 `text2image_dit.py`，使基库行为与本仓实现对齐；`tokenizer.patch` 删 VAE `encode/decode` 的 `@torch.no_grad()`（hunk `@@ -705,7`、`@@ -718,7`），配合 `src/model/__init__.py:55/71` 的 `my_vae_encoder_fwd/my_vae_decoder_fwd`（`(self, sample)` 签名的 monkey-patch 惯用法）双保险打通 VAE 梯度。下接双变体组装（`pix2pix_turbo_harmonizer.py:29`、`...faster_tokenizer.py:32`）与 ONNX 导出（`exportable_modules.py:109` 要求已 `compute_caching`）；`__init__.py` 的 `make_1step_sched_base/sprint`（`:27/36`）给单步调度器。

## 数据流

一次增强前向：输入渲染帧（+可选时序参考帧）→ `FastTokenizer.encode`（`pipeline.py:84`）得 latent → 按 `RectifiedFlowScaling`（`denoiser_scaling.py:36`）以最大噪声 σ 构造 `xt`（c_in 缩放）→ `FastDenoiser.forward` 单步网络前向（`pipeline.py:198`）→ 输出经 `c_skip·x + c_out·F(x)` 残差式合成干净预测 → `FastTokenizer.decode`（`:88`）回像素域。条件嵌入与空条件在 `compute_caching`（`:150`）一次算好缓存——"单步"能快的关键。

## 设计决策

① **独立移植而非 import 基库**：1657 行独立实现让训练侧改动不污染上游；② **Rectified Flow 时间重参数化**（`:36-42`）：t 压到 (0,1) 使单步端点的 c_skip/c_out 对齐恒等映射，蒸馏成单步时网络只需学残差修正；③ **缓存一切可缓存**：条件嵌入、缩放张量在 `compute_caching` 预计算（`pipeline.py:150-195`），推理热路径只剩一次 DiT 前向；④ **双注意力算子**（`text2image_dit.py:371/375`）：MinimalA2A 面向 TRT 部署，Natten 面向邻域注意力质量——同一模型两种后端取向。

## 新人提示

按 `:1198`（类）→`:1411`（位置编码）→`:1559`（cuda graph）→`pipeline.py:150`→`denoiser_scaling.py:36` 顺序读最省力。改前向先确认 `inference_only_mode` 语义（`exportable_modules.py:242` 会强校验）。`utils/profiling.py:53-58` 的 `NVTXRangeDecorator` 是模块级三态变量（nvtx/Compat/nullcontext），`text2image_dit.py:668` 等处直接当装饰器用——在静态分析里"找不到定义"属预期。
