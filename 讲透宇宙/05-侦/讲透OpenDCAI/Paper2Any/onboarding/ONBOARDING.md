# Paper2Any ONBOARDING · 新工程师入门指南

> understand-anything 图谱（2327 节点/5173 边/16 层/16 步，commit b538531e）+源码核实，行号锚以此为准。配套 `../deepwiki/` 与 `../explain/` 12 篇。

## 1. 一句话定位

OpenDCAI org 的**论文到任意格式转换平台**：上传论文 PDF 转出 PPT/海报/视频/draw.io 图/思维导图/播客等，带积分计费、知识库工作台与 OnlyOffice 在线编辑。四件套：React 前端（`frontend-workflow/`）+ FastAPI 后端（`fastapi_app/`，19 router）+ **dataflow_agent** 41-agent 框架（LangGraph）+ 7 大 toolkit；19 个活跃 `wf_*.py` 加 deprecated 7 张。

**上游血统**：本仓剥离自 DataFlow-Agent，pip 包名保留实证——`pyproject.toml:4` `name = "dataflow-agent"`（import 名 `dataflow_agent`）；同 org DataFlow 经 `requirements-base.txt:7` `open-dataflow==1.0.6` 进依赖。

## 2. 心智模型：五层积木

1. **前端手写路由**：`App.tsx`（332 行）不用 react-router，自实现 20 页面 pathname/legacy-hash 双轨路由（App.tsx:80/98）；Provider 挂载链见 `src/main.tsx:12-19`。
2. **FastAPI get_service 延迟装配**：`routers/paper2ppt.py:33` 函数体内 import 重服务再 `Depends()` 注入——启动快、测试可换。
3. **BaseAgent 自动注册**：`cores/base_agent.py:95` 经 `__init_subclass__`（base_agent.py:150）按 role_name 登记进 `cores/registry.py`，`agentroles/__init__.py` pkgutil 自动导入——**定义类即注册 agent**。
4. **workflow 状态机**：`graphbuilder/graph_builder.py:10` GenericGraphBuilder 链式建图（`@pre_tool`/`@post_tool` 见 graph_builder.py:39/48）；wf_*.py 用 `workflow/registry.py` 登记工厂，`workflow/__init__.py:29` 懒加载防启动拉起重依赖；状态全来自 `state.py`（MainState:41 起 13 套）。
5. **toolkit 工具岛**：`toolkits/tool_manager.py` 按角色挂工具、把 agent 包装成 LangChain Tool，七大工具家族各成岛。

黄金链：**前端页面 → router（鉴权/计费）→ service → wa_* 适配器 → run_workflow(图名) → GenericGraphBuilder → BaseAgent 群 → toolkit**。

## 3. 代码地图（按 16 层）

- **前端五层**：L01 根配置（53 文件，requirements×7/compose 三服务/`database/01_init_schema.sql` 8 张表）｜L02 基座（34，authStore.ts 494 行）｜L03 页面与编排（55，37 页面+ReactFlow 画布四件）｜L04 paper2ppt 家族（25 文件 15060 行，index.tsx 5422 行）｜L05 知识库与五条转换线（43）。
- **后端两层**：L06 FastAPI 入口（36，`main.py:58` 挂 19 router；`middleware/api_key.py` 限流/配额/鉴权三合一）｜L07 业务服务（30，paper2ppt_frontend_service 5332 行最大类、billing 计费、wa_* 10 件）。
- **框架三层**：L08 dataflow_agent 核心（48，base_agent.py/strategies.py 七策略/graph_builder/state.py）｜L09 41 智能体（outline 族/diagram_planner/websearch/p2v）｜L10 工具箱（69，model_servers/multimodaltool 16 件/citationtool/dockertool 沙箱）。
- **外围五层**：L11 postertool（34，独立子系统，pipeline.py 七节点图）｜L12 workflow+提示词（54，prompts_repo.py 2460 行总仓）｜L13 部署（43）｜L14 i18n（28）｜L15 docs（19）+L16 tests（34，conftest.py 伪造 MinerUClient）。

## 4. 核心链路：一篇论文到 PPT 的旅程

**上传与解析**：`paper2ppt/index.tsx` upload 步（L2837 分界）→ `POST /api/v1/paper2ppt/page-content`（routers/paper2ppt.py:286）；PDF 走 MinerU（`multimodaltool/mineru_tool.py`），outline_agent 族生成大纲；前端 Step 2 编辑（index.tsx:3091）。

**生成双模式**（types.ts:2）：
- frontend（主力，可编辑）：`paper2ppt_frontend_service.py:17` create_react_agent，ReAct 逐页产出 FrontendSlide（canvas 节点树）+信号量限流与审阅循环；
- image：`wa_paper2ppt.py:316` → L457 `run_workflow("paper2ppt_parallel_consistent_style")` 进 `wf_paper2ppt_parallel_consistent_style.py:348` 的图；`_route` 四分支生成/编辑/重生成/导出；先出第 0 页作风格锚，其余页并行 Img2Img 复用。

**导出三通道**（index.tsx:4771 分界）：① canvas——`canvasPptxExporter.ts:1153` 递归展开成 PptxGenJS 元素，守卫过则首选；② HTML——`htmlDeckArtifact.ts:88` 编自包含 HTML 转 PPTX，再上传进 OnlyOffice 编辑（后端 `routers/files.py:347/365`）；③ 结构化——`exportStructuredSlides.ts:178` 按 8 种 layoutType 导出，主页面零调用（仅 Node CLI），半下线残留。计费夹击：APIKeyMiddleware 前查配额/限流，billing_service 后记账。

## 5. 运行与调试

**两套依赖**：pyproject.toml 只声明框架最小集（langgraph==0.6.7/langchain 0.3.x），完整运行靠 requirements 分层——base（含 open-dataflow==1.0.6）→ paper（`-r` 继承）→ cu12/system-ubuntu/win；tectonic 走 conda-forge。

**起后端两路**：① `fastapi_app/start_backend.sh`（`uvicorn main:app --reload`）——**必须在 fastapi_app/ 内跑**；② Docker 以 `fastapi_app.main:app` 启动。

**env 四层各管一摊**（.env.example:6-22）：`fastapi_app/.env`（BACKEND_API_KEY/托管 API/SUPABASE_*/ONLYOFFICE_*；懒人 .env.simple 只填 SIMPLE_*）；`frontend-workflow/.env`（VITE_API_KEY 须等于 BACKEND_API_KEY）；`deploy/docker.env`（compose）；`deploy/profiles/{muxi,nv}.env`（GPU/模型路径）——**业务配置别写进 profiles**。另有 `settings.py:21` 三层模型分配；`managed_api_service.py:10` 12 scope+凭据三级解析（用户→scope 托管→全局）。

**部署双中心**：日常在 `deploy/`（docker-up/logs+backend_watchdog.sh）；CLI 与 worker 在 `script/`。前端 `npm run dev`（3000 代理 8000）。

## 6. 已知坑（接手前必读，全部源码实证）

1. **make build 必 ModuleNotFoundError**：`toolkits/dockertool/Makefile:6` 仍用老路径 `dataflow.dataflowagent.*`（README 同漂移）；兼容 shim 在 `dataflow_agent/__init__.py` 整段被注释——全局替换即可。
2. **api_key 明文日志**：`llm_callers/text.py:32-39` 把完整 api_key 打进每次 LLM 日志——删除或脱敏。
3. **WebAgent L548 参数错位**：`paper2any_agents/websearch_researcher.py:533`——L543-547 构造默认 self.llm_config 兜底，L548-550 却读裸参数，不传即 AttributeError；默认值含硬编码内网 IP（L544，多处同款）。修法=改读 self.llm_config。
4. **postertool sys.path 隐式包根**：`postertool/src/workflow/pipeline.py:13` 把 postertool 根塞进 sys.path，L18-26 全用 `from src.state...` 顶层名——必须以自身根为包根跑，否则与主仓 src/、utils/ 打架。
5. **占位符双机制**：postertool `config/prompts/` 的 layout_balancer.txt 用 str.format 单花括号（balancer_agent.py:49），其余全用 Jinja2 双花括号（parser.py:16）——往单花括号模板写带 `{}` 的 JSON 即 KeyError。
6. **types.ts 成段重复**：`paper2ppt/types.ts` L160-299 与 L301-440 重复 11 个 interface，FrontendDeckPalette 三现（L282/L423/L566）；声明合并让编译器沉默——改前先查重。
7. **MCP yaml 无关本仓**：全仓 grep "mcp" 仅三处无关命中——本仓无 MCP server yaml，上游资料说法别信。
8. **cli.md 路径漂移**：`docs/cli.md` L70-72 引 `agentroles/base_agent.py`（实在 `agentroles/cores/`）；反复 import `dataflow_agent.states`——复数 states/ 是 0 字节空壳包，真身单数 `state.py:41`；L114 的 wf_text_processing.py 不存在。
9. 附加雷：`workflow_adapters/__init__.py` 的 `__all__` 漏 wa_paper2poster/wa_pdf2ppt/wa_kb_report；`wf_paper2video.py:1018-1045` 硬编码 `/data/users/ligang/...` 老机器路径。

## 7. 上游与生态

- **DataFlow-Agent 血统**：`dataflow_agent/` 是剥离自独立项目的框架层，pip 包名/dfa CLI/templates 全是遗产；残迹见第 6 节 1/8/9 条。
- **DataFlow 依赖**：同 org DataFlow 经 open-dataflow==1.0.6 进依赖；前端 index.tsx:339-341 拉姊妹仓 star。
- **模型与硬件**：`model_servers/` 起 sam3/sam/ocr/mineru 本地服务（`script/start_model_servers.sh` 三通道 GPU 发现）；`deploy/profiles/muxi.env.example` 为**沐曦（MetaX）国产 GPU** profile、nv.env 对应 NVIDIA——国产硬件一等公民。
- **外部服务**：Supabase（认证/存储）、OnlyOffice、CosyVoice/LivePortrait（视频线）、OpenAlex/DBLP/Crossref（引文）。

## 8. 学习路径：16 步 tour × explain 12 篇

- **第一周（跑起来）**：Step 1-4 配 explain 09+01+11，simple 模式 .env 拉起全栈。
- **第二周（旗舰线）**：Step 5 深潜 paper2ppt 配 **explain 07**（最重要精读）；Step 6-7 配 explain 10；第 4 节链路作 checklist。
- **第三周（后端与框架）**：Step 9-11 配 explain 03+04——base_agent/graph_builder/state 三件套是扩展必经之路；Step 12-13 配 05+02。
- **第四周（收官）**：Step 14-16 配 explain 06+08；explain 12 挑 1-2 条做练手 PR。
- **扩展模板**：加 agent=继承 BaseAgent；加工作流=wf_*.py `@register`+GenericGraphBuilder；加产品线=routers+services+wa_*；加工具=toolkits 建岛。

> 图谱：仓内 `.understand-anything/knowledge-graph.json`；30 枢纽（BaseAgent/state.py/schemas.py/authStore.ts 等高扇入文件）见 onboard-input.json hubs 节。
