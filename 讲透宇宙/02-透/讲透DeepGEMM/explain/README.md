# 讲透DeepGEMM · 重要文件精讲索引

基于仓库 `~/ai/explore/deepseek-ai/DeepGEMM`（v2.6.1）的源码精读，按知识图谱 tour 主线（API 层 → JIT 框架 → 启发式 → 设备内核）挑选 4 个核心文件。所有 API 与行为描述均以真实源码为准。

| # | 精讲文件 | 原文件路径 | 层次 | 一句话定位 |
|---|---------|-----------|------|-----------|
| 1 | [01-csrc-apis-gemm.hpp.md](01-csrc-apis-gemm.hpp.md) | `csrc/apis/gemm.hpp` | C++ API 层 | 全部 GEMM 算子的 pybind 注册与校验分发总入口 |
| 2 | [02-csrc-jit-compiler.hpp.md](02-csrc-jit-compiler.hpp.md) | `csrc/jit/compiler.hpp` | JIT 编译层 | NVCC/NVRTC 双后端运行时编译器与分布式安全缓存 |
| 3 | [03-csrc-jit_kernels-heuristics-sm90.hpp.md](03-csrc-jit_kernels-heuristics-sm90.hpp.md) | `csrc/jit_kernels/heuristics/sm90.hpp` | 启发式层 | 形状 → tile/流水参数的枚举 + 解析成本模型 |
| 4 | [04-deep_gemm-impls-sm90_fp8_gemm_1d2d.cuh.md](04-deep_gemm-impls-sm90_fp8_gemm_1d2d.cuh.md) | `deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d2d.cuh` | 设备内核层 | SM90 FP8 1D2D 主力内核：TMA+WGMMA+缩放后置 |

## 阅读路线

- **快速入门**：按 1→2→3→4 顺序读，即"用户可见 API → 内核怎么编译出来 → 参数怎么选 → 内核怎么算"的完整链路。
- **性能调优**：优先读 3（heuristics）与 2（JIT 环境变量），配合 `DG_JIT_DUMP_SASS` 观察产物。
- **内核开发**：直接读 4，再横向对照 `sm90_fp8_gemm_1d1d.cuh` 与 `sm100_*` 系列。

## 每篇结构

六节固定结构：①角色定位 ②内部结构 ③外部连接 ④数据流走读 ⑤设计决策 ⑥新人提示。
