# 05 · math_functions 双实现与 mkl_alternate：藏在死代码里的除法 bug

> 涉及：`src/math_functions_cpu.cpp`（108 行）、`src/math_functions_gpu.cu`、`src/math_functions.cuh`、`src/mkl_alternate.hpp`（62 行）、`src/pruning_gpu.cu`

## ① 角色定位

这一组文件是引擎的"ATen 底座"：逐元素运算与 BLAS 包装的 CPU/GPU 双实现，给 Broadcast、Pooling、Pruning 等算子提供最底层的算术原语。命名约定 `cpu_*/gpu_*` 对偶（如 `cpu_addition/gpu_addition`），上层入口用 `AT_DISPATCH_FLOATING_TYPES` 按 dtype 实例化。`mkl_alternate.hpp` 是无 MKL 环境的兼容层——本文同时钉版一个全仓最硬的源码级 bug：**`cpu_div<double>` 调的是 `vdMul`（乘法）**。

## ② 内部结构

**CPU 侧**（`src/math_functions_cpu.cpp`）：全部是模板显式特化。加法走 CBLAS：`cpu_axpy<float>` 调 `cblas_saxpy`（L97-100）；逐元素四则走 VSL：`cpu_mul<double>` 调 `vdMul`（L84）、`cpu_div<float>` 调 `vsDiv`（L89）——而 `cpu_div<double>`（L93-96）调的是 **`vdMul(n, a, b, y)`（L94）**，不是 `vdDiv`。无论链接真 MKL 还是无 MKL 构建，double 通道的"除法"执行的都是乘法；float 通道（vsDiv）正确。grep 全仓证实 `cpu_div` 零调用方——**真 bug 但处于死代码**，无测试覆盖所以存活至今（上游未修）。

**GPU 侧**（`src/math_functions_gpu.cu`）：手写 elementwise kernel——`addition_kernel`（L66）、`multiplication_kernel`（L72）、布局转置 `col2row_major_kernel`（L111）/`row2col_major_kernel`（L139）；GEMM 一律转 cuBLAS（`gpu_gemm` 声明于 `src/math_functions.cuh:37`）。声明/实现分工：`math_functions.cuh:43-47` 挂 gpu 侧原型，供各算子 `*_gpu.cu` 调用。

**mkl_alternate.hpp**：宏两段式代码生成——`DEFINE_VSL_BINARY_FUNC(name, operation)`（L42）展开出一个模板函数 `v##name` 与 `vs##name`/`vd##name` 两个内联包装；L56-59 四次实例化 Add/Sub/Mul/Div，每个操作 float+double 两版本共 8 个函数，全部是标量循环（如 Div 即 `y[i]=a[i]/b[i]`）。这层让 `math_functions_cpu.cpp` 可以无条件写 `vsDiv/vdMul/vdDiv` 而不必关心构建是否带 MKL。tree-sitter 对这种宏生成函数完全不可见（批 14 实证），也是本组文件在知识图谱里子节点偏少的原因。

**非常规一招**：`src/pruning_gpu.cu:36` 直接 `#include "pruning_cpu.cpp"`，把 CPU 实现编进 GPU 翻译单元共用其工具函数——跨文件边界但合法，读代码时别按"cu 不含 cpp"的直觉找定义。

## ③ 外部连接

上游消费者：`BroadcastForwardCPU/GPU`（Broadcast 算子的 ELEMENTWISE_ADDITION/MULTIPLICATION 两模式）与 `LocalPooling` 的归约/尺度变换；`col2row_major/row2col_major` 服务特征矩阵布局交换。注意 BroadcastMode 枚举只有加/乘两值（`pybind/extern.hpp:730-735`，且 `ELEMENTWISE_ADDITON` 是上游拼写笔误）——**除法根本不在广播面上**，这是 `cpu_div` 成为死代码的直接原因。下游依赖：cuBLAS/VSL/CBLAS 三套线性代数库。

## ④ 数据流

一次 Broadcast 加法（CPU）：Python `MinkowskiBroadcastFunction.forward` → C++ BroadcastForwardCPU → `cpu_addition<float>` → VSL `vsAdd`（MKL 构建为矢量内核，无 MKL 构建为 mkl_alternate 的标量循环）→ 回 torch tensor。GPU 路线：BroadcastForwardGPU → `gpu_addition<Dtype>` → `addition_kernel`（gpu.cu:66）以 N 线程一次访存完成。dtype 分派统一在算子入口的 `AT_DISPATCH_FLOATING_TYPES` 完成，kernel 模板只写一遍。

## ⑤ 设计决策

- **宏代码生成对齐 MKL API 面**：8 个函数用 4 行实例化顶掉一整套 `#ifdef INTEL_MKL` 分支——代价是宏展开体对静态分析与 tree-sitter 双重不可见；
- **CPU 走 BLAS 库调用而非手写循环**：MKL 矢量内核（vsAdd 等）在长数组上远快于标量循环，mkl_alternate 只是"能编译"的兜底而非性能路径；
- **`cpu_div` 的教训**：死代码不等于无害——一旦广播面扩出除法模式，L94 直接变成线上算错。修法一行：`vdMul`→`vdDiv`。

## ⑥ 新人提示

1. 改任何逐元素运算前先看 `math_functions.cuh` 的声明面与 `mkl_alternate.hpp:42` 的宏展开，否则 grep 函数定义会扑空；
2. 验证 bug：MKL 构建下跑 `cpu_div<double>(2, [1.0,4.0], [2.0,2.0])` 应得 [0.5,2.0]，实得 [2.0,8.0]（乘法）；
3. GPU 侧无除法 kernel——只有 add/mul/布局转置，除法需求要自己补；
4. 读 `pruning_gpu.cu` 记得跳到 `pruning_cpu.cpp`（L36 include），两个文件的边界是假的。
