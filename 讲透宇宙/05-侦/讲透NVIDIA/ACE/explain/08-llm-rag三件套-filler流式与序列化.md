# 08 · tokkio_rag / tokkio_llm / serializer——llm-rag 三件套

> 源：`workflows/tokkio/5.0.0-ga/src/llm-rag/src/` 下 `tokkio_rag.py`（219 行）、`tokkio_llm.py`（139 行）、`serializer.py`（126 行）

## 一、角色定位

三个文件是 bot.py 合成根的三块"插座板"：**tokkio_llm.py** 给两家 LLM 服务（NVIDIA NIM / OpenAI）统一挂上"filler 填充语"能力——首 token 迟到超过 time_delay 秒就让数字人先说句"Let me think"垫场（`tokkio_llm.py:9-14` 模块 docstring 自述）；**tokkio_rag.py** 对 NvidiaRAGService 做同款扩展，RAG 检索慢时同样垫话（`tokkio_rag.py:10-19`）；**serializer.py** 是 pipecat 帧与浏览器 JSON 消息的双向翻译器（`serializer.py:42`），前端字幕/自定义视图/按钮事件全靠它过闸。三者都不改 pipecat 框架本身，全部以"继承重写 `_process_context`"或"实现 FrameSerializer"的方式插进去。

## 二、内部结构

### 2.1 TokkioLLMServiceMixin——filler 机制的唯一实现（tokkio_llm.py:46-113）

`_process_context_common(context, stream_chat_completions)` 是模板方法：起 TTFB 指标（:55）→ `monitor_request_time` 协程 `asyncio.sleep(time_delay)` 后若首 chunk 未到且未说过填充语，`random.choice(self.filler)` 选一句 `push_frame(TTSSpeakFrame(...))`（:62-68）→ 主流程 `await stream_chat_completions(context)` 拿流（:74）→ 首个 chunk 到达即 cancel 监控任务（:76-88）→ 逐 chunk 按**两种格式**剥文本：OpenAI 风格 `chunk.choices[0].delta.content`（:91-94）、NVIDIA 风格 `chunk.content`（:96-98），都转 TextFrame 下推；异常路径推 `TTSSpeakFrame("Cannot connect to the LLM endpoint")` 让数字人亲口报错（:102-104）；finally 兜底再 cancel 一次监控任务（:106-113），防泄漏。两个子类 `TokkioNvidiaLLMService`（:116-126）与 `TokkioOpenAILLMService`（:129-139）只是 `基类+Mixin` 多继承再把 `_process_context` 委托给 common。

### 2.2 TokkioNvidiaRAGService——filler + 流式 RAG（tokkio_rag.py:49-219）

`__init__` 收 `filler`/`time_delay` 存自身，其余 RAG 参数透传父类（:50-86）；`_get_rag_response` POST `{rag_server_url}/generate`、超时 15 秒、`@traced` 挂 OTel span（:88-91）。`_process_context`（:93-218）：① 逐消息校验 role ∈ system/user/assistant 否则抛异常（:98-100）；② `suffix_prompt` 倒序找**最后一条** user 消息追加约束（:103-107，如"75 字符内回答"）；③ 组 `request_json`（:117-128）；④ filler 监控任务与 LLM 版同构（:140-149）；⑤ `resp.aiter_lines()` 逐行消费——`chunk[6:]` 剥 `data: ` 前缀再 `json.loads`（:172-177，与 rag_bot 插件 rag.py:121-124 同一招），文本进 `full_response` 并推 TextFrame（:199-209）；带 `citations` 的行构造 `NvidiaRAGCitation`（document_type/id/name/content.encode()/metadata/score 六字段，:180-189）打成 `NvidiaRAGCitationsFrame` 推给下游多模态处理器（:200-207）；⑥ `finally resp.aclose()`（:212-213）。外层异常退化为一句 TTS："Cannot connect to the RAG endpoint"（:216-218）。

### 2.3 TokkioUIWebSocketSerializer（serializer.py:42-126）

**serialize**（:47-92）九进一出：presence 起止（:48-55）、tts_update/tts_end（:56-63）、asr_update/asr_end（:64-71）、custom_view 起（`frame.to_json()` 展平+`show_ui:True`，:72-79）止（:80-86）、interruption（:87-91），其余帧返回 None 静默丢弃（:92）。**deserialize**（:94-126）：JSON 解析失败返 None（:97-98）；`conversation_start/end`→presence 帧（:102-105）；`rag_settings` 只收集三个在场的键（collection_name/use_knowledge_base/rag_server_url）打 NvidiaRAGSettingsFrame（:106-114）——**运行时换 RAG 知识库的通道**；`button_pressed` 按 `toggled` 有无分派 UISelectableOptionPressFrame/UIButtonPressFrame（:115-119）；`key_pressed`/`editing_finished`→文本输入帧（:120-123）；未知类型落 None（:124-125）。

## 三、外部连接

**上游**：bot.py:32-33/19 import 三者；audio2face-3d-tuning 的 bot.py 也复用同一 serializer（图谱 imports 边）。**下游**：TTSSpeakFrame 直达 ElevenLabs TTS（bot.py:188）——填充语**只进语音队列不进 LLM 上下文**，对话历史零污染；TextFrame 进 TTS 与字幕；NvidiaRAGCitationsFrame 进 RAGMultimodalResponseProcessor（rag_multimodal_response_processor.py:76 消费）转 custom_view；NvidiaRAGCitationsFrame 的镜像端 NvidiaRAGSettingsFrame 由 nvidia_pipecat 的 RAG 服务消费热切换检索参数。**协议对端**：浏览器 Tokkio UI（六 chart 的 with-ui 变体）；RAG chain server（GenerativeAIExamples 项目，/generate SSE）。

## 四、数据流

RAG 问答全链：用户问句→context aggregator→`_process_context` 拼 messages+suffix→POST /generate（15s）→[time_delay 秒无响应→TTSSpeakFrame 填充语→ElevenLabs→A2F，嘴先动]→SSE 行流回→`data: ` 剥前缀→TextFrame 逐句下推（TTS 边收边合成）+ CitationsFrame 旁路→多模态处理器按 confidence_threshold 过滤出图/表引用→StartCustomViewFrame→serializer 转 `{"type":"custom_view",...}` JSON→浏览器渲染引用卡片。UI 侧反向：用户在设置面板换知识库→`rag_settings` JSON→NvidiaRAGSettingsFrame→下一次 /generate 用新 collection。

## 五、设计决策

1. **Mixin 而非复制**：filler 逻辑写一遍（tokkio_llm.py:48），两家服务共享；tokkio_rag 没用 Mixin 而是整段复制监控任务（tokkio_rag.py:140-149）——因为 RAG 的流是 HTTP 行流不是 SDK chunk 流，模板没法完全统一，NVIDIA 选择了复制而非抽象。
2. **填充语走 TTSSpeakFrame**：绕过 LLM 上下文，说完即弃；用户听感连续，模型历史干净。
3. **死参数三处痕迹**：`__init__` 收 `vdb_top_k=20`/`reranker_top_k=4`（tokkio_rag.py:61-62）但 request_json 里对应两行被注释（:123-124）——**收了不发**；`self.timeout=120`（:70）注释写"端点不可达判据"但实际超时用 :90 的 15.0，timeout 属性全文件零消费。改 RAG 检索深度须先解开这两行注释。
4. **报错也走嘴**：LLM/RAG 连不上时 push TTSSpeakFrame 而非仅记日志——数字人场景里静默失败等于黑脸挂机。
5. **serializer 白名单式丢帧**：serialize 对未列帧返 None，pipecat 静默吞——加新 UI 能力必须同步扩 serializer，否则帧在出口蒸发。

## 六、新人提示

- 调 filler 手感改 config.yaml 的 `Pipeline.time_delay/filler`（默认 2.0 秒/"Let me think"/"Hmmm"），不用动代码。
- `chunk[6:]` 隐含约定服务端 SSE 行以 `data: `（含空格共 6 字符）开头；RAG chain server 换实现先核对这里。
- suffix_prompt 只追加最后一条 user 消息（倒序扫描 :104-107），多轮对话中历史消息不会被重复加约束。
- serializer 的 deserialize 不处理任何音频/视频——媒体走 RTSP/WebRTC 通道，这里只有控制面文本协议，别在此找音频路径。
- `content.encode()`（tokkio_rag.py:185）把引用正文转 bytes——下游 ImageBlock 按 base64 解码（rag_multimodal_response_processor.py:146-151），链条是 bytes 对 bytes。

## 甄别记录

图谱 summary 称 tokkio_rag "_get_rag_response 调 /generate 流式接口"无误；但称 "timeout 120 为请求超时"（tokkio_rag.py:70 注释原话）与实证不符——真实生效超时是 `_get_rag_response` 的 `timeout=15.0`（:90），self.timeout 零消费点，属注释性死参数。任务书 "request_json 死参数痕迹" 确认坐实在 :123-124。
