# 11 · 医疗与资产行业：industries/healthcare 与 asset_lifecycle_management_agent

## 角色定位

图谱 layer-6「医疗与资产行业」（118 节点）= `industries/healthcare`（78 节点）+ `industries/asset_lifecycle_management_agent`（40 节点），是仓库 `industries/` 目录的全部（`industries/energy` 属能源层）。两个示例代表行业化的两条路线：healthcare 是**主线 RAG 的行业裁剪**——把仓库主 RAG 示例原样搬来，只换提示词、文档类型与交互形态（语音）；asset 是**Agent Toolkit 原生应用**——用 NeMo Agent Toolkit 的工具注册体系从头构建预测性维护 agent。

healthcare 下实际有三个目录：`medical-device-training-assistant`（主体，手术室设备 IFU 说明书问答）、`agentic-healthcare-front-desk`（仅剩一个 README——内容已迁移到 NVIDIA-AI-Blueprints/ambient-patient 仓库，README 明说）和共用文件。asset 则聚焦 NASA C-MAPSS 涡扇发动机数据集的 RUL（剩余寿命）预测与异常检测。

## 内部结构

**medical-device-training-assistant** 完整复刻主线 multi_turn_rag 的拓扑（README 自述"based on .../examples/multi_turn_rag"，注意该链接指向旧路径 RetrievalAugmentedGeneration/，仓库已重组为 RAG/）：`src/chain_server/`（server.py 491 行 FastAPI：`/health`、`/upload`、`/generate`、`/documents/search`、`/documents`、DELETE 文档，startup 时 `import_example` L203）+ `src/rag_playground/`（**只有 speech 一种模式**）+ `app_chain/chains.py`（369 行，LLM 服务工厂）+ `evaluation/`（RAGAS 评测独立 compose）+ `deploy/` 教程笔记本。

双向量库结构在 `chains.py`：文档库 `docstore`（L55 `create_vectorstore_langchain`）存 IFU 切块，对话库 `convstore`（L141，`collection_name="conv_store"`）存历史问答——多轮记忆即"把对话也向量化再检索"，与主线 multiturn 同款设计。compose 里 `PLAYGROUND_MODE: ${PLAYGROUND_MODE:-speech}`（docker-compose.yaml L68）把语音钉为默认。

**asset** 是 NeMo Agent Toolkit 工具包结构：`src/asset_lifecycle_management_agent/` 下 `retrievers/`（`generate_sql_query_and_retrieve_tool.py` L31 用 FunctionBaseConfig 注册工具，L87 指向 `vanna_training_data.yaml` 训练语料；`vanna_manager.py`/`vanna_util.py` 封装 Vanna）+ `predictors/`（四个工具：`predict_rul_tool.py` XGBoost、`nv_tesseract_anomaly_detection_tool.py` NV-Tesseract NIM、`moment_*` 两个 MOMENT 替代实现）+ `plotting/` + `evaluators/` + `register.py`。根目录 `test_alm_workflow.py`（`run_workflow_with_prompt` L30 起三个异步测试）、`setup_database.py`（SQLite/PostgreSQL/MySQL 三态建库）。

## 外部连接

healthcare 的外部件：Riva ASR/TTS（本地容器或 API Catalog 端点，docs/riva-asr-tts.md 是总开关文档）、Milvus（CPU 默认，GPU 加速可选）、LLM/embedding/rerank 三类 NIM（默认 llama3-70b + nv-embedqa-e5-v5 + nv-rerankqa-mistral-4b-v3，README 表格明示）。README 强调"No GPU requirement"——全端点模式一台笔记本可跑。

asset 的外部件更工业：SQL 数据库三选一、ChromaDB 向量库存表 schema/Vanna 训练对/文档、NIM LLM（生成 SQL）+ NV-Tesseract 时序基础模型 NIM（异常检测）+ 本地 XGBoost（RUL）——**"LLM 编排 + 传统 ML 打分 + 基础模型感知"三种智能混编**是它最值得看的架构点。

## 数据流

**healthcare 语音问答**： clinicians 对麦克风提问 → rag_playground speech 前端（ASR）→ `/generate`（server.py L324）→ `rag_chain`（chains.py L121）→ 并行检索 docstore（IFU 上下文）与 convstore（最近对话）→ prompt 组装 → LLM 流式生成 → TTS 播回。上传侧 `/upload`（L280）收 PDF/TXT/MD → `ingest_docs`（chains.py L70）切块入库。整套流程与主线 RAG 逐字节同源——**差异只在 prompt.yaml（医疗设备培训助手人设）与 speech 交互**。

**asset 的维护决策环**：ReAct agent 收到"检查 3 号发动机健康度"类指令 → 调 `generate_sql_query_and_retrieve_tool`：Vanna 先用 ChromaDB 里的 schema+训练对（`vanna_training_data.yaml`）RAG 出 SQL → 查 SQL 库取传感器时序 → 可选调 `nv_tesseract_anomaly_detection_tool` 判异常、`predict_rul_tool` 出剩余寿命 → `plotting/` 画图 → agent 汇总成建议。测试文件 `test_alm_workflow.py:53/67` 的 `test_data_retrieval_and_plotting`/`test_rul_distribution_analysis` 就是这条环的两个切片。

## 设计决策

1. **speech 单模式 + 前端字节级复用**：healthcare 的 rag_playground 只有 speech/ 子目录，没有 default/；经逐文件比对，主线 `RAG/src/rag_playground/default/static/` 与 `speech/static/` 的全部 27 个 HTML/JS 静态文件**字节级完全相同**（含 _next 构建产物），仅 Python 侧（api/chat_client 等）分叉——"模式差异在服务层、界面零改动"的工程决策，也意味着 default↔speech 的切换成本被压到纯后端。
2. **行业化=换语料换 prompt，不动引擎**：medical-device 示例对主线代码的改动集中在 prompt.yaml 与文档类型，chain_server 几乎原样——这是"平台+行业包"思路的最小样例；反过来说，想给它加新行业能力应先看主线 RAG 有没有现成的。
3. **front-desk 的"搬家不留壳"**：agentic-healthcare-front-desk README 只剩迁移声明（去 ambient-patient blueprint），代码全删——仓库用"墓碑 README"维持链接不坏，比留一套过期代码诚实。
4. **asset 的 Vanna 训练数据 YAML 化**（L87 `vanna_training_data_path`）：把 text-to-SQL 的 few-shot 对从数据库配置升格为仓库内受版本控制的文件，训练数据可 review、可 diff。
5. **异常检测双实现**：NV-Tesseract NIM 与 MOMENT 并存（predictors/ 四个文件两两成对），README 称 MOMENT 为 alternative——供应商锁定的对冲，也是评测视角的现成 A/B。

## 新人提示

- 读 healthcare 先看两份文档再碰代码：`docs/riva-asr-tts.md`（语音配置总纲）与示例自带 `prompt.yaml`（行业人设）；chain_server 不必精读，与主线 RAG 的 chain_server 对照 diff 更高效。
- asset 示例的正确入口是 `INSTALLATION.md` + `test_alm_workflow.py`——测试即用例文档；想理解工具注册范式直接读 `generate_sql_query_and_retrieve_tool.py:31-100`，FunctionBaseConfig → InputSchema → VannaManager.create_with_config 三段式是 NeMo Agent Toolkit 的标准姿势。
- 两个示例都依赖主线/平台知识：healthcare 背后是 RAG 主线（见第 1-2 篇组），asset 背后是 NeMo Agent Toolkit（仓库 nemotron/ 目录线）；把它们当"行业皮肤"读，别当独立系统读。
- 甄别备注：任务书提示"speech 单模式+default/speech html 字节级同"，经逐文件二进制比对实证：主线 RAG 的 default/static 与 speech/static 27/27 文件全同、无单侧独有文件；healthcare 的 rag_playground 仅含 speech（无 default 目录），compose 默认 PLAYGROUND_MODE=speech（docker-compose.yaml:68）。README 中 multi_turn_rag 引用路径已过时（旧 RetrievalAugmentedGeneration/ 路径）。行号锚（chains.py:55/70/121/141、server.py:203/280/324、generate_sql_query_and_retrieve_tool.py:31/87、test_alm_workflow.py:30/53/67）均对照源码核实。
