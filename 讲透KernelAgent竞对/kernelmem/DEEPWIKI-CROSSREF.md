# KernelMem × DeepWiki 关联文档（更新于 2026-09-03）

## 本仓索引状态（钉版）

- **0satan0/KernelMem 未被 DeepWiki 索引**（2026-09-03 核验：页面为 "Loading..." 壳）。本目录用「关联仓 wiki + 本仓源码深读」补位。
- **强关联仓 KernelBench（ScalingIntelligence/KernelBench）已被全量索引**（36 子页，快照 2026-01-16，commit 2f65279d），全文快照在本目录 `kernelbench/`。本仓 `KernelBench/` 目录（270 个 problem.py，level1/2/3）即其数据集的 vendored 拷贝——任务定义/层级语义/评测哲学全部以上游 wiki 为准。

## KernelBench wiki 与本仓的交叉引用

| DeepWiki 章节 | 与 KernelMem 的关联点 |
|---|---|
| `5.1-dataset-organization` + `5.2~5.4` | 本仓 KernelBench/ 三层任务（L1 原子算子/L2 融合/L3 完整模型）的语义、组织与 get_inputs/get_init_inputs 协议 |
| `2.1-kernel-evaluation-system` | 正确性协议（多 seed 随机输入+allclose）——utils/compile_and_run.py 的 tol 比对是它的简化实现 |
| `2.5-timing-and-profiling` | 上游 4 种计时法（cuda_event/do_bench/host_time/nsight）；KernelMem 用 host 侧平均延迟（warmup/repeat），NCU/nsys 深度剖析走 run_ncu_memory.py/run_nsys.py（nsight 路线的 agentic 化） |
| `4-prompt-engineering` 全家 | 上游提示工程体系（TOML 模板/zero-one-few-shot/硬件感知）；KernelMem 的 prompts/ 是与之对位的自研记忆化提示词族（历史轮次+profile 回灌）——设计哲学差异：上游静态模板 vs 本仓动态记忆装配 |
| `7.1-evaluation-metrics` | speedup/fast_p 定义——本仓 speedup=ref_latency/test_latency 的口径对照 |

**KernelMem 相对上游的增量**（详见 `../docs/explain/`）：①长短期记忆双库（memorybank yaml+gate 表=长期；轮次 code/evaluation/profile 回灌=短期）②judger 修复/优化双分支提示词 ③NCU section 级指标→优化建议的自动转译。

## 覆盖检查

`kernelbench/` 36/36 子页全量快照（见 `_coverage-check.md`），抓取于 2026-09-03。
