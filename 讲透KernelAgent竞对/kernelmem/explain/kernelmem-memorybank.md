# KernelMem memorybank/ 深解：长期记忆资产与其门控消费链

> 对象：`memorybank/bottleneck_headroom_kernelstructure.yaml`（v2.1，1325 行，~62KB）与 `memorybank/gate_value_from_kernel_struct`（markdown 表，18 条 × 7 列）。图谱定位：layer:memory-bank「长期记忆资产层」，经 configures 边注入 machine_check_ver2 与 judger_optimization_memory_latest。

## ① 角色定位：长期记忆 vs 短期记忆的分界

KernelMem 的记忆体系按**生命周期与变更主体**切成两层：

- **长期记忆（memorybank/）**：人工策展的静态先验，跨任务、跨轮次只读。内容是"瓶颈分类学 + 结构门控规则 + 方法目录"这类不随单个 kernel 变化的领域知识。它在每轮优化开始前就已存在，是系统的"出厂大脑"。
- **短期记忆（运行时记忆）**：单任务生命周期内累积的动态上下文——每轮采集的 NCU 指标 CSV、judge_gate 产出的 code_features JSON（`round{N}_code_features.json`）、judger 落盘的 machine_check 结果，以及逐轮增长的 optimization_history（前几轮试过什么方法、瓶颈判定是什么）。这些随任务结束即弃，或在任务内滚动。

分界的本质：**memorybank 提供"什么方法在什么条件下合法"的约束知识，短期记忆提供"这个 kernel 现在处于什么状态"的观测证据**。二者在 judger 提示词里汇合——YAML 决定 allowed_methods 硬约束，history 决定"机制上不得重复已失败尝试"。

## ② 内容审计

### YAML（bottleneck_headroom_kernelstructure.yaml，machine_check 层 + llm_assist 层）

**machine_check 层（确定性门控）共 7 节：**

1. **input_normalization**：①`field_mapping`——28 个 NCU 原始键到标量字段的映射（dram/l2/l1/sm 四路吞吐、occupancy 三类限制项、long/short scoreboard 停顿的 avg+max 双份、分支分化计数等）；②`run_features_schema`——仅 `kernel_launch_count`（int，运行时提供）；③`code_features_schema`——18 个结构特征键（17 个 bool + 1 个 int `kernel_structure_id` 0..4），与 gate 表逐一对齐；④`derived_fields`——~20 条表达式，如 `primary_limiter_util_pct = max(dram,l2,sm)`、`reuse_possible = has_reuse OR is_naive_gemm OR is_gemm_kloop OR is_stencil_conv`、`bytes_structurally_unavoidable`（S0+流式+已向量化三合一）。
2. **headroom_tiers**：Tier-H（主限流器利用率 <60）/ Tier-M（60–80）/ Tier-L（>80 且字节结构性不可避免）。
3. **bottleneck_priority_rules**：1 条 BandwidthDominatesLatency（DRAM/L2 ≥80 强制判带宽，防误判 latency）。
4. **ncu_predicates**：~30 条谓词，分四族——代码结构族（reuse_possible、naive_gemm_like、gemm_rewrite_candidate、stencil_conv_like…）、吞吐族（high/mid/low 各档阈值）、occupancy/分化/停顿族、launch 开销族（tiny_kernel_duration + many_kernel_launches）。
5. **kernel_structures**：S0 流式无复用 / S1 复用友好 / S2 不规则 / S3 规约扫描 / S4 多核图，各带 detect_hints。
6. **decision_table**：8 个瓶颈桶共 ~29 个 case——memory_bandwidth（6）、gemm_tiling_needed（8，含 ncu_signature_any 四种签名组合）、l1_saturated_access_pathology（1）、memory_latency（4）、compute（4）、register_pressure/divergence（各 1）、launch_overhead（2）、code_structure_fallback（2，无 NCU 签名也可靠 gate_when 兜底）。每个 case 由 headroom × kernel_structure × gate_when 三维定位，产出 allowed/forbidden_methods + expected_speedup。
7. **guardrails**：OneMethodOnly / MechanismCheck / BenchmarkConstraints。

**llm_assist 层（门控后的非约束知识）**：bottleneck_taxonomy（4 大类 ~25 个子瓶颈各带 solutions）、optimization_techniques（6 组）、optimization_scope（4 档）、**method_catalog**（~20 个方法的 intent/mechanism_requirements/expected_metric_change/forbidden_patterns 全卡，其中 CUDA_Graph 与 GEMM_Rewrite_CUBLASLT_TF32 两个带完整 implementation_case 参考代码——GRU 静态缓冲捕获回放、cuBLASLt TF32 行主序全流程）。

### gate 表（gate_value_from_kernel_struct）

markdown 管道表，**18 个条目 × 7 列**（key / type / range / default / meaning / value semantics / LLM judgment criteria）。18 键与 YAML code_features_schema 完全一致：复用族（has_reuse、streaming_no_reuse）、向量化族（has_vector_load_store、is_aligned_vector_access、has_tail_handling_overhead、uses_vector_types）、结构族（kernel_structure_id、has_shared_memory_tile、has_bounds_check、is_pointwise、uses_transcendentals）、GEMM 族（is_naive_gemm、has_k_loop、is_gemm_kloop、is_stencil_conv）、图级族（has_multiple_kernels_in_forward、cudagraph_eligible、tc_eligible）。default 设计有倾向性：`streaming_no_reuse=true`、`is_aligned_vector_access=true`（避免过度触发限制）、`has_bounds_check=true`，其余保守 false。

## ③ 外部连接：两个消费者

**machine_check_ver2.py（规则引擎）**：`load_yaml_rules` 加载 YAML 为全部规则源；`_load_code_feature_semantics()` 在**运行时逐行解析 gate 表**，抽取 meaning/value_semantics，供 `build_code_feature_table()` 合成特征总表注入提示词。即 gate 表不是给人看的注释，而是被代码按 markdown 管道格式解析的活数据——改表即改行为。

**judge_gate.py（LLM 特征提取器）**：`build_gate_prompts(arch_path, cuda_code)` 产出 system+instruction 提示词，要求 LLM 读 PyTorch 参考实现与候选 CUDA 代码后输出**恰好 18 个字段的严格 JSON**。其判定标准长文（如 S4 优先覆盖规则、"局部 val+= 不算 reuse"、"GEMM 一律 streaming_no_reuse=false"）本质是 gate 表第 7 列"LLM judgment criteria"的展开版。调用方向是 machine_check 在 `feature_mode="llm"` 时反向 import judge_gate——judger 注入 call_llm 回调，machine_check 内部完成提取、解析（剥 ```json 围栏）、schema 校验、落盘三级流水。

上游还有 judger_optimization_memory_latest.py：`YAML_RULES_PATH` 硬指向该 YAML，先调 run_machine_check，再把结果作为 HARD CONSTRAINT 写进裁判提示词（"method_name MUST be one of allowed_methods"）。

## ④ 数据流：结构特征 → gate 值 → 方法推荐的推理链

```
CUDA 源码 + PyTorch 参考
  │ (A) 正则启发式扫描 extract_code_features_from_cuda
  │     （支持 // @has_reuse: true 手工覆盖标签，最可靠）
  │ (B) judge_gate LLM 提取（feature_mode="llm"）
  ▼
18 项 code_features → validate_against_schema（bool 归一/int 钳制/丢未知键）
  ▼ 并入 NCU CSV 归一化字段（field_mapping + 中位数聚合）
env 求值环境 → safe_eval（AST 白名单，无 eval，禁字符串/三元/属性链）
  ├─ derived_fields（reuse_possible 等复合门）
  ├─ headroom tier（H/M/L）
  ├─ ncu_predicates 匹配（结构签名 + 吞吐签名）
  ├─ 优先级规则（带宽压制延迟）
  ▼
decision_table 三维查找：瓶颈桶 × tier × S0-S4，case 级 gate_when 复核
  ▼
case = {allowed_methods, forbidden_methods, expected_speedup}
  ▼
judger 提示词（硬约束 + llm_assist method_catalog 参考实现 + optimization_history 去重）
  ▼
LLM 选定唯一方法 + 方案 → guardrails 复核 → 生成优化代码
```

关键设计：**代码结构特征能纠正 NCU 歧义**。如 naive GEMM 代码形态是 S0（无共享内存 tile），但 `reuse_possible` 经 OR 门承认"算法级复用"，落入 gemm_tiling_needed 桶拿到 large 期望加速；反之 NCU 像带宽瓶颈但 `streaming_no_reuse=true` 时，禁止 SharedMemoryTiling（CacheWithoutReuse 否决）。code_structure_fallback 甚至允许零 NCU 签名时纯靠 gate_when 触发 cuBLASLt 重写。

## ⑤ 设计决策与竞对启示

**三层可贵的工程决策**：①**机器可判与 LLM 可判分层**——所有阈值/组合逻辑进 machine_check 层用确定性求值，LLM 只在两处出场（提取结构特征、门控后写方案），且输出都过 schema 钳制，幻觉被压缩到"18 个布尔"粒度；②**gate 表作为人机共读契约**——同一份语义文档同时服务 LLM 提示词构建与特征表渲染，单一事实源；③**表达式沙箱**——AST 白名单求值器让 YAML 规则可任意编辑而不引入代码执行风险，规则热更新等于改配置。

**维护成本与可迁移性**：这套先验是纯人工策展的"专家系统复活"路线——阈值（60/80、≥96 寄存器、≥75% occupancy）全是 NVIDIA 生态经验值，换 ISA（如 NPU/warp_size=64 设备）后 field_mapping 整层失效，谓词阈值需重标定。维护负担集中在：gate 表与 judge_gate 判定长文的双写同步（已见轻微漂移风险）、decision_table case 组合爆炸（29 case 且随新瓶颈类型增长）。

**对照 KernelBlaster 的 optimization_database.json 出厂 KB**：KernelBlaster 的 KB 仅 3 个策展状态组、无实测对，状态分类可直接被真值表检验且跨机失效率构成攻击面；KernelMem 的先验则深得多——18 维特征 + 三维决策表 + 方法级 forbidden_patterns，等价于把"优化师的经验"显式编码成可审计规则而非模糊的 few-shot 案例。启示：我们的 E-M 系"oracle 真值表"恰是二者缺的第三块——KernelMem 的阈值先验没有实测校准通道（Tier-H <60 这类数字无证据链），若用真值表反向验证/修正这些阈值，就把"人工策展先验"升级成"测量锚定先验"，这正是定律位工作（win/trap 可交换性）可直接嫁接的接口。
