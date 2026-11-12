# 07 · agentos_router：AgentOS 南向路由扩展——惰性 barrel、无中心降级与 single-flight 沙箱生命周期

> 所属仓库：openJiuwen-ai/agent-gateway（进程名 agent-gateway）。本篇是外围与跨系统线第一篇，覆盖 `agent_gateway/extensions/agentos/agentos_router/` 全部 11 个文件（约 6700 行）。核心链路（app_gateway/message_handler/routing）见 01/02/04 篇。

## ① 角色定位

agentos_router 是 Gateway 的**南向路由扩展包**：当 `config.yaml` 里 `gateway.agent_client.type` 配成 `agentos_router` 时（判定函数在 `agent_gateway/extensions/agentos/agentos_router/config.py:113` 的 `agentos_router_selected`），扩展系统会实例化本包，把 Gateway 依赖的两个抽象接口——`AgentServerClient`（聊天请求的南向出口）与 `ThirdAgent`（第三方 agent 的 list/switch 能力）——落到"**YuanRong 沙箱 + Registry 注册表 + 本机 AgentManager**"三件套上。

它在整个扩展体系里的挂载点是 `agent_gateway/extensions/agentos/agentos_router/extension.py:28` 的 `class AgentOSRouter(AgentServerClientExtension, ThirdAgentExtension)`：一个类同时实现两个扩展槽位，`register_extensions`（`agent_gateway/extensions/agentos/agentos_router/extension.py:124`）把它同时注册进 `register_agent_server_client` 与 `register_third_agent` 两个注册表。换言之，这是"一个扩展顶两个身份"的组合式设计——扩展本体只做组装，真正干活的是它拼起来的五个组件：YuanRong 前端客户端、RegistryClient、AgentManager、SSH relay、AgentOSRouterClient。

## ② 内部结构

**包级惰性 barrel（解循环导入的关键）。** `agent_gateway/extensions/agentos/agentos_router/__init__.py:18` 定义 `_EXPORTS` 字典（名字 → 定义它的子模块），`agent_gateway/extensions/agentos/agentos_router/__init__.py:53` 的模块级 `__getattr__`（PEP 562）按需 `import_module` 再取属性并缓存进 `globals()`。文件头注释（`__init__.py:3-10`）把动机写得非常直白：导入 `agentos_router.agent_manager` 这类轻量子模块时**不能**拉起 `extension` → `router_client`，否则包初始化就会依赖 `gateway.channel_manager`，形成 "channel_manager ←→ agentos_router" 循环导入。这是本仓反巨型文件宪法的典型落地——消费方只想用 `models`/`AgentManager` 时，路由与传输组件完全不被加载。

按职责分四层：

- **数据模型层**：`models.py` 只有两个 dataclass。`AgentStatus`（`agent_gateway/extensions/agentos/agentos_router/models.py:12`）是四态枚举 `creating / ready / failed / deleted`；`AgentInfo` 携带 user_id、agent_type、sandbox_id、public_key 与 metadata。
- **内存生命周期层**：`agent_manager.py`（625 行）的 `AgentManager` 是进程内 Agent 运行时存储 + single-flight 创建器（下文⑤详述）。
- **注册表层**：`registry_client.py`（881 行）的 `RegistryClient` 是 AgentOS 注册中心 HTTP API 的 SDK 封装（httpx 长连接）。
- **路由转发层**：`router_client.py`（3517 行，全包最大文件）的 `AgentOSRouterClient`（`agent_gateway/extensions/agentos/agentos_router/router_client.py:522`）实现完整的 `AgentServerClient` 协议：`send_request`/`send_request_stream` 转发、容器文件四操作（upload/download/list/mkdir）、`resolve_web_endpoint`、SSH relay、鉴权、idle reaper、断连清理、连接预热、启动清扫。

辅助件：`config.py`（468 行）把 `gateway.agent_client` + `gateway.agentos` 两段 YAML 加 20 余个环境变量种子折叠成 frozen `RouterConfig`；`ssh_relay.py` 提供 SSH 南向中继；`agentos_authenticator.py` 是 Web/TUI 握手鉴权客户端；`logutil.py` 统一 `sandbox.*` 结构化日志前缀；`third_agent.py` 的 `AgentOSThirdAgent`（`agent_gateway/extensions/agentos/agentos_router/third_agent.py:16`）是 ThirdAgent 槽位的薄壳，直接把 `thirdagent_list/switch` 转发给 router client。

## ③ 外部连接

- **YuanRong 前端**：`extension.py:33` 构造 `YuanrongFrontendAgentClient`（来自 `agent_gateway/extensions/yuanrong_frontend_client.py`，2020 行共享客户端，08 篇详述），负责沙箱 create/get_info/delete 与 WS 代理。
- **Registry HTTP API**：`GET/POST/PATCH/DELETE api/images|api/instances` 四族端点（`registry_client.py:361/389/438/469/510/558`），httpx keep-alive 池限 `max_keepalive_connections=4 / max_connections=8`（`registry_client.py:837-841`）。
- **ChannelManager**：`router_client.py:603` 的 `set_channel_manager` 做两件事——给 Web 与 CLI(TUI) 通道挂 `authenticate_http` 握手鉴权、订阅通道断连事件驱动延迟清理。
- **extensions 注册表**：`AgentOSRouter` 经 `register_extensions` 装载；`extensions/loader.py` 的通用扩展发现机制见 12 篇。
- **E2A 协议**：转发面全程以 `openjiuwen_protocol.e2a.models.E2AEnvelope` 为载体，`AgentRuntime.attach_to_envelope`（`agent_manager.py:138`）把 agent_id/agent_type/sandbox_id 写进 `channel_context` 供下游追踪。

## ④ 数据流

以一条聊天请求走 `send_request`（`router_client.py:1853`）为例：

1. **旁路识别**：先判 `_is_ssh_relay_request`（SSH 接入走独立 relay 通道），再 `_inject_external_cli_agents` 注入外部 CLI agent 清单。
2. **cancel 特例**：`chat.interrupt` 不得冷启动沙箱——没有 READY 实例就返回 no-op 成功，避免与断连清理竞态重建孤儿沙箱（`router_client.py:1867-1877` 注释钉版）。
3. **解析或创建**：`_resolve_agent(acquire=True)` → `AgentManager.get_or_create_agent`（`agent_manager.py:330`）。`acquire=True` 在锁内原子递增 `task_count`，保证 idle reaper 不可能在"解析完成"与"实际使用"之间回收沙箱；调用方必须在 finally 里 `release`。
4. **WS 直连**：create 成功后不走 YuanRong invoke 链路，而是 `_get_ws_client` 经 frontend 的 WS 代理直连 instance（`router_client.py:592` 的 `_ws_clients` 缓存 + `:595` 的 `_ws_connecting` Future 合并并发首连）。
5. **三类失败分流**：实例"确认不存在"（`YuanrongAgentApiError`）走删除重建并打独立日志；网络错误 token 命中（`_is_agent_network_error`）走 `_cleanup_agent_on_network_failure`；其余异常直接抛。三条路都产出 `_routing_error_response` 而非让 Gateway 崩溃。

创建侧的数据流同样关键：owner 请求调 `creator`（即 `_create_agent`，`router_client.py:2797`）真正向 YuanRong 建沙箱，成功后 `AgentRuntime.apply_creator_result`（`agent_manager.py:145`）强制以本地 base 的 agent_id/user_id/agent_type 为准覆盖返回值——**远端信息永远不能改写本地身份**——然后 `mark_ready` 并 `creating_event.set()` 唤醒所有等待者。

## ⑤ 设计决策与权衡

**决策一：RegistryClient 无中心可启动（local stub 降级）。** `registry_client.py:8-9` 文件头写明契约：`RegistryConfig.endpoint` 为空时 client 进入 local-only 模式，AgentOS 无 registry 进程也能启动。每个 HTTP 方法都有对应的桩分支：`get_launch_spec` 返回 `raw={"source": "local_stub"}` 的空 spec（`registry_client.py:367-372`）、`list_images` 只报 `_LOCAL_STUB_FRAMEWORKS` 里的内置框架（`:390-407`）、`register_instance` 直接回一条 `status="运行"` 的假记录（`:456`）。这让单机部署/测试环境零外部依赖，代价是注册表功能（跨节点发现、心跳）静默缺失——用 `enabled` property（`:343`）显式暴露给上层判断。

**决策二：single-flight 创建 + 失败语义三分。** `get_or_create_agent` 的锁内逻辑（`agent_manager.py:363-395`）：无 runtime → 自己当 owner 去创建；有且 READY → 直接快照；有但 CREATING → 等待者等 `creating_event`（默认 60s 超时抛 `AgentCreatingTimeout`）；有但 FAILED → **抛 `AgentCreateFailed` 且禁止自动重试**（`:387-393`）。注释把理由说透了：取消/失败的一次创建可能已经建了一半 YuanRong 沙箱，重试会双开沙箱。与之对照，`AgentPreCreateError`（`:97`）标记"YuanRong create 之前就失败"（如 workspace 校验），`_discard_precreate_failure`（`:558`）直接丢弃 runtime 唤醒等待者重试——**失败位置决定失败语义**，这是整个包最值得学的分支设计。

**决策三：中文语义常量直入代码。** `registry_client.py:33-35`：`KIND_THIRD_PARTY = "三方"`、`KIND_JIUWEN = "九问"`，`resolve_instance_kind`（`:256`）按 framework 名（`jiuwenswarm`/`jiuwen-report` 前缀）映射。registry 的 kind 字段本身是中文值，SDK 层如实建模而非硬翻成英文枚举再翻译回来——跨系统契约以服务端数据形态为准。

**决策四：确定性 service_id + CAS 注销。** `instance_service_id`（`registry_client.py:248`）用 `sha256(user\0framework)[:8]` 生成 `generic_xxxxxxxx`，使"(user, framework) 唯一实例"天然幂等；`unregister_instance` 带 `expected_instance_id` 时走 `DELETE WHERE service_id=? AND instance_id=?` 的 CAS（`:558-565`），并发 upsert 换掉的行不会被旧 owner 误删——匹配的是**实例身份而非时间窗**。

**决策五：idle 时钟的持有计数。** `AgentRuntime.task_count`（`agent_manager.py:111`）在整个 chat/流/SSH relay/web proxy 生命周期内 +1，`pop_if_idle`（`:485`）要求 `task_count==0` 且 `last_active_at` 超时才允许回收——引用计数式防抢占，而非纯时间判断。

## ⑥ 新人提示与坑

1. **改 barrel 要同时改 `_EXPORTS` 与 `__all__`**：`__all__ = sorted(_EXPORTS)`（`__init__.py:50`）自动派生，但新导出忘登 `_EXPORTS` 时 `__getattr__` 会抛 AttributeError——不是静默，好事；反之从这里 import 一个不存在的名字，报错点在运行时而非 import 期。
2. **`AgentCreateFailed` 是钉死态**：一旦某 (user, agent_type) 创建失败被缓存，后续请求全吃 `AGENT_CREATE_FAILED`，只有显式 `delete_agent`（`agent_manager.py:460`）或重启才能解除。排查"为什么这个 agent 永远建不起来"先查 FAILED 缓存，别盯着 YuanRong。
3. **agent_type 大小写双语义**：`normalize_agent_type`（`agent_manager.py:179-189`）对 builtin `jiuwenswarm` 大小写不敏感并统一小写，对 registry 框架名则 case-sensitive 原样保留——`Jiuwenswarm` 和 `MyAgent` 走完全不同的归一化路径，混用大小写切换第三方 agent 会得到"新 agent"。
4. **`wait=False` 不是不等待**：仍 single-flight，但非 owner 直接抛 `AgentCreating`（`retry_after_seconds=5`，`agent_manager.py:79-82`），调用方要自己按这个间隔重试。
5. **启动清扫只认 registry CAS**：`stale_cleanup.py` 文件头（`stale_cleanup.py:2-13`）钉版——重启后内存态清空但上一进程的沙箱和 registry 行还在，清扫时"同进程快照跳过"只是快速路径，兄弟 worker 的 upsert 不可见，所以注销必须走 instance_id CAS，不能无条件按 service_id 删。
6. **`set_channel_manager` 是握手鉴权入口**：Web/TUI 通道的 HTTP 鉴权不是全局中间件，而是本包注入的 `authenticate_http`（`router_client.py:603-614`）；`auth_enabled=False` 时 `extension.py:74` 传 `None`。调鉴权问题别去 channel_manager 找，源头在这。

**关联阅读**：YuanRong 共享客户端与 adx 深度适配见 08 篇；etcd 管理面如何热更 `apply_remote_overrides`（`router_client.py:2545`）见 10 篇；扩展装载与 types shim 见 12 篇。
