# AgentFlow ONBOARDING

> 基于图谱（909 节点/1857 边/16 层/16 步 tour，`23aa36a`）与源码核实，行号锚已验证。

## 1. 一句话定位

AgentFlow（OpenDCAI org）是**数据流水线式 agent 编排框架**：自研 agent 核心（`rollout/` 评测+轨迹采集、`synthesis/` QA 合成）跑在自研 sandbox server（`sandbox/`，FastAPI）上；桌面沙箱=vendored OSWorld、PDF 线=vendored DocDancer+mineru_vl_utils；doc/ds/rag/web 四 benchmark 开箱即用；MCP 侧经 Toolathlon-GYM manifest 暴露 25 server/438 工具。方法论=三阶段合成（Trajectory Sampling → Selection → QA Synthesis）：沙箱真实跑工具长轨迹树→挑优→基于真实观察出题。

## 2. 心智模型：五个关键词

**① protocol 契约先行**：`sandbox/protocol.py` 13 个 class 是通信唯一权威契约（execute/session/init 三族+`:193` HTTPEndpoints）。
**② tools 双面注册**：agent 侧声明面 `sandbox/tool_schemas/__init__.py:40` 聚合六域 schema+MCP 438 工具；服务端执行面双轨——轻量 `@register_api_tool`（`backends/tools/__init__.py`）vs 重量 `Backend` 基类（`backends/base.py:107` 生命周期契约）+`@tool` 五件套。
**③ rollout 懒加载主循环**：`rollout/__init__.py` 模块级 `__getattr__` 懒加载重依赖；主循环 `AgentRunner._run_conversation`（`rollout/core/runner.py:223`）：LLM 产出→工具调用→执行→观测回填→final answer。
**④ sandbox 双线供给**：自研线 `server/app.py:60` HTTPServiceServer 挂 `/api/v1/*`（`routes.py:45-502`）；vendored 线 desktop_env（VM 内还有机载 Flask `desktop_env/server/main.py`）。`resources/vm.py`（全仓最大 2198 行）管连接池/快照回滚+OSWorld 式评估。
**⑤ configs 驱动**：48 份配置（23 JSON+25 MCP YAML），路径一律 `${VAR:-default}` 占位（`server/config_loader.py` 展开+动态装配 backend）。

## 3. 代码地图（16 层）

- L01 入口：README 双语、`install.sh`、`start_sandbox_server.sh`
- L02 客户端：`protocol.py`、`client.py:103`、`sandbox.py:150`、`result_formatter.py`
- L03 工具 schema：`sandbox/tool_schemas/`（六域+438 工具 manifest）
- L04 rollout：`api.py:54`、`pipeline.py`、`core/runner.py:30`、`core/config.py:21`（34 字段）、`core/evaluator.py`
- L05 server 核心：`app.py`、`routes.py`、`core/tool_executor.py:49`、`core/resource_router.py`、`config_loader.py`
- L06 无状态四工具：`backends/tools/` doc/ds/text2sql/websearch+`base_tool.py:22`
- L07 有状态后端：`base.py:107`+`resources/vm.py`（18 个 vm:* 工具）/`rag.py`/`mcp/`
- L08 OSWorld vendored：`actions.py`、`controllers/`、`providers/`、`evaluators/`（13 getter+17 metric）、`osworld-settings/`（⚠真实凭据）
- L09 mineru_vl_utils 0.1.15（AGPL-3.0）：`mineru_client.py`、`vlm_client/base_client.py`、`post_process/`
- L10 DocDancer：`PDF_preprocess/` 三脚本（OCR→data.pkl→outline.xml）+`eval/eval_score.py`
- L11 synthesis：`pipeline.py`、`core/sampler.py:20`、`core/selector.py:12`（评分+Jaccard 去重）、`core/synthesizer.py:15`（泄漏过滤）
- L12 BrowseComp-V3：加解密+多模态推理+LLM-as-judge
- L13 配置家族 48 份（7+8+4+4 JSON+25 YAML）
- L14 种子与基准：seeds/ 五域+benchmark/ 三线（rag/web/doc；⚠ds 缺席）
- L15 测试：rollout/tests 5 件+sandbox/tests 11 件（MCP 集成需 `AGENTFLOW_RUN_MCP_INTEGRATION=1` 门控）
- L16 文档案例：docs 双语群+examples 五篇

## 4. 核心链路走读：一次 rollout

rag 线六站台（`configs/infer/rag_infer.json`）：①`RolloutConfig.from_json`（`config.py:21`）加载校验；②`load_benchmark`（`pipeline.py:91`）读 rag_benchmark.jsonl；③`AgentRunner.start`（`runner.py:59`）经 `Sandbox.start()`（`sandbox.py:150`）拉服务端、预热资源、`_load_tool_schemas`（`runner.py:129`）取 rag_search schema；④主循环 `run_task`（`runner.py:144`）→`_run_conversation`（`runner.py:223`）：chat→tool_calls→`_execute_tool`（`runner.py:325`）→`Sandbox.execute`→`HTTPServiceClient`（`client.py:103`）POST execute 端点（`routes.py:62`）→`ToolExecutor.execute`（`tool_executor.py:155`）→RAGBackend `@tool` 函数→四件套响应→`result_formatter` 压缩回填→循环至 final answer（`runner.py:312-321`）；⑤`Evaluator` 按 metric 分派——MMLongBench 系动态加载 `projects/DocDancer/eval/eval_score.py`（`evaluator.py:507`，DocDancer 唯一耦合点）；⑥落盘三产物。synthesis 线同构：Worker→Sampler→Selector→Synthesizer 产 QA+轨迹双 JSONL。

## 5. 运行与调试

`bash install.sh`（`--ml` torch 栈/`--cloud` 阿里云/`--all`；`install.sh:54/57/101`）。起沙箱 `bash start_sandbox_server.sh --config configs/sandbox-server/web_config.json`（exec 入口 `start_sandbox_server.sh:86`）；**坑：`--host/--port` 被显式忽略**（`start_sandbox_server.sh:25-27`），换端口只能改 config 的 server.port。四场景：推理 `configs/infer/{doc,ds,rag,web}_infer.json`、采集 `configs/trajectory/` 对偶；入口 `python -m rollout.pipeline`。资源前置：rag 需 RAG_{EMBEDDING_MODEL,INDEX,CORPUS}_PATH 三环境变量；doc 需 DocDancer 预处理产物；text2sql 需 SQLite 库；web 需 SERPER/JINA key。测试 `pytest rollout/tests/ sandbox/tests/`。排障：`--show_config`、/api/v1/health、错误码查 `sandbox/docs/*/api/ERROR_CODES.md`。

## 6. 已知坑（按危害分级）

**S 级 · osworld-settings 真实明文凭据未脱敏（应立即轮换）**：`utils/osworld-settings/google/settings.json`（邮箱+弱口令）、`proxy/dataimpulse.json`（代理 hex 账密）、`thunderbird/settings.json`（邮箱+25 字符密码）三处随 vendored 进仓；googledrive 目录已清空=脱敏漏网。删文件≠revoke（git 历史仍在），须轮换凭据+清历史。
**A 级 · README 启动命令指向不存在脚本**：`README.md:110`/`README_zh.md:92` 的 `./sandbox-server.sh`——实际是 `start_sandbox_server.sh`，新人第一命令必挂。
**A 级 · calc.py vendored 缩进缺陷**：`evaluators/getters/calc.py:9-14`——`next(reader)` 与取列写在 with 块外，惰性迭代遇已关文件必抛 ValueError，VM 评测链调用即炸；修=三行缩进进块。
**A 级 · eval() 注入面**：`projects/DocDancer/eval/eval_score.py:138/142/178/179` 四处裸 eval()——外部评测数据埋系统调用串即代码执行；修 `ast.literal_eval`。同族：`run_pipeline.sh:7` set -e 吞错误处理；`synthesis/pipeline.py:45-47` output_dir 焊死。
**B 级 · MCP YAML 文件名≠name（5 处）**：`mcp/configs/` 下 12306.yaml→rail_12306、arxiv-latex-mcp.yaml→arxiv-latex、npx-fetch.yaml→fetch、scholarly_search.yaml→scholarly、youtube_transcript.yaml→youtube-transcript；`mcp_config.json:13` enabled_mcp_servers 认 **name 不认文件名**，写错静默失效。
**B 级 · synthesis 配置路径断链**：`GUI_config.json:26` 引 vm_config.json（实际 GUI_config.json）+`:53` 引 seeds/vm（实际 seeds/GUI）；`doc_ds_config.json:21` 引不存在的 configs/server/；`text2sql_config.json:26/75` 两处裸 `/path/to/AgentFlow/` 占位。
**B 级 · docstring 示例误报排除法**：`rollout/api.py:8-9` 示例引的 configs/rollout/ 与 benchmark/benchmark.jsonl 双双不存在（真配置在 configs/infer 与 configs/trajectory）；鉴别=docstring 路径非运行代码，报断链先 `test -e` 区分"示例失修"与"真断链"。同型：`sandbox/sandbox.py:64-78` 默认配置注册 bash/browser/code 三后端但模块不存在。
**C 级**：ds 基准缺席；`${VAR:-default}` 与 MCP YAML `${local_servers_paths}` 同形不同义（`mcp/client.py:43-48`）；弱凭据兜底 `${VM_CLIENT_PASSWORD:-password}`。

## 7. 上游与生态

OSWorld（xlang-ai）vendored 进 desktop_env，VM 镜像拉自 HF `xlangai/ubuntu_osworld`（`providers/docker/manager.py:19-20`）；mineru-vl-utils 0.1.15（AGPL-3.0 传染性约束）整包 vendor；Toolathlon-GYM=25 server/438 工具 MCP 基准；同 org 的 DataFlow 是姊妹仓（数据清洗），构成"合成+清洗"上下游；Agent Family（DocDancer/RAGShaper 论文）以本仓为基座。

## 8. 学习路径

16 步 tour 即课程表，四段配 explain 12 篇（`../explain/`）：①骨架：step-01~03+explain 01/02，装依赖起沙箱；②主循环：step-04~05+explain 03，跑通 rag_infer.json 并对照第 4 节设断点；③沙箱深水：step-06~10+explain 04/05，精读 zh-CN ARCHITECTURE 与 BACKEND_DEVELOPMENT 两文档；④数据线：step-11~16+explain 06-11。无论哪条线**先读 explain 12-known-bugs.md**（17 坑地图）：跑 DocDancer 前修 py2 encode 与 set -e、评测前换 eval()、部署前处置 S 级凭据。自检三问：工具调用经哪些文件？两条扩展路线边界？48 份配置四层各驱动什么？脱稿能答即出师。
