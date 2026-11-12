# NVIDIA Harmonizer 深度导览（ONBOARDING）

> 仓库：github.com/NVIDIA/harmonizer @ 32f3eca · CVPR 2026（arXiv 2602.24096，`README.md:6,180`）· 图谱 192 节点 / 417 边 / 9 层 / 13 步 tour · fingerprints 基线 58 文件
> 本文所有行号锚均从源码逐一核实（2026-11-08），口径为 `文件:行`。

## 1. 项目定位：单步扩散增强器，不是球谐工具

Harmonizer 是**在线生成式增强框架**（online generative enhancement framework）：把预训练多步扩散模型蒸馏成**单步、时序条件的增强器**，在单 GPU 上跑在仿真器在线回路里（`README.md:19`）。它解决的是 NeRF / 3D Gaussian Splatting 类神经重建（Omniverse NuRec）在新视角渲染中的伪影、光照与阴影错误，并把插入的外部资产重新调和进重建场景（`README.md:9,17`）——服务自动驾驶与机器人仿真。名字里的 harmonization 指**外观调和**（appearance harmonization），与球谐函数（spherical harmonics）无关；同 org 的球谐库是 torch-harmonics。

三大事实钉死认知：基座是 **Cosmos-Predict2-0.6B-Text2Image**（`README.md:44`）；训练数据用专门策展管线造"合成-真实"配对，瞄准三种失败模式——appearance harmonization、artifact correction、lighting realism（`README.md:19`）；伪影修正的退化帧策略沿自 Difix3D+（稀疏重建/循环重建/交叉引用/故意欠拟合四程序，`README.md:112`）。权重在 HF `nvidia/Harmonizer`（`download_checkpoints.sh:25`）。

## 2. 分层架构总览（图谱 9 层）

| 层 | 主题 | 代表文件 |
|---|---|---|
| L01 | 训练工具与损失底座 | `utils/training_utils.py`（758 行）、`opticalflow_loss.py`、`style_loss.py`、`dino_struct.py` |
| L02 | Cosmos 基座改造：模型核心 | `model/text2image_dit.py`（1657 行）、`pipeline.py`、`denoiser_scaling.py` |
| L03 | 双变体模型组装 | `pix2pix_turbo_harmonizer.py`（378 行）、`...nocond...faster_tokenizer.py`（472 行） |
| L04 | 训练入口 | `train_pix2pix_turbo_harmonizer.py`（537 行）、`train_..._nocond_...py`（437 行） |
| L05 | 推理与评测入口 | `inference_pix2pix_turbo_harmonizer.py`、`inference_pretrained_model.py`（649 行）、`evaluate_test_dataset.py` |
| L06 | ONNX/TensorRT 部署线 | `onnx_export/` 八件套 |
| L07 | 容器环境与基库补丁 | `Dockerfile.cosmos`、`tokenizer.patch`、`text2image_dit.patch` |
| L08 | Agent Skill 知识包 | `skills/harmonizer/`（SKILL.md 401 行 + 六分册） |
| L09 | 仓库治理与社区文档 | `README.md`、`doc/` 两教程、issue 模板、`request-nvskills-ci.yml` |

结构上是一个"研究仓 + 部署仓 + skill 仓"三合一：L01-L05 是研究主线，L06/L07 是工程落地，L08 是把整个使用流程封装给 Claude agent 的知识包装层——最后一层是同类研究仓里罕见的配置。

## 3. 环境落地：patch-in-image 容器

`Dockerfile.cosmos` 采用罕见的 **patch-in-image** 模式：不 fork 上游，而是在镜像构建期直接修改 dist-packages 里的 cosmos_predict2 源文件——`RUN patch .../cosmos_predict2/tokenizers/tokenizer.py tokenizer.patch`（`Dockerfile.cosmos:69`）与 `RUN patch .../cosmos_predict2/models/text2image_dit.py text2image_dit.patch`（`Dockerfile.cosmos:70`）。基础镜像 `nvcr.io/nvidia/pytorch:25.10-py3`（`Dockerfile.cosmos:19`）。

两个 patch 的语义要分开记：**tokenizer.patch 删的是装饰器而非改函数体**——在 `encode`/`decode` 两个方法头上各删一行 `@torch.no_grad()`（patch hunk `@@ -705,7` 与 `@@ -718,7`），让 VAE 编解码可回传梯度；text2image_dit.patch（25 行）让被 patch 的基库行为与仓内 `src/model/text2image_dit.py` 的本地实现对齐。这与 `src/model/__init__.py:55/71` 的 `my_vae_encoder_fwd/my_vae_decoder_fwd` 手写 forward（`(self, sample)` 签名、供外部直接赋给 VAE 模块实例的 monkey-patch 惯用法）构成**双保险**。

checkpoint 布局由 `download_checkpoints.sh` 钉死：Harmonizer 权重 → `models/`（`diffusion_harmonizer.pkl` + `harmonizer_nontemporal.pt`），基座模型 → `src/checkpoints/nvidia/Cosmos-Predict2-0.6B-Text2Image/`（`download_checkpoints.sh:7-8,25-29`）——记住这两个路径，评测链断点（§8）正是路径错位。

## 4. 模型核心：MiniTrainDIT 与 Fast 三组件

`src/model/text2image_dit.py`（1657 行，全仓最大）是 Cosmos DiT 的**独立可训练移植**：`class MiniTrainDIT`（`text2image_dit.py:1198`，继承 WeightTrainingStat）完整实现 Attention（`text2image_dit.py:285`，支持 MinimalA2A/NattenA2A 两类 window attention 算子，`text2image_dit.py:371/375`）、RoPE3D/Learnable 两类位置编码（`build_pos_embed`，`text2image_dit.py:1411`；`LearnablePosEmbAxis`，`:635`）。选择性 activation checkpoint 的上下文工厂有三套预设：`predict2_2B_720_context_fn`（`:102`）、`predict2_14B_720_context_fn`（`:125`）、`linear_selfattn_context_fn`（`:148`），按层名策略分派（`:169-185`）。`create_cuda_graph`（`:1559`，import 自 `imaginaire.utils.graph`，`:38`）是单步推理低延迟路径。

把基座改造成单步增强器的是 `pipeline.py` 三组件：**FastTokenizer**（`pipeline.py:70`）封装 VAE 编解码状态（`encode/decode`，`:84/88`；`get_state_shape`，`:115`）；**FastDenoiser**（`:144`）的 `compute_caching`（`:150`，内部调 `dit.compute_caching`，`:195`）预计算条件并缓存 `c_skip/c_out` 张量，`forward`（`:198`）与 `denoise`（`:216`）执行单步去噪；**FastUnconditioner**（`:18`）提供无条件嵌入（`sample_batch_image` 默认 544×960，`:28`）。缩放函数在 `denoiser_scaling.py` 的 `RectifiedFlowScaling`：`t = sigma/(sigma+1)`，`c_skip = 1-t`、`c_out = -t`、`c_in = 1-t`、`c_noise = t·t_scaling_factor`（`denoiser_scaling.py:36-42`）——EDM 式参数化的 Rectified Flow 变体，训练损失权重用 `exp(-2(t-0.5)^2)` 重整化（`:30`）。

## 5. 双变体与训练链

两个 `Pix2Pix_Turbo` 定义**成对存在**：标准版 `pix2pix_turbo_harmonizer.py:177`（`get_cosmos_predict2_text2image_pipeline(model_size="0.6B", fast_tokenizer=False)`，`:29`）吃 `diffusion_harmonizer.pkl`；nocond faster_tokenizer 版 `...faster_tokenizer.py:217`（`fast_tokenizer=True`，`:32`）另带 **AOTModule**（`:186`）——经 `torch._inductor.aoti_load_package`（`:193`）加载 AOT inductor 编译产物，`ImageEncoder/ImageDecoder`（`:199/208`）用 lambda 把 4D 图像适配到 FastTokenizer 的 5D `(B,C,T,H,W)` 接口（`x[:, :, None, :, :]`）。注意 `:421` 的注释：AOTModule 不能用关键字参数调用。

训练入口对应双变体：`train_pix2pix_turbo_harmonizer.py` 复刻 legacy 多数据集形态（docstring `:5` 自述前身名 `..._cosmos_skip_tp_multidataset_optical.py`，RAFT 光流时序损失 `:8`），支持逗号分隔多源+加权采样；nocond 版走 `PairedDatasetV2` JSON 数据源（`train_..._nocond_...py:164/168`）。两者都经 `accelerate` 多卡启动（`train_..._nocond_...py:31`）。`--pretrained_path` 指向 `diffusion_harmonizer.pkl` 则从预训练 Harmonizer 续训，省略则直接从裸 Cosmos 0.6B 微调（`README.md:159`）。

损失面四件：`opticalflow_loss.py` 用 torchvision RAFT（small/large 双选，`:49-55`，冻结参数 `:70`）算后向光流，`warp_backward`（`:24`）把首帧预测 warp 到后续帧做 Charbonnier 惩罚，`get_temporal_loss`（`:78`）处理 5D 多视角张量——这是保时序一致性的关键损失；`style_loss.py` 是 Gatys 风格损失；`dino_struct.py` 的 `VitExtractor`（22 个方法+`BLOCK_KEY/KEY_MAPPING` 常量表）做白盒 DINO 特征抽取。配对策略矩阵直接编码在函数名里：`get_gt_multiview_randomNone_noteven2_kx_ispdata_gap1`（`training_utils.py:526`）与 ds/relight/randomwhite 变体（`:536/546/578`）——参考(随机无/白)+采样(非均匀)+数据源(kx/ds/relight)+间隔(gap1)四维组合；`PairedDataset`（`:596`）目录式与 `PairedDatasetV2`（`:660`）JSON 式两种数据源形态。

## 6. 推理三态与部署线

推理入口三态：① **时序推理** `inference_pix2pix_turbo_harmonizer.py`——README 官方演示命令载体，逐帧自回归：每帧与前序输出（`--history_idx` 负偏移，`:82`）一起喂入，首帧历史不足时回退非时序 V=1 前向（`:133`），`--nontemporal`（`:85`）整体关闭时序条件；`save_folder2video` 以 30fps 合成 mp4（`:41`）。② **部署工具箱** `inference_pretrained_model.py`（649 行）——JIT trace 导出（`export_encoder_with_jit:230`）、`torch_tensorrt.dynamo.compile`（`:314`）、VAE 走 `torch.compile(backend="torch_tensorrt", mode="max-autotune")`（`:318`），且按 `_TRT_VERSION`（`:26`，缺省 `(999,0)` 视为最新，`:28`）分支——`>=2.9` 才能用 `aot_inductor` 格式导出（`:328-330`）。③ **导出模型加载** `inference_exported_model.py`——`aoti_load_package`（`:24`）装 `.aoti` 包做加载推理。

ONNX/TensorRT 部署线是 `src/onnx_export/` 八件套三步管线：`exportable_modules.py` 定义四个固定 shape 导出包装（VAEEncoder `:21`/VAEDecoder `:49`/Denoiser `:86`/FullModel `:176`），**前置双条件**——模型须处 `inference_only_mode` 且 `compute_caching` 已执行，否则直接 raise（`:229-245`）；`export_onnx.py`（410 行）自插 `sys.path`（`_SRC_DIR`）支持任意 cwd 运行并做数值校验；`convert_trt.py` 走 trtexec（`:39-74`）或 Python API 双路径按精度（fp32/fp16/bf16/int8）生成引擎；`inference_trt.py`（575 行）是混合后端：只有 denoiser 走 TRT/ORT 引擎，VAE tokenizer 保留 PyTorch 的 TorchTokenizer 执行——规避动态 shape 与复杂数值算子的引擎兼容问题。

## 7. Agent Skill 知识包

`skills/harmonizer/` 是随仓发布的 **Claude agent skill**（v0.5.0）：`SKILL.md`（401 行）以 frontmatter 的 name/description 决定触发条件——description 自述"运行 NVIDIA DiffusionHarmonizer（老 Fixer recipes 的公开继任者）来增强/调和/评测/微调 NuRec/3DGS/NeRF 新视角帧"，并明确**不要**用于 3D 重建本体训练（用 nurec skills）或 sensor→NCore 转换（用 ncore）——SKILL.md:2-8。References 一节链接 `references/` 六篇分册：inference/training/evaluation/troubleshooting（症状-原因-修复三元组）/wrapper-image/teardown（完整流程可留 100GB+，逐项给删除命令）——按"何时需要才加载"组织的渐进披露结构。`scripts/validate_setup.py` 逐项检查前置：GPU 算力 ≥8.0 即 Ampere（`:9,130`）、Docker+nvidia runtime（`:62/66`）、hf CLI 与凭据（`:135`，`_hf_cached_token_path:163` 直接解析 `~/.cache/huggingface/token`）、NGC_API_KEY（`:13`）、120GB 磁盘（`:14`）。`evals/evals.json` 是 skill 的评测集。

出身：skill 前身是 NVIDIA/nurec-skills 仓的 `nurec-fixer`（`skills/harmonizer/NOTICE:10`），联系方式仍是 nurec-skills@nvidia.com（`SKILL.md:31`）。CI 走 reusable workflow 转发 NVIDIA/skills 仓（`.github/workflows/request-nvskills-ci.yml`）。

## 8. 评测链与上手路线

`evaluate_test_dataset.py` 复用推理基座算 PSNR/LPIPS/FID（torchmetrics，`:27-28`；指标初始化 `:121`，逐场景 FID `:146`，均值输出 `:325`）。**但注意文档自曝的两处 blocker**（`skills/harmonizer/references/evaluation.md:3-18`）：① `evaluate_test_dataset.py:109` 调 `load_and_compile_model` 时缺其签名要求的 `image_size` 参数，直接崩；② 评测加载 fast-tokenizer 管线，其 config 指向 `/work/models/base/model_fast_tokenizer.pt`——与 `download_checkpoints.sh` 落盘路径不匹配（`evaluation.md:51-54`）。skill 明确告诫 agent：**勿向用户承诺评测可完成，先上报两处 blocker**。上手路线按 13 步 tour 精简：README（step-1）→ Dockerfile+patch（step-2）→ MiniTrainDIT（step-3）→ Fast 三组件（step-4）→ 双变体（step-5）→ 损失库（step-6）→ 训练与数据策展（step-7）→ 推理三态（step-8）→ 评测断点（step-9）→ TRT 部署（step-10）→ skill（step-11/12）→ 双许可收尾（step-13）。常见坑：评测直接跑必撞断点；ONNX 导出前须先 `compute_caching`（`exportable_modules.py:229`）；AOTModule 不能关键字传参（`...faster_tokenizer.py:421`）；NVTX 装饰器是三态变量非函数定义（`utils/profiling.py:53-58`）。

> 勘误与甄别清单见 `../README.md`；三篇深讲见 `../explain/`。
