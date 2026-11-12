# LPLB/csrc/plugin.cpp 精讲——JIT 编译链路与三个 CUDA 入口

> 原文件：`LPLB/csrc/plugin.cpp`（679 行，pybind11 扩展）

## 一、角色定位

plugin.cpp 是 LPLB 的 C++ 骨架，把 `compiled_solver` 结构体暴露为 Python 的 `lplb._cpp.CompiledSolver`。它做三件事：**运行时 JIT**（读入 minilp.cu 模板，按当前 GPU 架构与拓扑宏 NVRTC 编译 + nvJitLink LTO 链接出 cubin）、**通信初始化**（NVSHMEM + CUDA IPC 两级 workload 缓冲）、**三个执行入口**（solve / count_idx / map_idx 的 kernel 发射）。设计上它是"参数特化代码 + 内容寻址缓存"的教科书样本。

## 二、内部结构

- **防御性开头**：`#undef __CUDA_NO_HALF_CONVERSIONS__` 等四连——torch extension 头会禁用半精度运算符，而 JIT 的 mathdx 代码需要它们。
- **错误宏三件套**：NVRTC_CHECK / CUDA_CHECK / NVJITLINK_CHECK（后者还把 nvJitLink 的错误日志读出来拼进异常）。
- **`vector_string_hash`**：把 kernel 名 + 源码 + 全部编译选项逐项混进一个 size_t（经典 `0x9e3779b9` seed 组合）。
- **`compiled_solver` 字段**：三个 `cudaKernel_t` 句柄 + `cudaLibrary_t`；拓扑参数；`smem_size = -1`（prepare 时由 kernel 自己报）；NVSHMEM 双层缓冲——节点间 `workload_buf/sig_internode`（nvshmem 分配）与节点内 `workload_buf/sig_intranode`（cudaMalloc + IPC 互通的指针数组）。
- **`compile_cubin`**：探测 `prop.major*10+minor` → 读 `resources/csrc-tmpl/minilp.cu` 源码 → nvrtcCreateProgram → 编译选项（`-dlto`、mathdx include、`-DGROUP_SIZE=...` `-DDUP_PER_RANK=...` `-DSM_Ver=...` `-DBLOCK_DIM=...`、条件 `-DUSE_NVSHMEM`）→ 算内容哈希查缓存（`cubin/cu/options` 三文件齐全且逐字节相等才命中，防哈希碰撞）→ 未命中则 nvrtcCompileProgram → 取 LTO IR → nvJitLink 链接（离线 `libcusolverdx.fatbin` + 可选 `libnvshmem_device.a` + 在线 LTO IR）→ 写 `tmp/名字_哈希_主机名_pid` 临时目录 → `rename` 原子发布进共享缓存（`LPLB_CACHE_PATH` 可重定向）。
- **`prepare_module`**：`cudaLibraryLoadFromFile` → `cudaLibraryGetKernel` 取 kernel_solve/map_idx/count_idx/get_solve_smem_size → **launch 一次 get_solve_smem_size**（用 zero-copy 主机映射指针把 `sizeof(smem_variables)` 报回来）→ `cudaKernelSetAttributeForDevice` 放开动态共享内存上限。
- **`init_comm`**：可选 `nvshmemx_init_attr` 自初始化 → `sync_current_to_module` 三连（dlopen 宿主 DeepEP 的 .so，dlsym 设备全局符号，`cudaMemcpy` 设备到设备把 `nvshmemi_device_state_d` 等状态拷进 JIT module）→ 推断 n_nodes/node_size → 分配节点间缓冲（`nvshmem_align`/`nvshmem_calloc`）→ 节点内 `cudaIpcGetMemHandle` + `pg->_allgather_base` 互换句柄 + `cudaIpcOpenMemHandle` 互开。
- **三个入口**：solve（大量张量断言后 `cudaLaunchCooperativeKernel`；NVSHMEM 生效时换 `nvshmemx_collective_launch`）；count_idx（cooperative launch，smem = `(16+n_experts)*sizeof(int)`）；map_idx（普通 `cudaLaunchKernel`，smem = `5*n_logical_experts*sizeof(int)`）。析构逆序清理（关 IPC 句柄 → barrier → nvshmem_free）。

## 三、外部连接

setup.py 把它编成 `lplb._cpp`（探测到 deep_ep_cpp 就加 USE_NVSHMEM 宏与 NVSHMEM 头/库路径）。编译输入 `lplb/resources/csrc-tmpl/minilp.cu` 是**运行时读的文件**（改它不用重编 C++）；mathdx 头与离线 fatbin 由 download-mathdx.sh 下到 resources/mathdx/。`deepep_rt_slim.h` 是 DeepEP 运行时最小声明（借它的 NVSHMEM team 与 `nvshmemi_*` 设备符号）。上层唯一调用方是 planner.py。

## 四、数据流

构造流：`Planner.__init__` → `_get_solver`（lru_cache）→ `compiled_solver(resource_path, n_group, group_size, dup_per_rank, 256, ...)` → compile_cubin（首进程秒级编译，其余进程读缓存打印 "Using cached kernel"）→ prepare_module。

solve 流：Python 侧 workload(int32, [n_group, group_size, n_local_logical]) / r2o / phy2log / avail_num → 指针打包进 `void* args[]`（NVSHMEM 时再追加双层缓冲指针与 team）→ cooperative launch，grid = n_group 个 block、block = 256 线程、smem = kernel 自报的尺寸 → 返回 `result(float32, [n_group, group_size, dup_per_rank])` + `global_workload`。count_idx 返回 `(末行求和, 全矩阵 [n_sms, n_experts])`——全矩阵留给 map_idx 当前缀。map_idx 拿 idx + o_weight + 前缀矩阵 + o2r + phy2log，原地映射出物理索引。

## 五、设计决策

- **为什么 NVRTC 而非 AOT**：GROUP_SIZE/DUP_PER_RANK 是部署期参数，共享内存数组尺寸必须编译期定死；LTO 让 cuSolverDx 的模板化线性代数与 minilp.cu 跨模块内联——这是选 `-dlto + relocatable-device-code` 组合的原因。
- **内容寻址 + 原子发布的缓存**：哈希覆盖源码与全部选项，命中后再逐字节比对源码、逐行比对选项（双重防碰撞）；临时目录带 hostname+pid，`rename` 进共享目录天然无锁，多进程并发编译也安全。
- **两级 allreduce 通信**：节点间走 NVSHMEM `putmem_signal_nbi`（IBGDA 单线程发环），节点内走 CUDA IPC + `cuda::atomic` 信号量——全部发生在 kernel 内部，不出 GPU；cooperative launch 是 `this_grid().sync()` 的硬要求。
- **sync_current_to_module**：JIT 出的 module 与宿主 .so 各有一份 NVSHMEM 设备态，直接把宿主已初始化的符号按地址拷进 module，避免二次 init 带来的 team 撕裂——非常规但极有效的手法。

## 六、新人提示

改 minilp.cu 后缓存按内容自动失效，不必手动清。编译失败看异常里的 NVRTC log 全文。smem 预算：GROUP_SIZE=8/DUP=2 时结构体已不小，Hopper 动态共享上限 227KB，加大拓扑先心算 `sizeof(smem_variables)`。USE_NVSHMEM 是编译期二态：没链 DeepEP 时 `init_comm` 不存在于绑定里，Python 侧调它会 AttributeError——这通常不是 bug 而是构建配置。
