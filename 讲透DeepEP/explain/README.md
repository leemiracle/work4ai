# 讲透DeepEP · 重要文件精讲索引

基于仓库 `~/ai/explore/deepseek-ai/DeepEP` 的源码精读，按知识图谱 tour 主线（Python 门面 → V2 宿主 → JIT 运行时 → 设备内核）挑选 4 个核心文件，V1/V2 双线均覆盖。所有 API 与行为描述均以真实源码为准。

| # | 精讲文件 | 原文件路径 | 层次 | 一句话定位 |
|---|---------|-----------|------|-----------|
| 1 | [01-deep_ep-buffers-legacy.py.md](01-deep_ep-buffers-legacy.py.md) | `deep_ep/buffers/legacy.py` | V1 Python 门面 | Buffer：NVLink/RDMA/低延迟三模式 + NVSHMEM 引导 |
| 2 | [02-deep_ep-buffers-elastic.py.md](02-deep_ep-buffers-elastic.py.md) | `deep_ep/buffers/elastic.py` | V2 Python 门面 | ElasticBuffer + EPHandle：NCCL Gin 底座与四类通信 |
| 3 | [03-csrc-jit-handle.hpp.md](03-csrc-jit-handle.hpp.md) | `csrc/jit/handle.hpp` | JIT 运行时 | cubin 加载与内核发射的 driver/runtime 双路径胶水 |
| 4 | [04-deep_ep-impls-dispatch.cuh.md](04-deep_ep-impls-dispatch.cuh.md) | `deep_ep/include/deep_ep/impls/dispatch.cuh` | V2 设备内核 | dispatch 单跳模板：notify+发送两阶段 all-to-all |

## 阅读路线

- **快速入门**：按 1→2 的顺序理解两代 API 的差异（NVSHMEM vs NCCL 对称内存），再读 3→4 下探执行层。
- **V2 使用者**：重点读 2（ElasticBuffer/EPHandle 语义、SM/QP 自动决策、deterministic 模式）。
- **内核/通信开发者**：重点读 4（Gin 原语、TMA/mbarrier 握手、64 位打包归约），横向对照 `hybrid_dispatch.cuh`/`combine.cuh`。

## 每篇结构

六节固定结构：①角色定位 ②内部结构 ③外部连接 ④数据流走读 ⑤设计决策 ⑥新人提示。
