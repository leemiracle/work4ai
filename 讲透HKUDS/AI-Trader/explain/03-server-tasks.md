# 03 · service/server/tasks.py — 14 个后台任务的注册表与「函数体延迟 import」大本营

## 1. 角色定位

tasks.py 是平台的**后台心脏**：1265 行、36 个函数，把「价格刷新、利润历史、polymarket 结算、挑战结算、团队任务三段、信号质量评分、实验指标快照、协作网络边、四条市场情报快照线」全部编排成统一的 asyncio 循环。全文件最核心的资产是文件尾的 `BACKGROUND_TASK_REGISTRY`（tasks.py:1226-1241）——14 个任务的字典注册表，API 进程与 worker 进程共享同一张表，靠环境变量决定谁跑、跑哪些。

它同时是全仓「函数体延迟 import」惯例最集中的展示场：模块顶部只有标准库（tasks.py:7-16），**零业务 import**——database、price_fetcher、market_intel、challenges、team_missions、signal_quality、experiment_metrics 全部在函数体内按需 import（如 tasks.py:1103 `from challenges import settle_due_challenges`）。这不是风格洁癖，而是解循环依赖的命脉：routes 层会 import tasks（main.py:45-49），tasks 又要调用 routes_shared 的 normalize_market，若都放模块顶就是环。

## 2. 内部结构

按职能分六块：

**环境工具与全局状态（tasks.py:19-60）**：三个 `_env_*` 小工具（bool/int/csv，全部容错默认值）让每个循环的节奏都可环境变量调参；模块级可变状态包括 trending_cache 列表、价格失败表 `_PRICE_FAILURES`、polymarket 结算游标 `_POLYMARKET_SETTLEMENT_CURSOR`（tasks.py:29）、threading.Lock（:28）。`_SUPPORTED_PRICE_MARKETS = {"crypto", "polymarket", "us-stock"}`（:23）三市场口径在此再次钉死。

**价格失败熔断器（tasks.py:63-127）**：每个 (symbol, market, token_id, outcome) 四元组一个状态，失败一次进入指数退避冷却——`cooldown = min(21600, 3600 × 2^min(count-1,6))`（:96），即 1 小时起步、封顶 6 小时；成功即清除（:112）。状态还经 sha1 键（:85-88）落 Redis，进程重启后冷却不丢（:66-79 懒恢复）。这是对外部行情 API 的体面保护：拉不到价的烂合约自动降频到 6 小时一次。

**利润历史分层保留（tasks.py:229-418）**：`_prune_profit_history_unlocked` 把 profit_history 表按分辨率分层清理——原始精度保 24 小时、15 分钟桶 7 天、小时桶 30 天、日桶 365 天（:243-249，全部可调），SQLite 清完还跑 `VACUUM` 回收空间（:415）。入口用非阻塞 `lock.acquire(blocking=False)` 防重入（:230-232），调度侧有同步（:421-433）与异步 create_task+to_thread（:445-465）两条触发路径。

**核心循环：update_position_prices（tasks.py:468-650）**：每轮先做 polymarket 元数据回填（:483），再从 positions 表聚合去重持仓，四道漏斗过滤候选——不支持的市场跳过（:521）、已有价且不在强制刷新名单跳过（:526，crypto/us-stock 默认每轮强刷、polymarket 只补空价 :476）、过期的 updown 合约过 900 秒宽限后跳过（:531-535，合约到期时刻就编码在 symbol 里，正则 `^(btc|eth|sol|xrp)-updown-(5m|15m|1h|4h)-(\d+)$` :27 直接解出）、熔断冷却中跳过（:538）。并发受 `MAX_PARALLEL_PRICE_FETCH` 信号量限制（默认仅 2，:474,:569），同步抓价函数包 `asyncio.to_thread`（:585-587）避免阻塞事件循环；全部结果在一笔短事务 executemany 写回（:623-627），顺手刷新 trending top20 缓存（:642）。默认 900 秒一轮（:648）。

**领域结算/评分循环（tasks.py:928-1223）**：八个高度同构的 `while True + try/except + sleep` 循环，模板统一为「启动延迟 → 循环调 `asyncio.to_thread(领域函数)` → 打点 → 睡环境变量间隔」。polymarket 结算最讲究：每轮最多处理 25 个合约（:989），超额时用全局游标轮转分页（:991-996），未解析合约 1 小时内不重查——把无限的链上合约宇宙切成有限批次。挑战/团队/信号质量等循环的间隔与启动延迟全部错峰：15/18/22/26/30/34/38 秒（:1105-1213），避免启动时雷群效应。

**注册表与启动（tasks.py:1226-1265）**：14 任务字典 → `DEFAULT_BACKGROUND_TASKS` CSV 串（:1244）→ `AI_TRADER_BACKGROUND_TASKS` 环境变量可裁剪（:1252-1255，未知名字静默丢弃）→ `start_background_tasks` 用 `asyncio.create_task(..., name=f"ai-trader:{name}")` 拉起（:1264）。API 进程的默认门禁在 :1247-1249（默认 False）。

## 3. 外部连接（对齐图谱边）

- **main.py**：startup 事件调 `_update_trending_cache` 预热+读两个开关函数——API 进程是注册表的第一个消费者。
- **worker.py**：import `DEFAULT_BACKGROUND_TASKS/_prune_profit_history/start_background_tasks`（worker.py:17）跑全量任务，Redis 锁+fcntl 文件锁保单例。
- **database.py**：所有循环的持久层；update_position_prices 只写 positions.current_price，profit history 只写 profit_history 表。
- **price_fetcher.py**：`get_price_from_market`/`_polymarket_resolve`/`price_fetch_logging`（:471,:585-587）；`_backfill_polymarket_position_metadata` 还借用其私有函数 `_polymarket_resolve_reference`（:144）——跨模块取私有名的先例。
- **market_intel.py**：四条快照线 refresh_* 函数（:655 等）。
- **领域模块**：challenges/team_missions/signal_quality/experiment_metrics 各供 1-2 个入口函数，全部由本文件调度——tasks.py 是「谁在什么时候被调」的唯一权威。
- **cache.py**：trending 缓存与失败冷却状态的持久化侧。

## 4. 数据流

以价格循环为代表：positions 表（聚合去重）→ 候选过滤（市场/已定价/过期/熔断四道闸）→ 并发外部抓价（信号量限流）→ 成功清熔断/失败记退避 → 单事务批量回写 positions.current_price → trending 缓存双写（内存列表+Redis）。利润历史则是反向流：agents+positions 联表算总权益（排除 leaderboard 排除名单 :791-796）→ 单条 CTE INSERT SELECT 批量落 profit_history（:773-827）→ 满一小时触发分层清理。结算流把 positions 行变成 agents.cash 增量+polymarket_settlements 台账+删仓三步原子操作。所有循环都是「拉模型」：没有消息队列，节奏完全由环境变量控制的轮询间隔决定。

## 5. 设计决策

- **同步领域函数+asyncio.to_thread 桥接**而非全 async 重写：领域模块（challenges 等）保持纯同步可单测，tasks 只负责调度壳——这是把「业务逻辑」与「并发策略」分层的干净做法，代价是每轮起线程的微小开销。
- **注册表模式而非装饰器注册**：一张显式字典让「系统里有哪些后台任务」一眼可见（:1226-1241），也天然成为 worker.py 与环境变量的公共契约。
- **失败熔断进 Redis**：冷却状态跨进程/重启存活（:66-79），API 进程和 worker 进程理论上还能共享同一份熔断状态。
- **利润钳制 ±1e12（:768）**：对荒谬盈亏值做数据卫生钳制（:816-819）——纸面交易平台上 bug 仓位的脏数据不至于污染整个排行榜。
- **错峰启动延迟**：3-38 秒手工错开的启动偏移，是零成本防雷群的朴素工程。
- **一处死代码**：`periodic_token_cleanup`（tasks.py:748-759）定义完整却**未注册进 registry，全仓零引用**——过期 token 清理目前实际不会自动运行（其消费的 utils.cleanup_expired_tokens 同样无人调用）。这佐证注册表才是「事实任务清单」，函数存在≠任务在跑。

## 6. 新人提示

1. 判断「某个后台行为多久跑一次/在哪跑」：先查 registry（:1226-1241）确认任务名，再 grep 对应环境变量默认值；改频率改环境变量，不改代码。
2. 新增后台任务三步：写 async 循环（抄 :1101-1116 模板）→ 注册进字典 → 不要忘了启动延迟错峰；切记函数体内 import 目标模块，放模块顶会直接 import 环。
3. 排查「价格一直不更新」：先看 `[Price Update]` 日志行的 skipped_cooldown/skipped_unsupported 计数（:553-566），八成是熔断退避或市场不在三市场白名单。
4. 单测领域逻辑不要从 tasks 入口进：直接测 challenges/team_missions 的同步函数，tasks 只是壳——反过来想本地验证某个循环，用 `AI_TRADER_BACKGROUND_TASKS=prices python worker.py` 单跑一个。
5. 读 trending 榜单数据时记住它的口径是「持仓人数 top20」（:194-200），不是交易量也不是涨幅——positions 表的派生统计。
