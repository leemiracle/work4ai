# 06 · crates/runtime/src/config.rs 与顶层 TOML profile：双解析器分界

## 一、角色定位：一份文件、两个读者、一条楚河汉界

model-router 的配置故事有一个不寻常的设计：**同一个 TOML 文件被两个独立的解析器先后读取，各取所需，互不越界。**证据写在 `config/x-router-example.toml:1-2` 的头注释里："The Rust profile parser reads everything above [x-router]; the [x-router] table is read by openjiuwen.x_router.build_router()." Python 侧的呼应同样直白（`python/openjiuwen/x_router/facade.py:50-52`）：`SECTION = "x-router"`，注释"The Rust profile parser ignores unknown tables, so it can live in the same file as the kernel's own configuration."

这条分界能成立的技术前提有两个：其一，`config.rs` 的 `RouterProfile` 是普通 serde `#[derive(Deserialize)]` 结构体（`config.rs:8-16`），**没有** `#[serde(deny_unknown_fields)]`——未知表静默忽略；其二，Python 3.11+ 的 `tomllib` 是完整 TOML 解析器（`facade.py:55-68` 的 `_load_toml`，3.11 以下回退 `tomli` 依赖，都没有则抛 ParamsError 要求"install it, or pass configuration as a dict"）。

于是"端云差异全部收敛在配置，不在代码分叉"（`config.rs:1`）有了完整含义：内核四个顶层键管装配骨架，`[x-router]` 子树管 Python 算法的全部参数，两者共享同一份文件、同一个 `algorithm = "..."` 入口——profile 依然是"single source of truth"（`facade.py:198-200` 原话）。

## 二、内部结构

### Rust 侧：config.rs 的四个键（68 行收拢全部内核配置）

`RouterProfile`（`config.rs:8-16`）的键空间：

- `algorithm: String`——必填，算法槽名字；
- `state: StateConfig`（L18-30）——`backend`（"memory" | "remote"）+ 四个可选参数（`ttl_secs` / `max_entries` / `endpoint` / `timeout_ms`，全部 `#[serde(default)]`）；
- `targets: TargetsConfig`（L32-36）——`models: Vec<String>`，默认空表（空 targets 意味着第一次 route 就 NoTarget，装配期不拦——见坑节）；
- `evolving: Vec<EvolvingJobConfig>`（L38-45）——训练任务数组，`name` 必填，`kind` / `slot` 可选。

两个加载入口：`from_path`（L53-58，读文件失败包成 `RouterError::Config("read {path}: {e}")`）与 `from_toml`（L65-67，解析失败包成 `"parse toml: {e}"`）。全部错误收敛到 Config 变体——启动期暴露（`error.rs:1` 的原则）。

**整个 Rust 内核的配置就这 68 行**：没有环境变量插值、没有 include、没有继承——连算法参数都不存在（算法槽无参构造的契约后果，见第 3 篇）。

### config/ 目录：四份 profile 的光谱

- `edge.toml`（10 行）：`algorithm = "passthrough"` + `[state] backend = "memory"` + 300s/1024 + 单目标 `["local-default"]`——端侧最小形态。
- `cloud.toml`（15 行）：`backend = "remote"` + endpoint `http://127.0.0.1:50051` + `timeout_ms = 5` + 双目标 + `[[evolving]]`（mf-weights 任务，slot = "state.mf_weights"）——云侧形态（虽然 RemoteState 目前是返回空视图的 stub）。
- `stage_router.toml`（10 行）：头注释即协议——"第一个目标是高效模型，第二个是能力模型"（L1），models 顺序 `["efficient-model", "capable-model"]`。
- `x-router-example.toml`（77 行）：唯一的带 `[x-router]` 样本，也是本文的主角。

### Python 侧：[x-router] 键空间全图

以 x-router-example.toml 为地图逐层看：

**第一层 `[x-router]`（L13-16）**：`local_capability_level`（"SIMPLE".."REASONING" 或 **"NONE" 禁用本地档**——`types.py:379-383` 解析为 None，此后"everything escalates and the local model survives only as a degrade target"，`x_router/algorithm.py:40-42`）、`local_model`（本地档模型名兼降级目标）、`classifier_preview_chars`（默认 6000，下限 256，`types.py:40`）。

**`[x-router.tier_models]`（L18-21）**：档位 → 云模型映射。铁律（`types.py:319-323`）：**COMPLEX 档必须定义**（`FALLBACK_TIER`，types.py:37）——未配档位自动落 COMPLEX 模型（`model_for`，types.py:340-343）；未定义 COMPLEX 直接 ParamsError；档位名拼错也在装配期被 `ComplexityLevel.parse` 拒绝（"rejects typos at assembly time"，`types.py:312`）。五档 IntEnum SIMPLE=1..REASONING=5（types.py:74-86），"Ordering is the whole point"（L77）——`tier <= capability` 的整数比较就是路由判定。

**`[x-router.classifier_model]`（L25-35）**：`enabled`（默认 true）/ `model_path` / `device`（"auto"=CUDA 可用则 cuda:0 否则 cpu）/ `dtype`（"auto"=CUDA 上 bf16、CPU 上 fp32，注释算账 0.6B 约 1.2GB）/ `max_input_tokens = 4096` / `max_tokens = 16`。分类器**在本进程跑**："there is no server to start"（L23-24）。

**`[x-router.bandit]` 与 `[x-router.bandit.store]`（L37-59，默认注释掉）**：bandit 半场（`min_neighbors`/`margin`/`lambda_c`/`cost_ref_usd`）与 store 侧（`retriever_dim=4096`、`max_entries=2000` FIFO（注释给出内存估算 ≈2000×4096×4B）、`top_k`、`min_similarity`、`forgetting_gamma`、`pending_ttl_secs`、`exclusion_ttl_secs`）。

**`[x-router.judge_model]`（L61-77）**：`kind = "local"`（本进程权重）或 `kind = "api"`（OpenAI 兼容端点 + **`api_key_env` 是环境变量名不是 key 本身**，L75 特意强调）。

### facade.py：装配流程与三道防线

`build_router(config, backend=None, state=None)`（`facade.py:194-225`）的流程：

1. `load_profile`（L71-78）：config 是 str 走 `_load_toml`，是 Mapping 直接 `dict(config)`，否则 ParamsError；
2. 检查 `algorithm` 非空（L207-209）；
3. `build_params`（L116-132）：取 `[x-router]` 段（缺失即 ParamsError "profile has no [x-router] section"）→ 构造分类器 backend → `XRouterParams.from_mapping` 校验 → `validate_against(profile["targets"]["models"])`——**每个可选模型必须在 [targets] 里**（`types.py:354-368`，错字模型 id 在装配期暴毙而非线上 404）；
4. `_resolve_state`（L158-191）：bandit store 的**双声明一致性检查**；
5. 分类器 warmup（L213-219）——注释值得整段读："At request time a failure degrades to the heuristic on purpose, so a model that never loads would otherwise show up as a router that quietly stops escalating — healthy-looking and wrong."（请求期故意降级，所以坏模型必须死在装配期）；
6. `specialize(params, name)`（`x_router/algorithm.py:129-148`）动态生成带参数的子类并以 profile 的 algorithm 名注册（定义即注册，`__init_subclass__` 机制）；
7. `Router.from_config(config)`（state 为 None）或 `Router.from_config(config, state=state)`（L223-225）——进入 Rust 装配，此时 Python 注册表里已有该名字，`py/lib.rs:100-103` 的 Python 优先查找接管。

**双声明协议**（`_resolve_state`，facade.py:158-191）是 bandit 的安全带：`[state] backend = "x-router-bandit"`（`bandit_store.py:59` 的 `STORE_BACKEND`）与 `[x-router.bandit.store]` 表**必须成对出现**——"is configured but [state] backend is ..."（L175-178）与反向（L180-184）两种错配都直接 raise。注释（L160-166）解释了为什么：内核要求 backend 名字但带不了参数（DESIGN.md G6），双声明让"忘了任何一边"都无法静默产生一个"bandit 永远不热身"的路由器。还有一个降级警告：bandit 启用但 state 是普通后端时 warn "the bandit will report `cold` on every request"（L185-190）。

### 第三条通道：dict 配置（py/convert.rs）

Python 宿主可以不落盘直接传 dict：`profile_from_obj`（`py/src/convert.rs:797-811`）对 str 走 `RouterProfile::from_path`，对 dict 走 `profile_from_dict`（L814 起，手工提取 algorithm/state/targets 三键——注意 `[[evolving]]` 在 dict 通道中不被解析，差异点）。而 `build_router` 收 dict 时 Python 侧 `load_profile` 原样返回 dict，`[x-router]` 键照常可读。dict 通道是为配置中心（etcd/环境变量拼装）准备的，`py/lib.rs:48` 注释直言"dict 便于配置中心注入"。

## 三、外部连接

- **config.rs 被谁用**：`Router::from_config/from_toml/from_profile`（`router.rs:41-67`）与 `state_from_profile`（L74）；py 的 `profile_from_dict` 手工重建同构结构体。
- **[x-router] 被谁用**：只有 `facade.py` 一家（SECTION 常量）；`service.py`（请求侧）不读配置，只消费 params 实例——"Everything here runs once, at start-up"（`facade.py:9-10`）。
- **targets 的双重身份**：Rust 把它当目录（TargetSet 装配）；Python 拿它做 validate_against 的对账基准。两边读的是同一份数据。
- **judge 的旁路**：`build_judge`（`facade.py:228-250`）只读 `[x-router.judge_model]`，产物不进 Router——judge 由宿主持有，在每个模型调用后跑分（`facade.py:60-63` 注释），分数经 Feedback 回流 bandit。

## 四、数据流：一次 build_router 的键值旅行

输入 `config/x-router-example.toml`：

1. Python `load_profile` → 完整 dict（含 x-router 键）；
2. `[x-router]` → `XRouterParams`（校验五档映射、COMPLEX 兜底、preview 下限）；
3. `[x-router.classifier_model]` → `LocalBackend`（或 enabled=false → None → 启发式）；
4. `[targets] models` → 对账所有 tier_models + local_model 都在列；
5. `[state]`（memory）+ 无 bandit.store → state 解析落回 Rust `state_from_profile` → `MemoryState(300s, 1024)`；
6. `specialize` 注册 "x-router" 名；
7. `Router.from_config(path)` → Rust 再次从磁盘读同一文件 → serde 解析出 algorithm="x-router" / state / targets（`[x-router]` 被忽略）→ py assemble 的 Python 注册表命中 XRouter 子类 → `from_parts` 完成。

**注意第 7 步：文件被读了两遍**（Python tomllib 一遍、Rust serde 一遍）。这是双解析器的自然成本——换来的是内核对 Python 配置的零知识。

## 五、设计决策与权衡

**为什么双解析器而不是内核支持任意参数表？** 内核保持极简（68 行 config、四个键），`[algorithm.params]` 之类的通用机制会引入"内核必须理解所有算法参数形状"的耦合。facade docstring 明说这是权宜："When the kernel grows an [algorithm.params] table, this collapses into Router.from_config"（`facade.py:13-15`）。代价是文件读两遍、一致性要手工对账——退出条件写在了墙上。

**为什么 classifier 缺失必须显式 enabled = false？** `classifier/backend.py:53-58`："An absent section, or one with no weights, is a deployment mistake rather than a request for heuristic mode: left to resolve itself it would produce a router that silently never escalates, which looks healthy from the outside."（缺失段=部署事故而非启发式请求。）只有 `enabled = false` 才返回 None 走启发式。与 warmup 强制（facade.py:213-219）构成同一原则的两道闸：**所有"会静默降质"的配置错误都要在装配期爆炸。**

**为什么 bandit 要双声明？** 内核 state backend 只认名字不认参数，参数只能走 Python 侧子表；两个声明点意味着两处可能不一致，`_resolve_state` 把不一致变成硬错误——用"显式麻烦"换"无声错误"。

**砍掉了什么？** 无环境变量展开（`api_key_env` 是唯一 env 语义，只给 judge 的 api 模式）、无 include、无热重载、无 schema 导出——TOML 键名即 schema，错字靠 ParamsError 消息定位。

## 六、新人提示与坑

1. **顶层键与 [x-router] 的边界要记牢**：`ttl_secs`/`max_entries` 是 Rust `[state]` 的；`retriever_dim`/`top_k` 是 Python `[x-router.bandit.store]` 的。把 bandit.store 的键写进 `[state]` 会被 serde 静默吞掉（未知字段忽略），无任何报错。
2. **`algorithm = "x-router"` 单独给 Rust 会装配失败**：Rust registry 没有这个名字（`registry.rs:13-29` 只有六个 Rust 算法），必须走 `build_router`（Python 先注册）。用 `Router.from_config` 直连 x-router profile 报 "unknown or disabled algorithm"。
3. **dict 通道与 TOML 通道不等价**：`[[evolving]]` 数组在 `profile_from_dict`（convert.rs:814+）中不解析——用 dict 装配的宿主没有训练任务。
4. **tier_models 的 COMPLEX 是法定兜底**：只配 RESEARCH/REASONING 不配 COMPLEX 会 ParamsError（`types.py:319-323`）；SIMPLE/MEDIUM 未配时自动落 COMPLEX 的模型（`model_for`，types.py:340-343）。
5. **timeout_ms 是毫秒**：cloud.toml 的 `timeout_ms = 5` 是 5 毫秒不是 5 秒；RemoteState 反正返回空视图，但换成真实现后这个值会让所有远程读秒级超时降级。
6. **`api_key_env` 是变量名**：填成实际 key 字符串不会报错——只会让 judge 在运行期找不到环境变量而失败。这是全配置里唯一一处"错了不立即炸"的地方。
7. **stage_router.toml 的顺序约定无校验**：models 顺序写反，算法照跑但档位语义全反（efficient 位上是 capable 模型）。此坑在第 4 篇已钉，配置篇再强调一次：这份文件的头注释就是全部规格。
