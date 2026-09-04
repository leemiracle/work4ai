# 深解：src/kernelblaster/agents/database.py —— KernelBlaster 的持久 CUDA 优化知识库

> 源码 2324 行（NVIDIA Apache-2.0）。知识图谱定位：`layer:agent-core`（Agent 核心层），被 opt_ncu_rl / rl_agents / opt_ncu_minimal 三个 agent 导入调用，由 `data/kernelblaster/optimization_database.json` 配置。

## ① 角色定位

`GPUOptimizationDatabase`（别名 `OptimizationDatabase`）是 KernelBlaster "记忆增强"卖点的落点：一个**状态为中心的优化经验库**。它维护"性能状态 → 优化技术"两张表，用**双 LLM agent**（State Summarizer 定性归纳 NCU 报告 → State Matcher 与已知状态匹配）把当前 kernel 归类到某个状态，再从库里选出候选优化技术；技术应用后的实测结果回写库里，滚动更新预测值与置信分。文件头自述为 "Enhanced Database utility ... with LLM-powered qualitative state analysis"——本质是把教科书式 CUDA 优化知识变成 LLM 可检索、可被经验校准的活文档。

## ② 内部结构

**数据模型（3 个 dataclass）**：
- `StateProfile`：定性状态档案——`primary_bottleneck`（memory/compute/latency/hybrid_bound 四值）、次级特征列表、性能签名、`relative_patterns`（如 `memory_pressure: high`）。刻意**只存定性档位不存数值**，作者注释明言这是为了跨 kernel 泛化。
- `OptimizationEntry`：单条技术——technique、predicted/actual_improvement、confidence_score、usage_count、predicted/actual_speedup、initial_elapsed_cycles。这是**预测-实测对账的最小单元**。
- `CompositeOptimization`：2-3 个技术的编排组合，带 `order_of_techniques`、`parameters_to_fine_tune`（unrolling factor、tile size 等），`get_composite_id()` 生成复合键。

**主类四层结构**：
1. **加载层**：优先级为 输出目录持久化 JSON → 输出目录 markdown → 仓内默认 JSON 模板（copy 到输出目录后再加载）。JSON 是事实源，markdown 由 `_build_states_markdown()` 从内存重生成（拼 header/footer）。
2. **双 LLM agent 层**：`analyze_performance_state()` 用固定模板 prompt 让 LLM 输出 `PRIMARY_BOTTLENECK/RELATIVE_PATTERNS/...` 格式化文本再行解析；`match_state_against_database()` 把当前状态与库里 16 个状态的文字卡片拼进 prompt 做"软匹配"，置信 <0.6 返回 `NEW_STATE_NEEDED`。
3. **选择层**：`_select_best_optimization_llm()` **跨所有状态**取全局技术池（不再限定单状态），按预测加速比排序取 top-15 塞给 LLM 单选；LLM 不可用或答非所问时回退确定性打分 `predicted_speedup × confidence − usage_penalty + composite_bonus`，再按 τ=0.5 softmax **随机采样**（`KERNELAGENT_DB_FALLBACK_TOP1=1` 可强制贪心）。
4. **演化层**：`update_optimization_result()` 是学习核心——usage_count++、predicted_improvement/speedup 做滚动平均、confidence 按预测准确率 ±0.1 步进调节（accuracy∈[0.8,1.2] 加分）；基线 cycles 从 `ncu/0_init_ncu_log.txt` 懒取。注意 `actual_improvement` 参数**双语义**：无文件路径时当百分比，有路径时被 `int()` 当作当前 elapsed cycles——一处明显的设计妥协。

`LLMInterface` 是薄门面：`is_available()` 只查凭据不发网络请求；事件循环已运行时 `query_sync` 返回硬编码 mock（"memory_bound" 模板答案）——静默降级链很长。新状态发现走混合策略：`discovered_<bottleneck>_<N>` 命名，从瓶颈映射表继承源状态策略（预测值与置信 ×0.8 阻尼），找不到就按瓶颈类型注入 `_create_default_strategies_for_bottleneck` 的内置默认组。

## ③ 外部连接

图谱边显示：**被三个 agent 消费**——`opt_ncu_rl.RLNCUAgent`（主 RL 循环）、`rl_agents.PolicyEvaluationAgent/ParameterUpdateAgent`（反思回路）、`opt_ncu_minimal.MinimalOptimizationAgent`；`LLMInterface → utils/query.py:generate_code_retry`（真实 LLM 通道）；`config:optimization_database.json → 本文件`（configures 边）。**写入调用点**：`update_optimization_result` 在 opt_ncu_rl.py:1124（每次实测后）、`add_new_optimization` 在 opt_ncu_rl.py:1652 与 rl_agents.py:448/465/482（反思产出新技术）、`add_composite_optimization` 在 rl_agents.py:420。落盘三件套：`database_llm_log.txt`（全 prompt/响应）、`database_change_log.txt`（全变更）、`<db>.json`（每次变更后全量快照，`_io_lock` RLock 保护并发）。

## ④ 数据流

**读路径**：agent 拿到 NCU 报告+代码 → `get_state_from_ncu_report()`（Agent1 归纳 → Agent2 匹配 → 命中新状态则混合继承）→ `generate_optimization_plan()` 请求 top-5 计划或 `select_best_optimization()` 取缓存的单选 → 技术名单+描述通过 `_build_available_optimisations_summary()` 以 "STATE: xxx / - technique (pred Nx | conf y): desc" 格式**注入下游代码生成 prompt**；header/footer markdown（含 KernelBench 高手解法的 wmma 完整 CUDA 示例）也作为 few-shot 上下文一并拼进库文本。**写路径**：技术实测后 `update_optimization_result` 回写 → `_log_db_change` 记日志 → `_persist_database` 全量刷 JSON → 下轮加载即读到新值，markdown 反向重生成。闭环成立，但只在**本次 run 的输出目录**内。

## ⑤ 知识库内容审计（出厂 JSON 实测）

对 `data/kernelblaster/optimization_database.json`（40KB）全量解析：

| 顶层键 | 内容 | 数量 |
|---|---|---|
| known_states | 定性 StateProfile（memory_bandwidth/compute_throughput/latency_occupancy_limited） | **3** |
| optimization_strategies | 状态组：high_level_inefficiency、memory_bandwidth_saturated、memory_latency_bound、memory_bank_conflicts、cache_inefficient、compute_throughput_saturated、instruction_mix_suboptimal、thread_divergence_high、low_occupancy_register_pressure、low_occupancy_shared_memory、insufficient_parallelism、hybrid_bound、memory_compute_balanced、latency_memory_bound、api_overhead_dominant、transfer_bandwidth_limited | **16 组** |
| optimization_strategies 内技术条目 | 每组 3-6 条（vectorized_memory_access、tensor_core_utilization、bank_conflict_padding、cuda_graphs…） | **73 条** |
| composite_optimizations | 空 | 0 |
| discovered_states | 空 | 0 |

**关键发现：73 条技术全部 pred_impr=None / pred_speedup=1.0 / confidence=0.5 / actual=None / usage=0 / last_updated=None——实测对数量 = 0，无一条使用痕迹。** 竞对情报修正：此前"仅 3 个策展状态组"实为 known_states 的 3 个定性档案；策略组实为 16 个/73 技术，规模不小。但更深一层的判断**完全坐实**：出厂 KB 是纯静态先验，所有"预测/置信/学习"字段都是出厂默认值。header.md 自称 "living knowledge base ... Tracks actual vs predicted ... Learns from optimization results" 描述的是**运行时能力**而非出厂内容；README 里 "curated optimization knowledge" 的实际价值 = 技术名+一句描述+footer 的 leaderboard 高手代码示例，仅作 prompt 注入素材。且因全库 confidence 同为 0.5、pred 同为 1.0，LLM 缺席时确定性回退退化为 **73 选 1 的近似均匀随机采样**——策展先验对选择排序几乎无贡献。

## ⑥ 设计决策与竞对启示

**强度**：①定性状态表示（档位词而非数值）让匹配跨 kernel/规模可泛化，是聪明的抽象；②预测-实测-置信三件套的对账结构、滚动平均+±0.1 置信步进，是最小可用的经验学习机制；③全链路可审计（LLM 日志+变更日志+JSON 快照），复现性好。

**局限（攻击面）**：①**无硬件维度**——状态键只有瓶颈类型，没有 GPU 型号/arch 字段。跨代迁移（H100→A100 乃至非 NVIDIA）时整张状态→技术映射被默认不变；而 `actual_speedup` 是 elapsed cycles 比值，**cycles 跨架构不可比**，在 A 机累积的实测一旦随继承机制（×0.8 阻尼并不能去除机器特异性）带到 B 机，就是系统性污染。②瓶颈分类本身是机器函数（本项目 E-M1 结论）：同一 kernel 换机可落入不同状态，LLM 定性匹配的跨机失效率恰可用 oracle 真值表量化——**这是"状态分类可被真值表检验跨机失效率"攻击面的具体打点**。③出厂零实测意味着论文 demo 的记忆优势全部来自**当次 run 内累积**，跨任务迁移证据依赖运行时而非预置知识；16 状态词表 CUDA 中心（bank conflict/warp divergence 语义在 warp_size=64 硬件上变形）。④工程毛刺佐证研究代码成色：`load_databases` 引用未定义的 `default_md_path`（走到该分支即 NameError）、`__init__` 残留 `print("!!!!")`、`actual_improvement` 百分比/cycles 双语义。

**对我方定位**：KernelBlaster 的"记忆"= 静态策展先验（可注入 prompt 的教材知识）+ 单机单 run 的在线校准；它没有回答"经验跨机/跨代何时可信"。迁移定律论文的 win/trap 可交换性框架正打此空档——把"×0.8 一刀切阻尼"换成有真值表支撑的可交换性判据，即是差异化贡献点。
