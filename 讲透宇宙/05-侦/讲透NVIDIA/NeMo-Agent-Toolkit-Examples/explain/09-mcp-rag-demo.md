# 09 · mcp_rag_demo：Milvus 工单检索与"一套工具两种暴露"

## 角色定位

`mcp_rag_demo` 是技术支持工单 RAG 示例：Milvus 向量库存工单，四个检索工具（语义搜索/类别过滤/优先级过滤/重排）挂给 ReAct agent。它在示例仓的价值不在 RAG 本身，而在**双配置对照**——同一套注册函数，既能被本地 agent 直连调用，也能经 `nat mcp serve` 服务化后由远端 MCP 客户端 agent 消费，是"工具提供方"形态的完整样板。包名 `nat_mcp_rag_demo`。

## 内部结构

`register.py` 注册四个函数，前三个共享 Milvus 参数模式（`milvus_uri` 默认 `http://localhost:19530`、`collection_name` 默认 `support_tickets`，如 `register.py:34-35`）：

1. `search_support_tickets`（Config `register.py:31`，注册 `register.py:63`）：从 builder 取 embedder（`register.py:68`），运行时 `MilvusClient(uri=...)` 现连（`register.py:77`）→ `aembed_query` 向量化（`register.py:78`）→ `milvus_client.search`（`register.py:80-84`，`anns_field="embedding"`，output_fields 携带 ticket_id/content/category/priority/status）→ 逐条格式化，相似度按 `1 - distance`（`register.py:97`），content 截 150 字符（`register.py:98`）。输入 schema `SearchInput`（`register.py:70-72`），产出用 `FunctionInfo.from_fn`（`register.py:105-108`）。
2. `query_by_category`（`register.py:111`）：常量集合 `ALLOWED_CATEGORIES = {"bug_report","feature_request","question","incident"}`（`register.py:116`），不在白名单直接返回错误串（`register.py:126-128`），过了才拼 Milvus filter 表达式 `f'category == "{category}"'` 走 `milvus_client.query`（`register.py:131-134`）。
3. `query_by_priority`（`register.py:156`）：同构，`ALLOWED_PRIORITIES` 四档（`register.py:161`）。
4. `rerank_support_tickets`（Config `register.py:56`，注册 `register.py:201`）：函数体内 import `NVIDIARerank`（`register.py:206`）并按配置模型名构造（`register.py:208`），运行时把字符串列表包成 Document 后 `acompress_documents` 重排（`register.py:225`），按 metadata 里的 relevance_score 输出（`register.py:230-232`）。

数据装载在 `scripts/load_support_tickets.py`：`NVIDIAEmbeddings(model="nvidia/nv-embedqa-e5-v5", truncate="END")` 生成 1024 维向量（`load_support_tickets.py:43`，维度注释在 `load_support_tickets.py:79`），建 collection 后 `collection.insert`（`load_support_tickets.py:317`）。

## 外部连接

三个外部依赖：Milvus 实例（默认 19530 端口）、NVIDIA NIM（embedder 与 reranker，`nvidia/nv-embedqa-e5-v5` 与 config 里的 `nvidia/llama-3.2-nv-rerankqa-1b-v2`）、NAT 的 `react_agent` 工作流。双配置把这个示例连成两种拓扑：

- `configs/support-ui.yml`：**直连形态**。functions 节直接配四个工具（Milvus URI 内嵌），`embedders` 节配 nim embedder，workflow 用 `react_agent` 挂四个工具名 + `meta/llama-3.1-70b-instruct`。单进程跑通全部能力。
- `configs/mcp-client-for-ui.yml`：**MCP 消费形态**。functions 节消失，换成 `function_groups` 一个 `mcp_client`（`transport: streamable-http`，`url: http://localhost:9904/mcp`），workflow 的 `tool_names` 只引用这个组名。

两形态的桥是 NAT CLI：`nat mcp serve --config_file support-ui.yml --port 9904`（README.md:201）把第一份配置的工具暴露成 MCP server，`nat serve --config_file mcp-client-for-ui.yml`（README.md:208）起第二份配置的 agent 作为纯 MCP 客户端。

## 数据流

装载期：工单文本 → NIM embedder（1024 维）→ Milvus collection（embedding 字段 + 结构化字段）。查询期（直连形态）：用户问题 → react_agent 选工具 → 语义搜索路径 query→embedding→ANN search→格式化串；过滤路径 query→白名单校验→标量 filter query；混合路径先语义搜索再 `rerank_tickets(query, documents)` 两段式精排——注意 rerank 的 documents 参数由 LLM 从搜索结果里转录，这是把重排做成独立工具的代价。所有工具统一返回**字符串**而非结构体（如 `register.py:87`、`register.py:103`），异常也被捕获转成错误串（`register.py:102-103`），LLM 视角下永不崩。MCP 形态下同样的字符串经 MCP 协议跨进程传输，agent 侧无感知差异。

## 设计决策

1. **白名单先于拼接**（`register.py:116`/`register.py:126-128`）：Milvus filter 是字符串拼接，不过白名单就是注入面——这是把 LLM 不可控输出接入查询语言的必备防线，注释明言 "prevent injection attacks"。
2. **每调用新建 MilvusClient**（`register.py:77`/`register.py:130`/`register.py:175`）：牺牲连接复用换零连接管理，示例代码的合理取舍，生产应改池化。
3. **embedder 走 builder、reranker 直接 import**（`register.py:68` vs `register.py:206`）：前者可被 NAT 配置体系替换，后者因为 langchain_nvidia_ai_endpoints 的 rerank 不在 builder 抽象里——展示了"能用框架抽象就用，抽象缺口就函数内 import"的务实分层。
4. **双配置同工具**：把"工具实现"与"工具暴露方式"解耦，证明 NAT 注册函数天然是 MCP-ready 的，不需要为服务化改一行代码。
5. 值得批评的点：`1 - distance` 的"相似度"（`register.py:97`）假设 distance 是 cosine 距离，换度量就失真；rerank 工具要 LLM 手动转贴 documents，多 token 又易截断。

## 新人提示

最小可跑路径：起 Milvus（docker 即可）→ 设 `NVIDIA_API_KEY` → 跑 `scripts/load_support_tickets.py` 灌库 → `nat run --config_file configs/support-ui.yml --input "search for login issues"`。验证 MCP 形态需要两个终端按 README.md:201/208 顺序起服务。改检索质量先动两处：`top_k`（Config 默认 5/10）与 reranker 模型名（config.yml）。加新工具照 `query_by_category` 模板抄最稳——Config 三字段 + 白名单 + from_fn 注册，再在两份 config.yml 里同步登记。注意 `support-ui.yml` 的 embedder 名必须与 search 工具的 `embedder_name` 引用一致，改名漏一处启动即报 LLM 引用错误。
