# MatX 文档面、示例集与 vendored 构建框架

## 一、角色定位

本篇覆盖 MatX 的"库外圈"：`docs_input/`（330 文件，Sphinx 文档站）、`examples/`（41 文件，领域示例集）、vendored 的 `cmake/rapids-cmake/`（648 文件）与 `public/cpm-cmake/`（81 文件）。它们不参与张量计算本身，却决定三件事：用户怎么学会用、下游怎么接入、clone 之后为什么不需要预装任何依赖。对 header-only 库而言，这一圈的工程质量直接等于产品体验。

## 二、内部结构

### 2.1 docs_input：三层文档体系

- **api/**（259 rst，18 个子目录）：casting/creation/dft/io/linalg/logic/manipulation/math/polynomials 等逐 API 参考，linalg 再分 decomp/eigenvalues/matvec/other（:5 个子区）——与 transforms/ 双后端目录一一呼应。每页一个函数签名+语义（as_double.rst 到 svd.rst）。
- **教学层**：basics/（16 rst：concepts/creation/broadcast/datatype/debug/fusion/logging…速成课）、notebooks/（11 个 ipynb：01_introduction→02_operators→03_transforms→04_radar_pipeline→05_fusion→06_profiling→99_assignments，配 clear_cache.sh）、examples/（black_scholes.rst/fftconv.rst 文档化示例）。
- **骨架**：index.rst/quickstart.rst（make_tensor 两种形状 :30/:41、`(t4pc = t4p).run()` :196、嵌套命名空间说明 :17）、build/external/executor_compatibility/version rst、conf.py.in 与 Doxyfile.in——构建链是 **Doxygen 抽 C++ 注释 → breathe 桥接 → Sphinx 渲染**（docs_input/CMakeLists.txt:12 Doxygen 输出目录、:21 DOXYXML_DIR、:50 SPHINX_BUILD、:62 `-Dbreathe_projects.MatX=...`）。developer_guide/（5 rst：operators/transforms/distributed_tensors/docs）是贡献者向的架构文档。

### 2.2 examples：41 文件的领域横截面

顶层示例覆盖金融（black_scholes.cu + black_scholes_benchmark.py 基准联动）、雷达（simple_radar_pipeline.cu 全链四段 NVTX range :83-95，:141 吞吐打印，:155 matxPrintMemoryStatistics）、波束成形（mvdr_beamformer）、信号（fft_conv/spectrogram/pwelch/resample/convolution/conv2d/interpolate/recursive_filter）、数学（cgsolve/eigenExample/qr/svd_power/spherical_harmonics）、机制演示（kernel_fusion 融合、print_styles、streaming 流式、sparse_tensor、test_host host 路径）。两个接入示范：**cmake_sample_project** 教下游消费——CMakeLists.txt:9 注释"importing MatX as a CMake subdirectory"、:16 可改 MatX 路径（find_package(CUDAToolkit 11.5) :6 是硬门槛）；**python_integration_sample** 教嵌入 Python（与 core/pybind.h 的 numpy 零拷贝闭环）。

### 2.3 vendored rapids-cmake：648 文件的构建框架

`cmake/rapids-cmake/` 是 RAPIDS 生态 CMake 框架的整体 subtree，**VERSION 26.04.00**（VERSION:1）、分支 release/26.04（RAPIDS_BRANCH:1）。三块组成：
- `rapids-cmake/`（98 文件）：核心模块——cpm/cuda/cython-core/export/find 子系统（rapids-cpm.cmake/rapids-cuda.cmake 等）+ RAPIDS.cmake 入口（:8 注释"preferred entry point"，:14-15 强制要求 rapids-cmake-branch/version 变量）；
- `testing/`（448 文件）：**模块级回归测试**——每模块一个 .cmake 场景（enable_fatbin_compression-{invalid-tuning-flag,no-arguments,target,var}.cmake 四变体、init_arch-{native,native-no-gpu,...}），testing/cpm/ 下 cpm_bs_thread_pool-{build-config-works,export,install-config-works}.cmake 验证依赖封装——它是 CMake 模块的 GTest；
- docs/ci/.github 余量。MatX 借它获得 CUDA 架构探测、依赖封装与安装导出，不必自研。

### 2.4 vendored cpm-cmake：依赖拉取的最后一块

`public/cpm-cmake/`（79 文件）= CPM.cmake v0.32.2。`CPMFindPackage`（CPM.cmake:232）语义：本地 find_package 优先、失败回退 CPMAddPackage 源码拉取（:244/:258 调用点）——与 MatX 自身 Get*.cmake 模块（GetCUTLASS/GetGTest）协作，保证"clone 即可构建"。**subtree 纪律**（public/subtreeInstructions.txt:1-4）：`git subtree add/pull --prefix public/cpm-cmake ... v0.32.2 --squash`——两个 vendored 树都只能整树升级，禁止散改（rapids-cmake.txt 是它的指针文件）。

## 三、外部连接

- docs 的 api/ 树映射 include/matx 公开面（api/linalg/decomp ↔ transforms/ 求解器族），breathe 吸 doxygen 注释——**新 API 不写注释=文档自动缺页**；
- examples 是 CI 的编译目标之一（MATX_BUILD_EXAMPLES，CMakeLists.txt:62），永远保持可编译=文档级承诺；
- rapids-cmake 与 cpm-cmake 服务同一件事：MATX_BUILD_TESTS/BENCHMARKS 打开时的 GTest/nvbench/CUTLASS 拉取，版本钉死在 cmake/versions.json；
- docs_input/notebooks 的 04_radar_pipeline 与 examples/simple_radar_pipeline 同题材（notebook 教学 vs .cu 生产形态）。

## 四、数据流

文档构建流：`MATX_BUILD_DOCS=ON` → Doxygen 扫注释 → XML（:21）→ breathe 桥（:62）→ Sphinx 渲染站点。依赖流：CMakeLists → rapids-cmake init（RAPIDS.cmake:8）→ Get*/CPMFindPackage 按 versions.json 拉依赖。下游流：抄 cmake_sample_project → add_subdirectory/find_package(MatX)。

## 五、设计决策

1. **文档三分层**（api 参考/basics 速成/notebooks 交互）对应三类读者：查签名的、入门的、要跑通看的——99_assignments.ipynb 甚至留作业，教学意图明显。
2. **vendored 而非 fetch**：CPM 本可以运行时拉 rapids-cmake，但 subtree 让离线构建与版本审计成为可能——代价是仓库 648+79 文件膨胀，靠 subtreeInstructions.txt 的整树纪律控制。
3. **api 目录即架构镜像**：docs 分区刻意贴合代码分区（linalg/decomp ↔ 求解器族），文档漂移在目录层面就可见。
4. **示例双形态**：.cu 生产形态 + notebook 教学形态覆盖同一题材（雷达），一份认知两种入口。
5. **甄别**：任务书称"217 页 API 参考"——实测 api/ 为 **259 个 rst**（18 子目录）。

## 六、新人提示

1. 改公开 API 后本地跑一遍 docs 构建（MATX_BUILD_DOCS=ON），breathe 会把没注释的符号暴露成空页；
2. 学 API 顺序：quickstart → notebooks 01-03 → 领域 notebook（04 雷达）→ api/ 当字典查；
3. 下游集成直接抄 examples/cmake_sample_project，注意 CUDAToolkit 11.5 门槛（其 CMakeLists.txt:6）；
4. 升级 vendored 依赖：改 cmake/versions.json（轻）或 subtree pull（重，按 public/subtreeInstructions.txt:4 的命令模板）；
5. 给库提 PR 前读 docs_input/developer_guide/{operators,transforms}.rst——贡献者约定的权威文本；
6. rapids-cmake/testing 的 .cmake 场景文件是学"怎么测试 CMake 模块"的稀有范本，构建系统工程师值得单独精读。

*锚清单：quickstart.rst:17/30/41/196、api 子目录清单（casting/creation/dft/io/linalg/decomp/eigenvalues/matvec）、notebooks 01-06/99、docs_input/CMakeLists.txt:12/21/50/62、examples/simple_radar_pipeline.cu:83-95/141/155、examples/cmake_sample_project/CMakeLists.txt:6/9/14/16、cmake/rapids-cmake/VERSION:1、RAPIDS_BRANCH:1、RAPIDS.cmake:8/14-15、testing/enable_fatbin_compression-*.cmake、testing/cpm/cpm_bs_thread_pool-*.cmake、public/cpm-cmake/cmake/CPM.cmake:232/244/258、public/subtreeInstructions.txt:1-4、CMakeLists.txt:3/37/62。*
