# restful_api.py — RESTful API 服务面精讲

> 源文件：`~/ai/inference/xinference/api/restful_api.py`（HEAD b3de260，3832 行）

## 1. 角色定位

11 层 understand 图谱中属 **layer:api** 的唯一核心：supervisor 集群仅此一个 HTTP 门面。向下经 xoscar ActorRef 触达 **layer:core** 的 `SupervisorActor`，向旁代理 **layer:router**。进程上不独立——由 `deploy/local.py:180`、`deploy/supervisor.py:96` 在子进程调 `run()`（3788）拉起 uvicorn。

## 2. 内部结构

全文件几乎只有一个类 `RESTfulAPI(CancelMixin)`（332），约 90 个方法分六组：

- **装配鉴权**：`__init__`（345）构造 `AdvancedAuthService`（缺密钥即 `SystemExit`）；`_init_allowed_ip_list`（417）CIDR 白名单；`_audit_middleware`（572）审计。
- **serve() 流水**（806-974）：CORS→IP 限制→审计→OTEL→`register_all_routes`（852，从 `api/routers/` 12 个领域模块注册）→oauth2/OIDC→`/metrics`+15 秒指标循环（898/976）→加固 uvicorn `Config`（961-972，防 Slowloris）。
- **OpenAI 兼容推理**：`create_chat_completion`（3307，核心）、`create_completion`（1688）、embedding/rerank/audio/images/videos/world 系列。
- **Anthropic 兼容**：`create_message`（1856）挂 `/v1/messages`，靠 `api/protocols` 的 `openai_to_anthropic` 与 `_iter_openai_sse_bytes`（1593）互转。
- **模型生命周期**：`launch_model`（1151）、`terminate_model`（1439）、`add_model_replica`（1464）等。
- **Token Router 代理**：`_proxy_token_router_chat_completion`（714），httpx 懒单例（673）。

## 3. 外部连接

图谱出边 38 条：imports 指向 `core/supervisor.py`、`core/event.py`（错误上报 `_report_error_event`:655）、`api/routers/*`、`api/schemas`、`api/utils`（`require_model`:96）、`api/frontend_static`，并跨层引 `router/constants.py`、`router/credentials.py`。真实入边图谱漏记（延迟 import）：deploy 两处调 `run()`。

## 4. 数据流：一次 /v1/chat/completions

1. `api/routers/llm.py:50` 把端点绑到 `api.create_chat_completion`（`Security(scopes=["models:read"])`）；URL→方法映射全在 routers/，本文件搜不到 `@app.post`。
2. 解析归一（3308-3354）：JSON→`CreateChatCompletion`；`enable_thinking` 折叠进 `chat_template_kwargs`（3325-3344）；guided 参数走 `extract_guided_params`（3713）。
3. 分流（3372-3395）：开 `XINFERENCE_TOKEN_ROUTER_ENABLED` 则 `supervisor.resolve_token_router_runtime`——虚拟模型不可用时 **fail-closed** 返 503（3380-3392）不落回物理模型；可用则字节透传代理（756-792）。
4. 取 Actor：`require_model`→`SupervisorActor.get_model`（supervisor.py:5077）按副本轮询返回 `ModelActor` ref（core/model.py:205）；`ModelNotReadyError`→503+`Retry-After: 30`。
5. 前置校验：非 tool-call 家族带 `tools` 400（3442-3452）；`strict_system_first` 错位 400（3459-3465）。
6. 推理：`model.chat(...)` 经 xoscar RPC 到 `ModelActor.chat`（core/model.py:861）委托引擎实现；流式逐块 yield、补 `"[DONE]"`（3485）、包 `EventSourceResponse(ping=...)`（3515），`finally` 里 `decrease_serve_count`（3513）；`_get_model_last_error`（1675）把 `xo.ServerClosed` 还原成模型最后错误。

## 5. 设计决策

- **OpenAI 兼容**：SDK 用户只改 `base_url` 即迁移；`response_model=ChatCompletion` 兼作 schema 文档；再叠 Anthropic 双协议——兼容做在边缘，core/model 不感知。
- **性能护栏**：强制端点返回 `Response` 子类（904-936），规避 `jsonable_encoder` 热路径（issue #647）；SSE ping 防代理断连。
- **代理字节透传**：不解析不重组 SSE，`asyncio.shield`+`BackgroundTask` 保证断连时上游连接必回收（759-791）。
- **鉴权双模**在构造期读环境变量而非模块常量——fork 子进程不被父进程冻结值误导（358-368 注释）。

## 6. 新人提示

- 切入三步：`serve()`（806）→`api/routers/__init__.py`→`create_chat_completion`（3307）。
- 请求体 `model` 是 **model_uid 非 model_name**，404 先查这个。
- 新增端点=返回 `Response` 的方法+routers/ 注册，缺一样 933 行启动报错。
- 流式 `CancelledError` 必须 `return` 不能 `yield`（3494 注释）。
- 排查先看 `XINFERENCE_TOKEN_ROUTER_ENABLED`（3374）决定走代理还是本地 Actor 链。
