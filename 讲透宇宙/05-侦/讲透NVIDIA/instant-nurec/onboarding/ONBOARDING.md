# InstantNuRec 上手指南（ONBOARDING）

> 仓：github.com/NVIDIA/instant-nurec（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/instant-nurec`，HEAD `f2ecafcd`）
> 图谱：`.understand-anything/knowledge-graph.json`（587 节点 / 1328 边 / 12 层 / 14 步导览，fingerprints 140 文件基线）
> 论文：arXiv 2607.14203（README.md:498 bibtex、README.md:12 项目页 2026-07 上线）

## 1. 一句话定位：前馈 3DGS 自动驾驶场景重建

**InstantNuRec 不是语音工具（任务书原判断被源码推翻），而是 NVIDIA 的前馈神经重建模型**：把一段多相机驾驶日志（NCore V4 序列）在**单次前馈**中变成可仿真的 3D 高斯（3DGS）场景——每个上下文像素产出一个高斯图元，覆盖几何、外观与运动（README.md:4、README.md:8）。输出是分层结构：静态层 + 动态层 + 天空 cubemap + 逐相机 ISP 仿射修正，原生支持非 pinhole 相机模型（走 3DGUT 渲染）；10–20 秒多相机场景约 1.5 秒重建完成，Waymo Open Dataset 上 PSNR 比最强基线高 2.01 dB（README.md:16）。它的下游位：可直接作静态重建用，也可作为 NuRec（Docker 版、更高保真、逐场景优化）的初始化（README.md:32、README.md:35-38）——InstantNuRec 是"native-Python 前馈预览（秒级每片段），NuRec 是精修"。与 AlpaSim 闭环仿真兼容。

仓库三入口：`run_inference.py`（根目录薄包装，run_inference.py:17-27 给出完整调用样例）、`instant_nurec/cli.py`（全量旗标）、训练入口见 `docs/TRAINING.md`。运行要求 NVIDIA GPU 与驱动（README.md:85-86 链到 NuRec 硬件页）；安装走 `setup.sh`→`uv sync --frozen` 锁定依赖树（README.md:99-100）。

## 2. 技术栈与依赖策略（工程立场鲜明）

- **全 pin 策略**：pyproject.toml:9-11 注释钉版"所有依赖版本 pin 死，任何 parity/运行时漂移都应归因于刻意的依赖 bump 而非最新 wheel"。`torch==2.7.0+cu128`（pyproject.toml:24）、torch-scatter 2.1.2、zarr 2.18.2、pytorch-lightning 2.6.5；uv 双索引（PyTorch cu128 wheel + PyG flat 索引，pyproject.toml:68-77）。
- **lietorch 垫片**：本仓**不装 lietorch**。`instant_nurec/utils/se3.py:15-22` 头注释写明原因：PyPI `lietorch==0.8.2` 硬钉 `torch==2.6.*`/`torchvision==0.21.*`，与本仓 cu128/torch2.7 冲突，于是只把 predict 路径实际用到的 SE3/SO3 子集（构造/指数对数/求逆/xyzw 四元数 slerp）用纯 torch 重实现（详见 explain 03）。
- **训练/渲染可选 extras**：`uv sync --extra render` 装 nvdiffrast 与 gsplat（README.md:114）；渲染侧构建开关用 `os.environ.setdefault` 保持部署侧权威（render_preview.py:43-44）。
- Python 3.10+ 风格：`@dataclass(kw_only=True, slots=True)` + ABC 抽象属性的惰性接口组合（backbone/base.py）。

## 3. 仓库地图（图谱 12 层导览）

图谱 12 层自下而上就是阅读顺序：

| 层 | 内容 | 代表文件 |
|---|---|---|
| L01 | 门户与工程文档 | README.md（512 行）、docs/TRAINING.md（709 行）、docs/camera_rectification.md |
| L02 | 配置 schema | `config_schema/` 五域：dataset/models/predict/train/instantnurec |
| L03 | NCore 数据集 | datasets/instantnurec_ncore.py（1142 行）、tracks.py、samplers.py、mixture.py |
| L04 | 相机与 SE3 | utils/sensors/ray_gen.py（660 行）、kernel_types.py、utils/se3.py（271 行） |
| L05 | 批契约中枢 | utils/batch.py（839 行）、cubemap.py、merge_covariances.py |
| L06 | 神经算子 blocks | model/blocks/：aa_vit、dpt、attention、embeds、dav3、layers |
| L07 | backbone | encoders.py、decoders.py（编码器/解码器） |
| L08 | 模型组装与图元 | model/kelvin.py、static_core.py、inference.py、primitives/kelvin_primitive.py |
| L09 | 推理入口 | cli.py（318 行）、ncore_input.py、pretrained.py |
| L10 | 预测导出 | predict/：export_ply、export_sky、export_dynamic、primitive_merge、render_preview、render_video |
| L11 | 训练主线 | training/：system.py、losses.py、renderer.py、data.py |
| L12 | 测试 | tests/ 39 个测试文件 |

## 4. 数据面：NCore 日志 → 批契约

`NCoreInstantNuRecDataset`（instantnurec_ncore.py:80，全仓最大文件 1142 行）解析序列 JSON、时间区间与相机集合（内部类型 `UniqueFrameId`:106、`ExtendedCameraId`:111、`LoadersAndSensorsResult`:158），构建帧批采样与相机子采样，输出 `InstantNuRecDataBatch`。采样器两件：`AdaptiveSequentialFrameBatchSampler`（samplers.py:48）与 `UniformFrameBatchSampler`（samplers.py:129）；多数据混合走 `NCoreMixtureDataset`（mixture.py:23）。

动态目标侧，`Tracks`/`CuboidTracks`（datasets/tracks.py）是 packed 轨迹容器，叠加射线-AABB 求交（datasets/ray_intersections.py）与位姿插值，供动态层运动建模；`utils/motion.py` 对 `CuboidTracks` 用 TYPE_CHECKING-only 导入避免循环依赖。

**批契约中枢 batch.py（839 行）是全仓接缝文件**：RenderingData:77 / FrameMeta:205 / CameraFrameLabels:250 / DataBatch:344 / RenderingBatch:404 / DataAndRenderingBatch:431 六个渲染侧数据类；`CameraFreePoseViewGeometry`:504 做相机几何换算；顶层 `InstantNuRecDataBatch`:713 含 `maybe_compute_rendering_data` 惰性渲染数据推导。读懂任何消费方的输入，先读它（tests/test_batch.py 655 行锁死这份契约）。

## 5. 模型面：blocks → backbone → Kelvin 组装

- **感知底座**：`AlternateAttentionVisionTransformer`（blocks/aa_vit.py:30）基于 ByteDance Depth-Anything-3 的多图 DINOv2 ViT，局部（带 RoPE，仅局部层加）/全局注意力交替（aa_vit.py:33）；激活检查点三档 `all/local/none`（aa_vit.py:52，全局块重算贵故可只 checkpoint 局部）。预训练权重经 `blocks/dav3.py` 键名桥——(regex, replacement) 元组表驱动迁移，未匹配键显式报告（dav3.py:140-144）。
- **密集头**：DPT 家族（blocks/dpt.py：DPTReassembleBlock:31、DPTFullHead:278）把 ViT 中间特征重排融合为逐像素预测；嵌入件在 blocks/embeds.py（PatchEmbed:25、ContinuousTimeEmbed:186、RotaryPositionEmbed2D:254）；注意力家族六件在 blocks/attention.py:36-402（SelfAttention/KVProjector/CrossAttention/AttentionBlock/ModulatedAttentionBlock/CrossAttentionBlock）。
- **backbone**：`KelvinDAv3Encoder`（encoders.py:69）把多相机图像+相机参数编码为多尺度 latent，FOV 用 pinhole 近似（encoders.py:100-106 `_fov_wh_from_pinhole`，:131 有 TODO 标记 F-Theta 也先用 pinhole 近似）；`KelvinDPTDecoder`（decoders.py:89）解码逐像素高斯参数（深度/法线/语义/scale/rotation），激活参数化 `GaussianActivations`/`GaussianParams` 在 model/activations.py:87/132，`TimeModulatedMotionHead`（decoders.py:94）管动态头；`KelvinPointQueryCADecoder`（decoders.py:530）是 point-query 变体。
- **总装三视图**：`KelvinInstantNuRec`（model/kelvin.py:44）串联编码器→DPT 解码器→天空头→`PerCameraAffinePostProcessing`（kelvin.py:133 `_compute_affine_matrix`），输出 KelvinInstantNuRecPrimitive；`KelvinStaticCore`（static_core.py:65）是发布权重的 eager 静态核心——**公开检查点刻意省略学习式 `sky.*` 头，天空 cubemap 由观测 RGB 推导**（static_core.py:167-171 调 utils/cubemap.py:206 `build_observed_sky_cubemap_with_mask`）；`KelvinInferenceModel`（inference.py:58）施加语义 + 可选 cuboid-track 动态掩码精化（inference.py:150-193，`TrackFlags.DYNAMIC` 判定在 :192），动态推理是 opt-in（`include_dynamic`:79）。

图元体系 `primitives/kelvin_primitive.py`：`KelvinSemanticClass`:42（OTHERS/EGO/SKY/ROAD/MOVABLE，枚举值=通道索引）、`KelvinLayer`:64 基类、`KelvinStaticLayer`:116（voxelize:197 体素化降数）、`KelvinDynamicLayer`:260（`_interpolation_segment`:354 分段线性插值）、顶层容器 `KelvinInstantNuRecPrimitive`:415。协方差 KL 最优合并在 utils/merge_covariances.py，注释钉版 cusolver batched eigh 在 ~18M 个 3x3 矩阵时报 `CUSOLVER_STATUS_INVALID_VALUE`，分块规避（merge_covariances.py:28-29）。

## 6. 预测面：入口 → 合并 → 五形态导出

一次 `python run_inference.py --model pa-front --ncore-path X --output-dir Y [--merge] [--render-preview] [--render-video]`（run_inference.py:17-27）背后：`cli.py` 定义全量旗标，8 处函数体内延迟 import 让 `--help` 保持廉价（cli.py:216 注释、:201/:209/:217-234）；`resolve_ncore_paths`（ncore_input.py:31）把单 JSON 或 `.lst` 清单展开为校验路径；`run_predict`（predict/run.py）种子固定后构造 `GaussiansInstantNuRecSystem`（model/system.py:48，Lightning 风格总装）触发 predict。

权重侧：三个发布 profile `pa-front`（默认，pretrained.py:42）/`pa-multiview`/`pq-front`（pretrained.py:60-84），HF 下载到 hub 缓存，环境变量 `INSTANT_NUREC_FULL_PT` 可离线短路（pretrained.py:132）；模型工厂 `model/__init__.py` 的 `make` 预检相机 ID（:55-78 `_validate_camera_ids`，配错相机名直接报可用列表）并**拒载旧 traced archive**（:125-130）。

分块长序列用 `primitive_merge`（predict/primitive_merge.py：CameraFrustum:41 视锥、`compute_frustum_ownership_mask`:130 归属去重、`merge_primitives_and_batch`:284 合并+KL 体素化迭代至目标高斯数区间）。导出**五形态**：① 3DGS PLY（export_ply.py，颜色 SH、scale/density 为预激活值，逆激活 scale=log、density=logit 硬编码在 :47-52，用途是 NuRec SO 的初始化，:105）；② 天空侧车 `.sky.npz` + `.sky.png`（export_sky.py:25-33）；③ 动态层 `.dynamic.npz` 世界系刚体变换（export_dynamic.py:15）；④ `--render-preview` 出 `.render.png`（render_preview.py，`_looks_like_ftheta`:102 分流相机模型、BUILD_3DGUT setdefault:43-44）；⑤ `--render-video` 出 `.render.mp4`（需 `--merge`+render extra+ffmpeg/libx264，render_video.py require_ffmpeg 于 cli.py:209 引入）。run.sh 对非法 `.ncore-path` 后缀 exit 65、不可写输出目录 exit 73。

## 7. 训练面：context→render 两阶段契约

`docs/TRAINING.md` 钉版可训矩阵（TRAINING.md:11-16）：**dense 前相机两阶段可训**（主支持路径）；multiview 固定相机/帧集（随机 1/3/5 相机与 12/16/18 帧课程未发布）；point-query 变体 standalone 训练"no"（全模型组合刻意拒绝 point-query decoder）；TokenGS 不在公开训练路径。参考配方对 = `configs/training/full_model_front_context.yaml`（phase 1）与 `full_model_front_render.yaml`（phase 2），同数据/日志结构。关键超参：每 phase 40 epochs（TRAINING.md:47）；phase 2 从 phase-1 检查点出发，**编码器冻结、Gaussian 头重初始化**（TRAINING.md:57、:442 `model.init_weights_paths.full`）；context 期损失含深度/RGB/法线余弦 0.2/速度 L1 1.0，render 期换天空等权重（TRAINING.md:63）；phase-2 首次渲染会 JIT 编译 pinned CUDA kernel 需数分钟（TRAINING.md:133）。

代码侧：`TrainingSystem`（training/system.py，LightningModule）组装模型+损失+DAv3 预训练初始化+PSNR；`TrainingLosses`（training/losses.py:78）统一入口，`_context_losses`:95 覆盖上下文深度/置信度/RGB/法线（:162-170 cosine）/语义（:153-158 cross-entropy），`_render_losses` 管可微渲染监督，聚合工具 `_masked_mean`:28/`_quantile_mean`:53；渲染器 training/renderer.py 用 gsplat 3DGUT 对参考帧渲染（`RenderOutput`:29、rolling shutter 支持 :59-76、"RGB-d" 契约 :135 opacity 加权距离）；断点续训由 SkipBatchSampler（training/data.py:24）+ TrainingDataModule:55 + ResumableDataModuleCallback:147（跳批采样器状态存取 + Slurm 重排队）支撑。

## 8. 质量防线与上手路线

**测试即反向教材**：tests/ 39 个文件覆盖数据契约（test_batch.py 655 行）、训练语义（test_training.py 833 行：损失分支/渲染监督/优化器/前向）、传感器几何（ray_gen 分支与挡风玻璃畸变 551 行、SE3 往返）、导出三件与合并、CLI 48 用例——GPU 端到端之外的全量隔离验证。

**推荐路线**（图谱 14 步导览的压缩版）：
1. README.md 全读（512 行，含 FAQ 与 TROUBLESHOOTING.md 指引）→ 跑通一次 `run.sh`；
2. 读 batch.py:76-743 六个数据类，配 test_batch.py 对应用例；
3. 读 kelvin.py:44-177 的组装流（prepare_context→_build_primitives→reconstruct）；
4. 读 kelvin_primitive.py:42-415 图元体系 + export_ply.py 导出约定；
5. 要训练再进 TRAINING.md + training/ 四件（system/losses/renderer/data）；
6. 相机/几何深水区读 explain 03（ray_gen/se3 垫片）。

新人三坑：a) 别按直觉给 PLY 消费方直接用激活后 scale——导出的是**预激活值**（export_ply.py:51-52）；b) 别以为天空头是网络输出——公开权重走观测推导（static_core.py:167）；c) torch 版本别升——全 pin 策略 + lietorch 垫片的存在就是版本漂移的血泪史（pyproject.toml:9、se3.py:15）。
