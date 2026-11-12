# dns-host-resolver —— HostResolverManager：Chromium DNS 解析的调度中枢

目标文件：`net/dns/host_resolver_manager.cc`（1965 行）+ `host_resolver_manager.h`（667 行）——net/dns 中节点最丰富的文件之一（图谱 39 节点、95 条边）。三条主线：**Job 状态机**（请求聚合推进）、**DoH 任务序列**（secure/insecure 回退竞速）、**stale cache**（失败兜底）。

## 一、角色定位

主机解析接口是 `HostResolver`，真正干活的是 `HostResolverManager`。头文件 L66 注释一锤定音："Scheduler and controller of host resolution requests"——解析天然是全局资源，故设计为**浏览器进程内近似单例**，外部经每个 `URLRequestContext` 一份的 `ContextHostResolver`（context_host_resolver.h L39）间接访问。它管四件事：同 host 请求挂同一 `Job` 去重（.h L83-89 图）、`PrioritizedDispatcher` 限并发（.h L98）、本地捷径（IP 字面量/localhost/hosts/缓存不走网络）、生成任务序列让 Job 执行到出结果。

**该文件已拆成家族**：`Job`、`RequestImpl`、端点请求、mDNS listener 与四种任务实现（system/dns/mdns/nat64）各在兄弟文件，本文件保留 Manager 本体。老叫法 "ProcTask/DohTask" 已过时——getaddrinfo 现为 `HostResolverSystemTask`，DoH 查询为 `HostResolverDnsTask` 的 kHttp 模式。

## 二、内部结构

按功能簇（行号均经 grep -n 实证）：

- **本地解析簇（L798-1282，本文件的灵魂）**：`InitializeJobKeyAndIPAddress()`（L798）转去重键、`ResolveLocally()`（L858）本地总入口、`CreateAndStartJob()`（L993）去重建 Job。
- **任务序列生成簇（L1307-1538）**：`GetEffectiveSecureDnsMode()`（L1307）、`PushDnsTasks()`（L1340）、`CreateTaskSequence()`（L1424）——见第四节。
- **其余一笔带过**：请求工厂（L537-612）、常量与调度（L196 默认并发 64、L198 `GetDispatcherLimits()`）、DoH 探测 `ProbeRequestImpl`（L346-423）、IPv6 探测（L1543-1710）、网络变更响应（L1712-1887）。

## 三、外部连接

依赖按层（图谱 95 条 imports 边）：调度层 `prioritized_dispatcher.h`；DNS 协议栈 `dns_client.h`（唯一 DnsClient 持有者）；缓存与上下文 `host_cache.h`/`resolve_context.h`；网络状态 `network_change_notifier.h`；跨层的 `http_network_session.h`——net 栈少见的"下层反向 include 上层"，靠前向声明控制。被依赖：直接 include 本 .h 的非 net/dns 文件只有 `url_request_context_builder.cc`，其余全走中间层——`ContextHostResolver` 转发、`HttpNetworkSession` 经接口消费、`StaleHostResolver`（stale_host_resolver.h L37）装饰兜底。

## 四、数据流（Job 状态机主线）

一次解析（TransportConnectJob 触发）：

1. **创建与启动**：`CreateRequest()`（L551）产出 `RequestImpl`（显式 Start 惯例）；`Start()`（request_impl.cc L79）设 `next_state_=STATE_IPV6_REACHABILITY` 进 `DoLoop()`（L252）——查 AAAA 且探测缓存过期时先 `StartIPv6ReachabilityCheck()`（L1569）异步挂起（WiFi 默认跳过探测，L1590-1600）。
2. **JobKey 推导**：`InitializeJobKeyAndIPAddress()`（L798）算出去重键（host+NAK+类型+flags+source+secure+context），未指定类型默认 A+AAAA（L820）。
3. **本地解析**：`ResolveLocally()`（L858）先在 L873 生成任务序列，再同步消费前端本地任务：主机名校验（L888-896，mDNS 放宽）→ 空名/超长名 `ERR_NAME_NOT_RESOLVED`（L905-909）→ IP 字面量（L912-922，IPv6-only 网插队 NAT64）→ localhost（L926）→ 缓存/CONFIG_PRESET/HOSTS（L933-984）。命中即同步返回（带 `EntryStaleness`），不建 Job；全 miss 返回 `ERR_DNS_CACHE_MISS`（L990）。
4. **Job 状态机**：`CreateAndStartJob()`（L993）查 `jobs_` map（.h L314）：同 key Job 已存在则 `AddRequest` 挂接（去重生效）；否则新建并 `Job::Start()`（job.cc L725）→ `RunNextTask()`（job.cc L510）主循环——序列空则用存储的错误收尾，否则按任务类型决定是否经 dispatcher 派发（SYSTEM/DNS/MDNS 占槽，SECURE_DNS 不占），队列满时驱逐最老最低优先级 Job（job.cc L567-568）。DNS 任务失败走 `OnDnsTaskFailure()`（job.cc L885）把错误压进 `completion_results_` 继续；`CompleteRequests()`（job.cc L1266）收尾——写 HostCache、向全部 Request 分发回调（origin 线程），请求侧 `OnJobCompleted()`（request_impl.cc L233）跑 callback。取消时 `Job::CancelRequest()`（job.cc L357）：**最后一个 Request 摘除才中止 Job**。

**任务序列生成规则**（`CreateTaskSequence` L1424 + `PushDnsTasks` L1340）是理解 DoH 竞速的钥匙。序列以缓存查找开头（Secure 模式 `SECURE_CACHE_LOOKUP` 否则 `CACHE_LOOKUP`；bootstrap 三层 SECURE 缓存→CONFIG_PRESET→insecure 缓存，L1439-1446）接 HOSTS，再按 Secure DNS 模式分叉：

- **kSecure**（L1363-1370）：只 push `SECURE_DNS`，绝不回退明文——除非配置错误无 DoH 可用（crbug.com/1326526）。
- **kAutomatic**（L1372-1400）：`SECURE_CACHE_LOOKUP → SECURE_DNS → INSECURE_CACHE_LOOKUP → DNS → (SYSTEM)`——先 DoH，失败先查 insecure 缓存再发明文；若 `FallbackFromSecureTransactionPreferred()`（DoH 全探测失败）则直接从明文开始。
- **kOff**（L1402-1405）：明文 DNS+系统。

L1417-1420 允许回退时 `SYSTEM` 兜底压尾；强制 SYSTEM 特例：`HOST_RESOLVER_CANONNAME`（L1473，CNAME 支持差）与 `*.local` 查询（L1497-1501，公共递归不处理 mDNS 名）。

## 五、设计决策

**DoH 竞速：序列化回退而非赛跑**。Chromium 没做"同时发 DoH 和 UDP 谁先回用谁"，而是序列化回退+细粒度短路——任务序列本身就是优先级声明，失败才降级。理由：① 查询放大——双路并发使上游 QPS 翻倍，且明文查询本身就泄露域名（加密收益归零），故 kSecure 宁可失败不回退明文（L1363-1370）；② `FallbackFromSecureTransactionPreferred()` 把"DoH 可用性"做成序列生成输入——DoH 全挂自动切明文；③ 回退路径插 `INSECURE_CACHE_LOOKUP`（job.cc L818）：DoH 失败先查缓存里的历史明文结果，常免掉一次真实查询。DoH 事务完全绕开 dispatcher（job.cc L866-870）——HTTP 栈自带并发管理。

**stale cache 三层兜底**。① 参数级 `CacheUsage::STALE_ALLOWED`（L1097-1100 走 `HostCache::LookupStale`，过期也返回）；② `STALE_ALLOWED_WHILE_REFRESHING`（L1102-1111：stale 在 Job 创建前同步给出，后台继续刷新）；③ 装饰器级 `StaleHostResolver` 整层包装。哲学：**解析失败比数据陈旧更伤体验**——错误页"重试"常能靠一条过期缓存救活。

**去重键与并发预算**。同 host 的 secure 与 insecure 查询是两个 Job——安全语义不同。并发默认 64（L196），field trial 可调预留槽（L198），insecure 任务按事务数扩槽（.h L274）。配置变更激进失效：`OnSystemDnsConfigChanged()`（L1824）无论是否真变都 `InvalidateCaches()`——宁可错杀不可放过。

## 六、新人提示

1. **单线程铁律**：.h L94 明言非线程安全，回调经 WeakPtr/origin sequence 回来。`ProbeRequestImpl::CancelRunner()`（L402）的 DeleteSoon 注释是重入陷阱活教材——runner 析构可重入 `jobs_`。
2. **Job 生命周期**：Request 取消≠Job 取消——最后一个 Request 摘除才中止（job.cc L357）。调试"还在发查询"先看 `jobs_` 挂了几个。

3. **地图与测试**：改 Manager 前先读 `net/dns/README.md`。`host_resolver_manager_unittest.cc` 约 1.6 万行是最权威规格；`SetDnsClientForTesting`（L766）注 mock DnsClient、`SetHaveOnlyLoopbackAddresses`（L747）控 IPv6 分支。
4. **常见失误**：往 `TaskType`（.h L319-330）加类型须同步改 `CreateTaskSequence`/`PushDnsTasks`/`Job::RunNextTask` 三处 switch，漏一处即 NOTREACHED 崩溃；本地任务须在 Job 创建前消费完（job.cc L604-610 对到达 Job 的本地任务直接 NOTREACHED）。
