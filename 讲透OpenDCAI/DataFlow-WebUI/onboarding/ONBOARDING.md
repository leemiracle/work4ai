# DataFlow-WebUI ONBOARDING

> 图谱基线 commit `2e95d40a`（840n/1532e）。行号锚均源码核实；同句 `:N` 指代刚出现的文件。

## 1. 一句话定位

DataFlow-WebUI 是 OpenDCAI DataFlow 数据清洗框架的**图形前端**：FastAPI 后端（REST `/api/v1`/WebSocket/MCP）+ Vue3/VueFlow 画布前端 + `skills/canonical` 五技能单一真源，由 `install.sh --profile <webui|harness|skills>`（install.sh:4-6）声明式安装。上游算子不在本仓——`open-dataflow==1.0.10`（backend/requirements.txt:11）经 pip 提供 `OPERATOR_REGISTRY`/`PROMPT_REGISTRY`，本仓做注册表持久化、DAG 编排与执行。CLAUDE.md 钉版：**单用户本地工具，禁认证/多租户/遥测**。

## 2. 心智模型：三层形态 + DI 装配 + 真源派生链

**三层**：① `backend/` FastAPI 单进程（8000 口）：REST+Agent 聊天 WebSocket+MCP 三面；② `frontend/` Vue3：dev 态 vite 独立跑；生产态 dist 由后端托管（main.py:46）单端口；③ `skills/canonical/` 手工编辑**单一真源**（ADR-001），经 `installers/generate_agent_assets.py` 派生 `.claude/`/`.cursor/`/`.codex/` 三家资产——派生物勿手改（CI 双向校验 check_skills.py；check_mcp_whitelist.py 以 ast 对账白名单与真实路由）。

**AppContainer DI**：backend/app/core/container.py:3 定义容器，`init()`（container.py:20）根治 Registry 初始化顺序不可控：动态加载 DataFlow 扩展（:34）→ 探测 Ray worker（:42，worker 内跳过 dataset 扫描）→ 受控顺序实例化 12 个 registry/manager（:45-55）。端点一律 `container.xxx_registry` 取依赖。

## 3. 代码地图（按图谱 15 层）

| 层 | 内容（代表文件） |
|---|---|
| L01 | 骨架/CI/容器化（checks.yml） |
| L02 | 入口/DI/响应封装（main.py、core/container.py） |
| L03 | API 端点层（endpoints/{pipelines,tasks,agent,...}.py） |
| L04 | Schema 层（schemas/pipelines.py 最大） |
| L05 | 注册表+执行引擎（services/{pipeline_registry,task_registry}.py 等） |
| L06 | Agent 适配器（agent_session.py、agents/factory.py） |
| L07 | MCP Server 单文件（app/mcp_server.py，20 白名单操作） |
| L08 | 测试与工程配置（tests/、pytest.ini） |
| L09 | 基座/状态/生成 API（stores/、axios/api.js） |
| L10 | 视图：管理端九页（views/manage/dataflow/index.vue） |
| L11 | 画布组件树 32 件（components/manage/mainFlow/） |
| L12 | 五技能主体 99 件（canonical/*/SKILL.md） |
| L13 | 模板族与脚手架（operator-builder 的 build_operator_artifacts.py） |
| L14 | 声明式安装（install.sh 486 行、lib/steps.sh、profiles/*.json） |
| L15 | docs：三 ADR+profiles+迁移（adr-001~003） |

## 4. 核心链路走读：一次管线创建与执行

**① 画布建管线**。画布页 dataflow/index.vue 保存时 `sortPipeline()` 序列化节点（:626）、校验数据集节点（:628），调 `$api.pipelines.create_pipeline({name, config})`（:636）→ `POST /api/v1/pipelines`。

**② 落注册表**。api/v1/endpoints/pipelines.py:44：`model_dump()`（:48）→ 逐算子 `_parse_frontend_params` 矫正参数形态（:50-52）→ `create_pipeline` 落 YAML 持久层（:54）→ `created()` 包 `ApiResponse`。

**③ 提交异步执行**。`executePipeline()`（dataflow/index.vue:660）→ `POST /api/v1/tasks/execute-async`（endpoints/tasks.py:282）：不存在则 404（:295），进 `start_execution_async`（:298）。

**④ TaskRegistry 移交 Ray**。task_registry.py:428：懒导入单例 `ray_executor`（:443），取 config（:448）、生成 task_id，交 `RayPipelineExecutor.submit_execution`（ray_pipeline_executor.py:972），即返 queued（endpoints/tasks.py:306）。

**⑤ Ray 内跑算子**。`RayPipelineExecutor`（ray_pipeline_executor.py:808）懒启 Ray（:827），`@ray.remote` 的 `_execute_pipeline_remote`（:849）执行体为模块级 `dataflow_pipeline_execute`（:162）：逐算子反射实例化（上游注册表在此消费），`LogStream`（:45）截获 stdout 回写算子粒度状态。**同步轨**：`POST /tasks/execute`（endpoints/tasks.py:206）走 `DataFlowEngine.run`（dataflow_engine.py:425）阻塞至完成。

**⑥ 前端轮询**。`GET /tasks/execution/{task_id}/status`（endpoints/tasks.py:33）→ task_registry.py:251 → ray_executor（ray_pipeline_executor.py:1023）；日志 :87、下载 :119。

**旁路：Agent 改画布**。Claude Code 经根 `.mcp.json` 连 `/mcp` 调 `render_pipeline_in_editor`（app/mcp_server.py），配置经 WebSocket 推画布渲染。

## 5. 运行与调试

**三档安装**（install.sh:4-6）：`webui` 全栈（需 Python+Node）；`harness` 纯 Python（backend+MCP+skills）；`skills` 仅技能。由 profiles/*.json manifest 驱动，支持 `--dry-run/--check`。

**日常**：后端 `scripts/start.sh`——`HOST="${DATAFLOW_HOST:-0.0.0.0}"`（start.sh:19），dev 态 `uvicorn app.main:app --reload`（:83），起前 curl 探活（:55）。前端 `npm run dev`（frontend/package.json:7）。根 Makefile **无 dev 目标**，只有 `make check` 等门禁（Makefile:17-36）。

**测试免装直跑**：backend/pytest.ini 仅 `[pytest] pythonpath=.`——backend 目录直接 `pytest`；conftest.py 临时注册表 fixture 隔离磁盘。

**CI 负向断言**（checks.yml）：每 job 防一类历史事故：skill lint+manifest 一致（L38）、生成器确定性（L47）、MCP 白名单=真实路由（L50）、dry-run 零落盘（L59/L67）等——改安装先想哪条断言拦你。

**调试**：日志 loguru 统一 stdout；响应全包 `{success,code,message,data,meta}`；任务卡死先查 status 再看 log（endpoints/tasks.py:87）。

## 6. 已知坑（新人必读）

1. **main.py 三个 app 缠绕**：backend/app/main.py:17 模块级 `app = FastAPI()` 是**死实例**（无路由），被 main.py:50 `app = create_app()` 覆盖；真正服务是 create_app 内 :26 新建的。另：spa_fallback（main.py:52）注册在 `mount("/")` StaticFiles（main.py:46）**之后**，catch-all 先命中——基本死码。
2. **404 被 except 吞成 500**：endpoints/datasets.py:67 `raise HTTPException(404)` 在 try 内，`except Exception`（:69，其子类）以 500 重抛（:70）；:79 同型。对照**已修**的 endpoints/operators.py:289（`except HTTPException: raise` 直通）——新端点照 operators 版写。
3. **user_prompt_registry 未兑现**：endpoints/prompts.py:26 起有用户模板全套 CRUD，但算子参数解析链（pipeline_registry/param_coercion）零消费——只有内置 `PROMPT_REGISTRY` 能被 operator config 引用（CLAUDE.md encouraged 未完成项）。
4. **host 绑定双策略**：开发仓 start.sh:19 默认 `0.0.0.0`；release 的 run.sh 由 scripts/build_release.sh:101 生成、**默认只听本机**（:99：无认证不应暴露局域网），且 build_release.sh:176 CI 断言禁止其硬编码 0.0.0.0（刻意相反，勿统一）。
5. **CursorAdapter 死码**：agents/factory.py:15 `AGENT_KINDS` 只注册 claude/codex；cursor_adapter.py 保留对等实现但永不注册（Cursor 走 IDE 内 MCP 连回）；请求 cursor 得到指向 .cursor/mcp.json 的引导 ValueError（factory.py:66）。
6. **@/ 别名+Options API 的读法**：frontend/vite.config.js:13 定义 `@`→src，组件却是 Options API，IDE 跳转失灵——按 **operation_id 对表**：api.js 方法名=后端路由装饰器的 operation_id（endpoints/pipelines.py:44 的 `create_pipeline`）。api.js/model.js 为生成物，重生成 `npm run api` 的 URL 硬编码 `100.64.0.91:8000`（package.json:12）。
7. **run.sh 不在 git 里**：release 的 run.sh 由 build_release.sh:101 heredoc 生成、仅存在于 zip（:142）；开发一律 start.sh，找不到不是丢文件。

## 7. 上游与生态

本仓是 **OpenDCAI/DataFlow 主仓的官方 GUI**：DataFlow（arXiv:2512.16676）提供算子框架与 core 注册表语义，以 `open-dataflow==1.0.10` 进入 backend；CLAUDE.md 钉版"只能扩展、不得重定义 `OPERATOR_REGISTRY`/`PROMPT_REGISTRY`"。命名（README.md）：DataFlow=上游框架 / Harness=发行产品（arXiv:2607.16617）/ 本仓=WebUI；93.3% 通过率不可从本仓复现。三家 agent 经 `.mcp.json` 等接入本仓 MCP（fastapi-mcp==0.4.0，SSE）实现"Agent 改画布"。工具链：FastAPI+uvicorn+ray+loguru+pydantic-settings / Vue3+vue-flow+Pinia+vite / nginx:1.27 交付（frontend/Dockerfile）。

## 8. 学习路径：15 步 tour × explain 12 篇

**定位（tour 01-02）**：README+CLAUDE.md 建形态与边界观，checks.yml 体会"断言=历史事故"。配 explain/11。
**backend（tour 03-08）**：main→container→端点→schemas→注册表→双执行引擎→agent 适配器→MCP；配 explain/01（tour03）、02（tour05）、08（对应第 4 节）、03+07（tour07-08）。
**frontend（tour 09-11）**：main.js→router→dataflow.js store→画布页→组件树；配 explain/04、05。重点 dataflow/index.vue 与 chatPanel（1121 行全双工 WebSocket）。
**skills 与安装（tour 12-15）**：canonical 真源→operator-builder 脚手架→派生门禁→install.sh 防漂移；配 explain/06、09、10。
**收官**：explain/12 与第 6 节互证。第一周跑通前两程（亲手 execute-async 一次），第二周画布+skills；改动从 CLAUDE.md encouraged 清单挑。
