# KernelBlaster × DeepWiki 关联文档（更新于 2026-09-03）

## 本仓索引状态（钉版）

- **NVlabs/KernelBlaster 本身未被 DeepWiki 索引**（2026-09-03 核验：deepwiki.com/NVlabs/KernelBlaster 仅返回 "Loading..." 壳页，需 Devin 登录触发生成，无公开 wiki）。本目录用「关联仓 wiki + 本仓源码深读」补位。
- **直接上游/关联仓 KernelBench（ScalingIntelligence）已被 DeepWiki 全量索引**（35 子页，快照 2026-01-16，commit 2f65279d）。全文快照在 `kernelbench/`（35 页，抓取于 2026-09-03）。

## KernelBench wiki 与本仓的交叉引用（为什么必须一起读）

KernelBlaster 的输入数据 `data/kernelbench-cuda/<level>/<problem>/{init.cu, driver.cpp}` 直接来自 KernelBench 生态（上游 problem.py → CUDA starter + C++ harness 的转译产物）。读源码时对照 DeepWiki 章节可分清「哪些是上游设计、哪些是 KB 创新」：

| DeepWiki KernelBench 章节 | 与 KernelBlaster 的关联点 |
|---|---|
| `2.1-kernel-evaluation-system` | 上游正确性+计时评测协议（n_correctness 试验、L2 清缓存、fast_p）；KB 的 driver.cpp 验证与 scripts/run_baselines.py 对应此协议的 C++ 化实现 |
| `2.5-timing-and-profiling` | 上游四种 timing_method（cuda_event/do_bench/host_time/nsight）；KB 用 NCU elapsed cycles 作为主信号，属 nsight 路线的深化 |
| `3.4-generating-baseline-timings` | KB 的 PyTorch baseline 复现（run_baselines.py / run_baselines_compile.py）对应上游 baseline 生成流程 |
| `5.1-dataset-organization` / `5.2~5.4` | 数据集三层级（L1 原子算子 100 / L2 融合 100 / L3 完整架构 50）；KB README 声称的 geomean 1.43x/2.50x/1.50x 即在这三层上测得 |
| `7.1-evaluation-metrics` | fast_p / pass@k / geomean speedup 定义——解读 KB 论文指标的前提 |
| `8.3-profiling-and-debugging` | NCU/nsys 工作流上游视角；KB 的 servers/ 编译评测设施是其 agentic 化 |

**KB 相对上游的关键增量**（源码侧证据，详见 `../docs/explain/`）：
1. `data/kernelblaster/optimization_database.json`——出厂持久优化知识库（策展状态组），上游无此概念；
2. `src/kernelblaster/agents/opt_ncu_rl.py`——NCU 状态提取 → KB 检索 → 候选生成 → reward → replay buffer 的 MAIC-RL 闭环，上游只做一次性生成评测；
3. `src/kernelblaster/servers/`——编译/GPU 独立服务化（并发隔离），上游是脚本级多进程。

## 覆盖检查

见 `_coverage-check.md`：35/35 子页全部抓取，无遗漏；抓取器对 SSR 正文完整（抽样 3 页人工比对源页面）。
