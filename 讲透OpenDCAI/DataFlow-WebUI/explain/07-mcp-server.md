# 07 · MCP Server 线：把后端变成 Agent 的工具箱

## 角色定位

`backend/app/mcp_server.py`（168 行）是整个"Agent 驱动 DataFlow"故事的协议转换层：它把 FastAPI 已有的 REST 端点原封不动地包装成 MCP（Model Context Protocol）工具，让 Claude Code / Codex / Cursor 不写一行 HTTP 代码就能列算子、建 pipeline、触发执行、回读结果。实现路径不是手写 MCP server，而是用 `fastapi_mcp.FastApiMCP` 库扫描 app 的路由——每个 FastAPI 路由的 `operation_id` 就是一个 MCP 工具名（mcp_server.py L25-52）。与之配套的两个部件同样属于这条线：`backend/app/api/v1/handlers.py` 里的 MCP 协议路径豁免（防止 WebUI 错误信封污染 JSON-RPC 响应），以及 `installers/configure_agent.sh` + `installers/lib/mcp_json_config.py` 负责把 server 地址写进三家 agent 的客户端配置。

## 内部结构

**白名单 20 个操作。** `create_mcp_server(app)` 的核心是一个 `include_operations` 列表（mcp_server.py L30-51），逐条注释了每个工具的用途与调用纪律：`list_operator_categories` 被标注为"便宜入口，agent 必须先调"（L31），`get_dataset_preview` 被标注"必须在设置 lang 等语义参数前调用，agent 凭样本判断数据语言"（L45）。数一下正好 20 项，其中 19 个指向既有 REST 端点的 operation_id，只有 1 个例外——`render_pipeline_in_editor` 是 mcp_server 自己现场注册的路由。这个白名单是安全边界：危险操作（删除 dataset、kill 任务）一个都没进来。

**自定义 render 工具。** `_register_render_pipeline_route(app)`（L61-129）在 FastApiMCP 扫描之前先把 `POST /api/v1/agent/render` 注册成带 `operation_id="render_pipeline_in_editor"` 的路由（L77-88），然后 FastApiMCP 自动把它暴露为 MCP 工具。工具行为：按 pipeline_id 取配置，调 `_config_to_vue_flow` 转成 Vue Flow 节点边（L132-163，默认水平布局 `location = [250*i+100, 200]`，L145），再通过 WebSocket 推给前端。注意 L90-91 两行**函数体内延迟导入**：

```python
from app.core.container import container
from app.api.v1.endpoints.agent import ws_manager, agent_manager
```

这是刻意的：`endpoints/agent.py` 顶部 import 了完整的 agent 适配器栈（claude/codex/cursor 三家 CLI 包装），如果模块级导入，任何只想要 MCP 工具定义的进程都被迫拖起整条重依赖链。推送策略也有讲究：优先 `agent_manager.get_last_active_user_id()` 定向推给"最近发起对话的用户"，避免串扰其他浏览器窗口，仅在无活跃用户时回退广播（L111-123）。`_last_active_user_id` 的维护在 `agent_session.py` L277（每次 chat_stream 更新）、L381-382（读取）。

**协议路径豁免。** handlers.py L12-17 的 `_is_protocol_path` 判断 `request.url.path.startswith("/mcp")`。三个异常处理器——参数校验（L34-48）、HTTP 异常（L50-64）、未捕获异常（L66-77）——全部先查它：MCP 路径返回原生 HTTP 状态码 + 原生 JSON 结构，非 MCP 路径一律包成 `ApiResponse` 信封且**无论什么错误都返回 HTTP 200**（L31-32 注释"关键：无论什么错误，都返回 200"，真实状态在 body 的 `success`/`code` 字段）。没有这层豁免，Cursor 这类严格校验 JSON-RPC 2.0 格式的客户端会直接拒绝信封化的响应。这条修复来自 branch-audit 记录的 `skills-agent` 分支（`c6fbcfe` "fix(api): keep /mcp responses as raw JSON-RPC"，经 PR #84 进 main）。

## 外部连接

- **上游**：`app.main:create_app` 在 L41 调 `create_mcp_server(app)`，且注释明示"必须在 StaticFiles catch-all 之前注册，否则 /mcp 请求被静态文件拦截"（main.py L40）——挂载顺序是正确性约束而非风格偏好。
- **下游消费者**：`.mcp.json`（仓库根）声明 `{"mcpServers":{"dataflow":{"type":"sse","url":"http://localhost:8000/mcp"}}}`，Claude Code 从启动目录读它。URL 不是硬编码在脚本里：`installers/config.sh` 定义 `DF_PORT`/`DF_MCP_PATH`/`DF_MCP_URL`（默认 `http://localhost:8000/mcp`），configure_agent.sh 与文档全部引用该变量。
- **配置写入线**：`./install.sh configure-agent --agent claude`（configure_agent.sh L236-251）把目标定为 `$DF_REPO_ROOT/.mcp.json`（L244），内容由 `merge_mcp_json`（L158-183）产出——它调 `installers/lib/mcp_json_config.py`：先验证 JSON 可解析（不可解析退出码 3，绝不回写）、拒绝把已有指向别处的 dataflow 条目改向（退出码 4，须 `--force`）、保留其他 server 与条目内用户附加键。Codex 走 `codex_config.py` 的 TOML 版同套规则。
- **CI 对账**：`installers/checks/check_mcp_whitelist.py` 用 `ast`（不 import 任何东西，无 FastFlow 依赖也能跑）同时解析 mcp_server.py 的 `include_operations` 列表与 `backend/app/api` 全部路由装饰器的 `operation_id`，报告白名单里有而路由不存在的名字——防止"端点改名后 agent 调用工具时才发现 tool not found"。

## 数据流

以 agent 建一条 pipeline 为例：agent 先调 `list_operator_categories`（GET，带 use_for/not_for 指引）→ `get_dataset_preview` 看样本 → `create_pipeline` → `validate_pipeline_config` → `execute_pipeline_async` 拿 task_id → 轮询 `get_execution_status` → 最后 `render_pipeline_in_editor`，后端把 `{type: "sync_pipeline", pipeline, nodes, edges}` 经 WebSocket 推给前端，画布即时刷新（mcp_server.py L100-108，注释明确"前端 renderPipeline() 用的是完整 config，nodes/edges 只是旧消费者的兼容字段"）。MCP 传输本身走 SSE（JSON-RPC 2.0 over text/event-stream），这也是 harness profile 验证命令用 `curl -H 'Accept: text/event-stream' http://localhost:8000/mcp` 的原因。

## 设计决策（含批判）

**用 operation_id 白名单而非自动暴露全部路由**——正确的最小暴露。FastApiMCP 默认会把所有路由变成工具，这里反过来列名单，把删除类、kill 类端点挡在外面。批判：白名单是纯字符串，靠 check_mcp_whitelist.py 的 AST 对账兜底，若有人给路由起了重复 operation_id（仓库历史上确有同名路由处理器的代码味道），对账只查"存在性"不查"唯一性于路由侧"（重复只在白名单内部查，check 脚本 dupes 检查的是 whitelist.count>1）。

**错误信封双轨制**——WebUI 一律 200 + 业务码，MCP 路径保持原生语义。这是对"前端依赖统一信封、协议客户端依赖标准错误格式"两类消费者的诚实妥协。批判：双轨逻辑散在三个 handler 的 if 分支里，新增 handler 忘记调 `_is_protocol_path` 就会回归——豁免没有被抽成装饰器或中间件，是靠纪律维持的。

**render 工具用延迟导入规避重依赖**——务实。批判：`_config_to_vue_flow` 生成的 nodes/edges 已沦为"兼容字段"（L105 注释），真实渲染走 `pipeline.config`，意味着这段 32 行的布局代码是事实死代码的第二生命，将来要么前端彻底不读 nodes/edges 后删除，要么继续背着。

## 新人提示

1. 加新 MCP 工具的完整动作是三步：给端点写唯一 `operation_id` → 在 include_operations 加名字 → 跑 `python3 installers/checks/check_mcp_whitelist.py` 对账；漏第二步工具不可见，漏第一步 CI 会拦。
2. 调试 MCP 连不上时按序查：backend 是否起来（`curl -sf http://localhost:8000/api/v1/datasets/`）→ `.mcp.json` 的 URL 是否与 `DATAFLOW_PORT` 一致 → 是否误把 MCP 响应当成了坏信封（看 handlers 的豁免分支是否覆盖你新加的异常类型）。
3. `get_mcp_instance()`（L166-168）返回全局单例仅供调试；不要在生产代码里依赖它拿 app 引用。
4. 改 render 推送行为时记得 `agent_manager` 的 last-active 语义是"最近一次 chat_stream 的 user_id"（agent_session.py L145 注释），不是"当前连接者"——浏览器 A 聊过天、浏览器 B 打开画布时，render 结果会推给 A。
