# Capstone-C: 工作负载刻画报告

> 本报告由 `collect.py` 自动生成，所有数据来自 `driver.sh` 跑出的 `perf stat` 输出。

**生成时间**：2026-06-30 10:03:48  
**工作负载数**：9

---

## 1. 性能指标总览

| 工作负载 | Cycles (G) | Instr (G) | **IPC** | CPI | L1 Miss (M) | Miss Rate | Br Miss (M) | 耗时(s) |
|---------|-----------:|----------:|:-------:|----:|-----------:|----------:|------------:|---------:|
| `gemm_single_core` | 18.61 | 33.33 | **1.79** | 0.56 | 1310.5 | 9.35% | 8.66 | 8.13 |
| `zstd_random_L1` | 0.20 | 0.21 | **1.04** | 0.96 | 4.9 | 4.69% | 0.57 | 0.10 |
| `zstd_random_L19` | 56.36 | 22.94 | **0.41** | 2.46 | 453.2 | 3.87% | 130.50 | 23.41 |
| `zstd_random_L3` | 0.27 | 0.28 | **1.03** | 0.97 | 8.4 | 6.45% | 1.05 | 0.12 |
| `zstd_random_L9` | 0.53 | 0.52 | **0.97** | 1.04 | 13.9 | 6.86% | 0.19 | 0.23 |
| `zstd_text_L1` | 0.14 | 0.19 | **1.36** | 0.74 | 2.6 | 3.98% | 0.07 | 0.06 |
| `zstd_text_L19` | 0.62 | 1.20 | **1.93** | 0.52 | 5.9 | 1.51% | 0.19 | 0.25 |
| `zstd_text_L3` | 0.20 | 0.27 | **1.35** | 0.74 | 3.8 | 4.04% | 0.10 | 0.09 |
| `zstd_text_L9` | 0.45 | 0.88 | **1.94** | 0.51 | 4.5 | 1.78% | 0.12 | 0.19 |

## 2. IPC 可视化

```
workload                IPC  (max=1.94)
gemm_single_core       1.79  ████████████████████████████████████
zstd_random_L1         1.04  █████████████████████
zstd_random_L19        0.41  ████████
zstd_random_L3         1.03  █████████████████████
zstd_random_L9         0.97  ███████████████████
zstd_text_L1           1.36  ███████████████████████████
zstd_text_L19          1.93  ███████████████████████████████████████
zstd_text_L3           1.35  ███████████████████████████
zstd_text_L9           1.94  ████████████████████████████████████████
```

---

## 3. 自动分析

- **IPC 最高**：`zstd_text_L9` = 1.94（接近理论 4-wide 峰值 IPC=4 的 49%）。
- **IPC 最低**：`zstd_random_L19` = 0.41，瓶颈通常是访存或分支密集。
- **L1 miss 率整体健康**（最高 9.35%），工作负载具有良好的空间 / 时间局部性。
- **分支预测失败最多**：`zstd_random_L19` = 131M 次，建议重排分支（把 `if (rare) → else` 改为 likely/unlikely 提示）。

### 基于数据的 Top-Down 推断

| 工作负载 | 推测瓶颈 | 优化方向 |
|---------|---------|---------|
| `zstd_text_L9` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_text_L19` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `gemm_single_core` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_text_L1` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_text_L3` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_random_L1` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_random_L3` | 依赖链 / 局部 miss | 打破依赖链 / 算子融合 |
| `zstd_random_L9` | Backend / Frontend 混合 | 减小工作集 / 循环展开 |
| `zstd_random_L19` | Backend Bound（访存） | 数据预取 / 分块 / 大页 |

---

## 4. 优化建议（详细版见 [`recommendations.md`](./recommendations.md)）

- 见 [`recommendations.md`](./recommendations.md) 的 5 条具体可落地建议。
- 见 [`../alpha_21264_study/comparison.md`](../alpha_21264_study/comparison.md) 的微架构上下文对比。

## 5. 数据可重现性

```bash
# 重跑所有工作负载 + 重新生成本报告
cd Capstone/workload_characterization
./driver.sh            # 重新跑 + 写 data/
python3 collect.py 'data/*.perf' -o profile_report.md
```
