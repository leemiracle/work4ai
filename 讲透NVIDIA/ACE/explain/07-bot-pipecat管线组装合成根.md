# 07 · bot.py——pipecat 管线的组装合成根

> 源：`workflows/tokkio/5.0.0-ga/src/llm-rag/src/bot.py`（276 行）；配套 `config.py`（72 行）、`otel.py`、`entrypoint.sh`

## 一、角色定位

bot.py 是 Tokkio llm-rag 参考实现的**合成根（composition root）**：FastAPI 应用（`bot.py:270`）挂两条路由（websocket/register，`bot.py:271-272`），真正的核心是 `create_pipeline_task(pipeline_metadata)`（`bot.py:97`）——ACEPipelineRunner 的回调工厂（`bot.py:273`），每来一路视频流会话就现场装配一条完整 pipecat 管线。它自己不实现任何 AI 能力：ASR/LLM/TTS/面部动画全部来自 `nvidia_pipecat` 包与同目录三个扩展文件（tokkio_llm/tokkio_rag/serializer，`bot.py:32-33`、`bot.py:19`）。模块尾部 `uvicorn.run(app, host="0.0.0.0", port=8100)`（`bot.py:275-276`）只是直跑兜底——容器内实际由 entrypoint.sh 以 `APP_NAME=src.bot:app`、PORT=8000 拉起（`entrypoint.sh:14-16`）。

## 二、内部结构

### 2.1 模块级初始化（一次性，先于任何会话）

`.env` 加载并把全部键值打进日志（`bot.py:70-76`，泄密面提示）；日志定级 DEBUG（`bot.py:78`）；**Config 从 CONFIG_PATH 的 YAML 反序列化**（`bot.py:80-83`），pydantic 强校验；**AnimationGraphService 动画库预生成**（`bot.py:85`）——启动期把姿态/手势数据库算好，会话期零开销；Redis 客户端从 REDIS_URL 手工切串解析（`bot.py:87-91`）；OTEL 采集器探活失败直接 raise 拒绝启动（`bot.py:93-95`，除非 `OTEL_SDK_DISABLED=true`）。

### 2.2 create_pipeline_task 装配序（97-268）

1. **trace 续链**：从 Redis hash `trace_contexts` 按 stream_id 取 W3C 上下文包进 `ace-pipeline` span（`bot.py:100-106`）。
2. **transport**：`ACETransport`（websocket + TokkioUIWebSocketSerializer + rtsp_url + SileroVADAnalyzer，`bot.py:107-114`）——控制面 WS JSON，音视频 RTSP。
3. **渲染侧**：`Audio2Face3DService`（gRPC 到 `A2F_GRPC_URL` 默认 0.0.0.0:50010、16kHz/16bit、`send_silence_on_start=True` 先推静默防黑脸，`bot.py:116-121`）；`AnimationGraphService`（REST 8020 + gRPC `ia-animation-graph-microservice:51000` + Redis 代理，`bot.py:124-131`）。
4. **行为处理器**：PostureProvider（`bot.py:133`）、UserPresence 欢迎告别语（`bot.py:135-137`）、Proactivity 主动搭话（`bot.py:138-141`）。
5. **大脑三选一**（`bot.py:143-169`）：`TokkioNvidiaLLMService` / `TokkioOpenAILLMService` / `TokkioNvidiaRAGService`——串行 if 而非 elif，但 Literal 类型（`config.py:16`）保证只命中一个。
6. **语音**：`RivaASRService`（RIVA_SERVER_URL 默认 localhost:50052，模型 `parakeet-1.1b-...-silero-vad-asr-bls-ensemble` 自带 VAD，`bot.py:182-187`）；TTS 是**云端 ElevenLabs**（voice cgSgspJ2msm6clMCkdW9、eleven_flash_v2_5，`bot.py:188-196`）。
7. **上下文**：化身名注入 prompt（`{name}` 替换，`bot.py:202-206`）→ `OpenAILLMContext`（`bot.py:215`）→ `llm.create_context_aggregator`（`bot.py:218`）。
8. **Pipeline 阵列**（`bot.py:227-255`）：`transport.input → user_presence → stt → stt_sync → ctx.user → llm → proactivity → tts → tts_sync → rag_multimodal → a2f → posture → animgraph → ctx.assistant → transport.output`。
9. **PipelineTask**：`allow_interruptions=True`、metrics 双开、start_metadata 带 stream_id、`cancel_on_idle_timeout=False`（`bot.py:257-266`）。

## 三、外部连接

**上游**：entrypoint.sh→uvicorn→`src.bot:app`；ACEPipelineRunner（enable_rtsp=True，`bot.py:273`）注入 PipelineMetadata。**下游**：Riva(50052)、ElevenLabs API、A2F(50010)、AnimationGraph(8020/51000)、Redis（trace+动画代理）、可选 RAG chain server(config.yaml:8081)、NIM/OpenAI 端点。**同目录协作**：config.py 供 Config 模型；customization-notebooks 03/04/07/09/10 五册以此为改装配靶文件（图谱 related 边实证）。

## 四、数据流

一次语音问答：浏览器→WS（JSON）+RTSP（音视频）→transport.input→VAD 判说话→RivaASR 流式转写→UserTranscriptSynchronization 对齐字幕→context aggregator 入 user 轮→LLM/RAG 流式回 TextFrame→Proactivity 拦静默→ElevenLabs 合成 16kHz PCM→BotTranscriptSynchronization→RAGMultimodalResponseProcessor 顺路把引用转 custom_view→A2F 吃 PCM 产 blendshape→posture/animgraph 产动画→context aggregator 收 assistant 轮→transport.output 回浏览器。打断帧双向穿透，TTS/A2F 立即让路。

## 五、设计决策

1. **工厂回调而非常驻管线**：每流一管线，会话隔离天然成立，代价是每会话重建十余服务对象（AnimationGraph 靠 `bot.py:85` 预生成摊平最贵一段）。
2. **ASR/TTS 非对称选型**：ASR 本地 Riva（低延迟流式），TTS 云端 ElevenLabs（音色质量）——数字人延迟敏感段留在边缘，音质敏感段上云。
3. **推测语音处理整段注释保留**（`bot.py:217-223`、`bot.py:234-252`）：create_nvidia_context_aggregator/NvidiaTTSResponseCacher 成对开关，是文档级 feature flag。
4. **两处死代码痕迹**：`riva_server_ip.replace("http://", "")`（`bot.py:181`）返回值被丢弃——str 不可变，剥协议前缀实际从未生效；`RivaTTSService` 只 import（`bot.py:48`）从不实例化。
5. **trace 上下文走 Redis 而非帧内传递**：控制面（建会话者）与数据面（管线）解耦，跨进程续链。

## 六、新人提示

- 改装配先看 customization-notebooks 对应册（03 换声音/06 换 LLM/07 换 TTS 供应商），那是官方给的改此文件剧本。
- `config.Pipeline.llm_processor` 是唯一换脑开关；三段配置（NvidiaRAGService/NvidiaLLMService/OpenAILLMService）都在 config.py 是必填段，少一段 pydantic 直接 ValidationError。
- 会话级 bug 先查 `bot.py:100` 的 trace 链——Redis 里缺 trace_contexts 键只是降级（trace_context=None）不报错。
- 直跑 `python bot.py` 起在 8100，容器里是 8000——排查端口先确认运行形态。
- 注意类名拼写 `UserPresenceProcesssor`（三个 s）——config.yaml 的段名同拼法（config.py:64）， typo 已是契约。

## 甄别记录

任务书称 "TokkioBot 合成 root"；源码实证：**仓内无 TokkioBot 类**（全仓 grep 零命中），合成根是模块本身 + `create_pipeline_task` 工厂函数。任务书提到的 "request_json 死参数痕迹" 实际位于 `tokkio_rag.py:117-128`（vdb_top_k/reranker_top_k 形参收下但请求体里被注释），不在本文件——详见 08 篇。
