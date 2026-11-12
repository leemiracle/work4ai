# 04 · 事件流核心：`events/` 三层继承链与 `core/schema` 事件宇宙

> 覆盖：`openhands/events/`（stream.py 291 行/event_store.py 183 行/event_store_abc.py 111 行/event.py 121 行/serialization 三件）+ `openhands/core/schema/`（三枚举）+ `openhands/core/setup.py`（304 行）
> 选题甄别：任务书路径 `openhands/core/eventstream/` 不存在——事件流实装在 `openhands/events/`，`core/schema/` 只放枚举契约。

## 1. 角色定位

事件流是 V0 架构的**中枢神经**：Agent 每步（Action）与环境/用户的回应（Observation）都是事件，追加写进 `EventStream`、持久化到 FileStore、广播给全部订阅者——控制器/运行时/记忆/UI 全挂在这条流上（01 篇 `/events` 端点、06 篇 Runtime 订阅都消费它）。`core/schema/` 三枚举是词汇表：ActionType 27 值、ObservationType 21 值、AgentState 12 态。`core/setup.py` 是**七工厂组装线**。三者都带 `# Tag: Legacy-V0`（`openhands/core/schema/action.py:1-7`、`openhands/core/setup.py:1-7`），但事件模型被 V1 跨代复用（01 篇直接 import EventStore/MessageAction）——**拆的是编排，留的是数据格式**。

## 2. 内部结构

**词汇表**：ActionType 27 值（`openhands/core/schema/action.py:11-109`）——会话族 MESSAGE/SYSTEM/START（`:12-20`）、文件族 READ/WRITE/EDIT（`:24-32`）、执行族 RUN/RUN_IPYTHON（`:36-40`）、浏览器族（`:44-48`）、MCP（`:52`，串值 `call_tool_mcp`）、协作族 DELEGATE/THINK/FINISH/REJECT（`:56-69`）、生命周期族 NULL/PAUSE/RESUME/STOP/CHANGE_AGENT_STATE（`:74-88`）、Git 族 PUSH/SEND_PR（`:90-93`）、记忆族 RECALL/CONDENSATION/CONDENSATION_REQUEST（`:96-102`）、管理族 TASK_TRACKING/LOOP_RECOVERY（`:105-108`）。ObservationType 21 值（`openhands/core/schema/observation.py:12-69`）：大体镜像另加 CHAT（`:32`）、ERROR/SUCCESS（`:42-44`）、USER_REJECTED（`:52`）、CONDENSE（`:54`）、DOWNLOAD（`:63`）、LOOP_DETECTION（`:69`）。AgentState 12 态（`openhands/core/schema/agent.py:11-56`）：LOADING→RUNNING→…→RATE_LIMITED，含确认三态（`:44-52`）。

**Event 基类**（`openhands/events/event.py:25-26`）不定义存储字段，全用 property+hasattr 探测 `_` 前缀属性：id（`:36-41`，缺省 `INVALID_ID=-1` `:27`）、timestamp（`:43-53`）、source（`:55-60`）、cause 因果链（`:62-67`）、timeout+`set_hard_timeout`（`:69-86`，设超时自动置 blocking）、可选 `llm_metrics`（`:89-98`）/`tool_call_metadata`（`:101-110`）/`response_id`（`:113-121`）。`EventSource` 三值（`:9-12`）。`:6` 依赖 `openhands.llm.metrics`——事件层反向依赖 LLM 层计费模型。

**双继承链**：`EventStoreABC`（`openhands/events/event_store_abc.py:11`）纯抽象 search/get/get_latest（`:17-25`、`:54-64`），保留三个 `@deprecated` 旧接口做转发兼容（`:38-52`、`:66-68`、`:70-111`）。`EventStore`（`openhands/events/event_store.py:43-44`）是 **FileStore 背板读侧**：字段含 `cache_size=25`（`:47-50`）；`cur_id` 懒计算（`:53-63`）——首访列目录找最大文件号+1（`:65-83`，`_get_id_from_filename` `:177-183`）；`search_events` 生成器（`:85-136`）做**反向遍历下标换算**（`:110-116`）与 **25 条/页缓存页加速**（`_CachePage.covers` `:25-30`、页未命中回退单读 `:126-130`、按 `index % cache_size` 对齐 `:172-175`）。`EventStream`（`openhands/events/stream.py:43`）加**写路径与订阅分发**：构造即起 daemon 线程（`:63-65`）；`EventStreamSubscriber` 七身份（`:23-30`）；`subscribe()` 为每回调建 **max_workers=1 专属线程池**（`:137`）+专属事件循环（`:71-76`），callback_id 重复即抛（`:142-145`）；`add_event()`（`:163-203`）是全仓最热写路径——拒绝已有 ID（`:164-167`，防 handler 回灌死循环）、锁内分配递增 ID（`:170-172`）、**写前脱敏**（`:178`）、页满换新页（`:183-184`）、超 1MB 告警（`:190-198`）、落 FileStore（`:199`）、整页缓存最后写（`:201-202`）、入队（`:203`）；`_process_queue` 以 0.1s 轮询（`:258`）按**订阅者字典序**分发（`:263`）到各线程池（`:272`）；`_replace_secrets` 递归替换 `<secret_hidden>`，顶层系统字段豁免（`:221-244`）。

**序列化三件**：`serialization/event.py` 定 wire format——`TOP_KEYS` 九键（`:16-26`）、`UNDERSCORE_KEYS` 六键（`:27-34`）；`event_from_dict`（`:52-91`）按 action/observation 键分派（`:54-57`）到 `ACTION_TYPE_TO_CLASS`（21 类注册 `serialization/action.py:31-55`）或 `OBSERVATION_TYPE_TO_CLASS`（19 类 `serialization/observation.py:36-61`），再水合 metrics（`:69-89`）；`event_to_dict`（`:100-152`）反向——`id=-1` 丢弃（`:108-109`）、Action 余量进 args（`:133`）、Observation 余量进 extras（`:143-146`）；另有轨迹裁剪集（`:36-49`）与中部截断器（`:167-178`）。

## 3. 外部连接

- **脆弱模块环**：`events/__init__.py` 依次 import event.py（`:1`）→stream.py（`:3`）；`stream.py:13` import serialization.event，后者 `:8` 又 `from openhands.events import Event`——**serialization↔events↔stream 三方成环**，靠 `__init__.py` 里 Event 先绑定侥幸成立；调换导入顺序即 ImportError。
- **上游**：`core/setup.py:24` 顶层 import，`create_runtime` 建流（`openhands/core/setup.py:70`）塞给 Runtime（`:81-89`）；01 篇 V0 路由裸构造 EventStore（`conversation.py:259-263`）；AgentController/Memory 分别以 AGENT_CONTROLLER/MEMORY 身份订阅（`setup.py:209-213`）。
- **存储底座**：`openhands/storage`（FileStore+路径约定 `event_store.py:11-15`）与 `openhands.io.json`（`stream.py:14`）。
- **LLM 层互依**：事件携带 llm_metrics（`event.py:6`）——events↔llm 是第二个环。`session_exists`（`stream.py:33-40`）是会话恢复探测公用入口。

## 4. 数据流

`run_controller`（`openhands/core/main.py:59`）驱动一次会话：`generate_sid` 造 ≤32 字符 ID（`main.py:105`→`setup.py:279-303`，K8s 63 字符限注释 `:282-284`）→`create_registry_and_conversation_stats`（`main.py:107-111`）→`create_agent`（`:113`→`setup.py:233-240`，`Agent.get_cls` 查注册表——01 篇 agenthub 注册在此兑现）→`get_provider_tokens`（`main.py:119`→`setup.py:99-147`，四平台 token 环境变量逐个收集）→`create_runtime`（`main.py:120-127`→`setup.py:42-96`：建流 `:70`→`get_runtime_cls` `:79`→注入 plugins/LLMRegistry `:81-89`）→`runtime.connect`（`main.py:129`）→选仓时 `initialize_repository_for_runtime`（`main.py:133-137`→`setup.py:150-185`：clone→setup script→git hooks）→`create_memory`（`main.py:143-151`，装载 repo microagents `setup.py:222-225`）→可选 `add_mcp_tools_to_agent`（`main.py:154-164`）→`create_controller`（`setup.py:243-276`：先 `State.restore_from_session` `:257-259` 再组装 AgentController `:263-275`）。运行期每事件走 `add_event`：赋 ID→脱敏→序列化→落盘→入队→按序派发——观察与动作交替直到 FINISH/STOP。

## 5. 设计决策（V0→V1 代际语境）

- **事件溯源作为一等架构**：会话状态是事件日志而非表记录；`cur_id` 靠扫文件系统推算（`event_store.py:65-83`）换 FileStore 后端全可插拔（local/S3/GCS 同路径），代价是冷启动一次目录列举；缓存页是对"逐事件读慢"的事后补强（`:161-175` 注释直言）。
- **per-callback 单工作线程池**（`stream.py:137`）：订阅者内天然串行、彼此并行，免锁消解"controller 慢不能阻塞 memory"；`sorted(keys)`（`:263`）保证跨订阅者分发顺序确定。
- **add_event 防御性 ID 检查**（`:164-167`）：handler 回灌会死循环，这条 ValueError 的错误消息即架构文档——生产事故化石。
- **脱敏放写路径而非读路径**（`:178`）：秘密落盘即已替换；顶层豁免保系统字段可用。
- **deprecated 三件套留在 ABC**（`event_store_abc.py:38-111`）：旧调用方（resolver/评测脚本）大量存在，转发实现保兼容——V0 拆除期"接口先于实现死亡"。
- **V1 的扬弃**：EventService（02 篇）用注入器替换 FileStore 直连，但 `event_to_dict` wire format 未变——迁移成本压在编排层而非数据层。

## 6. 新人提示

- **坑：读历史用 `EventStore` 即可**（01 篇 `/events` 端点），零线程开销；`EventStream` 构造即起 daemon 线程（`stream.py:63-65`），请求处理器里误建流是线程泄漏源。
- **坑：分发顺序是字符串字典序**（`:263`）非枚举定义序——agent_controller<main<memory<openhands_resolver<runtime<server<test。
- **坑：`close()` 不等在途回调**（`:78-91`）：只 join 队列线程清订阅，已提交任务靠池 shutdown 兜底（`:124-126`），取消竞态（`:106-110`）可能吞掉最后一两个观察。
- **勘误：`cache_size=25` 硬编码默认**（`event_store.py:50`），EventStream 未暴露覆盖口。
- **序列化兼容层别乱动**：`handle_action_deprecated_args`（`serialization/action.py:58-97`）还在用 `ast.literal_eval` 解析 `translated_ipython_code` 时代的 `print(file_editor(**...))` 字符串（`:68-90`）——历史会话重放靠它，删即断旧轨迹。
- **`_make_error_handler` 的 re-raise**（`stream.py:288-289`）：实际抛在 future 上，调 `future.result()` 才可见；只 submit 不查 result 的路径异常仍被吞。
- **安全注意：脱敏是子串级替换**（`:242-243`）——secret 很短时正常文本也可能被误替换。
