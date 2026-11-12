# 10 · runtime 设备库与 cuda_p2p：生成代码的臂膀与绕 NCCL 的通信

## 1. 角色定位

`runtime/` 下 43 个 .cu 文件是 nvFuser 生成 kernel 的**设备侧标准库**：归约、扫描、cast、复数、低精度支持全在这里。它们不参与 NVRTC 单独编译，而是被 CMake「stringify」成字符串资源头，由 `kernelPreamble`（`compiled_kernel.cpp:99`）整体注入每次生成的源码。同层的 `csrc/multidevice/cuda_p2p.cpp`（1606 行）则是另一类角色：不走 c10d/NCCL，用 CUDA IPC 句柄 + 多播 kernel 原生实现 broadcast/allgather/allreduce——为的是在 CUDA Graph 捕获场景下不被 NCCL 卡住。

## 2. 内部结构

**构建链钉版**：`CMakeLists.txt:1261-1284` 用 `tools/stringify_file.py` 把每个 runtime .cu 转成 `${CMAKE_BINARY_DIR}/include/nvfuser_resources/<名>.h` 字符串字面量，`add_custom_target(nvfuser_rt_<名>)` 挂到 codegen_internal 依赖上；`compiled_kernel.cpp:101-114` 逐个 `ss << nvfuser_resources::*_cu`。

**casts.cu（1192 行）宏工厂**：四族宏批量生成类型转换——`DEFINE_CAST_VECN_WITH_VEC2`（`casts.cu:12`）成对处理元素（half 吞吐关键，注释 L9-10 说明 clang-format 与 `_Pragma("unroll")` 的冲突）、`DEFINE_CAST_NAIVE_VECN`（34）、`DEFINE_CAST_NAIVE_VECN_FROM_TEMPLATE`（50）、`DEFINE_CAST_VECN_WITH_VEC4`（12 处实例）。实例化计数：NAIVE 39 + FROM_TEMPLATE 27 + VEC2 12 + VEC4 3 = **81 处宏展开**，外加标量底座 `__to_float`（60）与 `__half2float`（318）等。**tree-sitter 对这套宏前缀定义完全失明**——图谱里 casts.cu 只有手扫的 file 节点，81 个真实设备函数全部藏在宏里。

**fused_reduction.cu（1797 行，最大单文件）**：`namespace fused_reduction`（8）内是模板元编程三级塔——`FuncSelector`（14/30 递归特化）、`FuncForEach`（43/68）、`TupleReduce` 一二三元特化（121/141/162），底座 `BlockReduceEach`（201 与 340 的偏特化）支撑多输出归约；585 行注释标出 grouped grid welford + fused reduction 的用户可见入口。规模梯队的其余成员：complex_number 1344、grid_reduction 1067、tuple 1047、fused_welford_impl 794、helpers 636。**.cu 全盲钉版**：tree-sitter 对 43 个 .cu 零提取，图谱 43 个 file 节点 + 18 个 function 节点全部为批阶段手扫补齐。

**cuda_p2p.cpp 三类入口**：协议枚举 `P2pProtocol{Get,Put}`（`cuda_p2p.h:18`）与 `P2pTransport{CopyEngine,Tma}`（`cuda_p2p.h:25`）；kernel 侧 `launchMulticastReduceKernel`（65）、`launchAlltoallvKernel`（91）、`launchMulticastKernel`（242——用 NVRTC 现场编译 `multicast.cu`，254-255；Multimem 协议要求新架构，271；目的/源指针与 size 都必须 16 字节对齐，353-361）、`launchTmaCopy`（420）。集合通信全部拆成 post/wait 两段：`postBroadcastWithCudaBackend`（518）/`waitBroadcast`（645）、Allgather（664/801）、Allreduce（828/923）、Reduce（951/1047）、点对点 recv/send Post/Wait（1217/1253/1270/1305）、`postWithCudaBackend`（1322）/`waitWithCudaBackend`（1384）、alltoallv（1559）与屏障（1601）。同步靠信号量状态机：`WriteValue32ToLocalAndPeer`（497）把 IpcSemaphore 的 kIdle/kInProgress **同时写本地与对端**（493-511），IPC 句柄由 `P2pIpcHandle`（`multidevice/ipc_handle.h:66`）封装。

## 3. 外部连接

上游消费方就是生成代码本身：codegen 产出的 `reduce/blockReduce/gridReduce` 等符号都在这些文件里定义；stringify 头由 `codegen_internal` 目标聚合（`CMakeLists.txt:1273-1274`）。cuda_p2p 上接 `SymMemForBroadcast/SymMemForAllgather`（symmetric_memory 层）与 `Communicator::getInstance()`（524），与走 c10d 的 `communication.cpp` 并存为两条可选路径；单测可用 `csrc/multidevice/c10d_mock.h` 的最小假后端在单进程里验证通信逻辑。

## 4. 数据流

runtime/*.cu →（configure/build 时 stringify）→ nvfuser_resources/*.h → kernelPreamble 注入 → 与生成体一起进 NVRTC。通信路径：调用方给 SymMem 句柄 → post 阶段写数据 + 信号量置 kInProgress（对端可见）→ wait 阶段自旋等对端 kIdle → 数据落 multicast/unicast buffer。

## 5. 设计决策

cast 宏工厂用预处理换类型矩阵的免维护——新增 dtype 只补一行宏实例化；VEC2/VEC4 成对变体是 half/bf16 吞吐的实测产物。集合通信 post/wait 拆分与信号量双写，本质是**把 NCCL 的内部状态机外置成显式两阶段 API**，从而可被 CUDA Graph 一次性捕获（launch 时不含隐式同步）。Multicast 与 BatchMemcpy 双协议（560-577 分支）留了硬件代际逃生门。

## 6. 新人提示

- 新增数据类型：除了 csrc 侧 DataType，`casts.cu` 必须补对应宏实例化，否则生成代码链接失败（NVRTC 报 undefined）。
- 改 runtime/*.cu 后 stringify 头只在构建时刷新（`CMakeLists.txt:1280-1284` 有 configure 期预生成），排查"改了没生效"先删 build/include/nvfuser_resources。
- cuda_p2p 的 16 字节对齐断言（353-361）在输入 tensor 切片不齐时最常触发。
- 图谱中 runtime/ 的 function 节点只覆盖 18 个最关键入口（alltoallv/argsort/array 等），宏工厂与模板深处的函数以 file 节点 summary 为准——这是 .cu 盲区的诚实标注。
