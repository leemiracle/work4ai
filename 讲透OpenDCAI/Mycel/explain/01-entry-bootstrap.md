# 01 · 后端入口与装配：main / app_factory / bootstrap / lifespan

## 角色定位

这一组文件是 Mycel 后端的"点火系统"：`backend/web/main.py` 是进程入口，`backend/web/app_factory.py` 决定"这个进程长成什么样"，`backend/bootstrap/` 提供与业务无关的启动原语（env 加载、端口解析、CORS、可重载 uvicorn），`backend/web/core/lifespan.py` 则是应用生命周期的总装配线——把存储容器、五个 repo、chat/threads 双运行时、通知接线、空闲回收器在 startup 阶段一次性挂到 `app.state`。理解这四个文件，就拿到了整个后端依赖注入图的根。

Mycel 前身代号 LEON，环境变量（`LEON_BACKEND_PORT`、`LEON_POSTGRES_URL`）与 git worktree 配置键（`worktree.ports.backend`）仍沿用旧名，读代码时不要被两套命名迷惑。

## 内部结构

**main.py（20 行）**做了三件事：`load_env_file_from_env()`（main.py:3，从 `ENV_FILE` 指定的文件加载 dotenv，见 app_entrypoint.py:10-17）；`app = create_app()`（main.py:7，模块级装配，供 `uvicorn backend.web.main:app` 直接引用）；`__main__` 分支（main.py:10-20）以 `python -m backend.web.main` 启动时走 `run_reloadable_app("backend.web.main:app", ...)`，热重载目录被显式限制在 backend/core/config/storage/sandbox/messaging 六个源码目录（main.py:19）——不限制的话 StatReload 会扫 `.venv/`、`node_modules/`、`.git/`，白烧 50-80% CPU（main.py:14-15 的 @@@ 注释原话）。

**app_factory.py 的 profile 分流**是核心：`create_app()`（app_factory.py:13-26）先 `resolve_runtime_profile()` 解析出 `RuntimeProfile`（StrEnum，仅 `FULL`/`COMMUNICATION` 两值，runtime_profile.py:7-9；来源环境变量 `MYCEL_RUNTIME_PROFILE`，非法值直接 RuntimeError 拒绝启动，runtime_profile.py:12-18）。COMMUNICATION 走 `include_communication_routes`（app_factory.py:29-36）——只挂 4 个路由器：`auth.communication_router`、chat 的 `app_router`、`contacts`、`users`；其余（FULL）走 `include_full_routes`（app_factory.py:39-73）——共 16 次 `include_router`，覆盖 threads/sandbox/webhooks/thread_files（含 `_public` 公开子路由）/settings/panel/marketplace/resources，并把 monitor 的 `global_router` 与 `monitor_threads` 挂到 `/api/monitor` 前缀下（app_factory.py:70-71）。所有 import 都写在函数体内（延迟导入），COMMUNICATION 形态下 threads/sandbox 等重模块根本不会被 import，冷启动成本随之砍掉。

**bootstrap/app_entrypoint.py（55 行）**的 `resolve_app_port`（app_entrypoint.py:20-35）实现端口解析链：先取 `LEON_BACKEND_PORT`，为空再取通用 `PORT`，两者任一存在即返回；否则 `git config --worktree --get worktree.ports.backend` 子进程查询（3 秒超时兜底）；最后落默认 8001。**注意：main.py:11 的 `@@@port-precedence` 注释写的是 "git worktree config > LEON_BACKEND_PORT > PORT > 8001"，与实码顺序相反——代码是环境变量优先于 worktree 配置。以源码为准：`LEON_BACKEND_PORT > PORT > worktree.ports.backend > 8001`**，这是注释与实现漂移的活标本。另外 `add_permissive_cors`（app_entrypoint.py:38-45）对全开放发环境的 `allow_origins=["*"]`。

**lifespan.py（214 行）**按 profile 走两条深浅不同的装配路径：
- 通用段：`attach_runtime_storage_state` 建存储容器（lifespan.py:53），五个 repo 挂上 `app.state`（user/thread/sandbox_runtime/workspace/sandbox，lifespan.py:57-61）；chat 运行时必须先于 threads 装配（lifespan.py:75-80，L72-74 的 `@@@web-chat-before-threads` 注明"调换顺序会在全新 dev 环境启动失败"——threads bootstrap 会急切构造 agent runtime gateway，依赖 chat 侧 typing 状态先就位）；auth 向 chat 借 `contact_repo` 而非重开存储（lifespan.py:84-89）。
- COMMUNICATION 早退段（lifespan.py:150-153）：挂上 threads_runtime_state 后直接 `yield; return`——不做 checkpoint、不启 reaper。
- FULL 段：`LEON_POSTGRES_URL` 是硬契约，缺失直接 RuntimeError，且启动时真连一次 Postgres 执行 `SELECT 1` 验活（lifespan.py:28-39，注释 L21-23 说得明白：web 路由会在首条消息时创建 LeonAgent，缺 checkpointer 配置是启动契约违例而不是迟到的请求期错误）；LangGraph checkpoint saver 在此建立并 `setup()`（lifespan.py:97-103）；threads_runtime 被 dataclass `replace` 补入 display_builder/event_loop/checkpoint_store（lifespan.py:158-173）。

## 外部连接

- 上游依赖：FastAPI（app+lifespan）、uvicorn（reload 运行器）、psycopg（启动验活）、storage.runtime 的 `build_supabase_client/build_storage_container`（bootstrap/storage.py 全文就是这三件套的 dataclass 包装）。
- 下游消费者：`backend/web/routers/*` 十余个路由模块读 `app.state` 上的 repo 与运行时；`backend/sandboxes/service.init_providers_and_managers` 被 lifespan 借走注入 reaper（lifespan.py:177）；`core/tools/lsp/service.lsp_pool` 在关停时统一关闭（lifespan.py:211-213）。
- 跨模块 monkey-patch：lifespan L11 `from backend.threads.pool import idle_reaper as idle_reaper_owner`，随后在 L182-185 把 `init_providers_and_managers` 与 `IDLE_REAPER_INTERVAL_SEC` 写进那个模块——这是下文要讲的"占位注入"机制的注入端。

## 数据流

启动一次 FULL 后端的完整时序：`ENV_FILE` dotenv → profile 解析 → `create_app` 按需 import 16 路由 → uvicorn 拉起 → lifespan startup：Postgres 契约校验 → 存储容器与 5 repo → chat 运行时（产出 contact_repo/typing_tracker/messaging_service 等）→ auth 借件 → FULL 分支建 checkpoint → threads 运行时注入 chat 各服务 → 五组通知接线（delivery/relationship 两段/join_request/workflow event，lifespan.py:112-147）→ **idle_reaper 注入与启动**：若 `configured_sandbox_db_path()` 非空，把真实的 `init_providers_and_managers` 写入 `backend.threads.pool.idle_reaper` 模块，否则写 None（reaper 只扫 `app.state.agent_pool`）；再把 `IDLE_REAPER_INTERVAL_SEC`（config.py:7 定义为 30 秒）覆盖进模块，最后 `asyncio.create_task(idle_reaper_loop(app))`（lifespan.py:187）。

`backend/threads/pool/idle_reaper.py` 是被注入方：模块级只有两个占位值——`IDLE_REAPER_INTERVAL_SEC = 0` 和 `init_providers_and_managers: Callable | None = None`（idle_reaper.py:5-6）。模块单独 import 时完全无害（interval 为 0、工厂为 None，`run_idle_reaper_once` 退化为只回收 agent_pool）；被 lifespan 注入后才成为完整形态——`run_idle_reaper_once` 对 `agent_pool` 先取 `list()` 快照再迭代（idle_reaper.py:15，L13-14 @@@ 注释：回收活 manager 会把兄弟 agent 挤出池，必须迭代稳定快照），随后对不在 pool 命中的 provider 补一轮 `enforce_idle_timeouts()`（idle_reaper.py:26-30）。

关停时序（lifespan.py:190-213）：取消并 await idle_reaper 任务 → 关 recipe_repo → `__aexit__` checkpoint saver 上下文 → 遍历 `agent_pool` 逐个 `agent.close(cleanup_sandbox=False)` → `lsp_pool.close_all()`。

## 设计决策（含批判）

1. **两档 profile 而非微服务拆分**：COMMUNICATION（4 路由）面向纯聊天/社交的轻部署，FULL（16 路由）是全功能工作台。用"同一工厂函数+延迟 import"换取部署形态切换，而不是拆两个服务——省掉了跨服务鉴权与运维成本，代价是 FULL 模式的路由 import 全部塞在一个函数里（app_factory.py:39-73），新增路由要记得同步两处清单，且没有测试保证两清单不漂移。
2. **占位+运行时注入破循环依赖**：idle_reaper 需要 sandboxes.service 的工厂，而 sandboxes.service（经 threads 链）间接依赖 pool 模块——直接 import 会成环。模块级占位 `= None` + lifespan 运行时覆写，是"晚绑定"的最小实现。批判：这让 `idle_reaper.py` 单看是"残缺品"，任何绕过 lifespan 的测试或脚本用它都会静默空转；interval 占位为 0 时 `idle_reaper_loop` 会退化成忙循环（`sleep(0)`），幸好它只在注入后被 create_task。
3. **启动期硬失败文化**：LEON_POSTGRES_URL 缺失、Postgres 连不上、profile 非法，全部在 startup 抛错拒启，而不是等到首请求才炸。这是"快失败"的正统做法；但 `SELECT 1` 验活只保证 psycopg 能连，不保证 langgraph checkpoint 表已 `setup()`——表结构问题仍会迟到。
4. **端口链的注释漂移**：@@@ 标记注释本应是钉死决策的资产（本仓大量使用），但 main.py:11 与 app_entrypoint.py:20-35 已经互相矛盾——读 @@@ 注释也要对着代码验。
5. **reload_dirs 白名单**是对 uvicorn StatReload 的实战优化，值得抄；但它只在 `__main__` 直启时生效，`uvicorn backend.web.main:app` 外部启动不带 reload 无此问题，而 `uvicorn --reload` 外部启动则会踩回全盘扫描的坑。

## 新人提示

- 改路由清单时先想清楚它属于哪个 profile：放进 `include_full_routes` 的模块绝不能被 COMMUNICATION 路径顶层 import，否则延迟装配的意义就没了。
- 调试启动失败：先看抛错发生在 lifespan 的哪一段——Postgres 契约（L46-47）、chat（L75）、threads（L104）三段各自的失败信息完全不同；fresh dev 环境启动炸多半是 chat/threads 顺序被改动（L72-74 注释即为此而立）。
- `app.state` 是这个后端事实上的服务定位器：想知道某路由用了什么服务，grep `app.state.` 比读路由文件更快。
- idle_reaper 行为不符合预期时，检查 lifespan.py:181 的 `configured_sandbox_db_path()` 分支——沙箱控制面数据库未配置时，非 pool 内的 provider 永远不会被回收，这是有意为之而非 bug。
- 端口被占用/连错实例时，按 `LEON_BACKEND_PORT > PORT > worktree.ports.backend > 8001` 的实际优先级排查（`git config --worktree --get worktree.ports.backend` 可确认第三层），别信 main.py:11 的注释顺序。
