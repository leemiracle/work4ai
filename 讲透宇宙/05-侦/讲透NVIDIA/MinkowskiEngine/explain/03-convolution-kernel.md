# 03 · 卷积 kernel：kernel map 驱动的 gather-GEMM

> 涉及：`src/convolution_kernel.cu/.cuh`、`src/convolution_gpu.cu`、`MinkowskiEngine/MinkowskiConvolution.py`（634 行，普通/转置/生成式三族同居一文件）

## ① 角色定位

稀疏卷积的本质难题是"输出点在哪里、每个输出点聚哪些输入点"。MinkowskiEngine 的解法分两步：坐标侧由上一条线讲的 kernel map 给出 (kernel_id, in_row, out_row) 三列映射，特征侧本文件的 `ConvolutionForwardKernelGPU`（`src/convolution_kernel.cu:321`）只做一件事——**按映射把稀疏卷积降解为 gather + GEMM**。`MinkowskiConvolution.py` 则是 Python 侧的 autograd 壳：注意 `MinkowskiConvolutionTranspose.py` 并不存在，转置与生成式转置类（`MinkowskiConvolutionTransposeFunction` py:124、`MinkowskiConvolutionTranspose` py:454、`MinkowskiGenerativeConvolutionTranspose` py:539）全在本文件内。

## ② 内部结构

**Python 壳**：`MinkowskiConvolutionFunction.forward`（`MinkowskiEngine/MinkowskiConvolution.py:44`）在 py:71 经 `get_minkowski_function("ConvolutionForward", ...)` 拼名取 C++ 函数；backward 对称（py:98）。`MinkowskiConvolutionBase`（py:204）持 `is_transpose` 开关（py:227），三个 nn.Module 子类（py:360/454/539）只差权重形状与 kernel map 查询方向。

**输出坐标生成**（`src/convolution_gpu.cu`）：`ConvolutionForwardGPU` 先算输出图——`stride_tensor_stride`（cu:93）求输出 stride；`expand_coordinates` 为真走 `stride_region`（cu:107，核区域展开出新坐标），为假走 `stride`（cu:112，纯下采样丢弃坐标）；随后 `p_map_manager->kernel_map(...)`（cu:117）取映射。转置版本在 cu:203 对调 in/out 再查同一缓存。

**kernel 主体**（`src/convolution_kernel.cu`，声明在 cuh:39/53）：前向入口 cu:321 按 `check_direct_gemm_forward`（cu:46）二选一——Direct-GEMM 或 Copy-GEMM。Direct-GEMM 用手写 `matmul` kernel（cu:114-115 定义，签名吃 `in_map/out_map` 两个指针）：block 把 in_feat 块与 kernel 权重块装进共享内存，按行号索引做分块矩阵乘——**kernel map 在这里被当作 gather 索引数组消费**。共享内存块大小按通道数经验选择（cu:336-345：32/24/16 三档）。backward `ConvolutionBackwardKernelGPU`（cu:554）由 `check_direct_gemm_backward`（cu:78）同样分派，复用同一 kernel map 做梯度 scatter。

## ③ 外部连接

上游：kernel map 由 CoordinateMapManager 缓存供给（`src/convolution_gpu.cu:117/203`）；权重是 `MinkowskiConvolutionBase` 的 `nn.Parameter`。下游：`MinkowskiChannelwiseConvolution.py` 走纯 Python 聚合路线（批 3 甄别：kernel_map 聚合不走 C++ 后端，与 docstring 声明风格相左）；模板在 cu:499-540 按 float/double × default/c10 四组合显式实例化，挂到 pybind 注册面。

## ④ 数据流

一次 stride-2 前向：输入 SparseTensor（坐标图 A，stride 1）→ 输出 stride 算得 2 → `stride_region` 展开出图 B（核区域覆盖到的输出点）→ kernel_map(A→B, kernel) 返回三列映射 → `check_direct_gemm_forward(in_ch, out_ch, N)` 决定路线 → Direct-GEMM：`matmul` kernel 按 out_map 行分块，从 in_feat 经 in_map gather 装载共享内存，与权重块相乘累加 → 输出特征按 B 行序落盘，重包 SparseTensor（键=B）。反向以 grad_out 为输入沿同映射反向 scatter。

## ⑤ 设计决策

- **map 与算术分离**：不规则访存全部集中在映射数组一次性完成，GEMM 主体保持规则分块——稀疏性代价被压到 gather 层；
- **Direct-GEMM 启发式是魔数调参**（cu:46-67）：`sA==32 && sB==64 && N<=490537`、`N<=295625`、`N<=74556` 等阈值是特定卡型经验值，显式 `DIRECT_GEMM/COPY_GEMM` 模式可绕过自动选择；
- **转置复用**：转置卷积=交换 in/out 方向的同一映射（缓存键含 is_transpose），不写第二套 kernel；
- **COPY-GEMM 兜底**：通道组合不利时先 gather 成稠密矩阵再交给 cuBLAS，用额外拷贝换库级 GEMM 效率。

## ⑥ 新人提示

1. 找转置卷积类别开新文件——`MinkowskiConvolutionTranspose` 就在 `MinkowskiConvolution.py:454`；
2. `expand_coordinates` 的语义差：True=核区域展开（卷积/转置卷积），False=纯 stride 下采样（池化线），输出坐标集完全不同；
3. 改魔数阈值前先跑 `docs/benchmark.md` 的对照基准，那组数字没有理论推导只有实测；
4. 新增卷积变体三处对齐：`convolution_gpu.cu` 输出图逻辑、`extern.hpp` 注册名、Python `get_minkowski_function` 的字符串——拼错名要到运行时才炸。
