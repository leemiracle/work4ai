# 讲透 NVIDIA/TensorRT

TensorRT OSS 仓（`github.com/NVIDIA/TensorRT`，commit `98adec8` = "TensorRT 11.3 OSS Release (#4858)"）全链路知识库。本仓=闭源推理引擎 `libnvinfer` 的开源配套面：Python 绑定与 wheel 流水线、Polygraphy/onnx-graphsurgeon/双量化工具链、约 40 个参考插件（含 BERT FMHA 预编译 cubin 资产）、Docker/CMake 构建部署与 Agent 技能卡。

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ 2026-10-26 | `deepwiki/`（INDEX.md + 全部章节页） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：**3344 节点 / 6537 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 1452 文件基线 @98adec82** |
| NOTES-DIGEST | ✅ | 仓内 `.understand-anything/NOTES-DIGEST.md`（532 条批阶段甄别笔记） |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md`（并行实例产出） |
| explain 组 1（C++/插件线，L01-L08） | ⏳ 并行实例撰写中 | 已落：`explain/01-NvInfer核心API谱系.md`；02-06 待落 |
| explain 组 2（Python/工具生态线，L09-L16） | ✅ 本文档实例 | `explain/07-12` 六篇，全部行号锚源码核实 |

## explain 索引

| 篇 | 主题 | 图谱层 |
|---|---|---|
| 01 | NvInfer 核心 API 谱系（伞形头/执行三件套/插件三代） | L02 · t02 |
| 02-06 | ONNX Parser / 插件公共基座 / BERT FMHA 与 cubin 资产 / 插件群（并行实例撰写中） | L03-L08 · t03-t09 |
| 07 | [pybind11 绑定：宏体世界与 vc Windows 体系](explain/07-pybind11绑定.md) | L09 · t10 |
| 08 | [Python 打包四 wheel 线：占位符模板 + PEP 517 后端](explain/08-Python打包四wheel线.md) | L10 |
| 09 | [Polygraphy 运行时：backend 分舱 / functor 流水线 / registry 盲区](explain/09-Polygraphy运行时.md) | L11-L13 · t12-t13 |
| 10 | [onnx-graphsurgeon 图手术：惰性求值与 Layer API](explain/10-onnx-graphsurgeon图手术.md) | L14 · t14 |
| 11 | [量化工具双域：cuda_ext 数值核与 QAT 前向](explain/11-量化工具双域.md) | L15 · t15 |
| 12 | [构建部署与 Agent 技能资产：cmake/docker/五张技能卡/DeBERTa](explain/12-构建部署与agent技能资产.md) | L16 · t16 |

## 勘误与重大甄别清单（源码级实证，读文档前必看）

以下各条均经源码行号核实（锚点为 `路径:行`，行号以 commit 98adec8 为准）：

1. **cubin 资产非源码（最大甄别）**：`plugin/bertQKVToContextPlugin/fused_multihead_attention(_v2)/` 下百余个 `*_kernel.sm{75..120}.cpp`（单文件最高 36080 行/约 669KB，如 v2 fp16_384_64 sm90）几乎全为 xxd 风格十六进制字面量——SASS 二进制的 C++ 源码化封装，不是手写代码；构建期按架构选择性链接，运行期驱动按 GPU 选载。它们占图谱整层 L06（181 节点）。
2. **两代 cubin 符号命名并存**：同批机器生成文件中旧代 `*_kernel_sm{arch}_cubin/_cu_o`（fatbin）与新代 `cubin_fmha_v1|v2_*_cu_cubin` 共存，生成脚本不在仓内——按符号名断代可考证 cubin 生产管线迭代史。
3. **FCPlugin 官方已弃用 + cuBLASLt 启发式**：`plugin/fcPlugin/README.md:14` 明示 deprecated since 10.6、被 `IMatrixMultiplyLayer`（`addMatrixMultiply()`）取代；实现并非朴素 GEMM——`fcPlugin.cpp:70-97` `customMatmulRun` 经 `cublasLtMatmulAlgoCheck` 启发式择优，`:136` `LtGemmSearch` 做算法搜索；cuBLASLt 经 `plugin/common/cublasLtWrapper.cpp` 双平台 dlopen（`uint64_t data[N]` 复刻不透明 ABI，不 include cublasLt.h）。
4. **instanceNorm cuDNN→自研迁移**：`plugin/instanceNormalizationPlugin/README.md:14` 三代轨迹——v1 弃于 10.3、v2 弃于 10.12、推荐 v3 或原生 `INormalizationLayer`；Legacy 路径仍持 cuDNN 遗留（`instanceNormalizationPlugin.h:113-119` `cudnnHandle_t` 等句柄，`instanceNormCommon.h:778` `convertTrt2cudnnDtype`），v3 现代实现走自研 kernel（`instanceNormFwdImpl.cu:46-49` 模板化 `instanceNormFwd`，`__launch_bounds__(THREADS_PER_CTA, DESIRED_OCCUPANCY)`）。
5. **`##TENSORRT_MODULE##` 占位符**：`python/packaging/bindings_wheel/tensorrt/__init__.py`（L26/L33/L84/L96/L135）与 frontend_sdist 全部 plugin/*.py（各 L18）在源码树中**不是合法 Python**（import 即 SyntaxError）——构建期由 `python/scripts/process_wheel_template.py` 的 `contents.replace()` 系列替换；读这份"__init__.py"须先过占位符心智转换。
6. **golden_io_path 全域悬空**：所有插件 `*PluginConfig.yaml` 的 `golden_io_path`（部分还有 `golden_reference_script`）指向的 `*PluginGoldenIO.json`/`*PluginReference.py` **全仓不存在**（fc/cropAndResize/efficientNMS/fft/groupNorm/roiAlign/scatter/skipLayerNorm/disentangled 等逐一 find 零命中）——golden 数据是仓外生成物，YAML 字段是测试 harness 约定而非仓内路径。
7. **`postprocess_kernal` 原拼写**：`plugin/common/kernels/decodeBbox3DKernels.cu:45`（定义）与 `:164`（调用）——`kernal` 是源码原拼写，非文档 typo，勿"顺手修正"。
8. **ATen 同源移植**：`plugin/scatterElementsPlugin/TensorInfo.cuh` 的 `IndexToOffset<tDims>` 模板特化链是 PyTorch ATen `TensorInfo` 的同源自包含副本（`scatterElementsPluginKernel.cu` 唯一消费）；同插件 kernel 头注明 Modified from pytorch_scatter（Matthias Fey, TU Dortmund）。
9. **Agent 技能卡实为五张（非四张）且在仓根**：`.agents/skills/` 实测 5 目录——重卡 `trt-perf-analysis`（图谱 82 节点：报告模板/校验脚本/常量表）与 `trt-strong-typing-migration`（8 节点），轻卡 trt-cpp-runtime-quickstart/trt-onnx-quickstart/trt-torch-quickstart（各单 SKILL.md）；位置在仓根而非 tools/Polygraphy 之下。
10. **docs 真身在 docstring**：`tools/Polygraphy/docs/**/*.rst` 几乎全为 `automodule` 存根页（正文 Sphinx 构建时从源码 docstring 注入），读文档直接读 `.py` docstring 更新更快；`docs/backend/trt/algorithm_selector.rst` 带 TRT 10.8 弃用警告，是该域唯一带弃用声明的页面。
11. **scatterElements 版本号反直觉**：`scatterElementsPluginLegacy.cpp:43`（V2 文件）`kSCATTER_ELEMENTS_VERSION{"1"}`，`scatterElementsPlugin.cpp:49`（V3 文件）`kSCATTER_PLUGIN_VERSION{"2"}`——文件名 Legacy/V3 与版本号 1/2 语义相反，V2/V3 零继承零代码共享（接口代际双轨）。
12. **同注册名多版本插件族**：`embLayerNormVarSeqlenPlugin.cpp:38` 与 embLayerNorm 主实现的注册字符串完全相同（"CustomEmbLayerNormPluginDynamic"），同库 6 个 Creator 仅靠版本号 "1"-"6" 区分（v1/v6 固定序列、v2/v4 HFace、v3/v5 MTron）；类似地 plugin 注册名≠实现类名是全仓惯例（如 EfficientNMS_TRT 是常量名非类名）。
13. **cropAndResize README 双失真**：类名过时（README 称 CropAndResizePlugin/cropAndResizePluginCreator，实际 `cropAndResizePlugin.h:36/115` 为 CropAndResizeDynamicPlugin/CropAndResizeDynamicPluginCreator，IPluginV3 系）+ 参数表互换（crop_width 行写 "The height of the output"）；且 `CropAndResizeDynamic_PluginConfig.yaml` 的 output_dims 末两维与实现相反（`cropAndResizePlugin.cpp:80-86` 实际输出 [N,R,C,H,W]）。
14. **proposalLayer README 双 Limitations 节自相矛盾**：`plugin/proposalLayerPlugin/README.md` L54 与 L61 两个 "## Limitations"——前者称锚点数上限 1024（与源码不符，锚点实为 261888，被 cap 的是 prenms_topk≤1024），后者口径正确；系 2022-01 追加与 2025-05 废弃标注两次编辑未删旧节。
15. **Polygraphy vendor 副本无打包元数据**：`tools/Polygraphy/` 全树无 pyproject.toml/setup.py（Makefile 的 `python3 -m build --wheel` 在开源树内不可用）；PyPI 发布走 NVIDIA 内部 Artifactory→Kitmaker 的 staged wheel 管线。
16. **onnx-graphsurgeon 死代码**：`onnx_graphsurgeon/importers/onnx_importer.py` 的 `get_onnx_tensor_type` 逐字重复定义两次（L170 与 L194，函数体完全相同），后者覆盖前者，前者纯死代码。
17. **docker 双脚本默认 tag 不一致**：`docker/launch.sh:19` 默认 `tensorrt-ubuntu24.04` vs `docker/build.sh` 默认镜像名 `tensorrt-ubuntu`——连跑需手动 `--tag` 对齐；`docker/downloadTRT.sh:5` 与 `:47` 两处硬编码 TRT_VERSION="11.3.0.99"，升级须同步双改。
18. **efficientNMS 三代废弃轨迹**：EfficientNMSONNXPlugin 2023-06 弃用→2026-03 移除；EfficientNMS_TRT 2025-05（TRT 10.12）弃用；官方替代是**核心层 INMSLayer 而非其他插件**——检测 NMS 正在从插件回归引擎本体。
19. **检测族 README 大小写笔误**：detectionLayer README 写 `DetectionlayerPluginCreator`（小写 l），源码实为 `DetectionLayerPluginCreator`（`detectionLayerPlugin.h:103`）；generateDetection README 写 `generateDetectionPluginCreator`，源码实为 `GenerateDetectionPluginCreator`（`h:111`）。
20. **插件测试配置口径三陷阱**：①顶层 inputs 空 ≠ 插件零输入被推翻（gridAnchor 的 config1.input_layer 是 harness 封装层占位）；②取值约束混用三种语法（字面量/"=1" 表达式/"=pinf" 正无穷哨兵）；③min "0,0" 可能比 cpp 校验宽松（pillarScatter 实际要求严格大于 0）。

## 图谱阅读指引

16 层即阅读动线：L01-L02 治理与 API 契约 → L03 ONNX parser → L04-L08 插件宇宙（公共基座→BERT FMHA→cubin 资产→插件群×2）→ L09-L10 Python 线（绑定→打包）→ L11-L13 Polygraphy 三层（核心/示例测试/文档扩展）→ L14 gs → L15 量化双域 → L16 构建部署收官。树状细节见仓内 `tour` 16 步（t01 全景→t16 onnx→engine→deploy 数据流）。

## 维护说明

- 本 README 与 explain/07-12 由 explain 组 2 实例产出（2026-11-06）；组 1（01-06）与 onboarding 由并行实例产出，状态表以盘上文件为准。
- 所有行号锚以 commit `98adec8` 为基线；上游演进后请用 fingerprints（1452 文件）做增量对账再修订。
- 勘误清单条目 16 为组 2 撰写期新发现（非 NOTES-DIGEST 既有），已在 `explain/10` 正文展开。
