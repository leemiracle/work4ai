# 精讲：csrc/jit/compiler.hpp —— JIT 运行时编译框架

> 原文件：`csrc/jit/compiler.hpp`（DeepGEMM，362 行）

## 一、角色定位

DeepGEMM 的招牌设计是 **JIT（即时）编译**：把 M/N/K 形状、BLOCK 尺寸、swizzle 模式、流水级数等当作编译期常量生成 kernel 源码，运行时编译成 cubin 再加载。本文件就是这套机制的编译器抽象层（知识图谱 tour 第 4 步"JIT 编译框架"），定义了 `Compiler` 基类与 `NVCCCompiler`/`NVRTCCompiler` 两种后端，以及带分布式文件系统安全保证的缓存写入协议。它决定了"第一次调用慢、后续命中缓存快"的整体行为。

## 二、内部结构

- **`Compiler` 基类**：静态成员 `library_root_path`/`library_include_path`/`cuda_home`/`cuobjdump_path`（由 Python 侧 `_C.init` 经 `prepare_init` 注入）；实例成员 `signature`（编译器指纹）、`flags`（公共编译选项）、`cache_dir_path`（默认 `~/.deep_gemm`，可被 `DG_JIT_CACHE_DIR` 覆盖）。
- **文件系统工具**：`fsync_path`/`fsync_dir`（自底向上递归 fsync）、`put`（写文件+fsync）、`make_tmp_dir`。
- **核心方法 `build(name, code)`**：签名 → 缓存查询 → 编译 → 原子落盘 → 返回 `KernelRuntime`。
- **`NVCCCompiler`**：构造时调用 `nvcc --version` 解析版本（要求 ≥12.3，<12.9 打印性能警告），`compile()` 写 `kernel.cu` 后起子进程调 nvcc，可选产出 PTX，并用正则检查 "Local memory used"。
- **`NVRTCCompiler`**：进程内编译（`nvrtcCreateProgram`/`nvrtcCompileProgram`），≥12.8 启用 `--pch`（注释明言 PCH 对编译速度至关重要），直接取 CUBIN 字节写盘。
- **全局单例**：文件尾 `static auto compiler = LazyInit<Compiler>(...)`，按 `DG_JIT_USE_NVRTC` 环境变量选后端，默认 NVCC。

## 三、外部连接

依赖 `nvrtc.h`、`cache.hpp`（`kernel_runtime_cache` 运行时缓存）、`device_runtime.hpp`（查询 SM 架构生成 `-arch` 旗标）、`include_parser.hpp` 与 `utils/{hash,system,format,lazy_init}.hpp`。产出的 cubin 由 `KernelRuntime` 加载执行；SASS 反汇编用外部 `cuobjdump`。环境变量大家族：`DG_JIT_CACHE_DIR`、`DG_JIT_DEBUG`、`DG_JIT_DUMP_ASM/DUMP_PTX/DUMP_SASS`、`DG_JIT_PTXAS_VERBOSE/PTXAS_CHECK`、`DG_JIT_CPP_STANDARD`（默认 C++20）、`DG_JIT_NVCC_COMPILER`、`DG_JIT_PRINT_COMPILER_COMMAND`。

## 四、数据流

`build()` 走读：①拼 `kernel_signature = name$$signature$$flags$$code`，SHA 十六进制摘要生成缓存目录 `cache/kernel.<name>.<digest>`；②查 `kernel_runtime_cache` 命中即返回；③在 tmp 目录下编译出 `kernel.cubin`（按需另出 `kernel.ptx`/`kernel.sass`）；④`fsync_dir` 刷盘；⑤`std::filesystem::rename` 把整个临时目录原子改名为最终缓存路径——若别的 rank 已抢先创建，rename 失败则清理自己的目录改用现存版本；⑥再从运行时缓存取出并断言非空。编译旗标固定含 `--ptxas-options=--register-usage-level=10`（倾向高占用率调度）与 `-O3`、`--expt-relaxed-constexpr` 等。

## 五、设计决策

- **目录级原子 rename**：注释点明——单文件 rename 在分布式文件系统上有陈旧 inode 问题，目录 rename 本地与分布式都原子；这是多 rank/多进程共享缓存不损坏的关键。
- **fsync 三件套**：`close()` 不保证对其他进程（如 nvcc 本身）可见，故写后必 fsync。
- **`remove_all` 禁令**：并发进程操作同一父目录时 `std::filesystem::remove_all` 可能段错误，改用 `safe_remove_all`。
- **签名即失效键**：NVCC 版本号进 signature，编译器升级自动重编译。
- **NVCC 的 cwd 陷阱**：编译命令先 `cd` 到干净临时目录，避免 cwd 下同名文件遮蔽 C++ 标准库头。
- **PCH 加速**：NVRTC ≥12.8 用预编译头把数十个 CUTLASS 头的解析成本摊薄。

## 六、新人提示

排障第一课：首次运行某形状的内核会卡几秒到几十秒，那是 NVCC 在跑，不是死锁；缓存查询可开 `DG_JIT_PRINT_COMPILER_COMMAND=1` 观察命令行。想看生成的 SASS/PTX 设 `DG_JIT_DUMP_ASM`，产物就在缓存目录里。改了头文件但行为没变？先清 `~/.deep_gemm` 或换 `DG_JIT_CACHE_DIR`。写新内核时记得 `DG_JIT_PTXAS_CHECK=1` 能帮你抓寄存器溢出到 local memory。
