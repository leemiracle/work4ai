# model-router 新人上手指南（ONBOARDING）

> 图谱口径：442 节点 / 944 边 / 15 层 / 16 步 tour @dd68ef0a，fingerprints 120 文件；行号锚均经源码核实（2026-11-02）。

## ① 项目定位：一句话与生态位

**openJiuwen-router 是 openJiuwen 的模型路由内核：从请求加状态快照中挑出一个模型，核心是 Rust，端侧 crate 与云侧 wheel 共享同一份决策逻辑**（README.md:7）。宿主调 `Router::route`、自己调被选模型、再 `report` 结果——路由器不在流量路径上（README.md:23）。

生态位是**骨架阶段的插件化内核**：README.md:19 自声明 Weighted 算法、remote state gRPC、完整 PyO3 绑定仍是 stub；唯一非 stub 算法是 Stage Router，最完整应用层是 Python 侧 x-router 五档路由 + bandit 闭环。

## ② 技术栈与代码形态

- **Rust**：Cargo workspace 五成员（Cargo.toml:3-9），`default-members` 排除 crates/py——日常 `cargo build/test` 无需 PyO3 工具链。依赖极简：serde、toml、pyo3 0.23 abi3-py38（Cargo.toml:30）；protocol crate 零依赖。
- **Python**：maturin 打同一份源码出 wheel（pyproject.toml:24）；torch/transformers 是可选 extra（pyproject.toml:11-17），classifier 引擎懒加载 torch。
- **类型形态**：`.pyd` 产物不在仓内，跨边界类型由 `_openjiuwen.pyi`（202 行静态桩）+ py.typed（PEP 561）代表。
- **双解析器**：同一份 TOML 两个消费者——顶层键归 Rust `RouterProfile`（crates/runtime/src/config.rs:9-16），`[x-router]` 表归 Python `build_router()`（config/x-router-example.toml:1-2 注释即分界）。

## ③ 目录结构导览（对应图谱 15 层）

| 图谱层 | 位置 | 一句话 |
|---|---|---|
| L01 | Cargo.toml / pyproject / typings | 五成员与双语言构建链 |
| L02 | README(.zh).md / docs/{zh,en}/ | 双语总览；中文版多欧盟 AI 法案合规表述 |
| L03 | crates/protocol/ | 零依赖词汇表，类型全带硬上限 |
| L04 | crates/state/ | StateProvider 契约 + MemoryState / RemoteState（骨架） |
| L05 | crates/algorithms/（除 stage_router） | 双 Provider 契约 + test_algo 五 stub |
| L06 | algorithms/src/stage_router/ | 唯一真实算法（688 行含 10 内联测试） |
| L07 | crates/runtime/ | Router 门面、decide_loop、registry、config、training/trigger 骨架 |
| L08 | config/*.toml | edge/cloud/stage_router/x-router-example 四份 profile |
| L09 | crates/py/ | 15 pyclass、convert.rs 转换中枢、adapter 反向绑定 |
| L10 | python/openjiuwen/ | Python 门面、双槽契约、discover 自动注册 |
| L11 | test_algo{,2}/ + custom_test_algo/ | 算法槽三个消费者样本 |
| L12 | x_router/（前半） | 五档复杂度分类与决策 |
| L13 | x_router/（后半） | bandit 闭环：bandit/bandit_store/judge/service |
| L14 | examples/ | 双语宿主闭环、x-router CLI 与 bandit 演示 |
| L15 | tests/ | pytest 全家 + 双语 ReAct 宿主示例 |

## ④ 核心数据流：一次路由请求的完整旅程

以 `config/stage_router.toml` 装配的 Router 为例：

1. **装配**：`Router::from_config` 解析 TOML（config.rs:53-58）→ 按名建算法（router.rs:60）→ 按 backend 建 state（router.rs:74-97）。
2. **route 入口**：宿主持 `RouteRequest` 与 `RouteHint` 调 `Router::route`（router.rs:119）。**route_id 在读 state 之前生成**（router.rs:125，pid-纳秒-序列号 :141-149）——state 的 query 要靠它关联稍后的反馈，算法全程拿不到（:121-124）。
3. **决策循环** `decide_loop::run`（decide_loop.rs:41-65）：`read_state` 有检索意图走 `state.query`（带 route_id :25），否则或失败降级 `snapshot`（:22-29）；合并请求排除与视图排除（:52-54）；`catalog.without` 过滤（:56）；装配只读 `RouteContext`（:58-63）；调 `algorithm.decide`（:64）。
4. **返回 Decision**：reasoning 必填；route_id 由 runtime 回填（router.rs:136），算法不接触。
5. **宿主执行**：宿主自己调被选模型——在路由器之外，即"决策与执行分离"。
6. **回报闭环**：`Feedback` 走 `try_report`（router.rs:159-163）——校验不过**不写 state**；兼容入口 `report` 静默丢弃（:169-173）。MemoryState：Overflow/Unavailable 进排除表（memory.rs:131-134），Ok 更新亲和（:137-139）。下一轮经 StateView 回到第 3 步。

## ⑤ 关键模块深潜

### 5.1 StageRouter：唯一真实算法（algorithms/src/stage_router/mod.rs）

无状态、efficient-first、信号不足 fall-open（:162）。`decide`（:170-195）取目标集第一个为 efficient 档、第二个为 capable 档（:171-172；次序约定 stage_router.toml:1）。决策四态（assess_stage :324-363）：上下文被压缩（标记串 "session is being continued" :12）或临界失败 → SafetyOverride 升 capable（:325-332）；干净测试跑过且有产出 → VerifiedProgress 回 efficient（:333-340）；否则证据向量（failure/stalled/investigation/delivery_ratio）经 tanh 打分（:275-279），置信度过 0.5 按 score 正负选档（:344-352）；不够 → fall_open 回 efficient（:353-355）。证据全是字符串观察：11 组失败签名（:32-96）+ 工具分类表（:98-146）；十个内联测试即行为规格书。

### 5.2 registry 与 config：单槽装配的 Rust 侧

`create_algorithm`（registry.rs:12-30）六分支全 `#[cfg(feature)]` 门控——五个示意算法取自 test_algo，**stage_router 是唯一正式实现**（:21）。**批分析勘误钉版：五个示意"算法"是同构 stub**——每个恰好 21 行，decide 全是"剔除排除后取首个目标"（passthrough.rs:13-19 与其余四者逐行同构）；weighted 没有权重表——读它们是学接入不是学算法。RouterProfile 只认四个顶层键（config.rs:9-16），"端云差异收敛在配置，不在代码分叉"（config.rs:1）。

### 5.3 MemoryState 与"假 LRU"勘误

`backend = "memory"` 的实现（memory.rs:18-22）：TTL + 容量上限。**勘误钉版：L1 注释自称"TTL + LRU 上界，骨架阶段用容量上限代替完整 LRU"，而 L114-118 淘汰实为 `map.keys().next()`——HashMap 迭代序无语义，淘汰的是任意条目而非最旧**；L113 注释"移除最旧的条目"与实现不符。对可丢失 hint 无伤，但别当 LRU 推理。delayed 反馈（无 call 字段）不计数（:108-110），内联测试 :44-65 覆盖聚合语义。

### 5.4 x-router：五档分类 + bandit 闭环（python/openjiuwen/x_router/）

facade.py 是**内核三缺口的吸收层**（:1-25 docstring）：①算法槽收不到 profile 参数 → `specialize()` 生成带参数的配置子类、类定义即注册（algorithm.py:129-148），注册名取 profile 自己的 algorithm 名（facade.py:207-221），故 registry 无 "x-router" 也能装配；②协议层只收 str content → `normalize_messages` 展平（facade.py:81-102），不展平则 route() 内炸，宿主兜底后会"看似健康地"全部本地路由；③自定义 state 收不到 [state] 参数 → BanditStore 从 `[x-router.bandit.store]` 读配置以实例注入（facade.py:158-191 双声明互检，缺一即拒绝）。

决策流（algorithm.py:86-126）：`classify()` 定档（complexity.py:269 起永不抛错：无后端→heuristic、后端失败→heuristic_fallback）→ 可选 bandit `choose_tier()` 覆写（bandit.py:165：邻居不足判 cold :174，最优档超不出 margin 不动 :194）→ `decide_by_tier()` 选模型（algorithm.py:34-52：档位≤本地能力走本地，目标被排除只降不升）→ 输出 rule/tier/source 结构化 reasoning（:118-120）。bandit 效用来自 judge 固定 rubric（judge.py:62，权重是量尺不是参数），记忆由 BanditStore 两阶段写入 + kNN 余弦检索承担（bandit_store.py:59）。

## ⑥ 设计决策与权衡

- **决策与执行分离**：算法只返回 selected_model_id + reasoning，调模型是宿主的事（algorithm_provider.rs:5-13 三条边界：不得调被选模型 / 可自带决策辅助模型 / 调用应无状态）。代价是看不到执行现场，收益是可嵌入任何宿主。
- **算法纯函数**：同 `(request, ctx)` 必同 Decision（algorithm_provider.rs:3），随机性经 seed 显式注入（:32）保可重放。纪律不靠框架强制——Python 侧 `check_purity` 双调用比对辅助验收（algorithm_provider.py:86-95）；x-router 带 LLM 后端明确禁用它（algorithm.py:71-77），改用 decide_by_tier 真值表。
- **状态外置、可丢失**：StateProvider 是有界 hint（state_provider.rs:18-20），query/publish 均有默认实现（:42-49 降级 snapshot、:59-62 no-op），远程超时须返回空视图而非 Err——丢失只降质为冷路由。
- **决策与演进分离**：EvolvingProvider.fit 纯计算、产不可变 Artifact（evolving_provider.rs:67-72），拉数据与 CAS 写回归 runtime——训练不污染决策路径。
- **单槽装配**：一个 Router 一个算法槽 + 一个状态槽（router.rs:26-33），候选进 registry、profile 选名，零分发开销。
- **PyO3 双语言同一内核**：Python 算法反向包装成 Rust trait（adapter.rs:30-56，进程内 OnceLock 注册表 :14-17），`__init_subclass__` 类定义即注册（algorithm_provider.py:74-76），扩展未构建时入 pending 队列（:36-41）；代价是每次 decide 跨 GIL + convert.rs 双向转换。

## ⑦ 常见任务上手

**加一个 Rust 算法**：实现 `AlgorithmProvider`（name + decide）→ registry.rs 加 `#[cfg(feature)]` 分支 → algorithms 与 runtime 两个 Cargo.toml 加同名 feature → TOML 写 `algorithm = "名字"`；照 stage_router/mod.rs 抄最稳。

**加一个 Python 算法**：继承 `AlgorithmProvider`，设类属性 `name`、覆写 `decide(request, ctx)`、**必须无参可构造，配置放类属性**（algorithm_provider.py:44-57 校验三连，违反即 TypeError）——CostAware 的冻结成本表 MappingProxyType 就是该约束下的惯例。类定义完成即注册（:74-76）；包内算法由 discover 扫描安装，包外 import 即注册（custom_test_algo/prefer_first.py + run_custom_algorithm.py 端到端断言）。

**改 TOML profile**：顶层四键看 config.rs:9-45；`[x-router]` 段看 facade.py build_params（:116-132）与 x-router-example.toml 内嵌注释（bandit 默认整段注释，开启需同时设 `[state] backend = "x-router-bandit"`，缺一即 ParamsError）。

**跑测试**：Rust `cargo test`；Python 先 `maturin develop` 编出 `_openjiuwen` 再 `pytest`（conftest.py 把仓内 python/ 插到 sys.path 首位）。test_x_router_live.py 是唯一加载真分类器权重的冒烟，未设 `X_ROUTER_CLASSIFIER_MODEL` 整文件 skip。

## ⑧ 新人提示与坑

1. **五个示意算法是同构 stub**（5.2）：weighted 里没有权重逻辑。
2. **MemoryState 不是 LRU**（5.3）：HashMap 任意序淘汰，注释与实现不符。
3. **x-router 无分类器必须显式 `enabled = false`**：`[classifier_model]` 段缺失/为空、或有段无 model_path 都是 ParamsError 部署错误而非降级（classifier/backend.py:54-66）——理由："静默永不升档的路由器看起来很健康"。
4. **RemoteState 是骨架**：snapshot 恒空视图、gRPC 未接线——cloud.toml 能装配成功但云侧状态不存在。KvCacheCoordinator 只存不触发（router.rs:20-23）；evolving 的 TriggerSpec 七变体同是调度骨架。
5. **report 静默丢弃非法反馈**：感知原因用 `try_report`（router.rs:167-173）。
6. **x-router 的 decide 同步阻塞**（algorithm.py:64-69）：async 宿主勿在协程里直调。
7. **normalize_messages 丢非文本部分**（facade.py:85）：x-router 只读文本故无损，别当通用工具用。
8. **route_id 生成时机是刻意的**：先于读 state、算法拿不到、宿主填的被覆盖——router.rs:121-124 注释是权威解释，测试 router.rs:312-361 钉死时序。
9. **骨架预期管理**：README.md:19 明说本仓是蓝图骨架——契约先行的内核，非生产就绪。
