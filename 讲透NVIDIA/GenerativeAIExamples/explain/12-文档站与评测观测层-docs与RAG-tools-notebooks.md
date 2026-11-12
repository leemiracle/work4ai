# 12 · 文档站与评测观测层：docs/ 与 RAG/tools、RAG/notebooks

## 角色定位

本篇收尾两个横切面：图谱 layer-15「文档站」（21 节点，docs/ 目录 17 个 md+VFX 图片目录）与 layer-4「RAG 评测与观测」（60 节点 = RAG/tools 38 + RAG/notebooks 22）。它们不实现任何业务功能，却决定两件事：**别人能不能正确跑起来示例**（docs），以及**跑起来之后能不能被度量与调试**（evaluation/observability）。docs/ 是主线 RAG 示例的官方手册（架构图、配置矩阵、换模型指南）；RAG/tools 把"评测"与"追踪"做成了可 compose 起停的独立容器组，与前端/链路服务并列。

## 内部结构

**docs/**（17 篇）可分四组：①架构与概念——`architecture.md`（软件组件总览：API Catalog 端点/Chain Server/Jupyter/Milvus-pgvector 四件套，TensorRT-LLM 与 NIM 两节讲推理底座）、`chain-server.md`、`frontend.md`；②配置与定制——`configuration.md`、`change-model.md`（换模型操作单）、`llm-params.md`、`prompt-customization.md`、`text-splitter.md`、`vector-database.md`（含 Milvus GPU 加速）、`multiturn.md`、`riva-asr-tts.md`（语音，被第 11 篇 healthcare 引用）；③运维——`support-matrix.md`（GPU 显存表：Llama3-8B 30GB / 70B 320GB / Arctic-Embed-L 2GB / NV-RerankQA-Mistral4B-v3 9GB）、`common-prerequisites.md`（NGC/NVIDIA 双 API key 清单，几乎被所有示例 README 引用）、`contributing.md`；④机器可读接口——`api_reference/openapi_schema.json`（chain server 的 OpenAPI 契约，唯一的非 md 文件节点）。

**RAG/tools/evaluation/** 两件套：`synthetic_data_generator/`（`data_generator.py:43` `generate_synthetic_data`，chunk_size=3000/overlap=100，默认模型 `ai-mixtral-8x7b-instruct` temperature=0.2，从 zip 数据集生成 QnA 对）+ `rag_evaluator/`（`evaluator.py` 基于 RAGAS，`main.py`/`llm_answer_generator.py` 配套，`dataset.zip` 与 `results/` 示例产物随仓）。**observability/** 三容器：OpenTelemetry Collector（`configs/otel-collector-config.yaml`）+ Jaeger（`configs/jaeger.yaml`）+ Cassandra 存储，docker-compose 一键起；探针是两份对称的 `langchain/opentelemetry_callback.py` 与 `llamaindex/opentelemetry_callback.py`。

**RAG/notebooks/** 教学区：`langchain/` 十个笔记本（basic RAG、HTML docs RAG、本地 NIM、金融报告对话、agentic RAG with NeMo Retriever、NIM tool call 人机协同多智能体、LangGraph 中间步骤处理、NeMo Guardrails 两组）+ `llamaindex/` 一个（basic RAG）。

## 外部连接

docs/ 的引用拓扑值得注意：`common-prerequisites.md` 被 healthcare、asset、各 community 示例的 README 反复相对链接（`../../../docs/common-prerequisites.md`）——它是全仓示例的"共同前置条件单一事实源"。observability 栈对接任何 OTLP 后端（README 点名 Zipkin/Prometheus 可替换 Cassandra/Jaeger）；evaluation 对接 RAGAS 库与 NVIDIA 端点（评测 LLM 也是 ChatNVIDIA，`evaluator.py:22` 导入）。

## 数据流

**评测流水线**：原始语料 zip → 合成数据生成器（LLM 对每个 3000 字符块造问答对）→ 评测数据集 → `llm_answer_generator` 用被测 RAG 链跑出答案 → `evaluator.py:144` 把四指标喂给 `ragas.evaluate`：faithfulness（忠实度）、answer_relevancy（答案相关性）、context_relevancy（上下文相关性）、context_recall（上下文召回）——L93/157 按 `[faithfulness, context_relevancy, answer_relevancy, context_recall]` 固定顺序取值打印。另有独立于 RAGAS 的 LLM 打分器：`LLAMA_PROMPT_TEMPLATE`（`evaluator.py:36` 起）给 Llama 格式指令模板，内嵌两个女王去世日期的 few-shot 评分例（5 分对/1 分跑题），要求输出 JSON 的 Rating+Explanation——**RAGAS 客观指标 + LLM 主观评分双轨**。

**观测流水线**：应用侧 LangChain/LlamaIndex 挂 callback → `opentelemetry_callback.py` 实现 13 个 `on_*` 钩子（`on_llm_start` L147、`on_chat_model_start` L189、`on_llm_new_token` L230、`on_chain_start` L307、`on_tool_start` L392、各 `*_error` L295/380/462……）把每次 LLM/chain/tool 事件开成 span → `_create_span_attr`（L94）写属性、`_parse_lc_messages`（L133）把 LangChain 消息序列化进 span → OTLP 发 Collector → Jaeger 存 Cassandra → 浏览器看瀑布图。README 的 Key Terms 一节（span/trace/root span/attributes）是给 RAG 开发者的分布式追踪速成课。

## 设计决策

1. **评测与观测做成"旁挂容器组"而非内嵌代码**：加观测=多起一组 compose + 应用挂 callback，删观测=停容器，业务镜像零改动——把横切关注点从代码里外置到部署层。
2. **双框架对称探针**：langchain/llamaindex 两份 callback 文件结构镜像，维护成本×2 但采纳面×2；代价是两份 500+ 行代码各自演化，读一份即可推另一份。
3. **合成数据先行**：没有标注集也能评——先用 LLM 造 QnA 再评，评测闭环不等人；但合成质量上界就是造题 LLM 的水平，`ai-mixtral-8x7b-instruct` 已是上一代模型，结果解读时要打折。
4. **docs 的"换模型操作单"模式**：`change-model.md` 不讲原理只给步骤（NIM 容器名→compose 环境变量→前端下拉），把最常发生的运维变更文档化成 checklist——示例仓的文档就该这么写。
5. **support-matrix 是选型入口**：30GB/320GB/2GB/9GB 四行显存表 + "多卡可拼"一句，比任何长文都快；但注意它只覆盖默认模型组合，community 各示例自带的模型（如 07 篇 405B）不在此表。
6. notebooks 目录 langchain:llamaindex = 10:1 的失衡是诚实的生态现状——主线 chain_server 用 LangChain，LlamaIndex 只在 09 篇 routing 示例等处出现。

## 新人提示

- 跑任何示例前先读 `docs/common-prerequisites.md`（API key 双证）与 `support-matrix.md`（显存预算），这两页能省掉八成"起不来"的问题。
- 想给自研 RAG 加观测，直接抄 `RAG/tools/observability/langchain/opentelemetry_callback.py` 的 `__init__`（L140 拿 tracer）+ 任意两个 `on_*` 钩子，半小时可接入；README 末节"Adding Observability to RAG Applications"有最短路径。
- 评测线建议顺序：notebooks 里的基础 RAG → 合成数据生成 notebook → rag_evaluator——先用小语料走通再上自己的数据；`results/` 里有现成输出格式样例。
- 甄别备注：任务书将本篇概括为"docs 文档站+评测观测"，经图谱核实为两个独立层（layer-15 文档站 21 节点、layer-4 评测观测 60 节点=RAG/tools 38+notebooks 22），本篇按"横切双面"合并叙事；docs/api_reference/openapi_schema.json 为层内唯一非 markdown 文件。行号锚（evaluator.py:22/26/36/93/144/157、data_generator.py:43-48、opentelemetry_callback.py:94/133/140/147/189/230/295/307/380/392/462）均对照源码核实。
