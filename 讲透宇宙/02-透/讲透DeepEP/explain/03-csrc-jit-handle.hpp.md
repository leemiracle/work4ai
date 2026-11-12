# 精讲：csrc/jit/handle.hpp —— JIT 内核的加载与发射胶水

> 原文件：`csrc/jit/handle.hpp`（DeepEP，166 行，命名空间 `deep_ep::jit`）

## 一、角色定位

DeepEP V2 的设备内核（dispatch/combine/engram 等）是**运行时按形状 JIT 编译的 cubin**，本文件负责编译产物与 GPU 执行之间的最后一公里：加载 cubin 拿内核句柄、构造 launch 配置、以变参方式发射内核。它对应图谱 tour 第 4 步"内核运行时：加载与泛型启动"，是 `csrc/jit/api.hpp`（`init_jit` 注册）→ `compiler.hpp`（产出 cubin）→ 本文件（装载执行）链条的末端。文件小但处处是 CUDA 版本地雷，读它等于读一份"driver API vs runtime API"实战对照。

## 二、内部结构

- **`get_kernel_arg_ptr<arg_t>`**：小而关键——参数类型派生自 `NoRefPtr` 时直接取 `arg.ptr`（把"无意义的占位对象"退化为裸指针传给内核），否则取地址，统一进 `void*` 数组。
- **双后端条件编译**（`#if CUDART_VERSION >= 12080 and defined(EP_JIT_USE_RUNTIME_API)`）：类型别名整套切换——runtime 路径用 `cudaLibrary_t/cudaKernel_t/cudaLaunchConfig_t/cudaLaunchAttribute`，driver 路径用 `CUmodule/CUfunction/CUlaunchConfig/CUlaunchAttribute`。
- **`load_kernel(cubin_path, func_name)`**：runtime 路径 `cudaLibraryLoadFromFile` → **`nvshmemx_culibrary_init`** → `cudaLibraryGetKernel`；driver 路径 `lazy_cuModuleLoad` → `lazy_cuModuleGetFunction`。
- **`construct_launch_config`**：设 max dynamic smem 属性，填 grid/block/smem/stream；driver 路径支持三个 launch attribute（cooperative、cluster 维度、PDL 程序化流序列化），runtime 路径当前只支持 cluster（cooperative/PDL 标 TODO）。
- **`launch_kernel<...>(kernel, config, args...)`**：折叠参数为 `void*` 数组，`cudaLaunchKernelExC` / `lazy_cuLaunchKernelEx` 发射。

## 三、外部连接

依赖 `cuda.h` 与自家 `utils/lazy_driver.hpp`（惰性 driver 符号加载，避免进程早期强制 `cuInit`）、`jit/no_ref.hpp`（占位参数类型）、`common/exception.cuh`（`EP_HOST_ASSERT`）。宏 `EP_CUDA_UNIFIED_CHECK` 随后端映射到 runtime 或 driver 检查宏。调用方是 `jit/kernel_runtime.hpp`（`KernelRuntime` 包装 load/launch 生命周期）与 `kernels/elastic` 下的五组运行时工厂；`unload_library` 在 `KernelRuntime` 析构时调用，容忍 `cudaErrorCudartUnloading`/`CUDA_ERROR_DEINITIALIZED` 的退出期竞态。

## 四、数据流

一次典型发射：①启动期 `init_jit` 完成 `Compiler::prepare_init` 等注入；②首次用到某内核配置时，compiler 产出 `cache/xxx.cubin`；③`load_kernel` 把 cubin 装入 library、（runtime 路径）给 NVSHMEM 注册符号、取出 `KernelHandle`；④每次调用：`construct_launch_config(kernel, stream, smem_size, grid, block, cluster, cooperative, enable_pdl)` 组装配置——注意 smem>0 时先 `cuFuncSetAttribute`/`cudaFuncSetAttribute` 解锁超过 48KB 的动态共享内存；⑤调用点把张量指针、形状等实参直接展开传给 `launch_kernel`，模板折叠成 `void* ptr_args[]` 后发射。

## 五、设计决策

- **默认走 driver API**：runtime 路径虽有 `cudaLibraryLoadFromFile` 的便利，但 cooperative launch 与 PDL 两个发射属性尚未支持（代码里 TODO 注明），生产内核需要它们，故条件编译默认落在 driver 侧。
- **`nvshmemx_culibrary_init` 的存在**：JIT 出的 cubin 若引用 NVSHMEM 设备符号，必须对该 library 单独初始化——这是 V1 NVSHMEM 内核与 JIT 共存时的兼容钩子。
- **`static` 属性存活的坑**：launch attr 必须是 `static`，否则配置结构体持有悬垂指针（注释原话提醒"attr 会被析构"）——C++ 返回聚合内嵌指针的经典陷阱在此显式防御。
- **惰性 driver 包装**：`lazy_cu*` 系列统一走函数指针，进程 fork/派生场景不提前初始化驱动。
- **卸载容错**：退出阶段卸载错误码被断言放行，避免析构顺序问题误报。

## 六、新人提示

改动前先确认目标 CUDA 版本：`CUDART_VERSION >= 12080` 才有 runtime library 加载 API；想启用 runtime 路径需显式定义 `EP_JIT_USE_RUNTIME_API`。排障时若见"invalid argument"类发射失败，优先查三处：smem 属性是否设置、attr 是否因非 static 而悬垂、`void*` 数组里的参数生命周期是否活过发射时刻。新增需要 cluster 的内核时，driver 路径的 `cluster_dim` 参数即可，runtime 路径记得同步补齐。
