# 讲透LPLB — 重要文件精讲索引

LPLB（Linear Programming Load Balancer）用线性规划做 MoE 专家并行的动态负载均衡：冗余专家成边、边容量为副本 token 数、LP 最小化组内不均衡。本目录收录 3 篇精讲，覆盖 Python 调度 → C++ JIT → CUDA 求解内核的完整纵切面。

## 精讲列表

| 篇目 | 原文件 | 一句话定位 |
|---|---|---|
| [01-planner.md](01-planner.md) | `lplb/planner.py` | Python 总调度：r2o/o2r 拓扑代数、静态 EPLB 重排 + 动态 LP 分流 |
| [02-plugin-cpp.md](02-plugin-cpp.md) | `csrc/plugin.cpp` | JIT 编译链路：NVRTC+nvJitLink LTO、内容寻址缓存、NVSHMEM/IPC 双级通信 |
| [03-minilp-cu.md](03-minilp-cu.md) | `lplb/resources/csrc-tmpl/minilp.cu` | 单 SM 内点法内核：cuSolverDx/cuBLASDx 块级原语、affine scaling 5 步迭代 |

## 建议阅读顺序

1. **01-planner.py**：自顶向下，先懂四张映射表（r2o/o2r/phy2log/log2phy）与三步 run 流程。
2. **03-minilp.cu**：再入数学核心，手推小规模 LP 后读 kernel_solve 五段式。
3. **02-plugin.cpp**：最后看工程粘合层——为什么 JIT、怎么缓存、怎么在 kernel 内做两级 allreduce。

## 一图流（调用链）

```
Planner.run(idx)
  ├─ count_workload  → CompiledSolver.count_idx → kernel_count_idx（SM 分片直方图+前缀）
  ├─ solve_probs     → CompiledSolver.solve     → kernel_solve（单 block IPM，NVSHMEM 全局聚合）
  └─ weighted_select_target → CompiledSolver.map_idx → kernel_map_idx（期望计数+伪散列重定向）
```

## 配套资料

- [onboarding/ONBOARDING.md](../onboarding/ONBOARDING.md) — 项目全貌入门
- 上游仓库：~/ai/explore/deepseek-ai/LPLB
- 姊妹项目：EPLB（静态冗余重排，LPLB 内嵌其副本于 lplb/eplb.py）
