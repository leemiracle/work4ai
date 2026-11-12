# KernelMem 新人上手指南

> 基于 `.understand-anything/knowledge-graph.json`（129 节点 / 258 边 / 6 层 / 12 步导览）生成，commit `8b57ccc`。

## 1. Project Overview

KernelMem 是**基于 PyTorch 模型代码的自动 CUDA kernel 生成与优化系统**，核心特色是「长短期记忆机制」。系统的基本问题是：给定一段 PyTorch forward 代码，如何让 LLM 迭代写出数值等价且更快的 CUDA kernel。单纯多轮重试容易在同一个编译错误上反复摔倒、或重复尝试已证伪的优化方向，KernelMem 的解法是把「经验」显式建模为两类记忆并持续回灌：

- **短期记忆（工作记忆）**：当前任务当前 run 内产生的一切过程证据——每轮生成的 kernel 源码、编译/运行错误日志、正确性比对结果、speedup 指标、NCU/nsys 剖析数据、修复历史与优化历史。它们由 `_build_history_block` 等辅助函数拼装成 Markdown 代码块，直接嵌入下一轮提示词，目的是让 LLM 不重复犯错、能继承已验证的加速结构。
- **长期记忆（先验知识）**：`memorybank/` 中跨任务沉淀的瓶颈先验（YAML 规则库：瓶颈分类 → 解法映射、kernel 结构 × 瓶颈的 decision table）与 gate 取值表。它以确定性规则而非自由文本的形式存在，先经机器检查闸门约束 LLM 的优化方向，再在门控通过后把方法目录注入提示词。

两类记忆在优化裁判环节汇合于同一次 LLM 调用，构成完整的 memory loop。对新人而言，理解本项目的关键不是某个算法，而是**数据流**：一条 kernel 从 seed 生成到被评测、剖析、诊断、修复/优化、再回灌的全生命周期。

- **主入口**：`main_memory_latest.py` 的 `main()`（CLI 触发），支持单任务与批跑两种模式。
- **技术栈**：Python（主体）+ YAML（规则库）+ PyTorch + Nsight Compute（ncu）+ Nsight Systems（nsys）+ OpenAI-compatible LLM API（十种后端可切换）。
- **闭环**：seed 生成 → 编译评测（子进程隔离）→ 不可运行走修复链 / 可运行走「NCU+nsys 剖析 → 机器检查 → 优化裁判」链 → 记忆回灌 → 下一轮，直到 `--round` 轮数耗尽。
- **内嵌数据集**：`KernelBench/` 目录含 270 个任务脚本（level1×100 基础算子、level2×100 小子网、level3×50 代表模型如 ResNet/Transformer、level4×20），既是任务的参考实现也是真值来源。该目录已被 `.understand-anything/.understandignore` 排除在知识图谱之外（属数据而非代码，分析时无需扫描）；其上游为 **ScalingIntelligence/KernelBench** 公开数据集，DeepWiki 上有该数据集的全量 wiki，查任务背景与评测语义时可前往检索。

## 2. Architecture Layers

| # | 层 | 职责 |
|---|---|---|
| 1 | **编排与剖析层**（orchestration） | 系统主控：`main_memory_latest.py` 驱动生成→评测→剖析→修复/优化→记忆回灌的自进化闭环；`run_ncu_memory.py`/`run_nsys.py` 负责两类剖析；`scripts/individual.py` 定义进化个体。 |
| 2 | **记忆化提示词层**（prompts） | 面向 LLM 的提示词资产：generate/judger/optimization/error 各阶段记忆化提示词、few-shot 示例、GPU 规格表、确定性机器检查引擎——经验注入与记忆回灌的语义载体。 |
| 3 | **LLM 后端接口层**（agents） | `query_server.py` 统一调用入口（10 种后端分派），`llm_local.py` 本地 vLLM 兼容客户端；生成/修复/裁判三类调用共用。 |
| 4 | **编译评测与工具层**（utils） | `compile_and_run.py` 编译执行与真值评测、`kernel_io.py` LLM 输出提取与落盘、`print_utils.py` 终端输出。 |
| 5 | **长期记忆资产层**（memorybank） | 跨任务沉淀的瓶颈先验 YAML（两层规则库）与 gate 取值表，向机器检查与优化裁判注入历史经验。 |
| 6 | **配置与文档层** | 两份 ncu-cfg 采集配置（configures→run_ncu_memory）、README、分析工具 ignore 规则。 |

## 3. Key Concepts

1. **短期记忆**：当前 run 的 kernel 代码、错误日志、NCU/nsys 结果、修复/优化历史，经 `_build_history_block`（按 mtime 取最近 N 个历史 kernel）等拼成 Markdown 代码块嵌入提示词；持久化为 `optimization_tree.json` 与逐轮 `opt_round_*.json`/`repair_round_*.json`，重启后可续读。
2. **长期记忆**：`memorybank/` 的瓶颈先验与 gate 表，以 YAML 规则而非自由文本形式跨任务约束 LLM——规则的确定性意味着同样输入永远得到同样的优化方向白名单。
3. **memory loop**：生成→评测→剖析→诊断→回灌的多轮自进化循环，`_run_single_task` 是总剧本；loop 中维护 base/best 双基准，best kernel 是全局最优候选。
4. **judger 修复链**：kernel 失败后并不直接让 LLM 盲修，而是先由 judger 以审计者身份诊断错误（四路决策流：编译失败→CUDA 崩溃→数值失配→超时），产出 critical_issue/root_cause/minimal_fix 等八字段结构化结论，再据此构建修复提示词；repair_history 注入避免重复踩坑。
5. **NCU 剖析驱动**：`ncu` 按 `config_metrics.ncu-cfg` 采集 30 余项微架构计数器（SM/DRAM/L1/L2 吞吐占比、occupancy 限制项、warp 停顿分解、分支分化、cache 命中率），清洗为 DataFrame 后渲染成提示词文本块——优化不是凭感觉，而是由微架构证据驱动。
6. **nsys 启动次数证据**：与 NCU 的单 kernel 深度剖析互补，`nsys stats` 提供全局时间线视角与各 kernel 的 launch counts——launch 开销大小与 kernel 融合机会的判定依据。
7. **few-shot 前后对照**：`Model`（PyTorch 参考）vs `ModelNew`（CUDA 加速版）成对示例，共同定义候选必须复现的接口契约（get_inputs/get_init_inputs 张量工厂、load_inline 绑定形态）——示例教格式，规格教硬件约束，源码教任务本身。
8. **gate 值（code_features）**：19 个结构特征字段（has_reuse、streaming_no_reuse、is_aligned_vector_access、is_gemm_kloop、is_stencil_conv、kernel_structure_id S0-S4 等）的取值与判定标准，定义在 `gate_value_from_kernel_struct`；特征提取以正则启发式扫描优先、LLM 门控（judge_gate）兜底。
9. **机器检查门控**：`machine_check_ver2` 加载 YAML 规则、按 field_mapping 归一化 NCU 指标、用 AST 白名单 safe_eval 计算 derived_fields 与 headroom 分层、匹配谓词签名后查 decision_table 得 allowed_methods——LLM 只能在确定性闸门划定的白名单内选优化方法。
10. **单一最有影响力优化裁判**：每轮只允许一个优化目标——judger_optimization 聚合全部证据后要求 Judge LLM 恰好返回一个优化目标与最小实施计划，避免多目标互相打架导致改无可归因。
11. **speedup = ref_latency / test_latency**：候选与参考 PyTorch 实现的 CUDA Event 计时之比，是全系统唯一排序指标；正确性由 `tol` 容差比对把关（超差抛 AccuracyError），不可运行候选不参与排序。
12. **KernelIndividual**：kernel 候选的统一载体（代码/指标/分数/反馈 + 类级自增 id + save_code/save_metrics 落盘为 `kernel_{id:04d}.py`/`eval_{id:04d}.json`）。
13. **子进程隔离评测**：`_bench_and_score` 以 spawn 子进程跑真值评测，超时按 terminate/kill 升级处理，CUDA 上下文崩溃不污染主进程——坏 kernel 挂死不会拖垮整个 batch。

## 4. Guided Tour（12 步）

1. **项目概览**：读 README 建立五模块地图（主编排/prompts/memorybank/utils/agents），了解单任务与批跑两种上手方式。
2. **主编排入口**：`main()`→`_build_arg_parser`（CLI：任务/GPU/LLM/轮数/评测参数）→时间戳+run_tag batch 目录→`_run_single_task` 千行核心循环——先读懂 runnable 分流逻辑再往下走。
3. **进化个体与 kernel I/O**：`KernelIndividual` 落盘 `kernel_{id:04d}.py`/`eval_{id:04d}.json`；`kernel_io.py` 从 LLM 回复提取代码围栏块（容忍未闭合 fence）、解析 judger 的 JSON——被主循环高频复用的「最后一公里」。
4. **种子生成提示词**：`build_seed_prompt` = few-shot 前后对照 + 任务源码 + GPU 规格表三要素，每份 seed prompt 自包含。
5. **编译评测**：`compare_and_bench` 动态 import 参考/候选双模型、逐字节捕获 Python+ninja+nvcc 编译日志、参数对齐、真值比对、CUDA Event 计时；抛出的错误类型直接决定下轮走哪条修复路径。
6. **NCU 剖析**：`profile_bench`（按 ncu-cfg 采集）→`load_ncu_metrics`（清洗过滤）→`metrics_to_prompt`（渲染紧凑文本块）三段管线，产出微架构证据。
7. **nsys 剖析**：`.nsys-rep` 追踪→`nsys stats` 提取 launch counts CSV；`extract_cuda_kernel_names` 从源码正则抽 kernel 名，供两个剖析器做目标过滤。
8. **修复链**：`judger_repair`（Repair History 截断注入）→`error_memory`（八字段诊断格式化+四路决策流）；编译/执行超时（模板递归扩张、constexpr 爆炸等）另有专用 judger 模板。短期记忆在此闭环。
9. **长期记忆与机器检查**：`machine_check_ver2`（1291 行、全程无 eval）+ memorybank YAML + gate 语义文档构成确定性闸门，先划 allowed_methods 白名单再放行。
10. **优化裁判**：九类证据源聚合→单一优化目标与最小实施计划→实现提示词；长短期记忆在此汇合于一次 LLM 调用。
11. **LLM 后端**：`query_server` match/case 分派 local/vllm/sglang/deepseek/fireworks/anthropic/google/together/sambanova/openai-Azure 十种后端 + token 记账；本地走 `llm_local`（指数退避重试+lru_cache 连接复用）。
12. **汇总输出**：`summary.json`/`summary.csv` 跨任务统计、matplotlib 每轮 score 曲线（runnable 分色）、`usage.csv` 按 call_type 的 token 成本核算；至此闭环走完，可回到第 2 步对照整条数据流。

## 5. File Map（按层）

**编排与剖析层**

| 文件 | 行数 | 说明 |
|---|---|---|
| `main_memory_latest.py` | 1831 | 主入口：CLI、任务收集、单任务循环、双基准维护、全局 summary |
| `run_ncu_memory.py` | 1151 | NCU 剖析三件套：采集/清洗/渲染为 prompt 块 |
| `run_nsys.py` | 439 | nsys 追踪与 kernel launch counts 统计 |
| `scripts/individual.py` | 35 | KernelIndividual 数据对象与落盘 |

**记忆化提示词层（prompts/）**

| 文件 | 行数 | 说明 |
|---|---|---|
| `generate_custom_cuda_memory.py` | 270 | seed 轮提示词（few-shot+规格+源码）；`generate_custom_cuda.py` 为共享规格加载器的旧版 |
| `judger_optimization_memory_latest.py` | 928 | 优化裁判：多源聚合+方法目录渲染 |
| `machine_check_ver2.py` | 1291 | 确定性规则引擎（AST 白名单 safe_eval） |
| `judger_repair_memory.py` | 191 | 修复链审计 judger（Repair History 注入） |
| `error_memory.py` | 209 | 失败修复提示词（四路决策流、八字段诊断） |
| `optimization_memory_latest.py` | 225 | 优化实现提示词（modification_plan 注入） |
| `judger_compilation_timeout.py` | — | 编译/执行超时专用诊断模板 |
| `judge_gate.py` | 364 | LLM 门控：19 特征字段严格 JSON 输出 |
| `hardware/gpu_specs.py` | — | 八种 GPU 规格纯数据模块 |
| `few_shot/model_ex_add.py` / `model_new_ex_add.py` | — | 前后对照示例对 |
| `utils.py` | — | read_file 极简 IO |

**LLM 后端接口层（agents/）**：`query_server.py`（354 行，10 后端分派+记账）、`llm_local.py`（131 行，chat/generate 双接口+重试）。

**编译评测与工具层（utils/）**：`compile_and_run.py`（809 行，地面真值评测器）、`kernel_io.py`（155 行）、`print_utils.py`。

**长期记忆资产层（memorybank/）**：`bottleneck_headroom_kernelstructure.yaml`（1325 行，machine_check 确定性门控 + llm_assist 非约束知识两层规则库 v2.1）、`gate_value_from_kernel_struct`（19 个 code_features 字段语义表，运行时被逐行解析）。

**配置与文档层**：`config_metrics.ncu-cfg`（raw 计数器采集）、`config_section.ncu-cfg`（七分节人读报告）、`README.md`。

**数据（图谱外）**：`KernelBench/` level1-4 共 270 个任务脚本——上游 ScalingIntelligence/KernelBench，DeepWiki 有全量 wiki。

## 6. Complexity Hotspots（谨慎接近区）

1. **`main_memory_latest.py`（1831 行）**：`_run_single_task` 是千行级状态机——runnable 分流、base/best 双基准、修复与优化双链历史、目录副作用极多；改一处常牵动记忆回灌路径，须先通读再动手。
2. **`prompts/machine_check_ver2.py`（1291 行）**：自研 mini 规则引擎——field_mapping 归一化、AST 白名单递归求值器、derived_fields/headroom/谓词签名/decision_table 四层耦合；全程禁 eval，改规则语义前必先读懂 safe_eval 的白名单边界。
3. **`memorybank/…kernelstructure.yaml`（1325 行）**：YAML 即 DSL——两层结构（machine_check 硬约束 / llm_assist 软知识）+ kernel 结构 S0-S4 × 瓶颈的 decision_table；缩进或字段名错误会被加载器静默吞掉，是「改一行全链路行为变」的最高危文件。
4. **`run_ncu_memory.py`（1151 行）**：ncu 命令行→CSV→DataFrame→prompt 的四段管线，还要与两份 ncu-cfg 配置及 kernel 名过滤对齐；多 kernel 合并采集的行归一化逻辑是隐性契约。
5. **`prompts/judger_optimization_memory_latest.py`（928 行）**：九类证据源（GPU 规格/NCU 指标与 DataFrame/nsys 计数/历史/机器检查/YAML 目录）聚合进同一模板，字段兼容旧名（"optimisation method" 等）；漏注入任一源即改变裁判行为且无报错。
6. **`utils/compile_and_run.py`（809 行）**：动态 import + 逐字节编译日志捕获 + 参数对齐 + CUDA Event 计时；CompilationError/AccuracyError 的错误分类直接驱动主循环分支，是「真值语义」唯一裁判点。
7. **`run_nsys.py`（439 行）**：.nsys-rep 二进制追踪解析依赖 nsys stats CLI 输出格式，版本升级易碎。
8. **`prompts/judge_gate.py`（364 行）+ gate_value 文档**：19 字段 JSON schema 与机器检查的字段校验强耦合；LLM 输出漂移（字段缺失/枚举越界）会静默落入兜底路径。
9. **`agents/query_server.py`（354 行）**：10 后端 match/case 分派 + 采样参数统一 + token 记账；新增后端须同时维护记账与 finish_reason 处理，否则成本核算失真。

---

*新手上手顺序建议：先跑通 README Quick Start 的单任务小轮数（level1 + `--round 3`），再按 §4 导览读码；改 prompts 前先看 §3 概念 1/2/9，改评测前先看概念 11/13。*
