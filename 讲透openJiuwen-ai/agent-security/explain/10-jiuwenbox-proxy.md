# 10 · jiuwenbox 服务端：8321 管理 API、8322 隐私代理与 Windows 回环代理线

## 一、角色定位

jiuwenbox 的 `server/` + `proxy/` 两目录构成子系统的"驾驶舱"。它对外暴露两个 TCP 面：

- **8321 管理 API**（`server/launcher.py` 默认 `http://0.0.0.0:8321`，launcher.py:30）：FastAPI 应用，管沙箱全生命周期（创建/exec/文件传输/策略）、管隐私代理、还挂一个 MCP 端点——09 篇的 supervisor 全部由它驱动。
- **8322 隐私代理**（`inference_privacy_proxies.listen_port`，测试默认 `JIUWENBOX_PROXY_PORT=8322`，tests/conftest.py:81）：给沙箱内 LLM 调用做**API key 隔离**的正向代理——客户端带任意 token，代理替换成真实上游 key 转发，密钥永不进沙箱。

另有 Windows 专属的第三个面：**127.0.0.1:60080-60089 回环代理段**（win_constants.py:417-418），这是 09 篇 WFP 线的服务端半边，本篇从服务端视角补完。

入口是 pyproject 的双 console scripts（jiuwenbox/pyproject.toml:30-32）：`jiuwenbox`（CLI，src/jiuwenbox/cli/jiuwenbox.py:1257 的 main）与 `jiuwenbox-server`（server/launcher.py 的 main）。CLI 与服务端共用同一套 models/routes 层。

## 二、内部结构

### 8321 服务端装配

`create_app`（app.py）的装配顺序值得记住：CORS 中间件（app.py:558-559）→ BearerTokenAuthMiddleware（app.py:565）→ 三个路由器挂到 `/api/v1` 前缀：sandbox_router、policy_router、proxy_router（app.py:637-639），外加 MCP 路由。

认证是 **opt-in** 的：`BearerTokenAuthMiddleware` 只有在环境变量配置了 token 时才校验，未配置直接放行（auth.py:45-55 的 dispatch 逻辑：`get_configured_token()` 返回 None 就跳过）。这与默认 `0.0.0.0` 监听组合成"默认裸奔"——已知沉淀里的"0.0.0.0:8321 默认暴露"双系统之一（另一是 agent_ssas 的 8443）。

沙箱 API 面很宽（routes/sandbox.py）：`/capabilities`、`/sandboxes`（CRUD+start/stop/restart）、`/exec`、`/exec_background`、`/upload`、`/download`、`/files`、`/search`、`/logs` 等 20+ 端点（routes/sandbox.py:38-297）。策略面（routes/policy.py）只有三个：按沙箱查策略、GET/PUT 全局 timeout（routes/policy.py:26-74）。

**capabilities 端点的诚实报告**（routes/sandbox.py:38-83）：枚举 bubblewrap/windows/conch 三个 runtime，先查 `available_runtime_names()`，不可用标 `"available": false`；加载即实例化并逐字段报告十项能力（local_pid/background_jobs/fast_file_io/…/soft_delete），装载抛异常也落到 unavailable+error 而非静默列表（routes/sandbox.py:81-82）。这是"探测即部署前置"的设计（注释引设计文档 5.3 规则 4）。

**proxy-only 模式**：策略文件只配了 inference_privacy_proxies 时，lifespan 置 `_proxy_only_mode=True`（app.py:64-69），跳过构建 SandboxManager；此后任何沙箱 API 调用会被 `get_sandbox_manager` 主动拒绝为 503，而不是懒构建复活沙箱子系统（app.py:246-260）——"关了就是关了"，防止半启用状态。

### 8322 隐私代理

数据模型两层：`ProxyRoute`（path_prefix/target_endpoint/api_key/skip_cert_verify，inference_privacy_proxy.py:36-99）与 `InferencePrivacyProxyConfig`（listen_host 默认 127.0.0.1、listen_port 默认 0=禁用，inference_privacy_proxy.py:102-106）。路由匹配按路径前缀，命中后把 `Authorization: Bearer <any-key>` 正则替换为 `Authorization: Bearer {route.api_key}` 再转发（inference_privacy_proxy.py:221-230）——密钥注入是代理内发生的，沙箱侧永远只见占位 token。

关键点是 **listen_port: 0 = 默认禁用**。inference-policy.yaml 头注释把这个设计写得很清楚："proxy stays off until the deployed copy sets listen_port above 0"、"Leave api_key empty here. Set the upstream key only on the deployed copy"（configs/inference-policy.yaml:1-16，listen_port: 0 在 :22）——发行模板零密钥零监听，部署侧显式开启。这是六份 YAML 里唯一默认不监听的对外面。

### ProxyManager 的"单实例多路由"命名误导

`inference_privacy_proxy_manager.py` 的 API 词汇是 create_proxy/get_proxy/stop_proxy/list_proxies，但**实例字典里永远只有一个条目**：`_proxies["default"]`（manager 侧 get_global_instance 直接取 `"default"` 键，inference_privacy_proxy_manager.py:79-81）。所谓 "proxy" 其实是全局实例上的一条 route：

- `create_proxy`（:142-190）：无全局实例则建；有则往 `config.routes` 里 append 一条，日志如实写 "Added route"（:183）；
- `stop_proxy`（:265-277）：停的是"一条 route"，全部 route 都停了才停全局代理（docstring: "Stop a specific route (disable it, stop global proxy if all routes disabled)"）；
- `list_proxies`（:83-108）：返回"每 route 一条"的列表，每条带独立 state/listen_host/listen_port——同一 listen_port 被重复报成 N 份。

REST 面（routes/proxy.py）照单全收：POST `/proxies`、GET `/proxies/{name}`、DELETE、start/stop、logs（proxy.py:70-196）。读这份 API 时必须在脑内做一次"proxy→route"的翻译，否则会误以为能起多个监听端口——实际只有一个端口、一个 asyncio.Server（inference_privacy_proxy.py:116），route 只有启停态（enable_route/disable_route，:133-143，禁用的 route 404）。

### Windows 回环代理段（服务端半边）

app.py lifespan 在 win32 上做一次性环境准备并启动 `win_proxy.serve_windows_proxy`（app.py:297-334），端口范围取自根策略的 windows.proxy 字段、缺省回退 60080-60089。与 09 篇呼应的三件套在服务端视角闭合：WFP Permit 只放行 `127.0.0.1:[60080,60089]`；win_proxy 只绑 60080（win_proxy.py:716-718）；60081-60089 高到低留给 recycle broker 与沙箱内本地服务（win_recycle_broker.py:587-593）。

### 8321 的自我保护

`network.mode: host` 的沙箱（code-agent 档）与 box-server 同网络命名空间，理论上可以 `curl 127.0.0.1:8321` 打穿管理 API。防御是 iptables OUTPUT 按 sandbox-uid 阻断到 server 自身端口（runtime/process.py:99-121）：保护端口默认 `(8321,)`，但会从 `JIUWENBOX_LISTEN` 自动推导、可用 `JIUWENBOX_SERVER_PROTECT_PORTS` 覆盖或清空禁用（:119-120）。**无 root 装不上规则时 warning 后继续建沙箱**而非中止（process.py:110-114）——注释明说这是 code-agent 无特权部署形态的既定取舍。

## 三、外部连接

- **驱动 supervisor**：sandbox API → SandboxManager → runtime registry（bubblewrap/windows/conch 三后端，routes/sandbox.py:52-55）→ 09 篇全部隔离件。
- **策略链**：PolicyReader 读 YAML → PolicyEngine 校验/合并/裁剪（保留路径防窜改见 09 篇）→ SecurityPolicy 下发。fail-closed 链条上有三个默认：网络规则 `default: "deny"`（jiuwenbox/src/jiuwenbox/models/policy.py:464，NetworkRulePolicy 的 Literal 默认值）；bwrap user namespace 下 capabilities 只经显式 `--cap-add` 授予（bwrap.py:284-290 映射 add/drop，空 add=零能力）；/capabilities 对载不出的 runtime 报 unavailable。
- **MCP**：routes/mcp.py 挂 MCP 协议端点，TransportSecuritySettings 开 DNS rebinding 防护，allowed_hosts 默认四个回环条目（`localhost`/`localhost:8321`/`127.0.0.1`/`127.0.0.1:8321`，mcp.py:23-28），可用 `JIUWENBOX_MCP_ALLOWED_HOSTS` 追加。
- **Windows 线**：win_setup 环境准备 + win_proxy + recycle broker 全在 lifespan 启动（app.py:297-334）。
- **agent_ssas 无直接耦合**：两个子系统独立成包，jiuwenswarm 宿主分别集成。

## 四、数据流

一次沙箱内 LLM 调用经隐私代理的完整链路：

```
沙箱进程: POST http://127.0.0.1:8322/llm/v1/chat/completions
          Authorization: Bearer <沙箱侧任意 token>
  ↓ (Linux: 网络规则放行该 egress; Windows: WFP 放行非回环需经 60080 代理)
InferencePrivacyProxy (单 asyncio.Server, 8322):
  按 path_prefix "/llm" 匹配 route → 正则替换 Authorization 为上游真实 key
  → 转发 target_endpoint (可选 skip_cert_verify)
  ← 响应原路回传; 沙箱侧全程接触不到真实 key
```

管理面数据流则相反：运维打 8321 `/api/v1/sandboxes`（Bearer token 若配置），SandboxManager 建 bwrap/Windows 沙箱；`/api/v1/proxies` 增删的其实是全局代理实例上的 route，改动即时生效于 8322 的路由表。

## 五、设计决策与权衡

1. **密钥拓扑选"代理注入"而非"环境变量下发"**。api_key 只存在于服务端策略与代理内存，沙箱拿占位符——即使沙箱被完全逃逸，攻击者也只能拿到转发能力而非密钥本体。代价是多一跳延迟与代理成为单点。
2. **默认关闭 + 部署侧显式开启**（listen_port: 0）与 8321 的默认 0.0.0.0 形成刺眼对照：同一个包里，带密钥的面默认关、不带密钥的管理面默认全网开。运维落地时 8321 必须配 token 或改绑回环/UDS（launcher 支持 `unix:///abs/path`，launcher.py:50-56）。
3. **"proxy"命名债**。REST 词汇表暗示多实例，实现是单实例多路由。这大概是设计演进（先多代理后收敛为路由）留下的接口化石——API 兼容性压过了命名诚实。get_proxy 返回结构里 route 字段嵌套着真实语义（inference_privacy_proxy_manager.py:122-135），新代码应读 route 字段而非 name。
4. **proxy-only 503 而非懒复活**（app.py:246-260）：显式拒绝优于隐式复活，让"这台机器只做代理"的部署意图不可被运行时状态模糊掉。
5. **iptables 自保护的可失败性**：装不上规则时选择继续（process.py:110-114），因为阻断建沙箱会废掉无特权部署形态；这与 cgroup fail-closed（09 篇）是同一系统内按资产重要性分级的又一实例——管理 API 打穿是风险，但部署可用性是刚性。
6. **三个 runtime 后端 + capabilities 自描述**（routes/sandbox.py:52-83）：把"本机有没有 bwrap/Windows/Conch"变成可探测的 API 而非文档约定，部署脚本可以先行探测再决定下发哪种策略。

## 六、新人提示与坑

- **6443/8321/8322/60080-60089 四个端口别混**：8321=管理 API（可关可认证）；8322=隐私代理（默认关）；60080-60089=Windows 沙箱回环段（WFP 强制）；agent_ssas 的 8443 是另一子系统的 HTTP 事件口。
- **enterprise-policy.yaml 是孤儿**：六份 YAML 里它最"唬人"（名字最像生产档），但 src/ 与 tests/ 全仓 grep 零引用——没有任何代码路径加载它。真实的档位谱系是 default → java（更严、无出网）→ windows（WFP 代理）→ code-agent（host 网络最宽）+ inference（代理档）。
- **stop_proxy 的级联语义**：停最后一条 route 会连全局监听一起停；下次 create_proxy 又会重建实例。测试断言端口占用时要考虑这个生命周期。
- **API key 出现在 get_proxy 响应里**（inference_privacy_proxy_manager.py:128）：管理 API 能读到明文上游 key——8321 的认证配置因此不是可选加固而是必要前提。
- **CLI 与 server 是同一模型的两张皮**：cli/jiuwenbox.py 1257 行，改 models/policy.py 的字段两边同时受影响；集成测试（tests/integration/）同时覆盖 server API 与 CLI 两条路。
- **proxy 日志内存有界**：ProxyInstance.add_log 只在内存滚动（inference_privacy_proxy_manager.py:47-54），进程重启即失；审计需求走 `/proxies/{name}/logs` 端点时注意它不是持久账本。
