# routers.py 精讲——FastAPI 8 端点路由层（工作流 REST 契约与每请求实例陷阱）

## ① 角色定位

`workflows/backend/routers.py`（119 行）是 backend 四件套（api.py/routers.py/service.py/views.py）的路由层：一个 `APIRouter(prefix='/api/workflows')`（L19）挂 8 个端点，把 HTTP 请求翻译成对 `WorkflowService` 的调用。它是 L09「backend FastAPI 服务与 REST 契约」层的全部表面——ui 前端（api.py L12 的 CORS 白名单 localhost:5173）与扩展都经这份契约管理工作流与任务。

装配在 `api.py`：FastAPI 实例 + CORS + `app.include_router(router)`（L19），可独立 `uvicorn api:app` 跑（127.0.0.1:8000，L24）。routers 本身极薄，但 **L22-23 的 `get_service()` 藏着全仓最值得引以为戒的架构缺陷**（见⑤）。

## ② 内部结构

8 端点一览（全部 async，无依赖注入）：

| 端点 | 行号 | 功能 | response_model |
|---|---|---|---|
| GET `/api/workflows` | L26-30 | 列工作流文件名 | WorkflowListResponse |
| GET `/api/workflows/{name}` | L33-36 | 读工作流内容（YAML→JSON） | str |
| POST `/api/workflows/update` | L39-42 | 按 nodeId 替换单个步骤 | WorkflowResponse |
| POST `/api/workflows/update-metadata` | L45-48 | 更新 name/description/version/input_schema | WorkflowResponse |
| POST `/api/workflows/execute` | L51-86 | 异步启动执行，返回 task_id | WorkflowExecuteResponse |
| GET `/api/workflows/logs/{task_id}` | L89-101 | 从 position 增量读日志 | WorkflowLogsResponse |
| GET `/api/workflows/tasks/{task_id}/status` | L104-110 | 查任务状态 | WorkflowStatusResponse |
| POST `/api/workflows/tasks/{task_id}/cancel` | L113-119 | 取消任务 | WorkflowCancelResponse |

`get_service()`（L22-23）是两行工厂：`return WorkflowService()`——每次调用新实例。

execute 是唯一有实质逻辑的端点：校验 name（L57-58）与文件存在（L60-62）→ uuid task_id + `asyncio.Event`（L65-66）→ 注册进 `service.cancel_events`（L67）→ 记录日志偏移 `log_pos`（L68）→ `asyncio.create_task` 派后台协程（L70-71）→ `add_done_callback` 收尾清理两个 dict（L72-77，lambda 里两个 `pop` 组元组绕开单表达式限制）→ 返回 task_id/log_position（L78-84）；异常统一 500（L85-86）。

logs 端点拿 `service.active_tasks.get(task_id)` 的 TaskInfo（status/result/error，views.py L7-11）组装响应（L92-100），找不到时 status 给 'unknown' 而非报错；cancel 仅在 service 返回 `Task not found` 时转 404（L117-118）。

## ③ 外部连接

- **上游消费者**：ui 前端（workflow-layout/play-button 等经 `ui/src/lib/api` 走这份 REST）与 extension sidepanel；openapi.json 由 FastAPI 自动生成（`npm run get-openapi` 拉取）。
- **下游依赖**：`WorkflowService` 承载全部实现——文件系统 CRUD（./tmp 下 *.workflow.json/yaml/yml）、`run_workflow_in_background`（service.py L164-266：`Workflow.load_from_file` + `run(inputs, close_browser_at_end=True, cancel_event=...)`）、日志三件套（全局单文件 ./tmp/logs/backend.log）、`get_task_status`/`cancel_workflow`。
- **执行引擎挂钩**：service 持 `ChatBrowserUse(model='bu-latest')` + `Browser()` + `WorkflowController()`（service.py L45-48）传给 Workflow——backend 是 workflow_use 引擎的宿主；cancel_event 从 HTTP 层透传到 `Workflow.run`（service.py L200），协作式（set 事件自检）+ 强制（`task.cancel()`，service.py L256-257）双通道。

## ④ 数据流

一次「执行并观察」的完整时序：

1. **POST execute** `{name, inputs}` → 校验 → task_id=uuid4 → 在**本请求专属 service 实例**注册 cancel_event/task → 返回 `{success, task_id, log_position}`。log_position 是执行前 backend.log 字节偏移，前端以此为起点拉增量。
2. **后台协程**（闭包持有同一实例）：active_tasks[task_id] 置 running → 写启动日志 → 双重 cancel 检查（service.py L179/L195）→ 加载工作流 → `Workflow.run` → 逐步写 Completed step 日志 → 状态机 running→completed/failed/cancelled（L218/L228/L224）。
3. **GET logs?position=p**：磁盘读 backend.log 从 position 起的新行，**过滤 INFO:/WARNING:/DEBUG:/ERROR: 前缀行**（service.py L75-82），返回 logs + 新 position + active_tasks 里的 status/result/error。
4. **GET status / POST cancel**：按 task_id 查 active_tasks / workflow_tasks + cancel_events。

状态与日志是两条独立通道：日志走磁盘（跨请求可见），状态走内存 dict（**跨请求不可见**——致命处见下）。

## ⑤ 设计决策与取舍

**`get_service()` 每请求新建实例 = 跨请求状态全灭（重点 bug）**。`WorkflowService.__init__` 把 `active_tasks`/`workflow_tasks`/`cancel_events` 定义为**实例属性**（service.py L51-53），而每个端点各自 `get_service()` 拿全新实例。后果按端点展开：

- execute（L52）在实例 A 注册任务、后台协程把状态写进 A.active_tasks；
- **GET /tasks/{id}/status（L104）在实例 B 查询——B.active_tasks 恒空 → 永远 404 "Task not found"**；
- **POST cancel（L113）在实例 C——恒 404，任务实际无法经 API 取消**；
- GET logs（L89）在实例 D——日志内容能读（磁盘共享），但 status 恒 'unknown'、result/error 恒 None，前端永远看不到任务完成。

唯一"能跑"的解释是开发期恰好单请求内完成断言。正确做法是模块级单例或 FastAPI `Depends` + app state——L22 的函数形态（看似为依赖注入预留的接缝）说明作者有此意图，只是没落实。

**其余取舍**：execute 用 `asyncio.create_task` 而非线程/队列——协作式调度，取消语义清晰（Workflow.run 是 async 所以成立）。日志全局单文件 + 字节偏移增量读（L68/L93）是最朴素的 tail -f 实现；log_position 与 position 双字段并存（L96-97）是兼容残留；cancel 判 404 靠字符串比对（L117）——用消息文本当错误码，脆弱。

## ⑥ 新人提示（坑/勘误）

1. **修 bug 别修一半**：把 `get_service()` 改单例能救活 status/cancel/logs 端点，但注意 `__init__` 每次 new `Browser()`（service.py L47）是重资源——单例化后恰好只建一次；当前每请求实例化下连 list_workflows 这种纯目录扫描也各建一个 Browser/LLM 客户端，纯浪费。
2. **`self.workflow_obj` 是伪共享**（service.py L186）：实例属性但只在后台协程当局部变量用；修好单例后同实例并发两任务会互相覆盖——应顺手改局部变量。
3. **加载失败产生僵尸 running**：service.py L189-191 加载异常时 `print` 后裸 `return`，active_tasks[task_id] 停在 L174 设的 'running' 且无 error——前端将无限轮询永不结束的任务。对比通用 except（L226-229）有写 failed，唯独这个早退漏了。
4. **路径拼接无防穿越**：execute 的 `service.tmp_dir / workflow_name`（L60）对用户输入 name 不做 basename 归一化，`../` 可逃出 ./tmp。
5. **日志过滤在读取端**（service.py L75-82）：写全量、读时滤级别前缀——非标准 logging 格式的行不会被滤，前端会混入引擎噪音；且并发多任务写同一 backend.log，从 log_position 读增量会把**别的任务的行**也读进来。
6. **`ui/src/lib/api/openapi.json` 是 0 字节空文件**：`npm run get-openapi` 在后端未启动时 curl -o 留下的脏状态，类型生成链依赖它（详见 workflow-layout 篇）。
7. **update 端点用 nodeId 当数组下标**（service.py L135-136）：直接按索引替换 steps——nodeId 是 ReactFlow 图节点标识，若图节点与 steps 数组不一一对应会错位覆盖；L125 对 `updated_step_data` 用真值判断，无法把步骤显式置为空结构。
8. **logs 的 position 语义是字节不是行号**（L90），传行号会从错误位置 seek 出乱码；`position >= current_size` 时返回原 position（service.py L69-70），日志轮转会在此静默错乱。
