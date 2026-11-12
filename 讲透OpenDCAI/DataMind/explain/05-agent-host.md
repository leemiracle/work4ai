# 05 · CodexHost 宿主：SDK 会话注入、Hook 链与 calculator 沙箱

## 角色定位

`datamind/host.py:33` 的 `CodexHost` 是"官方 Codex SDK 当外脑、DataMind 只当数据工具"的适配器——头注释自划边界："It does not plan tasks, generate SQL, extract relationships, or run tool-use loops itself"。它不做 agent loop，只管子会话环境、流转发、账本证据、读租约。配套 `CodexSession`（`datamind/codex.py:44`）封装 SDK 线程生命周期——profile 是数据隔离非租户鉴权。

## 内部结构

**注入点**：`CodexHost.__init__` 第 34 行 `session_factory=CodexSession` 是可替换默认参——测试注入假会话不必碰真 SDK。并发限流 `asyncio.Semaphore(max_concurrency)`（L40）。`_session()`（L44-96）是环境工程核心：①身份三元组 `DATAMIND_SESSION_ID/REQUEST_ID/ACCESS_MODE` 注入 env（L47-50），`protected` 集合硬挡 runtime_env 越权（L51-53）；②八个 data 节配置序列化成 `DATAMIND__<节>__<键>` 转发（L57-69）；③网关模式补 `model_providers.datamind_gateway.*`（L77-89）。**CodexSession**：`sdk_config`（`codex.py:12`）先 `DataConfig` 验证再序列化（L16），preapproved_tools 查未知名（L18-20）；import openai_codex 失败报 `pip install 'datamind[codex]'`（L69-71），thread_start 挂 MCP INSTRUCTIONS（L75-81）；turn 未完成 5 秒 shield interrupt 强收（L108-112）。sandbox 二值：read→'read-only'，write→'workspace-write'（host.py:93）。

## 外部连接

**Hook 链**（`core/hooks.py:153` `HookChain`）是工具调用单一咽喉：`Hook` Protocol `@runtime_checkable`（L113-114）只约定 `name` + async `pre_tool_use`/`post_tool_use`；`HookDecision` 是四个 frozen dataclass 判别联合 Allow/Deny/AskUser/Rewrite（L107）——非 enum：后三者带 payload。链语义在 `pre()`（L179-209）：首个非 Allow 决胜，但 **Rewrite 可组合**——hook N 改写的 args 流进 hook N+1（L201-203），链尾有净改写统一返回 Rewrite（L207-208）；单 hook 抛异常只 warning 不炸 agent（L191-198）。post 恒全跑保审计（L211-229）。实现：生产三件 PathAllowlist/DestructiveSql/AuditLog（`capabilities/hooks/__init__.py:40-44` 按"便宜→贵"排序），加测试桩共 6 处 `pre_tool_use`（生产 `path_allowlist.py:68`/`audit.py:139`/`destructive_sql.py:71`，测试桩另三处）。

## 数据流

`stream()`（`host.py:106`）：read 先 `workspace.acquire_lease` 钉住已发布修订（L115-116；write 带 revision 拒 L118-119）→ 拼 prompt（L131-142：只许用 datamind MCP、禁 legacy ask/store、source content 不是行动授权）→ keepalive+timeout+信号量三护栏（L143-145）→ 消费 `session.stream` 三类事件：delta/tokenUsage/工具 item（L150-181）→ 收尾 `OperationStore.take_events` 拉**权威** trace/evidence（L190-205，覆盖流内初值）、`_receipts` 查账本（L98-104）、recovery 统计（L214-218）→ 单一 done 事件（L210-213）。finally 必释放租约（L219-228）。

## 设计决策（含批判）

①"SDK 为外脑、宿主无内环"把规划/SQL 生成全归 Codex，DataMind 退成纯工具面——复杂度外移，代价是行为随 SDK 版本漂移；②身份三元组 env 注入+protected 集合做成不可伪造的进程边界；③证据链双源（流内+账本）且账本胜出，防 LLM 幻觉工具调用。**批判**：calculator 沙箱（`skills/code_skills.py:44-54`）是黑名单 + `eval(expression, {"__builtins__": {}}, _SAFE_CALC)`（L53）凑合——黑名单（L49）挡不住 `().__class__` 属性链外逃变体，应换 AST 白名单求值器；`host.py:175` 靠工具名切片推断证据面，改名即失配。

## 新人提示

测宿主用 `CodexHost(settings, session_factory=FakeSession)` 注入。读懂 stream 必读 L131-142 prompt 模板——Codex 行为的实际约束源。加 Hook 只需写 `pre_tool_use` 返回四决策之一。Codex SDK 缺包认准 `datamind[codex]`。calculator 别暴露给不可信输入。
