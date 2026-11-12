# 06 · 微服务群：app.py 应用工厂 + ingest.py 主路由

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

服务模式是 NeMo-Retriever 的生产形态：`service/app.py`（405 行）是 FastAPI 应用工厂，按 standalone/gateway/realtime/batch 四种角色装配同一套代码；`service/routers/ingest.py`（2467 行，全仓第二大文件）是主路由，承担"作业聚合"全生命周期——建作业、传文档、追状态、收事件、查询答案。与它并行的 `service/vectordb_app.py`（993 行）是独立 VectorDB 服务（向量库 CRUD/检索的 HTTP 面），两者通过内部令牌互认。dashboard 是挂在 gateway 上的只读监控面。

## 内部结构

**app.py 工厂**（`create_app :252`）：启动三前奏——`_configure_logging`（`:27`，控制台+50MiB 轮转文件双 handler `:38-44`）与 `_apply_resource_limits`（`:53`）：CUDA_VISIBLE_DEVICES 白名单（`:57-59`）、`os.sched_setaffinity` 绑核（`:61-67`）、`resource.setrlimit(RLIMIT_AS)` 内存帽（`:69-77`），全部 best-effort 带异常降级。

**lifespan 装配**（`_lifespan :123`）：九个服务单件按角色分装。job_tracker 先建（`:161`）并挂 metrics 终态观察者（`:162-163`）、event_bus（`:164`）接进 tracker（`:165`）；sidecar_store 只在 gateway/standalone 装（`:166-170`）。分叉点 `:172`：gateway 模式只装 proxy（带内部令牌与公共鉴权头，`:173-177`）+ work_broker（`:178`），自己不跑管线；其余模式从 `pipeline_executor` 取 realtime/batch 双 work_fn（`:186-187`）装 pipeline_pool（`:190-198`），本地模型开预热时 `warmup_process_pool_workers` 线程内执行（`:200-212`）。收尾 `_check_media_dependencies`（`:80-120`）：ffmpeg 缺失打 WARNING 提示 Helm 参数，因为音视频上传会 501 且 gateway 也要做媒体分类。shutdown 全序逆拆（`:225-239`）——executors→broker→proxy→pool→sidecar→bus→tracker→metrics→OTel。

**中间件与路由**：`_RequestIdMiddleware`（`:243-249`）每请求注 uuid；Bearer 鉴权（`:295-302`，含内部令牌与 scope 授权）；MCP 可选挂载（`:259-275` fastmcp combine_lifespans，`:311-313` mount）；五个 router 前缀 `/v1`（`:318-324`）；dashboard 静态目录 gateway 独享（`:328-342`）。探针双分：`/v1/live`（`:344-347`）进程活着即 ok；`/v1/health`（`:349-390`）深就绪——本地模型未热完报 starting（`:353-366`），gateway 并发探测 realtime/batch 双后端（`:377-386`），任一不通 503。兜底异常 handler（`:392-403`）把类名+路径+模式打进 500 响应。

**ingest.py 主路由**（`router :132`）按职能分五组。作业生命周期：`create_job`（`:914-920`，`_job_idempotency_fingerprint :246` 用显式字段白名单 sha256——注释 `:248-252` 说明为何不用全 model dump：防新增字段静默作废旧指纹）、`get_job`（`:1023`）、documents 三查（`:1054-1144`）。上传三形态：document（`:1196`）/page（`:1273`）/whole（`:1415`），共同走 `_prepare_job_work_item`（`:666`）→ 池路由。**池路由规则** `_route_by_page_count`（`:606`）：音视频恒 batch（重管线 `:625-626`）、text/html/image 恒 realtime（`:627-628`）、带 page_number 的补页恒 realtime（`:629-630`）、PDF 用 pypdfium 数页（`_count_pdf_pages :592`）按阈值分流，且客户端要求 pdf_split 时"多于一 chunk 页即 batch"（`:632-634`）。容量防线 `_enqueue_or_reject`（`:387`）、拒绝回滚 `_rollback_rejected_work_item`（`:802`）。事件与状态：SSE 流 `ingest_job_events`（`:2306`，先补发已终态文档的 catch-up 批再实时推）、`ingest_status`（`:1624`）/page/document 三态端点（`:1628-1642`）、批量状态（`:2415`）。检索面：`/v1/answer`（`:1725`，经典+agentic 双形态响应）与 `/v1/query`（`:1886`）。gateway 代理线：`_gateway_enqueue`（`:518`）spool 到 work broker、worker 回调 `job_callback`（`:2084`）、结果回拉 `_pull_and_store_worker_result`（`:472`）与 `worker_document_result`（`:2061`）。遗留端点显式下线：上传与 firehose 两个旧路径返回 410 语义（`:2258-2262` 与 `:2277-2281`）。

## 外部连接

配置源 `service/config.py`（ServiceConfig Pydantic，含 `AgenticConfig :270`）；服务件全家在 `service/services/`——job_tracker（终态观察者模式）、work_queue（gateway↔worker 桥）、pipeline_executor/pipeline_pool（03 篇执行器的进程池包装）、event_bus（SSE 底座）、sidecar_store（大载荷外置）、proxy（gateway 转发）、prometheus/metrics。兄弟路由：collections（集合 CRUD，转发 vectordb）、admin（pool_stats，gateway 上自报空 `app.py:321-323`）、work、dashboard（无构建 CDN SPA，`static/index.html:193-195` unpkg 引 React/Babel——离线白屏是预期）。部署面：helm values.yaml 渲染 `retriever-service.yaml`；`service/client.py` 供 ServiceIngestor 复用。

## 数据流

一次上传的完整旅程：客户端 POST document → 鉴权 → 作业/文档登记（stable_document_id `:332`、manifest 校验 `:346`）→ 页数路由定 realtime/batch → `_prepare_job_work_item` 组 WorkItem → 入队（standalone 直进本地池 / gateway spool 到 broker `:518`）→ worker（realtime/batch 池）跑管线写库 → 回调（standalone 本地 / gateway `job_callback :2084`）→ 结果存储（retain_results 决定是否留 sidecar `:172`）→ SSE 事件推给订阅者 → 客户端也可轮询 status。查询独立成流：`/v1/query` 走 ResolvedQueryPlan（04 篇）查 LanceDB；`/v1/answer` 可升级 agentic。

## 设计决策

1. **四角色一套代码**：同一 create_app 按 mode 分装单件，gateway 无管线、worker 无 proxy——部署拓扑（standalone 单体/split 分离）由配置而非代码分叉，Helm 层才能灵活编排。
2. **幂等指纹白名单化**：指纹只哈希显式列出的字段（`:248-252`），请求模型加新字段不破坏重放判定——API 演进与幂等性解耦。
3. **池路由按"工作形状"而非大小**：媒体类型优先（音视频必 batch）、页数只是 PDF 的启发式——路由依据是管线的计算形状，可预测且免配置。
4. **SSE catch-up 批**：订阅晚到的客户端先收已终态文档（`:2306` docstring 明示），事件流不丢史——轮询与推送两种消费习惯都照顾。
5. **资源限制 best-effort 降级**：绑核/内存帽失败只 WARNING 不阻断启动（`:66-67,76-77`）——容器环境里 cgroup 已做限制时不应硬失败。

## 新人提示

- 本地起服务最快的路径是 dev/compose 的 service-mode（见 L14）；只测路由逻辑用 factory + 假 config，`tests/test_service_health.py` 是现成模板。
- 读 ingest.py 别按行序读：先 132（router）→ 914（create_job）→ 1196（document 上传）→ 606（路由）→ 2306（SSE），主链即通；其余是这五点的支撑函数。
- 上传 501 先查 ffmpeg 横幅（`app.py:110-120`），410 检查是否还在调 firehose/旧上传端点。
- gateway 模式 `/v1/health` 不通先看 backends 子状态（`:367-386`）——问题多半在下游 worker 而非 gateway 自己。
- 新路由挂载记得走 `app.include_router(..., prefix="/v1")`（`:318-324`）的统一前缀；OpenAPI 文档由 docs 脚本自动生成，路径改动会触发 docs CI。
