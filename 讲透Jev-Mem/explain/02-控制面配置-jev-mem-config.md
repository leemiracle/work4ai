> 标题：控制面配置——JevMemConfig 精讲 · 源文件：memory/jev_mem_config.py（106 行）· 图谱标签：System-One 决策控制层 / 全仓扇入冠军枢纽（file:memory/jev_mem_config.py，fanIn=14）

## 角色定位

`JevMemConfig`（`memory/jev_mem_config.py:11`）是 Jev-Mem 控制面的唯一事实来源：40 个冻结字段管住"系统今天开哪些能力、每次决策花多少钱、检索走多深"。文件头一句话定调（1）："Validated, opt-in configuration for the Jev-Mem control plane"，两个关键词都是设计承诺。**opt-in**：`write_enabled`/`read_enabled`/`admission_enabled` 默认全 False（12-14），装好不动配置就是纯 MAGMA 基线——这既是安全默认（不碰外部 API、不花钱），也是消融实验的对照组开关。**Validated**：`__post_init__`（54-87）对每个字段做类型与取值校验，配置错误在构造期爆炸，而不是运行期产出鬼数据。

它是全仓扇入冠军：图谱统计 fanIn=14（30 个枢纽里最高），grep 实证 13 个非测试源文件引用它——`jev_mem/cli.py:16`、`jev_mem/system.py:7`、`memory/jev_client.py:28`、`memory/memory_builder.py:61`、`memory/query_engine.py:54`、`memory/jev_mem_retrieval.py`、`memory/cache_compat.py`、两个 benchmark、demo、`scripts/check_public_release.py`，再加 6 个测试文件。改一个默认值等于同时动全系统行为，所以它必须是 frozen 的。

## 内部结构

`@dataclass(frozen=True)`（10）加 40 个字段（12-52），按语义分六组读：

- **总开关**（12-15）：`write_enabled`/`read_enabled`/`admission_enabled`/`jev_mock`。注意 admission 是 write 的**子开关**——写开着但 admission 关，就只做 typing 不做取舍（消费点在 `memory/memory_builder.py:137` 与 `:154` 的 if/else 分叉）。
- **决策后端**（16-24）：`decision_backend` 三选一 jev / laya / laya-mlx（远程 API / 本地 HF 模型 / Apple MLX），配 laya 四参数与 `jev_model`（21，默认 "jev-latest"）、`jev_base_url`（24，默认 `https://api.typesafe.ai`）；`decision_schema_version="noul-choice-v3-magma-temporal"`（22）与 `retrieval_schema_version="anchored-temporal-v1"`（23）——协议版本写进配置，缓存兼容检查靠它识别旧指纹。
- **调用经济学**（25-28）：`timeout_seconds=3.0`、`max_retries=2`、`cache_size=1024`、`fallback_to_magma=True`。这是**单次决策**的预算，不是查询级的（查询级见 44-45 两项）。
- **写路径阈值**（29-32）：`admission_threshold`/`relation_threshold` 各 0.60（前者管节点准入、后者管边建立，语义不同）、`candidate_top_k=10`（关系判定的候选对上限）、`admission_weights=(0.4,0.3,0.3,0.2)`——四元组前三项是 utility 权重、第四项是 redundancy 惩罚系数，解包证据在 `memory/jev_mem_policies.py:20`。
- **读路径预算**（33-46）：图预算组 `total_graph_budget=20`/`minimum_graph_budget=1`/`graph_activation_threshold=0.15`/`probability_exponent=1.5`；检索组 `anchor_count=5`/`answer_top_k=15`/`multihop_top_k=30`/`beam_width=5`/`maximum_depth=5`/`maximum_nodes=30`/`maximum_edges=200`；查询级限额 `maximum_jev_calls=10`/`max_latency_seconds=15.0`；`transition_weights` 五元组（46，图间游走权重）。
- **停止与巩固**（47-52）：`stopping_enabled`、`evidence_sufficient_threshold=0.85`、`continue_threshold=0.40`、`consolidation_interval=0`（0=关闭周期巩固）、`consolidation_threshold=0.85`、`audit_path`。

方法只有四个：`__post_init__`（54-87，约 33 行校验）、`_integer`（88-91）、`load` classmethod（93-103）、`to_dict`（105-106）。

## 外部连接

上游零第三方依赖——只有 stdlib 的 json/math/os/dataclasses/pathlib（3-7），这使它能躺在任何导入链的最底层而不引入环。下游消费者如上节所列。还有一个隐蔽的**持久化回环**：`memory/memory_builder.py:1312-1314` 在 save 时若 write/read 任一开启，就把 `to_dict()` 写成 `jev_mem_config.json`；下次 `load` 时 `memory/cache_compat.py` 的 `validate_cached_backend`（调用点 `memory/memory_builder.py:1333-1334`）校验缓存是否同一后端所建——防止拿 laya 时代的缓存喂 jev 决策。图谱把它归入 layer:system-one-control（System-One 决策控制层，6 个文件）。

## 数据流

典型流：CLI args → `JevMemConfig.load(args.jev_config, **overrides)`（`jev_mem/cli.py:58`）→ 注入 builder/client/engine → 各决策点按需读字段。`load`（93-103）的合并顺序值得背下来：读 JSON 文件（95）→ 未知键直接 raise（96-98，typo 早失败）→ 环境变量 `TYPESAFE_DEFAULT_MODEL`/`TYPESAFE_BASE_URL` 强制覆盖（99-101）→ 调用方 overrides 过滤掉 None 后覆盖（102）→ `cls(**values)` 构造并触发全量校验（103）。

具体例子：配置文件写 `{"admission_threshold": 0.7}`，shell 里 `export TYPESAFE_BASE_URL=https://staging.typesafe.ai`，调 `load("cfg.json", candidate_top_k=None)`——得到 threshold 0.7、base_url 指向 staging、其余 38 项默认的实例；若文件里多写一个 `admission_treshold`（拼错），97-98 行当场 ValueError，而不是静默忽略。

## 设计决策

**fail-fast 校验的细节**是本文件最值得学的部分：`_integer` 用 `type(value) is not int`（90）而非 isinstance——bool 是 int 的子类，`True` 会被 isinstance 放过；阈值组（65-69）显式 `isinstance(value, bool)` 排除（68）+ `math.isfinite` + 范围 [0,1]。权重组校验长度、非负、和不为零（78-81），且前三个 utility 权重至少一个为正（82-83）——这条直接对应打分公式的除法分母（`memory/jev_mem_policies.py:21` 的 `a+b+c`），配置层在防运行期 ZeroDivisionError。frozen 带来值语义：实例可哈希、可跨线程共享，运行期想改只能整体重建（或 `dataclasses.replace`）。env 覆盖只开两个 TYPESAFE 键（99-101）是最小惊讶原则——不给"环境变量偷偷改阈值"留后门，实验可复现性优先。

批判地看局限：40 个字段平铺无嵌套分组，新人难以一眼分辨"写路径的 top_k"（31）与"读路径的 top_k"（38-39 三个）；`admission_weights`/`transition_weights` 是裸 tuple，元素语义只能去消费点反查；默认值同时扮演"安全值"与"论文实验值"两个角色——改默认就是改实验配置，review 时对这文件的 diff 要格外警惕；`load` 的 overrides 过滤 None 意味着无法显式传 None（此处无妨，字段都非 Optional）。

## 新人提示

上手顺序：先读 12-16 五个开关理解能力矩阵（write/admission/read 三个独立维度的组合各有实验意义），再按需查阈值组。三个高频坑：① `write_enabled=True` 但忘了 `admission_enabled=True`，以为在测 admission 其实在测纯 typing——看节点属性 `jev_mem.admission_enabled`（`memory/memory_builder.py:164`）可确认；② `jev_mock=True` 时一切决策走 mock 函数（`memory/jev_client.py:175-181`），指标"完美"是因为没花真钱也没真判断；③ 改了问题措辞或决策语义却不 bump `decision_schema_version`（22），旧缓存会被当成兼容——`load` 只比较字符串相等，不知道语义变了。调参先看 29-32（写）与 33-46（读），这两组就是消融实验的旋钮面板。
