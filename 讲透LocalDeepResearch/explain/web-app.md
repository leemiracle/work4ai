# web/fastapi_app.py — FastAPI 主应用：中间件栈与请求装配线

> 精讲对象：`src/local_deep_research/web/fastapi_app.py`（2651 行）。勘误钉版：web 入口是本文件 + `web/app.py`，**不是** `web/utils/app.py`。

## 1. 角色定位

知识图谱 16 层中属 **Web 服务层** 根节点（入边 0——靠 uvicorn 模块字符串消费的进程顶点）。docstring 自称 "application factory"，实现是**模块级单例**：`app = FastAPI(...)` 在 L2141 import 时创建，随后以工厂式 setup 函数装配。进程入口 `web/app.py::main()` 以 `uvicorn.run(..., workers=1)` 拉起（Socket.IO 无 Redis 队列的硬约束），并把 Socket.IO 挂为 ASGI 子应用 `/ws`（L2339）。

## 2. 内部结构

- **密钥**：`_load_secret_key`（L54-110）`O_EXCL` 原子建 `.secret_key`，读失败/空文件 RuntimeError（拒绝静默降级毁会话）。
- **lifespan**（L162-455）：startup `set_main_loop`（L175，后台线程发 Socket.IO 的前提）、queue processor v2（L321，pytest 默认关）等；shutdown 在 `yield` 后逆序停止（L410-452）。
- **纯 ASGI 中间件族**（L458-1706）：`SecurityHeadersMiddleware`（L479）、`BodySizeLimitMiddleware`（L675，三层配额 multipart ~600GB / JSON 16MB / notes 100MB）、`SecureCookieMiddleware`（L840）、`RememberMeMiddleware`（L968）、`DatabaseMiddleware`（L1484，最内层开每用户加密 DB）。全手写纯 ASGI 而非 BaseHTTPMiddleware——后者缓冲 `StreamingResponse`，SSE 杀手（L2210 注释）。
- **异常/限流**（L1102-1865）：401 重定向登录页（L1109）；catch-all 补安全头（L1185，因 `ServerErrorMiddleware` 在中间件栈之外）；slowapi handler 刻意同步 `def`（L1737，async 版会被丢弃）。
- **装配**：`_add_static_routes`（L1875）防路径穿越；`_mount_all`（L2330）载 20 个 router；`_validate_url_for_bindings`（L2512）启动查模板死链。

## 3. 外部连接

import 期依赖（图谱 6 条）：`template_config`、`dependencies/csrf` 等。运行期 lazy import：20 个 router（缺 `router` 属性即 RuntimeError，L2377）、`socketio_asgi.socket_app`、`queue/processor_v2`。反向无人 import。

## 4. 数据流 — 一次研究请求的流转

1. 中间件栈外→内：CORS（仅 `/api/` 等三前缀）→ SlowAPI → SecureCookie → SecurityHeaders → BodySizeLimit → Session → CSRF → Database → 路由。
2. `POST /research/api/start_research`（routers/research.py:722）async 壳只 `await request.json()`，同步体（`get_user_db_session`+PBKDF2）甩线程池。
3. `_start_research_sync`（research.py:782）取快照，超并发限额走 `_queue_research`（research.py:648）插队并 `notify_research_queued`（L699）。
4. queue processor v2 出队 → `run_research_process`（research_service.py:914）→ `AdvancedSearchSystem` → 策略 `analyze_topic`。
5. 进度回传**不走 SSE**：研究进度走 Socket.IO `emit_to_subscribers`；SSE 仅用于 library/RAG/日志导出（library.py:859 等）。

## 5. 设计决策

- **单例而非 create_app()**：uvicorn 字符串加载 + workers=1 下"import 即装配"最简。
- **纯 ASGI 中间件**：保流式不被缓冲；500/429 处理器复用同一组安全头方法补头（L1195/L1769）防漂移。
- **容错分级**：可选守护包 try 不阻断 boot，SECRET_KEY 硬错。
- **docs 默认关**（L2135，连 `/openapi.json` 一起）；**CORS 空配置 fail-closed**（L2257）。

## 6. 新人提示

- 阅读顺序：`web/app.py::main` → 本文件自底向上（L2141 装配区 → 中间件族 → lifespan）。
- `add_middleware` 是 LIFO，最后 add 的在最外（L2154，测试钉契约）。
- 加路由：入 `_router_modules`（L2350）并导出 `router`；`LDR_STRICT_TEMPLATE_LINKS=1` 时模板死链变硬错。
- 测试坑：`is_testing`（L2131）import 期求值，pytest 收集阶段恒 False，用 `LDR_TEST_MODE`；queue processor 在 pytest 默认不启动（L328）。
