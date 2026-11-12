# 01 编译线：从 .cu 到 SASS

> 《NVIDIA 全栈深讲系列》第 01 篇。行号锚全部现场核实自本地源码 `/usr-data/data2/repos/agent-repos/NVIDIA/`；口径：源码优先于 deepwiki。

## 1. 第一性原理设问：为什么必须有中间那一层

根源矛盾：**GPU 指令集两年一换，而二进制要跑在还没造出来的芯片上。** SASS（真实机器码）不是稳定契约——SM80/90/100 互不兼容、无公开规范；分发场景（wheel、游戏、集群滚动升级）却要求一份产物跑遍已有与未有的硬件。直接编到 SASS 只有死路：每 arch 各编一份（未来 arch 天然缺位），或用户机上重编（用户机上没有也不该有编译器）。

唯一解：编译目标拆两级——编译期瞄准稳定**虚拟架构**（`compute_XX`，产物 PTX），装载期由驱动内置 JIT 降到**真实架构**（`sm_XX`，产物 cubin/SASS）。PTX 由此成为契约层：上层语言、下层硬件随便换，只经"PTX 指令集 + 装载 ABI"耦合。fatbin 自然推出：容器装若干已知 arch 的 cubin（免 JIT、吃满代际特性）加一份兜底 PTX（未来 arch 现场编译）；`-gencode arch=compute_90,code=[sm_90,compute_90]` 即"一份 90 的 SASS 快件 + 一份 90 的 PTX 图纸"。经济结构同层定型：PTX 之上全开放（cuda-tile/numba/cuda-rust 为证），ptxas 之下全封闭（调度与寄存器分配是护城河）。

2024-2026 出现 tile 抽象（cuda-tile、TileLang 类 DSL）是第二个必然性：**内存墙**。HBM 带宽每代涨约 1.5-2×（A100 ~2 TB/s → H100 3.35 → B200 8），tensor 算力涨得快得多（FP16 dense：312 → ~990 TFLOPS，B200 FP4 dense ~4.5 PFLOPS）。峰值所需算术强度 = FLOPS÷带宽：A100(FP16) 约 150 FLOP/B、H100 约 300、B200(FP4) 约 560——**搬一字节要榨几百次运算**。128×128 FP16 tile 的 GEMM 一箱数据只摊出约 64 FLOP/B，还得靠更大 tile、双缓冲、寄存器分片再叠。结构解只有一个：数据进片上（shared memory/寄存器）反复复用，即 tile。手工管 tile（`__shared__`、bank conflict、async copy、每代重学）心智负担极重——tile 遂升格为语言抽象：load/store/mma 以 tile 为单位，**数据搬运成为一等公民语句**，调度交给编译器。

本篇看三层流水线（前端 → PTX → SASS）在各入口语言里分别怎么走，以及 2026 年它正在怎么变。

## 2. 直觉层：三个比喻

**分层**：PTX 之于 SASS，像 JVM bytecode 之于 x86 机器码。fatbin 是集装箱——几个主流市场的成品（cubin）加一张通用图纸（PTX）；驱动里住着微型工厂（JIT），遇图纸现场造一台，成品存 `~/.nv/ComputeCache` 下次直取。

**tile**：SM 是厨房。HBM 是城外仓库，L2 是门店货架，shared memory 是备菜台，寄存器是手里食材。算力十年翻几十倍，进城的路只宽几倍——瓶颈从"切菜"变成"物流"。传统 CUDA 让厨师手写物流单（指针算术 + `__syncthreads`）；tile DSL 把物流升格为标准集装箱（`tile<8x4xf32>`），"运一箱、腌一箱、炒一箱"成为显式动词。

**三层**：前端说人话，PTX 说"硬件听得懂但不绑定硬件"的话，SASS 管这一颗芯片的时序流水。越往下越贴近硅、越无通用性、越无文档——所以调试工具必须每层留观察窗（§4）。

## 3. 机制层：五条入口路径的真实流水线

### 3.0 经典 nvcc 线（基线）

`.cu` → EDG 前端 + cicc → NVVM（LLVM 系组件）→ PTX → ptxas → cubin → fatbin。关键不是工具名，而是**虚拟/真实 arch 的分离贯穿一切 API**：`-arch=compute_90` 只产 PTX，`-arch=sm_90` 产 cubin，驱动收到 PTX 即现场 JIT。下面五条路径都在此骨架上换前端/装载策略。

### 3.1 C++ 运行时 JIT：jitify——把编译器搬进进程

模板 kernel 连源码带进运行时，首次调用 NVRTC 编出 PTX（`jitify/jitify.hpp:2811` `nvrtcGetPTX`），随后两条装载路：

- 无链接文件：`cuModuleLoadDataEx(&_module, _ptx.c_str(), ...)`（`jitify.hpp:1143`）——**驱动内嵌编译器**把 PTX 直接降到当前卡的 SASS；
- 有链接文件：`cuLinkAddData(_link_state, CU_JIT_INPUT_PTX, ...)`（`jitify.hpp:1150`）→ `cuLinkComplete`（`:1187`，产出 cubin）→ `cuModuleLoadData(&_module, cubin)`（`:1189`）。

注意驱动 linker 收 PTX/cubin/LTOIR/object 多种输入——JIT 不止是 arch 适配，还是**装载期链接优化**的机会（MatX 用到极致，见 3.6）。

### 3.2 Python 直通一代：numba-cuda（LLVM→libnvvm 路线）

Python 字节码 → Numba IR → llvmlite 出 LLVM IR → **libnvvm** → PTX → 驱动 linker → cubin。主路径在 `numba-cuda/numba_cuda/numba/cuda/` 下（下同）：

- `cudadrv/nvvm.py:544` `compile_ir()`：LLVM IR 装入 NVVM CompilationUnit，verify 后 lazy 链入 libdevice（bitcode 形式的数学库），`cu.compile()` 内调 `_nvvm.compile_program`（`nvvm.py:247`，C API 边界）产出 PTX；
- 目标 arch 在 `compiler.py:1273` 取 `get_current_device().compute_capability`——永远瞄准**当前卡的虚拟 arch**，PTX→SASS 留给驱动；
- 收尾 `cudadrv/driver.py:2474` `self.linker.link("cubin")`：驱动 linker 把 PTX（可混入 LTOIR/静态库）链成 cubin；
- 版本锁之疼：llvmlite 与 libnvvm 的 LLVM 不同步，`nvvm.py:576` `llvm150_to_70_ir()` 干脆用正则把 LLVM 15 的 IR 文本"降级"成 LLVM 7 能吃的样子——两套 LLVM 世界的过桥税，也是 3.3 存在的理由。

### 3.3 Python 直通二代：numba-cuda-mlir（MLIR 路线的意义）

Numba IR → MLIR（arith/memref/scf/gpu dialect）→ `convert-gpu-to-nvvm` 等降级 pass → llvm dialect → LLVM IR → libnvvm → PTX/LTOIR（deepwiki 2.3/2.4 页）。值得重造中端的原因：

- **结构保留**：shared memory 是 `memref` + `memory_space=3`，循环是 scf.for 结构化区域——这些信息进 LLVM IR 就被拍平成指针与 branch；tiling/向量化/pipelining pass 在结构化层级写一次、处处复用。IR 层级本身成了编译资产，与 cuda-tile（3.5）互为镜像；
- 它同样被迫分叉：sm_100+ 走新版 LLVM IR 直译，更老的卡要把 IR 降回 LLVM 7 形态喂老 libnvvm——契约层（libnvvm 认的 IR 版本）落后于前端演进，是三层架构的真实税单。

### 3.4 Rust 直通：cuda-oxide（rustc 后端 → LLVM NVPTX 路线）

cuda-rust 工作区的 cuda-oxide 是 **rustc codegen 后端**：Rust → MIR → Pliron（Rust 写的 MLIR 式 IR）→ LLVM IR → `llc -march=nvptx64 -mcpu=<target>`（`cuda-rust/cuda-oxide/crates/cuda-oxide-codegen/src/ptx.rs:332-334`）→ PTX → ptxas → SASS；host/device 同 crate，一次 `cargo oxide build` 单源编译。

本篇最重要的"契约渗漏"实证也在这里：`ptx.rs:321` `DISABLE_BRANCH_FOLD = "-disable-branch-fold"`——注释记录上游 LLVM 23 分支折叠把循环尾布局改成 ptxas 展开启发式不认的形状，寄存器 38→26、FFMA 18→4，RTX 5090 实测 sgemm 7218→5708 GFLOPS（**-26%**），只能禁掉 LLVM 两个后端 pass 保住 ptxas。PTX 名义中立，**实际质量取决于 ptxas 启发式对 PTX 形状的偏好**——开放/封闭边界两侧互相渗漏语义。

### 3.5 tile 抽象：cuda-tile——把搬运升为一等公民

MLIR dialect + 字节码 + 驱动装载的完整闭环（TableGen 定义在 `cuda-tile/include/cuda_tile/Dialect/CudaTile/IR/`，下同）：

- **类型**：`Types.td:136` `CudaTile_TileType`——shape **必须全静态、只支持 2 的幂**（描述原文），因为形状要在编译期映射到寄存器/shared memory 布局；
- **搬运动词**：`Ops.td:2780` `load_view_tko`、`:4804` `store_view_tko`、`:3284` `make_tensor_view`（裸指针升格为带 shape/stride 的视图）、`:5198` `make_partition_view`（把全局矩阵切成 tile 网格）；
- **计算动词**：`Ops.td:1497` `mmaf`（另有 13.3 的 `mmaf_scaled` 与整数 `mmai`）、`:2155` `fma`、`:265` `alloca`（13.3 自动内存分配）；连 PDL 都是显式 op——`:5666` `CudaTile_GdcWaitTkoOp`（`gdc_wait_tko`，等前驱 kernel 完成）；
- `load_view_tko` 带 `inbounds` 属性（该 op 描述节）——**内存安全信息从运行时检查升格为 IR 属性**；
- **装载**：`cuda-tile/README.md:330-333`——`cuda-tile-translate` 把 .mlir 编成 `.tilebc` 字节码；AOT 用 `tileiras --gpu-name sm_100 example.tilebc -o example.cubin`；JIT 时把 `cuModuleLoad` 的参数直接换成 .tilebc，**驱动吃 Tile IR 字节码现场编译**（需 CUDA 13.1+ 驱动）。

这是 2026 年最大的架构信号：驱动 JIT 入口正从 PTX 上移到更高层 IR——契约层本身在换代；tile 级信息（静态形状、inbounds、显式 wait）让编译器能做的远多于对着平铺 PTX 逆推。

### 3.6 算法层不是编译层，但决定"什么被编译"：cccl 与 MatX

cccl（CUB/Thrust/libcudacxx）不碰编译器，是"模板实例化工厂"：`cccl/cub/cub/device/dispatch/tuning/tuning_reduce.cuh:416` 的 `chained_policy<500, ...>` 从 GTX Titan 时代调参链一路链到 `:196` `sm100_tuning`（Blackwell 专用，按 accumulator 类型/位宽特化 threads_per_block/items_per_thread/vec_load，注释全是实测加速比，如 int8 reduce 1.417×）。运行时按 compute capability 选档，选中模板参数决定**哪个 kernel 被实例化编译**——模板元编程当 autotuner。仓内 `nvrtcc/` 工具沿用 nvcc 轨迹、把 PTX 换成 NVRTC 现编——侧面证明 PTX 是可替换互换层。

MatX 运行时生成 kernel 源码交 NVRTC：`MatX/include/matx/core/nvrtc_helper.h:915` `nvrtcCompileProgram`；LTO 路线把 LTOIR（LLVM bitcode）用 nvJitLink 链成 cubin——`:996`/`:1000` `nvJitLinkAddData(NVJITLINK_INPUT_LTOIR)`、`:1001` `nvJitLinkComplete`、`:1006` GetLinkedCubin，`:1017` `cuModuleLoadDataEx` 装载——跨模块在 JIT 链接期内联，正是"懒表达式→融合 kernel"的编译期落点。

## 4. 程序员实操：每层都留了观察窗

1. **看产物**：`cuobjdump -sass` / `-ptx` / `nvdisasm`；fatbin 黑盒先 `--list-elf --list-ptx` 看装了哪些 arch——排查"wheel 在新卡上 JIT 失败"第一步。numba 侧 `inspect_asm()/inspect_llvm()/inspect_ptx()`。
2. **编全 arch**：发库必带 PTX 兜底 `-gencode arch=compute_100,code=[sm_100,compute_100]`；只编 `sm_100` 的产物到下一代卡既无 cubin 又无图纸，首启即败。
3. **JIT 运维**：首启延迟来自驱动 JIT（大 kernel 秒级）；`CUDA_CACHE_PATH`/`CUDA_CACHE_MAXSIZE` 控缓存，驱动大版本升级即失效；服务化要么 AOT 要么预热。
4. **调试接线**：`-G`（device debug）砍优化，只在真单步变量时用；`-lineinfo` 保优化 + 行号映射，是 cuda-gdb 定位与 ncu 归因的日常档——numba 同款分离就在 `compiler.py:1259-1260`（`debug`/`lineinfo` 两参数）。工具分工：语义错 → PTX 对照源码；性能错 → SASS 看调度/寄存器（cuda-gdb `disassemble`、Nsight Compute）；访存错 → compute-sanitizer（memcheck/racecheck/initcheck）抓运行时越界与竞争。cuda-gdb = GDB + CUDA 扩展，断点可下源码/PTX/SASS 三级，`info cuda` 按 warp/lane 视角观察。

## 5. 批判边界：坑与适用边界

- **PTX 是 ABI 契约，不是性能契约**：3.4 的 -26% 实证；只能用 `__launch_bounds__`/`-maxrregcount` 间接收买 ptxas，改不了它。
- **JIT 三税**：首启延迟、缓存随驱动升级失效、云端每台冷启机各交一遍——按秒计费的租赁下是真金白银。
- **fatbin 膨胀**：arch 列得越全产物越大（每份 SASS 都是真二进制）。
- **tile 静态性是硬边界**：形状全静态 + 2 的幂（Types.td 明文），动态 shape/尾块回落传统 CUDA；cuda-tile 对齐 CUDA 13.1 且按小版本演进（ops 已标 13.3/13.4），生产采用要盯版本。
- **双 LLVM 世界税**：numba 正则降级 IR、numba-cuda-mlir 维护 LLVM 7 翻译器、cuda-oxide 硬扛上游变化——三条路径都在为"前端 LLVM 与 NVIDIA 组件 LLVM 版本不同步"付租。
- **算法层调参是实证资产非原理**：cccl 的 1.4× 来自 benchmark 硬扫（连"int16 以外刻意不调"的负结果都注释在案），换 workload 未必成立。
- **JIT 库缓存工程占半条命**：jitify 的 JitCache、MatX 的 JITLaunchParamsCache 都在把编译成本摊成零——选型先问负载命中缓存吗。

## 6. 费曼检验

**自测题**（不看书能答出才算懂）：

1. 一个 wheel 里只有 `sm_90` 的 cubin、没有 PTX：H100 上能跑吗？B200 上呢？——H100 能（同代直接装载）；B200 不能（cubin 不跨代，又没有 PTX 图纸给驱动 JIT）。
2. numba 已有 llvmlite 的 LLVM IR，为什么必须绕 libnvvm 而不用上游 NVPTX 直产 PTX？——kernel 约定（NVVM 元数据）、libdevice 挂接、专有 intrinsic 都长在 libnvvm 那套 LLVM 分支上；cuda-oxide 反证：走上游可以，但要自补整条 kernel 元数据链并独面 ptxas 兼容性。
3. cuda-oxide 为什么给 llc 加 `-disable-branch-fold` 还写成常量？暴露 PTX 契约什么性质？——LLVM 23 分支折叠改变 PTX 形状，毁掉 ptxas 展开启发式（-26% 吞吐）；PTX 只保语义等价不保生成质量——契约是 ABI 级的，不是性能级的。

**一句话总结**：编译线 = 用一个稳定契约（PTX，如今又多了 Tile IR 字节码）把"前端语言百花齐放"与"硬件两年一代"解耦；tile 抽象是把内存墙的搬运压力从程序员手上挪给编译器的最新一轮解耦。

---

## 勘误（deepwiki vs 本地源码）

- 行号锚全以本地源码为准（cuda-tile@5b3fa4c 2026-09-26 等），未发现 deepwiki 与源码的实质矛盾。
- deepwiki cuda-tile 9.1 页"`.tilebc` 经 cuModuleLoad 由驱动自动编译"——已由 `cuda-tile/README.md:330-333` 原文证实（需 CUDA 13.1+）。
- numba-cuda-mlir 无本地克隆，其"sm_100+ 直译 / LLVM 7 降级"双路径（deepwiki 2.4 页）**未能源码核实**，采信 deepwiki 并标注。
- cuda-gdb deepwiki 呈现的是 GDB 通用组件（DWARF/BFD/GAS/simulator），无 CUDA 扩展专页；本篇对该仓仅按通用定位描述、未引行号。
