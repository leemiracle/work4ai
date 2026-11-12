# 05 · crates/runtime/src/router.rs 与 decide_loop.rs：装配与决策循环

## 一、角色定位：把插件组装成机器的总装车间

L4 运行层是宿主真正接触的东西——`lib.rs:1` 一句话定调："宿主只看 `Router`；北向契约是 `RouterProvider`。"这个 crate 自己不包含任何智能（算法在 L3、记忆在 L2、词汇在 L1），它的全部价值是**装配的正确性**与**循环的纪律**：把一个算法实例、一个 state 实例、一份目标集合，按 profile 组装成一台能回答"这次选谁"的机器，并保证每次问答经过同样的关口。

七个模块各司一职（`lib.rs:3-9`）：`config.rs`（profile 解析，见第 6 篇）、`registry.rs`（算法名 → 实例）、`router.rs`（门面）、`router_provider.rs`（北向 trait）、`decide_loop.rs`（单次决策循环）、`training.rs` + `trigger.rs`（自演进调度骨架）。本篇聚焦 router.rs（381 行）与 decide_loop.rs（65 行）这对"门面与引擎"。

分层的装配图：`Router::from_config(path)` → `RouterProfile::from_path` → `from_profile` → `registry::create_algorithm` + `state_from_profile` → `from_parts`。每一层都可单独调用（PyO3 走的是旁路，见下文），但终点都是 `from_parts`（`router.rs:100-112`）——算法 `Box<dyn AlgorithmProvider>`、state `Arc<dyn StateProvider>`、目标 `TargetSet`、种子计数器清零、kv_coordinator 置 None。

## 二、内部结构

### Router 结构体（router.rs:26-33）

五个字段就是运行期的全部世界：`algorithm`（boxed trait object——单槽）、`state`（Arc 共享——反馈与检索共用）、`targets`（装配期定死的目录）、`seed: AtomicU64`（每请求自增的种子源，`route` 里 `fetch_add`，L120）、`kv_coordinator`（KV cache 协调回调，骨架"仅保存，不触发"，L20 注释 + L31 的 `#[allow(dead_code)]` 自认未接线）。

### 四级装配入口（router.rs:41-112)

`from_config(path)` / `from_toml(text)` / `from_profile(profile)` 是便利阶梯，全部塌缩到 `from_parts`。值得单讲的是 **`state_from_profile`（L74-97）被做成 pub 的原因**（L69 注释）："供 PyO3 在注入 Python StateProvider 前复用"——py crate 的装配需要单独拿到 state 时（比如三段查找失败后落回 Rust 实现，`py/src/lib.rs:104-110`）直接调它，不必经过 from_profile 全流程。

state 分派逻辑（L77-96）：`"memory"` → `MemoryState::new(ttl.unwrap_or(300), max_entries.unwrap_or(1024))`；`"remote"` → endpoint 必填（缺失即 `RouterError::Config("remote state requires endpoint")`，L84-87）、timeout 默认 **5ms**（L88）；其他名字 → `Config` 错误。错误全部走装配期通道——与 `error.rs:1` 的"装配期错误在启动时暴露"对齐。

### route：route_id 的诞生地（router.rs:119-138）

一次路由的前三步都发生在这里，顺序有讲究：

1. `seed = self.seed.fetch_add(1, Relaxed)`（L120）——每请求单调递增，喂给算法保证可重放；
2. `route_id = Self::next_route_id()`（L125）——注释（L121-124）讲了完整动机："**先于读 state 生成**：state 的 query 需要它来关联之后带同一 id 回来的反馈。算法仍然拿不到它——它不进 RouteContext，只在 run 返回后写入 Decision。路由和反馈是拆开的两步……中间没有别的主键能把这两次调用绑成同一笔决策，所以 runtime 先发一个 id。"
3. `decide_loop::run(...)` 拿到 Decision 后，`decision.route_id = Some(route_id)`（L136）回填。

`next_route_id`（L141-149）的格式是 `{pid}-{unix_nanos}-{seq}`：静态 `AtomicU64` 序列保证"同进程不同 Router 不重号；不承诺分布式唯一或去重"（L140 注释——诚实的能力边界声明）。时间戳在 fetch 之后取，保证字典序大致按时间。

### 反馈双入口：try_report 与 report（router.rs:151-173）

`try_report` 是**跨语言一致的唯一校验入口**（L151-154 注释原话）："校验不过的反馈不写入 state，并以 FeedbackError 返回原因。Python 门面同样走这里。"先 `feedback.validate()`（版本/扩展预算全查），再 `state.report`。`report` 是兼容入口，内部委托 try_report，非法反馈"丢弃且不写入 state"（L167）——静默但安全。测试 `invalid_feedback_does_not_reach_state`（L256-307）把这条纪律钉死：坏版本号、NaN 载荷、旧入口，三种非法路径之后 `sample_count` 恒 0。

### RouterProvider（router_provider.rs:11-39）与 trait 实现

北向契约只有四个方法：`route`（返回 **ModelSelection** 而非 Decision——"跨边界规格"，L4-5 注释）、`try_report` / `report`、`algorithm_name`。`Router` 的实现（`router.rs:189-209`）是薄转发 + `ModelSelection::from` 投影。宿主持有 `&dyn RouterProvider` 即可路由——不依赖具体 Router 类型，这让 Python 适配层或未来其他门面能实现同一契约。

### decide_loop::run：65 行的决策循环（decide_loop.rs:41-65）

签名七个参数（算法、state、请求、hint、目录、种子、route_id），函数体只有三段：

1. **读状态** `read_state`（L13-31）：`hint.state_query` 为 None → `snapshot`；Some 但 `is_empty() || validate().is_err()` → 还是 `snapshot`（L22-24——非法查询静默降级，不报错）；合法 → `query(key, query.with_route_id(route_id))`（L25）。对 query 结果又是三态：合法快照用 (view, retrieved)；快照自身校验不过 → 只用 view 丢弃 retrieved（L28）；Err → 整体退回 snapshot（L29）。**检索能力在任何故障形态下都不影响路由可用性**——这是 L7 注释"绝不让检索能力影响路由可用性"的四重落实。
2. **合并排除**（L52-56）：`req.exclusions` ∪ `view.exclusions` → `catalog.without(&exclusions)`。注意方向：请求的排除（宿主重试）与状态的排除（Overflow/Unavailable 拉黑）在这里合流，算法看到的是已净化的 targets。
3. **调算法**（L58-64）：打包 `RouteContext{targets, view, retrieved, seed}` → `algorithm.decide(req, &ctx)`。

route_id 参数的注释（L35-37）再次强调分工："这里只把它交给 state 的 query；写回 Decision 仍由调用方完成，算法全程不接触它。"

### 周边三件：registry / training / trigger

`registry.rs:12-30` 的 `create_algorithm` 是编译期裁剪的 match：六个算法名各挂 `#[cfg(feature)]`，未启用的 feature 连 match 臂都不存在（名字落入 L26-28 的 `unknown or disabled algorithm` 错误）。`training.rs` 是训练骨架：`DataSelector`（"骨架返回空 batch"，L8；双通道语义见 L10-19 注释）、`TrainingJob::run_once`（L57-61：select → fit → "丢弃工件。真实写回走 StateProvider::publish"）。`trigger.rs` 定义七态 `TriggerSpec`（Startup/Delay/Interval/Cron/Threshold/Event/Composite，L10-33）与 `Trigger` trait，原则一句话（L1）："判定在 runtime，不进算法。"`TriggerRegistry` 骨架"只保存规格"（L65）。

## 三、外部连接

- **上游依赖**：四个 crate 全用上——protocol（类型）、state（`router.rs:13` 引入 `test_state as backends`）、algorithms（registry 的样本来源）、加 serde/toml（config 解析）。
- **被 py 消费**：`py/src/lib.rs:96-114` 的 `assemble` 是本层装配的**平行实现**而非调用——算法解析顺序：`adapter::lookup`（Python 注册表）优先，`registry::create_algorithm` 兜底（L100-103）；state 解析三段：显式注入 > `state_adapter::lookup`（Python 后端，如 x-router-bandit）> `Router::state_from_profile`（L104-109）。这就是 Python 算法（x-router）能顶掉同名 Rust 算法的机制所在。
- **被 Rust 宿主消费**：`examples/rust_integration/src/main.rs` 直接用 `Router::from_config` + `route` + `report`；集成测试 `tests/react_agent.rs` 走完整闭环。
- **被 Python 门面消费**：`python/openjiuwen/__init__.py:126-160` 的 Router 包装类，把同步内核调用再包成 async（`route`/`report` 的 async 方法只是直通 `route_sync`，L143-153——**伪异步**，云侧蓝图形态，真异步要靠宿主 executor）。

## 四、数据流：一次完整路由的十二步

宿主视角，`router.route(req, hint)` 内部：

1. `seed.fetch_add`（router.rs:120）；
2. `next_route_id` 生成 pid-time-seq（L125）；
3. 进 `decide_loop::run`（L126-135）；
4. `read_state`：无查询意图 → `state.snapshot(routing_key)`（decide_loop.rs:19-21）；
5. 有意图且合法 → `state.query(key, query.with_route_id(route_id))`（L25）；
6. 合并 exclusions、过滤 targets（L52-56）；
7. 组 `RouteContext`、调 `algorithm.decide`（L58-64）；
8. 决策返回，`route_id` 回填（router.rs:136）；
9. 宿主收到 Decision（或经 RouterProvider 投影为 ModelSelection，L195）；
10. 宿主按 `selected_model_id` 调真实模型（runtime 从不碰这步）；
11. 宿主把结果包成 `Feedback`（带同一 route_id）调 `try_report`（L159）；
12. 校验通过 → `state.report`，更新下一次路由的 StateView。

闭环成立：第 12 步的写入是第 4 步未来的读取。route_id 让 5 与 11 可关联（state 可开待回填记录），seed 让 7 可重放。

## 五、设计决策与权衡

**为什么 route_id 在 runtime 生成而不给算法？** 关联性是横切关注点：StateQuery 要它（关联检索）、Decision 要它（回溯解释）、Feedback 要它（关联结果）。若算法生成，纯函数契约被破坏（同一输入产出不同 id）；若宿主生成，三个消费点可能填不一致。runtime 是唯一同时接触三者的层，由它统一发号、事后回填，算法保持无菌。

**为什么读状态的降级做四层而不是返回 Err？** 一次路由的可用性优先级高于状态精度。返回 Err 意味着宿主要写 fallback 逻辑，每个宿主都要写一遍；在这里降级，宿主拿到的一定是可用 Decision（最坏 fall_open 到冷路由）。这与 state 层"超时返回空视图而非 Err"（state_provider.rs:20）是同一条哲学在两层的实现。

**为什么装配与运行分开（from_parts 的存在）？** 给 PyO3 留注入点：Python 宿主可以塞 Python 算法、Python state 进同一台机器（`py/lib.rs:111-113` 直接 `Router::from_parts`）。如果只有 from_profile 一条路，跨语言插件就没有入口。代价是 Rust 宿主也能绕过 profile 校验直接 from_parts——信任边界交给调用者。

**kv_coordinator 为什么是死代码？** KV cache 驻留模型切换协调（`on_switch(from, to)`，L21-23）是真实需求（cache_affinity hint 已进协议），但触发链路（监听决策变化 → 失效/迁移 cache）未实现。字段与 trait 先行占位、`#[allow(dead_code)]` 显式认账——比删掉再考古好。

**砍掉了什么？** 没有并发控制（Router 天然 Send+Sync，route 无锁——seed 用 Atomic；想串行化得自己包）；没有指标埋点（algorithm_name 是唯一的遥测钩子）；training/trigger 是类型占位（run_once 丢弃工件，TriggerRegistry 只存规格）——自演进闭环的"最后一步"刻意留白，等真实 EvolvingProvider 落地再接线。

## 六、新人提示与坑

1. **别用 report 排查问题**：它静默丢弃非法反馈（L169-173）。调 `try_report` 拿 FeedbackError——最常见的是 extensions 预算超限与版本号不等于 1。
2. **route_id 不要自己拼**：宿主在 StateQuery 里填的 route_id 会被覆盖（decide_loop.rs:25，测试 `query_receives_the_route_id_the_decision_carries`，router.rs:311-361 钉死"host-filled 被顶掉"）；想关联事件请用 Feedback.event_id（协议自己的字段）。
3. **`targets` 是装配期冻结的**：运行中增删模型需要重建 Router。profile 热更新不存在——`from_config` 每次都新建实例。
4. **Python 的 async route 不真异步**：`__init__.py:146-147` 的 async def 直接调同步 `route_sync`，会阻塞事件循环。x-router 这类带本地 LLM 推理的算法（decide 内调分类器）在 async 宿主里必须丢进 executor——`x_router/algorithm.py:69-71` 的 docstring 明确警告"an async host must not call it from a coroutine"。
5. **seed 是 Router 实例级的**：两个 Router 实例的种子序列各自从 0 开始；跨实例重放同请求要连同 Router 实例（或手动保证 seed 相同）。
6. **改 exclusions 语义要三处同步**：请求侧（宿主重试）、状态侧（report 的 Overflow/Unavailable）、合并处（decide_loop.rs:52-54）。只改一处会出现"拉黑了却还能被选中"或反之的诡异行为。
