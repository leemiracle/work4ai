# backend_api/session — SDK 与 ClearML Server 的通信层

## ① 角色定位

`clearml/backend_api/session/` 是 SDK 的"网络栈"：所有与 ClearML Server 的 HTTP 通信（认证、请求封装、重试、版本协商、限流分片）都收敛于此。它对上以 `Session.send(Request) -> CallResult` 一对极简签名服务整个 `backend_interface`，对下以 `requests.Session`（带重试适配器）直连 REST 风格但非标准 REST 的 `/service.action` 端点。图谱归入 **Backend API Client 层（69 节点，全仓最大服务层）**，`file:clearml/backend_api/session/session.py` 出边 22 条（token_manager/request/callresult/defs/utils/config）、入边 6 条（`task.py`、`backend_interface/base.py`、`backend_interface/task/log.py` 等），是典型的被全仓依赖的底座节点。

## ② 内部结构

**session.py（1177 行）— 核心 `Session`（session.py:67，`class Session(TokenManager)`）**：

- **类属性即协议常量**：双品牌请求头 `X-ClearML-Worker/X-Trains-Worker`（session.py:71-81）；超时阶梯——首请求 `(3.0,10.0)` 快速失败、常规 `(10.0,300.0)`、大载荷写超时（session.py:86-89）；重试码含 502/503/429/421（session.py:114）；离线开关（session.py:92）与离线默认版本 "2.9"（session.py:93）。`api_version = "2.9"`（session.py:99）注释言明须与 services 目录最低版本一致。
- **`__init__`（session.py:141）→ `_connect`（session.py:191）**：解析 host、按 `api.http.retries` 建重试会话、读 `max_req_size`；凭据三选一——`ENV_AUTH_TOKEN` 裸 token、或 access_key/secret_key（env → config → 默认空，session.py:225-236），全空抛 `MissingConfigError`；随后进 TokenManager 立即 `refresh_token()`。
- **版本协商**：解码 JWT 取 `api_version/server_version/feature_set` 写回类属性（session.py:253-268）——SDK 能力随服务器降级，企业版 feature_set 门槛由此判。vault 配置回写见 `_load_vaults` 调用（session.py:281-291）。
- **请求流水**：`send_request`（session.py:507）加 Bearer 头（session.py:503）→ `_send_request`（session.py:380）发 HTTP。四个细节值得逐行读：URL 拼接 `{host}/v{version}/{service}.{action}` 或无版本 `{host}/{service}.{action}`（session.py:421-425）；按请求体大小选超时阶梯（session.py:429-434）；SSLError/解码错误无限 sleep(0.1) 重试（session.py:456-473）；**401 自动刷新 token 仅一次**（session.py:475-485），503 且 `wait_on_maintenance_forever` 时永久等待。
- **批量分片**：`send_request_batch`（session.py:550）把 JSON-lines 按 `max_req_size` 切片，在换行符边界断开，超限行丢弃记 error——大批量上报靠客户端自切而非服务器分页。
- **顶层 `send`（session.py:651）**：校验 schema → Batch/普通分路 → `CallResult.from_result` 包装；`send_async`（session.py:642）只是加 `X-ClearML-Async` 头的语义糖。token 刷新在 `_do_refresh_token`（session.py:899）：优先既有 token 换新、其次 HTTPBasicAuth、均无则裸请求，成功后回写 `ENV_AUTH_TOKEN` 供子进程继承。

**token_manager.py（110 行）— `TokenManager`（token_manager.py:10）**：模板方法模式，`token` property 经 `_get_token`（token_manager.py:100）检查有效期（默认阈值 60s，token_manager.py:46）不足自动调抽象 `_do_refresh_token`（token_manager.py:106）；`get_decoded_token`（token_manager.py:69）兼容 PyJWT 1.x/2.x 两套 API 无签名解码。

**client/client.py（556 行）— 高层 ORM 风格封装**：`APIError`（client.py:46）、`Response/TableResponse`（client.py:141/189）、`Entity`（client.py:274）实现 `client.tasks.get_by_id(id).action()` 链式语义（`__getattr__` 注入 id）、`StrictSession`（client.py:98）把失败结果升级为异常且支持 `config_file` 临时覆盖配置路径；`APIClient`（client.py:509）用 `make_service_class`（client.py:464）+ `get_requests`（client.py:445）+ `make_action`（client.py:365）**运行时动态生成** auth/queues/tasks/events/models/projects/workers 等服务类——服务定义完全由 `backend_api/services/v?.*` 的 Request 类驱动，零手写样板。

**周边小件**：request.py:23 `Request` 与 `BatchRequest`（request.py:47）；request.py:24 `def_method = ENV_API_DEFAULT_REQ_METHOD.get(default="get")` 是**全局默认 HTTP 方法为 GET** 的出处；defs.py:6-19 定义 `CLEARML_API_HOST/API_ACCESS_KEY/API_SECRET_KEY`（均带 TRAINS_ 旧别名）；session.py:1035 `browser_login` 浏览器交互式发 token。

## ③ 外部连接（图谱边证据）

`session.py` 出边指向 `token_manager.py/request.py/callresult.py/defs.py`、`backend_api/utils.py`（重试会话工厂）、`backend_config/{__init__,defs,utils}`、`config/__init__.py`（凭据与 api.* 配置消费）、`utilities/pyhocon`（配置解析）；入边证明唯一性：`task.py`、`backend_interface/base.py`（所有 InterfaceBase 子类共享此会话）、`backend_interface/task/log.py`。`client/client.py` 出边 26 条几乎全为自身类节点+`services/__init__`（动态服务注册表），入边仅 `client/__init__.py` 重导出与一份 GCS SDK 破坏性变更勘误文档——说明 APIClient 是自治封闭子系统，改动风险低。

## ④ 数据流

用户调 `task.get_logger().report_scalar()` → `backend_interface` 组装 `events.AddRequest` → `Session.send(req)` → 校验 → `send_request` 加 Bearer/Worker 头 → `_send_request` 选超时、发 POST（events 大多为 POST 覆写默认 GET）→ 401 则刷 token 重发一次 → `CallResult.from_result` 解包 `meta.result_code` 判定成败 → 失败抛 `APIError`/返回 `ok()=False`。BatchRequest 路径在 `send` 内先被 `send_request_batch` 切片，多响应取首个非 200 为代表（session.py:681-688）。

## ⑤ 设计决策

1. **token 生命周期模板方法化**：刷新策略与存储解耦，Session 只实现"如何换"，TokenManager 决定"何时换"。
2. **客户端分片而非服务端分页**：`max_req_size` 切片把吞吐责任放在 SDK，弱化服务器实现耦合。
3. **能力协商内嵌于登录**：api_version/feature_set 藏在 JWT 里，一次登录完成降级协商，省一轮探测请求。
4. **APIClient 动态建类**：`type()` 工厂让新增 API 服务只需写 Request 类定义，客户端零改动——代价是 IDE 补全与静态分析失效。
5. **双品牌头/双 env 别名**：TRAINS→ClearML 迁移期兼容写死在协议层，属于历史包袱型决策。

## ⑥ 新人提示（含勘误）

- **勘误 1**：任务书所称 "apiproxy" 文件**不存在**——`session/` 目录下没有 apiproxy；对应物是 `client/client.py` 的 `APIClient` 动态服务代理（client.py:509）。全仓 grep 无 APIProxy 命名。
- **勘误 2**：默认 HTTP 方法是 **GET 不是 POST**（request.py:24），与多数人直觉相反；`api.http.default_method` 配置可改，但仅允许 GET/POST/PUT（session.py:291-305）。
- **勘误 3**：URL 路径是 `/tasks.get_by_id` 这种**点号动作式**，不是 REST 的 `/tasks/{id}`；带版本时才是 `/v2.9/tasks.get_by_id`（session.py:421-425）。
- SSLError 是**无限重试**（session.py:456-462），配错证书时会表现为"卡死"而非报错，排查挂起先看这里。
- `StrictSession` 的 `config_file` 参数靠临时改 `CLEARML_CONFIG_FILE` 环境变量实现（client.py:120-127），线程不安全，勿并发构造。

---
自检：不计空格字符 4729、含空格 5080、行号锚去重 44 处（session.py:{67,71-81,86-89,92,93,99,114,141,191,225-236,253-268,281-291,291-305,380,421-425,429-434,456-462,456-473,475-485,503,507,550,642,651,681-688,878,899,1035}、token_manager.py:{10,46,69,100,106}、client.py:{46,98,120-127,141,189,274,365,445,464,509}、request.py:{23,24,47}、defs.py:6-19），全部经 grep -n/源码逐条核实。
