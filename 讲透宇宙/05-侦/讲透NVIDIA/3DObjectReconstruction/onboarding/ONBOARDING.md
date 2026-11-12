# 3DObjectReconstruction 新人上手文档（ONBOARDING）

> 事实源：仓库 git `e7aa98dc` 的 understand 图谱精简视图（13 层 / 14 步导览 / 187 节点 351 边）+ 源码逐处核实。所有 `文件:行号` 锚均已在源码验证。写作日期 2026-11-06。

## 1. 一句话定位

NVIDIA 官方开源的**立体视频 → 3D 资产**端到端重建框架（PyPI 包名 `nvidia-3d-object-reconstruction`，CLI 命令 `nvidia-3d-reconstruct`）：输入一段绕物体拍摄的左右目立体视频，经 SAM2 目标分割、FoundationStereo 深度估计、BundleTrack/Theseus 位姿优化、NeRF SDF 重建与纹理烘焙，输出可直接进 Omniverse/AR 生态的 OBJ / USD / USDZ 网格资产，官方口径 RTX A6000 上 30 分钟内完成。给谁用：机器人 sim2real 数据生成（real2sim）、零售物品数字化、3D 内容创作的研究者与工程师——前提是有一块 NVIDIA GPU 和能跑 Docker 的 Linux 环境。

## 2. 仓库全景（13 层结构）

图谱把仓库切成 13 层，从外到内大致呈"文档 → 环境 → 入口 → 配置/数据 → 感知 → 重建 → 出口 → 交互/测试"的依赖走向（上层依赖下层，L09 重建核心是全仓收敛点）：

| 层 | 名称 | 一句话 |
|---|---|---|
| L01 | 仓库治理与项目文档 | README（733 行四阶段管线总览）、CHANGELOG（0.1.0→0.2.0）、CITATION（FoundationStereo/BundleSDF 两篇论文）等 6 件门面文档 |
| L02 | GitHub 协作与仓库杂项 | Issue Forms 四模板、CODEOWNERS、print_env.sh 环境诊断脚本等 10 件 |
| L03 | Python 包构建与依赖 | `src/pyproject.toml`（入口+可选依赖组）、`src/requirements.txt`（18 项锁版本）、MANIFEST.in 共 4 件 |
| L04 | 容器镜像与一键部署 | 三份 Dockerfile + docker-compose + deploy.sh（592 行总控：架构探测、五组权重 MD5 校验下载）共 5 件 |
| L05 | 包骨架与 CLI 入口 | `src/nvidia/__init__.py` 命名空间声明、主包 barrel、`cli/main.py` 四步流水线编排 |
| L06 | 配置系统 | `configs/schema.py`（329 行 19 个 dataclass 配置树）+ `data/configs/base.yaml`（333 行 YAML 镜像） |
| L07 | 数据加载与前处理 | `preprocessing.py`（read_video 立体抽帧）+ `dataloader/reconstruction_dataloader.py`（多视角序列读取） |
| L08 | 感知推理组件 | sam2infer.py / foundationstereo_onnx.py / roma.py 三个预训练模型推理封装 + networks barrel |
| L09 | 重建核心引擎 | nvbundlesdf.py（1372 行总编排）+ nerf_runner.py（2492 行全仓最大）+ tool.py 几何工具箱 |
| L10 | 位姿优化器 | theseus_optimizer.py（389 行，纯 Python GPU 替代原 C++ OptimizerGPU） |
| L11 | 资产后处理出口 | postprocessing.py（OBJ/MTL 解析 → USD/USDZ）+ structures.py（dataclass 递归转 dict） |
| L12 | 交互可视化与演示 | visualization.py（996 行 ipywidgets 三件套）+ 42-cell 官方 demo notebook |
| L13 | 测试与冒烟验证 | E2E 7 用例 + conftest GPU 探测 + pytest.ini 四 marker + test_reconstruction.sh Docker 冒烟 |

层间依赖走向：CLI（L05）读配置（L06）→ 前两步调感知组件（L08）→ 第三步进 NVBundleSDF（L09），其内部再调 L07 数据加载、L10 位姿优化、kaolin 生态 → 结果经 L11 转 USD 出口；L04 容器层与 L12/L13 分别从环境与验证两端夹住整条链。核心 Python 代码只有 `src/nvidia/objectreconstruction` 下 23 个 .py、约 8900 行——这是个"薄 Python 编排 + 重外部依赖"的仓，理解它的关键一半在源码、一半在 §8 的生态版图。

## 3. 核心数据流

完整链路（`cli/main.py:290-401` 按固定顺序编排，每步幂等可跳过）：

```
立体视频(read_video 抽帧 left/right)
  → Step1 SAM2 分割: run_mask_extraction (main.py:322)
  → Step2 FoundationStereo 深度: run_depth_estimation_onnx (main.py:334)
  → Step3 组装: NVBundleSDF + 三个不同 downscale 的 DataLoader (main.py:347-362)
  → Step4a 位姿跟踪: tracker.run_track (main.py:379)
  → Step4b SDF 训练: tracker.run_global_sdf (main.py:390)
  → Step4c 纹理烘焙: tracker.run_texture_bake (main.py:401)
  → OBJ → USD → USDZ (nvbundlesdf.py:1190/1196)
```

各环节做什么：

1. **入口整理**：CLI 先把输入目录整树拷进输出目录，再把 left/right 帧名规范成 `left000000.png` 连续序号（`main.py:89-105` 的 `_normalize_image_sequence`，非 PNG 顺带转码），左右目数量必须相等且 ≥5 对（`main.py:49`）。
2. **SAM2 分割**（`sam2infer.py:501`）：按配置里首帧 bbox 提示（默认 `[1144, 627, 2227, 2232]`，零售样本标定值）构建视频预测器逐帧传播目标掩码到 `masks/`；已有掩码数与 RGB 帧数一致则直接跳过（幂等）。
3. **FoundationStereo 深度**（`foundationstereo_onnx.py:384`）：ONNX Runtime 加载 NGC 发布的 `deployable_foundationstereo_small.onnx`，`InputPadder`（:40）把左右目 pad 到 8 的倍数，推理输出视差后按 `深度 = fx × baseline / 视差` 换算成米制深度图（:318）落 `depth/`。
4. **位姿跟踪**（`nvbundlesdf.py:211` run_track）：把 bundletrack 配置序列化成临时 YAML 喂给 `my_cpp.YamlLoadFile`/`my_cpp.Bundler`（:227/:233，即 Docker 里源码编译的 BundleTrack C++ 扩展），逐帧送 color/depth/mask（掩码先按 `erode_mask` 腐蚀），跟踪期间全程钉 float32（:78 `set_nvbundlesdf_precision`）。
5. **全局优化**：跟踪中对关键帧对调 RoMa 稠密匹配（`nvbundlesdf.py:868` 调 `roma._process_batch`），把 2D 匹配反投影成 3D-3D 对应点交给 `TheseusOptimizer.optimize_frames`（`nvbundlesdf.py:689` → `theseus_optimizer.py:72`）：外层采样对应点、内层 Levenberg-Marquardt 逐步长优化位姿（:344），Huber 鲁棒核压离群。
6. **SDF 重建**（`nvbundlesdf.py:916` → `nerf_runner.py:1253` NerfRunner）：先用关键帧点云建 kaolin SPC 八叉树（`nerf_runner.py:1040-1049` quantize/unbatched_points_to_octree/scan_octrees 全套），再迭代"光线采样 → SDF 损失（:643 get_sdf_loss，trunc 带宽监督）→ 位姿联合优化"，收敛后提取网格。
7. **纹理烘焙 + 出口**（`nvbundlesdf.py:1037`）：离屏渲染各视角贴到 2048 纹理（`nerf_runner.py:244 build_texture_from_images`），产出 OBJ+MTL 后经 `postprocessing.py:296 convert_obj_to_usd` 挂 UsdPreviewSurface 材质网络，`postprocessing.py:376 export_usd_to_usdz` 打包 USDZ。耗时汇总写 `run_time.yaml`（`main.py:420`）。

失败语义：CLI 按错误类别返回退出码——文件/目录 2、配置 3、运行时 4、OOM 5、Ctrl+C 130（`main.py:418-446`）。

## 4. 关键模块深潜

**nerf_runner.py（2492 行，全仓心脏）**。不必逐行读，抓四个支柱：① `OctreeManager`（:1037）——kaolin SPC 八叉树加速，含点量化、层级生成、trinkets 构建（:1040-1049）与 `unbatched_raytrace` 光线求交（:1151），这是它比朴素 NeRF 快的关键；② 位姿参数化 `PoseArray`（:790）/`GlobalPoseArray`（:819）——把待优化位姿注册成可反传张量，支撑 SDF 训练与位姿联合优化；③ `get_sdf_loss`（:643）——截断带 SDF 监督的核心损失；④ 烘焙与渲染——`build_texture_from_images`（:244）、`ModelRendererOffscreen`（:118）离屏渲染、`trimesh_split`（:497，自实现大网格拆分，注释明说 trimesh 自带 split 内存开销过高）。入口类 `NerfRunner`（:1253）23 个方法串起"建八叉树→建网络→优化器→迭代训练→提网格→渲染"全流程。

**networks 感知组件**（三个模型封装共同模式：config dict 进、幂等 run 出）：
- `sam2infer.py`：模块导入期就做两件全局事——monkey-patch `torch.load` 兼容旧 checkpoint（:34-53，把 `weights_only=True` 强改 False）和**开 TF32**（:73-74，Ampere+ 全局 `allow_tf32=True`，SAM2 上游代码原样带入）；核心推理 `segment_image_with_bbox`（:248）走 init_state → add_new_points_or_box → propagate。
- `foundationstereo_onnx.py`：`FoundationStereoProcessorOnnx`（:142）构造 InferenceSession（CUDA EP 优先），`infer`（:240）做 InputPadder padding、视差→深度换算（:318）；ORT 日志噪声用 `set_default_logger_severity(3)` 压掉（:31）。
- `roma.py`：五个多元组 transform 类（`TupleResize`:28 / `TupleToTensorScaled`:76 / `TupleTensorNormalize`:92 / `TupleCompose`:127 等）服务成对图像；`FeatureMatchingInfer`（:183）加载 roma_outdoor（DINOv2 backbone）权重；`_process_batch`（:478）输出稠密对应点。

**configs/schema.py（配置唯一事实源）**：19 个 dataclass 组成配置树，顶层 `NVBundleSDFConfig`（:317）总装 camera_config/bundletrack/foundation_stereo/sam2/nerf/texture_bake/roma/base_path 八大节；bundletrack 又嵌套 segmentation/depth_processing/bundle/keyframe/sift/feature_corres/ransac 等子节（`BundleTrackConfig`:179）。`data/configs/base.yaml` 是同构 YAML 镜像——两处结构一一对应，改行为前先在两边建立映射。注意 CLI 实际只校验六段存在性（`main.py:182`），schema dataclass 主要给程序化构造用。

**cli/main.py（457 行）**：除 §3 的四步编排外，值得记的三件事：自定义 `PROGRESS=25` 日志级别填 INFO(20)/WARNING(30) 之间空隙（:36-37）；输出目录会整体复制输入数据（幂等跳过已存在项）；三份 DataLoader 同数据不同 downscale——跟踪/NeRF/纹理各有独立的 `downscale`+`min_resolution`（`main.py:351-362`），低于 `min_resolution` 时 dataloader 会强制把 downscale 收回 1.0 并上采样保护（`reconstruction_dataloader.py:107-112`）。

## 5. 构建与部署

本仓**没有环境安装脚本**——全部重依赖固化进 Docker，这是刻意设计（`deploy/compose/deploy.sh` 592 行是唯一部署入口）。

**docker/Dockerfile（313 行，x86 主力）**：基座 `nvcr.io/nvidia/pytorch:25.04-py3`（:1），其上源码编译 cmake/Eigen/OpenCV 4.12(+contrib, CUDA)/PCL/pybind11/yaml-cpp，然后依次装 kaolin（:189，源码 setup.py，CUDA arch 列表 7.0→12.0）、pytorch3d、onnxruntime-gpu、baspacho+theseus（:199-213，Theseus 要 BASPACHO_ROOT_DIR 指向自编译的 ba-spacho 求解器）、flash-attn、**BundleSDF 仓 nvbundlesdf 分支**（:234——先编译 mycuda 扩展、再从 BundleTrack 子目录编译出 `my_cpp*.so` 装进 site-packages，:250-265）、SAM2（:269）与 RoMa（:275，钉死 commit `edd1b8b`）。末段 COPY src/notebooks/data、editable 安装本包、配无 token Jupyter（8888 端口）。环境变量四处关键：`PIP_NO_BINARY=torch,...`（:68，防 pip 重装 torch）、HPC-X UCX 的 LD_LIBRARY_PATH（:220，注释说明是 Ubuntu 24.04 兼容问题）、`PYOPENGL_PLATFORM=egl`（:223）+ NVIDIA EGL vendor（:225），离屏渲染 headless 必需。

**docker/Dockerfile.aarch64（295 行，Jetson Orin 变体）**：基座换 `-igpu` 后缀（:1），PCL 1.10 + OpenCV 用 `CUDA_ARCH_BIN="8.7"` 对准 Orin（:56），pip 走 jetson-ai-lab JP6 cu129 源（:102），kaolin 钉 v0.18.0（:163-164）。

**deploy/compose/deploy.sh**：`uname -m` 探测架构选 Dockerfile（:19-31）；五组权重下载全带 MD5 白名单校验（:258 起）——RoMa 两件（GitHub release + fbaipublicfiles DINOv2）、SAM2 两件（HuggingFace）、FoundationStereo ONNX 一件（**只能从 NVIDIA NGC 拉**，:315-317，失败时提示手动去 catalog.ngc.nvidia.com）。docker-compose.yml 挂 src/data/notebooks 三卷进容器、`runtime: nvidia` + `shm_size: 8gb`。

**冒烟**：`test_reconstruction.sh` 在仓根找镜像（没有就先 deploy.sh setup），`docker run --gpus all` 跑 retail_item 样本全管线。开发机装依赖的替代路径只有 `pip install -e src/`——但 BundleTrack 的 `import my_cpp`（`nvbundlesdf.py:56`）和 romatch/sam2 三个包仍需自己解决，这也是官方只推 Docker 的原因。

## 6. 新人 14 步导览摘要

图谱 tour 的 14 步本质是一条"先看结果、再进管线、最后看边界"的路线，浓缩如下：

1. **总览**（README/CHANGELOG/CITATION）建立四阶段认知 → 2. **demo notebook**（42 cell 走完 real2sim 全流程，cell 4 有各阶段耗时参考）建立直觉 → 3. **容器层**（Dockerfile ×3 + deploy.sh）理解环境为何一键化 → 4. **包骨架与 CLI**（`cli/main.py` 读调用时序）→ 5. **配置系统**（schema.py ↔ base.yaml 映射）→ 6. **数据入口**（read_video + ReconstructionDataLoader 的 v1/v2 双版本协议）→ 7. **SAM2** → 8. **FoundationStereo ONNX** → 9. **位姿跟踪与全局优化**（run_track/RoMa/Theseus 三角）→ 10. **SDF 核心**（nerf_runner.py 主线：训练→提网格→烘焙）→ 11. **几何工具箱**（tool.py，theseus_optimizer 和 nerf_runner 都 import 它，改动影响面大）→ 12. **资产出口**（OBJ→USD→USDZ）→ 13. **交互可视化**（visualization.py 三件套，接新数据排查第一步）→ 14. **测试与治理**（E2E 套件；注意 CONTRIBUTING.md 明言**不接受外部贡献**、漏洞必须走 PSIRT 不走 GitHub issue）。

建议阅读顺序照 tour 原序即可，唯一强化：第 4 步读 `cli/main.py` 时对照 §3 数据流逐行核对四步调用点，这是把全仓串起来的最短路径；第 10 步 nerf_runner.py 不要通读，按"八叉树→损失→位姿参数化→烘焙"四个锚点跳读。

## 7. 已知坑与勘误

新人最容易踩的八个点（全部源码实证）：

1. **文档包名漂移**：`src/README.md:14` 起与主包 `__init__.py` 的 Example Usage docstring 都还在写 `from nvidia.reconstruction3d.object.networks import NVBundleSDF`——这个包路径**不存在**，实际是 `nvidia.objectreconstruction`（pyproject 入口 `nvidia-3d-reconstruct = "nvidia.objectreconstruction.cli.main:main"`，`src/pyproject.toml:116`）。照 README 抄 import 会 ImportError。
2. **三个版本号并存**：pyproject `0.2.0`（`src/pyproject.toml:7`）、CLI `--version` 硬编码 `0.1.0`（`cli/main.py:261`）、包 `__version__ = "1.0.0"`（`__init__.py:27`）。E2E 测试断言的是 CLI 的 `0.1.0`（`tests/e2e/test_reconstruction_pipeline.py:39`）——升版本时三处+测试要一起动，否则测试红。
3. **pytest 双配置打架**：`tests/pytest.ini`（含 slow/e2e/unit/gpu 四 marker 定义、3600s 超时）与 `src/pyproject.toml` 的 `[tool.pytest.ini_options]`（`--strict-markers` + `filterwarnings = error`）同时存在。pytest 以"最靠近 rootdir 的配置"取胜——从仓根跑和从别处跑可能吃到不同配置，遇到 marker unknown 或 warning-as-error 先查这个。
4. **scipy 双清单微差**：`src/pyproject.toml:67` 钉 `scipy==1.15.1`，`src/requirements.txt:10` 钉 `scipy==1.15.2`——两份清单各自安装会得到不同 scipy；排查数值差异时先核对实际装的是哪个。
5. **`num_iter_outter` 是血统不是笔误**：schema.py:94、theseus_optimizer.py:53、base.yaml:60/121 四处的 "outter" 拼写沿袭自 BundleSDF/BundleFusion 的 C++ 原始命名（theseus_optimizer.py:104 注释原文 "Outter/Inner Loop optimization like BundleFusion"）。**不要"顺手修正"**——改了就与上游配置和 C++ 扩展的 YAML 键对不上。
6. **TF32 全局设置竞争**：`sam2infer.py:73-74` 在**模块导入期**全局开 TF32（SAM2 上游代码带入，Ampere+ 才生效），而 `roma.py:216` 在 RoMa 模型初始化时全局 `torch.set_float32_matmul_precision('highest')`（关 TF32，注释引 RoMaV2 issue #35：RoMa 权重对 TF32 数值敏感）。两者都是进程级全局开关，同进程先后执行会互相覆盖——CLI 顺序恰好是 SAM2 先跑、RoMa 后初始化所以"碰巧"正确；若改流程顺序或单独复用某个模块，务必检查精度设置时序。跟踪/优化另有 `set_nvbundlesdf_precision` 强制 float32 兜底（`nvbundlesdf.py:78`），Theseus 也用 `torch.autocast(dtype=float32)` 防 BFloat16 问题（`theseus_optimizer.py:356`）。
7. **配置路径全是容器绝对路径**：schema 默认值与 base.yaml 里大量 `/workspace/3d-object-reconstruction/...`（如 `SAM2Config` 默认 checkpoint，schema.py:41-46），裸机跑必须改配置；base.yaml:197 还有个 `//workspace` 双斜杠笔误（POSIX 下无害，但别当规范抄）。
8. **FoundationStereo 权重需 NGC 手动**：deploy.sh 对 RoMa/SAM2 都能自动下载，唯独 FoundationStereo ONNX 走 NGC API 重定向常失败（deploy.sh:322-338 有完整的失败兜底与手动指引）——首次部署卡在深度估计一步先查这个文件在不在。

另有两点边界认知：`optimizer_type: theseus` 注释明言"商业构建只支持 Theseus，bundlefusion 已移除"（base.yaml:59）——旧 BundleSDF 用户别找 C++ OptimizerGPU；CONTRIBUTING.md 只有一行"不接受外部贡献"，这不是文档缺失，是政策。

## 8. 与生态的关系

本仓本质是**五个研究项目的工业化编排层**，每个上游各司其职：

| 上游 | 角色 | 在本仓的落点 |
|---|---|---|
| **BundleSDF**（NVlabs，CVPR 2023） | 神经 6-DoF 物体跟踪与重建的学术原型，提供 BundleTrack C++ 位姿跟踪引擎 | Docker 里 clone 其 **nvbundlesdf 分支**（Dockerfile:234），编译出 `my_cpp` Python 扩展（Bundler/YamlLoadFile）+ libBundleTrack.so；本仓 NVBundleSDF 类是它的 Python 重组版 |
| **BundleTrack** | BundleSDF 的跟踪子系统（BundleSDF 仓内含） | Dockerfile:250-265 单独编译安装；运行期以 `import my_cpp` 消费（nvbundlesdf.py:56） |
| **SAM2**（Meta segment-anything-2） | 视频目标分割，"只重建物体不重建背景"的守门人 | sam2infer.py 全套封装 + HuggingFace 权重 sam2.1_hiera_large |
| **FoundationStereo**（CVPR 2025 零样本立体匹配） | 左右目视频 → 米制深度，本仓**不训练**任何深度网络只消费它 | ONNX 形态从 NVIDIA NGC 分发（deployable_foundation_stereo_s_dynamic_v2.0），foundationstereo_onnx.py 纯推理封装 |
| **Theseus**（Meta） | 可微优化库，本仓用它重写了原 C++ OptimizerGPU | theseus_optimizer.py：AutoDiffCostFunction + LevenbergMarquardt（:297/:344），Docker 里连 baspacho 稀疏求解器一起源码编译 |
| **RoMa**（Parskatt） | 稠密鲁棒特征匹配，为全局位姿优化供 3D-3D 对应点 | roma.py 封装 roma_outdoor（DINOv2 backbone），Docker 钉 commit `edd1b8b`（Dockerfile:276）防上游漂移 |
| **kaolin**（NVIDIAGameWorks） | 3D 深度学习库，本仓用其 **SPC 八叉树**做光线追踪加速与转台可视化 | nerf_runner.py:33 起：quantize/octree/raytrace 全套 ops；visualization.py 的 IpyTurntableVisualizer |
| 周边小件 | pytorch3d / nvdiffrast / baspacho / flash-attn / pxr(OpenUSD) | 分别服务几何渲染、纹理、稀疏求解、注意力加速、USD 出口 |

一句话理解生态位：BundleSDF 贡献跟踪、FoundationStereo 贡献深度、SAM2 贡献分割、RoMa+Theseus 贡献全局优化、kaolin 贡献加速结构，本仓把五者黏成"视频进、资产出"的商业级管线（0.2.0 起 ONNX 化深度 + Theseus 化优化 + USD 化出口 + ARM64 化部署，都是把研究原型往工业交付推的改造）。

---

### 新人第一周建议

Day1：跑 demo notebook（Docker 起 Jupyter）看全流程产物 → Day2：读 `cli/main.py` 对照数据流 → Day3：schema.py ↔ base.yaml 对照改一个参数（如 `nerf.n_step`）重跑感受影响 → Day4：精读 theseus_optimizer.py（389 行，最小的核心）→ Day5：带着 §7 坑清单回头扫 nerf_runner.py 四个锚点。
