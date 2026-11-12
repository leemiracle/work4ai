# 精讲 01：jitify.hpp——单头库本体与流式 JIT API

## 角色定位

`jitify.hpp`（4540 行）是整个仓库唯一的产品：一个零编译依赖的 header-only 库，把 NVRTC 运行时编译 + CUDA Driver 装载 + 源码工程化（多来源加载、include 递归、标准头垫片）+ 模板反射实例化打包成五个句柄类的流式调用。宿主程序 `#include "jitify.hpp"` 一行即得全部能力（`jitify_example.cpp:43`）。

## 内部结构

四段纵切。**detail 工具层**：`hash_larson64`（`jitify.hpp:428`）是 JitCache 缓存键；`replace_token`（`:348`）按 token 边界替换标识符，供 `__restrict__`/`throw` 等宿主不认的关键字剔除；`extract_include_info_from_compile_error`（`:442`）从 NVRTC 报错文本里解析缺失头文件名。**jitsafe 垫片层**：`jitsafe_header_preinclude_h`（`:1378`）到 `jitsafe_header_string_h`（`:2115`）等十余个原始字符串虚拟标准头，`get_jitsafe_headers_map`（`:554`）注册、`load_source` 命中即替换（`:620-621`）——NVRTC 没有系统头文件，这套垫片是"JIT 侧世界"的地基。**impl 层**（`:3054-3175`）：五个 `*_impl` 类持真实状态。**公开层**：`JitCache`（`:3492`）进程级缓存，同源码+选项命中免重编，建议 static 单例（`jitify_example.cpp:99`）；`Program`（`:3457`）→ `Kernel`（`:3392`）→ `KernelInstantiation`（`:3244`）→ `KernelLauncher`（`:3176`）四级句柄链。

## 外部连接

向上被 `jitify_example.cpp`（API 活文档）与 `jitify_test.cu`（26 用例回归线）消费；向下依赖三组系统库：NVRTC（编译）、CUDA Driver `cuModuleLoadDataEx`（`create_module` `:1135` 装载，`get_cuda_jit_input_type` `:1082` 按上下文选 PTX/CUBIN）、dlfcn（`-ldl`，取链接器嵌入源）。constant 内存链路走 `demangle_ptx_variable_name`（`:1033`）还原 PTX mangled 名再取全局变量指针。

## 数据流

`kernel_cache.program(source, headers, options)` → `load_source`（`:556`，160 行引擎：内嵌字符串/磁盘文件/include 回调/链接器嵌入四来源，递归展开 `#include`，jitsafe 替换）→ `compile_kernel`（`:2717`，首轮**故意空编**，靠 NVRTC 报错逐个发现缺失头再补载——错误驱动重试）→ 产出 PTX/CUBIN → `create_module` 装载并登记全局变量表 → `kernel("name").instantiate(args…)` 用 `reflect_template`（`:1013`，把类型/值反射成 `"<float,7,char>"` 代码串，注释 `:729-730` 给了映射规则）生成特化名 → `.configure(grid,block).launch(...)` 真正下发。

## 设计决策

- **错误驱动头发现**：不预扫描 include 树，而是让编译器报错来"要"头文件——省掉半个 C 预处理器，代价是首轮编译必失败一次。
- **pimpl 全覆盖**：公开类全是句柄，`*_impl` 持状态，单头库也能保 ABI 面干净。
- **两代 API 同名共存**：classic（`:3176-3492`）与 `experimental::serialization`（`:3927` 起，`Program :4071`/`Kernel :4174`/`KernelInstantiation :4229`/`KernelLauncher :4419`）——后者可把 PTX+链接文件落盘重建，服务冷启动。
- **线程安全默认开**（`JITIFY_THREAD_SAFE :85`）：缓存表加锁，多线程共享 JitCache 安全但有序列化开销，可宏关。

## 新人提示

调 Jitify 三件套：开 `JITIFY_PRINT_PTX/JITIFY_PRINT_LINKER_LOG/JITIFY_PRINT_LAUNCH`（`jitify_example.cpp:40-42`）看编译/链接/启动全链日志；include 找不到先想 file_callback（`:74` 虚拟 my_header4 是官方示范）；改库本体后必跑 `jitify_test.cu`（nvcc 编译路径与 example 的纯 g++ 路径行为有差异）。注意 `:1439-1442` 等 `cuda/std/*` include 写在 jitsafe 字符串里，grep 本文件时会大量假命中"依赖 libcu++"——那是 JIT 侧垫片内容。
