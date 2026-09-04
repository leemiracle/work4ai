# KernelMem 记忆化提示词族深解

> 对象：`prompts/generate_custom_cuda_memory.py`、`optimization_memory_latest.py`、`judger_optimization_memory_latest.py`、`judger_repair_memory.py`、`error_memory.py`、`prompts/few_shot/`
> 主循环：`main_memory_latest.py::_run_single_task`（round 0 种子 → NCU/Nsys 剖析 → 判官 → 优化 → 基准 → 失败则修复，往复）

## 1. 角色定位：提示词即记忆装配器

KernelMem 是单 LLM 自迭代系统，`prompts/` 下的 `build_*` 函数不是普通"模板"，而是**记忆装配器**：每次调用都从磁盘拉取系统全部状态——GPU 规格表（`hardware/gpu_specs.py`）、参考架构源码、当前 kernel 源码、NCU 指标块、Nsys launch 计数、**优化历史 JSON**（`code_dir/<父kernel名>/opt_round_NNN.json`）、**修复历史 JSON**（同目录 `repair_round_NNN.json`）、以及 `memorybank/bottleneck_headroom_kernelstructure.yaml` 的确定性规则与 method catalog——拼装成一条 prompt。换句话说，项目没有独立的"memory 模块"，**记忆 = 落盘 JSON + YAML 规则库，提示词构建函数 = 记忆的读取接口**。装配器本身无状态，所有状态经参数流入，这让每次调用可从 `io_dir/roundNNN_*_prompt.txt` 完整回放。

## 2. 四类提示词解剖（输入槽位）

**① 种子生成 `generate_custom_cuda_memory.py::build_seed_prompt`**（round 0）。三个槽：`$few_shot_examples`（few_shot/ 的 before/after 对）、`$arch_src`（GPU 规格弹点列表）、`$kernel_src`（待优化的 `class Model` 参考源码）。核心契约：粒度四选一（A 单热点算子 / B 多算子多 kernel / C 融合 / D 全重写 forward）且必须写进 ModelNew 头注释；参数 parity（PyTorch 模块仅作 parameter holder）；固定编译旗标（`-O3`/`sm_80`）。**few_shot 的作用是教"输出语法"而非"优化技巧"**：`model_ex_add.py`（22 行朴素 a+b）→ `model_new_ex_add.py`（71 行 load_inline+kernel+cpp_src+ModelNew 完整骨架），示范的是交付格式，例子本身毫无优化含量——把"格式教学"与"策略生成"解耦。

**② 优化实现 `optimization_memory_latest.py::build_optimization_prompt`**。槽位：GPU 三元组、`$arch_src`（**注意：这里是当前 base kernel 的 ModelNew 全文，不是参考架构**——优化永远在"最新可用 kernel"上做最小差分）、`$optimization_suggestion`（判官产出的策略 JSON，经 `_format_problem` 归一化，同时兼容 `modification plan`/`modification_plan` 新旧字段名）。输出契约是双段结构：Section A 逐条 plan→代码位置映射 + 分隔符 `=== KERNEL CODE STARTS BELOW ===` + Section B 代码块，供主循环 `_extract_kernel_from_optimization_reply` 精确切码。值得注意：`history_block` 参数被硬编码为 `""`（"Not used anymore"）——**原始 kernel 历史堆栈已被判官中介的结构化记忆取代**。

**③ 优化判官 `judger_optimization_memory_latest.py::build_judger_optimization_prompts`**。最重的装配器，双分支模板：machine_check `NO_MATCH` 走精简版（自由策略）；命中走完整版。槽位：GPU 规格、`$python_code` 参考、`$CUDA_CODE` **父 kernel**（判官分析的是 base_kernel 而非刚失败的 current_kernel）、`$NCU_METRICS`（`run_ncu_memory.metrics_to_prompt`：指标 JSON + section 分析文本）、`$NSYS_LAUNCH_COUNTS`、`$OPTIMIZATION_HISTORY`（历史 JSON 渲染成 Previous Attempt 条目，带 speedup/PASSED/FAILED/repaired 标签），再加 MACHINE_CHECK 五字段（tier/bottleneck/case/kernel_structure/key_metrics）、allowed/forbidden 方法表、case 级要求、全局禁令、method catalog（只注入 allowed 方法的目录条目，省上下文）。产出唯一 JSON：`bottleneck/primary_optimisation_method/method_name/modification_plan/evidence/expected_metric_change/headroom`。

**④ 修复两步 `judger_repair_memory.py` + `error_memory.py`**。第一步判官 `build_correctness_prompts`：槽位 `$ERROR_LOG`（`_last_n_lines` 截尾 150 行）、`$PYTORCH_CODE` 真值参考、`$CUDA_CODE` 待审计代码、`$REPAIR_HISTORY`（历史 error_log 截 500 字符 + problem_identification + 结果）。产出问题 JSON（critical_issue/evidence/root_cause/minimal_fix/patch_anchor/confidence），**evidence 要求逐字摘自 ERROR_LOG 可 grep**——反幻觉设计。第二步修复器 `build_error_prompt`：槽位 `$ERROR_LOG`/`$OLD_CODE`/`$Problem`（第一步 JSON 格式化后注入），patch 预算 ≤3 处耦合修改。

## 3. 数据流：memory 最新态 → prompt 的装配函数链

每轮开始先测 `is_runnable`，分流后两条链：

- **修复链**：repair chain 以"链上第一个失败 kernel"锚定历史目录（代码每轮都在换，但历史文件夹不换）→ 加载该目录全部 `repair_round_*.json`（只取有 test_timestamp 的已完成条目）→ `build_correctness_prompts` → problem_json → `build_error_prompt` → 新代码 → 基准 → **回填同一 JSON** 的 runnable/speedup/test_passed。
- **优化链**：runnable → `profile_bench`（NCU）→ `load_ncu_metrics` → `metrics_to_prompt` → 读 `code_dir/<父kernel名>/opt_round_*.json` → `build_judger_optimization_prompts`（内部先跑 `run_machine_check`：临时 CSV + YAML 规则 + 可选 judge_gate LLM 抽代码特征）→ strategy_json → `build_optimization_prompt`（arch_path=父 kernel 路径）→ Section A/B 回复 → 切码 → 基准 → 回填。

**"最新态"由先写后补保证**：策略 JSON 在测试前就落盘（speedup=None），测完回填；下轮只加载已回填条目，天然过滤半成品。

## 4. judger 决策逻辑：判修复 vs 判优化

**修复还是优化不由任何 LLM 决定**，由主循环的 `is_runnable`（基准指标的布尔位）硬分派：跑不起来 → 修复链；跑得动 → 优化链（NCU 超时是特例，走 `_handle_compilation_timeout` 修父 kernel）。两链内部各有一套优先级阶梯：

- 修复判官按**可观察失败现象**四级降序：编译/构建失败（不碰 kernel 逻辑）→ CUDA 执行崩溃（只查越界/launch 配置；含 wmma:: 特判"集体契约违反"三不变量）→ 数值失配（内部再分五级：覆盖/索引 → 参数 parity → 形状公式 → 未支持参数 → dtype/layout）→ 超时。一次只报一个问题。
- 优化判官的核心是**历史去重 + 方法选择**：区分"实现差"（同方法改进，必须声明 concrete delta）vs"方法错配"（换方法）；禁止机制相同仅换标签的 relabeling；必须从 machine_check 的 allowed_methods 硬约束清单中选，且证据须引用 ≥1 个数字指标并排除 1 个备选瓶颈。

## 5. 设计决策与新人提示

1. **全族用 `string.Template` 而非 f-string**：CUDA/C++ 代码充满 `{}`，format 会炸；`$` 冲突由 `_escape_template` 双写转义。文件头注释明说此动机。
2. **结构化记忆优于原始历史**：opt/repair JSON 存"策略+结局标签"，判官据此推理；直接堆 kernel 源码的 history_block 已废弃——教训是**带结局标注的决策记忆比产物本身更有价值**。
3. **两层系统**：machine_check（确定性 YAML 门，答"能不能做"）+ LLM（答"怎么做/为何做"），知识目录只对 allowed 方法注入。
4. **防御性字段解析**：`_format_problem` 双方言兼容、evidence 逐字可 grep、错误日志三级截断（150/500/1000 字符）控上下文预算。
5. 新人建议：先读 `_run_single_task` 的 round 循环看状态机，再对照 `io_dir/` 落盘的 prompt 文本逐轮回放；改槽位时记住 `$arch_src` 在种子与优化两处语义不同（参考架构 vs base kernel）；排查"为何又修不回来"时看 repair chain 目录下的 JSON 链，而非看代码。
