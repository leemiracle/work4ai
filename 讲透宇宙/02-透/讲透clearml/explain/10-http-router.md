# 10 · HttpRouter：任务内 HTTP 路由与本地反向代理

## ① 角色定位

HttpRouter 解决：训练/推理任务跑在 agent 容器里，任务内部起的 web 服务（模型服务、Gradio）如何被外部访问并观测？答案是**本地反向代理 + 服务器协调的外部端点**两层。`Task.get_http_router()`（task.py:921）拿到 `HttpRouter`（router.py:8），管理"本地端口转发 + 请求/响应拦截回调 + 端点遥测"；`Task.request_external_endpoint`（task.py:983）向服务器申请把代理端口暴露成外网 URL（由 clearml-agent 的 ingress/端口映射落地）。依赖非默认：需 `pip install clearml[router]`（setup.py:89-93 extras；task.py:956-958 import 失败抛 UsageError）。官方样例 examples/router/http_router.py:33-43。

## ② 内部结构

四个文件呈清晰的单向分层：router（门面）→ proxy（薄抽象）→ fastapi_proxy（引擎）→ route（回调容器）+ endpoint_telemetry（遥测）。

**HttpRouter（clearml/router/router.py:8）**：纯门面，不含网络代码。`_proxy_params` 初始 `{"port": 9000, "access_log": True}`（router.py:50）；`set_local_proxy_parameters()`（router.py:52-76）改端口/默认目标/流式开关；`start_local_proxy()`（router.py:78-82）幂等（`self._proxy or HttpProxy(...)`）；`create_local_route()`（router.py:84-158）最常用——自动起代理（router.py:150）并把三种回调（request/response/error，均共享 `persistent_state` 字典）转给 `add_route`（router.py:151-158）；`remove_local_route()`（router.py:160）；`deploy()`（router.py:169-209）把代理端口交给 `task.request_external_endpoint`（router.py:202-208），支持 static_route 持久路由名；`wait_for_external_endpoint()`（router.py:211）与 `list_external_endpoints()`（router.py:237）补全查询面。

**HttpProxy（clearml/router/proxy.py:8）**：意图上是"可换实现的代理抽象"，`DEFAULT_PORT = 9000`（:9）；:20 注释明言 "at the moment, only a fastapi proxy is supported"，构造即把参数交给 FastAPIProxy 并立刻 `start()`（:21-29）；`add_route()`（:33-50）委托并登记 `self.routes`。

**FastAPIProxy（clearml/router/fastapi_proxy.py:18）**：真正的引擎，三处关键设计——
1. **父子进程双态**：uvicorn 跑独立 `multiprocessing.Process`（fastapi_proxy.py:257-259 → `_start()` :231-247，绑 `0.0.0.0` :243）。`add_route()`（fastapi_proxy.py:158）有双模式：父进程态只往 `SafeQueue`（fastapi_proxy.py:33，来自 utilities/process/mp.py）put 一条 RPC 消息（:167-181）即返回；子进程态才真正建 `Route`、挂 httpx.AsyncClient（:187-193）并注册路由；常驻 `_rpc_manager` 线程（:249-255）消费队列。
2. **双路由注册**：每个 source 同时注册裸路径与 `source.rstrip("/") + "/{path:path}"` 两条路由（:200-216），方法集 ALL_REST_METHODS 六动词（:19）；`remove_route` 只置 None 不 pop（:219-229——防同 source 重建时重复 add_api_route）。
3. **转发与转换**：`proxy()`（:77-98）串起 on_request → `_send_request`（:100-124，流式时 `request.stream()`+`stream=True` 直通）→ `_convert_httpx_response_to_fastapi`（:126-156，chunked 包成 StreamingResponse :127-137；上游无 content-length 时删头 :151-155，注释引 RFC 9112）。default_target 兜底走 `DefaultRouteMiddleware`（:43-75）整体转发未命中流量。

**Route（clearml/router/route.py:7）**：单条路由的回调容器。`persistent_state = {}`（route.py:21）跨请求共享给三个回调当缓存；`on_request/on_response/on_error`（route.py:76-84/:86-94/:96-102）统一处理同步与协程回调（`inspect.isawaitable` route.py:80），回调返回 None 时回退原对象。遥测参数经 `set_endpoint_telemetry_args()`（route.py:25-63）暂存、`start_endpoint_telemetry()`（route.py:65）实例化。

**EndpointTelemetry（clearml/router/endpoint_telemetry.py:11）**：serving 遥测。`Task.current_task()._resource_monitor or ResourceMonitor(...)`（endpoint_telemetry.py:84）复用已有监视器；`register_container()`（endpoint_telemetry.py:142-145）向服务器 `serving/register_container` 注册；守护线程每 30s（:48）跑 `container_status_report()`（:206-225）上报 requests_num/latency_ms/machine_stats；`BACKEND_STAT_MAP`（:12-26）把 ResourceMonitor 指标名映射成 serving 后端认的通配名。

## ③ 外部连接（图谱边证据）

图谱边完整刻画了分层：`router.py --imports--> proxy.py`；`proxy.py --imports--> fastapi_proxy.py & route.py`；`fastapi_proxy.py --imports--> route.py & utilities/process/mp.py`；`route.py --imports--> endpoint_telemetry.py`；`endpoint_telemetry.py --imports--> task.py & utilities/resource_monitor.py`；反向唯一入口 `task.py --imports--> router.py`（懒加载）。contains 边给出各文件类清单（FastAPIProxy/DefaultRouteMiddleware/EndpointTelemetry/Route/HttpProxy/HttpRouter），与源码一一对应无缺漏。

## ④ 数据流

用户 create_local_route → 父进程 put 消息 → 子进程 _rpc_manager 消费 → 建 Route + 注册 FastAPI 路由 + 启动遥测注册 → deploy() 向服务器报端口（task runtime properties 记录 endpoint）→ 外部流量进 `0.0.0.0:9000` → FastAPI 匹配 → Route.on_request（业务回调改写/计时）→ httpx.AsyncClient 转发 target_url → 响应（流式或整包）转 FastAPI Response → Route.on_response（业务回调可替换响应）→ 返回客户端；遥测线程并行每 30s 汇总 QPS/延迟/机器与 GPU 指标推给 serving 后端。

## ⑤ 设计决策

1. **代理放子进程**：uvicorn 阻塞式 serve 不能进训练进程的事件循环，multiprocessing.Process 隔离（fastapi_proxy.py:257-259）；代价是回调对象必须可 pickle 过队列。
2. **队列 RPC 而非共享内存**：SafeQueue 消息驱动（add_route/remove_route 两种 method），父进程 API 调用永不阻塞。
3. **同 source 双注册 + 置 None 不删除**：空间换时间，重建路由零成本（fastapi_proxy.py:227-229）。
4. **chunked 流式透传**：对 LLM/SSE 类响应不缓冲整包（fastapi_proxy.py:127-137），推理服务刚需。
5. **遥测复用 ResourceMonitor**（endpoint_telemetry.py:84）：机器/GPU 指标一份代码两处消费。
6. `HttpRouter._instance = None`（router.py:41）是**从未使用的单例残留**（grep 全仓无赋值以外引用）——实际"单例"由 `Task._http_router` 持有（task.py:960-962 懒创建）。

## ⑥ 新人提示（含勘误）

- **勘误 1（重要）**：模块路径是 `clearml/router/`，不少资料（含本流水线早期笔记）写的 `clearml/utilities/http_router/` **不存在**——全仓无该目录；examples/router/http_router.py 只是示例脚本。
- **勘误 2**：默认端口 9000（proxy.py:9），不是 8080/8000；examples 里 8000 是被转发的目标 webserver 端口，别混淆。
- fastapi 三件套非基础依赖，未装 extras 时 get_http_router 抛 UsageError（task.py:957-958）。
- `deploy(wait=True)` 90 秒拿不到 endpoint 返回 **None 而非抛异常**（router.py:183-193），必须检查返回值。
- remove_route 后再 create_local_route 同一 source 受支持（不会重复注册路由，fastapi_proxy.py:227）。
- 回调经 multiprocessing 传递需可 pickle；官方示例都写成模块级函数（examples/router/http_router.py:19-25）。
