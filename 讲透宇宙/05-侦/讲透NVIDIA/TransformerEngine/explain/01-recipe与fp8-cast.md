# 01 · recipe.h 与 cast/——量化配方与类型转换核

> 源文件：`transformer_engine/common/include/transformer_engine/recipe.h`（456 行）+ `transformer_engine/common/recipe/`（5 个 .cu 共 2288 行）+ `transformer_engine/common/cast/`（六子目录）。图谱将这一族标注为框架无关公共层核心节点群——五种 scaling 语义的 C API 全在此声明，双前端共享同一实现。

## ① 角色定位：这个子系统解决什么问题

FP8/NVFP4 动态范围远小于 FP32/BF16，每个张量（或块/行）必须配缩放因子。**scale 何时算、什么粒度、用多旧的统计量，就是"配方"（recipe）**。TE 在此定义五种 scaling 语义：delayed（历史 amax）、current（本步现算）、blockwise 2D（128×128 块）、mxfp8（32 元素块，OCP MX）、nvfp4（16 元素块+全局二级 scale）。`cast/` 是执行者：按配方 quantize/dequantize 并顺带产出 amax。上层 Linear/Attention/MoE 的量化最终都落到这里的 C API。

## ② 内部结构：关键类/函数与行号锚

**C API（`recipe.h`）**：`nvte_delayed_scaling_recipe_amax_and_scale_update`（`recipe.h:41`）约定 delayed 语义——amax 历史左旋一格、首位置零，scale 按 `2^{-margin}·max_fp8` 估计。`nvte_fp8_block_scaling_compute_partial_amax`（`recipe.h:198`）与 mxfp8 版（:298）docstring 各画 ASCII 分块图：partial 只对本 rank 展平片段 `[start_offset, +len)` 算块 amax，不重叠块置 0——为切分后局部统计再归约准备。`nvte_nvfp4_compute_per_block_scale`（`recipe.h:412`）给出双级公式 `global_scale = 448×6/global_amax`。

**delayed（`recipe/delayed_scaling.cu`）**：`fp8_dtype_max`（:32）钉死 E4M3=448、E5M2=57344，`scaled_max = fp8_dtype_max·2^{-margin}`（:300）。kernel（:84）grid=num_scales，原地滚动历史靠 `__syncthreads()` 防竞态（:108），MOST_RECENT 取历史首项、MAX 走 shared memory 树归约；scale 更新（:138）在 amax 过小致 inf 时钳 FP32_MAX；bulk 版（:162）把多张量参数塞 `__constant__` 内存（:60-66）。

**current（`recipe/current_scaling.cu`）**：`zero_amax_kernel`（:24）先查 `noop_ptr[0]==1.0f` 即返回——noop 张量是 CUDA Graph 重放"跳过本步"的逃生门（:165 提取）；`nvte_compute_scale_from_amax`（:281）做设备端 scale 推断。



**cast 执行器**：`nvte_quantize`（`cast/cast.cu:26`）是薄壳，分流在 `dispatch/quantize.cuh:72` 的 scaling_mode switch：delayed（:73）→`fp8::quantize` 或 cast_transpose；mxfp8（:94）先试 CuTeDSL 后备原生核；nvfp4（:113）按 row_scaled/4over6/2D 选路径；blockwise 2D（:190）走 square_blockwise 核。sm100 主力核是 TMA 风格的 `cast_fp8_2D_kernel`（`cast/fp8/quantize_fp8.cuh:58`）。

## ③ 外部连接：与哪些子系统互依

向上是 common C API 边界，PyTorch 与 JAX 绑定各自包装 `nvte_*`（"一套内核双前端"主线）。向内依赖 `transpose/cast_transpose.h`（量化+转置融合）；swizzle（`swizzle/swizzle.cu:20` 定义 MXFP8 块=32、NVFP4 块=16）满足 cuBLAS 的 swizzled scale 布局，由 `with_gemm_swizzled_scales` 开关触发（`dispatch/quantize.cuh:172`）。hadamard_transform 的 cast 融合变体（04 篇）复用同一约定。

## ④ 数据流：一次典型调用的路径

delayed 训练一步：①上一步 cast 已把 amax 写进历史首位；②本步 `Float8Tensor.quantize_()` 经绑定调 `nvte_quantize`（`cast.cu:26`）→`quantize_fwd_helper`（`dispatch/quantize.cuh:36`）→delayed 分支完成 FP8 转换并更新 amax；③recipe 更新调 `recipe.h:41` 的 API，kernel（`delayed_scaling.cu:84`）滚历史归约新 amax，`scaled_max/amax` 产出下一步 scale。其余四种语义把②③并进同核，多卡走 partial 归约（`fp8_block_scaling.cu:225`）。

## ⑤ 设计决策：为什么这么设计

**delayed/current 分家**：delayed 用历史 amax，scale 在 GEMM 前已知，代价是突增激活溢出——所以有 margin 与左旋；current 每步现算精度好，但需设备端推断接口。**partial amax 展平 offset 协议**：一个 kernel 服务 TP 列切/DP 行切/任意片段，块坐标由四参还原。**NVFP4 二级 scale**：FP4 仅 2 位指数，单级块 scale 盖不住全局范围；2688 全局 scale 把块 scale 压进 E4M3。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`recipe.h` 全文→`dispatch/quantize.cuh:72` 的 switch（量化路径总地图）→`delayed_scaling.cu`。
- **坑一：scaling_mode 决定一切**。同一 `nvte_quantize_v2`（`cast.cu:39`），mode 不同走的核完全不同。
- **坑二：noop 语义**。CUDA Graph 须传 `nvte_quantize_noop`（`cast.cu:33`），否则 amax 每步被清零（`current_scaling.cu:24`）。
- **坑三：NVFP4 路径矩阵**。四开关组合合法性靠 NVTE_CHECK 守门（`dispatch/quantize.cuh:118`），报错即文档。
