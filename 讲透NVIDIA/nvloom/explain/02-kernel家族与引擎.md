# 讲透 nvloom 之二：12 kernel 家族与基准引擎

## 一、角色定位

`library/kernels.cu`（991 行）+ `kernels.cuh`（65 行声明面）与 `library/nvloom.cpp`（1019 行）合起来是 nvloom 的**测量本体**：kernel 家族负责在 device 侧产生真实负载（SM/TMA/组播/CFT 各形态的拷贝、延迟链、校验数据），Benchmark 引擎负责 host 侧的编排（warmup、同步、计时、统计、负载维持）。一条铁律贯穿两者：**测的是 fabric，不是 kernel**——kernel 写法都刻意朴素（直循环搬运），把变量留给互连。tree-sitter 对 .cu 全盲，本仓 12 个 `__global__` kernel 节点全部为批阶段手扫（行号主会话已逐一复核）。

## 二、内部结构

**12 个 `__global__` kernel**（kernels.cu 行号）：

| kernel | 行 | 职责 |
|---|---|---|
| stridingMemcpyKernel | `:64` | SM 拷贝·跨步形态 |
| simpleMemcpyKernel | `:116` | SM 拷贝·朴素形态 |
| memcpyKernelTma | `:300` | TMA（cp.async.bulk）拷贝 |
| cftPutKernel / cftGetKernel / cftPullredKernel | `:517/:562/:605` | CFT put/get/pull-reduce |
| spinKernelDeviceMultistage | `:706` | 非参与 rank 的 SM 负载维持 |
| patternFillKernel / patternCheckKernel | `:747/:812` | 校验数据发生/核对（FillPattern） |
| pointerChaseFillKernel / pointerChaseKernel | `:886/:905` | 延迟测量（指针追逐链） |
| getSmIdsKernel | `:927` | SM 拓扑探测 |

声明面 kernels.cuh 的调度家族 `copyKernel/copyKernelTma/copyKernelMulticast/copyKernelMulticastTma/...` 在 `:30-38`；**CFT 五个声明包在 `#if CUDA_VERSION >= 13030`**（`:39-44`，签名带 `CUlogicalEndpointId`）——CFT 是 CUDA 13.3+ 的编程模型。kernel 底层大量内联 PTX：TMA mbarrier、multimem.ld/st/red、fabric 指令。

**引擎侧（nvloom.cpp）**：`NvLoom::initialize`（`:847`）绑定设备与机架映射；总入口 `doBenchmark`（`:506-553`）→ 核心测量 `doBenchmarkCore`（`:468`）；状态机五态 NOT_STARTED→WARMUP→SYNCHRONIZE→RUNNING→EXTRA_WORK 定义在 `nvloom.h:120-126`（Benchmark 类 `:128`）；warmup 显式标记在 `:569`；**spin-kernel 维持**在 `:312` 调用（开关 `:479`）——只有执行 rank 的 blockingVar 生效，其余 rank 的 SM 全速空转保温。辅助面：`filterCopyType`（`nvloom.h:271`）按系统支持性过滤拷贝类型。

## 三、外部连接

- **向上**：`doBenchmark(std::vector<Copy>)` 静态入口（`nvloom.h:208`）是全部用例的共同终点——内置模板用例（`cli/testcases.cpp:98` 起的 N_squared_pattern 等 12+ 模板类）与 CSV 通道（`cli/csv_testcase.cpp:36` 的 run）最终都调它；
- **向左**：Copy/Latency 描述（`nvloom.h:80-95`）携带分配器 shared_ptr 与 executingMPIrank，引擎据此决定哪个 rank 发 kernel；
- **向下**：cuLaunchKernel 封装调度（NOTES 批记录：kernels.cu 的 kernel 经 nvloom.cpp 调度）；错误路径四级断言 ASSERT/CU_ASSERT/CUDA_ASSERT/NVML_ASSERT（`library/error.h:59/70/86/99`）带 hostname:device 上下文即退，CU 级失败先转储驱动日志（`getCudaLogs`，`error.h:39`）;
- **横向**：输出交给 OutputMatrix（`cli/util.h:40`）四统计聚合，再走 CSV/JSON（`cli/util.cpp:229` printJson）。

## 四、数据流

一次带宽测量（write、SM 形态）的完整时序：

1. **准备**：用例层按 FillPattern 调 patternFillKernel（`:747`）在源缓冲生成可校验伪随机数据；
2. **warmup**：引擎进入 WARMUP 态（`nvloom.h:121`）先跑若干轮不计分——驱动/JIT/时钟爬升都被吸收；
3. **保温**：非执行 rank 的 spinKernelDeviceMultistage（`:706`）持续烧 SM（`nvloom.cpp:312`），防 GPU 空闲降频改变 fabric 状态；
4. **同步**：SYNCHRONIZE 态做 MPI 屏障 + 流同步，全体 rank 对齐到同一起跑线；
5. **测量**：RUNNING 态执行 rank 循环提交 simpleMemcpy/stridingMemcpy（`:116/:64`，loopCount 参数内化重复），TMA 形态则 memcpyKernelTma（`:300`）以 mbarrier 管理异步块搬运，组播形态一条 multimem.st 同时写多卡（对应 enums.h `:29-35` 的四种组播 CopyType），CFT 形态走 cftPut/cftGet（`:517/:562`）面向 logical endpoint；
6. **计时归一**：按 repeat 或 duration 模式（CLI `shouldContinue`，`cli/nvloom_cli.cpp:45-63`，rank0 决策 MPI_Bcast `:56-58`）收尾，字节量/时间→带宽；
7. **校验**：patternCheckKernel（`:812`）核对目的缓冲——组播 RED_SINGLE/RED_ALL 共用 kernel 但校验算法不同（`enums.h:31-34` 注释）；延迟模式则 pointerChase（`:905`）沿链追逐取往返时间。

## 五、设计决策

1. **朴素 kernel + 显式保温**：把 kernel 从性能方程里约掉，同时用 spin kernel 把"空闲 GPU 状态漂移"显式固定——fabric 测量的两个最大噪声源都被制度化管理；
2. **校验内建**：带宽数字自带正确性背书（fill/check 配对），这在 fabric 工具里并不常见，排查"高带宽但数据坏了"类问题（链路降宽、映射错误）时极其省事；
3. **CFT 条件编译**（`kernels.cuh:39`）而非运行时探测：CFT 类型签名（CUlogicalEndpointId）依赖 13.3+ 头文件，编译期裁剪比运行时分支干净，代价是旧工具链二进制天然缺 CFT 能力；
4. **错误即退**：四级断言宏打印上下文后直接 exit——测试工具宁死不出错报数字；CU_ASSERT 附带驱动日志转储把"为什么挂"留在现场；
5. **静态入口 + Copy 列表**：doBenchmark 接整个测量组而非单条，MPI 集体操作（裁决/归约）按组摊薄。

## 六、新人提示

- 先读 `kernels.cuh`（65 行）再看 .cu——声明面就是 kernel 能力清单；
- 第一个精读 stridingMemcpyKernel（`:64`，模板函数）：totalThreadCount/loopCount/dst/src 四参数就是全部协议，其余 kernel 都是它的变奏；
- 改 kernel 记住铁律"测 fabric 不测 kernel"：任何"优化"kernel 写法都在污染测量目标；
- 调试顺序：CU_ASSERT 挂了先看转储的驱动日志（`error.h:76-89` 的 getCudaLogs 路径），再查映射（分配器侧），最后才怀疑 kernel；
- spin kernel（`:706`）的两段 latch 参数容易误读——它是 multistage 状态机，读 `nvloom.cpp:312` 的调用点理解 blockingVar 语义比读 kernel 本体快。
