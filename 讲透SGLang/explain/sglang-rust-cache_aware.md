# 深度解析：`sgl-model-gateway/src/policies/cache_aware.rs`

> 源码: `sgl-model-gateway/src/policies/cache_aware.rs` @ commit ec075d8bc（全文件 1511 行，其中 L538-1511 为测试，源码部分约 537 行）
>
> 这是 SGLang Rust 数据面（sgl-router 血统，本 commit 已迁入 `sgl-model-gateway` crate）中**请求级 KV-aware 路由**的核心实现：`CacheAwarePolicy`。它通过为每个 `(worker 池, model)` 维护一棵"近似 radix tree"，用**请求文本的字符级前缀匹配**来近似推断哪个后端 worker 的 KV cache 里最可能已有这份 prefix，从而把请求路由到缓存亲和度最高的 worker。当系统负载失衡时，策略动态退化为最短队列（shortest queue）负载均衡；负载恢复平衡后又切回缓存亲和路由。它同时是所有 `LoadBalancingPolicy` 中唯一"既管亲和又管负载"的双模策略，并支持通过 `smg_mesh` 在多网关节点间同步树操作日志。

## 0. 一句话定位

`CacheAwarePolicy` 回答的问题是：**"这条请求发给谁，能最大化命中后端已经缓存的前缀？"** 它不查询后端真实 cache 状态（那是 `cache_aware_zmq`/KV-events 路线的做法，见 `experimental/sgl-router`），而是自己记账——把每条路由过的请求文本插入一棵多租户 radix tree，下次来相似前缀的请求时查树决定亲和。这是一场用"近似"换"零后端开销"的设计豪赌，赌注是：**请求历史是 KV cache 内容的良好代理**。

## 1. 背景知识：为什么需要 cache-aware 路由

SGLang 推理引擎内部用 radix cache（基数树）管理 KV cache：请求的 prompt 前缀如果与近期请求重叠，对应 KV block 可以直接复用（prefix caching），避免重新 prefill。单机时这件事引擎自己就能做好；但多 worker（多副本/多机）部署、前面再加一层 router 时，就出现了一个新问题：

- 同一条 prompt 发给 worker A 和 worker B，两边都会各自缓存一份；
- 如果后续多轮对话（prompt 逐轮变长且前缀重叠）被随机路由打散到不同 worker，每轮都要在新 worker 上重新 prefill 相同前缀——**TTFT（首 token 延迟）和算力都被浪费**。

解法就是路由层"粘性"：把前缀相同的请求族尽量固定到同一个 worker，让每棵引擎内的 radix cache 各自深耕一片前缀空间。Python 版 sgl-router 的 `TreeCacheWorkerLoadBalancer` 开创了"router 侧维护近似 tree"的方案；本文件是它的 Rust 后裔（同源算法，重写了并发结构与扩展点）。

注意一个精妙的差别：**router 侧的 tree 存的是原始文本字符，不是 token**（文件头注释 L22-23 明说 "stores raw text characters instead of token IDs to avoid tokenization overhead"）。router 不做 tokenization，用字符前缀匹配作为 token 前缀匹配的近似——两者在绝大多数 tokenizer 下前缀边界高度一致。

## 2. 整体架构：双策略状态机

文件头注释（L1-60）给出了完整的策略说明书，可浓缩为一张图：

```
                       select_worker(request)
                              │
                 ┌────────────┴────────────┐
                 │ 1. 健康过滤 (is_healthy │
                 │    + circuit_breaker)   │
                 │ 2. 计算 min/max load    │
                 └────────────┬────────────┘
                              │
        is_imbalanced = (max-min) > abs_threshold
                     && max > min * rel_threshold
                              │
               ┌──────── 不平衡 ┴ 平衡 ────────┐
               ▼                               ▼
    ┌─────────────────────┐      ┌──────────────────────────┐
    │ select_worker_min_  │      │ tree.prefix_match(text)  │
    │ load: 最短队列       │      │ match_rate = matched/total│
    │ (L309-372)          │      └──────────┬───────────────┘
    │ 仍更新 tree 记账!    │            ┌────┴─────┐
    └─────────────────────┘       rate >    │   rate ≤
                              cache_threshold│  cache_threshold
                                   ▼         ▼
                          路由到树中 tenant  最小负载的健康
                          (按 URL 反查 worker) worker
                                   │
                        tenant 已摘除/不健康?
                                   ▼
                     remove_tenant 清理陈旧租户
                     + 兜底: first healthy
```

三个值得先记住的细节：

1. **失衡判定是双门槛 AND**（L401-402）：绝对差和相对比必须同时超标。只用绝对差会在高负载时误报（差 50 但两边都上万）；只用相对比会在低负载时误报（0 和 2 差 3 倍）。双门槛是经典的防抖组合。
2. **失衡路径也更新 tree**（L334-365 注释 "Even in imbalanced mode, update the tree to maintain cache state"）：负载切换是暂时的，亲和记账是长期的。如果失衡期间丢记账，切回平衡模式后树就"失忆"了。
3. **兜底不是轮询（round_robin）**：`cache_aware` 内部的降级链是"最短队列 → first healthy → 随机（无树时）"。真正的 `round_robin` 是 `policies/round_robin.rs` 里另一个独立策略。用户视角的"轮询兜底"实际对应"cache miss 时选最小负载 worker"（L441-446）。

## 3. 核心结构与函数

### 3.1 tree key 体系：`pool_tag` / `make_tree_key` / `tree_key_for_worker`（L83-100）

```rust
fn pool_tag(worker_type: &WorkerType) -> &'static str {   // L83
    match worker_type {
        WorkerType::Regular => "regular",
        WorkerType::Prefill { .. } => "prefill",
        WorkerType::Decode => "decode",
    }
}
fn make_tree_key(pool: &str, model: &str) -> String {      // L91
    format!("{}::{}", pool, model)
}
fn tree_key_for_worker(worker: &dyn Worker) -> String {    // L95
    make_tree_key(pool_tag(worker.worker_type()),
                  normalize_model_key(worker.model_id()))
}
```

树不是全局一棵，而是按 `"{pool}::{model}"` 复合键分桶。L76-82 的文档注释解释了为什么必须带 pool 前缀：PD 分离（prefill-decode disaggregation）部署下，同一个 model 会有 prefill 池和 decode 池两批 worker；如果 key 只有 model，交替的 prefill→decode 调用序列会互相覆盖对方在树里的租户记录，`cache_aware` 退化成两池之间的 flip-flop（随机弹跳）。这是从真实 bug 中长出来的设计——L999-1004 的回归测试 `test_pd_pool_isolation_shared_policy_regression` 专门护住它。

`normalize_model_key`（mod.rs L150-156）把空 `model_id` 归一为 `UNKNOWN_MODEL_ID`，保证单模型与多模型部署行为一致；测试里随处可见 `format!("regular::{}", UNKNOWN_MODEL_ID)` 这个键（L745, L1120-1121）。

### 3.2 主结构体 `CacheAwarePolicy`（L110-116）

```rust
pub struct CacheAwarePolicy {
    config: CacheAwareConfig,
    trees: Arc<DashMap<String, Arc<Tree>>>,
    mesh_sync: OptionalMeshSyncManager,
    _eviction_task: Option<PeriodicTask>,
}
```

| 字段 | 职责 |
|---|---|
| `config` | 五个阈值参数（见 3.3） |
| `trees` | 复合键 → radix tree 的分片并发 map；值是 `Arc<Tree>`，取出后 clone Arc 即可脱锁使用 |
| `mesh_sync` | 可选的多网关同步管理器（`Option<Arc<MeshSyncManager>>` 别名）；`None` 时纯单机 |
| `_eviction_task` | 后台 LRU 驱逐线程的 JoinHandle 保活（字段名下划线 = 只为持有不读取） |

注意策略本体没有 `&mut` 方法——所有可变状态（树、计数）都在 `DashMap`/`Tree` 内部自管并发，因此 `CacheAwarePolicy` 可以以 `Arc<dyn LoadBalancingPolicy>` 无锁共享给所有请求 handler。

### 3.3 配置 `CacheAwareConfig`（mod.rs L98-116，默认值）

| 参数 | 默认 | 含义 |
|---|---|---|
| `cache_threshold` | 0.5 | 前缀匹配率超过它才走亲和路径 |
| `balance_abs_threshold` | 32 | 负载绝对差阈值 |
| `balance_rel_threshold` | 1.1 | 负载相对比阈值（max > min×1.1） |
| `eviction_interval_secs` | 30 | 后台驱逐周期；0 = 关闭驱逐线程 |
| `max_tree_size` | 10000 | 每租户字符数上限，超出后 LRU 逐叶 |

### 3.4 构造与后台驱逐：`new` / `with_config`（L119-157）

`with_config` 在 `eviction_interval_secs > 0` 时启动一个 `PeriodicTask`（utils.rs L13-21，自管线程 + 停止旗标）：每 30 秒遍历所有 tree，调用 `tree.evict_tenant_by_size(max_tree_size)`。`Tree::evict_tenant_by_size`（tree.rs L718-821）的实现是"收集所有租户叶节点进按时间戳排序的最小堆（`Reverse<EvictionEntry>>` + `BinaryHeap`），从最老开始逐租户摘除，直到该租户的字符计数 ≤ max_size；摘除后若父节点变为新叶则推回堆继续"。两个防御性细节：摘除前重新验证节点仍是该租户的叶（并发下可能已变，L757-766）；空节点从父的 children 里物理删除防止树膨胀（L783-789）。

### 3.5 worker 生命周期钩子（L168-214）

- `init_workers(&[Arc<dyn Worker>])`（L168）：按 tree key 分组，对每组 `tree.insert("", worker.url())`——**空前缀注册**。空文本插入意味着该租户被挂在 root 的 `tenant_last_access_time` 里（tree.rs L369-373），此后任何查到 root 的请求都能拿一个合法 tenant，这是"树永不为空"的种子操作。生产上由 `PolicyRegistry::init_pd_cache_aware_policies`（registry.rs L333）在 worker 注册完成时调用。
- `add_worker`（L191）／`remove_worker`（L201）：单 worker 增量更新，走复合键。
- `remove_worker_by_url`（L209）：只知道 URL 不知道 model 的兼容路径——**遍历所有 tree 逐个 `remove_tenant`**（因为不知道它属于哪个 model 桶，宁多勿漏）。

`Tree::remove_tenant`（tree.rs L823 起）不是简单删键：它从叶往根回溯，摘除该租户的所有挂载点并回收空节点，同时递减 `tenant_char_count` 记账。

### 3.6 mesh 同步三件套（L160-297）

- `set_mesh_sync`（L160）：构造后注入同步管理器；若启用立即调用 `restore_tree_state_from_mesh`。
- `restore_tree_state_from_mesh`（L218-249）：对本机已有的每个 tree key，从 mesh 拉 `TreeState`（一个 `TreeOperation` 的**操作日志**），按序重放 `Insert`/`Remove` 重建整棵树。选 op-log 而非树快照同步，使恢复天然幂等可重放。
- `apply_remote_tree_operation`（L273-297）：接收端入口——把远端节点同步来的单条操作应用到本地树。注意 L270-272 的诚实注释：**当前生产代码没有接收路径的调用方**（`PolicyRegistry::apply_remote_tree_operation` 无 in-process caller），此方法今天只有测试能到达。发送端是活的（见 4.3），接收端是"预埋的接口"——阅读时不要误以为多节点树同步已经闭环。

`normalize_mesh_model_id`（L254-260）把意外为空的 key 归一成 `UNKNOWN_MODEL_ID`，纯防御（复合键 `pool::model` 实际永不为空）。

### 3.7 主算法：`select_worker`（L376-505，trait 实现）

这是整个文件的心脏，逐段拆解：

**① 健康过滤（L382-386）**
```rust
let healthy_indices = get_healthy_worker_indices(workers);
```
`get_healthy_worker_indices`（mod.rs L136-143）= `is_healthy() && circuit_breaker().can_execute()`——**健康是双门的**：主动健康标记 + 熔断器（连续失败后短期拉黑）。空则返回 `None`，调用方（router）转为"无可用 worker"错误。

**② 选树（L388-391）**
```rust
let pivot = workers[healthy_indices[0]].as_ref();
let tree_key = tree_key_for_worker(pivot);
```
用第一个健康 worker 当 pivot 推导 tree key。注释明说前提："the router pre-filters so every healthy worker here belongs to the same pool and same model"——上游（`routers/http/router.rs` L143-149 的 `get_workers_filtered`）已按 model+pool+连接模式筛过，policies 层不再校验。这是层间契约：谁违反（比如混池传参），key 就可能选错树。

**③ 单遍 min/max 负载统计（L393-398）**
```rust
let (min_load, max_load) = workers.iter().fold((usize::MAX, 0usize), |(min, max), w| {
    let load = w.load();
    (min.min(load), max.max(load))
});
```
一次 fold 同时求 min/max，零中间分配。`Worker::load()`（core/worker.rs L172）是 worker 对象上的运行中/排队请求计数（由请求 pipeline 的 `increment_load`/完成时递减维护），不是引擎侧 `#running-req`——后者的拉取在 `worker_manager.rs` 的 `LoadMonitor`（另一套，喂 PowerOfTwo 策略）。

**④ 失衡判定与短路（L400-413）**
```rust
let is_imbalanced = max_load.saturating_sub(min_load) > self.config.balance_abs_threshold
    && (max_load as f32) > (min_load as f32 * self.config.balance_rel_threshold);
```
`saturating_sub` 防 usize 下溢。失衡则整个亲和逻辑被旁路，走 3.8 的最短队列。

**⑤ 亲和查询（L415-430）**
```rust
let text = request_text.unwrap_or("");
let tree = self.trees.get(&tree_key).map(|entry| entry.value().clone());
```
两处微观优化：空文本归一为 `""`（匹配 0 字符，自然落入 miss 分支）；`DashMap::get` 的 shard 读锁内只做 `Arc::clone` 就放锁（L418-419 注释 "without holding the entire HashMap lock"——其实是"不持 shard 锁做长活"）。

```rust
let result = tree.prefix_match_with_counts(text);
let match_rate = if result.input_char_count == 0 { 0.0 }
    else { result.matched_char_count as f32 / result.input_char_count as f32 };
```

`prefix_match_with_counts`（tree.rs L531-619）沿树逐字符下降：每步取首字符查子节点（子节点 map 是按首字符分片的 `DashMap<char, NodeRef>`，配黄金比例乘法的 `CharHasher`，tree.rs L58-84），`shared_prefix_count` 算节点内共享前缀（ASCII 走字节快速路径，非 ASCII 退回逐字符，tree.rs L289-307）；整节点匹配完继续下降，部分匹配即停。**返回的 tenant 是"匹配终点节点上最后驻留的租户"**（先查节点级 `last_tenant` O(1) 缓存，miss 再迭代 `tenant_last_access_time` 取第一个，tree.rs L568-599）。`match_rate = 匹配字符数 / 输入总字符数`——这就是"affinity 计算"的全部：一条 0-1 之间的前缀重叠率。

一个容易被忽略的语义：匹配终点节点可能同时挂着多个租户（多 worker 的前缀在这点分叉），此时取哪个租户由 DashMap 迭代顺序决定——**近似算法故意不在这里做 tie-breaking**，而是靠 miss 阈值和负载兜底吸收不确定性。

**⑥ 三路决策（L433-446）**
```rust
let selected_idx = if match_rate > self.config.cache_threshold {
    // Cache hit: 树说 worker X 有这前缀 → 按 URL 反查
    workers.iter().position(|w| w.url() == tenant_url)
        .filter(|&idx| workers[idx].is_healthy())
} else {
    // Cache miss: 选负载最小的健康 worker
    healthy_indices.iter().min_by_key(|&&idx| workers[idx].load()).copied()
};
```
hit 路径用 `position` 按租户 URL 反查 worker 下标（`&str` 直接比较零分配，L434 注释），并二次健康过滤——**树里的租户可能已经下线**，这里查不到或已病就落到后面的清理逻辑。miss 路径等价于"最空闲者得"：新前缀应该去缓存最空（也是负载最轻）的地方开垦。

**⑦ 记账与同步（L448-468）**
选中后无论走哪条路，都执行 `tree.insert(text, workers[idx].url())`——把这条请求的完整文本挂到选中 worker 名下。**查询和写入用的是同一棵树**：本次的 miss 在写完后就成了未来的 hit（多轮对话下一轮带着更长前缀回来，match_rate 超阈值，粘住同一 worker）。随后 `increment_processed()` 累计 worker 处理数（用于观测/负载），并把 `TreeOperation::Insert` 发给 mesh（若启用，L453-462）。

**⑧ 陈旧租户清理（L471-488）**
仅当"hit 路径选中失败"（租户 URL 已不在 worker 列表或全不健康）时触发：`tree.remove_tenant(tenant_url)` 把这个已死 worker 从树上摘干净，并同步 `TreeOperation::Remove` 到 mesh。这样下一轮同前缀请求不会再被死租户绊倒。

**⑨ 兜底（L490-503）**
清理后（或未触发清理的选中失败）返回第一个健康 worker。若连树都没有（key 不存在——注释指出是"pool tree 未播种或注册竞态"），打 warn 并**随机**选一个健康 worker。此时（L496-498 的 warn 文案明说）"cache affinity is effectively disabled until this clears"——亲和降级为随机，直到树被播种。

### 3.8 失衡分支：`select_worker_min_load`（L309-372）

```rust
let min_load_idx = healthy_indices.iter()
    .min_by_key(|&&idx| workers[idx].load()).copied()?;
```
最短队列选人后，**依然把请求文本插入选中 worker 的树**（L335-365），同样发 mesh Insert、`increment_processed()`。L319-326 是个小的观测优化：只有 DEBUG 级别启用时才收集各 worker 负载的 `Vec` 用于日志。tree 缺失时只 warn 不阻断（L357-363）——失衡模式下树本来就是配角。

### 3.9 trait 其余方法（L507-529）

- `on_request_complete`（L507-517）：请求完成回调，当前只打 debug 日志——**失败请求不降亲和、不记仇**，注释坦言这是留给"按成功率调权"的扩展点。
- `name()` → `"cache_aware"`（L519）：这个字符串是运行时类型标签，`PolicyRegistry::remove_pd_worker_from_cache_aware` 用它做 downcast 前置校验（非 cache_aware 策略静默跳过，测试 L1386-1399 护住）。
- `needs_request_text()` → `true`（L523）：**全策略族里唯一的 true**。router 据此决定是否从请求体提取文本传进来——是 `SelectWorkerInfo.request_text`（mod.rs L161-162）的主要消费方。
- `as_any()`（L527）：支持 `dyn Any` downcast，供 registry 做策略特定操作（如 init_pd 播种）。

## 4. 与后端 worker 的数据同步

这是本文件除算法外的第二大主题。同步是**三个层面**的：

### 4.1 拓扑同步：worker 增删 → 树租户增删

worker 注册/注销事件经 `WorkerRegistry` → `PolicyRegistry` 落到本策略：

| 事件 | 入口 | 树操作 |
|---|---|---|
| 批量注册（启动/PD 播种） | `init_workers` L168 | 每池 `insert("", url)` 空前缀注册 |
| 单个上线 | `add_worker` L191 | 同上 |
| 按对象下线 | `remove_worker` L201 | 精确 key 树 `remove_tenant` |
| 按 URL 下线（兼容） | `remove_worker_by_url` L209 | 全部树扫一遍 `remove_tenant` |

PD 场景由 `PolicyRegistry::init_pd_cache_aware_policies`（registry.rs L333）与 `remove_pd_worker_from_cache_aware`（registry.rs L377）编排：前者按 `Prefill => prefill_policy, Decode => decode_policy` 分发播种（生产上是**两个独立的 `CacheAwarePolicy` 实例**分别管两池，测试 L941-997 复现该接线）；后者按 `worker_type()` 分发摘除，`Regular` 短路返回，非 cache_aware 策略静默跳过。双向 dispatch-swap 都有测试钉死（L1252, L1296）。

### 4.2 请求记账同步：每次选择 → 树更新 + mesh 操作日志

3.7 的 ⑦⑧ 已覆盖：本机树 insert/remove 的同时，镜像一条 `TreeOperation::{Insert, Remove}` 到 mesh（key = `pool::model` 复合键）。mesh 层（`smg_mesh` crate）负责跨网关节点传播；对端收到后应走 `apply_remote_tree_operation` 回放——如前所述，这段接收管线尚未接线，多节点一致性今天靠"重启时 restore + 单向发送"维持（测试 `test_cache_aware_multi_node_consistency` L845 的注释也承认这点，"would be synced via gossip protocol"）。

### 4.3 状态恢复：启动时从 mesh 重放

`restore_tree_state_from_mesh`（L218-249）在 `set_mesh_sync` 注入时自动执行：对本机每个 tree key 拉 op-log 重放。配合 `init_workers` 的空注册，一个重启的网关能在秒级找回集群的前缀亲和记忆，而不是从零开始抖动一轮。

### 4.4 与引擎真实 cache 的关系：刻意的一无所知

本策略**从不**向后端 worker 发起任何 cache 查询。树的字符计数、LRU 时间戳（概率性更新，1/8 采样，tree.rs L601-607）都是 router 侧对"引擎 radix cache 该有什么"的推测。后果：引擎侧主动 `flush_cache`、容量驱逐、PD 的 KV 迁移都不会反映到树里——亲和决策可能指向已失效的缓存（多算一次 prefill，不影响正确性）。这是明确的工程取舍：正确性归引擎，命中率归概率，延迟归零开销。想要强一致的路线存在（`experimental/sgl-router/src/policies/cache_aware_zmq.rs`，订阅引擎 KV events 事件流维护 token 级 tree），但那是另一个故事。

## 5. 与其他模块的交互

```
routers/http/router.rs            routers/grpc/.../worker_selection.rs
  select_worker_for_model L134 ──► PolicyRegistry::get_policy(_or_default)
  extract_text_for_routing L203      │
        │ SelectWorkerInfo           ▼
        └──────────────────► CacheAwarePolicy::select_worker L376
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
  policies/mod.rs               policies/tree.rs             core::Worker trait
  LoadBalancingPolicy L42       Tree::insert L362             url/load/is_healthy
  CacheAwareConfig L98          prefix_match_with_counts L531 worker_type/model_id
  get_healthy_worker_indices    evict_tenant_by_size L718     circuit_breaker
  normalize_model_key L150      remove_tenant L823            increment_processed
        │                            │
        ▼                            ▼
  policies/registry.rs          policies/utils.rs
  init_pd_cache_aware L333      PeriodicTask L13（后台驱逐线程）
  remove_pd_worker L377
        │
        ▼
  smg_mesh（MeshSyncManager: op-log 同步/恢复）
```

- **上游调用方**：HTTP 路由 `routers/http/router.rs::select_worker_for_model`（L134-192）先用 `WorkerRegistry::get_workers_filtered` 按 model+Regular+HTTP 滤人，再把 `typed_req.extract_text_for_routing()`（L203）提取的文本塞进 `SelectWorkerInfo` 传进来；gRPC 侧对应 `routers/grpc/common/stages/worker_selection.rs`（L171, L250-251 分别选 prefill/decode worker）。
- **`policies/mod.rs`**：trait `LoadBalancingPolicy`（L42-94）定义五个能力点（select/complete/name/needs_text/update_loads），`cache_aware` 是最重的实现。
- **`policies/tree.rs`**：2310 行的多租户并发 radix tree，锁粒度到节点（children 用分片 DashMap），自带 LRU 与租户记账。本文件只消费它五个方法。
- **`core::Worker`**（core/worker.rs L113 起）：策略只依赖 trait 方法，不关心 HTTP 还是 gRPC worker——虽然 gRPC 路径的 worker 池同样适用本策略。
- **`policies/registry.rs`**：策略的装配与 PD 编排层；`get_all_power_of_two_policies`（L258）是它对外的另一个钩子（与本文件无关，但与 `worker_manager.rs` 的 LoadMonitor 相关，见姊妹篇）。
- **`smg_mesh`**：跨节点同步 crate；`OptionalMeshSyncManager` 是 `Option<Arc<MeshSyncManager>>`，让 mesh 成为零成本可选依赖。

## 6. 关键设计决策

1. **近似而非查询（approximate tree over real cache introspection）**：用请求历史的字符级 radix tree 代理引擎 KV cache。换来的是路由决策零后端 RTT、零协议耦合（HTTP/gRPC 通吃）、tokenizer 无关；付出的是弱一致（引擎侧驱逐不可见）与字符/token 的近似误差。L4 注释开宗明义 "eliminating the need for direct cache state queries"。
2. **双模策略 + 双门槛防抖（abs AND rel）**：缓存亲和与最短队列不是二选一的部署选项，而是同一策略里按实时负载自动切换的两档；`(max-min)>32 && max>min×1.1` 的 AND 语义同时抑制高负载误报与低负载误报。且切换不丢状态——失衡路径继续记账，保证模式回切时亲和立即有效。
3. **`(pool, model)` 复合 tree key 根除 PD 串扰**：历史上单 model key 让 prefill/decode 交替调用互相覆盖租户，策略退化成随机弹跳（L76-82 注释 + L1005 回归测试记录了这次教训）。复合键 + 生产上双策略实例，把池间隔离做成了结构性质而非约定。
4. **op-log 式 mesh 同步，发送先行、接收预留**：同步的是 `Insert/Remove` 增量操作而非树快照，天然可重放（`restore_tree_state_from_mesh`）；但接收路径 `apply_remote_tree_operation` 目前无生产调用方（L270-272 明示）。多节点一致性是"尽力而为"档——诚实留白好过假装闭环。
5. **并发设计上的"锁内最小工作"原则**：`DashMap` shard 锁内只 `Arc::clone` 就放锁再操作树（L336-343, L418-424）；树侧节点级锁 + 概率性时间戳更新（1/8）压 DashMap 争用；hit 路径按 URL `position` 反查用 `&str` 直比避免 String 分配。热路径上每一处分配都被显式优化过，注释可考。

## 7. 测试导览（L538-1511，占全文件 2/3）

测试本身是行为规格的最好文档，按主题分组：

| 主题 | 测试 | 行号 | 钉住的行为 |
|---|---|---|---|
| 亲和粘性 | `test_cache_aware_with_balanced_load` | L544 | 相同/相似前缀连续请求必粘同一 worker |
| 负载切换 | `test_cache_aware_with_imbalanced_load` | L609 | 人为拉开负载后无视亲和选轻者 |
| 摘除清理 | `test_cache_aware_worker_removal` | L646 | remove_worker_by_url + set_healthy(false) 后请求全部转向存活者 |
| mesh 发送 | `test_cache_aware_sync_tree_operation_to_mesh` | L706 | select 后 mesh 里出现 `regular::UNKNOWN_MODEL_ID` 的 op |
| mesh 恢复 | `test_cache_aware_restore_tree_state_from_mesh` | L753 | 预置 op 后树状态可查 |
| 远端应用 | `test_cache_aware_apply_remote_tree_operation` | L812 | apply 接口建树 |
| 无 mesh 降级 | `test_cache_aware_without_mesh` | L889 | mesh=None 一切照常 |
| PD 隔离 | `test_pd_pool_isolation_two_policies` | L941 | 生产接线：双策略实例，4 轮增长 prompt 各池粘住各 worker |
| PD 回归 | `..._shared_policy_regression` | L1005 | 单实例混接两池也不串扰（复合键兜底） |
| PD 摘除 | `test_pd_pool_isolation_remove_worker` | L1083 | 摘 prefill 不碰 decode 树（字节级不变） |
| 注册表分发 | `test_registry_remove_pd_worker_...` ×3 | L1252, L1296, L1341 | prefill/decode 双向 dispatch + Regular/非 cache_aware 短路 |
| 播种门控 | `test_registry_init_pd_cache_aware_policies_gating` | L1407 | 四象限：谁 cache_aware + 谁非空才播种谁 |

## 8. 阅读建议

1. **先读文件头 L1-60**：这是全文件最浓缩的算法说明书，正文只是它的展开。
2. **带着两个问题读 `select_worker`（L376-505）**：①这条请求的 match_rate 怎么算的？②三种 fallback（min-load / first-healthy / random）分别在什么条件下触发？能答对这两个，算法就懂了。
3. **`tree.rs` 只读四个签名**：`insert` L362、`prefix_match_with_counts` L531、`evict_tenant_by_size` L718、`remove_tenant` L823——把它当黑盒 KV（`文本 → 租户` 的可 LRU 字典）足以理解本文件；想抠并发细节再回头读 `NodeText`/`CharHasher`（L56-160）。
4. **对照测试读设计决策**：L1005 的回归测试注释就是"为什么有复合键"的第一手史料；L742-749 断言 mesh key 格式，是理解同步寻址的最短路径。
5. **横向对比姊妹实现**：`policies/prefix_hash.rs`（token 前缀 + 一致性哈希的强一致路线）和 `experimental/sgl-router/src/policies/cache_aware_zmq.rs`（订阅引擎 KV events 的实时路线）解决了同一个问题的不同侧面，三者对照能看清"近似 vs 精确"的谱系。
6. **注意版本漂移**：本文件属于 `sgl-model-gateway` crate（原 rust workspace 拆分后的产物）；`rust/` 目录在本 commit 只剩 `sglang-grpc`，而 `experimental/sgl-router` 是正在演进的新一代路由。阅读上游文档时注意区分三者血缘。
