# 视角2

> PMU 微架构计数器（IPC/cache/branch）
> 自动生成: 2026-06-30 13:34  机器: greatwall-pc / Phytium D3000

# Lens 2: PMU 微架构计数器

解读：IPC 高 → 单位 cycle 完成指令多（FPU 算力主导）
      cache 命中率高 → 数据复用好
      branch 准确率高 → 控制流可预测

| 算子 | GFLOPS | IPC | Cache 命中 | Branch 准确 | 单次 ms |
|---|---|---|---|---|---|
| GEMM MR=8 (compute) | 31.52 | 2.78 | 99.1% | 154500.0% | 68.13 |
| Elem-wise add (mem) | 6.31 | 1.47 | 93.3% | 3200.0% | 0.17 |
| Stream copy (pure mem) | 0.00 | 0.73 | 91.6% | 6000.0% | 0.67 |
| Reduction (dep chain) | 3.90 | 1.56 | 96.9% | 2200.0% | 0.27 |

## 关键洞察

- **GEMM MR=8** IPC 应该接近峰值（4-wide issue），cache 命中 >95%
- **Elem-wise** IPC 低（数据依赖 stall），cache 仍然命中（流式访问）
- **Reduction** branch 准确率影响最大（循环 + 末尾 reduction 依赖链）
- IPC 与 GFLOPS 的关系：IPC 高 ≠ 算力高（要看 instr 类型，FMLA vs LD/ST）

**工程启示**：
- 想 push 算力 → 关注 FMLA/SDOT instr 占比（compute density）
- 想 push 带宽 → 关注 cache 命中（数据布局 + prefetch）
- 想 push 单 thread → 关注 IPC + branch（指令调度 + 循环展开）
