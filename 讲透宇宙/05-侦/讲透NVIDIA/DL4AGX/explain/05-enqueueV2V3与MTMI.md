# 05 · enqueueV2/V3 代差与 MTMI 异构：TRT8→10 迁移与 GPU+DLA 协同

## 角色定位

本篇覆盖推理壳的两个进阶命题：**API 代际迁移**（uniad-trt 同仓并存 enqueueV2/V3 两代 app，示范 TRT 8.6→10.7 的 enqueueV2 废弃过渡）与**片上异构**（mtmi 在 Drive Orin 上把一帧图像同时交给 GPU 与两颗 DLA）。前者回答「TRT 升级时应用层要改什么」，后者回答「SoC 全算力怎么吃满」。

## 内部结构

**enqueueV2**（`AV-Solutions/uniad-trt/inference_app/enqueueV2/`，TRT 8.6）：`src/tensorrt.cpp`（304 行）的 `__native_engine_context`（tensorrt.cpp:117）封装原生引擎/上下文生命周期，`EngineImplement : Engine`（tensorrt.cpp:164）以 shared_ptr 持有并以纯虚接口 Engine 对外——应用层只依赖抽象头 `include/tensorrt.hpp`。`include/uniad.hpp`（278 行）是 kernel 编排层：TRACK_INS_MAX 常量、十四个时序状态张量（prev_track_intances0-13）与全管线数据结构，衔接插件节点与前后处理 kernel。

**enqueueV3**（TRT 10.7，README:4-6 明言 enqueueV2 deprecated）：代差核心全在两文件——`include/tensorrt.hpp:64` `class DDSOutputAllocator : public nvinfer1::IOutputAllocator`（适配 data-dependent-shape 动态输出），`tensorrt.hpp:113` 声明 `is_dynamic_dim`；`src/tensorrt.cpp`（417 行，较 V2 的 304 行增 113 行）实现 reallocateOutput（tensorrt.cpp:125）/reallocateOutputAsync（:136）/notifyShape（:146），:254-271 为每个动态输出建 allocatorMap 并 `setOutputAllocator`（:270），推理调用改为 `context->enqueueV3(_stream)`（:275）；V3 的 `EngineImplement`（tensorrt.cpp:201）扩展至 23 方法。

**mtmi**（`AV-Solutions/mtmi/inference_app/main.cpp` 557 行，main 于 main.cpp:535）：同一帧图像走 GPU（encoder，FP16）+DLA0（depth decoder，INT8）+DLA1（seg decoder，INT8）三种加速器（README:4-7）；DLA 处理上一帧时 GPU 同时跑当前帧 encoder，流水重叠。DLA 侧核心 `src/cudla_context.cpp`（409 行）：cuDLA C API 包装——设备句柄、可加载构建（loadable）、内存张量注册与 CUDA 互操作绑定。

## 外部连接

两代 app 目录结构完全平行（include×10 + src×7），`uniad.hpp:28` 两版均有 include-guard 保护下的 `#include "uniad.hpp"` 自引用残留（无害的复制痕迹，见 README 勘误）。V3 依赖 `patch/plugins-trt10-support.patch`（513 行）把 MSDA/Inverse/Rotate 三插件迁到 IPluginV3（inference_app/README.md:13）。共用依赖 cuOSD 无独立 repo，需手动放入 common/dependencies/（inference_app/README.md:9-16），stb 为 submodule。mtmi 侧 `tools/onnx_split.py`（72 行）把整网拆三子网、`tools/create_calibration_cache.py`（155 行）生成 DLA INT8 校准缓存、`include/lodepng.h`（2089 行 vendored 单头库）负责输出 PNG 落盘；五份 mtmi*.onnx 为拆分后引擎资产。

## 数据流

uniad 线：jpg 图像 + data_prep 生成的 metadata（timestamp/l2g_r_mat 等）→ app 读入 → V2 走 bindings+enqueueV2，V3 走 setOutputAllocator+enqueueV3 → 动态输出（如检测框数）由 DDSOutputAllocator 在 notifyShape 回调后按真实维度现分配 → 时序状态回写供下一帧。mtmi 线：单帧图像 → GPU 预处理（kernels.cu 的 resize/归一化/量化）→ GPU encoder FP16 → 特征分流 → DLA0/INT8 depth head 与 DLA1/INT8 seg head（--useDLACore 与 --buildDLAStandalone、int8:chw32，README:74-95）→ 后处理 → lodepng 写 PNG。

## 设计决策

V3 迁移的最小改动面值得抄：应用层经 Engine 抽象隔离，代差只落在 tensorrt.cpp/hpp 两个文件；动态输出从「预分配最大 buffer」变为分配器回调，内存占用按真实 shape 收缩。mtmi 的 INT8 resize 有个隐蔽权衡：README:60 为让 TRT 选到更好 DLA kernel 而**手动改分割头 I/O scale**，以精度微损换 kernel 质量——异构部署里量化参数可以反向迁就硬件，这是常被忽略的自由度。

## 新人提示

写新 app 请直接以 enqueueV3 为模板（V2 已废弃，保留只为对照）；引擎构建注意十四个时序状态的 min/opt/max 三档 shape（README trtexec 示例 MIN=901/OPT=901/MAX=1150），缺档会在运行时报 shape 越界。uniad.hpp:28 的自引用是 include-guard 保护下的残留，可删但两版都在，复制 V3 目录起步时会一并带走。mtmi 跑通前提是三份校准缓存与三个子网引擎齐备；DLA loadable 与 GPU engine 不可混用上下文，cudla_context.cpp 的互操作绑定顺序是关键，读它先看 destroy 的逆序清理。
