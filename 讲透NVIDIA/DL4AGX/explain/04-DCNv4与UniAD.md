# 04 · DCNv4 三形态与 UniAD 大补丁：算子优化的两条极端路线

## 角色定位

dcnv4-trt 与 uniad-trt 代表部署工作量的两个极端：前者对**单一算子**（DCNv4 可变形卷积）做三形态深度调优，后者对**整网全栈模型**（UniAD 感知-预测-规划一体）做 7560 行级导出改造。两者同把「上游不动、本仓补丁」哲学推到极致，合看即得算子落地方法论的完整光谱。

## 内部结构

**DCNv4 三形态**（`AV-Solutions/dcnv4-trt/README.md:4-7` 的 Figure 1）：
- (a→b) `plugins/dcnv4Plugin/dcnv4_plugin.cpp`（389 行）：原始 CUDA 实现的 IPluginV2 完整生命周期（构造 dcnv4_plugin.cpp:41 / :89 反序列化、getOutputDimensions :132、getSerializationSize :174），TRT 图优化自动做层融合，FP16 2.48ms；
- (c) `plugins/dcnv4PtxPlugin/`：**5 个 .ptx 汇编直接作为文本资产提交**（dcnv4_stage0_b1/b128、stage1-3_b1.ptx），`dcnv4_ptx.cu:119/124/163/243` 经 `cuModuleLoadDataEx` 运行时加载，README:109 限定仅 5 种输入组合（128x3136x64 等）被接管，FP16 2.35ms；
- (d) `plugins/dcnv4FusePlugin/dcnv4_fuse_offset_plugin.cpp`：value/offset 不切分直接入插件，自带数值验证器（dcnv4_fuse_offset_plugin.cpp:240 PluginChecker、:260 validate）；`tools/fuse_value_and_offset.py`（79 行）改写 ONNX 消掉 slice 算子的冗余访存（README:92-98 论证 [B,3136,64+112] 的读写节省）。
端到端 app `src/main.cpp`（359 行）三层结构：struct Tensor（main.cpp:69-162）、class SubNetwork（:182-246）、struct Application（:250 起，全链路计时与精度校验）。导出流水线 `tools/export_onnx.py` 四段：speed_test（export_onnx.py:86）、torch2onnx（:100）、onnx2trt（:114）、check（:131）。

**UniAD 导出线**：`patch/uniad-onnx-export.patch`（7560 行，全仓最大资产）改写模型可导出性；`tools/add_onnx_export_support.sh` 拷入 export_onnx.py 等 10 个支持文件；`tools/add_bevformer_tensorrt_support.sh` 从 BEVFormer_tensorrt submodule 拷入 **27 个文件**（FILES 数组：functions 7 算子 bev_pool_v2/MSDA/rotate/grid_sampler/inverse/MDC2D/MHA + modules 3 个 + utils 全套含 8 个测试）——即「17 个 TRT 友好算子」资产库（图谱口径）；`tools/export_onnx.py`（544 行，main 于 export_onnx.py:152）主脚本；`tools/prepare_calib_data.py`（main 于 prepare_calib_data.py:143）备校准数据。

## 外部连接

DCNv4 依赖 OpenGVLab/DCNv4 上游与 3rd_party/stb submodule（图像读写），基线模型 FlashInternImage-T。UniAD 挂 OpenDriveLab/UniAD + DerryHub/BEVFormer_tensorrt + nutonomy/nuscenes-devkit 三个 submodule（.gitmodules:1-16），五篇 documents 手册（env_prep/proj_setup/data_prep/train_export/explicit_quantization）覆盖环境→数据→训练→导出→量化全流程；`patch/plugins-trt10-support.patch`（513 行，IPluginV2→V3 迁移）衔接 inference_app 的 enqueueV3，三插件 MultiScaleDeformableAttnTRT/InverseTRT/RotateTRT 点名于 inference_app/README.md:18（见 05 篇）。DCNv4 侧共享头 `include/common.cuh`（145 行）被两个插件的 .cu include。

## 数据流

DCNv4 线：PyTorch FlashInternImage-T → `tools/export_onnx.py` 四段流水（torch2onnx→onnx2trt FP16→check）→ 可选 fuse 改写 → trtexec 建引擎 → DCNv4_app 三层执行。UniAD 线：submodule 拉源码 → 七连补丁按序应用 → 拷友好算子 → tiny 档训练（uniad-tiny-training-support.patch 1462 行）→ export_onnx.py 导出 → 校准/量化（explicit_quantization.md：modelopt 0.29.0 + TRT>=10.9 在 x86 加 Q/DQ，Orin 建 INT8 引擎）。

## 设计决策

三形态并存是罕见的诚实：不宣称一种最优，而把「图优化够不够」「PTX 手写值不值」「融合改图赚多少」各自量化（benchmark 表四种配置同精度 83.3% 只差时延）。PTX 形态是 triton2cubin 工作流的前身（guidance README 370 行即其方法论化）；fuse 形态证明算子边界可以上移到图改写层。UniAD 侧 7560 行补丁换来上游零 fork，代价是与上游 commit 强绑定（拷文件而非改 import，降低侵入）。

## 新人提示

读 dcnv4 先看 README:4-7 与 Figure 1 建立三形态心智模型——PTX 最快（2.35ms）但受 README:109 尺寸白名单约束，shape 不匹配静默回退原 kernel；.ptx 是文本文件可直接读。UniAD 线务必按 documents/proj_setup.md 的补丁顺序操作，顺序错会 patch 冲突；utils/test_trt_ops/ 的 8 个测试文件可单独跑，是验证插件安装的最小冒烟集。
