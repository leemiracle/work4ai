# 01 · V0/V1 双栈并存：`server/app.py` 与 `server/routes/conversation.py`

> 覆盖：`openhands/server/app.py`（104 行）、`openhands/server/routes/conversation.py`（449 行）

## 1. 角色定位

这两个文件是 Legacy-V0→V1 大重构代际的**第一入口与双栈物证核心**。`openhands/server/app.py` 是 V0 老服务器进程组合根：构造 FastAPI、挂全部 V0 路由，又把 V1 路由与 lifespan **嫁接进同一进程**。`openhands/server/routes/conversation.py` 是单会话级**双栈分派器**：同一 `/api/conversations/{conversation_id}` 前缀下按会话 ID 形态运行时判代，走完全不同的代码路径。

两文件头注相同（`openhands/server/app.py:1-8`、`openhands/server/routes/conversation.py:1-8`）："LEGACY V0 CODE - Deprecated since version 1.0.0, scheduled for removal April 1, 2026"，指明 V1 去处——agentic core 在 Software Agent SDK 独立仓（`openhands/server/app.py:3-4`），V1 应用服务器在本仓 `openhands/app_server/`（`:5`）。`# Tag: Legacy-V0`（`:7`）是全仓 V0 统一标记，grep 可枚举待拆除面。

## 2. 内部结构

**app.py（104 行）**：副作用导入 `import openhands.agenthub`（`openhands/server/app.py:25`，注册全部内置 Agent）；V1 嫁接导入 `v1_router` 与 `get_app_lifespan_service`（`:26-27`）；MCP 子应用 `http_app(path='/mcp', stateless_http=True)`（`:47`）；`combine_lifespans` 用 AsyncExitStack 拼多个 lifespan（`:50-59`）；V0 唯一 lifespan 是 `async with conversation_manager`（`:62-65`）；装配表起步 `[_lifespan, mcp_app.lifespan]`（`:68`），V1 lifespan 存在则追加（`:69-71`）——**V1 以可选插件挂在 V0 骨架上**；FastAPI 构造注入组合 lifespan 与 `/mcp` Mount（`:74-80`）；`AuthenticationError` 全局兜底 401（`:83-88`）。

挂载块两个条件分支是精华：`app_mode == AppMode.OPENHANDS` 才挂 git 路由（`:99-100`）；`enable_v1` 才挂 v1_router（`:101-102`）。`enable_v1 = os.getenv('ENABLE_V1') != '0'`（`openhands/server/config/server_config.py:41`）——**默认开启**，双栈不是过渡态而是当前默认形态。

**conversation.py（449 行）**：路由器挂前缀叠 `get_dependencies()` 鉴权（`openhands/server/routes/conversation.py:34-36`）；模块级预绑定 `depends_app_conversation_service()`（`:39`）。判代内核三函数：①`_is_v1_conversation`（`:42-65`）——`uuid.UUID(conversation_id)`（`:55`），V1 会话 ID 是 UUID、V0 是旧格式；解析成功查 `get_app_conversation()`（`:56-58`）；非 UUID（`:60-62`）与**任何服务异常**（`:63-65`）都判 V0，判代失败保守回落老栈。②`_get_v1_conversation_config`（`:68-91`）——`runtime_id = sandbox_id`（`:89`）、`session_id = conversation_id`（`:90`）：V1 的"运行时"就是 sandbox。③`_get_v0_conversation_config`（`:94-112`）——从 `conversation.runtime` 用 hasattr 探测 `runtime_id`/`sid`（`:105-107`）。

七端点六标 `deprecated=True`：`/vscode-url`（`:150`）、`/web-hosts`（`:185`）、`GET /events`（`:218`）、`POST /events`（`:288`）、`/message`（`:308`）、`/microagents`（`:363`）；唯一例外 `/config`（`:115`）本身就是双栈端点。

## 3. 外部连接

- **下游 V1**：`v1_router`（`openhands/app_server/v1_router.py:13`）定义 `/api/v1` 前缀并收编 event/app_conversation/sandbox/sandbox_spec/user/webhook/web_client 七子路由（`:14-20`）；`get_app_lifespan_service` 来自 V1 DI 组合根 `openhands/app_server/config.py:389-391`（见 02 篇）。
- **V0 骨架**：`conversation_manager`/`server_config` 来自 `openhands.server.shared`（`openhands/server/app.py:43`）；鉴权 `get_dependencies()` 在 `openhands/server/dependencies.py:31`（同为 Legacy-V0，V1 鉴权已迁 app_server）。
- **跨代共享层**：`ServerConversation`（`openhands/server/routes/conversation.py:28`）属 V0，`AppConversationService`（`:15-17`）属 V1；`EventStore`/`event_to_dict`/`MessageAction`（`:20-23`）属 `openhands/events` 共享层——**V1 未重写事件模型直接复用**（04 篇）。
- `/config` V0 分支 `attach_to_conversation`（`:134`）与 finally 中 `detach_from_conversation`（`:144-145`）配对，保会话引用计数正确。

## 4. 数据流

以 `GET /api/conversations/{id}/config`（前端打开会话页探测连接信息）为例：鉴权与 `get_user_id`（`:119`）→ `_is_v1_conversation` 判代（`:127`）→ V1 命中走 `_get_v1_conversation_config` 返回 `{runtime_id: sandbox_id, session_id}`（`:129-131`），前端转投 `/api/v1/sandboxes` 体系；未命中走 V0：attach（`:134`）→ 404 检查（`:137-141`）→ 取 runtime 配置（`:143`）→ finally detach（`:144-145`）→ 返回（`:147`）。

弃用端点单栈化：`GET /events` 绕过 conversation_manager **裸构造 `EventStore(sid, file_store, user_id)`**（`:259-263`），`search_events` 取 limit+1 条判 `has_more`（`:266-279`）；`POST /events` 经 `send_event_to_conversation` 送事件（`:298`）；`POST /message` 把文本包成 `MessageAction`（`:330`）→`event_to_dict`（`:333`）→`send_event_to_conversation`（`:336-338`）；`/microagents` 深入 `agent_session.memory` 读 `repo_microagents`/`knowledge_microagents`（`:401`、`:421`）并抽 `mcp_tools.stdio_servers`（`:411-413`）。

## 5. 设计决策（V0→V1 代际语境）

- **先并行后拆除**：V1 不是替换而是可选 router 挂在 V0 进程内（`:101-102`），`ENABLE_V1` 默认开——新旧前端同进程共存、同一会话列表混排两代会话，回滚只需一个环境变量。
- **判代用 ID 形态而非版本字段**：V1 UUID vs V0 旧格式是零 schema 成本判别键（`:55`）；但 `except Exception: return False`（`:63-65`）使 **V1 服务故障被静默降级为"按 V0 处理"**，随后 V0 路径 404——用户看到"会话不存在"而非"V1 服务异常"，排障须知这层伪装。
- **deprecated 注释即迁移说明书**：`/vscode-url`→`exposed_urls` 的 `VSCODE`（`:164-165`）、`/web-hosts`→`AGENT_SERVER`（`:199-200`）、`/events`→`/api/v1/events/search`（`:249-251`）、`POST /events`→sandbox webhook（`:294-295`）、`/message`→沙箱内 agent server（`:325-326`）、`/microagents`→`.../skills`（`:374-375`）。这份映射表是 API 迁移指南权威来源。
- **V1 架构位移**：V0"runtime 内嵌会话"在 V1 拆成 sandbox（资源）+agent-server（进程内会话）+webhook（事件回流）三件套，`X-Session-API-Key` 头鉴权取代 cookie 链。
- **lifespan 组合器**（`:50-59`）让两代栈互不干扰启停：MCP 与 V1 各带 lifespan，AsyncExitStack 逆序清理。

## 6. 新人提示

- **别在 V0 文件加功能**：头注明令 "avoid extending this legacy file"（`openhands/server/app.py:6`）；改会话需求先问"是否该去 app_server"。
- **坑：`/config` 对 V0 会话每次 attach/detach 整会话**（`openhands/server/routes/conversation.py:134-145`），高频轮询注意成本。
- **坑：判代依赖"V0 ID 从不是 UUID"的隐式约定**（`:60-62`）——动 ID 生成逻辑要记得这条契约。
- **勘误：`/vscode-url`、`/web-hosts` 无判代逻辑**（`:150-215` 不调 `_is_v1_conversation`），V1 会话请求走 V0 分支后 404/500——V1 会话直接用 `exposed_urls`。
- **`GET /events` limit 边界**：docstring 说 1-100，实际校验 `limit < 0`（`:253`）——`limit=0` 也通过返回空列表，文档与实现小漂移。
- **`/mcp` 以 Mount 直挂且 stateless**（`openhands/server/app.py:79`、`:47`），鉴权由 MCP 子应用自管，不走 get_dependencies。
- **`import openhands.agenthub`（`:25`）是注册副作用**：删掉它所有内置 Agent 从注册表消失且无静态报错——import-for-registration 陷阱。
