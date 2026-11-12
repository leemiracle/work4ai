# 05 · vendored Boost 基座与构建系统

## 角色定位

`src/boost/` 1201 个文件占了全仓 1301 个分析文件的 92%，但真实消费点只有 `src/PictureSequenceImpl.h:3-4` 两个 include（variant + mp11）。这坨体积的由来写在 pImpl 注释里：安装方头文件必须干净，于是 Boost 被整个塞进 `src/` 私有编译（`include/PictureSequence.h:555-558`）。构建系统则负责三件事：探测 FFmpeg 两代 API、编 CUDA 三型 kernel、在 nvidia-docker "构建期没有驱动库"的世界里把库链出来。

## 内部结构

Boost 五域构成：mpl 759 文件（编译期序列/算法/lambda 元函数库，占全仓 58%）+ preprocessor 140（宏原语，mpl 骨架的生成底座）+ config 82（编译器探测）+ type_traits 70 + variant 36；另有 mp11/move/bind/core 等支撑件 60 个。真正被走到的高频路径只有 variant 的核心机制：`src/boost/variant/variant.hpp`（2583 行）用 placement new + 无类型 `storage_` 原始存储 + `which_` 索引实现无标签开销联合（成员声明 `:1429-1430`，`#include <new>` 注释 `:19`），访问经 `visitation_impl` 按 which 分派（`:2448-2452`，`:33` 引入）；NVVL 侧的容器类型由 mp11 一行拼出（`src/PictureSequenceImpl.h:190-194`）。

## 外部连接

构建侧主文件 `CMakeLists.txt`：要求 CMake 3.8（内置 CUDA 语言，`CMakeLists.txt:1`）、`project(NVVL VERSION 1.0 LANGUAGES C CXX CUDA)`（`:7`）、pkg-config 循环找 avformat/avcodec/avfilter/avutil（`:17-22`）、九个源文件编一个 SHARED 库（`:32-42`）、链 `${FFmpeg_LIBS} cuda nvcuvid nvidia-ml`（`:73`）。三个辅助模块：`cmake/CudaArchFlags.cmake`（世代名翻 sm_##，`:26-32`，默认 Maxwell+Pascal+Volta）、`cmake/BuildType.cmake`（无 CMAKE_BUILD_TYPE 时兜底）、`cmake/NVVLConfig.cmake.in`（配 `CMakeLists.txt:106-108` 生成 find_package 入口）。文档 `doc/Doxyfile.in`（1519 行）与 `doc/examples/CMakeLists.txt` 都以 EXCLUDE_FROM_ALL 挂载（`CMakeLists.txt:124-125`）。

## 数据流

**FFmpeg 版本探测流**：`check_struct_has_member("struct AVStream" codecpar ...)` 与 `check_type_size("AVBSFContext")` 在 configure 期探测（`CMakeLists.txt:26-28`），结果转成 `HAVE_AVSTREAM_CODECPAR=1/HAVE_AVBSFCONTEXT=1`（`:51-57`）；编译期 `src/detail/Decoder.h:8-14` 用前者把 `CodecParameters` 别名到 AVCodecParameters 或旧 AVCodecContext，`src/VideoLoader.cpp:66-74` 的 `codecpar()` 与 `:101-107,284-311` 的双路 BSF 跟随同一宏——一份源码吃 FFmpeg 3.x/4.x 两代。**CUDA 编译流**：`CUDA_SEPARABLE_COMPILATION ON` + PIC（`CMakeLists.txt:59-63`）配默认 `-cudart shared`（`:3-5`），imgproc.cu 三型模板实例化（`src/detail/cuda/imgproc.cu:147-160`）在此落成。**链接流**（容器侧）：build 镜像源码编最小 FFmpeg（只开 file 协议+mov/matroska demuxer+两 bsf，`docker/Dockerfile.build:18-30`）；`NVIDIA_DRIVER_CAPABILITIES=video,compute,utility` 声明视频驱动注入（`:10`，minimal 镜像同款 `docker/Dockerfile.minimal:8`）；开发链接靠双路径 `ln -s` 伪装（`:52-53`）；示例工程更进一步——`make-stub.sh:13-18` 用 `nm -D` 抽符号清单生成全部返回 `CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND` 的空壳（`examples/pytorch_superres/docker/make-stub.sh:16`），strip 后以 ELF 二进制入库（`libnvcuvid.so`，file 实证 stripped），COPY 进 stubs 目录过链接期（`examples/pytorch_superres/docker/Dockerfile:46-47`）。

## 设计决策

(1) **vendoring 而非找 Boost**：2018 年发行版 Boost 版本参差，NVVL 只需 variant+mp11 两个 header-only 件——直接内嵌换取"克隆即编译"，代价是仓库膨胀 92% 与审计面扩大。(2) **探测结果转宏而非版本号判断**：`check_struct_has_member` 探测"成员是否存在"这一事实，比解析版本号稳健（发行版 backport 常让版本号说谎）。(3) **桩库分两级**：ln -s 软链（运行时有真库的 build 镜像）与 ELF 桩（构建期连运行时都没有，链接期只看符号名）按容器形态分别部署，注释还预言"future CUDA versions 会消除该需求"。(4) **EXCLUDE_FROM_ALL 挂载 doc/examples**：默认 `make` 不编，`make doc`/`make examples` 显式触发（`CMakeLists.txt:124-125`）。

## 新人提示

快读请把 `src/boost/` 整棵从 IDE 排除，深挖入口只需 variant.hpp 的 6 个行号锚（`:19,33,1429-1430,2448-2452`）。构建 `mkdir build && cd build && cmake .. && make -j`（`README.md:101-108`）；`CUDA_ARCH` 可传 `Kepler` 或 `sm_61`（`README.md:114-118`，映射表 `cmake/CudaArchFlags.cmake:26-32`）。复用"探测转宏"的样板在 `CMakeLists.txt:26-28`；复用桩库技法直接抄 `examples/pytorch_superres/docker/make-stub.sh:4-20`（找版本库→nm 抽符号→gcc -shared -nostdlib→strip）。审计提醒：入库的 libnvcuvid.so 是 stripped ELF 制品，供应链扫描应剔除重建。
