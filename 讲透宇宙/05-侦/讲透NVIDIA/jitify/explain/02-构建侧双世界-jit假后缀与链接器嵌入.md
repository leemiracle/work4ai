# 精讲 02：构建侧双世界——.jit 假后缀、stringify 与 -Wl,-b,binary 嵌入

## 角色定位

Jitify 的根本矛盾：宿主编译器（g++/MSVC）看不懂 `__global__`，NVRTC 又没有系统头与完整预处理器。仓库用三个构建期机制维持"宿主语法检查"与"运行时 JIT"两个世界并行：`stringify.cpp` 字符串化工具、`Makefile` 的 `%.jit` 规则与链接器嵌入技巧。它们都在 `jitify.hpp` 之外——理解 Jitify 不只读头文件，构建侧同样关键。

## 内部结构

**stringify.cpp**（92 行小工具）：`main`（`:64`）读入文件，`sanitize_string_literal` 逐行转义后输出合法 C++ 字符串字面量——首行是文件名（`:80`），正文逐行 `"…\n"`（`:82`）；`Usage: … infile [varname] > outfile`（`:68`）说明它就是个纯过滤器。产物如 `my_header1.cuh.jit`，内容形如 `const char* my_header1_cuh = "template <typename T>\n…"`——宿主编译器 include 它毫无障碍（纯字符串定义，不触碰任何 CUDA 关键字），`my_header1.cuh:31-34` 的 `square<T>` 模板因此能被宿主编译器做语法检查。

**Makefile 双规则**：`%.jit: %` + `./stringify $< > $@`（`Makefile:50-51`）——`HEADERS` 列表（`:39-41`）里的 `example_headers/my_header1.cuh.jit` 由此生成；`jitify_example.cpp:45` 的 `#include "example_headers/my_header1.cuh.jit"` 消费它。而 Jitify 运行时回调剥掉 `.jit` 假后缀加载真实 `.cuh`——一个 include 名字，两个世界各自取所需。

**链接器嵌入**：`Makefile:16-17` `EMBED_BEGIN = -rdynamic -Wl,-b,binary,` / `EMBED_END = ,-b,default`，`:26-29` 仅 `uname == Linux` 分支把 `my_header2.cuh` 直接嵌进可执行文件（`:27` 注释明示 GCC-on-Linux 专属）。运行时 `JITIFY_INCLUDE_EMBEDDED_FILE(name)`（宏定义 `jitify.hpp:176`，用法见 `:49-50` 文档示例）配合 dlfcn 按链接器惯例符号（`_binary_…_start/_end`）取回源码；这就是 `Makefile:37` `-ldl` 的用途。第三条来源是 file_callback 回调虚拟文件（`jitify_example.cpp:74` 的 my_header4），完全绕开磁盘。

## 外部连接

三个示例头各验证一条链路：`my_header1.cuh`（.jit 机制原型）、`my_header2.cuh`（链接器嵌入）、`my_header3.cuh`（多头包含链）；`constant_header.cuh` 测 `__constant__/__device__` 变量更新；`class_arg_kernel.cuh:31-36` 的 `Managed` 基类在 `#ifndef __CUDACC_RTC__` 时让 `operator new` 走 cudaMallocManaged——宿主侧分配、JIT 侧可用的类参数范式。

## 数据流

`make jitify_example`：先隐式构建 stringify（`:53-54`）→ `%.jit` 规则生成 `.cuh.jit` → g++ 编译 `jitify_example.cpp`（`:47-48`，注意它不经 nvcc）→ EMBED 宏把 my_header2.cuh 塞进 ELF → 运行时 load_source 四来源分发（`jitify.hpp:556`）。jitify_test 走 nvcc 路径（Makefile 另有规则），额外链接第二编译单元验证头文件无多重定义——两条编译路径互补护住"单头库"承诺。

## 设计决策

- **.jit 而非条件编译**：给宿主看的不是 `#ifdef` 裁剪版而是字符串字面量——零语法污染，IDE 还能把 .jit 当独立文件管理。
- **嵌入只押注 GCC/Linux**：Darwin 分支（`Makefile:32-33`）只改库目录不嵌入，Windows 则完全没有 Makefile 支持——README 的跨平台声明弱于构建现实（README 勘误 #2）。
- **构建即测试**：`Makefile:58` 构建 nvrtc_cli 后自动跑 `nvrtc_cli_test.sh`，防止 CLI 工具静默腐化。

## 新人提示

克隆仓库后直接 `g++ jitify_example.cpp` 会失败——`.jit` 文件不入库，必须先 `make`（或手工 `./stringify example_headers/my_header1.cuh > example_headers/my_header1.cuh.jit`）。看到 `_binary_example_headers_my_header2_cuh_start` 这类符号不要慌，是 `-Wl,-b,binary` 的命名惯例。改示例头后记得 .jit 是缓存产物，重跑 make 即再生成；调试嵌入源是否生效，开 `JITIFY_PRINT_LINKER_LOG`（`jitify_example.cpp:41`）。
