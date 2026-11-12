# router/app.py — Token-aware Router 精讲

> 源文件：`/data/usershare/ai/inference/xinference/router/app.py`（970 行；协作者 classifier/runtime/tokenization/admission/config/control_plane。HEAD b3de260 已无老版 `router/router.py`）

## 1. 角色定位

11 层图谱中属 **layer:router**，是**独立进程的 OpenAI 兼容数据面**（docstring 自述）：一个逻辑模型挂多个物理后端（各带 model_uid 与 max_context_tokens），按**请求 token 预算**分发。入口 `router/service.py` `main()`（105）以 `--supervisor-url/--router-uid` 拉控制面配置，或 `--config` YAML 单机跑（app.py `main()`:950）。supervisor 侧 `resolve_token_router_runtime`（supervisor.py:5814）按 round-robin 游标轮选 ready 实例（5846-5850）。

## 2. 内部结构

- **`create_app(config)`**（150）：组装 `RouterMetrics`、`RouterRuntime`；`lifespan`（155-215）在 `runtime.start()` 成功后才 `control_plane.ack(revision)`，关停时 cancel→unregister→drain。
- **五个端点**：`/healthz`（237）、`/readyz`（253）、`/metrics`（268）、`/v1/models`（291）、`POST /v1/chat/completions`（311-945，约 630 行核心）。
- **chat 分相**：`runtime.acquire()`（349，disabled→503）→`_authorized`（100）→模型名须在 `{logical_model, *model_aliases}`（443）→能力闸（tools/thinking 不在 `tokenizer_asset_capabilities` 直接 400，465-482）→`tokenization.estimate`（484）→`policy.classify`（487）→后端闸 `gates[decision.pool].acquire()`（623）→httpx 转发。

## 3. 外部连接

图谱边：出边 imports 指向 router 包内 10 个模块，入边仅 `router/service.py`。跨层连接在运行时：上游 `api/restful_api.py` 经 supervisor 解析后 httpx 打进来（restful_api.py:3374-3395），并反向 import `router/credentials.py`；下游后端是另一组 Xinference API（`config.backend_url`，app.py:669）。控制面 `RouterControlPlaneClient` 与 supervisor 间是 register/heartbeat(30s)/ack/get_config(5s 轮询) 协议（138/173/199/288）。

## 4. 数据流：一次请求的分发

1. 客户端→supervisor API 命中虚拟模型→代理进 Router（两级代理链）。
2. **token 计量**：`estimate`（tokenization.py:150）把 payload 交 spawn 进程池 worker 做真实 chat-template 渲染+编码，产出 `TokenBudget`（tokenizer.py:19：prompt/output/reserve/total_tokens+enable_thinking）；池忙则 429（app.py:501-526）。
3. **路由决策**：`classify`（classifier.py:218）按 priority 降序首条匹配（188-190），维度 `total_tokens_gte/lte、thinking、tools_present、stream`（config.py:65-70）；`_execute`（193）校验后端 `max_context_tokens`，超限 `ContextLimitExceeded`→400；旧短/长阈值参数归一化为同一规则链（152-178）。
4. **准入转发**：`CapacityGate.acquire()`（admission.py:42，满则 429+`retry-after`）；改写 `backend_payload["model"]=backend.model_uid`（668）——逻辑名→物理名在此发生；头部经 `backend.py request_headers`（34）白名单转发并注入后端 Bearer key。
5. **回程**：流式 `aiter_raw` 透传+断连检测（767-770），清理链 finish metrics→aclose→gate.release→runtime.release 用 `asyncio.shield`+`BackgroundTask` 恰好一次（725-761）；响应头附 `x-xinference-router-*`（138-147）；超时 504（888）、连接失败 503（912）。

## 5. 设计决策

- **token-aware**：按请求计数的均衡对 LLM 失真——100 与 100k token 成本差百倍；按 prompt+输出预留的预算路由，短请求走小上下文便宜后端，thinking/tools/stream 是一等匹配维度而非权重。
- **tokenization 进程隔离**：HF tokenizer 渲染 CPU 密集持有 GIL，spawn 池才不卡事件循环；worker 启动自证无凭据残留且资产指纹一致（tokenization.py:94-148），`BrokenProcessPool` 自动换池（226）。
- **确定性规则优于打分**：first-match 可审计——rule_id/reason 进日志与响应头，可精确复盘，配置可热更。
- **不可变快照热更新**：`RouterRuntime.apply`（runtime.py:152）建新快照、drain 旧快照（等 `active_requests` 归零），在途请求永见旧配置；revision-ack 让 supervisor 知道哪版就绪。
- **背压即显式拒绝**：两级闸以 429 拒绝而非无限排队，fail-closed 把过载尽早暴露。

## 6. 新人提示

- 别混两个"路由"：supervisor `get_model` 副本轮询是 core 层调度；本目录管"逻辑模型→物理后端"。
- 阅读顺序：`chat_completions`→classifier→runtime→tokenization；`RouteDecision.pool` 只是 backend_id 别名（classifier.py:87）。
- 调试三处：`x-xinference-router-*` 响应头、`route_decision/route_rejected` 日志、`/healthz` 快照。
- thinking 两道检查：`_payload_thinking`（app.py:110）渲染前预拒，`budget.enable_thinking`（492）权威判定，改逻辑须两处同步。
- 单机实验 `python -m xinference.router.service --config x.yaml`；托管模式两参数必须成对（service.py:82-84）。
