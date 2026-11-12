# 08 · memtest 与 memory 双测试线 + nvbandwidth 集成

## 角色定位

DCGM 诊断的显存测试有三条线：`nvvs/plugin_src/memory/`（插件名 "memory"，nvvs/include/PluginStrings.h:245）做 L1 tag 与帧缓冲写入/校验；`nvvs/plugin_src/memtest/`（插件名 "memtest"，nvvs/include/PluginStrings.h:265）是 cuda_memtest 移植，跑模式测试；`nvvs/plugin_src/nvbandwidth/` 不写 kernel，包一个外部带宽工具二进制，子进程+JSON。三者都走篇 7 的 Plugin 框架（`Memory`/`NVBandwidthPlugin` 均 `: public Plugin`，见 nvvs/plugin_src/memory/Memory_wrapper.h:33 与 nvvs/plugin_src/nvbandwidth/NVBandwidthPlugin.h:34）。

## 内部结构

memtest 线核心是测试分发表 `cuda_memtests[]`（nvvs/plugin_src/memtest/Memtest.cpp:117）：**勘误一：实际 11 项而非"22 核"**——test0 Walking 1 bit、test1 Own address、test2/3/4/6 Moving inversions、test5 Block move、test7 Random、test8 Modulo 20、test9 Bit fade、test10 stress，原型 `int testN(memtest_device_p, MemoryChunkManager const &)`。默认只开 test7/test10（数组 enabled=1，参数默认亦 True，nvvs/plugin_src/memtest/memtest_wrapper.cpp:44）。`MemtestPlugin` 构造于 nvvs/plugin_src/memtest/memtest_wrapper.cpp:23，C ABI 外壳在 nvvs/plugin_src/memtest/MemtestWrapper.cpp:86；`MemoryChunkManager`（nvvs/plugin_src/memtest/MemoryChunkManager.h:61）切分显存并执行最小分配比例闸门（默认 75%）。memory 线由 `memory.cpp` 的 `mem_globals_t` 全局态与 `L1TagCuda.cpp` 组成，kernel 源仅 memtest_kernel.cu（47 行，memsetval/memcheckval）与 l1tag.cu（175 行，InitL1Data/L1TagTest）。

## 外部连接

memory 线最独特的机制是 **PTX 内嵌 + Driver API 免 CUDA runtime**：nvvs/plugin_src/memory/build_ptx_string.sh:24 用 docker 镜像 `nvcr.io/nvidia/cuda:10.2-devel-ubuntu18.04` 起 nvcc，`-ptx -arch=sm_30`（:33）编译两个 .cu——sm_30 让 PTX 在 Kepler 以后所有架构靠驱动 JIT 前向兼容；bin2c 把 .ptx 转成 C 数组头，find_ptx_symbols.py 扫 PTX 的 `.entry`（nvvs/plugin_src/memory/find_ptx_symbols.py:31）追加 `<kernel>_func_name` 符号变量。**勘误二："3471 行"口径不成立**：实测 l1tag_ptx_string.h 为 15409 行、memtest_kernel_ptx_string.h 仅 119 行。运行期 nvvs/plugin_src/memory/memory.cpp:107 `cuModuleLoadData(&mod, memtest_kernel_ptx_string)`，:115/:119 `cuModuleGetFunction` 取 memsetval/memcheckval，:224 `cuLaunchKernel` 发射；L1Tag 同款（nvvs/plugin_src/memory/L1TagCuda.cpp:167/:341）。全程 Driver API、不链 cudart。

nvbandwidth 线是外部二进制集成：四份 nvbandwidth（Cuda12/13 × x86_64/aarch64）在仓里均为 **132 字节** Git LFS 指针文本（勘误三：非"134 字节"），三行 version/oid sha256/size，真身 3.2-3.7MB——git-lfs 安装后 checkout 才拉真文件。CMake 按 `bin/${CMAKE_SYSTEM_PROCESSOR}/nvbandwidth` 安装（nvvs/plugin_src/nvbandwidth/Cuda12/CMakeLists.txt:17）。

## 数据流

memtest：`MemtestPlugin::Go` → `Memtest::Run`（nvvs/plugin_src/memtest/Memtest.cpp:535）→ 逐 enabled 项调 `testN(gpu, chunkManager)`（kernel 在 nvvs/plugin_src/memtest/tests.cu:58 起）。memory：`Memory::Go`（nvvs/plugin_src/memory/Memory_wrapper.cpp:52）→ `mem_init`（nvvs/plugin_src/memory/memory.cpp:414，含 cuModuleLoadData）→ `main_entry`（:509）→ memsetval 写入再 memcheckval 校验，错误计数经 `cuModuleGetGlobal_v2` 回读（memory.cpp:111）。nvbandwidth：`NVBandwidthPlugin::Go`（nvvs/plugin_src/nvbandwidth/NVBandwidthPlugin.cpp:204）`FindExecutable("nvbandwidth", m_cudaDriverMajorVersion, ...)`（:331，PluginCommon 的 cuda{N} 搜索），argv 加 `-j`/`-v`（:347）后走基类 `LaunchExecutable`（:353），解析 JSON 判 PASS/FAIL。

## 设计决策

其一，**Driver API + sm_30 PTX** 换免 cudart 依赖与跨代兼容，代价是每次 JIT。其二，**LFS 分发外部工具**：build.sh 克隆 github.com/NVIDIA/nvbandwidth V0.8（nvvs/plugin_src/nvbandwidth/build.sh:37），四组合（CUDA 12.9.1/13.0.0 × amd64/arm64）各建一次，`-DMULTINODE=0`、静态 libstdc++ 后 strip。其三，**单阶段 Dockerfile**：nvvs/plugin_src/nvbandwidth/Dockerfile:20 设 `NVIDIA_VISIBLE_DEVICES=all`，:45 用 `RUN --mount=type=bind,source=cuda-repo.deb` 注入本地 CUDA repo deb——避免安装包进镜像层。其四，默认仅 test7/test10：全量太慢，模式覆盖交给 memory 线互补。

## 新人提示

- 三条线速记：memory=L1tag+fb 写校验（内嵌 PTX），memtest=cuda_memtest 11 项模式测试，nvbandwidth=外部带宽二进制（LFS+子进程 JSON）。
- git-lfs 判定：仓库里 nvbandwidth 应是 MB 级，132 字节文本即假货，先 `git lfs pull`。
- 改 memtest_kernel.cu/l1tag.cu 后必须重跑 build_ptx_string.sh——不重新生成 ptx_string.h，运行时用的还是旧 PTX。
- sm_30 是刻意选择：别"升级"成 sm_90，会丢老卡前向兼容；新架构特性走 nvbandwidth 这类外部工具线。
