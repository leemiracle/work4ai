# explain-03 · RESTfulAPI——协议兼容大杂烩与 API 门面（xinference/api/restful_api.py）

## 角色定位

`restful_api.py`（3832 行）是 Xinference 对外的 HTTP 门面：一个进程内同时讲 **OpenAI 协议**（`/v1/chat/completions`、embeddings、images、audio、videos）、**Anthropic 协议**（`/v1/messages`）、**Stable Diffusion WebUI 协议**（`/sdapi/*`）和自家的集群管理协议（模型注册/launch/terminate/replica/缓存/token router）。核心是 `RESTfulAPI` 类（`api/restful_api.py:332`，继承 `CancelMixin`）——历史上的 `create_app` 闭包工厂已重构为"类持有 FastAPI 实例 + routers/ 模块注册"的形态（`self._app = FastAPI(lifespan=self._lifespan)`，`:413`），`serve()`（`:806`）负责组装并启动 uvicorn。它自己不跑推理，全部转发给 supervisor/ModelActor ref。

## 内部结构

`__init__`（`:345-415`）做三件事：解析认证模式（advanced auth 双密钥校验失败直接 `SystemExit`，`:371-391`；注释解释为何要在构造时而非模块常量读环境变量——fork 出的子进程要尊重自己的环境）；挂三个 SQLite 存储（launch history `:395`、monitor config `:401`、system settings `:407`）；建 `APIRouter` 与 FastAPI 实例（`:411-413`）。`serve()`（`:806-974`）是组装车间，顺序考究：CORS → IP 白名单中间件（`:815-823`，`XINFERENCE_ALLOWED_IPS` 支持 CIDR）→ 审计中间件 → OTEL → 500 兜底 handler → `app.state.api = self` 供 Depends 注入（`:845-849`）→ `register_all_routes(self)` 从 `api/routers/` 包注册 12 个域路由模块（`:851-854`，见 `routers/__init__.py:30-46`：admin/models/llm/embeddings/rerank/audio/images/videos/worlds/launch_history/system_settings/token_routers）→ advanced auth/OIDC 路由条件注册（`:857-875`）→ Prometheus `MetricsMiddleware`+`/metrics`+15 秒集群指标刷新循环（`:877-902`）→ **全路由返回类型断言**（`:904-936`，任何 handler 不返回 `Response` 子类直接抛错拒绝启动——规避 issue#647 的 `jsonable_encoder` 性能坑）→ 挂载 Web UI 静态目录（`:945-959`）→ 带 Slowloris 防护的硬化 uvicorn（`:961-974`，`create_hardened_http_protocol`+`limit_concurrency`）。

## 外部连接

向上是 `deploy/cmdline.py` 的 `xinference-local/supervisor/worker` 命令（`deploy/supervisor.py:96` 调 `restful_api.run`；`run()` `:3788-3817` 还处理默认端口被占的自动换端口重试）。向下经 `_get_supervisor_ref()`（`:641`）拿 SupervisorActor ref 做控制面调用；推理路径则 `require_model(...)` 拿 ModelActor ref **直连模型子进程**。横向：token router 启用时 `_proxy_token_router_chat_completion`（`:714`）用常驻 `httpx.AsyncClient`（`:412`，lifespan 关闭时释放 `:338-343`）把 chat 请求代理给 router 运行时；`_cluster_metrics_update_loop`（`:976-996`）周期拉 `get_cluster_metrics_data`+`list_models` 灌 supervisor 侧 Prometheus gauges。

## 数据流

以最复杂的 `create_chat_completion`（`:3307`）为例：①pydantic 解析+`_normalize_token_router_chat_payload` 归一（`:3308-3310`）→ ②`enable_thinking` 特判：改写进 `chat_template_kwargs` 同时置 `enable_thinking/thinking` 两键（`:3325-3344`，兼容各家模板）→ ③guided decoding 参数提取、max_tokens 默认值、logit_bias 直接 501（`:3347-3357`）→ ④**虚拟模型分流**：`resolve_token_router_runtime` 命中则整包代理给 token router（503+Retry-After 表示 router 未就绪，`:3374-3395`）→ ⑤`require_model` + `describe_model` 拿模型描述（ModelNotReadyError 转 503+Retry-After:30，`:3403-3408`）→ ⑥按 model_family 做能力门禁：工具调用只放行七个 TOOL_CALL_FAMILY 白名单（`:3433-3452`）、Qwen3.8 的 reasoning_effort 特判（`:3428-3429`）、`strict_system_first` 模型校验 system 消息次序（`:3454-3465`，注释强调要在 stream 分流前拦，避免流式路径 200+SSE 里才炸）→ ⑦stream/非 stream 两路，流式经 `_iter_model_openai_chunks`（`:1626`）转 OpenAI SSE 帧。审计链路独立成中间件：`_check_model_access` 把 model_uid 塞 `request.state`（`:473-475`），`_audit_middleware`（`:572-602`）在响应后按状态码分类（success/model_not_found/error/login_failed）落审计事件并打点 `api_key_requests_total`。

## 设计决策

①**协议兼容优先于内部整洁**：Anthropic 端点 `create_message`（`:1856`）内部有"路由器块流→物理块流"两级变换；`_convert_openai_to_anthropic`（`:3759`）对畸形 tool JSON 做降级重试而非直接失败——外部生态（Claude Code 等）拿它当 Anthropic 网关用，容错就是契约。②**启动期强校验**：路由返回类型断言（`:904-936`）把性能陷阱变成启动失败，这是"fail fast"在框架层的少见应用。③**认证可完全关闭**（`:361-370` 注释），关掉时 `_advanced_auth_service=None` 所有端点裸奔——部署时必须显式决策。④handler 级细节：`handle_request_limit_error`（`:604-607`）把引擎报错文本"Rate limit reached"翻译成 HTTP 429，属于字符串嗅探式的协议桥接，升级引擎时要小心。

## 新人提示

找端点实现别在 restful_api.py 里 grep 装饰器——路由注册已拆到 `api/routers/*.py`（`llm.py`/`models.py` 等），本文件的 `create_chat_completion` 等方法是被 routers 模块绑到 `api._router` 上的 handler 本体。加新端点的姿势：在类里写 handler（返回类型必须是 `Response` 子类，否则启动断言拒绝），再到对应 routers 模块加 route。排查 403 先分清是 IP 白名单（`:816-823`）还是模型级访问控制（`:457-472`）；排查 503 看是模型 loading（Retry-After:30）还是 token router 未就绪（Retry-After:1），两个 Retry-After 值就是两处故障的指纹。
