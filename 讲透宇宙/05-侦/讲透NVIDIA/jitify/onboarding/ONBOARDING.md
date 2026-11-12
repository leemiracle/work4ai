# jitify 讲透导航（Onboarding）

> 基于图谱 67 节点/78 边/4 层/6 步 tour @ commit e0a37a6c，行号锚经源码核实（2026-11）。配套：`../deepwiki/`、`../explain/` 2 篇、`../README.md`（勘误 5 条）。

## 1. 这个仓库是什么

NVIDIA 出品的 **header-only CUDA 运行时编译（JIT）库**：单头文件 `jitify.hpp`（4540 行）把 NVRTC 的裸 API 封装成 `JitCache → Program → Kernel → KernelInstantiation → KernelLauncher` 流式调用（`jitify_example.cpp:100-111` 是最短完整样例：`kernel_cache.program(...) → program.kernel("my_kernel").instantiate(3, type_of(*d_data)).configure(grid, block).launch(d_data)`）。README 钉的动机：直接用 NVRTC 要手写编译选项、头文件路径与错误日志解析，Jitify 把这些连同源码加载、模板反射实例化、constant 内存更新、进程级缓存一并收编。整个仓库 15 个受分析文件里真正的产品只有 `jitify.hpp` 一个，其余全是围绕它的示例（`jitify_example.cpp` 359 行）、测试（`jitify_test.cu` 1153 行）、工具（`stringify.cpp`/`nvrtc_cli.cpp`）与构建配置。

## 2. 单头库内部分层（4 层图谱怎么读）

图谱四层：L1 构建与工程配置 → L2 单头库核心 → L3 示例头与字符串化工具 → L4 示例测试 CLI。`jitify.hpp` 内部则是清晰的四段纵切：

1. **detail 工具层**（约 L348-1080）：`replace_token`（`:348`，token 边界替换防子串误伤）、`path_simplify`（`:394`）、`hash_larson64`（`:428`，缓存键哈希）、`extract_include_info_from_compile_error`（`:442`，从编译报错解析缺失 include——错误驱动重试的核心）、`split_string`（`:521`）。
2. **jitsafe 头垫片层**（约 L1378-2200）：`jitsafe_header_preinclude_h`（`:1378`）等十余个 `R"(...)"` 原始字符串，为没有系统头文件的 NVRTC 虚拟出 limits/float/stdint/iostream 等标准头（`:554` `get_jitsafe_headers_map` 统一注册，`:620-621` 加载时命中即替换）。注意 `:1439-1442` 的 `cuda/std/*` include 在字符串内部，是给 JIT 侧探测 libcu++ 用的，不是本文件的宿主依赖（README 勘误 #4）。
3. **impl 层**（L3054 起）：`JitCache_impl`（`:3054`，Larson 哈希缓存+互斥锁）、`Program_impl`（`:3076`，构造期完成源码收集+编译+模块装载 `load_sources` `:3087`）、`Kernel_impl`（`:3110`）、`KernelInstantiation_impl`（`:3125`）、`KernelLauncher_impl`（`:3143`）——pimpl 惯例隔离实现。
4. **公开句柄层**（L3176-3500）：`KernelLauncher`（`:3176`）/`KernelInstantiation`（`:3244`）/`Kernel`（`:3392`）/`Program`（`:3457`）/`JitCache`（`:3492`），外加 `Capture`（`:3780`，CUDA Graph 捕获辅助）与 `ExecutionPolicy`（parallel_for 的启动配置载体）。编译主管线 `compile_kernel` 在 `:2717`（组装选项→nvrtcCompileProgram→日志诊断→错误驱动重试），`create_module`（`:1135`）经 `get_cuda_jit_input_type`（`:1082`）按上下文选 PTX/CUBIN 载入。线程安全由 `JITIFY_THREAD_SAFE`（`:85`，默认 1 开互斥）控制。

## 3. 双世界技巧：.jit 假后缀与三种源码来源

Jitify 的核心矛盾：宿主编译器（g++/MSVC）看不懂 `__global__`，NVRTC 又没有系统头。解法是"一个 include，两个视角"：

- **.jit 假后缀**：`jitify_example.cpp:45` 写 `#include "example_headers/my_header1.cuh.jit"`——宿主编译器 include 的是 `stringify` 生成的字符串化版本（内容是 `const char* my_header1_cuh = "…源码…"`，见 `stringify.cpp:80-82` 的逐行转义输出），让宿主侧做语法检查且不触碰 CUDA 关键字；Jitify 运行时回调则**剥掉 .jit 假后缀**去加载真实源码 `my_header1.cuh`（`my_header1.cuh:31-34` 就是一个 `square<T>` 模板）。`Makefile:50-51` 的 `%.jit: % stringify` 规则是构建侧一半；`.jit` 文件是产物不入库（勘误 #3）。
- **源码三来源**由 `load_source`（`jitify.hpp:556`）统一处理：①首行内嵌源码字符串（program 名+源码体）；②磁盘文件（含 `file_callback` 回调——`jitify_example.cpp:74` 虚拟出磁盘上不存在的 `my_header4.cuh`）；③链接器嵌入源（`JITIFY_INCLUDE_EMBEDDED_FILE` 宏 `:176` 声明 + dlfcn 从可执行文件自身查符号）。
- **-Wl,-b,binary 嵌入**：`Makefile:16-17` 定义 `EMBED_BEGIN = -rdynamic -Wl,-b,binary,` / `EMBED_END = ,-b,default`，`:26-29` 仅 Linux 分支把 `my_header2.cuh` 直接嵌进可执行文件（GCC 专属技巧，`:27` 注释明示），配合 dlsym 按 `_binary_…_start` 惯例取回——这解释了 `Makefile:37` 为什么要 `-ldl`。

## 4. 两代 API：classic 与 experimental::serialization 同名共存

`jitify.hpp` 里有**两套同名类**：classic 公开层 `Program`(`:3457`)/`Kernel`(`:3392`)/`KernelInstantiation`(`:3244`)/`KernelLauncher`(`:3176`)，以及 `jitify::experimental::serialization` 命名空间（`:3927-3931` 开 namespace，`:4063-4066` 前向声明）内的 `Program`(`:4071`)/`Kernel`(`:4174`)/`KernelInstantiation`(`:4229`)/`KernelLauncher`(`:4419`)——后者支持把编译产物（PTX+链接文件）落盘、再从磁盘重建实例，服务于"编译一次、冷启动复用"的场景。图谱把两代同名类各合并成了单节点（13 个 class 节点无一重复），读图谱时须知 `Program` 节点实际覆盖源码里两个不同代的类（勘误 #1）。测试侧两代都有对应用例：`jitify_test.cu:107` `Simple` vs `:133` `Simple_experimental`、`:219/:278` `MultipleKernels(_experimental)`、`:375/:456` `ConstantMemory(_experimental)`。

## 5. 回归防线与独立工具

- **`jitify_test.cu`**（1153 行 26 个 `TEST(JitifyTest, …)` 用例，nvcc 编译）：覆盖多 kernel 程序（`:219`）、constant 内存（`:375`）、parallel_for（`:542`）、非法程序报错（`:564`）、pragma 替换（`:597`）、Thrust/CUB 头（`:615/:672`）、未用全局剔除（`:752`）、外部文件与当前可执行文件链接（`:819/:863`）、类型反射（`:897`，`:904` `JITIFY_TYPE_REFLECTION_TEST` 宏逐类型展开）、类对象作 kernel 参数（`:995`，对应 `example_headers/class_arg_kernel.cuh:31` 的 `Managed` 基类——`:35` `#ifndef __CUDACC_RTC__` 时 `operator new` 走 cudaMallocManaged，JIT 侧跳过）。Makefile 会链接第二个编译单元验证 jitify.hpp 无多重定义问题（digest 钉版）。
- **`nvrtc_cli.cpp`**（593 行）：脱离 Jitify 的 NVRTC 裸用法参照，复刻 nvcc 风格 CLI 子集——`-ptx`（`:407`）/`-cubin`（`:409`）/`-arch`（`:447`）/`-ne` demangle（`:418`）/`-h`（`:387`）/`-V`（`:390`）/stdin 输入（`:511-513`）。`Makefile:56-58` 构建它之后**自动**执行 `nvrtc_cli_test.sh`（构建即测试的少见结构）。

## 6. 新人上手路线

1. 读 `README.md` 的 Quick example（与 `jitify_example.cpp:99-111` 同构），建立流式 API 直觉；
2. `make` 跑通 jitify_example（注意先决条件：`%.jit` 规则自动 stringify，gtest 需 `make get-deps` 装 cmake 再 `Makefile:66-71` 拉 googletest release-1.12.1，CUB 头 `Makefile:76-80` 克隆到 /tmp/cub）；
3. 按 `jitify_example.cpp` 的 `test_*` 函数顺序精读（40-42 行打开 `JITIFY_PRINT_PTX/LINKER_LOG/LAUNCH` 三个调试宏是现成的观察窗口）；
4. 深入 `jitify.hpp` 时按第 2 节四段纵切自下而上；改库本体后必跑 `jitify_test.cu`；
5. 需要理解 NVRTC 裸行为时用 `nvrtc_cli` 直接实验；进阶阅读 `explain/01`（单头库本体）与 `explain/02`（双世界构建机制）。
