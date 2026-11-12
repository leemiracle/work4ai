# 01 · service/server/main.py — 101 行薄入口：FastAPI 组装与双进程分叉点

## 1. 角色定位

main.py 是整个后端的进程入口，但它是刻意的「薄入口」：全文件仅 101 行，真正的业务能力一件都不在这里实现。它只做四件事——配日志、初始化数据库、调用 `create_app()` 工厂组装路由、在 startup 事件里决定「API 进程内嵌后台任务」还是「提示去跑独立 worker」。这个分叉点正是 2026-04-10 生产稳定化的核心决策落地点：HTTP 请求处理与价格刷新/利润历史压缩/market-intel 快照等重活分进程部署，避免事件循环互相竞争。

需要先钉版一个事实勘误：`service/README.md:7` 把 main.py 描述为 "Full FastAPI backend implementation"（完整 FastAPI 后端实现），这是虚标——真实实现散布在 routes.py 的工厂与 13 个 routes_* 模块、services.py、tasks.py 等处，main.py 只是总装线末端的一颗螺丝。新人若按 README 期待在 main.py 里找路由表，会扑空。

文件头部 docstring（main.py:1-12）自带一张六文件结构图（config/database/utils/tasks/services/routes/main），是理解「同目录平铺、无包结构」风格的最短入口。

## 2. 内部结构

文件按执行顺序分五段：

**日志装配（main.py:21-39）**：在一切 import 业务模块之前先 `os.makedirs` 出 `logs/` 目录，用 `RotatingFileHandler` 落 `server.log`，10MB 轮转保留 5 份（main.py:28-32）。日志先于业务 import 配置，保证业务模块初始化期的输出不丢。`API_STDERR_LOG` 环境变量（main.py:36）可选把日志镜像到 stderr，方便容器化部署 `docker logs` 直读——默认关，生产靠文件轮转。

**业务 import（main.py:41-49）**：五组依赖各来自一层——`get_cache_status`（cache）、`init_database/get_database_status`（database）、`create_app`（routes）、`api_access_log_enabled`（routes_shared）、三个任务函数（tasks）。注意这些是裸模块名 import（`from cache import ...` 而非 `from server.cache import ...`），这是全仓「同目录平铺」约定，IDE 跳转要求 cwd 在 service/server。

**访问日志静音（main.py:51-53）**：当 `api_access_log_enabled()` 为假（`API_ACCESS_LOG` 默认 false，routes_shared.py:134-135）时，直接 disable 掉 uvicorn.access logger——高频交易轮询下 access log 会淹没轮转文件，默认只留业务 INFO。

**模块级组装（main.py:56-59）**：`init_database()` 与 `app = create_app()` 都在模块顶层执行而非 startup 事件里。这意味着哪怕只 `import main`（如测试收集），建库也会发生；uvicorn 的工厂模式 (`--factory`) 这里没用，`app` 是模块级单例。

**startup 事件与运行（main.py:64-101）**：startup_event 依次打日志确认 database/cache 状态（main.py:67-82），随后同步调用 `_update_trending_cache()`（main.py:85，定义在 tasks.py:186）预热趋势缓存——让首个用户请求不必等冷缓存；然后走关键分叉：`background_tasks_enabled_for_api()` 为假时只打一行提示 "Run `python service/server/worker.py` ..."（main.py:87-90）就 return，为真才 `start_background_tasks(logger)`（main.py:93）。开关读 `AI_TRADER_API_BACKGROUND_TASKS` 环境变量，默认 False（tasks.py:1247-1250）——即默认部署形态就是 API+worker 双进程。`__main__` 直跑时 uvicorn 绑 `0.0.0.0:8000`（main.py:99-101）。

## 3. 外部连接（对齐图谱边）

- **routes.py**（main.py:43）：`create_app()`（routes.py:26）内部按 market→agent→signals→trading→experiments→research→challenges→team_missions→users→misc 顺序注册十个路由族（routes.py:45-54），外加计时中间件——main.py 拿到的 app 是完整平台。
- **database.py**（main.py:42）：`init_database()` 是约 1293 行的巨型建表迁移函数入口；startup 里 `get_database_status()` 汇报 backend 是 PostgreSQL 还是 SQLite（DATABASE_URL 决定）。
- **tasks.py**（main.py:45-49）：消费 `_update_trending_cache`（预热）、`background_tasks_enabled_for_api`（分叉开关）、`start_background_tasks`（内嵌启动路径）。
- **cache.py**（main.py:41）：startup 只读 `get_cache_status()` 打日志——Redis 是优雅降级件，挂了不影响启动。
- **worker.py**（间接）：main.py:88 的提示语是它与 worker 进程的唯一耦合点；worker.py 反向 import tasks 的 `start_background_tasks/DEFAULT_BACKGROUND_TASKS/_prune_profit_history`（worker.py:17），双进程共享同一任务注册表。
- **routes_shared.py**（main.py:44）：`api_access_log_enabled` 决定 uvicorn access log 生死。

## 4. 数据流

进程冷启动的数据流是单向漏斗：环境变量 → 日志/开关装配 → DDL 建库（database.py）→ 路由树组装（routes.py）→ uvicorn 拉起 → startup 事件（状态确认 → trending 预热 → 任务分叉）。运行期 main.py 本身几乎不再出现在数据流里——HTTP 流量走 routes 树，后台循环走 tasks 注册表，main.py 只贡献了「进程里有哪些 asyncio 任务」这一次性决定。

值得注意的一条隐藏数据流：`_update_trending_cache()` 是同步调用且发生在 startup 事件（async 上下文）里，若首次抓取外部行情慢，会短暂阻塞事件循环——这是「预热收益 vs 启动延迟」的小取舍，102 行的篇幅装不下完美主义。

## 5. 设计决策

- **薄入口+工厂组装**：main.py 只做装配不做业务，`create_app()` 工厂让「应用定义」与「进程入口」解耦，测试可以直接 `from routes import create_app` 起隔离实例而不触发 main.py 的日志/建库副作用（虽然模块级 init_database 略破坏了这点）。
- **默认双进程**：API 进程默认不带后台任务（tasks.py:1249 默认 False），提示语而非自动拉起——运维上「提示去跑」比「偷偷 fork」可预测得多。worker.py 侧用 Redis 分布式锁+fcntl 文件锁双保险保单例，锁续租失败直接 `os._exit(1)` 自杀（worker.py:27-35, 38-51）——宁可全停也不双跑结算。
- **日志默认静音 access**：轮询型 agent 平台 QPS 高、单条信息低，关 access log 换轮转文件寿命。
- **startup 事件用已弃用的 `@app.on_event`**（main.py:64）而非 lifespan 上下文——FastAPI 新旧 API 过渡期的实用主义选择，对一个 2026 年活跃迭代的项目而言属已知技术债。

## 6. 新人提示

1. 找 API 不看 main.py：端点全在 routes_* 模块，OpenAPI 文档由 `create_app()` 自动生成；文档代差问题（SKILL.md/YAML 滞后）下，`create_app` 注册顺序（routes.py:45-54）就是路由族的权威地图。
2. 本地起步最小路径：不配 Redis、不配 PG（回落 SQLite）、不开任何开关，`python main.py` 即可起一个「无后台任务」的纯 API 实例；要让价格动起来须另起 worker。
3. 排查「为什么价格不更新/结算不跑」时，第一反应查是不是只起了 API 进程——main.py:87-90 那行日志就是设计者留给你的路标。
4. 改日志格式/级别在 main.py:24-34，但别把 `API_STDERR_LOG` 与 `API_ACCESS_LOG` 混淆：前者是业务日志镜像到 stderr，后者是 uvicorn 访问日志开关，语义相反方向（一个默认关可选开，一个默认关开了才响）。
5. 阅读顺序建议：main.py → routes.py 的 create_app → 任一 routes_* 模块，这条线走通后整个服务端的「平铺宇宙」就不再迷路。
