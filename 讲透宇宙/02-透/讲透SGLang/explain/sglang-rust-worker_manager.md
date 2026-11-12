# 深度解析：`sgl-model-gateway/src/core/worker_manager.rs`

> 源码: `sgl-model-gateway/src/core/worker_manager.rs` @ commit ec075d8bc（全文件 394 行，无测试模块——测试在 `tests/` 与依赖模块内）
>
> 这是 SGLang Rust 数据面 `sgl-model-gateway` 中 worker 生命周期运维与负载信息汇集的控制面模块，包含两个角色：**`WorkerManager`**——一个无状态工具集，向后端所有 worker 扇出（fan-out）管理类 HTTP 请求（`flush_cache`、拉取 `/v1/loads`、聚合 `/metrics`），是"运维操作"与"指标聚合"的唯一入口；**`LoadMonitor`**——常驻后台的负载监控服务，周期性拉取全体 worker 负载，把最新快照推送给所有 `PowerOfTwo` 负载均衡策略并通过 `watch` channel 广播给任意订阅者。它承接 sgl-router 传统中 router 对 worker 池的"生命周期管理"职责，但注意：本网关**不 spawn worker 进程**，worker 是外部启动、注册进来的 SGLang 引擎进程，本模块管的是它们的运行时状态面。

## 0. 一句话定位

如果说 `policies/cache_aware.rs` 是数据面（每个请求都要走一遍的选路大脑），那么 `worker_manager.rs` 就是**控制面**：请求转发本身不经过这里，但运维刷缓存、看负载、聚合指标、给负载均衡策略喂数据，全都从这走。394 行代码干干净净地分两半：前 267 行是无状态的扇出工具，后 127 行是一个可启停的监控循环。

## 1. 先澄清一个容易误解的问题：worker "进程模型"到底是什么

模块文档注释（L1-3）自述为 "worker lifecycle operations and fan-out request utilities"。但通读全文你会发现：**这里没有任何进程 spawn、健康检查循环或重启逻辑**。这不是缺失，而是 sgl-model-gateway 的架构立场：

- **worker = 外部进程**。每个 worker 是一个独立启动的 SGLang 引擎进程（HTTP 或 gRPC server），由部署环境（脚本、systemd、K8s……）管理。网关通过服务发现/注册 API（`service_discovery.rs`、`WorkerRegistry`）拿到它们的 URL 与凭据。
- **健康检查在别处**。由 `WorkerRegistry::start_health_checker`（core/worker_registry.rs L646）启动的 `HealthChecker` 周期执行，底层是 `Worker::check_health_async`（core/worker.rs L145；L712-713 按 `ConnectionMode` 分派到 `http_health_check` L389 或 `grpc_health_check` L388）。server.rs L917-927 在启动时根据 `config.router_config.health_check` 决定是否拉起。
- **"重启策略" = 不重启**。worker 挂了由外部编排器负责拉起；网关侧的反应链是：健康检查失败 → `set_healthy(false)` / 熔断器打开（`CircuitBreaker`，core/circuit_breaker.rs）→ 路由层 `get_healthy_worker_indices`（policies/mod.rs L136-143，`is_healthy() && circuit_breaker().can_execute()`）把它从候选集摘掉 → worker 重新注册后回来。
- **本模块的"生命周期操作"** 指的是运行时状态操作：flush cache（清引擎 KV cache）、拉负载、聚合指标——即"对活着的 worker 做管理动作"，而非进程生死。

所以本文件在"进程模型"里的真实角色是：**worker 注册进 `WorkerRegistry` 之后，一切"从网关侧主动打向 worker"的非推理请求，都从这里出去**。

## 2. 整体架构图

```
                         ┌────────────────────────────────┐
   admin/ops 请求         │        WorkerManager (L84)     │
   (server.rs 路由)  ───► │  get_worker_urls      L87      │
   L155 /metrics          │  flush_cache_all     L95       │──── fan_out L36 ──┐
   L402 /flush_cache      │  get_all_worker_loads L160     │                  │
   L408 /loads            │  get_engine_metrics  L232      │                  ▼
   L1021 (worker 列表)     └────────────────────────────────┘   POST /flush_cache
                                  ▲                             GET  /v1/loads?include=core
                                  │ 取 worker 列表                GET  /metrics
                          WorkerRegistry.get_all()         （每个后端 SGLang 引擎进程）
                                  ▲
                                  │ update_loads(&loads)
                                  │（仅 PowerOfTwo 策略）
   ┌──────────────────────┐      │
   │ LoadMonitor (L270)   │      └──────────► policies/power_of_two.rs
   │ monitor_loop L338    │                   （随机取二、择优而路由）
   │  interval tick       │
   │  → get_all_worker_   │──── watch::channel ───► subscribe() L334
   │    worker_loads      │     (HashMap<url, isize>)   （任意外部订阅者）
   └──────────────────────┘
        ▲ start/stop
   server.rs L929-932（启动时拉起）
   app_context.rs L455（构造）
```

两条腿：左腿 `WorkerManager` 是按需触发的请求-响应式工具；右腿 `LoadMonitor` 是自驱动的周期任务，把左腿的 `get_all_worker_loads` 当探针复用。

## 3. 核心结构与函数

### 3.1 常量：`REQUEST_TIMEOUT` / `MAX_CONCURRENT`（L26-27）

```rust
const REQUEST_TIMEOUT: Duration = Duration::from_secs(5);
const MAX_CONCURRENT: usize = 32;
```

所有扇出请求共享 5 秒超时；fan-out 并发上限 32。这两个数定义了本模块的"脾气"：管理请求宁可超时放弃也不悬挂，且对每个 worker 的管理面请求总并发有界，不会在 worker 数量大时打爆对端连接。

### 3.2 `WorkerResponse` 与 `fan_out`（L30-68）

```rust
struct WorkerResponse {                       // L30
    url: String,
    result: Result<reqwest::Response, reqwest::Error>,
}

async fn fan_out(                             // L36
    workers: &[Arc<dyn Worker>],
    client: &reqwest::Client,
    endpoint: &str,
    method: reqwest::Method,
) -> Vec<WorkerResponse>
```

对每个 worker 拼 `format!("{}/{}", url, endpoint)`（L47），从 `worker.api_key()` 取可选 bearer token（L48, L53-55——支持带鉴权的多租 worker 池），挂上 `REQUEST_TIMEOUT`（L52），然后：

```rust
stream::iter(futures)
    .buffer_unordered(MAX_CONCURRENT)   // L64-66
    .collect()
    .await
```

`buffer_unordered(32)` 是关键：**结果顺序不保证、并发有界**。管理面请求不关心谁先回来，只关心最终成败清单；32 的并发帽意味着 100 个 worker 时会分批打出去，保护网关自身与网络的瞬时压力。注意 `reqwest::Client` 是外部传入复用的（连接池在调用方生命周期里），本模块不持有任何客户端状态。

返回的 `Vec<WorkerResponse>` 保持了"URL ↔ 结果"的对应关系——因为 futures 里闭包捕获了 `url` 的 clone（L46），即便响应乱序到达也能正确归因。

### 3.3 `EngineMetricsResult`（L70-82）

```rust
pub enum EngineMetricsResult { Ok(String), Err(String) }

impl IntoResponse for EngineMetricsResult {   // L75-82
    fn into_response(self) -> Response {
        match self {
            Self::Ok(text) => (StatusCode::OK, text).into_response(),
            Self::Err(msg)  => (StatusCode::INTERNAL_SERVER_ERROR, msg).into_response(),
        }
    }
}
```

直接实现 axum 的 `IntoResponse`，让 server.rs 的 metrics handler（L155）一行就能把结果变成 HTTP 响应——200 带聚合后的 Prometheus 文本，或 500 带错误消息。用 `String` 而非错误类型枚举，是因为这个结果面向人/抓取器，不面向程序分支。

### 3.4 `WorkerManager`：无状态工具集（L84-267）

```rust
pub struct WorkerManager;                     // L84 —— unit struct
```

零字段。所有方法都是关联函数（`pub fn` / `pub async fn`，无 `&self`），状态全部来自参数：worker 列表问 `&Arc<WorkerRegistry>` 要，HTTP 客户端由调用方给。这是刻意的"函数式工具模块"设计——不存在生命周期、不存在并发共享、单测只需 mock 一个 registry。

#### `get_worker_urls`（L87-93）

`registry.get_all()` 拷出 worker 列表，map 出 URL 串。server.rs L1021 用它响应 worker 列表查询。简单到不值一提，但它是"registry 是唯一 worker 真相源"原则的体现——本模块自己从不缓存 worker 列表。

#### `flush_cache_all`（L95-158）

管理动作：让所有 worker 清空引擎 KV cache。流程：

1. `worker_registry.get_all()`（L99）——**全量**，不过滤健康状态（刷缓存对病 worker 也无害，且often正是为了救它）；
2. 过滤 `ConnectionMode::Http`（L102-105）——gRPC worker 的 flush 走别的路径（gRPC 路由域自己管），HTTP 才走本函数；
3. 空 HTTP 池则提前返回带解释性 message 的 `FlushCacheResult`（L107-115）；
4. `fan_out(workers, client, "flush_cache", POST)`（L123）——对应 SGLang 引擎 HTTP server 的 `POST /flush_cache` 端点；
5. 三路归档（L128-134）：`Ok + 2xx` → successful；`Ok + 非 2xx` → failed（`"HTTP {status}"`）；`Err` → failed（transport 错误串）；
6. 组装 `FlushCacheResult { successful, failed, total_workers, http_workers, message }`（L151-157）——`total_workers` 与 `http_workers` 并存，让调用方能区分"总数"与"实际可操作数"。

注意 message 的措辞逻辑（L136-147）：全成功、部分成功两种文案，都是给人看的（API 响应/日志 L149）。

#### `get_all_worker_loads`（L160-205）

负载快照：向每个 worker 问"你现在背了多少请求"。与 `fan_out` 不同，这里**没用** buffer_unordered，而是 `future::join_all`（L195）全并发：

```rust
let loads = future::join_all(futures).await;  // L195
```

每个 future 内部（L180-191）：HTTP worker → `parse_load_response`；非 HTTP → `load: -1` 哨兵。同时把 `WorkerType` 翻译成标签（L172-176：Regular→None、Prefill→"prefill"、Decode→"decode"），供结果 JSON 呈现。最后统计 `successful = load >= 0` 与 `failed = load < 0`（L196-197）。

为什么这里敢无界并发而 `fan_out` 要限 32？负载查询是 GET 且预期快（引擎内存计数），且这是 `LoadMonitor` 周期任务唯一依赖的路径，限流会让快照时间被拉长失真；而 flush/metrics 的响应体大、耗时长，必须限。两个函数的并发策略差异是**按请求代价量身定做**的，不是无心之失。

#### `parse_load_response`（L207-230）

```rust
let load_url = format!("{}/v1/loads?include=core", url);   // L212
```

打 SGLang 引擎的 `GET /v1/loads?include=core`，解析 JSON 路径 `aggregate.total_tokens`（L219-225）——即引擎侧聚合的 token 负载（running + queue 的 token 量级）。任何一步失败（HTTP 错、非 2xx、JSON 坏、路径缺）统一回落 `-1`（L226-229）。**用 `isize` + `-1` 哨兵而不是 `Option<isize>` 或 `Result`**：下游只需 `>= 0` 判断就能分流成功/失败，JSON 序列化和 HashMap 聚合（`LoadMonitor` 里 `HashMap<String, isize>`）都无需处理嵌套类型——简洁性的代价是"非 HTTP worker"与"查询失败"在类型上不可区分（都折叠成 -1）。

#### `get_engine_metrics`（L232-266）

Prometheus 指标聚合：

1. 无 worker → `Err("No available workers")`（L238-240）；
2. `fan_out(workers, client, "metrics", GET)`（L242）——引擎的 `GET /metrics` 暴露 Prometheus 文本格式；
3. 成功的响应体包成 `MetricPack { labels: vec![("worker_addr", url)], metrics_text }`（L249-252）——**worker URL 作为标签注入**，这是多实例指标可区分的关键；
4. 全军覆没 → `Err("All backend requests failed")`（L258-260）；
5. `metrics_aggregator::aggregate_metrics(metric_packs)`（L262）把 N 份文本合并成一份（同指标按标签维度拼接），成功 `Ok(text)` / 失败 `Err`。

server.rs L155 的网关 `/metrics` 端点直接消费它——**抓取网关 metrics = 抓取全部引擎 metrics 的聚合视图**，运维不必逐实例抓取。

### 3.5 `LoadMonitor`：常驻负载监控（L269-394）

```rust
pub struct LoadMonitor {                      // L270-278
    worker_registry: Arc<WorkerRegistry>,
    policy_registry: Arc<PolicyRegistry>,
    client: reqwest::Client,
    interval: Duration,
    tx: watch::Sender<HashMap<String, isize>>,
    rx: watch::Receiver<HashMap<String, isize>>,
    monitor_handle: Arc<Mutex<Option<JoinHandle<()>>>>,
}
```

字段分三组：两个 registry 的 `Arc`（只读共享）、reqwest client（连接池复用）、以及**任务生命周期三件套**——`watch` 的 tx/rx 对与 `monitor_handle`。

#### 构造 `new`（L280-298）

`watch::channel(HashMap::new())`（L287）起步值为空 map。`watch` channel 的语义是"只保留最新值"：任何时刻 `subscribe()` 的接收者立刻能读到当前快照，不需要历史回放——这正是负载快照该有的语义（3 秒前的负载没有意义）。

#### `start` / `stop` / `is_running`（L300-332, L380-383）

```rust
pub async fn start(&self) {
    let mut handle_guard = self.monitor_handle.lock().await;
    if handle_guard.is_some() { debug!(...); return; }    // L302-305 幂等
    ...
    let handle = tokio::spawn(async move {
        Self::monitor_loop(...).await;                    // L318-320
    });
    *handle_guard = Some(handle);
}
```

- **幂等启动**：句柄已存在就 debug 一句返回，重复调用无害（server.rs 启动流程可能多次触发）。
- **可停**：`stop()`（L325-332）`take()` 出句柄 → `abort()` → `await` 等任务真正退出。abort 是强杀，但 monitor_loop 里没有需要清理的临界资源（registry 是外部共享的，watch tx 随任务结束自动关闭），所以安全。
- `is_running`（L380-383）只是查句柄是否存在。

`monitor_handle` 用 `Arc<Mutex<Option<JoinHandle>>>` 而非裸 `Option`：`LoadMonitor` 以 `Arc` 共享（app_context.rs L53 存的是 `Option<Arc<LoadMonitor>>`），start/stop 可能从不同 handler 并发调用。

#### `subscribe`（L334-336）

返回 `watch::Receiver` 的 clone。任何想拿"最新负载快照"的模块（metrics 导出、调试 API、未来的自适应策略）都能零成本挂上，且**晚来的订阅者立即拿到最近一次值**——这是选 `watch` 而非 `mpsc`/`broadcast` 的决定性理由。

#### `monitor_loop`（L338-378）——核心循环

```rust
let mut interval_timer = tokio::time::interval(interval);   // L345
loop {
    interval_timer.tick().await;                            // L348

    let power_of_two_policies = policy_registry.get_all_power_of_two_policies();  // L350
    if power_of_two_policies.is_empty() {
        debug!("No PowerOfTwo policies found, skipping load fetch");              // L352-354
        continue;                                          // ← 关键短路
    }

    let result = WorkerManager::get_all_worker_loads(&worker_registry, &client).await;  // L357

    let mut loads = HashMap::new();
    for load_info in result.loads { loads.insert(load_info.worker, load_info.load); }   // L359-362

    if !loads.is_empty() {
        for policy in &power_of_two_policies {
            policy.update_loads(&loads);                   // L370-372 ← 喂数据
        }
        let _ = tx.send(loads);                            // L373 ← 广播快照
    } else {
        warn!("No loads fetched from workers");            // L375
    }
}
```

四个要点：

1. **按需轮询**：只有集群里配置了 `PowerOfTwo` 策略才真正打后端。PowerOfTwo（随机取二、择负载低者）是唯一实现 `update_loads`（trait 默认 no-op，policies/mod.rs L76-78）的消费方；cache_aware/round_robin 等策略用 `Worker::load()` 的网关侧计数，不需要引擎真值。没有消费者就完全不产生监控流量——**监控的开销跟着需求走**。
2. **喂策略优先于广播**：`update_loads` 同步推给每个策略（策略内部更新自己的负载视图），`tx.send` 的失败被 `let _ =` 忽略（watch 无订阅者时 send 只更新存量值，不算错误）。
3. **空结果不推送**：全体 -1 时 `loads` 其实非空（都是 -1 的项）……注意 L359-362 组装的是所有 worker 的项（含 -1），`is_empty` 只在 worker 列表本身为空时成立；-1 的项会照常进策略。这是一个值得留意的细节：**查询失败的 worker 在策略眼里负载是 -1**，PowerOfTwo 侧如何解读负值是它自己的语义（通常被当作"信息缺失"而非"最闲"）。
4. **首 tick 立即触发**：`tokio::time::interval` 的第一次 `tick()` 立刻返回，监控启动后马上就有第一份快照，不用等一个周期。

#### `Drop`（L386-394）

```rust
impl Drop for LoadMonitor {
    fn drop(&mut self) {
        if let Ok(mut handle_guard) = self.monitor_handle.try_lock() {
            if let Some(handle) = handle_guard.take() { handle.abort(); }
        }
    }
}
```

析构时 `try_lock` 而非 `lock().await`（Drop 里不能 await）也不阻塞：拿不到锁说明别人正在 start/stop，交给他处理。拿到了就 abort 任务，防止 monitor 泄漏成孤儿线程。`try_lock` 失败被静默接受——最坏情况是任务多活一会儿，随进程退出回收，可接受。

## 4. 负载均衡：本模块在选路体系里的位置

sgl-model-gateway 的负载信息有**两条并行的供应链**，服务不同策略：

| 供应链 | 数据源 | 更新方式 | 消费者 |
|---|---|---|---|
| **网关侧计数** | `Worker::load()`（core/worker.rs L172；请求进出时 `increment_load`/递减） | 同步、即时、零开销 | cache_aware（失衡判定）、round_robin 兜底等 |
| **引擎侧真值**（本模块） | 引擎 `GET /v1/loads` 的 `aggregate.total_tokens` | 周期拉取（LoadMonitor，默认间隔由 config 定） | PowerOfTwo（`update_loads`）+ watch 订阅者 |

为什么 PowerOfTwo 需要引擎真值？因为它比较的是"两个候选里谁更闲"：网关侧计数只反映在途转发数，而引擎内部 token 级负载（长 prompt vs 短 prompt 差异巨大）才是真实压力。cache_aware 的失衡判定只需粗粒度相对比较，网关计数够用；PowerOfTwo 要做精细二选一，值得付出周期拉取的成本。

**闭环路径**：`LoadMonitor.monitor_loop`（L338）→ `WorkerManager::get_all_worker_loads`（L160）→ `policy.update_loads`（L371）→ PowerOfTwo 在下次 `select_worker` 时用新快照择优 → 请求经 routers 选路落盘。监控与选路解耦在时间轴上：策略永远用"最近一次快照"决策，容忍一个轮询间隔的陈旧度——负载均衡本来就是概率游戏。

## 5. 与请求 pipeline 的关系

严格说：**没有关系——这正是设计**。请求转发热路径是：

```
client → server.rs axum 路由 → middleware（限流/队列）→ routers/http/router.rs
  → select_worker_for_model（L134）→ PolicyRegistry 选策略 → policy.select_worker
  → worker（HTTP/gRPC 转发）
```

全程不经过 `WorkerManager`/`LoadMonitor` 的任何代码。本模块的三类出口都挂在**非推理端点**上：

- server.rs **L155**：网关 `/metrics` → `get_engine_metrics`（给 Prometheus 抓取）；
- server.rs **L402**：`/flush_cache` 类运维端点 → `flush_cache_all`；
- server.rs **L408**：负载查询端点 → `get_all_worker_loads`；
- server.rs **L1021**：worker 列表端点 → `get_worker_urls`；
- server.rs **L929-932**：进程启动时 `load_monitor.start().await`（与 L917-927 的 health checker 启动相邻——两件事都是"后台常驻服务"，但一个在 WorkerRegistry，一个在这里）。

唯一的"间接进入热路径"通道是 4 节的闭环：LoadMonitor 的数据**异步地**影响 PowerOfTwo 的选择，但永远不会阻塞或内联在某个请求的处理里。控制面慢 5 秒（REQUEST_TIMEOUT 上限），数据面毫秒级选路，互不拖累。

## 6. 与其他模块的交互

| 模块 | 交互点 | 性质 |
|---|---|---|
| `core/worker_registry.rs` | `get_all()` 取全量 worker；其 `start_health_checker`（L646）承接本模块不管的健康检查 | worker 真相源 |
| `core/worker.rs` | `Worker` trait：`url`/`api_key`/`worker_type`/`connection_mode`（L115-124）；`load`/`increment_load`（L172-175，网关侧计数供应链的另一半） | 数据提供方 |
| `policies/registry.rs` | `get_all_power_of_two_policies`（L258）——monitor_loop 的消费方发现机制 | 策略装配层 |
| `policies/power_of_two.rs` | `update_loads(&HashMap<String, isize>)`——本模块产出的最终归宿 | 数据消费者 |
| `policies/mod.rs` | `LoadBalancingPolicy` trait 的 `update_loads` 默认 no-op（L76-78） | 接口契约 |
| `protocols/worker_spec.rs` | `FlushCacheResult`/`WorkerLoadInfo`/`WorkerLoadsResult`——三个出参类型 | API 形状 |
| `core/metrics_aggregator.rs` | `MetricPack` 与 `aggregate_metrics`——Prometheus 文本合并 | 指标聚合 |
| `server.rs` | L155/L402/L408/L929-932/L1021 五个挂载点 | HTTP 出口与启动编排 |
| `app_context.rs` | L455 构造 `LoadMonitor`（L53 存为 `Option<Arc<LoadMonitor>>`） | 依赖注入容器 |
| 后端 SGLang 引擎 | `POST /flush_cache`、`GET /v1/loads?include=core`、`GET /metrics` 三个 HTTP 端点 | 跨进程协议 |

依赖方向非常干净：本模块只 import registry/worker/policy 的接口与协议类型，不反向依赖任何 router/handler——所以它能被 server、测试、未来 CLI 工具任意复用。

## 7. 关键设计决策

1. **无状态 unit struct + 关联函数**：`WorkerManager` 零字段，状态全部外置（registry 持 worker 真相、调用方持 HTTP client）。收益是三重的：天然线程安全、单测零 mock 基建（造个 registry 就能测）、不参与任何生命周期管理。"生命周期操作"被精确定义为"对已注册 worker 的运维请求"，而非进程管理。
2. **两套并发策略按请求代价分化**：`fan_out` 用 `buffer_unordered(32)` 有界并发（flush/metrics 响应重、耗时长）；`get_all_worker_loads` 用 `join_all` 无界并发（负载查询轻快、且被周期任务依赖，限流会拉长快照时间窗）。同文件内并存的两种模式不是不一致，而是对"管理面请求代价谱系"的显式回应。
3. **`watch` channel 的"最新值"语义**：负载快照只有当前值有意义。watch 让晚订阅者立即拿到现值、无回放压力、send 在零订阅者时也不算错误（`let _ = tx.send(...)` L373）。对比 mpsc（会丢晚订阅者）与 broadcast（要回放/丢包处理），这是语义最贴合的选择。
4. **监控流量按需产生**：monitor_loop 在没有 PowerOfTwo 策略时 `continue` 短路（L352-355），一个周期都不打后端。监控成本与消费需求精确挂钩，避免"为了监控而监控"的常驻空转。
5. **哨兵值 `-1` 折叠失败语义**：`parse_load_response` 的所有失败路径（HTTP 错/非 2xx/JSON 坏/字段缺）与非 HTTP worker 统一折叠为 `load: -1`，下游用 `>= 0` 一个比较即可分流。换来 JSON 与 HashMap 的平坦性，付出"失败原因不可区分"的代价——在"聚合给策略与展示"的场景里是划算的交换；PowerOfTwo 把 -1 视为信息缺失即可。

## 8. 阅读建议

1. **先读 L1-27 再读 L84 和 L270**：模块文档、两个常量、两个 struct 定义加起来不到 40 行，却是全文件的骨架——两个角色（工具集/监控器）+ 两个数字（5s/32）划定了所有行为的边界。
2. **把 `fan_out`（L36-68）当模板读**：理解了"闭包捕获 url/api_key → async move → buffer_unordered → Vec 归因"这一套，`flush_cache_all` 和 `get_engine_metrics` 就是它的两次实例化；再对比 `get_all_worker_loads` 为何不用它，并发策略的取舍就懂了。
3. **monitor_loop（L338-378）逐行读完**：只有 40 行，但包含四个语义决策（首 tick 立即、无消费者短路、先喂策略后广播、空结果不推送），每个都值得停下来问一句"为什么"。
4. **对照启动编排读**：跳到 server.rs L915-932，看 health_checker 与 load_monitor 如何在服务启动时被拉起——这 18 行是本模块与 `WorkerRegistry` 职责分界的最佳注脚（谁管健康、谁管负载，一目了然）。
5. **追一条数据链**：从引擎的 `GET /v1/loads` 响应（`aggregate.total_tokens`）→ `parse_load_response`（L207）→ `WorkerLoadInfo` → `update_loads` → PowerOfTwo 的选择。走通这条链，"控制面如何异步影响数据面"就有了具体的肌肉记忆。
6. **与姊妹篇对照**：`explain/sglang-rust-cache_aware.md` 讲的是选路策略本体（网关侧计数供应链的消费端）；本篇讲引擎真值供应链的源头。两篇合起来正好覆盖 sgl-model-gateway 负载均衡的完整供需两侧。
