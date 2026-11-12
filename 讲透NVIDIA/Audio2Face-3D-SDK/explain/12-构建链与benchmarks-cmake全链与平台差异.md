# 12 · 构建链与 benchmarks——cmake 22 节点全链、伞形共享库与三套基准的平台差异

## 角色定位

构建链是 L15 层：图谱 22 个 config 节点 = 10 份 CMakeLists + **12 个自带 FindXxx 模块**（cmake/Modules/ 全入层，scanner 原归 docs，按语义修正为 config，NOTES batch-3）。根 `CMakeLists.txt` 定义依赖获取与编译环境，四个 `add_subdirectory`（CMakeLists.txt:147-150）串起递归树；`audio2x-sdk/CMakeLists.txt` 把三库门面打包成**伞形共享库 libaudio2x**。benchmarks 是 L13 层：两个基准可执行文件+四个平台脚本，既测性能也当冒烟回归。

## 内部结构

**根 CMakeLists 要点**：`cmake_minimum_required(3.24)`（CMakeLists.txt:1）；ModulePath 指向自带 Modules（CMakeLists.txt:7-10）；C++17 强制（CMakeLists.txt:12-13）；**configure 期自动跑 fetch_deps**（CMakeLists.txt:35-55，packman 拉依赖，多配置生成器双拉 39-45）；CUDAToolkit 12.8 REQUIRED 且钉 nvcc（CMakeLists.txt:72-79）；CUDA 架构八代 `75..120`+Shared runtime（CMakeLists.txt:81-82）；**12 个 find_package 连发**（CMakeLists.txt:86-97）：AudioFile/Benchmark/Cnpy/CXXOPTS/Eigen3/GTest/MagicEnum/NlohmannJson/ReflCpp/TbtSVD/TensorRT/ZLIB；编译定义压三库日志到 error 级+`_GLIBCXX_USE_CXX11_ABI=0`+`USE_NVTX`（CMakeLists.txt:111-118）。

**12 个 Find 模块**同构套路（FindTbtSVD.cmake:22-40）：四级搜索——CMake 变量 > 环境变量 > 项目约定路径 > 系统路径，产出 imported target（`tbtSVD::tbtSVD`、`TensorRT::TensorRT`，FindTensorRT.cmake:17-30 同构）。这层把"packman 拉依赖到固定目录"与"CMake 发现已拉依赖"解耦。

**伞形打包**（audio2x-sdk/CMakeLists.txt）：`add_library(audio2x SHARED)`（audio2x-sdk/CMakeLists.txt:2）只编三个门面 .cpp（audio2x-sdk/CMakeLists.txt:16-20）链三 core 静态库（audio2x-sdk/CMakeLists.txt:36-42）；**Unix 下 `-Bsymbolic + --exclude-libs,ALL`**（audio2x-sdk/CMakeLists.txt:53-59，注释"prevent symbol clashes with other binaries"——静态库符号全隐藏，导出面只剩门面 DLL_API）；include 以 `$<TARGET_PROPERTY:...>` 透传三 core 接口目录（audio2x-sdk/CMakeLists.txt:45-50），POST_BUILD 拷公共头+VERSION.md 进发行目录（audio2x-sdk/CMakeLists.txt:62-97）。core 侧：audio2x-common `GLOB_RECURSE` 收源且 PUBLIC 链 Cnpy/CUDA::cudart/TensorRT/ZLIB（audio2x-common/source/audio2x/CMakeLists.txt:10-38）；audio2emotion-core **include 双根**（PUBLIC+PRIVATE internal，audio2emotion-sdk/source/audio2emotion-core/CMakeLists.txt:18-23）是手扫 #include 的依据（NOTES batch-8）。

**三套基准**：①audio2emotion-benchmarks 四源文件（audio2emotion-sdk/source/benchmarks/CMakeLists.txt:9-13）；②audio2face-benchmarks 六源文件（audio2face-sdk/source/benchmarks/CMakeLists.txt:10-17），**多链 Cnpy+ZLIB**（NOTES batch-5：NPZ 姿态数据所需）；③blendshape 求解器套件（藏在 ② 的 blendshape_solver.cpp，仅 Windows 脚本调用）。基准自带 `InteractiveExecutorBundle` 聚合 struct——CUDA 流+双累积器+执行器四件套（audio2face 侧 interactive_executor.cpp:56-66、audio2emotion 侧 interactive_executor.cpp:35-45）。

## 外部连接

上游工具链：packman python（tools/packman/）、fetch_deps、CUDAToolkit≥12.8、TensorRT。外围脚本族（L02 层）：build.sh/build.bat 驱动 `_build/{config}` 下 Ninja 构建，gen_testdata.sh 生成三库测试/样例/基准数据。

## 数据流

开发流：`fetch_deps.sh` → configure（自动补拉）→ 12 个 Find 模块定位 → 三 core 静态库 → 伞形 audio2x.so/dll+头目录 → tests/benchmarks/samples。基准流：`test_benchmark.{bat,sh} <exe>` 循环喂 `--benchmark_filter`，filter 编码完整实验矩阵（FP16/UseGPU/Identity/NbTracks 等维度）。

## 设计决策

- **伞形单 so**：只链一个库拿到三 SDK 全部 API，静态库符号全隐藏——避免与宿主程序里其他 Eigen/TRT 符号冲突。
- **configure 期自动 fetch**：首次 cmake 即闭环，代价是 CMake 缓存 package 路径——根 CMakeLists 警告切 build type 要清目录（CMakeLists.txt:17-19）。
- **基准脚本平台差异**：audio2face 的 test_benchmark **.bat 12 条 vs .sh 9 条**（test_benchmark.bat:10-21 十二个 args；test_benchmark.sh:10-19 只九个）——Windows 独有的三条正是 blendshape 求解器套件 `BM_Solve/BM_CPUSolveAsync/BM_GPUSolveAsync`（test_benchmark.bat:24-26）；audio2emotion 版两平台一致各 3 条（test_benchmark.bat:10-13 / test_benchmark.sh:10-15）。
- **GLOB_RECURSE 收源**：core 加文件零 CMake 改动，代价是新文件不触发 re-configure。

## 新人提示

1. **坑：build.sh 参数解析是死代码**——build.sh:10-21 解析双参后，L29-35 无条件重置 BUILD_CONFIG=release（仅 $2 生效）、L39 又重置 BUILD_PROJECT="all"；`./build.sh debug` **静默构建 release**。build.bat:33-39 同病，用 $2 传配置才生效。
2. Linux 复现基准对比 Windows 数据时，.sh 少了 blendshape 三条，非数据缺失。
3. 给 core 加 .h/.cpp 后 CMake 没感知时，touch 任一 CMakeLists 或清 build 目录（GLOB 坑）。
4. "链接了却 undefined symbol"——先查是不是 internal 符号被 `--exclude-libs` 藏掉。
