# DeerFlow 2.0 新人导览（ONBOARDING）

> 基于知识图谱（653 节点/1376 边/16 层/16 步 tour，commit 76803b82）与源码逐行核实。锚点 `path:line` 全部真实核对。

## ① 项目定位与一句话总结

DeerFlow 2.0（bytedance/deer-flow）是字节开源的 **super agent harness**：电池齐全的代理运行时，开箱提供记忆、沙箱、子代理委派、技能与 MCP 工具生态。README.md:11 自述为 ground-up 重写，与 v1（`main-1.x` 分支）零共享代码——v1 是 planner/researcher/reporter 多角色 LangGraph 图，2.0 彻底抛弃该形态。一句话：**双进程（LangGraph Server 跑 agent + FastAPI Gateway 暴露 REST）+ 配置驱动（config.yaml 字符串路径反射装载一切实现类）的单主代理架构，主代理按需拆活给子代理与沙箱**。第一站文档：README → backend/docs/ARCHITECTURE.md → backend/CLAUDE.md（唯一当代准确的架构事实来源，见⑦）。

## ② 技术栈与架构总览

Python 3.12 + uv + ruff；agent 层用 **langchain v1 `create_agent` + `AgentMiddleware` 栈**（非 LangGraph StateGraph 流水线）；Gateway 为 FastAPI；前端 Next.js（图谱阶段已裁剪）。五服务拓扑：LangGraph Server :2024（`backend/langgraph.json:9` 注册 `deerflow.agents:make_lead_agent`）、Gateway :8001（`backend/app/gateway/app.py:72`）、Frontend :3000、Nginx :2026 统一入口（`/api/langgraph/*`→2024、其余 `/api/*`→8001，`docker/nginx/nginx.conf:57`）、Provisioner :8002 可选（`docker/docker-compose.yaml:125`）。后端严格分层：harness（`backend/packages/harness/deerflow/`，可发布框架包）与 app（`backend/app/`），app 可 import deerflow、反向被 `backend/tests/test_harness_boundary.py` CI 禁止；checkpointer 声明在 `backend/langgraph.json:12`。

## ③ 目录结构导览

```
deer-flow/
├── Makefile · config.example.yaml · extensions_config.example.json
├── backend/
│   ├── langgraph.json         # harness 入口（14 行）
│   ├── packages/harness/deerflow/   # ★ 框架主体（import 前缀 deerflow.*）
│   │   ├── agents/lead_agent/ # 组装工厂 agent.py + prompt.py
│   │   ├── agents/middlewares/# 磁盘 11 个 AgentMiddleware
│   │   ├── agents/memory/ · agents/checkpointer/ · agents/thread_state.py
│   │   ├── sandbox/ · subagents/ · tools/ · skills/ · mcp/ · models/
│   │   ├── community/ · reflection/ · config/
│   │   └── client.py          # DeerFlowClient（907 行）
│   ├── app/gateway/           # FastAPI Gateway（九路由）
│   ├── app/channels/          # Feishu/Slack/Telegram
│   └── docs/                  # 18 篇文档（有代差，见⑦）
├── skills/public/             # 13 个技能包 · scripts/ · docker/
```

图谱 16 层中文件量最大三层：L16 技能生态（79 文件）、L15 后端文档（22）、L03 容器运维（19）；代码核心在 L04-L11。

## ④ 核心数据流：一次研究请求的完整旅程

1. **入口**：前端 → Nginx:2026 → `/api/langgraph/*` → LangGraph Server:2024，命中 `make_lead_agent`（`backend/langgraph.json:9`）。
2. **组装**：`make_lead_agent`（`agents/lead_agent/agent.py:257`）解析请求级 configurable，`_build_middlewares`（agent.py:207）按序装中间件，`create_agent`（agent.py:328）建实例；提示词由 `apply_prompt_template`（`agents/lead_agent/prompt.py:369`）注入 skills、记忆与 subagent 编排段（prompt.py:7）。
3. **模型**：`create_chat_model`（`models/factory.py:11`）按 config 的 `use` 路径经 `resolve_class`（`reflection/resolvers.py:73`）反射实例化。
4. **工具聚合**：`get_available_tools`（`tools/tools.py:22`）三源合一——config 工具（tools.py:43）、内建交互工具（含条件 view_image，tools.py:78-82）、MCP 缓存工具（tools.py:50-64，每次读盘保证 Gateway 改配置即刻生效）。
5. **状态**：`ThreadState`（`agents/thread_state.py:48`）扩展 AgentState 七字段，两个自定义 reducer：merge_artifacts 保序去重（thread_state.py:21）、merge_viewed_images 空字典=清空（thread_state.py:31）。
6. **沙箱**：首次工具调用时 `SandboxMiddleware` 经 `get_sandbox_provider`（`sandbox/sandbox_provider.py:42`）反射装载 provider（`sandbox/middleware.py:52`）。agent 见 `/mnt/user-data/{workspace,uploads,outputs}` 虚拟路径（`config/paths.py:6`），物理落 `threads/{thread_id}/user-data/`（paths.py:94）。
7. **执行与防御**：调 `task` 工具（`tools/builtins/task_tool.py:22`）委派 `SubagentExecutor`（`subagents/executor.py:123`）；`LoopDetectionMiddleware` 指纹哈希防空转（`middlewares/loop_detection_middleware.py:36`）；澄清时 `ClarificationMiddleware`（`middlewares/clarification_middleware.py:91`）以 Command 中断。
8. **记忆沉淀**：回合后 `MemoryMiddleware` 过滤用户输入+最终 AI 回复入 `MemoryUpdateQueue`（`agents/memory/queue.py:22`），Timer 防抖（queue.py:75）触发 `MemoryUpdater.update_memory`（`agents/memory/updater.py:235`）：LLM 按 `MEMORY_UPDATE_PROMPT`（`agents/memory/prompt.py:15`）增量更新，置信度过滤（updater.py:349）+ max_facts 截断（updater.py:361-367），临时文件+replace 原子写（updater.py:196/201）。
9. **旁路**：前端直连 Gateway:8001 管理面（上传/记忆/技能/MCP）；IM 用户走 channels 线（见⑤-6）。

## ⑤ 子系统深览

**1. lead agent 工厂**（`agents/lead_agent/agent.py`，334 行枢纽）。`_build_middlewares`（agent.py:207）先装共享链 `build_lead_runtime_middlewares`（`middlewares/tool_error_handling_middleware.py:97`：ThreadData/Uploads/Sandbox/DanglingToolCall/ToolError 五件套），再按需追加 Summarization/Todo/Title/Memory/ViewImage/SubagentLimit/LoopDetection，Clarification 恒最后（agent.py:252，顺序约束注释 :200-206）；子代理用精简链（tool_error_handling_middleware.py:106）。tools import 全部延迟到函数体规避循环依赖（agent.py:258-260）。

**2. 中间件栈**（磁盘 11 文件）。体验线：thread_data 注入线程目录、title 首轮后异步生成标题（`title_middleware.py:84`）、clarification 反问、todo 计划模式；健壮性线：loop_detection、dangling_tool_call、tool_error_handling 降级、subagent_limit 截断超额并发。dangling 精妙点：选 `wrap_model_call` 而非 before_model——后者只能追加到消息末尾，无法在悬空 AIMessage 正确位置插占位 ToolMessage（`dangling_tool_call_middleware.py:11` 注释）。

**3. 沙箱**。`Sandbox` ABC 五方法契约（`sandbox/sandbox.py:4`，abstractmethod 自 :16）；`SandboxProvider` acquire/get/release（`sandbox/sandbox_provider.py:8`）。local 进程内单例+路径映射（`sandbox/local/local_sandbox_provider.py:41`，release 为 `pass` 空操作 ：54-60）；Docker 隔离 `AioSandboxProvider`（609 行 21 方法巨石类）release 有真实动作——容器停入温池等复用免冷启动（`community/aio_sandbox/aio_sandbox_provider.py:76`）。

**4. 子代理委派**。`registry.py:12` 查内建注册表（general-purpose/bash）并应用配置覆盖（disallowed_tools 默认 `["task"]` 防递归）；双线程池 `_scheduler_pool`（`subagents/executor.py:71`）+ `_execution_pool`（:75）各 3 worker，全局 `_background_tasks` 字典+锁（:67-68）。

**5. 技能与 MCP**。`load_skills`（`skills/loader.py:22`）递归扫描 `skills/{public,custom}`（loader.py:58），enabled 从 extensions_config 回填（loader.py:86）；`build_server_params`（`mcp/client.py:11`）校验 stdio 必须有 command、sse/http 走 url（:24-32）。扩展配置唯一事实来源 `ExtensionsConfig`（`config/extensions_config.py:55`）。

**6. Gateway 与 IM 通道**。Gateway lifespan（`app/gateway/app.py:32`）启动时装配置并拉起 IM 服务，**刻意不做 MCP 初始化**——双进程各自缓存（app.py:45-49 注释）；`create_app`（app.py:72）组装九路由（:153-177）+ `/health`（:179）。channels 线：`MessageBus`（`app/channels/message_bus.py:117`）asyncio.Queue 解耦 IM 与调度；`ChannelManager`（`app/channels/manager.py:311`）经 langgraph_sdk `runs.wait`（:496，Slack/Telegram）或 `runs.stream`（:554，Feishu 增量补卡片）驱动 agent；artifacts 只放行 outputs 防外泄（:253）。

**7. 嵌入式客户端**。`DeerFlowClient`（`deerflow/client.py:66`，842 行巨类 26 方法）把双进程能力折叠进进程内直调：`stream`（client.py:272）对齐 LangGraph SSE 协议、`chat`（:367）同步、`_ensure_agent`（:184）惰性建 agent 复用 make_lead_agent 组装线；返回结构与 Gateway Pydantic 模型对齐（`backend/tests/test_client.py` 77 单测）。

**8. 模型工厂**。`create_chat_model`（`models/factory.py:11`）反射实例化，thinking 快捷字段深合并（factory.py:43-47）；vision 支持性决定 ViewImage 工具链激活。

## ⑥ 配置与运行

**双配置文件驱动**。`config.yaml`（模板 `config.example.yaml`）：models 多供应商（:22 起，use 全是 `"module:Class"` 字符串）、tool_groups/tools（:155/:166）、sandbox 三模式（:234-235 默认 Local，AioSandbox :243，provisioner/k3s :278）、subagents（:290）、title（:322）、summarization（:334）、memory（:381）、channels（:430）。查找优先级：显式参数 > `DEER_FLOW_CONFIG_PATH` > backend/ > 仓根（推荐）；`$` 前缀解析为环境变量。`AppConfig`（`config/app_config.py:26`）聚合十项子配置，单例 `get_app_config`（:223）。`extensions_config.json` 管 MCP+skills，双进程共享磁盘+mtime 失效热更新。

**启动**：本地 `make dev`（Makefile:88，`scripts/serve.sh` 拉起）；Docker `make up`（Makefile:154；gateway uvicorn 双 worker compose:64，langgraph `langgraph dev --port 2024` compose:96）。首次 `make config`（Makefile:32）生成配置填 key；沙箱镜像 `make setup-sandbox`（Makefile:59）；schema 升级 `make config-upgrade`（Makefile:35）。

## ⑦ 已知坑与勘误精选（工人甄别钉版）

1. **中间件计数三方漂移**：`backend/CLAUDE.md:31` 写 "10 middleware components"，backend/README 计 9，磁盘 `agents/middlewares/` 实为 11 文件。以源码为准。
2. **文档路径代差**：backend/CONTRIBUTING.md L66-127 仍是 `backend/src/` 旧布局（磁盘无此目录），同文件后半又是新路径；`backend/docs/ARCHITECTURE.md` 引用的 `mcp/manager.py`、`sandbox/local.py` 均不存在。路径以磁盘为准，架构事实以 CLAUDE.md 为准。
3. **generate_spreadsheet 死规格**：`skills/public/chart-visualization/scripts/generate.js:6-32` CHART_TYPE_MAP 实测 25 键（末键 word-cloud :31），SKILL.md 宣称 26 选项、references/ 26 个 md——有文档无映射，按 SKILL.md 调用报 Unknown tool。
4. **release"空操作"要分层看**：`sandbox/local/local_sandbox_provider.py:54-60` release 确为 `pass`；但 `sandbox/middleware.py:66-78` after_agent **确实调用** release——与 local_sandbox_provider.py:56 "intentionally not called" 注释矛盾（注释陈旧）。AioSandboxProvider 层 release 有真实动作（温池回收），三层语义勿混。
5. **compose 注释漂移**：`docker/docker-compose.yaml:90` 注释自认 `langgraph dev` 跑生产是许可证规避临时态；dev compose 注释称默认 nginx.local.conf，实际默认挂载带 `/api/sandboxes` 路由的 nginx.conf。
6. **小笔误群**：`scripts/serve.sh` 头注释仍写旧名 start.sh；`backend/Dockerfile:28` 注释 'Copy frontend source code' 实际 COPY backend；skills `vercel-deploy-claimable` frontmatter name=vercel-deploy 名实分离。
7. **巨石与延迟 import**：client.py 与 aio_sandbox_provider.py 方法级不拆，先看类 docstring 再下钻；"函数体内延迟 import"是本仓规避循环依赖的标准手法（agent.py:258、queue.py、loader.py 均是），工具报 import 缺边先怀疑这个。

## ⑧ 上手路径（对应 16 步 tour 的阅读建议）

- **第一段·建全局（tour 1-3，半天）**：README → ARCHITECTURE.md → CLAUDE.md 立认知；langgraph.json + `app/gateway/app.py` + compose 搞清"谁在哪跑"；啃配置链 config.example.yaml → `config/app_config.py` → `reflection/resolvers.py`（95 行）——看懂 resolve_class 就能顺着任意 config 字符串找到真实实现。
- **第二段·主链路（tour 4-8，一天）**：精读 `agents/lead_agent/agent.py`（全仓枢纽）→ thread_state.py → 按体验线/健壮性线读 middlewares → memory 三件套 → checkpointer。读完应能回答"一次请求经过哪些中间件、顺序为何"。
- **第三段·执行与扩展（tour 9-14，一天）**：sandbox 契约与虚拟路径 → subagents 委派链 → `tools/tools.py` 三源聚合 → skills loader → mcp/client → community 工具范式。此段是给 agent"加手"的改造面。
- **第四段·外围与运维（tour 15-16，半天）**：Gateway 九路由 → channels 线 → serve.sh/provisioner 收尾。
- **动手验证**：`make config` 填 key → `make dev` → :2026 发一条研究请求，对照④的 9 步在日志找中间件日志行；`cd backend && make test` 过单测。改码前重读 CLAUDE.md 的 TDD 强制条款。