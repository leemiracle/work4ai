# labs/ — 详细 Lab 导览

> 配套 [`学习路径.md`](../学习路径.md)（8 阶段总览），本目录是每个阶段的**代码级深入导览**。
> 每个 Lab 基于真实 `src/*.c` 代码，逐函数、逐行解释，含假设→实验→解释→陷阱→练习。

## Lab 索引

| Lab | 阶段 | 源文件 | 状态 | 核心知识点 |
|-----|------|--------|:--:|-----------|
| [Lab01](./Lab01_GEMM_FP32.md) | FP32 GEMM | `src/gemm_f32.c` | ✅ | MR/FVU/vfmaq_laneq 微内核/pack_B 布局 |
| [Lab02](./Lab02_数据类型.md) | INT8 + FP16 | `src/gemm_s8.c` `src/gemm_f16.c` | ✅ | UDOT 点积/反直觉陷阱/精度累加 |
| [Lab04](./Lab04_卷积.md) | Winograd | `src/conv_winograd_f44.c` | ✅ | F(4,3) 变换矩阵/换乘法/2D 推广 |
| [Lab05](./Lab05_Attention.md) | Flash Attention | `src/attention_neon.c` | ✅ | online softmax/分块/NEON 内积 |
| [Lab06](./Lab06_多核并行.md) | MC×NC 分块 | `src/multicore_tiled.c` | ✅ | flat vs tiled/L3 双段/OMP 盲区 |

> Lab03（自动调优）、Lab07（汇编）较简，见 [`学习路径.md`](../学习路径.md) 对应章节。

## 怎么读

1. 先读 [`学习路径.md`](../学习路径.md) 的对应阶段（看大图）
2. 再读本目录的详细 Lab（看代码）
3. 边读边跑：每个 Lab 都有"跑法"和"预期输出"
4. 做完练习题（每个 Lab 末尾）

## 前置条件

- 已读 [`项目宪法.md`](../项目宪法.md) §5（D3000 实测锚点）和 §7（实验纪律）
- 会用 `common/` 工具（见 [`common/README.md`](../common/README.md)）
- 能编译：`make gemm_f32 && ./bin/gemm_f32`
