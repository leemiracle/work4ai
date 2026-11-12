# 06 · OpenAPI 三契约——Chat Engine / NLP Server / Plugin Server

> 源：`microservices/ace_agent/4.1/openapi/` 三份 JSON：`chat_engine_openapi.json`（10 端点）、`nlp_server_openapi.json`（11 端点）、`plugin_server_openapi.json`（6 端点），合计 27；消费方 `webui/server/chat-session/tasks/HTTPChatTask.ts`（185 行）

## 一、角色定位

三份契约是 HTTP 面的**服务分界文档**：**Chat Engine**（10 端点）是对话主服务——多 bot、聊天、事件、上下文，WebUI `server` 模式直连（篇 01）；**NLP Server**（11 端点）是推理池——意图槽位/分类/NER/嵌入/QA/翻译/TTS 七类推理+四健康端点；**Plugin Server**（6 端点）是插件履行服务的 HTTP 落点。三者皆 FastAPI 导出风格（snake_case operationId + HTTPValidationError/ValidationError 伴生 schema），可断言全是 Python/FastAPI。webui 只消费 chat_engine 两端点；nlp/plugin 是 bot 配置的下游。

## 二、内部结构

### 2.1 chat_engine：10 端点三分组

**生命周期**：`GET /isReady`（bot 就绪清单，schema IsReadyResponseList）、`GET /reloadBot`、`GET /health`、`GET /metrics`。**对话**：`POST /chat`（流式）、`POST /event`。**上下文 CRUD**：update/set/get/delete 四端点共享 `UserContext`（UserId+Context kv+ChatHistory）。

`ChatRequest` 关键字段：`Query`（max 4096）、`UserId` 必填、`BotName`（多 bot 部署必填，须与 bot config `bot:` 一致）、`SourceLanguage`。**PascalCase 命名**与同功能 gRPC 侧 snake_case（`ace_agent.proto:548-583`）双轨并行。`ResponseField` 三通道：`Text`（供 TTS 拾取）、`CleanedText`（剥 SSML/HTML）、`Json`。

### 2.2 nlp_server：推理超市（11 端点）

四健康端点（status/metrics/model.is_ready/list_models）+ 七推理：joint_intent_slot（意图槽位联合）、text_classification、ner、generate_embedding、extractive_qa、nmt/translate、speech/text_to_speech。speech 组**只有 TTS 无 ASR**——识别走 gRPC 流（篇 05），HTTP 面只做一次性合成。

### 2.3 plugin_server：6 端点与 scope-cut 证据链

四基础端点（status/name/list/metrics）+ `/stock/get_ticker`、`/stock/get_stock_price`。`/list` 响应是插件名到能力清单的 fulfillment 目录。stock 端点的 operationId（`get_ticker_stock_yahoo_fin_get_ticker_get`）暴露生成路径：**指向 `stock.yahoo_fin` 插件模块**。插件源码在仓内：`samples/stock_bot/plugins/yahoo_fin.py`（FastAPI APIRouter，Yahoo Finance + AlphaVantage 兜底）。但 **plugin server 宿主不在仓内**——`deploy/docker/dockerfiles/plugin_server.Dockerfile` 只有建用户动作无源码 COPY；这份 openapi 是宿主装 stock 插件后导出的快照。**契约在仓、宿主被裁**，scope-cut 残留的实证形态。

### 2.4 HTTPChatTask：chat_engine 的 webui 消费者（HTTPChatTask.ts）

`getBotList`（70-110）：1s 轮询 `/isReady`（75-82 按 Ready 过滤取 BotName），**变化才 emit** botListUpdated（84-87）；ECONNRESET 无限重试、ECONNREFUSED 按 MAX_RETRIES 递减（91-101）——服务未起时优雅等待。`handleUserFinishedMessage`（134-184）：先 emit typing 气泡（143），POST `/chat` 带 {Query,UserId,BotName}（138-151）；非 200 人话错误（152-158）；**响应双形态**（160-183）——chunked 逐块 parse 累积 CleanedText，否则整包 json；两路取 `Metadata.QueryId` emit `botStartedUtterance`。

## 三、外部连接

HTTPChatTask 经 HTTPClient 单例（`HTTPClient.ts:29-42`）拼 `HTTP_CHAT_URL`（默认 9000）；interactionModes 仅 TEXT（45）——语音不走 HTTP。nlp/plugin 在 webui 零消费，客户端是 bot 运行时（sample 的 model_config/plugin_config.yaml）。`/event` 与 gRPC Event rpc（`ace_agent.proto:107`）同语义不同面。

## 四、数据流

webui `server` 模式文本链：浏览器 WS→WebSocketTask 事件化→HTTPChatTask POST `/chat`→Chat Engine 走 bot pipeline（内部可调 nlp/plugin）→chunked 流式响应→`botStartedUtterance`→浏览器。bot 清单链：轮询 `/isReady`→`botListUpdated`→前端下拉（`App/index.tsx:106`）。上下文 CRUD 由外部编排消费。

## 五、设计决策（从代码反推）

1. **一功能两面**：Chat/Event/上下文在 gRPC 与 HTTP 各有一套（snake_case vs PascalCase）——服务不同消费者：低延迟流式走 gRPC，通用集成走 HTTP。字段命名不统一是两代 API 演进的痕迹，对接时不能想当然互译。
2. **isReady 兼作 bot 目录**（75-87）：健康检查与业务发现合一，省一个 listBots 端点；代价是 Ready 字段双重语义。
3. **chunked 流式但不 SSE**：`/chat` 用 Transfer-Encoding chunked 逐块发 JSON（HTTPChatTask:160-174 每块独立 parse），不是 text/event-stream——客户端实现更简单（标准 fetch reader），但块边界必须恰好是完整 JSON，服务端序列化纪律是隐式契约。
4. **CleanedText 双版本设计**：Text 给 TTS（保留 SSML）、CleanedText 给 UI（剥标签）——一个响应同时服务两条下游，前端只取 CleanedText（170/180）。
5. **openapi 即裁剪边界文档**：plugin_server 的宿主不在仓内，但契约+Dockerfile+插件源码三件齐全——开源了接口形状与插件样例、裁掉宿主。这份 json 是**生成物快照**而非源码伴生文档。
6. **重试策略分级**（91-101）：ECONNRESET 无限重试（网络抖动）、ECONNREFUSED 限次（服务未起）——同一 catch 里两种错误两种命运，比一刀切的退避更贴近故障语义。

## 六、新人提示

- **对接 chat_engine 先核对 PascalCase**：字段名 Query/UserId/BotName 不是习惯的 snake_case，用 gRPC 直觉写 JSON 会收到 422（Pydantic 校验）。
- **chunked 解析别攒缓冲**：HTTPChatTask 每块独立 JSON.parse（169）；若块被网络分片打断会解析失败——生产环境加 try 或按行分隔协议改造。
- **/isReady 轮询别加急**：1s 间隔已足够（106）；bot 热重载后清单变更最多延迟一拍。
- **给 plugin_server 加插件**：仿 `yahoo_fin.py` 的 APIRouter 模式放 samples/<bot>/plugins/，宿主扫描装载；openapi 是宿主重新导出的，手改无意义。
- **nlp_server 的 embedding 端点**是 RAG bot 向量来源，与 gRPC 侧不重叠。

## 甄别记录

任务书称 "plugin_server /stock 端点指向被裁区=scope-cut 残留"；源码实证细化为：**插件源码在仓内**（`samples/stock_bot/plugins/yahoo_fin.py`），**被裁的是 plugin server 宿主实现**（仓内仅 openapi 快照 + 无源码的 Dockerfile）——"残留"的是宿主接口契约而非插件代码。三契约 10+11+6=27 端点与任务书一致。
