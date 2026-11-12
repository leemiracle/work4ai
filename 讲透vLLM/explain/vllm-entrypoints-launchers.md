# vllm/entrypoints/launchers/ — 新一代启动器：server 形态组装车间与 HTTP 承载内核

> 源码：`vllm/entrypoints/launchers/`（17 个文件约 3300 行，launcher.py 393 行领衔）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`launchers/` 是 2026-08~09 服务入口换代的产物：#52131/#53500/#53659/#56746 四连迁移把原 openai/ 目录与 entrypoints 根下的巨石入口搬出成独立包（代差考证见 api_server 垫片篇）。它处在 **CLI 层**与**协议实现层**之间：上接 `vllm/entrypoints/cli/serve.py` 的形态选择树，下接 entrypoints/{serve,openai,generate,pooling,speech_to_text} 的路由与 handler，职责是"进程形态组装"——起 HTTP/gRPC/DP 监督者/CPU 渲染/离线批哪种形态，并把 `EngineClient`（AsyncLLM）与对应 server 缝合。注意**命名陷阱**：launcher.py 不是总调度器——形态选择树在 vllm/entrypoints/cli/serve.py:54（ServeSubcommand.cmd），launcher.py 只是 HTTP 承载内核；单形态启动编排在 api_server/entry.py。

## ② 内部结构

四层。**底座 launcher.py**：`NoSignalServer`（:47）继承 uvicorn.Server，`capture_signals` 刻意空实现（:70-72）拒绝 uvicorn 自装 SIGINT/SIGTERM（#49668）；`serve_http`（:177）是唯一 HTTP 服务函数；`watchdog_loop`（:315）每 5s 查引擎死活，`terminate_if_errored`（:326）受 `VLLM_KEEP_ALIVE_ON_ENGINE_DEATH` 豁免（:335）；`create_server_socket`（:341，SO_REUSEPORT 可选 :353）与 unix 版（:359）；`setup_server`（:366）校验+**先绑端口再建引擎**（:373-375，规避 ray 竞态 #8204）+`set_ulimit`（:384）。

**HTTP 主形态 api_server/**：entry.py 是启动编排（链条见④）：`build_async_engine_client`（:34，asynccontextmanager，forkserver 预导入 :41-48）→`AsyncLLM.from_vllm_config`（:94）→`build_and_serve`（:115）→`run_server`（:164）→`run_server_worker`（:179，多 worker 时取共享负载表 :186-188）→`main`（:204）。app.py 的 `build_app`（:19）仅 56 行：骨架+`register_api_routers`（:45）+endpoint 插件（:51）+异常/中间件/sagemaker bootstrap（:53-55）。app_state.py 的 `init_app_state`（:24）注入 engine_client（:63）、`OpenAIServingModels`（:81）、Online 双渲染器（:88/:107），按 supported_tasks 条件初始化各任务 serving（:134-160）。routers.py（:12）按任务条件挂路由。

**多形态与 utils**：vllm/entrypoints/launchers/grpc_server.py（`serve_grpc` :56，servicer 来自外部包 smg-grpc-servicer :27-40）；dp_supervisor.py（`DPSupervisor` :269+`run_dp_supervisor` dp_supervisor.py:562，多端口外部 LB 监督者）；render/（CPU-only 渲染，vllm/entrypoints/launchers/render/entry.py:82-98 绕过 create_engine_config 手工拼 VllmConfig：quantization 置 None、KVCACHE_SPACE=0）；run_batch.py（1125 行离线批，唯一不走 HTTP）。utils/ 的 `lifespan`（vllm/entrypoints/launchers/utils/server_utils.py:76，周期拉 stats+`freeze_gc_heap` :94+退出 `del app.state` :109）、`SSLCertRefresher`（vllm/entrypoints/launchers/utils/ssl.py:19）、h11 限额默认（vllm/entrypoints/launchers/utils/constants.py:6-7）。

## ③ 外部连接

- **上游**：vllm/entrypoints/cli/serve.py:19-21（run_server/run_dp_supervisor/create_server_socket）；vllm/entrypoints/cli/launch.py:15（`vllm launch render`）；vllm/entrypoints/cli/run_batch.py:28（run-batch）；`vllm/v1/utils.py:509` 的 `run_api_server_worker_proc`（vllm/v1/utils.py:518 import run_server_worker）——多 API server 的 spawn worker 入口。
- **下游**：`AsyncEngineArgs.from_cli_args`→`create_engine_config`（vllm/entrypoints/launchers/api_server/entry.py:82）→`AsyncLLM.from_vllm_config`（vllm/entrypoints/launchers/api_server/entry.py:94）经 `EngineClient` 协议（vllm/engine/protocol.py）；路由侧惰性 import（vllm/entrypoints/launchers/api_server/routers.py:18/:56/:88）；渲染侧 vllm/renderers。
- **兄弟垫片**：vllm/entrypoints/openai/api_server.py（59 行）、vllm/entrypoints/grpc_server.py（27 行）、vllm/entrypoints/openai/run_batch.py（37 行）re-export 本包，仓内新代码零依赖。

## ④ 数据流

```
vllm serve → ServeSubcommand.cmd @vllm/entrypoints/cli/serve.py:54
  ├─ --grpc ──────────→ serve_grpc @vllm/entrypoints/launchers/grpc_server.py:56
  ├─ multi-port 外部 LB → run_dp_supervisor @vllm/entrypoints/launchers/dp_supervisor.py:562
  │    run :287 → spawn 子进程 dp_supervisor.py:397（回环 :252→run_server :241；
  │      端口=port+rank :122）
  │    → /health 探针 dp_supervisor.py:411 全绿才起 supervisor 自己的 /health :321
  │    → ready 后任一失败 → 全树 SIGTERM+kill_process_tree dp_supervisor.py:516
  ├─ api_server_count<1 → run_headless @vllm/entrypoints/cli/serve.py:181（纯引擎无前端）
  ├─ count>1 / rust 前端 → run_multi_api_server @vllm/entrypoints/cli/serve.py:269
  │    setup_server(reuse_port) :298 → bind_engine_zmq_listeners :333
  │    → launch_core_engines :336 → APIServerProcessManager @vllm/v1/utils.py:167
  │      spawn ApiServer_{i} @vllm/v1/utils.py:250（负载表 RawArray @:218）
  │      → run_api_server_worker_proc @vllm/v1/utils.py:509 → run_server_worker @vllm/entrypoints/launchers/api_server/entry.py:179
  └─ 默认单进程 ────────→ run_server @vllm/entrypoints/launchers/api_server/entry.py:164
       setup_server @vllm/entrypoints/launchers/launcher.py:366 先绑 socket
       → build_async_engine_client @vllm/entrypoints/launchers/api_server/entry.py:34（AsyncLLM 上下文管理器）
       → build_and_serve @vllm/entrypoints/launchers/api_server/entry.py:115：get_supported_tasks :132
            → build_app @vllm/entrypoints/launchers/app.py:19 → init_app_state @vllm/entrypoints/launchers/api_server/app_state.py:24
            → serve_http @vllm/entrypoints/launchers/launcher.py:177
       请求期：uvicorn → lifespan @vllm/entrypoints/launchers/utils/server_utils.py:76
            → 路由 handler → EngineClient.generate → SSE 流回
关停：SIGTERM @vllm/entrypoints/launchers/launcher.py:288 → handle_shutdown :262
  （timeout==0 → "abort" 否则 "drain" :266-267）
  → engine_client.shutdown 投线程池 :275 → server.should_exit
```

## ⑤ 设计决策

1. **形态选择树放 CLI 不放 launchers**：vllm/entrypoints/cli/serve.py:83-105 三种 LB 模式互斥校验，:113-130 推默认 api_server_count（内部 LB=DP size、hybrid=local、其余=1），:147-156 四路分发——launchers 只提供"形态函数"，Python 与 Rust 前端（:151→`RustFrontendProcessManager` :354）共享同一棵树。
2. **信号所有权归自己**：空 capture_signals（:70-72）+自管 shutdown_event（:251-289），watchdog（:315）补 StreamingResponse 生成器内异常杀不死 server 的盲区。
3. **peer_loads 最小负载接受**：多 worker 共享同一 socket 时，RawArray（vllm/v1/utils.py:218 建、vllm/entrypoints/launchers/api_server/entry.py:186-188 传入）让每 worker 发布连接数，忙者让出最多 5 次×1ms（:41/:109-112），未启动者恒为 `_NOT_ACCEPTING`（:44）永不中签——修正 asyncio"谁先醒谁全收"的倾斜。
4. **端口先于引擎**（:373-375）+CancelledError 时反查占用进程打印 cmdline（:294-305），把"端口被占"变成可读诊断。
5. **DP 监督者"迟开健康口"**：supervisor 的 /health 等全部子 /health 绿了才开（vllm/entrypoints/launchers/dp_supervisor.py:304-309），防 K8s 探针在初始化期拿 503 被误杀；ready 后任一失败即整体退场（dp_supervisor.py:447-455）。
6. **render 形态彻底去引擎化**：vllm/entrypoints/launchers/render/app_state.py:119 直接 `state.engine_client = None`，插件拿 None 自理（:124-126 注释）；entry 三处 CPU 特化让 VllmConfig 不进 GPU 校验。
7. **路由惰性 import+条件挂载**：routers.py 按 SupportedTask 分支（generate :55/transcription :80/pooling :87/fault-tolerance :92），最终 app 面由引擎任务探测结果决定。

## ⑥ 新人提示

- 读码顺序：vllm/entrypoints/cli/serve.py:54 → vllm/entrypoints/launchers/api_server/entry.py:164-201 → vllm/entrypoints/launchers/launcher.py:177 → vllm/entrypoints/launchers/app.py:19 → vllm/entrypoints/launchers/api_server/routers.py:12，一条线读完启动链。
- **别在 launcher.py 找路由/业务**——纯承载层；`/v1/chat/completions` 的 handler 在 vllm/entrypoints/openai/chat_completion/ 的 api_router 里。
- 进程名定位：`ApiServer_{i}`（vllm/v1/utils.py:250）与 `APIServer_DP{rank}`（vllm/entrypoints/launchers/dp_supervisor.py:260）；supervisor 端口与子端口重叠会硬报错（:108-115）。
- gRPC 形态默认 50051（vllm/entrypoints/launchers/grpc_server.py:192），可选依赖 `pip install vllm[grpc]`（:35-40）。
- 挂自定义端点走 endpoint plugins（vllm/entrypoints/launchers/app.py:51），别改 build_app。
