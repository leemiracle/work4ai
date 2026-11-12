# 03 前端入口层（front_ends）：NAT workflow 的交付面

## 一、角色定位

NAT 内核是 builder 层：workflow 把 function、LLM、tool 装配成可执行的图。front_ends 层回答的是这张图以什么形态面对外界——同一份配置换个 front_end 即从终端执行变成 OpenAI 兼容微服务或 MCP server，workflow 零改动。

注册制：`@register_front_end(config_type=...)`（fastapi `register.py:21`、console `console/register.py:21`），经 entry point 组 `nat.front_ends` 发现（`runtime/loader.py:142`）。CLI start 为每个注册项动态生成子命令，`build_fn` 生成插件并调 `run()`（`start.py:231`）。基类 `FrontEndBase`（`builder/front_end.py:26`）契约极小：唯一抽象方法 `run()`。

勘误一：front_ends/cron/ 目录是空壳——`cron/__init__.py` 全文 14 行只有 license 头，本版本没有 cron 前端代码。

勘误二（重要）："plugin 建 app、controller 分发、worker 执行"三分法与源码不符：plugin 是父进程编排者，不建 app；app 由 worker 在 uvicorn 子进程构建（`fastapi_front_end_plugin_worker.py:103`）。`fastapi_front_end_controller.py:26` 的 `_FastApiFrontEndController` 也不做请求分发，而是 OAuth 回调临时服务器的生命周期管理器——console（`authentication_flow_handler.py:266`）与 MCP 包（`auth_flow_handler.py:209`）用它拉起 redirect 服务器。

## 二、内部结构

**FastAPI plugin：父进程编排。** `FastApiFrontEndPlugin(DaskClientMixin, FrontEndBase[...])`（`fastapi_front_end_plugin.py:41`）的 `run()`（`:76`）做三件事：一是异步作业底座——dask 缺失则降级（`:138`），`scheduler_address=None` 时建 `LocalCluster`（`:122`，n_workers=max_running_async_jobs+1，多出的跑清理任务），否则连外部集群；二是跨进程传配置——config dump 成临时 YAML 写入 `NAT_CONFIG_FILE`（`:173`），worker 类名写入 `NAT_FRONT_END_WORKER`（`:176`）；三是启动 uvicorn（factory=True 指向 get_app，`:201`），darwin/linux 强制 `loop="asyncio"` 给 MCP 子进程留 child-watcher（`:184`）。

**get_app：worker 进程入口。** `main.py:31` 读环境变量，动态加载 worker 类后 `build_app()`（`main.py:57`）——中转设计让 uvicorn 多 worker/reload 的子进程不依赖父进程内存。

**Worker 双层与路由装配。** `FastApiFrontEndPluginWorkerBase`（`fastapi_front_end_plugin_worker.py:59`）给抽象契约，默认实现 `FastApiFrontEndPluginWorker`（`:210`）。builder 构建被推迟到 app lifespan：`WorkflowBuilder.from_config`（`:111`）随 `FastAPI(lifespan=...)`（`:129`）启动执行。`add_routes`（`:338`）先挂 auth/execution/monitor/health/static，eval 与 MCP client 工具清单路由是 try-import 可选件（`:351-360`），再对 `endpoints` 每项建 SessionManager（`:366`）挂三族路由。

**路由面。** 默认端点组在 `fastapi_front_end_config.py:331`：`/v1/workflow`、`/websocket`、`/v1/chat`、`/v1/chat/completions`（openai v1）与 legacy `/generate`、`/chat`。`add_chat_routes`（`routes/chat.py:93`）：两路径重叠时只注册 v1 单路由（`:110`），由 `add_v1_chat_completions_route`（`routes/v1_chat_completions.py:142`）落一个同时吃 `stream=True/False` 的端点（`:107`）。generate 族另派生 `/stream`/`/full`/`/atif`（`routes/generate.py:262`）。HTTP HITL/OAuth 走 execution 路由（`routes/execution.py:127/139`：状态查询与交互响应提交）。异步作业是 `{path}/async` 与 `/async/job/{job_id}`（`routes/async_generation.py:155`）。

**支撑件。** `ExecutionStore`（`execution_store.py:84`）进程内 TTL 存档默认 600 秒（`:37`）；`HTTPInteractiveRunner`（`http_interactive_runner.py:55`）把交互执行包成"202+轮询"；`StepAdaptor`（`step_adaptor.py:35`，process `:292`）把中间步骤整形为 OpenAI chunk；WebSocket 循环由 `WebSocketMessageHandler`（`message_handler.py:89`）承担；异步作业底座见数据流第 5 步。

**console 与 simple_base。** `SimpleFrontEndPluginBase`（`simple_base/simple_front_end_plugin_base.py:31`）是自定义前端最小模板：`run()` 依次 `pre_run` → `WorkflowBuilder.from_config`（`:41`）→ `SessionManager.create`（`:50`）→ 抽象 `run_workflow`。`ConsoleFrontEndPlugin`（`console/console_front_end_plugin.py:100`）是其最小完整实现，HITL 回调 `prompt_for_input_cli`（`:62`）用 `select.select` 做倒计时输入；`run_workflow`（`:130`）包住 query 或输入文件执行。

## 三、外部连接

上游是 YAML Config 与 CLI；协作方 `WorkflowBuilder` 与 `SessionManager`——前端不碰 workflow 内部，只经 session.run 拿 Runner。下游是 uvicorn/gunicorn、dask + SQLAlchemy、任意 OpenAI 兼容客户端。横向：`nvidia_nat_eval` 与 `nvidia_nat_mcp` 的路由都是可选拼装（`fastapi_front_end_plugin_worker.py:357`）。安全面注意 `identity_header` 与 JWT 凭据配置的互斥校验（`fastapi_front_end_config.py:318`）。

## 四、数据流：POST /v1/chat/completions（stream=true）

1. worker 进程 lifespan 已建好 builder 与 SessionManager（`fastapi_front_end_plugin_worker.py:111`）。
2. 请求命中 `post_openai_api_compatible`（`routes/v1_chat_completions.py:107`）走流式分支。
3. 开会话后进 `generate_streaming_response_as_str`（`response_helpers.py:35`）：`StepAdaptor.process`（`step_adaptor.py:292`）把中间步骤转成 `ChatResponseChunk`，SSE 逐块输出。
4. 若触发人工交互且开 `enable_interactive_extensions`：改走 `HTTPInteractiveRunner`，返回 202 与 execution_id 并挂起 Future；客户端 POST 响应后 `resolve_interaction`（`execution_store.py:194`）唤醒执行。
5. 异步变体：`POST /v1/workflow/async` → `JobStore.submit_job`（`job_store.py:280`）→ dask `run_generation` → 轮询 `/async/job/{job_id}`。
6. WebSocket 形态由 `websocket_endpoint`（`routes/websocket.py:70`）进消息循环；断线重连靠按 `(user_id, conversation_id)` 缓存的 handler。

## 五、设计决策

1. 父子进程分工 + 环境变量传配置：plugin 只编排、服务进程独立 get_app，兼容多 worker 与热重载。
2. 配置即路由：`endpoints` 逐项生成 SessionManager 与三族路由，一份配置可暴露多个入口。
3. OpenAI 兼容分三代路径、v1 单路由吃 stream 双态（`routes/chat.py:110`）、legacy 可关——兼容包袱显式化。
4. dask 可选依赖三态降级；状态存储按生命周期分级——HTTP HITL 短命状态进进程内存（TTL 600 秒），async job 元数据跨进程进 DB。
5. worker 双层抽象给 `runner_class` 留覆盖口（`fastapi_front_end_plugin.py:60`）——MCP 前端原样复用这一模式（见 05 篇）。

## 六、新人提示

- 读路由先读 `fastapi_front_end_config.py:331` 默认端点组；起服务先 `GET /health`（`routes/health.py:36`）。
- 配置覆盖链：YAML `general.front_end` 为基，CLI 只覆盖非默认值（`start.py:213`）；`db_url` 不配则临时 SQLite。
- 写自定义前端从 `simple_front_end_plugin_base.py`（58 行）起步，console 是最小完整参考。
- cron 目录别找定时功能（勘误一）；controller 不是分发器（勘误二）。
- MCP 前端与本篇同族，`MCPFrontEndConfig(name="mcp")` 同走 `nat.front_ends` 注册组，详见 05 篇。
