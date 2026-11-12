# 01 · vad-trt 主线：export_eval 补丁族与插件三家族

## 角色定位

vad-trt 是 DL4AGX 双子项目之一：把 hustvl/VAD（向量化自动驾驶模型）搬进 TensorRT 的端到端示范。它由两半构成——`export_eval/` Python 导出评估线（补丁族）与 `plugins/` 三家族 IPluginV2 算子；加上 `app/` 的 C++ 推理壳，构成全仓最完整的「PyTorch→ONNX→引擎→C++」闭环。README 248 行给出标准动线：插件构建→双版本导出→引擎→app（`AV-Solutions/vad-trt/README.md:248` 为全文末行）。

## 内部结构

导出线的第一道坎是**时序**：VAD 首帧无前帧状态，后续帧要先 temporal warp 再 concat 特征，故导出分两版——`export_eval/export_no_prev.py`（389 行，首帧）与 `export_eval/export_prev.py`（367 行，`main` 位于 export_prev.py:138，保留 prev bev/query 状态输入），README:58/62 分别给出两条命令。

第二道坎是**动态算子**。`export_eval/patch/patch_head.py`（638 行）是补丁族主战场：`SelectAndPadFunction`（patch_head.py:46）继承 `torch.autograd.Function`，forward（patch_head.py:55-61）里逐 batch 按 flag 选择变长 query；symbolic（patch_head.py:52）发出 `g.op("custom_op::SelectAndPadPlugin", ...)` 把整段循环折叠成一次插件调用；patch_head.py:85 以 `G_HANDLERS["SelectAndPadPlugin"]` 注册形状推断器；patch_head.py:160-165 在 head 前向三处（selected_map_query/pos/padding_mask）替换原逻辑。`patch_rotate.py`（135 行）同法处理旋转坐标系算子。hook 侧见 02 篇。

C++ 壳是 header-only 三件套：`app/lib/net.h:81` 的 `Enqueue(cudaStream_t)`、net.h:92 的 `EnableCudaGraph`（Graph 优先、net.h:94/98 回退）、net.h:109 的 `validate` 对拍；`app/lib/tensor.h:45-139` 的 `struct Tensor` 设备张量；`app/main.cpp:55` 的 `EventTimer` 与 main.cpp:83 的 main 驱动 backbone→head 引擎链。

## 外部连接

三家族插件各由「cpp 生命周期 + .cu kernel」组成，经 `plugins/CMakeLists.txt` 聚合：`multi_scale_deform_attn/` 的 `ms_deform_attn.cpp:67`（getOutputDimensions）与 :116（supportsFormatCombination）完成格式协商，kernel 声明在 `ms_deform_attn.h`、实现在 `ms_deform_attn_kernel.cu`、设备函数族在 `ms_deform_attn_kernel.cuh:284` 行规模；`rotate/` 的 `rotate_plugin.cpp:51/100` 同款协商；`select_and_pad/` 的 `decideTemp()`（`select_and_pad.h:94` 声明、`select_and_pad.cpp:119` 调用）依 batch 决定工作区布局——正是 export 侧 SelectAndPadFunction 的运行时对端。每个插件目录各持一份同构 `common.h`（GET_BLOCKS/caughtError）。上游 VAD 仓还需两处修正（README:28-34 的 img_norm_cfg 与 README:35-36 的 points_in_boxes_all）。

## 数据流

nuScenes 六路图像 →（export_eval `save_data.py` 落参考数据）→ ONNX（双版本）→ trtexec 加载插件建引擎 → `app/demo/config.json` 声明引擎链 → main.cpp 读图、预处理 → backbone 引擎 → head 引擎（内部 SelectAndPad/Rotate/MSDA 插件节点）→ `app/lib/visualize.cu`（696 行 GPU 绘制）输出；`export_eval/test_tensorrt.py` 与 Python 参考输出对拍。

## 设计决策

三个值得抄的决策：①**插件吸收动态性**——变长选择/padding 这类数据相关控制流放进插件，让 TRT 见到纯静态图（select_and_pad 把动态 query 填充到固定长度）；②**时序状态显式化为图输入**——不追逐导出完整循环，而是拆 no_prev/prev 两个静态图，运行时由 app 维护状态传递；③**CUDA Graph 捕获**（net.h:92）抹掉多引擎链的 launch 开销。代价是 patch_head.py 补丁与上游强耦合，上游改动需同步维护。

## 新人提示

先读 README:28-36 打好上游修正再谈复现；导出务必区分首帧/后续帧模型（两者引擎不同）；tree-sitter 对全部 .cu 文件零结构提取（ms_deform_attn_kernel.cu、rotateKernel.cu、select_and_pad_kernel.cu 在图谱中均为文件级节点），读 kernel 直接开源码；`plugins/*/common.h` 三份副本内容相同，改一处记得同步。
