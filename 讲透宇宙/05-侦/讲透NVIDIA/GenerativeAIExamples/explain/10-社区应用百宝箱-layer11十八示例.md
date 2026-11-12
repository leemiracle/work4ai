# 10 · 社区应用百宝箱：layer-11 的 18 个杂项示例

## 角色定位

图谱 layer-11「社区应用百宝箱」（165 节点）收纳 community/ 下其余 18 个示例（外加 README 与一个 `.DS_Store` 文件节点——图谱忠实记录了仓库的 macOS 残留）。这层的共同画像：**单场景小工具**，多数是几百到两千行的独立脚本/笔记本，覆盖聊天前端、Text-to-SQL、日志分析、健康助手、提示词工程、视频检索、教学视频配套等"长尾"。它不是某个连贯架构，而是 NVIDIA 开发者生态的"应用橱窗"——每个示例展示一种"把 NIM 端点当积木"的用法。

按节点数排序的头部：chat-llama-nemotron（27）、multimodal_assistant（21）、SQLServer_AI_with_NVIDIA_NIM（17）、llm-prompt-design-helper（16）、Azure-Serverless-GPU-Embedding（12）、log_analysis_multi_agent_rag（11）、chat-and-rag-glean（10）、llm_video_series（10）。

## 内部结构

挑六个代表拆开：

- **log_analysis_multi_agent_rag（BAT.AI）**：337 行的 LangGraph 自纠错 RAG。`bat_ai.py:29-50` 建五节点图：retrieve→rerank→grade_documents→generate，grade 不过则 transform_query 回 retrieve（L50）——教科书级 CRAG（Corrective RAG）拓扑。节点实现在 `graphnodes.py`（retrieve L13/rerank L25/generate L34/grade_documents L43/transform_query L62），`multiagent.py` 提供 BM25+FAISS 混合检索 `HybridRetriever`，`binary_score_models.py` 定义二元打分的结构化输出。
- **chat-llama-nemotron**：三段式全栈——React 前端（YAML 配置驱动 `frontend/public/config/app_config.yaml`）+ `backend-rag/src/`（app.py+rag_service.py）+ `backend-dynamo/llm-proxy/`（proxy.py，NVIDIA Dynamo 推理代理），服务 Llama-3.1-Nemotron-Nano-4B-v1.1。是这层唯一"前端+RAG+自托管推理"三件齐的示例。
- **SQLServer_AI_with_NVIDIA_NIM**：没有 Python，全部是 SQL 脚本（`scripts/0_CreateEmbeddingTable.sql` 建外部表、`2_proc_embedding.sql` 存储过程调 NIM embedding、`3_ChangeExternalModel.sql` 换模型）+ remote/local 两份 md——展示 SQL Server 2019+ 的 T-SQL 外部 REST 调用直接吃 NIM。
- **llm-prompt-design-helper**：提示词工程工作台。抽象后端 `APIRequest`（`api_request.py:26`）派生 `openai_client.py`/`chatnv_client.py` 双实现，FAISS 向量库存提示词语料（`vector_store/faiss_vector_store.py`），chat_ui 支持 temperature/top_p/max_tokens/few-shot 逐参调优（`api_request.py:55` 签名可见）。
- **smart-health-agent**：这层最"反 NVIDIA"的示例——`smart_health_ollama.py:36` 用 `langchain_ollama`+`OllamaLLM`，模型 `gemma3:4b-it-q4_K_M`（L50），embedding 是 CPU 上的 `all-MiniLM-L6-v2`（L271-272），外部数据源 open-meteo 天气 API（L61）。全本地零 NIM，配 `google_fit_utils.py`（226 行）读 Google Fit。
- **Vanna_with_NVIDIA_AI_Endpoints**：单 notebook，标题就是"Accelerating Text-to-SQL Inference on Vanna with NVIDIA NIM"（nb 第 7 行），L398 定义 `class VannaMilvus(Milvus_VectorStore, OpenAI_Chat)`——Vanna 的多继承扩展点接 NIM。

其余小件：`video-dataset-search`（Gradio 界面+`index_videos.py` 建视频索引）、`chat-and-rag-glean`（LangGraph agent 查 Glean 企业搜索）、`reasoning_coder`（479 行单文件推理编码器）、`data-analysis-agent`（616 行）、`5_mins_rag_no_gpu`（122 行最小 RAG）、`ai-podcast-assistant`（phi-4 多模态笔记本）、`rag-developer-chatbot`（RAPIDS notebook）、`synthetic-data-retriever-customization`（NeMo 合成数据+检索器定制两个 notebook）、`llm_video_series`（三个视频配套 app）、`Azure-Serverless-GPU-Embedding`（trigger-mode.py+spark-embedding.py，Azure 无服务器 GPU 批量 embedding）、`dgx-spark-demo`（README-only 指针型目录）、`multimodal_assistant`。

## 外部连接

这层的价值恰恰在"出圈"：SQL Server（微软生态）、Glean（企业搜索 SaaS）、Ollama（本地推理，绕开 NIM）、Azure Serverless GPU（云函数+Spark）、Google Fit/open-meteo（可穿戴与天气 API）、Perplexity 式外部检索在 09 篇。NVIDIA 端点被当作"可替换的 OpenAI 兼容后端"接入各种宿主——与主线示例"NVIDIA 端点为中心"的视角正好互补。

## 数据流

以 BAT.AI 为例（这层最完整的检索环）：日志文本 → `HybridRetriever`（BM25 关键词 + FAISS 向量并行召回）→ `rerank`（NVIDIA rerank 端点重排）→ `grade_documents`（LLM 按 `binary_score_models` 的二元 schema 逐文档判相关）→ 相关则 `generate`（带上下文生成日志洞察），不相关则 `transform_query` 改写查询回到 retrieve——一次问答最多经历"检索→打分→改写→再检索"的完整自愈回路。chat-llama-nemotron 的流则是 React UI → backend-rag（文档检索+prompt 组装）→ llm-proxy → Dynamo 上的 Nemotron Nano → 流式回传。

## 设计决策

1. **BAT.AI 的五节点图是 CRAG 的最小完整实现**：每边都有语义（rerank 后打分、打分失败改写重查），比 09 篇 routing 的单向流多了反馈环；代价是 337 行里没有任何持久化与并发控制——定位是"样例工程"不是"工程样例"。
2. **multimodal_assistant 与 oran-chatbot-multimodal 是同骨架双胞胎**：`diff -rq` 证实两者目录结构相同、核心文件（Multimodal_Assistant.py/fact_check.py/retriever.py）互有差异，oran 版多出 `evals/`、`config.yaml`、`oran.config`/`multimodal_oran.config`，通用版只有 `multimodal.config`——一次代码分叉出"领域版+通用版"，通用版没有随 oran 版回同步（evals 缺失），分叉债可见。
3. **SQLServer 示例证明"RAG 不一定要 Python"**：embedding 调用被压进 T-SQL 外部表/存储过程，DBA 在纯 SQL 世界里就能建向量列——这层最有"跨生态说服力"的一件。
4. **smart-health-agent 示范了断网姿态**：Ollama+MiniLM 全本地栈出现在 NVIDIA 官方示例仓里，本身就是对"端点可选"的表态；文件名直接叫 smart_health_ollama.py。
5. **dgx-spark-demo 是空目录级示例**（仅 README），图谱给它 1 个节点——橱窗里也有"只贴了张说明书的展位"，读仓库时别对它抱代码期待。

## 新人提示

- 想最快理解"自纠错 RAG"，直接读 `log_analysis_multi_agent_rag/bat_ai.py`（44 行建图）+ `graphnodes.py`（70 行节点），一小时闭环。
- 想做"提示词调参台"，llm-prompt-design-helper 的双后端抽象（openai/chatnv 可切）+ YAML 配置回写（`update_yaml`）是可直接抄的骨架。
- 这层适合"按需取用"而非通读：先看目录名猜功能，命中你当前需求再进；README 是这层最重要的索引（`community/README.md` 有全表）。
- 甄别备注：任务书把 log_analysis_multi_agent_rag 指给第 9 篇，但图谱将其归入 layer-11，本篇按图谱收录并已在第 9 篇篇末注明；另经 diff 实证 multimodal_assistant 与 oran-chatbot-multimodal 为分叉关系（任务书未提示）。行号锚（bat_ai.py:29-50、graphnodes.py:13/25/34/43/62、api_request.py:26/55、smart_health_ollama.py:36/50/271、Vanna nb L398）均对照源码核实。
