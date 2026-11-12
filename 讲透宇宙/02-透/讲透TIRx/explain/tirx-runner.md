# tirx-runner.md — runner.py：统一运行器与两阶段基准基建

> 源码：`tirx_kernels/runner.py`（885 行，四文件中最长）｜图谱层：`layer:core-registry`｜fan-in 35（全库第二）

## 角色定位

registry 管"有哪些 kernel"，runner 管"**怎么跑**"。它与 registry、`_protocol` 同属注册与运行时核心层，是 kernel 模块执行契约（`run_test` / `run_bench` / `prepare_bench`）的定义者，同时是多进程基准编排（bench_suite）赖以成立的三大工程基建：**进程局部性**、**GPU 绑定诚实性**、**CPU/GPU 两阶段隔离**。fan-in 35 意味着各类别 kernel 模块普遍 import 它的 `bench`/`compile_kernel`/`prepared_gpu_benchmark`——它是仅次于 kern 的第二公共面。

## 内部结构

图谱 contains 边 26 个子节点，源码可归为六簇：

| 簇 | 成员 | 职责 |
|---|---|---|
| 基准桥 | `PreparedBenchmark`(Protocol) / `ExplicitPreparedBenchmark` / `prepared_gpu_benchmark` / `PreparedKernelBenchmark` | kernel 自备的 prepare→GPU 桥，进程局部、禁序列化 |
| 生命周期 | `run_kernel_test` / `run_kernel_bench` / `prepare_kernel_bench` / `run_prepared_kernel_bench` / `close_prepared_kernel_bench` | 正确性与基准的统一入口 |
| 编译 | `compile_kernel` / `compile_executable` / `_materialize_cuda_import(_tree)` / `_offline_cuda_compile_parameters` / `_cuda_compile_mode` | 常规编译 + 离线（不初始化 CUDA 的）CUDA 物化 |
| 三守卫 | `cpu_prepare_compile_scope` / `gpu_stage_compile_guard` / `cuda_initialization_guard` | 证明 CPU prepare 不碰 CUDA、GPU 阶段不编译 |
| GPU 绑定 | `physical_cuda_uuids` / `bind_cuda_assignment` / `validate_current_cuda_assignment` / `_current_process_cuda_uuids` / `current_process_cuda_memory_bytes` | 物理 UUID 级的设备绑定与验证 |
| 中断与 A/B | `defer_gpu_interrupts` / `gpu_interrupt_should_defer` / `ab_current_benchmark_module` / `_apply_ab_benchmark_contract` / `bench` | SIGUSR1 延迟、A/B 双树模块加载、规范计时器 |
| 观测与旋钮 | `current_process_cuda_memory_bytes` / `hardware_num_sms` / `cuda_target` / `cuda_is_initialized` / `set_external_references_enabled` | 显存采样、编译画像参数（env 注入）、CUDA 状态探针 |

`hardware_num_sms` 与 `cuda_target` 是"CPU prepare 不碰 CUDA"原则下的参数逃生口：persistent kernel 需要 SM 数、编译需要 arch，prepare 阶段却不能查询设备，于是用 `TIRX_PREPARE_NUM_SMS`/`TIRX_PREPARE_CUDA_ARCH` 两个环境变量由编排方显式注入（torch 已初始化时也可实测兜底）。`current_process_cuda_memory_bytes` 用 NVML 按 PID 采样各卡显存，bench_suite 靠它区分"本 workload 自有驻留"与"外来残留"，在轮转调度多 workload 时发现泄漏。

## 外部连接

**入边 58 条**：kernel 模块侧（flashinfer/norm、quantization、topk、basic、flashattention 等 30+ 文件 import `bench`/`compile_kernel`）；编排侧（`bench_suite/run.py`、`tirx_kernels/test/__main__.py` 的 `main`）；测试侧三个专属文件（`test_low_level_ir.py`、`test_runner_interrupts.py` 三个中断用例、`test_runner_cuda_compile.py` 三个编译模式用例）。**出边**：无库内模块依赖——只 import tvm 与标准库，对 registry 一律函数内延迟导入，保持自身零循环依赖。

## 数据流

**A/B 双树流**（bench_suite 编排下）：ab.py 给子进程设 `CUDA_VISIBLE_DEVICES` + `PYTHONPATH=before 树` + `TIRX_INTERNAL_AB_CURRENT_BENCHMARK_ROOT=当前 checkout` → 子进程（bench CLI）import 到的 kernel 模块是**旧代码**，但配置解析走 `ab_current_benchmark_module(旧模块)`——从当前树取同名模块的 `CONFIGS`（当前版本是基准配置的唯一权威）→ `prepare_kernel_bench(module=旧模块)` 用旧代码的 `prepare_bench` 产出旧可执行文件 → `_apply_ab_benchmark_contract` 复核（要求 `ExplicitPreparedBenchmark`）。`run_gpu` 始终是旧模块自己的：启动参数打包必须匹配旧可执行文件的 ABI。`ab_current_benchmark_module` 的手术细节：暂存并摘除 `sys.modules` 全部 `tirx_kernels.*`，装一个 `__path__` 指向当前 checkout 的裸 namespace package（避免重跑 `__init__` 副作用），按同名 import 后还原；`bench`/`bench_suite`/`runner`/`basic.utils._runtime` 四前缀的字节级共享实例全程保留（防 tvm 注册类副作用跑两遍），**kern 故意不共享**——两代 DSL 同进程共存，before 模块踩自己年代的基座。

**正确性流**：`python -m tirx_kernels.test --kernel rmsnorm` → registry `discover_kernels(cuda_arch)` → `run_kernel_test(name, cfg, registry)` → 查 `KERNEL_META.reference_requirements` 未满足则 `SkipTest` → 剥掉 label 后 `mod.run_test(**params)`。rmsnorm 的 `run_test` 内部完成 compile→run→flashinfer 对照 `assert_close`——编译、运行、检查由模块自闭环，runner 只做调度与前置检查。

**两阶段基准流**：`run_kernel_bench` → ①`prepare_kernel_bench`（CPU 阶段）：`cuda_initialization_guard` 先证明 CUDA 未初始化、出来后再证明没被动过 → `cpu_prepare_compile_scope` 把 `tvm.compile` 猴补成 `compile_executable` 离线路径 → `load_kernel` → `mod.prepare_bench(**params)` 返回 `ExplicitPreparedBenchmark`（run_gpu 函数 + state），包上 `PreparedKernelBenchmark(kernel, label)`；②`run_prepared_kernel_bench`（GPU 阶段）：`assert_process_local` → 有 CUDA 分配则先 `validate_current_cuda_assignment` → `gpu_stage_compile_guard` 内执行 `run_gpu(**bench_kwargs)` → 结果 dict 补默认 kernel/label；③`close_prepared_kernel_bench` 释放。计时参数 `warmup/repeat/timer/rounds/cooldown` 全部可选——不传时由 `tvm.tirx.bench` 的规范计时器用各自默认（对齐 Triton 习惯），rmsnorm 注释里有个好例子：~2µs 的小 kernel 用 event 计时会被 launch 开销虚高 3 倍，得靠 proton 计时器量真身。

## 设计决策

1. **两阶段协议 + 三守卫**。基准必须"CPU 上准备完毕再领 GPU"：prepare 期间 `TVM_COMPILE_FORCE_FALLBACK=1` 拿到 CUDA source，用 nvrtc（cubin，默认）或 nvcc（fatbin，`-gencode` 保住 `a/f` 家族后缀特性）离线编译，注册 `tvm_callback_cuda_compile` 回调让重载的模块直接复用产物，递归 materialize 整个 import tree 并断言 runnable。GPU 阶段反手把 `tvm.compile` 换成 raise——特化漏到计时段是不允许的。守卫的报错文案本身就是架构文档。
2. **进程局部对象**。`ExplicitPreparedBenchmark` 记录 `owner_pid`、`__reduce_ex__` 直接 raise——已编译对象不可 pickle 跨进程。bench_suite 多进程调度时这是"想传也传不走"的硬保证，而非约定。
3. **GPU 绑定诚实性**。绕过 `CUDA_VISIBLE_DEVICES` 用 cuda.bindings driver 直取物理 UUID；NVML 枚举本 PID 的 compute running processes，验证进程**从未**在未分配的卡上建过 context。多卡基准下这保证"一 workload 一物理卡"可证明。
4. **中断延迟**。SIGUSR1 落在大型 import（torch._dynamo、CuTeDSL MLIR）或 host JIT 中途会留下半初始化的 `sys.modules`，毒化子进程的所有后续重试。深度计数器 + 安全线程属性 + 区域退出点重投递（`os.kill` 自发信号），让注定被丢弃的样本在无害点终结。
5. **A/B 的信任边界切分**。同一进程里"配置归当前、执行归过去"是刻意的：配置变了意味着基准问题本身变了（不可比），而执行链必须整体留在旧树（含旧版 kern 基座）才是一次公平对照。共享前缀白名单把"两个版本都必须一致的测量基建"（计时、调度）钉死为字节级同一份，其余一律隔离——对照实验的内部效度就是这样一寸寸砌出来的。
6. **`bench()` 引用门控**：外部 reference 计时仅在显式诊断模式（env 开关）放行，平时基准结果只含本库 kernel——防止基线混入默认计时。

## 新人提示

- 阅读顺序：`run_kernel_test`（10 行）→ rmsnorm 的 `run_test`/`prepare_bench`（最小实例）→ 回来读 `prepare_kernel_bench` 的守卫嵌套。
- 可基准 kernel **必须**提供 `prepare_bench`，缺了会 TypeError"cannot use a one-stage fallback"。
- 看到报错 "GPU stage attempted tvm.compile"：特化/编译没在 prepare 阶段做完，去补 `prepare_bench`，别想着在 run_gpu 里编。
- `required_num_gpus` 从 prepared 对象上动态取且严格校验类型——多卡 kernel 在这里声明需求。
- 易混淆：`PreparedBenchmark`（runner 定义的 Protocol）与 `ExplicitPreparedBenchmark`（唯一官方实现）与 `PreparedKernelBenchmark`（外层身份包装）三层各管一件事。
