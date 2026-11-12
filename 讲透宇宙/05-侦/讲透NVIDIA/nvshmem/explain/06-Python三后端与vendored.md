# 06 Python 三后端与 vendored——nvshmem4py 全栈与 gpunetio 依赖

## 角色定位

nvshmem4py（图谱 L12，151 节点）是 Python 全栈绑定：主机侧 API + 设备侧 API 都可在 Python 里调用，kernel 用 numba/CuTe DSL/Triton 写即可嵌入 NVSHMEM 通信。设备 API 有**三个后端实现**——numba、numba_cuda_mlir（新 MLIR 管线）、CuTe DSL——同一语义三种编译通路。externals/gpunetio（L14，66 节点）是 vendored DOCA GPUNetIO 库，作为 gpunetio 传输插件的地基，也是全仓第三大"代码不是自己的"区域（前两处：vendored pmi-2 与 dlmalloc）。

## 内部结构

bindings 层 `nvshmem4py/nvshmem/bindings/_internal/nvshmem.pyx`（7859 行）用 CyBind/Cython **函数指针表**而非直接 extern 声明——wheel 不硬依赖 libnvshmem 符号，运行时按可选库版本绑定；`nvshmem_linux.pyx` 与它逐字节相同（diff 实证），是平台别名拷贝非独立实现。设备后端三份：numba 的 `core/device/numba/amo.py` 每个原子操作一对函数（裸函数供 JIT 调用 + @overload 实现，atomic_fetch 的 overload 在 numba/amo.py:27、atomic_set 在 numba/amo.py:70、atomic_compare_swap 在 numba/amo.py:117、atomic_swap 在 numba/amo.py:163、atomic_fetch_add 在 numba/amo.py:296 成对展开），numba/collective.py 的 reduce_ol 起于 numba/collective.py:1391、约 490 行的逐 dtype×reduce_op 组合展开模板；`numba_cuda_mlir/amo.py` 与 numba 版逐函数同构（平行实现）；CuTe DSL 后端用 extern 声明直接在 JIT kernel 内调用（`core/device/cute/direct.py:204` 的 fence 是三后端唯一拥有设备级 fence/quiet 的，fence/quiet/signal_op 都在 cute/direct.py:9 的导出表）。core 层 `init_fini.py` 的 DeviceLibLanguage 枚举统一 numba/cute/triton 三语言设备库装载；`core/__init__.py:21` 注释钉版"CuTe DSL Tensor API 与 Torch 命名冲突，不在此引入 cute 模块"；`interop/cute.py` 自实现 DLPack v0.9 协议桥接 cuda.core Buffer 与 CuTe Tensor（interop/cute.py:16 的 _mr_references 注册表保 GC 安全，interop/cute.py:78-84 的 DLPack 探测）。**两枚 LFS 指针**：`bindings/device/numba/_numbast.py`（oid 53ed32a2，3.9MB）与 `numba_cuda_mlir/_numbast.py`（oid a82143e2，4.3MB）——安装期生成的桥接模块，仓里只有指针，分析时勿当源码解读（.gitattributes 钉版 filter=lfs）。

## 外部连接

core/__init__.py 显式注释：CuTe DSL Tensor API 与 torch 命名冲突故不引入 cute 模块；interop 三桥 torch/cupy/cute 走 DLPack。构建：python_libs_wheel/ 是 nvidia-wheel 打包层，nvshmem4py 构建期生成 _numbast.py 再进 LFS。Rust 侧镜像（L13）：contrib/nvshmem4rust 的 generator/generate_rust_bindings.py 从 host_api_surface.py 白名单生成 sys/bindings/api 三层，runtime/src/lib.rs 用 OnceLock+Arc+Weak 管进程单例。gpunetio 侧：high_level.cpp 不走 ibv_create_qp 而手工填 mlx5ifc PRM 命令块自造 GPU 可见 doorbell 的 QP/CQ（doca_gpunetio_high_level.cpp 的 create_qp:302/create_cq:246）；cuda_wrapper dlopen libcuda 仅依赖自带头最小声明；gdrcopy 函数表解耦 ABI 且支持 force_pcie 绕 NVLink。

## 数据流

一次 Python kernel put：用户在 numba @cuda.jit kernel 里调 nvshmem.putmem_nbi → amo.py/rma.py 的 @overload 展开成对 numbast 桥接符号的调用 → numba 编译期把符号 lower 到 NVVM（direct.py 的 @intrinsic 直生 LLVM IR）→ 与 NVSHMEM 设备库 bitcode/LTOIR 链接 → 运行时走 transfer_api 分派（IBGDA 直通或 proxy）。CuTe 后端则由 cute.ffi 声明被 CuTe 编译器 lowers。host 侧 API 经 nvshmem.pyx 的函数指针表进 libnvshmem。

## 设计决策

三后端并存是过渡期现实：numba 成熟、MLIR 是 numba 的继任管线、CuTe DSL 服务 CUTLASS 生态——但 96% 语义同构，改 API 要改三处（numba_cuda_mlir 与 numba 行号级对齐正是维护纪律）。函数指针表换来 wheel 的安装自由度；LFS 藏 4MB 生成物避免仓膨胀；ask_smem.pyx（注释明示 CyBind 生成的 C 声明刻意不含 NVSHMEM 头）与 cynvshmem 双实现服务不同绑定风格。vendored gpunetio 三层 wrapper（sdk/ibv/mlx5dv，每包装 7-9 行 env 开关模板）是对上游 ABI 不稳的防御性隔离。

## 新人提示

装好后先跑 nvshmem4py/examples 的 torch_mempool.py；别读 _numbast.py——它是 LFS 指针，本地未 fetch 时只有 3 行元数据。三个后端选型：一般负载用 numba，追新用 mlir，CUTLASS 流水线用 cute（且只有 cute 有设备 fence/quiet，见 direct.py:204）。贡献代码时 nvshmem.pyx 与 nvshmem_linux.pyx 必须同步改（或改构建让别名生成）。vendored 区改动谨慎：mlx5_ifc.h 两份拷贝（externals 5699 行 vs src/modules 5542 行）已漂移，上游更新时要人工对齐。
