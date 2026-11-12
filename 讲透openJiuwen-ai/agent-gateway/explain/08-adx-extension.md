# 08 · extensions/adx：ADX Environment 深度适配器——双继承替换内脏与幂等身份契约

> 所属仓库：openJiuwen-ai/agent-gateway。本篇覆盖 `agent_gateway/extensions/adx/`（7 文件约 670 行）及其依赖的共享错误契约 `agent_gateway/extensions/yuanrong_frontend_client.py`。前置阅读：07 篇（agentos_router 是它继承的母体）。

## ① 角色定位

adx 是 Gateway 的**另一种南向部署形态**：当 `gateway.agent_client.type = adx_router`（判定在 `agent_gateway/extensions/adx/config.py:30` 的 `adx_router_selected`）时，扩展系统装载 `AdxRouter`（`agent_gateway/extensions/adx/extension.py:13`，`register_extensions` 在 `:32`），用 **ADX Environment 公有 API** 替换掉 YuanRong 私有 API 作为沙箱生命周期后端。

`agent_gateway/extensions/adx/__init__.py:2` 一句话定位："ADX Environment transport for the Python Gateway"。但真正的架构意图写在 `agent_gateway/extensions/adx/router_client.py:39` 的类 docstring 里——**"Keep Registry, launch-spec assembly and user routing in the business Gateway"**：保留业务路由（注册表、launch-spec 组装、用户级路由决策），只替换生命周期与转发两条管线。也就是说，agentos_router 与 adx 不是并列的两套实现，而是**继承 + 换内脏**的关系——这是全仓最深的适配器样本。

## ② 内部结构

五个文件分三层：

- **config.py（82 行）**：`AdxRouterConfig`（`agent_gateway/extensions/adx/config.py:19`）持 ingress_url/tenant/token 加一个**完整内嵌的 `RouterConfig`**（`:22-23`，07 篇的配置原样复用）。`load_router_config`（`:45`）的校验近乎偏执：closed key set（`:47-51`，多余键直接 ValueError）、ingress 必须是纯 HTTPS origin（禁 userinfo/path/query/fragment）、token 只能来自 `token_env` 指定的环境变量且必须 ASCII 无空白（`:66-68`）、workspace_target 必须绝对规范路径（`:77-78`）。`token` 字段 `field(repr=False)`（`:22`）防止凭据进日志 repr。
- **control_client.py（234 行）**：`AdxControlClient` 把 ADX Environment REST API 适配成 YuanRong 客户端的鸭子类型——`connect/disconnect/get_agent_info/wait_until_running/create_sandbox/delete_sandbox` 六个方法签名与 `YuanrongFrontendAgentClient` 对齐，使它可以直接作为父类构造器的 `yuanrong` 参数注入（`agent_gateway/extensions/adx/router_client.py:48-49`）。
- **router_client.py（144 行）**：适配器本体 `class AdxRouterClient(AdxFileMixin, AgentOSRouterClient)`（`:38`），mixin 在前、基类在后。
- **file_client.py（158 行）**：`AdxFileMixin`（`agent_gateway/extensions/adx/file_client.py:23`）把容器文件四操作翻译成 ADX runtime 的 invoke 原语。
- **errors.py（12 行）**：`AdxRoutingError(RuntimeError)` 带 code 字段，"requests are never replayed"（`agent_gateway/extensions/adx/errors.py:6`）——路由面错误一律上抛，绝不自动重放。

## ③ 外部连接

- **ADX ingress**：control 面走 `POST/DELETE /api/environment/v1/environments`、查询走 `GET /api/instances`、操作面走 `/direct/{environment}/invoke`（`control_client.py:197/206/216`），全部 `Authorization: Bearer` + ingress_url。响应信封是 `{code, data(base64-JSON)}`，`:83-91` 解码。
- **父类 AgentOSRouterClient**：Registry、launch-spec、AgentManager、single-flight、idle reaper、断连清理全套继承（07 篇）。
- **Web 通道文件 API**：`set_channel_manager` 覆写（`router_client.py:68-72`）把 `channel.container_file_client = self` 挂到 Web 通道上——ADX 模式下容器文件不再走 YuanRong HTTP，而走本 mixin。
- **health_check 通道**：`send_request` 前置拦截 health check 探针，返回 mocked OK（`router_client.py:136-143`），`_closed` 期间则抛 `ADX_ROUTER_CLOSED`。
- **鉴权**：与 agentos_router 共用 `AgentOSAuthenticator`（`extension.py:16-19`），且 `authenticate_http` 对 `channel == 'file-api'` 的请求先调 `_begin_file_transfer()`（`router_client.py:74-81`）在鉴权时刻就固定本次传输的环境身份。

## ④ 数据流

**创建沙箱（幂等身份契约的主舞台）。** 父类 `_create_agent` 用确定性名称 `f"{user_id}+{agent_type}"` 调 `create_sandbox`（`agent_gateway/extensions/agentos/agentos_router/router_client.py:2894-2899`）。ADX 侧 `create_sandbox`（`control_client.py:179`）先派生稳定实例 ID `f'{namespace}-{name}'`（`:183`），然后走三段簿记：

1. **存在即复用**：`_lookup(instance)` 命中则直接返回 `SandboxInfo(instance, metadata=existing)`（`:184-186`）——实例 ID 就是幂等键。
2. **删除悬置确认**：若 `_deletes` 里挂着一个"响应丢失的 DELETE"，那么随后查不到实例（404）这个事实本身就是删除成功的确认，允许为新创建清空两个簿记（`:187-191` 注释钉版 "Absence is the confirmation"）。
3. **规格指纹 + 操作 ID**：请求体 `sha256` 指纹与 `X-Request-Id` 一起 `setdefault` 进 `_creates`（`:193-194`）。同一实例 ID 在结果未知期间**只能以完全相同的 body 与同一个 operation id 重放**——指纹变了就 `CONFLICT`（`:195-196`）。

**超时语义的传导链。** `control_client.py:71`：HTTP POST `/environments` 遇 `httpx.RequestError`（结果未知）时精确抛 `AdxCreateTimeout`。这个异常类在 `:29` 双继承 `AdxControlError` 与 `YuanrongAgentTimeoutError`，而 `AdxControlError` 又继承 `YuanrongAgentApiError`（`:22`）。于是父类 `router_client.py:2903` 的 `except YuanrongAgentTimeoutError:` 分支**原样命中**：以相同参数重试一次做幂等回查（`:2904-2919` 注释："首次请求未达则正常新建；已创建则按同名幂等复用，不产生第二个实例"）。`agent_gateway/extensions/yuanrong_frontend_client.py:375` 的 `YuanrongAgentApiError` 与 `:379` 的 `YuanrongAgentTimeoutError`（docstring："请求可能已在服务端生效，调用方需按幂等处理"）由此成为跨后端的**异常即协议**。

**转发面替换。** 父类的 WS 直连逻辑被三个 URL 工厂覆写：`_agent_url`（`router_client.py:91-95`）把实例寻址改写为 `wss/https://{ingress}/agent/{protocol}?target=urn:adx:instance:<quoted>&port=N`；`_connect_ws_until_ready`（`:106`）自带 Bearer 头（`:110`）与可重试循环，复用父类导出的 `is_ws_connect_retryable` 等辅助函数（`:26-28` 导入）。

**文件面适配。** 上传 = 分块 `file.write_chunk`（hex 编码，64KB 块，`file_client.py:69-75`）写 `.upload-<uuid>` 临时路径 → `file.rename` 原子落位（`:76`）→ finally 里 best-effort `file.remove`（`:80-83`，注释："Unknown transport outcomes must not trigger another business write"）。`_FILE_TRANSFERS` ContextVar（`:19`）在鉴权钩子清空（`:28`），流式任务继承同一 pin 字典，同一请求内环境身份漂移立即报 "Environment changed during transfer"（`:42-45`）。

## ⑤ 设计决策与权衡

**决策一：继承复用 vs 组合复用。** 用双继承把 AgentOSRouterClient 的 ~3000 行业务路由全盘吃下，只覆写 6 个方法（URL 工厂、WS 连接、鉴权、配置、tool-sandbox env、health check）。收益是不复制任何路由逻辑；代价是 AdxRouterClient 与父类私有约定强耦合（`self._yuanrong` 现在装的是 `AdxControlClient`，靠鸭子类型成立）。若 YuanRong 客户端接口漂移，两个后端要一起改——错误类继承链就是为此付出的契约成本。

**决策二：异常类型即协议通道。** 不改父类一行代码实现"超时回查"，靠 MRO 把 `AdxCreateTimeout` 塞进 `YuanrongAgentTimeoutError` 的 except 分支。`:30` 的类 docstring 把契约讲明："An unknown create outcome must retain its instance and request identities"——**结果未知的操作，其实例身份与请求身份必须可复现**，否则幂等回查无从谈起。这比给父类加 `backend` 参数更内聚，但也更隐蔽：不读继承链根本不知道回查逻辑被复用了。

**决策三：主动阉割 tool sandbox。** `set_or_update_server_config` 强制 `sandbox.enabled=False`（`router_client.py:83-86`），`_tool_sandbox_env` 返回空 dict（`:88-89`）——ADX 模式没有工具沙箱概念，与其让父类的环境注入半生效，不如显式关死。`__init__` 里 `self._closed = True`（`:61`）同理：构造完先处于关闭态，等显式 `connect()`（父类 `agentos/agentos_router/router_client.py:1248-1250` 置 `_closed=False`）才开门，health check 在此之前如实报 closed。

**决策四：builtin 镜像名的部署侧改写。** `_creation_body` 里 `name.endswith('+jiuwenswarm') and image == 'jiuwenswarm-agent-runtime:latest'` 时把镜像替换为配置的 `builtin_image`（`control_client.py:132-133`）——业务侧写死的缺省镜像名允许部署环境用私有 registry 镜像顶替，只动最内层转换不动上游。

**决策五：tenant 一致性校验。** `_lookup` 要求返回行 `id == instance` **且** `tenant_id == config.tenant`（`:100-103`），身份与租户双匹配，否则 CONFLICT——多租户 ingress 上错拿别家实例按最严重错误处理。

## ⑥ 新人提示与坑

1. **两份 router_client.py / 两份 config.py**：adx 的 `router_client.py`（144 行适配器）与 agentos_router 的同名文件（3517 行母体）极易混锚，写引用必须带全路径 `agent_gateway/extensions/adx/router_client.py:38` vs `agent_gateway/extensions/agentos/agentos_router/router_client.py:522`。两份 `load_router_config` 同理（adx 的在 `adx/config.py:45`，agentos 的在 `agentos_router/config.py:378`，且前者内部调后者）。
2. **改 `_creation_body` 字段前先想指纹**：body 进 sha256 指纹（`:193`），同一实例结果未知期间任何字段变化都会 CONFLICT 拒绝——这是特性不是 bug；但若你在"结果未知"窗口期部署了新代码改了 body 组装，存量悬置创建会全部卡 CONFLICT，需要等 operation 结算或换实例名。
3. **`AdxRoutingError` 永不重放**：路由面（`errors.py`）与生命周期面（`AdxControlError`）是两套错误体系，前者 code 直接透传给调用方；想加重试逻辑只能在 control 面做，别在 send_request 外层包 try-retry。
4. **上传临时文件名是 `.upload-` 前缀**：`file.remove` 在 finally 里吞掉异常（`:81-83`），意味着 rename 成功后对已不存在的临时路径 remove 失败属正常；但也意味着**孤儿临时文件会静默留存**（比如 rename 前进程崩了），运维清理脚本要认这个前缀。
5. **`connect_timeout_seconds` 双语义**：既是 httpx 客户端超时（`control_client.py:40`）也是 `wait_until_running` 的总等待上限（`:116`），配置一个值两处生效，调优时注意。
6. **health check 是 mock 的**：ADX 模式下 `send_request` 对 health check 通道直接返回 mocked OK（`router_client.py:140-143`），健康探针探测的是 Gateway 进程而非 ADX 后端连通性——排查"探针绿但实际不可用"时记住这一层。

**关联阅读**：母体路由与 single-flight 见 07 篇；YuanRong 共享客户端（错误契约源头）在 `agent_gateway/extensions/yuanrong_frontend_client.py`；扩展装载机制见 12 篇。
