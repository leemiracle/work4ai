# 09 · Channels 通道：把 agent 接进飞书/Slack/Telegram 的桥

## 角色定位

`backend/app/channels/`（9 文件 2384 行）是 DeerFlow 的 IM 接入层：外部消息平台 ↔ DeerFlow agent 的双向桥。它的独特之处在于**不自己实现任何 agent 逻辑**，而是作为 langgraph-sdk 的普通客户端经 HTTP 与 LangGraph Server 对话——与前端完全同构。这意味着线程（thread）的创建、持久化、状态管理全部收敛在 Server 侧，渠道层只做协议翻译与投递。

`__init__.py` 是纯 re-export barrel，`__all__` 固定四个符号：Channel/InboundMessage/MessageBus/OutboundMessage（`__init__.py:6-16`）。组装点在 `service.py`：`ChannelService` 读 config.yaml 的 `channels` 节、实例化启用渠道、拉起分发器，单例由 `start_channel_service()`（`service.py:163-170`）创建——它正是 gateway lifespan 里那次延迟导入的目标（08 篇 `app.py:53`）。

## 内部结构

五层积木，依赖方向单向向内：

- **message_bus.py（173 行）**：最底层，纯 stdlib（asyncio/dataclasses/StrEnum），零仓内依赖。`InboundMessage`/`OutboundMessage` 两个 dataclass 加一个 `MessageBus` 异步发布订阅枢纽（`message_bus.py:117`）；`created_at` 用 `field(default_factory=time.time)` 取时间戳（`message_bus.py:58`）。消息类型枚举走 StrEnum（`message_bus.py:22`）。
- **base.py（108 行）**：`Channel(ABC)` 契约（`base.py:14`），三个 @abstractmethod——start/stop/send（`base.py:36-52`）；`send_file` 默认返回 False 表示"本渠道不支持文件上传"（`base.py:54-60`）。共享投递语义收在 `_on_outbound`（`base.py:87`）：先发文本，**文本失败即 return 跳过全部附件**（`base.py:100`），避免出现"文件到了却没有 accompanying 文本"的半投递。
- **store.py（153 行）**：JSON 文件持久化 `channel:chat[:topic] → thread_id` 映射。默认路径由 `deerflow.config.paths.get_paths()` 推导到 `base_dir/channels/store.json`（`store.py:38-40`，__init__ 内延迟导入）；写入走 NamedTemporaryFile + `Path.replace` 原子替换（`store.py:57-66`），防止写一半崩溃损坏映射表。
- **service.py / manager.py**：生命周期与分发（下详）。
- **三个平台实现**：feishu.py（510 行最大）/slack.py（244）/telegram.py（299）。

懒加载注册表是 service 的核心：`_CHANNEL_REGISTRY` 只存 import 字符串（`service.py:15-19`，三条 `app.channels.feishu:FeishuChannel` 形态的路径），实例化时才 `from deerflow.reflection import resolve_class` 反射装载（`service.py:119-121`）。slack_sdk/telegram 这类重依赖因此完全不进模块顶层——没配置 IM 的部署连这些包都不需要装。

## 外部连接

**对 harness 的三条跨层细线。** ① `from_app_config` 借 AppConfig 的 `extra="allow"` 从 `model_extra` 里捞 channels 配置（`service.py:52-59`）——config 包没有 channels_config.py，渠道节是"编外"字段；② manager/store 在函数体内延迟 `from deerflow.config.paths import get_paths`（`manager.py:245`、`store.py:38`），这批跨层延迟导入曾造成 scanner 对 channels 层的系统性漏报（图谱批阶段全部依赖边靠源码重扫补齐）；③ gateway 经 `GET /api/channels/` 与 `POST /{name}/restart` 触达单例（08 篇）。

**对 LangGraph Server：langgraph_sdk 双消费模式。** manager 惰性持有一个 async client（`manager.py:339` 注释 "lazy init"，`manager.py:379` 的 `from langgraph_sdk import get_client`）。Slack/Telegram 走 `runs.wait()`（`manager.py:496`）一次性等最终态；飞书走 `runs.stream(stream_mode=["messages-tuple", "values"])`（`manager.py:554-560`）增量取流。结果解析是纯鸭子类型链：`_extract_response_text` 用 isinstance 分支兼容 state dict/AIMessageChunk/tuple/kwargs dict 多种载荷形态（`manager.py:42-95`），artifacts 则从消息里筛 `present_files` 工具调用提取路径（`manager.py:214`）。

**辅助命令走 Gateway。** `/new`、`/models`、`/memory` 等命令（`manager.py:633` 起）不进 LangGraph，而是 manager 直接 `import httpx` 起 AsyncClient 打 Gateway 的 REST API（`manager.py:674-677`）——渠道进程同时是两个后端进程的客户端。

## 数据流

一条飞书消息的完整生命周期：

1. lark WebSocket 事件在**独立线程**的事件循环里到达（`feishu.py:110` 的 `threading.Thread`）——WebSocket 长连接模式让部署无需公网 IP（`feishu.py:1`）。
2. 线程侧经 `asyncio.run_coroutine_threadsafe` 桥回主事件循环，包装成 InboundMessage 发布到 bus。
3. `_dispatch_loop`（`manager.py:409`，start 时 `create_task` 常驻 `manager.py:392`）消费队列；`_handle_message`（`manager.py:438`）按消息类型路由。
4. CHAT 类型查 store 找既有 thread_id，查不到则 `client.threads.create()`（`manager.py:457`）并落映射。
5. 流式路径上，飞书先发一张"运行中"卡片，随后对**同一张卡**反复 patch——卡片 JSON 带 `"update_multi": True`（`feishu.py:276`）是飞书 patch API 的硬性要求；每次 outbound 更新 `is_final=False`，最终 `is_final=True`。
6. 出站投递回 `_on_outbound`（`base.py:87`）：文本成功才逐个上传附件。

## 设计决策

**① 安全闸门：outputs 前缀白名单防 IM 外泄。** `_resolve_attachments`（`manager.py:235`）是渠道层最重要的防御：agent 产出的 artifact 虚拟路径**只有以 `/mnt/user-data/outputs/` 开头才允许作为 IM 附件**（前缀常量 `manager.py:232`，检查 `manager.py:252-254`），否则 warning 拒绝；即便前缀通过，还要 `resolve().relative_to(outputs_dir)` 防 path-traversal（`manager.py:260-263`）、`is_file()` 防幽灵路径（`manager.py:264`）。docstring 写明动机：**防止 uploads 或 workspace 文件经 IM 渠道外泄**（`manager.py:238-240`）——agent 内部可见整个 thread 目录（含用户上传的原始文件），但 IM 出口只放行"明确 present 给用户的产物"。这是"能力面（agent 视角）≠ 暴露面（IM 视角）"的刻意不对称。

**② 三平台两种线程模型，桥接模式统一。** 飞书 lark WebSocket 与 Slack SocketMode 的监听器都跑在 SDK 自带的 executor 线程里，回主循环一律 `run_coroutine_threadsafe`；Telegram 是 python-telegram-bot v20+ 异步 API 在独立线程事件循环分阶段 run_until_complete。平台 SDK 差异被挡在 Channel 子类内部，manager 完全无感。

**③ resolve_class 而非直接 import。** 注册表反射（`service.py:121`，注意 `base_class=None` 未启用继承校验）让新增渠道零改动 service——加一条注册表字符串即可。代价是 typo 只在运行时暴露（与 config 系统同款权衡）。

**④ 附件投递的"全有或先文本"序。** 文本失败跳过附件（`base.py:100`）、单附件失败不阻断其余（`base.py:102-108`）——两级粒度的容错序，最小化半投递状态。

## 新人提示

- 新渠道接入清单：实现 Channel 三方法 → 注册表加一行（`service.py:15`）→ config.yaml channels 节加配置。**不要**在 manager 里加平台 if-else——那会破坏分发器的平台无关性。
- 调"消息没回复"先看 `_dispatch_loop` 日志里的 `invoking runs.wait/stream` 行（`manager.py:494`/`manager.py:543`）：有这行说明入站链路通，问题在 LangGraph 侧；没有则查渠道 start 与 bus 订阅。
- thread 映射坏了直接删 `store.json`（原子写保证剩余内容完整），下条消息会自动重建 thread——代价是丢上下文，不是丢功能。
- 飞书卡片不更新先查 `update_multi`（`feishu.py:276`）：这个字段是飞书 patch 协议要求，漏掉时 patch 静默失败。
- 附件不上传查三类 warning：`rejected non-outputs artifact path`（前缀闸门）、`escapes outputs dir`（穿越防护）、`not found on disk`（虚拟/物理路径映射断裂）——分别对应 `_resolve_attachments` 的三道检查，日志原文可直接定位。
