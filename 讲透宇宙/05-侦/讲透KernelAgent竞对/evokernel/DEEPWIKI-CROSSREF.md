# EvoKernel × DeepWiki 关联文档（更新于 2026-09-03）

## 本仓索引状态（钉版）

- **EvoKernel 是 HuggingFace 数据集（noahli/EvoKernel），非 GitHub 仓，DeepWiki 无对应页面**；同名 GitHub 仓不存在（hf-mirror clone 为唯一通道）。随附论文 arXiv:2603.10846 的 agent 框架**未开源**（evokernel.zhuo.li 仅项目页）。
- **强关联仓 KernelBench（ScalingIntelligence/KernelBench）已被 DeepWiki 全量索引**（36 子页，快照 2026-01-16），全文快照在本目录 `kernelbench/`。本数据集 165 个 ops-kernelbench-910b kernels 与 250 个 ops-kernelbench-cuda-ncu kernels 的任务定义直接来自 KernelBench 三层级（pytorch-references/KernelBench 是其 vendored 拷贝）。

## KernelBench wiki 与本数据集的交叉引用

| DeepWiki 章节 | 关联点 |
|---|---|
| `5.1-dataset-organization` + `5.2~5.4` | KernelBench L1/L2/L3 任务的语义（本仓 pytorch-references/KernelBench 的 100+100+50）；ops-kernelbench-* 集合即这些任务在 Ascend 910B / CUDA 上的生成产物 |
| `2.1-kernel-evaluation-system` | 上游正确性协议（多 seed+allclose）——result.json 的 correctness 字段口径之源 |
| `2.5-timing-and-profiling` | NCU/nsight 计时路线——ops-*-cuda-ncu 集合的 "ncu-guided runs" 即该路线的迭代化 |
| `7.1-evaluation-metrics` | fast_p/speedup 定义；注意本数据集 MHC 版 result.json 的 speedup_vs_baseline 是自带 baseline 的口径，其余集合无 |

**注意**：Attention 79 任务与 MHC 15 任务不属于 KernelBench（自建任务族），无上游 wiki 对应，结构详见 `../docs/explain/evokernel-pytorch-references.md`。

## 覆盖检查

`kernelbench/` 36/36 子页全量快照（`_coverage-check.md`），抓取于 2026-09-03。
