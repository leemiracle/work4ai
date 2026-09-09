# 讲透 TileKernels — explain 精讲索引

TileKernels 是 DeepSeek 系 LLM 算子的 TileLang 高性能实现库，六大域（Gating/MoE Routing/Quantization/Transpose/Engram/MHC）各自成子包。本目录收录 4 篇重要文件精讲：3 篇选自知识图谱 tour 前 4 步（核心 MoE 门控内核 / SM 配置基建 / 基准回归插件），1 篇补全仓最大内核（Engram 门控，覆盖 Engram 域）。

## 精讲目录

| # | 文件 | 行数 | 主题 | 链接 |
|---|------|------|------|------|
| 1 | `tile_kernels/moe/top2_sum_gate_kernel.py` | 424 | 仓库最核心单内核：warp-per-token 完成 top2-sum 分组路由全链路（四评分函数/组选择/top-k 稳定排序/物理专家映射/ETP 掩码），TileLang JIT 编译期特化的样板 | [01-moe-top2_sum_gate_kernel.md](01-moe-top2_sum_gate_kernel.md) |
| 2 | `tile_kernels/config.py` | 29 | SM 配置中心：lru_cache 设备属性查询、set_num_sms 全局限额、被 10 个内核文件消费、SM 数作为 JIT 工厂参数参与代码生成 | [02-config.py-SM配置中心.md](02-config.py-SM配置中心.md) |
| 3 | `tests/pytest_benchmark_plugin.py` | 477 | 基准回归插件：--run-benchmark 门控、CUPTI 计时 fixture、JSONL 基线比对（阈值 15% 双向）、回归即 exit 1、xdist worker 绑卡与显存配额 | [03-pytest_benchmark_plugin.py-基准回归插件.md](03-pytest_benchmark_plugin.py-基准回归插件.md) |
| 4 | `tile_kernels/engram/engram_gate_kernel.py` | 570 | 仓最大内核（Engram 记忆门控 fwd/bwd）：持久内核 + cp.async 双 bank 软件流水、smem 复用（k→v 换角色）、梯度两级归约 + main_grad 支持 | [04-engram_gate_kernel.py-记忆门控内核.md](04-engram_gate_kernel.py-记忆门控内核.md) |

## 核心模式速览

- **TileLang JIT 模式**：内核工厂（`@tilelang.jit` + `@T.prim_func`）把形状/评分类型/可选输入编译期特化，`T.dynamic` 只留 batch 维；`pass_configs` 显式关闭 warp specialization 等编译 pass 换性能；`TK_PRINT_KERNEL_SOURCE=1` 随时查看生成的 CUDA 源码。
- **warp 级算法库**：shfl_xor 蝶形归约、逐轮找 max 的稳定 top-k、平局取小索引——路由内核全程单 warp 一 token，免 shared 同步。
- **持久内核 + 资源配额**：`config.get_num_sms` 决定 persistent blocks，token 循环在内核内跑，cp.async 流水跨 token 延续；占用估算用 `get_max_smem_per_sm` + 寄存器压力帽。
- **性能即测试**：基准不是脚本是 pytest 插件，基线 JSONL 进版本控制，回归拖垮 CI——"慢了"和"错了"同权重。

## 建议阅读顺序

先读 2（29 行读懂全仓资源契约）→ 1（核心内核，warp 算法密集）→ 4（进阶：流水线与反向设计）→ 3（工程化收尾：性能如何被守护）。每篇开头标注原文件相对路径与行数，六节结构，全部基于真实源码，无臆造 API。

*生成：2026-09-05，基于仓库知识图谱（503 节点/12 步 tour）挑选。*
