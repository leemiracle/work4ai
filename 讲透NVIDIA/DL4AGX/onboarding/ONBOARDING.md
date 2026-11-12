# DL4AGX Onboarding（NVIDIA DRIVE/Jetson AGX 深度学习案例集）

> 图谱基线：635 节点 / 837 边 / 14 层 / 14 步 tour / 0 issues / fingerprints 326 文件 @ 9f7b2910。
> 仓库定位：NVIDIA 官方自动驾驶（AV）模型在 DRIVE Orin 平台的**部署案例集**——不是单一产品，而是「13 个部署方案 + 3 个硬件友好模型 + 2 份方法论指南」的矩阵。本 Onboarding 按八节展开，全部行号锚从源码实测。

## 1. 项目定位：这是什么，不是什么

DL4AGX（Deep Learning for AGX）是 NVIDIA 面向 DRIVE AGX Orin / Jetson AGX 的深度学习部署示范仓库。根 README（`README.md`，1-27 行）给出两级目录：`AV-Solutions/`（13 个部署方案）与 `Models/`（3 个硬件友好模型）。

理解本仓的关键一句话：**案例集是「补丁 + 工具 + 推理壳」，不是模型源码本体**。`.gitmodules`（1-43 行）把 UniAD（OpenDriveLab）、BEVFormer_tensorrt（DerryHub）、nuscenes-devkit（nutonomy）、stb、Far3D（megvii-research）、mmdetection3d（open-mmlab）、Lidar_AI_Solution（NVIDIA-AI-IOT）共 8 个 submodule 挂进来，模型代码全部留在上游，本仓提供的是把模型搬进 TensorRT 的完整改造链：ONNX 导出补丁 → TRT 插件 → C++ 推理 app → Docker 交叉编译。

两份通用方法论指南是全仓套路的浓缩：
- `AV-Solutions/onnx-export-guidance/README.md`（579 行）：TorchScript exporter 实践——opset 选择、动态 shape、自定义算子注册、常见导出坑。
- `AV-Solutions/triton2cubin-plugin-guidance/README.md`（370 行）：用 Triton 写 kernel → 编译 PTX/cubin → CUDA Driver API 运行时加载进 TRT 插件，以 BEVPoolV2 为全流程示例。

时间跨度上，仓库同时容纳 TRT 8.6（enqueueV2 时代）与 TRT 10.7（enqueueV3 时代）两代实现（`AV-Solutions/uniad-trt/inference_app/README.md:4-6`），最新 commit 9f7b291 "Support IQ deprecation: replace 'best' with 'stronglyTyped'" 印证其持续跟进 TRT 新版本。

## 2. 仓库版图：双子项目 + 案例矩阵

14 层图谱的第一层（L01 仓库门面）到 L14（构建链）划出清晰矩阵：

| 板块 | 成员 | 图谱层 |
|---|---|---|
| 双子项目 | vad-trt、petr-trt（共享 bev_deploy 工具库） | L02-L05 |
| 大型全栈 | uniad-trt（导出线 + enqueueV2/V3 双代 app） | L06-L07 |
| 算子专题 | dcnv4-trt（同一算子三种实现形态） | L08 |
| 异构案例 | mtmi（GPU+DLA 协同） | L09 |
| 量化案例 | SparsityINT8、bevformer-int8-eq | L10 |
| 长尾案例 | far3d-trt、streampetr-trt、diffusion_planner-trt、llms-trtllm | L11 |
| 硬件友好模型 | DEST、ReduceFormer、SwinFree | L12 |
| 补丁资产 | 13 个 patch 文件（uniad-onnx-export.patch 7560 行为最） | L13 |
| 构建链 | 8 组 dockerfile + CMake 交叉编译 + setup 脚本 | L14 |

补丁层（L13）是理解改造哲学的核心：`AV-Solutions/uniad-trt/patch/uniad-onnx-export.patch`（7560 行）改写 UniAD 模型代码使其可导出；`plugins-trt10-support.patch`（513 行）做 IPluginV2→V3 接口迁移；`AV-Solutions/llms-trtllm/build_from_source_changes.patch`（6568 行）适配 TRT-LLM v0.13.0 源码编译；`Models/SwinFree/Swin-Free.patch`（1460 行）的目标仓是外部的 microsoft/Swin-Transformer（见第 8 节勘误）。「模型不动、上游打补丁」让每个案例都能跟随上游演进。

## 3. 双子主线：vad-trt 与 petr-trt

### 3.1 C++ 推理 app：header-only 三件套

两个项目各持一份**同构的** `app/lib/` 共享库（副本间几乎逐行一致，是又一处「共享库拷贝」标本）：
- `net.h`：Net 类封装引擎加载与推理。vad 与 petr 两份完全同构——`Enqueue(cudaStream_t)` 在 `AV-Solutions/vad-trt/app/lib/net.h:81`（petr 版同位），`EnableCudaGraph` 在 petr 版 `net.h:92` 捕获 CUDA Graph 消除 launch 开销，`net.h:94/98` 两条路径（Graph 优先/回退 Enqueue），类结束于 `net.h:107`，紧随其后的自由函数 `validate(Net&, frame_dir, key)` 在 `net.h:109` 与 Python 落盘参考数据对拍。
- `tensor.h`：`struct Tensor`（`AV-Solutions/petr-trt/app/lib/tensor.h:45-139`，vad 版同位）是裸 `void*` + Dims/DataType 描述的设备张量，提供 load/save bin 与 host↔device 拷贝。
- `visualize.cu`：696 行 GPU 绘制（BEV 视角/边框/轨迹），vad 与 petr 两份逐字节同构。

app 侧：`AV-Solutions/vad-trt/app/main.cpp`（267 行）以 `EventTimer`（main.cpp:55）计时、`main`（main.cpp:83）驱动 backbone→head 引擎链；`AV-Solutions/petr-trt/app/petrv1.cpp`（234 行）与 `petrv2.cpp`（245 行）结构同款，main 均起于 L46，读 config（`app/demo/v1_config.json`：warm_up/n_frames/perf_loop 计数 + 六路相机图像清单 + head 输入 mlvl_feats 由 backbone out.0 供给）。

### 3.2 Python 导出评估线：时序双版本

VAD 是时序模型，首帧与后续帧行为不同（有 prev bev/query 时先做 temporal warp 再 concat），故导出分两版：
- `AV-Solutions/vad-trt/export_eval/export_no_prev.py`（389 行）：首帧版。
- `AV-Solutions/vad-trt/export_eval/export_prev.py`（367 行，`main` 于 export_prev.py:138）：含时序前帧版，README 给出两条命令（`AV-Solutions/vad-trt/README.md:58/62`）。

对动态算子的手术集中在 `export_eval/patch/patch_head.py`（638 行）：`SelectAndPadFunction`（patch_head.py:46）把「按 flag 选择变长 query 再 padding」的手写循环（forward 内 L55-61 逐 batch 选择）替换为 TRT 插件调用，symbolic 在 patch_head.py:52 发 `g.op("custom_op::SelectAndPadPlugin", ...)`，并在 patch_head.py:160-165 三处（selected_map_query/pos/padding_mask）改写 head 前向；`patch_rotate.py`（135 行）同法处理旋转算子。配套 `save_data.py` 落参考数据、`test_tensorrt.py` 对拍。

上游适配坑写在 README：VAD 官方仓的 `img_norm_cfg` 需按 hustvl/VAD issue-18 修改（`AV-Solutions/vad-trt/README.md:28-34`），`points_in_boxes_gpu` 需改为 `points_in_boxes_all`（README.md:35-36）。

## 4. bev_deploy 双副本：共享工具库的 fork 学

vad-trt 与 petr-trt 各持一份同源 `export_eval/bev_deploy/` 工具库且已漂移（图谱 L03 专题层），是研究「工具库如何随项目分叉」的天然标本。核心差异：

1. **拼写漂移**：vad 版 `AV-Solutions/vad-trt/export_eval/bev_deploy/patch/inspect.py:158` 类名 `StaefulModuleTrt`（少一个 t，上游拼写原样保留）；petr 版 `AV-Solutions/petr-trt/export_eval/bev_deploy/patch/inspect.py:146` 已修正为 `StatefulModuleTrt`。有趣的是 petr 版只修了这一处——两版 inspect.py 的 `AutoStatufulModule`（vad:491 / petr:482）依然都拼错。
2. **包结构漂移**：vad 版多 `infer_shape/` 子包（`infer.py` 静态形状推断，被 inspect.py:38 引用）；petr 版删掉了这个依赖。
3. **hook 框架增量**：petr 版 `hook/hook.py` 较 vad 版多出三类适配——`functools.partial` 的函数名解包（petr hook.py:87-92）；空 args 防护（vad 版注释 TODO，petr hook.py:111-113 落地为 `if len(args) != 0`）；意外 self 替换时的 `p.requires_grad = False` 兜底（petr hook.py:124-133）；挂接类目扩展 BatchNorm1d/Conv1d（petr hook.py:229/231）。
4. **TraceableDict**：petr 版 `hook/traceable_dict.py:33` 多一个 `update` 方法。
5. **算子注册面**：vad 版有 `patch/bevformer/ms_deform_attn.py`（BEVFormer 系 MSDA 处理器）而 petr 版 `patch/custom_aten.py` 不含 `infer_grid_sample`。

hook 框架本身是「无侵入追踪」的范本：`Hook` 以 `functools.wraps` 包装目标 callable（vad hook.py:99-135 的 `_wrap`/`wrap`），捕获入出参供 inspect 侧重建 TRT 可导的等价模块。

## 5. 算子落地：IPluginV2 三家族与 DCNv4 三形态

### 5.1 vad-trt 插件三家族（图谱 L04）

`AV-Solutions/vad-trt/plugins/` 下三组插件共享统一范式——**cpp 承载 IPluginV2 生命周期，.cu 承载 kernel**：
- `multi_scale_deform_attn/`：BEVFormer 系 MSDA。`ms_deform_attn.cpp:67` getOutputDimensions、:116 supportsFormatCombination 完成格式协商；enqueue 声明于 `ms_deform_attn.h`，kernel 主体在 `ms_deform_attn_kernel.cu`，设备函数族在 `ms_deform_attn_kernel.cuh`（284 行：im2col/采样/聚合）。
- `rotate/`：`rotate_plugin.cpp:51/100` 同款协商接口，计算在 `rotateKernel.cu`。
- `select_and_pad/`：把动态数量的 query 选择结果填充到固定长度支撑静态 shape；`decideTemp()`（`select_and_pad.h:94` 声明、`select_and_pad.cpp:119` 调用）依 batch 决定工作区布局。

每个插件目录各有一份同构 `common.h`（GET_BLOCKS 网格计算 + caughtError 错误包装）。

### 5.2 DCNv4 三形态（图谱 L08）

`AV-Solutions/dcnv4-trt/README.md:4-7` 定义了同一算子的三条落地路径（Figure 1）：
- (a→b) `dcnv4Plugin/`：原始实现（`dcnv4_plugin.cpp` 389 行，IPluginV2 全生命周期），TRT 图优化自动融合。
- (c) `dcnv4PtxPlugin/`：Triton→PTX 工作流前身——**5 个 .ptx 汇编直接作为文本资产提交**（dcnv4_stage0_b1/b128、stage1-3_b1.ptx），`dcnv4_ptx.cu:119/124/163/243` 经 `cuModuleLoadDataEx` 运行时加载，满足特定 shape/dtype 约束（README:109 列出 128x3136x64 等 5 种组合）时接管 dcnv4Plugin 的 kernel 调用。FP16 下 2.48ms→2.35ms（README benchmark 表）。
- (d) `dcnv4FusePlugin/`：value/offset 不切分直接入插件，`tools/fuse_value_and_offset.py`（79 行）改写 ONNX 产出 fused 版，省掉 slice 算子的冗余访存（README:92-98 论证）。

## 6. 代差与异构：enqueueV2/V3 与 MTMI

### 6.1 UniAD 双代推理应用（图谱 L07）

`AV-Solutions/uniad-trt/inference_app/` 下两代 C++ app 同仓并存，目录结构完全平行（include×10 + src×7）：
- **enqueueV2**（TRT 8.6）：`src/tensorrt.cpp`（304 行）以 `__native_engine_context`（tensorrt.cpp:117）桥接原生引擎上下文，`EngineImplement : Engine`（tensorrt.cpp:164）对外提供稳定接口。
- **enqueueV3**（TRT 10.7，enqueueV2 已废弃）：核心代差是**动态 shape 输出**——TRT10 的 data-dependent-shape（DDS）输出无法预分配，`include/tensorrt.hpp:64` 定义 `DDSOutputAllocator : public nvinfer1::IOutputAllocator`，`tensorrt.hpp:113` 声明 `is_dynamic_dim`；`src/tensorrt.cpp:125/136/146` 实现 reallocateOutput/reallocateOutputAsync/notifyShape，tensorrt.cpp:254-271 对每个动态输出 `setOutputAllocator`，推理改为 `context->enqueueV3(_stream)`（tensorrt.cpp:275）。
- 两代的 `include/uniad.hpp`（各 278 行，TRACK_INS_MAX 常量 + 时序状态结构）在 **uniad.hpp:28 均有 include-guard 保护下的 `#include "uniad.hpp"` 自引用残留**（无害但是两版共有的复制痕迹）。

配套补丁：`patch/plugins-trt10-support.patch`（513 行）把 MSDA/Inverse/Rotate 三个插件迁移到 IPluginV3 接口（inference_app/README.md:13 点名这三个算子）。引擎构建时 prev_track_intances0-13 十四个时序状态张量走 min/opt/max 三档 shape（inference_app/README.md 的 trtexec 示例，MIN=901/MAX=1150）。

### 6.2 MTMI：一帧图像两种加速器（图谱 L09）

`AV-Solutions/mtmi/` 是 Drive Orin 异构调度的参考实现：encoder FP16 跑 GPU、depth decoder INT8 跑 DLA0、segmentation decoder INT8 跑 DLA1（`AV-Solutions/mtmi/README.md:4-7`），DLA 处理上一帧时 GPU 同时启动当前帧 encoder 形成流水重叠。关键文件：
- `inference_app/main.cpp`（557 行，main 于 main.cpp:535）：Feat/Tensor 内存抽象 + TRT GPU 引擎与 cuDLA 引擎双实例 + step_prepare/step_backbone 流水。
- `inference_app/src/cudla_context.cpp`（409 行）：cuDLA C API 包装——设备句柄、可加载构建（loadable）、内存张量注册与 CUDA 互操作绑定。
- `tools/onnx_split.py`（72 行）：把整网按边界拆成 encoder/seg_head/depth_head 三个子网。
- `tools/create_calibration_cache.py`（155 行）：PythonEntropyCalibrator 逐批供图生成 DLA INT8 校准缓存；README:60/84/95 展示 `--useDLACore=0/1 --buildDLAStandalone` 与 int8:chw32/dla_linear IO 格式。
- `include/lodepng.h`（2089 行）：vendored 单头 PNG 库负责输出落盘。

## 7. 量化双路线与硬件友好模型

### 7.1 显式量化（图谱 L10）

两条 INT8 路线对照：
- **SparsityINT8**（2:4 稀疏 + QAT）：`step1_sparse_training.py`（README:41 命令）用 APEX 做结构化剪枝微调；`step2_1_ptq_calibration.py`（README:53）PTQ 校准；`step2_2_qat_training.py`（README:63）QAT 恢复精度；`train_utils.py`（11 个公共函数，fanOut=22 的全仓枢纽）被三步复用；`infer_engine.py` 的 HostDeviceMem 管理 host/device 双端缓冲。Dockerfile 从源码编译 APEX 并开 `--permutation_search` 全局选项（`AV-Solutions/SparsityINT8/docker/Dockerfile:24-26`）。data/ 下 `valprep.sh` 是 **51000 行**的 ImageNet 验证集归类社区资产（纯 mkdir/mv 无控制流），`imagenet_data_setup.sh:14-16` 三个环境变量需按机器路径修改。
- **bevformer-int8-eq**（modelopt PTQ）：`tools/calib_data_prep.py`（`_add_data_to_dict` 聚合 nuScenes 输入为 npz）+ `results/onnx2trt_calib_npz.py`（DictDataset 逐批供图）构成校准闭环；`tools/onnx_postprocess.py` 处理图后处理；TRT 10 适配经 `bevformer_trt10.patch`（620 行）。

### 7.2 Models/（图谱 L12）

三个砍 softmax 注意力的硬件友好模型：
- **DEST**：`networks/DEST/simplified_attention.py:43` `Attention_MaxPool` 以 max 池化/reduction+逐元素乘替代注意力矩阵乘法；与 `semseg/simplified_attention_mmseg.py` 同源双版本（后者把 norm 织入 mmseg 规范）；`networks/DESTNet.py` 的 InvDepth 逆深度头 + `models/SelfSupModel_dest.py` 自监督光度重投影损失；b0-b5 全档配置（`configs/train_kitti_dest.yaml` 等）。
- **ReduceFormer**：`reduceformer/backbone.py` 的 RF_Attn 同思想（CVPRW2024，基于 EfficientViT 代码库）；b1/b2/b3 工厂对应 `configs/b1_rf.yaml`→`b3_rf.yaml` 三档缩放。
- **SwinFree**：size-varying window 替代 shifted window；核心资产是 `Swin-Free.patch`（1460 行），应用目标是外部 microsoft/Swin-Transformer 仓（`Models/SwinFree/README.md:23` `git checkout f82860bf`）。

## 8. 构建链与新人口径

统一范式：**x86 容器内导出/训练，Orin sm_87 交叉编译引擎**。
- 交叉编译锚点：`AV-Solutions/dcnv4-trt/CMakeLists.txt:14-16` 设 aarch64-linux-gnu-gcc/g++ 工具链，:22-25 硬编码 `/usr/local/cuda-11.4/` 路径，:38 `set(PTX_ARCH sm_87)`，:33-34 按 TARGET 切 TRT 头/库目录；`build.sh orin -DUSE_PTX=1` 一条命令出板端产物（dcnv4 README:134）。
- Docker 矩阵（L14）：vad/petr 用 nvcr pytorch:22.12-py3 + mmcv 栈；uniad 用 torch1.12 容器跑数据准备与导出；far3d 锁 `nvidia-modelopt==0.15.1`（`AV-Solutions/far3d-trt/docker/Dockerfile:23-25`，注释明言兼容 Far3D 依赖的老 torch/mmcv）；SparsityINT8 单 stage 源码编译 APEX；ReduceFormer 整仓 COPY + torchpack 固定 commit 安装（`Models/ReduceFormer/docker/Dockerfile:6` git+https@3a5a9f7a）；bevformer-int8-eq 用 TRT 26.01 容器。
- 免重编捷径：llms-trtllm 的 `setup_from_source_DeepSeek-R1-Llama-8B.sh` 把 aarch64 预编译静态库（batch_manager/executor/nvrtcWrapper，脚本 L21-23）直接覆盖进 TRT-LLM v0.13.0 源码树，免除在 Orin 上全量重编；L13 用 json_modifier 关闭 DeepSeek-R1-Distill-Llama 的 rotary_scaling（Orin 不支持该形态）。
- 长尾案例的迁移广度（L11）：far3d 的 `tools/export_onnx.py`（508 行）monkey-patch（`PatchMSDA` L70、`register_custom_op_symbolic` L172-173 注册 `trt::MultiscaleDeformableAttnPlugin_TRT` 与 aten::atan2）+ 三个 ExportWrapper 双管齐下；`inference_app/include/far3d.hpp:37-43` 用 StateTensor/InputTensor/TempBuffer 模板别名把传感器排布（CCHW/CHWC）编码进类型；streampetr 的 `visualize.py` 是与 C++ app 输出对照的 Python 基准；diffusion_planner 的核心资产即 1695 行 ONNX-export-and-TRT-engine-eval.patch。

**新人三步入门**：① 读两份 guidance README 建立导出与插件方法论框架；② 走 vad-trt README 全流程（插件构建→双版本导出→trtexec 建引擎→跑 app），这是最小完整闭环；③ 按需下钻——异构看 mtmi、量化看 SparsityINT8、代差看 enqueueV3、算子调优看 dcnv4PtxPlugin。陷阱提醒：submodule 未 init 时 uniad/far3d 的依赖不完整；cuOSD 无独立 repo 需手动放入 common/dependencies/（uniad inference_app/README.md:9-16）；vad 需先打 README:28-36 的上游修正。
