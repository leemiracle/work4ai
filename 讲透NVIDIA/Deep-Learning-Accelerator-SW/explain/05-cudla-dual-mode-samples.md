# 05 · cuDLA 双模式样例：CUDA 协同与 NvSci 独立的两条 DLA 编程路线

> 文件：`samples/cuDLA/cuDLALayerwiseStatsHybrid/main.cu`（888 行）与 `cuDLALayerwiseStatsStandalone/main.cpp`（1338 行）
> 图谱层：L10 | tour 步：T14/T15

## 角色定位

两个样例做同一件事：加载 DLA loadable、逐层 submit、把每层起止毫秒写成 CSV——DLA 逐层 profiling 的标准工具。但它们的**内存与同步模型**完全不同，放在一起读等于上一堂 cuDLA 架构课：Hybrid 把 DLA 融进 CUDA 编程模型（stream/graph 提交），Standalone 完全不碰 CUDA，用 NvSci 走嵌入式原生路线。

## 内部结构

**Hybrid（main.cu:219）**：`cudaFree(0)` 建上下文 → `cudlaCreateDevice(..., CUDLA_CUDA_DLA)`（main.cu:305）→ `cudlaModuleLoadFromMemory` → `cudlaModuleGetAttributes`（main.cu:345）枚举输入/输出/统计张量描述符 → `cudaMalloc`（main.cu:526）分配 + `cudlaMemRegister`（main.cu:601）把 CUDA 指针注册给 DLA → `cudlaSubmitTask(devHandle, &task, 1, stream, 0)`（main.cu:697）带 CUDA stream 提交 → 统计缓冲读回写 CSV。

**Standalone（main.cpp:461）**：`cudlaCreateDevice(..., CUDLA_STANDALONE)`（main.cpp:526）后走 NvSci：`createAndSetAttrList`（main.cpp:384）按张量描述符填 NvSciBufAttrList 键值对 → `NvSciBufAttrListReconcile`（main.cpp:786）协调 CPU/DLA 双方约束 → `NvSciBufObjAlloc`（main.cpp:905）分配 → `NvSciSyncCpuWaitContextAlloc`（main.cpp:1053）建 CPU 等待上下文 → `cudlaSubmitTask(..., NULL, 0)`（main.cpp:1183）不带 stream，靠 NvSciSyncFence 信号量同步。公共件：两个 `printTensorDesc` 打印张量描述符；超长 `cleanUp`（main.cpp:102-377）逐类型释放句柄。

## 外部连接

构建侧 Hybrid 用 cuda-samples 通用 Makefile 模板；Standalone 的 Makefile `include findnvsci.mk`（132 行 make 片段，遍历候选路径定位 NvSci 头文件与库）。上游 loadable 由 TensorRT 产（`--useDLACore` + `--exportDLAEngine` 或 NvMedia-DLA），README 给出完整命令。

## 数据流

loadable 文件 → buffer → 模块句柄 → 张量描述符驱动缓冲分配（尺寸/对齐/量化字段全来自描述符）→ 逐层 submit → 统计缓冲（statSupport 参数门控）→ CSV（layer_name,start_ms,end_ms）。Hybrid README 的样例输出显示 DLA 层名是 TRT 融合粒度（如 'Conv_219 + BatchNormalization_220+Relu_221+MaxPool_222' 一个条目 0.7ms）。

## 设计决策

- **两模式是 cuDLA 的正式 API 分野**（memory model 文档级概念），不是新旧版本关系：Hybrid 换来 CUDA 生态互操作（graph 捕获、event 计时），Standalone 换来更小依赖面（车载安全栈不引 CUDA）；
- **统计走专用缓冲而非 printf**：DLA 固件把 per-layer 统计写进注册的 outputTaskStatistics 缓冲，host 侧读回——profiling 不扰动执行；
- **失败路径全量 cleanUp**：嵌入式演示代码的资源纪律，main.cpp 的 276 行 cleanUp 是刻意为之。

## 新人提示

对照读时抓三条对照轴：内存（cudaMalloc+MemRegister vs NvSciBuf Reconcile+Alloc）、同步（stream 顺序性 vs fence 显式等待）、提交（第 4/5 参 stream vs NULL）。NvSciBufAttrListReconcile 是"多方约束协商"抽象——CPU 侧要求 CPU 可访问指针，DLA 侧要求对齐/布局，reconcile 求出双方都能接受的分配参数，理解这个"合同"机制后 Standalone 代码就不再神秘。CSV 里的层耗时记得除以你传入的 freqMHz 才是真实毫秒（样例用法 `./cuDLALayerwiseStatsStandalone model.bin 1152 1 out` 中的 1152 即 DLA 频率）。
