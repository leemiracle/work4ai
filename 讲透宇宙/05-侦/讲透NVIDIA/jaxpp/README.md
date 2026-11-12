# 讲透 NVIDIA/jaxpp

JAX MPMD（多程序多数据）流水线并行库：`mark_stage_end` 注解 + `mpmd_jit_with_loop`/`mpmd_jit_by_yield` 装饰器，把一个 JAX 函数编译成每设备独立 jit 程序；附带 MaxiMoE（DSV3 形状 MoE + SM90/SM100 ragged GEMM）参考实现。

- 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/jaxpp`（@`d5ff52c`，"Update 26.10.15"，版本 0.11.1）
- 图谱：903 节点 / 2037 边 / 14 层 / 16 步导览，validator 0 issues，fingerprints 117 文件基线

## 全链状态

| 环节 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ | `deepwiki/`（19 内容页 TRUE_100，含 INDEX/_coverage-check/wiki_full） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（903n/2037e/14 层/16 步 @d5ff52c3，fp=117） |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（8712 字符，8 节，50 锚） |
| explain | ✅ | `explain/` 4 篇（01-core 编译管线 / 02-调度器 DualPipeV+KimiK2 / 03-MaxiMoE MoE 参考 / 04-测试与文档站，各 3.1-3.4k 字符、15-39 path:line 锚） |
| 批注甄别 | ✅ | 仓内 `.understand-anything/NOTES-DIGEST.md`（17 条） |

## 源码级勘误（8 条，全部行号实证）

1. **KimiK2 不是新调度算法**：`src/jaxpp/schedules.py:547-549` 全部实现只有 `_uncapped_rank_warmup_ops` 返回 super()+1——它是 Interleaved1F1B 的 warmup+1 派生，不是 Kimi K2 式完整调度移植；名字极易让人高估其独立性与复杂度。
2. **DualPipeV 是 DeepSeek 原版的专门化子集**：硬约束 num_stages == 2×mpmd_dim（`src/jaxpp/schedules.py:614-619` 显式 raise）且 n_mubatches ≥ num_stages（`:632`）；溯源注释在 `:204`（Adapted from deepseek-ai/DualPipe，带原始 commit 链接）。
3. **mark_stage_end 的 docstring 口径偏窄**：`src/jaxpp/pipelining.py:55` 说"Must be called inside a function passed to treduce/treduce_i"，但 `examples/basic.py:130/:139` 在 mpmd_jit_with_loop 路线同样生效——真实条件是 yield_scope 激活（`src/jaxpp/core.py:3346` 与 `src/jaxpp/training.py:199/:253` 两处）。
4. **`_get_fused_jaxpr_cached` 是 @overload 三连**：`src/jaxpp/core.py:2218/:2231` 两个签名桩 + `:2244` 真实现（同类还有 `src/jaxpp/array_ops.py:62/:66`、`src/jaxpp/utils.py:275/:281`）；朴素抽取/阅读会误当三个函数，图谱构建时已按同名去重。
5. **deprecated API 仍走公共门面导出**：`pipeline_enter_stage`（`src/jaxpp/pipelining.py:39`，DeprecationWarning）仍被 `src/jaxpp/api.py:34` re-export，门面上与稳定 API 无区分。
6. **licm.py 默认不生效**：`JAXPP_ENABLE_LICM` 默认 False（`src/jaxpp/env_vars.py:5`）——LICM+部分求值+CSE 三合一 pass（`src/jaxpp/licm.py:680`）需显式开环境变量，文件名的"LICM"不等于默认行为。
7. **训练算子测试覆盖与实现复杂度倒挂**：`tests/test_training.py` 仅 52 行 vs `src/jaxpp/training.py` 407 行（对照 `tests/test_mpmd_api.py` 2116 行）；treduce/tscan 的正确性保障实际压在 MaxiMoE 端到端上。
8. **docs/rendered/ 不是普通文档**：CI runner 无 GPU（`.github/workflows/documentation.yml:27`），`docs/compilation.md`/`docs/unreduced_gradients.md` 构建时被 docs/rendered/ 预渲染副本替换（`:49-51`）再以 nb_execution_mode=off 跑 sphinx（`:74`）——手编 rendered/ 会被下次构建覆盖。

## 图谱构建实录（两缺陷自纠）

- **重载去重**：core.py 等三处 @overload 多段同名 def，批产物按"同文件同名保留首签名段"归一（图谱中 `_get_fused_jaxpr_cached` 仅一个节点，记首段 L2219-L2228）。
- **孤儿边兜底**：批产物端点悬空的边不按默认静默 drop，走兜底归位；终态 0 孤儿边、0 重复 id（validator 0 issues）。

## 阅读顺序建议

`examples/basic.py` → `deepwiki/2.1`（pipeline parallelism API）→ `onboarding/ONBOARDING.md` → `explain/01`（core 编译管线）→ `explain/02`（调度器）→ `explain/03`（MaxiMoE）→ `explain/04`（测试与 CI）。
