# Kernel-Lab 多视角分析汇总

生成时间: 2026-06-30 13:34

## 技术维度 lens（来自项目自身）

| Lens | 视角 | 文件 |
|---|---|---|
| `lens-roofline` | Roofline Model（compute/memory bound） | [`lens-roofline.md`](lens-roofline.md) |
| `lens-pmu` | PMU 微架构计数器（IPC/cache/branch） | [`lens-pmu.md`](lens-pmu.md) |
| `lens-thermal` | Thermal + DVFS（热设计） | [`lens-thermal.md`](lens-thermal.md) |
| `lens-precision` | 数值精度（FP16/INT8 误差分布） | [`lens-precision.md`](lens-precision.md) |
| `lens-latency` | 延迟分布 p50/p90/p99 | [`lens-latency.md`](lens-latency.md) |

## 专家角色 lens（来自多视角审查）

详见 [`docs/lenses/`](../../docs/lenses/) 目录：
- 性能架构师视角
- 首席算法科学家视角
- OS/Runtime 专家视角
- 编译器专家视角
- 硬件设计专家视角
- 应用集成工程师视角
- 安全/可靠性专家视角

---
每个 lens 独立可跑：```bash
make bin/lens-roofline && ./bin/lens-roofline
```
