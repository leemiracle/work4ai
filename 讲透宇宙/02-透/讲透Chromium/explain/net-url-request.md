# url_request.cc：Chromium 网络请求生命周期的中枢状态机

> `net/url_request/url_request.cc`（1478 行）+ `url_request.h`；图谱 15 节点/42 边

## 一、角色定位

//net 自底向上：socket/QUIC 传输 → HTTP 事务与缓存（`net/http`）→ 最上层 `net/url_request`——URL 级资源加载抽象层。`URLRequest` 代表"一次 URL 加载的完整生命周期"：从构造、配置、启动、重定向、认证到读数据、完成/取消，全部状态收敛于一个对象。

1. **URL 语义与字节流的分界线**：下层只认单次请求-响应；重定向跟随、cookie、referrer 降级等 URL 级策略在本层编排。
2. **net 栈与上层服务的接缝**：Network Service 的 `URLLoader` 经 `CreateRequest` 创建它（`url_loader.cc:467`）。
3. **net 最大耦合群的中心**：42 条 import 边横跨 base、net/base、cookies、http、log、ssl、url。

类声明 `url_request.h:105`，继承 `SupportsUserData`。

## 二、内部结构

**Delegate 默认实现（L172-208）**：默认全是"拒绝"——`OnAuthRequired`→`CancelAuth`（L182）、`OnSSLCertificateError`→`Cancel`（L193）、`OnResponseStarted`→`NOTREACHED`（L207）；头文件 L116-130 钉死回调时序（Start→各回调*→OnResponseStarted→Read 驱动 OnReadCompleted*）。

**构造/析构**：构造（L650）首参 `base::PassKey<URLRequestContext>`——只能经 `URLRequestContext::CreateRequest`（`url_request_context.h:101/123`）创建，并注册进 context 存活集合（L673）。析构（L213）先 `Cancel`（L216）、**先于自身销毁 job**（L226，job 拆除时可能戳本对象 UserData），摘集合（L229）后以 `REQUEST_ALIVE` NetLog 收尾（L236）。

**配置 setter 群（L239-597）**：几乎全带 `DCHECK(!is_pending_)`——启动后参数冻结。`set_isolation_info`（L531）从 IsolationInfo 派生 `CookiePartitionKey`（L538-543）。

**核心动词**：`Start`（L599）→`BeforeRequestComplete`（L681）→`StartJob`（L708）启动三部曲；Cancel 家族（L792/796/800）收敛到 `DoCancel`（L808，`job_->Kill()` 在 L831）；`Read`（L845）转发 `job_->Read`（L871）。重定向/恢复/通知各家族（L909/L969/L1084/L991/L938/L1292/L1320）共同模式是"置 `status_=ERR_IO_PENDING` 再转发 job"，详见下节数据流。

## 三、外部连接

**依赖**（42 条 imports 实证）：base/*（bind、histogram、pass_key）+net/base（io_buffer、load_flags、load_timing_info、net_errors、network_delegate、upload_data_stream）+cookies/http/log/ssl/dns/url。

**被依赖**：唯一跨文件 calls 入边来自 `url_request_test_util.cc`；生产侧最大消费者是 `url_loader.cc:467`。

**URLRequestContext 四大件**：`job_factory()`（L618 DCHECK 非空）、`network_delegate()`（L1184）、`net_log()`、`url_requests()` 存活集合。NetworkDelegate 是嵌入 net 的全局观察者（扩展拦截、隐私审计）。

**Job 工厂体系**：`CreateJob(this)`（L645/L704）按 scheme 查 `URLRequestJobFactory` 注册表——构造函数只注册 http/https/ws/wss（`url_request_job_factory.cc:58/60/63/65`），统一由 `HttpProtocolHandler` 转发 `URLRequestHttpJob::Create`（该文件 L37-42）；未知 scheme 返回 `URLRequestErrorJob(ERR_UNKNOWN_URL_SCHEME)`（:94 起）。另有 L693/L698 直接构造的 Error/Redirect job 与测试用 Filter/MockDataJob；**file:/data: 的 job 已不在 //net 树内**，旧文档常误导。

## 四、数据流

1. **启动链**：`Start`（L599）初始化 load timing（L627-629），有 NetworkDelegate 先 `NotifyBeforeURLRequest`（L633，可拦截挂起）→`BeforeRequestComplete`（L681）：失败给 `URLRequestErrorJob`（L693）、改 URL 给 `URLRequestRedirectJob`+307（L698-702，307 保 POST）、否则 `CreateJob`（L704）→`StartJob`（L708）把请求头/优先级/上传流搬进 job（L727-741）、校验 referrer 策略（L755-771），置 `ERR_IO_PENDING`（L782）后 `job_->Start()`（L783）——**永远异步完成**（L776 注释）。
2. **网络事务**：`URLRequestHttpJob`→`HttpTransaction`（HttpCache→HttpNetworkTransaction→socket/QUIC）。期间可能上报 `NotifyConnected`（L893）、证书请求（L1229）、SSL 错误（L1246）。
3. **重定向环**：job 侧判定重定向后 `CanFollowRedirect`（url_request_job.cc:472）、`ComputeRedirectInfo`（:478）算新方法/referrer/SiteForCookies，回调 `ReceivedRedirect`（:486）。本文件 L909 置 `is_redirecting_`（L911）、取弱指针（L918）后调 delegate（L921）：拒绝即止；不 defer 直接 `Redirect`；defer 存 `deferred_redirect_info_`（L930）。
4. **Redirect（L1084）**：`NotifyBeforeRedirect`（L1101）→缓存上传进度（L1104，POST 变 GET 后定格）→`PrepareToRestart`（L1061）销毁旧 job→`RedirectUtil::UpdateHttpRequest` 重写头（L1108，303/301 时 POST→GET 清 body）→更新 method/referrer/isolation（L1114-1120）→`url_chain_.push_back`（L1129）、`--redirect_limit_`（L1130，上限 20 跳，h:110）→**递归回 `Start()`（L1132）**。HSTS 同环升级 https（`url_request_http_job.cc:1155`）。
5. **响应与读体**：`OnHeadersComplete`（L1292）固化 LoadTimingInfo 并换算阻塞口径（L1314）；`NotifyResponseStarted`（L938）→delegate（L964，其后注释：`this` 可能已销毁，函数尾禁加代码）。Delegate 反复 `Read`（L845）→`OnReadCompleted`（L1287，同样禁忌）→完成后 `NotifyRequestCompleted`（L1320）。Storage Access 路径 `RetryWithStorageAccess`（L1135）重跑同一 URL，**同样计入 redirect_limit**（L1169-1170）。

## 五、设计决策

**URLRequest vs 简单 socket API**：重定向、缓存、cookie、认证、证书、HSTS、隔离键全是跨多次往返的状态；`URLRequest` 收敛为一个状态机，下层 job/transaction 保持"单跳无状态"。

**每跳一 job**：`url_chain_`（h:1126）记全程，`job_`（h:1123）只代表当前跳，重定向=销毁重建；job 无需理解重定向，`URLRequest` 无需理解 HTTP。

**双层 Delegate**：`URLRequest::Delegate`（结果消费者）与 `NetworkDelegate`（全局观察者）分离，扩展拦截不必污染每个消费者；`LogBlockedBy`（L361）+`blocked_by_` 把阻塞源写进 UI 可见加载状态（L309-313）。

**状态机自我保护**：`status_` 单向变坏——`set_status`（L883-887）DCHECK 禁止从错误恢复，`DoCancel` 注释（L816-817）明言已失败后取消是 no-op。弱指针（h:1317）+三处"回调后禁写代码"注释（L935/L965/L1289）系统性防御"回调内销毁请求"。PassKey（L650）+存活集合（L673/L229）把构造收口到 context。

## 六、新人提示

- **参数要赶早改**：setter 全带 `DCHECK(!is_pending_)`，Start 后再改 debug 构建直接崩。
- **回调里 `this` 随时会死**：三个 delegate 回调之后禁止碰成员；异步续命用 `GetWeakPtr()`（L1474）。
- **跨跳状态放 URLRequest 成员**：重定向后 job 全新，`final_upload_progress_`（L1103-1104）是范式。
- **调试**：NetLog 第一工具——`REQUEST_ALIVE`（L674/L236 构造析构配对）、`URL_REQUEST_START_JOB`（L716，每跳一对，数它即知重定向跳数）、`DELEGATE_INFO`（L373）；`url_chain`/`delegate_blocked_by` 字段见 L324-343。
- **测试**：主战场 `url_request_unittest.cc`，配套 test_util/Filter/MockDataJob。
- **上游已迁移**：浏览器主路径是 URLLoader（mojo 边界）；但它就是最大的 `URLRequest::Delegate` 实现，本文件状态机仍是所有出网请求必经之路。

---

*行号均对本仓快照 grep -n 逐条实证（含跨文件引用）。*
