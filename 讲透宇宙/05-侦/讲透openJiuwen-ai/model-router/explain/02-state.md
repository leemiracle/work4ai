# 02 · crates/state/src/state_provider.rs 与 test_state/：状态外置设计（"state 仅是提示"哲学）

## 一、角色定位：跨请求记忆的插件槽

`crates/state/src/` 是 L2 状态层，核心只有一个 63 行的 trait 文件 `state_provider.rs` 加两个测试实现。它在棋局中的位置：**runtime 与算法之间的旁路缓存**。算法做决策时需要一点跨请求记忆（"这个会话上次选谁成功了""哪个模型刚刚连续 overflow"），但架构不允许算法自己存——于是 state 层作为独立插件槽存在，与算法槽（`AlgorithmProvider`）严格对位。

`state_provider.rs:1-5` 的模块文档浓缩了全部设计哲学，三句话拆开看：

1. "与算法侧 `AlgorithmProvider` 对位：**运行期单槽选一**"——装配时 profile 的 `[state] backend` 决定用哪个实现，路由过程中不换。
2. "**状态是 hint：有界、可丢失**"——这是全仓最重要的三个字。state 提供的一切信息都是"提示"，不是事实。
3. "算法**从不直接调用**本 trait"——算法拿到的只是 `StateView` 数据（经 runtime 中转），state 对算法完全不可见。

`lib.rs:1-3` 补充了组织方式："runtime 只面向 `StateProvider`；内存或远程由 profile 决定。"目录结构印证：`state_provider.rs`（契约）与 `test_state/`（实现）分离，`service/` 是 feature 门控的 gRPC 服务骨架（`lib.rs:8-9`，`[cfg(feature = "service")]`）。

## 二、内部结构：一个 trait、四个方法、两种降级

### StateProvider trait（state_provider.rs:21-63）

```rust
pub trait StateProvider: Send + Sync {
    fn snapshot(&self, key: &RoutingKey) -> StateView;
    fn query(&self, key: &RoutingKey, query: &StateQuery)
        -> Result<StateSnapshot, StateQueryError> { /* 默认实现 */ }
    fn report(&self, feedback: Feedback);
    fn publish(&self, slot: &str, artifact: &[u8], ver: u64)
        -> Result<(), CasConflict> { /* 默认 no-op */ }
}
```

- **`snapshot(&self, key)`（L23）**：基础读取路径，入参只有路由键，返回裸 `StateView`。无 Result——**读 state 永不失败**，读不到就返回空视图。
- **`query(&self, key, query)`（L42-49）**：带检索意图的读取，返回 `StateSnapshot`（view + retrieved 命中列表）。关键在它是**带默认实现的 trait 方法**（Rust 的对象安全默认方法）：默认实现忽略查询参数、退化为包一层 snapshot（`state_provider.rs:32-34` 注释："既有实现不覆盖也能工作"）。这让检索能力成为**可选升级**而非破坏性变更——MemoryState 至今没有覆盖它（见下文勘误）。文档注释（L26-28）还规定了 `top_k` 的弱语义："只表示条数上限（实际可更少，空列表合法）"。
- **`report(&self, feedback)`（L52）**：吸收反馈，"异步、尽力而为；本骨架同步写入"。无返回值——反馈丢失是可接受的。
- **`publish(&self, slot, artifact, ver)`（L59-62）**：带版本原子写回（训练工件从 `EvolvingProvider` 流向 state），默认 no-op。`CasConflict`（`state_provider.rs:11-16`）记录乐观并发冲突的三元组：槽名 + 期望版本 + 实际版本。

三条铁律写在注释里：远程实现**超时必须返回空 StateView 而非 Err**（L20）；检索失败"返回仅含视图的结果，或返回 Err 让 runtime 回退"（L36-37）；绝不阻塞请求。

### test_state/mod.rs：两个内置实现

`mod.rs:1-4` 开宗明义："不是必须编进产物的『唯一实现』。profile `state.backend` 选一（memory / remote）；云侧自定义实现走 Python `StateProvider`。"

### MemoryState（memory.rs）——端侧默认实现

`memory.rs:17-22`：`Mutex<HashMap<RoutingKey, Entry>>`，Entry 是 `(StateView, expires_at)`。构造参数 `ttl` + `max_entries`，`with_defaults()` 给 `300s / 1024`（`memory.rs:33-35`），与 `config/edge.toml:6-7` 的默认值互相印证。

`snapshot`（`memory.rs:93-104`）：读时惰性过期——命中但过期就地 remove 并返回空视图。锁中毒用 `unwrap_or_else(|e| e.into_inner())`（L95）恢复而非 panic，这是"绝不阻塞请求"的细节落实。

`report`（`memory.rs:107-143`）是状态演化的全部逻辑，规则清晰：

- `call: None`（延迟反馈）直接 return（L108-110）——结果未知的反馈不产生状态；
- 容量满时淘汰（L114-118）；
- `sample_count` 饱和累加（L127）；
- **Overflow / Unavailable → 把 selected_model_id 追加进 exclusions**（L131-135）；
- **Ok → 更新 affinity 为该模型**（L137-139）；
- **Rejected → 什么都不做**（L140-142）。

**勘误（必须钉版）：注释宣称的 "TTL + LRU" 不是 LRU。** `memory.rs:1` 写"进程内内存实现（TTL + LRU 上界）"，但淘汰代码（`memory.rs:115-117`）是 `map.keys().next()`——HashMap 迭代顺序任意，这是**无序任意淘汰**，与"最近最少使用"毫无关系。文件自己的第二行（L1 后半句"骨架阶段用容量上限代替完整 LRU"）和 `remote.rs:1` 的口吻一样承认了这是骨架。对使用者的影响：容量打满时被淘汰的可能是**最活跃**的会话，别拿 MemoryState 当有质量保证的缓存。

另一个事实：**MemoryState 没有 `query` 的覆盖**。`memory.rs` 全文无 `fn query`，走 trait 默认实现降级为 snapshot——`memory.rs:68-79` 的测试 `default_query_degrades_to_snapshot` 明确验证了这一点（"视图一致、检索结果为空"）。想在内存态做向量检索的人需要自己覆盖。

### RemoteState（remote.rs）——云侧占位

`remote.rs:9-13`：`endpoint + timeout` 两个字段。`snapshot` 直接 `StateView::empty()` + TODO 注释（L28）："gRPC snapshot；超时返回空视图而非 Err"；`report` 空实现（L33-35）。**这是诚实的 stub**：接口语义（降级不报错）已定型，网络层未实现。装配时 `Router::state_from_profile`（`runtime/src/router.rs:83-92`）会要求 endpoint 存在，但即便配了，行为也是"永远返回空视图"。

## 三、外部连接

- **上游**：依赖 protocol 的六个类型（`state_provider.rs:6-8`）。workspace 中被 runtime（`runtime/src/router.rs:13` 引入 `test_state as backends`）和 py（`py/src/lib.rs:19` 引入 `StateProvider`）消费。
- **装配入口**：`Router::state_from_profile`（`router.rs:74-97`）按 `profile.state.backend` 字符串分派：`"memory"` → MemoryState（ttl/cap 带默认 300/1024）、`"remote"` → RemoteState（endpoint 必填否则 `RouterError::Config`，timeout 默认 **5ms**，`router.rs:88`）、其他 → 报错。
- **Python 侧旁路**：`py/src/lib.rs:104-110` 的 assemble 里，state 解析是三段式——显式注入的 Python 对象 > `state_adapter::lookup`（Python 注册的后端，如 x-router-bandit）> Rust 的 `state_from_profile`。云侧自定义 state 不需要动 Rust 代码。
- **调用方只有一个**：runtime 的 `decide_loop.rs:13-31`（read_state）和 `router.rs:159-163`（try_report）。算法层零依赖 state crate——`algorithm_provider.rs` 的 import 列表里没有它。

## 四、数据流：一条反馈如何变成下一次路由的提示

1. 宿主调用模型后构造 `Feedback`（key = session+agent，selected_model_id，outcome）；
2. `Router::try_report`（`router.rs:159-163`）先 `feedback.validate()`——**校验不过的反馈不进 state**（这是跨语言唯一校验入口）；
3. `MemoryState::report` 按 Outcome 更新对应 key 的 Entry：成功 → affinity="该模型"；溢出/不可用 → exclusions += 该模型；TTL 刷新；
4. 下一次同 key 请求进来，`decide_loop::read_state` → `snapshot(key)` 返回这份 StateView；
5. `decide_loop.rs:52-56` 把 `view.exclusions` **并入**请求 exclusions 再过滤 TargetSet——被 state 拉黑的模型从候选中消失；
6. 算法在 ctx.view 里看到 affinity（提示，可忽略）与净化后的 targets（硬过滤已完成）。

带检索意图的变体：`RouteHint.state_query = Some(...)` 且非空且校验通过（`decide_loop.rs:22-24`）时走 `query`，返回的 `retrieved` 进入 `RouteContext.retrieved`（x-router 的 bandit 半场消费它）；query 失败或快照校验不过，一律退回 snapshot（L26-30）——**检索能力永不影响路由可用性**。

## 五、设计决策与权衡

**"state 仅是提示"为什么重要？** 它决定了系统的故障模型。state 挂了/空了/错了，最坏结果是"路由变笨"（退化为冷路由、无亲和、无排除），**永远不会是"路由失败"**。对比把状态做成强依赖的设计（典型如带粘性会话的网关），这里牺牲了状态精度换取了路径可用性。三条配套规则保证这一点：读无 Err（L20）、写无确认（L52）、检索可降级（L36-37）。

**为什么 report 是 fire-and-forget 而 try_report 才校验？** 校验放在 runtime 门面（`router.rs:151-154` 注释："这是跨语言一致的唯一校验入口：Python 门面同样走这里"）而非 state 实现里，避免每个 state 实现都要自己抄一遍 65KB/256 元素/8 层的预算逻辑。`report` 保留为兼容入口，非法反馈静默丢弃（`router.rs:169-173`）。

**publish 的 CAS 语义为谁设计？** 为自演进闭环：`EvolvingProvider::fit` 产出 `Artifact`，`TrainingJob` 按 `PublishPlan{slot, expected_version}` 写回（`runtime/src/training.rs:43-61`）。`MemoryState::publish` 返回 Ok 的 no-op（`memory.rs:145-147`）——骨架阶段工件丢弃，但冲突协议已定型。

**砍掉了什么？** 持久化（进程重启状态全丢，Endpoint 在 remote 但未实现）、真正的 LRU、按模型粒度的统计（StateView 只有 sample_count 一个数，`state_view.rs:4-7` 注释"字段后续随算法需求扩展"）。这些都是刻意的骨架边界：先钉契约语义，再填实现质量。

## 六、新人提示与坑

1. **别信 memory.rs 头注释的 "LRU"**：实际是 HashMap 任意淘汰（`memory.rs:115-117`），满容量时活跃会话可能被逐。要确定性请自己实现或用 remote。
2. **MemoryState 不支持检索**：没有覆盖 `query`，`StateQuery` 会被默认实现吞掉。x-router bandit 需要 `retrieved`，所以它的 `BanditStore` 是独立的 Python StateProvider（`bandit_store.py:59` 的 `STORE_BACKEND = "x-router-bandit"`），不经过 MemoryState。
3. **remote backend 的 timeout 默认 5ms**（`router.rs:88`）而非 5s——毫秒不是秒，抄配置时容易看错。
4. **`report` 静默丢非法反馈**：排查"为什么 sample_count 不涨"时先换 `try_report` 看错误（版本号不等于 1、扩展超预算都是常见原因，见 01 篇）。
5. **Rejected 不产生任何状态**（`memory.rs:140-142`）：被拒的调用既不排除也不亲和。如果你的宿主把"被拒"当失败想触发回退，要在宿主侧重试逻辑里自己做 exclusions。
6. **snapshot 是惰性过期**（`memory.rs:96-103`）：过期条目在**被读到时**才删除，不活跃 key 的内存要等容量淘汰才释放。长期运行进程的内存曲线靠 max_entries 封顶，不靠 TTL。
7. **想在 Python 侧自定义 state**：实现 `snapshot` / `report`（`report` 可选），经 `register_state` 注册或直接把实例传给 `Router.from_config(config, state=...)`（`python/openjiuwen/__init__.py:133-137`）。契约细节见 `python/openjiuwen/state_provider.py`。
