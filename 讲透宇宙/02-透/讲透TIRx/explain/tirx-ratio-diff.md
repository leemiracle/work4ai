# ratio_diff.py 深度解析：固定的 before/after 性能门禁

> 源码：`tirx_kernels/bench_suite/ratio_diff.py`（765 行）｜图谱节点 `file:tirx_kernels/bench_suite/ratio_diff.py`（complexity=complex，tested）

## 角色定位：在 14 层架构中的位置

ratio_diff.py 是**基准编排层（bench-harness）**的"判决书"——前两个文件（run.py 产 run JSON、ab.py 产配对 payload）负责拿数据，它负责回答唯一的问题：**这次改动有没有让我们的 kernel 变慢**。它存在的根本理由写在文件头 docstring 里：判定语义必须**固定且不可调**。可配置的阈值会被一次次"这次先放行"慢慢调没；所以门禁硬编码 `MAX_AFTER_OVER_BEFORE = 1.01`——同一 TIR/TIRx 实现在 baseline 与当前 run 的 `round_samples` 算术均值之比，`after/before < 1.01` 通过。1% 容差吸收测量噪声，同时拒绝任何可检出的回归。它既是 CLI（默认拿 `.bench-suite/latest.json` 对 `baseline.json` 比），也是库（`build_report` 被 ab.py 配对调用、被 run.py 延迟调用）。门禁输出同时是给人看的 markdown 报告和给 CI 看的失败计数，一份产物两种消费方式。

## 内部结构：17 个函数分四组

图谱 contains 边列出 17 个函数，按职责天然四组：

- **键推导组**：`_key`（kernel + label-or-config 归一化键，label 与 config 冲突即报错）、`_expected_keys`（**实时**从 config 目录推导默认 roster，可选按架构过滤）、`_selected_after_keys`（校验 after 的 selection 声明：default 模式必须与默认 roster 全集一致，targeted 模式必须非空且是 roster 子集）、`_paired_expected_keys`（配对模式要求双侧 selection 完全一致）。
- **记录校验组**：`_records`（payload → {键: [行]} 索引）、`_validate_record_set`（对期望键查 missing/duplicate/unexpected）、`_validate_row`（单行体检：status=ok、clean≠false、无干扰标记、errors 空、provenance 六字段齐备、num_gpus 与 UUID 列表长度一致）、`_sample_means`（判定的**唯一数据源**：round_aggregate 必须=mean、轮数与样本数一致、实现顺序须为合法排列、样本全为正有限数，然后 `statistics.fmean`）。
- **provenance 校验组**：`_validate_git`（必需键 tir/tirx-kernels 存在、非白名单的 dirty 后缀即错）、`_compare_mapping`（同名映射比较，支持忽略键/空值策略）、`_compare_run_provenance`（运行级：git 与 kernel_tree 除白名单外双侧一致、references_enabled 同值、pipeline 三字段一致）、`_compare_row_provenance`（配对模式逐行逐字段，benchmark_protocol 剔除瞬态字段 timing_stream 后比较）。
- **判定与报告组**：`_ours`（恰好一个 our 实现，多了少了都报错）、`pick_ref`（挑最快外部基线做诊断）、`index`（兼容视图，重复键拒绝）、`build_report`（核心，下详）、`main`（CLI）。

## 外部连接：图谱边视图

- **imports →** `impls.is_our_impl`（唯一外部依赖，且 try/except 支持脚本直跑）。
- **被 imports ←** `ab.py`（调 `build_report(paired=True)`）、两个测试文件 `test_bench_suite_ab.py`/`test_bench_suite_run.py`（tested_by 边 ×2）；run.py 在 main 尾部经 `sys.path.insert` 延迟引入（2593-2597 行）。
- **related ←** `baseline.json`（pinned 基线，图谱相关边）；**documents ←** bench_suite/README.md。
- 对 run.py 的依赖全部是**函数内延迟 import**（`_load_config_dir`、`_expected_keys` 里的 `partition_workloads_by_arch`）——门禁模块保持零模块级依赖，保证它可以在任何机器上独立分析两份 JSON。

## 数据流：build_report 逐段走读（507-719 行）

输入：baseline（dict/Path/str 之一）+ current + 模式（paired / 默认门禁）。流程：

1. **定期望键**（522-543）：配对模式走 `_paired_expected_keys`；否则从 after 的 selection 读 cuda_arch，实时推导默认 roster，再校验 selection 合法性得到期望键集合。
2. **记录集对齐**（544-556）：双侧 payload 索引化；before 须覆盖期望键（配对模式还要拒绝意外键，非配对带架构时允许 before 有多余行——旧基线可能含本架构跑不了的行）。
3. **运行级 provenance**（557-563）：git/kernel_tree 除 `tirx-kernels` 白名单外必须一致（配对模式额外容忍 tir dirty——两个检出并存时 before 侧 TVM 仓可能带同样改动）；pipeline 的 execution_mode/process_model/measurement_protocol 必须相同。任何差异直接进 failures。
4. **逐行判定**（565-651）：跳到两侧都恰好一行的键；查双侧干扰标记 → `_validate_row` 体检 → `_compare_row_provenance` → `_ours` 找双侧唯一 our 实现（名字不同也 fail）→ 非配对模式还要求**双侧都有外部参考实现且名单一致**（没有参考的行判 fail——外部实现是"环境是否正常"的对照组，缺了对照组的行不可信）→ **核心三行**（615-619）：`direct_ratio = after_us / before_us`，`passed = direct_ratio < 1.01`，不过即 failures。外部基线只算 diagnostic：ref 自身漂移、ref/ours 比值变化，超阈值打 warning 标记。
5. **报告输出**（653-719）：行按 direct_ratio 降序（最慢的排最上），markdown 表格含双侧 µs、比值、加速百分比、direct gate PASS/FAIL、ref 诊断列；failures 单列一节。返回 `(markdown, failure_count)`，调用方据 count 设 exit 3。

CLI `main`（722-761）只是薄壳：默认路径、写报告到 `.bench-suite/reports/<run>/bench.md`、返回 failures 作退出码。

## 设计决策：值得学习的模式

- **判定与诊断分离**：verdict 只用 our 实现的原始样本均值；外部实现（cudlas/flashinfer/deepgemm…）双侧必查但**永不影响判定**。理由很深：外部实现自身也在变版本，拿它当判据会引入第二个不受控变量；但它又是绝佳的"环境对照组"——如果 ref 也同比变慢，多半是 GPU 状态而非代码回归，所以做成诊断列而非门禁条件。
- **`threshold_pct` 的诚实降级**：CLI 仍接受 `--threshold`，但 docstring（516-518 行）明说它只控制诊断列的 warning 标记，门禁钉死 1%——参数保留兼容、语义收窄声明，比直接删参数更稳。
- **fail-closed 的数据卫生链**：从样本合法性（正、有限、数量一致）→ 聚合协议（必须 mean）→ 实现顺序排列校验 → 行级 provenance → 运行级 provenance，五层任一不过都是 failure 而非跳过。基准门禁的公信力来自"宁可误杀不可放过"。
- **重复键拒绝而非静默覆盖**（`index` 的 docstring，251 行）：同名 (kernel, config) 出现两次说明上游装配有 bug，覆盖会销毁证据。
- **瞬态字段豁免表**：`_EPHEMERAL_BENCHMARK_PROTOCOL_FIELDS = {"timing_stream"}`——protocol 里随运行环境变但不影响可比性的字段白名单化，体现"一致性校验要严，但要严在对的地方"。
- **期望键实时推导**：不存一份"应该有哪些行"的清单（会腐烂），而是从 config 目录现算——基线与门禁永远对齐当前仓库的定义。

## 新人提示

- 阅读切入点：文件头 16 行 docstring 是语义声明书，逐句读；然后直接进 `build_report`，四组辅助函数按需查。
- 易混淆点一：**配对模式与非配对模式的期望键来源不同**——非配对以"默认 roster/selection 声明"为准（before 可以多于期望），配对以"双侧 selection 交集约定"为准（before/after 必须对称）。测试里有三个用例专测配对边界（允许跨 workload 换 GPU、拒绝单行内跨 GPU、允许关 references 时空基线），读懂它们就懂了配对语义。
- 易混淆点二：`direct_ratio > 1` 是变慢（分子是 after），而报告里 `speedup_pct` 的符号相反（正数是加速）——看表时别搞反。
- 易混淆点三：`_sample_means` 校验的是 `round_samples`（原始逐轮样本），不是 run.py 已聚成的 `impls` 均值——门禁只信任原始数据，聚合层的东西只做展示。
- 严格 `< 1.01` 而非 `<=`：恰好 1% 变慢也算不过。这是个有意的保守选择，改它之前请先理解 CI 消费方依赖它拦截什么。
