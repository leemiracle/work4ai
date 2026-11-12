# LPLB 新人指南（简版）

> 依据仓库知识图谱（47 节点/7 层/12 步导览）与 README 整理。前置：《讲透EPLB》（本仓内嵌其算法）；姊妹篇：《讲透DualPipe》。

## 一、项目定位

LPLB（Linear-Programming-Based Load Balancer）是 DeepSeek 开源的**线性规划动态负载均衡器**（早期研究阶段）：EPLB 只修静态不均衡，LPLB 针对**每 batch 内**小 batch 随机性造成的动态波动——把冗余专家连成边、边容量=该副本本 batch 的 token 数，在 GPU 图上求 LP 最优 token 分流，最小化 EP 组内负载不均。

求解器是亮点：**单 SM 内点法（IPM）**跑在 GPU 上（cuSolverDx/cuBLASDx），节点间负载同步走 NVSHMEM 而非 `torch.distributed.allreduce`，可与 DeepEP 共享通信。家族定位：EPLB 静态重排 + LPLB LP 动态 + DualPipe 流水线重叠，配合 DeepEP/3FS 构成 DeepSeek 训推基础设施。

## 二、架构分层

知识图谱 7 层，Python 薄壳 + C++/CUDA 重核：

1. **包入口层**：`lplb/__init__.py` 只导出 `Planner`。
2. **规划器层**：`lplb/planner.py`——总调度。
3. **静态重排层**：`lplb/eplb.py`——EPLB 算法内嵌副本（reordering-only，不复制）。
4. **C++ 扩展层**：`csrc/plugin.cpp`——JIT 编译、NVSHMEM/CUDA IPC 通信。
5. **CUDA 求解内核层**：`lplb/resources/csrc-tmpl/minilp.cu`——IPM 模板 + 计数/重定向内核。
6. **测试与基准层**：`tests/`、`scripts/`。
7. **文档与构建层**：README、setup.py。

## 三、核心模块

- **Planner（总调度）**：`run()` 串起 count_workload → solve_probs → weighted_select_target，返回改写后的物理专家索引；`update_redundancy_mapping` 调内嵌 `rebalance_experts` 做静态重排；`init_from_deep_ep(buffer)` 复用 DeepEP 通信；`_get_solver` 按拓扑参数 lru_cache 复用求解器。
- **csrc/plugin.cpp**：读 minilp.cu 按拓扑宏实例化，NVRTC+nvJitLink 编译得 cubin（哈希落盘缓存）；`init_comm` 引导 NVSHMEM、打通 DeepEP（`deepep_rt_slim.h`）；暴露 `solve/count_idx/map_idx` 三入口。
- **minilp.cu（算法心脏）**：`kernel_solve` 先 NVSHMEM 负载 allreduce，再在共享内存构造 KKT 系统迭代内点求解（cuBLASDx GEMM + cuSolverDx Cholesky）；`kernel_count_idx` 按物理专家计数；`kernel_map_idx` 按求解概率重定向路由索引。
- **典型拓扑**（改 `r2o` 可自定义）：**Cube**（8 GPU 带对角边）、**Hypercube**（16 GPU 无对角边）、**Torus**（跨节点邻居，全局均衡但通信较贵）。

## 四、快速上手

前提：CUDA Toolkit ≥ 12.6.3；DeepEP 可选但强烈推荐。

```bash
./download-mathdx.sh        # 拉取 MathDx 头文件
pip install --no-build-isolation --editable .
pytest tests
```

使用范式：构造 `r2o` 拓扑 → `Planner(r2o, n_physical, n_logical, group=ep_group)` →（可选）`init_from_deep_ep(buffer)` → 每 batch `planner.run(indices, avail_counter, N_SMS)` 拿到重定向的物理专家索引。

## 五、学习路径

1. 读 README 的 "How LPLB Works"（成边→边容量→LP 分流）与三条 Limitations（只平衡 token 数、求解 ~100µs、极端不均衡时可能不如 EPLB）。
2. 补 EPLB 背景（`lplb/eplb.py` 即其内嵌副本）。
3. 精读 `planner.py`，跑 `tests/` 与 `scripts/run_ep16_cube8p2e.py` 基准。
4. 下钻 `csrc/plugin.cpp` 的 JIT 编译链路，最后啃 `minilp.cu` 的单 SM 内点法——需 CUDA 共享内存与 KKT 背景。
