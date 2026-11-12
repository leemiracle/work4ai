# 08 · MathDx 枢纽链：宿主库的设备端对偶

## 角色定位

MathDx 是 L11 层最大子域之一（249 节点），把 cuBLAS/cuFFT/cuRAND/cuSOLVER/nvCOMP 五个宿主库"对偶"成单文件头库族 cuBLASDx/cuFFTDx/cuRANDDx/cuSolverDx/nvCOMPDx——算子直接在 kernel 内联执行（`fft::execute` 于线程块级），无 handle/plan 概念。`libmathdx` 则是其 JIT 运行时封装（C-API），README 明言它是 Warp 与 nvmath-python 的后端。图谱把六个子域的 common 头识别为枢纽链：cuFFTDx common 十头 1879 行、cuSolverDx common 十七头 3740 行，占本域提取量的大头。

## 内部结构

三层枢纽：cuFFTDx `common/common.hpp:308-309` 的 `sm_runner<Functor>` 以**模板模板参数**按 SM 架分发（`template<template<unsigned int> class Functor>`）；`block_io.hpp` 的 `example::__io` 命名空间（:25-27）做 half2 RRII/RIRI 布局特化，`io<FFT>`（:42 起）提供 load/store 静态接口，:59-70 的 `input_batch_offset` 处理 half 精度**隐式双批**（一个 complex<half2> 实含两批）；cuSolverDx common 另有 12 个 `cusolver_reference_*.hpp` 宿主参考实现族做对拍。libmathdx 十四个 .cpp 每个演示一个 C-API 面（cufftdx.cpp/cublasdx_pipeline.cpp 等），cufftdx.cpp:20-22 同时 include `libcufftdx.h`+`nvJitLink.h`+`nvrtc.h`——JIT 三角。

## 外部连接

NVRTC 枢纽是跨子域复用的关键件：cuBLASDx `15_nvrtc/common_nvrtc.hpp` 双层命名空间 `example::nvrtc`（:69-70）与 `example::nvjitlink`（:223），两边各有一个 `get_device_architecture_option`（:204 与 :224-225）——:222 注释点破差异："nvJitLink uses `-arch=sm_XX`, while NVRTC uses `--gpu-architecture=sm_XX`"。cuFFTDx 的 09_introduction_lto_example 用另一条构建路：CMakeLists.txt 逐 arch `foreach`（:26）后调 `run_cufft_lto_helper`（:34）按 `introduction_lto_cases.csv` 生成并链接 LTO blob——"CMake 运行期读 CSV 生成目标"是本仓 LTO 示例的标准做法。

## 数据流

以 cuFFTDx 入门示例为骨架：宿主定义 FFT 描述符类型（Dim/Type/Threads 编译期参数）→kernel 内 `fft<...>::execute` 就地变换→宿主对拍。libmathdx 路线则是：源码字符串→NVRTC 编译（带 arch 探测选项）→nvJitLink 链接→cuModuleLoad→执行。cuRANDDx 仅三个示例（introduction/thread_api/nvrtc），是六族中最薄的一支；nvCOMPDx 覆盖 LZ4/ANS 的 GPU/CPU 四种组合（05 号示例把 NVRTC 与 CPU 解码叠加）。

## 设计决策

设备端库的代价转移是核心权衡：换来零 launch 开销与融合自由，付出"全部类型在编译期定死"——所以示例矩阵按精度（fp16/mixed）、布局（padded/strided）、后端（nvcc/NVRTC/LTO）正交展开，07_convolution_3d 的支撑头模板参数达九个（Dim/Front/Batches+三对 FFT&IFFT 类型）。这也是 tree-sitter 的重灾区：namespace 内模板类全盲（07 号支撑头、block_io 全靠手工补），图谱 232 个 .cu 函数节点中 MathDx 独占 232——补扫量全仓第一。libmathdx 要求 CMake 3.31+/CUDA 13.x（README Requirements），与示例域的 12.x 基线并存。

## 新人提示

从 `00_introduction_example` 入手认描述符；改示例先看各子域 README 的编号清单（cuFFTDx 00-10 有教学次序）；跑 LTO 示例读 README_LTO.md 而非主 README。NVRTC 示例失败先查 arch 选项两套拼法是否用错命名空间——`-arch=` 与 `--gpu-architecture=` 互不通用。cuSolverDx 参考值都在 common 的 cusolver_reference_* 里，不用另装宿主 LAPACK。
