# 讲透 NVIDIA NPPDx

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NPPDx` @ commit `e7efdc12`
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（9 批/169 文件） | ✅ 9/9 | 终验通过；scanner 对 C++ 模板头 tree-sitter 全零提取 + batchImportData 全空（盲区全谱复现），**464 条 imports 全部源码手扫 + 逐条磁盘验证**（C/C++ 钉版补偿的极端案例） |
| understand 图谱 | ✅ 完成 | **547 节点 / 1151 边 / 14 层 / 14 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **169 文件 @ e7efdc12**（六仓中最大图谱） |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 7804 不计空格字符 / 30 锚 / 3 勘误；1308 团灭后 SendMessage 复活续写） |
| explain 精讲 | ✅ 3/3 | `explain/01-03`，六节结构、行号锚源码核实 |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 字数（不计空格）/锚 |
|---|---|---|---|
| 01 | nppdx.hpp 伞头 | 双层伞结构 + 入口值类型层 | 4886 / 49 |
| 02 | 表达式/算子 DSL | commondx 标签树→算子词汇表→op_impl 特化族 | 4955 / 53 |
| 03 | resize + 示例 | 有理数重采样全链 + 04_resize 双示例互证 | 4599 / 68 |

## 勘误与甄别（源码一手核实）

1. **commondx 姐妹库 include 易被当外部依赖漏边**：`include/commondx/` 前缀的 include 是仓内代码（约 33 条边），scanner 视为外部——NPPDx 手扫补偿的关键发现。
2. **numeric_traits.hpp 隐式依赖陷阱**：仅含 cstdint 垫片却依赖 complex_types.hpp 定义的 `COMMONDX_DETAIL_CUDA_FP8_ENABLED` 宏，单独包含时 FP8 分支静默失效。
3. **sm.hpp 含 CUDA 13 架构改名一手守卫**：static_assert 原文 "In CUDA 13 sm_101 (Thor) was renamed to sm_110"（1010↔1100 互斥 + CUDA_VERSION 阈值）。
4. **sm_75 文档 vs sm_70 代码**、`#error` 串尾多余 `");"`、CUDA 13.0 要求 vs NVRTC 12.0 检测——onboard 期核实（见 ONBOARDING 第 7 节）。
5. **formats.hpp:437 编译门控引入 formats_compat**（宏条件 include，scanner 盲区）；`formats_compat` 禁止直接 include（注释明示）。
6. **v210/uyvp 的 bytes_per_pixel 是整数近似**，不可用于 stride 计算（onboard 勘误）。
7. **模板特化族按同名合并**：format_backend 特化、Nchoose3 宏生成 10 组行加载器→1 家族节点（图谱粒度约定，计数时勿按特化数）。explain 期精确口径：**21 个 `format_backend<packing_format::X>` 特化分布在 `detail/backend/formats_impl/` 7 个族文件**，不在 function_operation_implementation.hpp。
7b. **`include/nppdx/resize.hpp` 不存在**：resize 实现在 `detail/backend/resize_operations.hpp` + `resize_geometry.hpp` + `function_operation_implementation.hpp:498-655`（explain 03 勘误节）。
7c. **`example/nppdx/04_resize/resize_example.cu:58` 注释与代码相反**："2x Upscale" 实际 j=2/k=1 是 2x downscale。
8. **median_operations.hpp 头部 CE 成本学设计墙注释**（N9L19D7 最优网络/IET 对比）——设计文档藏在代码注释里。
9. **is/get_operator_fd 是打破 operators↔traits 循环依赖的前置声明头**。
10. **`cow_312x376.rgb24` 是二进制像素数据**（测试样本，非代码）。

## 一句话

C++20 header-only CUDA 数据前处理库：表达式 DSL + 格式系统 + 滤波族三层抽象，169 文件全模板头——tree-sitter 全盲的极端案例，图谱边几乎全部来自人工 #include 手扫。
