# 02 · V1 组合根与沙箱服务：`app_server/config.py` + `app_server/sandbox/`

> 覆盖：`openhands/app_server/config.py`（453 行）、`services/injector.py`（34 行）、`sandbox/sandbox_service.py`（233 行）、`sandbox_spec_service.py`（95 行）、`sandbox_models.py`（61 行）、`remote_sandbox_service.py`（918 行节选）
> 选题甄别：任务书原路径 `app_server/sandbox.py` 不存在——沙箱是 14 文件的 `sandbox/` 包，本文按包级展开。

## 1. 角色定位

01 篇的 `server/app.py` 是 V0 遗骸，`openhands/app_server/config.py` 则是 **V1 心脏：依赖注入（DI）组合根**——V1 全部可替换服务（事件/回调/沙箱/会话/用户/JWT/HTTP/DB）由它装配、按环境变量选型、以两种口径分发。`sandbox/` 包是 V1 资源层第一抽象：V0 的 Runtime（进程+容器+会话一体）被拆解，"沙箱"成为独立生命周期对象，agent-server 跑在沙箱里、事件经 webhook 回流；`SandboxService` 与 `SandboxSpecService` 是这套抽象的两个 ABC。

## 2. 内部结构

**injector.py（34 行 DI 原语）**：`InjectorState` 是 starlette `State` 别名（`openhands/app_server/services/injector.py:9`）——请求级 State 作注入载体，注入器可嵌套复用中间产物（先注 httpx_client，沙箱服务再取用）。`Injector[T]` 三个面：抽象 `inject()`（`:16-21`）、`async with` 版 `context()`（`:23-29`）、FastAPI 版 `depends()`（`:31-34`，传 `request.state`）。

**config.py（组合根）**：头部 `import openhands.app_server.event_callback  # noqa: F401`（`openhands/app_server/config.py:13`）保证事件处理器注册——与 01 篇 agenthub 同款 import-for-registration。`AppServerConfig`（`:99`，继承 SDK 的 `OpenHandsModel` `:57`）宿主九个可空注入器槽位 event/event_callback/sandbox/sandbox_spec/app_conversation_info/app_conversation_start_task/app_conversation/user/jwt（`:110-118`）加必有默认的 httpx/db_session（`:119-124`）。

`config_from_env()`（`:133-289`）是环境驱动装配线，函数体内 **14 处延迟 import**（`:135-176`：LiveStatus/AWS/GCP/Filesystem/SQL/Docker/Process/Remote/Auth 各注入器）——推迟实现类加载，断"配置→实现"环且未选后端不被导入。回填逻辑：事件服务按存储商三选一（AWS `:183-190`/GCP `:191-195`/文件系统 `:197`）；沙箱按 `RUNTIME` 分派（remote `:204-208`/local+process `:209-210`/Docker 默认 `:256`，Docker 分支解析端口与 `SANDBOX_VOLUMES` 卷挂载 `:213-255`）；会话服务固定 LiveStatus 并接 `TAVILY_API_KEY`（`:274-281`）；用户/JWT 回填（`:283-287`）。

单例与分发：`_global_config`（`:292`）经 `get_global_config()` 懒初始化（`:295-302`）；每服务一对三行样板——手动 `get_sandbox_service`（`:321-326`）/`get_app_conversation_service`（`:353-358`）与 FastAPI `depends_sandbox_service`（`:406-409`）/`depends_app_conversation_service`（`:430-433`）——**组合根零业务逻辑**。

**sandbox 三抽象**：`SandboxStatus` 五态（`openhands/app_server/sandbox/sandbox_models.py:9-15`）；标准服务名 `AGENT_SERVER/VSCODE/WORKER_1/WORKER_2`（`:27-30`）；`SandboxInfo` 携带 `session_api_key`（`:40-47`，规定 `X-Session-API-Key` 头访问）与 `exposed_urls`（`:48-55`）。`SandboxService`（`openhands/app_server/sandbox/sandbox_service.py:29`）八方法：抽象的 search/get/get_by_key/start/resume/pause/delete（`:33-37`、`:41`、`:45-48`、`:60-68`、`:71-76`、`:173-186`）；基类自带 `batch_get` 并发（`:50-57`）、**轮询等待器 `wait_for_sandbox_running`**（`:78-125`：默认 120s/2s `:81-82`，ERROR 即抛 `:110-111`，RUNNING 后可选探 agent-server `/alive` 防"容器起了进程没起"竞态 `:116-118`）、探活实现（`:127-150`）、按 AGENT_SERVER 名取 URL 并做 localhost→docker 主机名替换（`:152-171`）、**配额回收 `pause_old_sandboxes`**（`:188-229`：分页迭代 `:203`→按 created_at 排序 `:212`→暂停超额最老者，单个失败继续 `:225-227`）。文件头三常量定义向沙箱注入密钥/回调/CORS 的环境变量协议（`:24-26`）。`SandboxSpecService`（`openhands/app_server/sandbox/sandbox_spec_service.py:19`）目前只读（search `:29-32`/get `:35-36`/默认取第一项 `:38-43`），docstring 明言扩展计划（`:22-25`）；`AGENT_SERVER_IMAGE='ghcr.io/openhands/agent-server:1.14.0-python'`（`:16`）**钉死镜像版本**，可被双环境变量覆盖（`:64-69`）；`get_agent_server_env` 从 `OH_AGENT_SERVER_ENV` JSON 注入沙箱环境（`:72-95`）。

## 3. 外部连接

- **上游**：`server/app.py:27` 经 `get_app_lifespan_service()`（`config.py:389-391`）把 V1 lifespan 挂进 V0 进程；`v1_router` 的 sandbox 路由经 depends 工厂取服务。
- **SDK 依赖**：`DiscriminatedUnionMixin/OpenHandsModel/page_iterator` 来自 `openhands.sdk`（`sandbox_service.py:19-20`）——独立仓 Software Agent SDK，V1 与之共生。
- **三实现族**：Docker/Process（`RUNTIME=local/process`，`config.py:209-210`）/Remote（`config.py:204-208`，适配 V0 遗留 RemoteRuntime HTTP API）。注入器双继承 `DiscriminatedUnionMixin + Injector[T]`（`sandbox_service.py:232-233`、`sandbox_spec_service.py:58-61`），前者使 config 槽位能从 env/JSON 反序列化出正确子类。
- **ORM**：`StoredRemoteSandbox(Base)`（`openhands/app_server/sandbox/remote_sandbox_service.py:82`）表 `v1_remote_sandbox`（`:90`），`session_api_key_hash` 存 SHA-256（`:77-79`）——远端 API 不返回停止态，**远端是"正在跑"的真值，本地表补"跑过"的账**（`:83-88`）；状态归一靠双映射表（`:56-70`），注释直言旧 status 不可信（`:191-195`）。
- **DB 注入器**：`DbSessionInjector`（`openhands/app_server/services/db_session_injector.py:27`）按 `GCP_DB_INSTANCE` 走 cloudconnector 或普通引擎（`:166`），驱动延迟导入（`:171`）。

## 4. 数据流

以"启动一个 V1 会话沙箱"为例：路由经 `depends_sandbox_service()` 取按 env 选型的服务（同时从 State 取 httpx/db_session/user_context，见 `RemoteSandboxService` 字段 `remote_sandbox_service.py:106-116`）→ `start_sandbox` 以 spec（id 即镜像名）+密钥/回调环境变量拉起容器或远程 runtime → `wait_for_sandbox_running(sandbox_id, httpx_client=...)`（`sandbox_service.py:78`）轮询至 RUNNING 后打 `{agent_server_url}/alive`（`:142-144`）确认进程就绪 → `_to_sandbox_info`（`remote_sandbox_service.py:134-186`）把 runtime dict 翻成 `SandboxInfo`：仅 RUNNING 组装 exposed_urls 四条（`:147-170`，VSCODE URL 内嵌 session token `:150-153`）→ 会话服务取 AGENT_SERVER URL 直连沙箱开会话；超额时 `pause_old_sandboxes` 淘汰最老（`sandbox_service.py:188-229`）。

## 5. 设计决策（V0→V1 代际语境）

- **从全局单例到注入器组合根**：V0 靠 `openhands.server.shared` 模块级单例（01 篇 `app.py:43`），测试与多租户皆难；V1 每服务变 Injector 槽位（`config.py:110-118`）+env 回填，**SAAS/OSS/本地 CLI 三形态只差环境变量**。
- **延迟 import 是架构手段**：14 处函数体导入（`config.py:135-176`）断循环+可选后端零导入成本；代价是 IDE 跳转失效、依赖图隐式化。
- **Sandbox 与 Runtime 分野**：V0 Runtime 捆绑执行+事件+浏览器（06 篇）；V1 拆纯资源抽象，`/alive` 探活（`sandbox_service.py:113-121`）对"容器 RUNNING≠服务可用"竞态补课。
- **Remote 实现是适配器**：docstring 明言 "adapts the legacy RemoteRuntime HTTP protocol"（`remote_sandbox_service.py:100-104`），双映射表+本地 ORM 补账兜底遗留 API 缺口。
- **密钥卫生**：key 仅 RUNNING 且有全权才返回（`sandbox_models.py:40-47`），存储只留哈希（`remote_sandbox_service.py:77-79`）。

## 6. 新人提示

- **坑：`get_global_config()` 进程级单例**（`config.py:292-302`）——测试改 env 后须重置 `_global_config=None`；运行时切后端不可行需重启。
- **坑：`os.environ['SANDBOX_API_KEY']` 直接下标**（`config.py:206-207`）——`RUNTIME=remote` 缺变量时是 KeyError 而非优雅报错。
- **勘误：默认 spec=列表第一项**（`sandbox_spec_service.py:38-43`）无优先级语义；多 spec 部署"不传 id 用哪个"取决于 search 排序。
- **勘误：`wait_for_sandbox_running` 不传 httpx_client 时跳过探活**（`sandbox_service.py:120-121`）——RUNNING 即返回，竞态重新暴露；传不传 client 行为不同。
- **`AGENT_SERVER_IMAGE` 是版本锚**（`sandbox_spec_service.py:16`）：升镜像同步此行或设双 env；排查"沙箱起不来"先核 tag。
- **`pause_old_sandboxes` 的 `except Exception: pass`**（`sandbox_service.py:225-227`）吞单次失败继续——回收数可能少于应回收数。
- **`sandbox_spec_id` shadows `runtime['image']`**（`remote_sandbox_service.py:93`）：字段名与远端键不同名，对远端 API 调试记得这层别名。
