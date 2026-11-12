# NVIDIA ACE 新人上手文档（ONBOARDING）

> 基于仓内知识图谱写作（commit `92a0ac1a`，487 节点/687 边/16 层/16 步导览）；行号锚于 2026-11-06 源码核实。

## 1. 一句话定位

NVIDIA ACE 是**生成式 AI 数字人**技术套件样例仓：`README.md:4` 定义其为"用生成式 AI 赋活数字人的技术集合"，仓内是使用 ACE NIM 微服务的样例与参考应用；微服务容器本体（Riva/Audio2Face/AnimGraph/ACE Agent，技术表 `README.md:17-29`）须通过 **NVAIE 评估许可从 NGC 获取**（`README.md:8`）——编排与客户端代码开源、模型镜像走商业许可。给游戏 NPC（npc_bots）与数字客服（tokkio）集成者用。两条主线：`microservices/`（ACE Agent 4.1 契约+Web UI+样例；A2F 1.2 协议族）与 `workflows/tokkio/5.0.0-ga`（Aki 化身全栈+六套 Helm 变体）。

## 2. 仓库全景（16 层）

依赖走向：**契约（L2-L4）→ 服务编排（L5-L6）→ 前端（L7-L9）→ 样例（L10-L12）→ A2F 落地（L13）→ tokkio 全栈（L14-L16）**。

- **L1 总览与基线**：根 README、`.gitattributes`（LFS）、`tools/`（Avatar Configurator+UCS Tools）。
- **L2 gRPC 契约**：AceAgentGrpc 17 rpc（`proto/ace_agent.proto:24`），语音管线生命周期与双向音频流。
- **L3 REST 契约**：三份 OpenAPI——chat_engine（/chat、/event、用户上下文）、nlp_server（NLU/TTS）、plugin_server（插件管理）。
- **L4 A2F 协议族**：nvidia_ace proto 族（a2f.v1 音频换 blendshape、animation_data.v1 动画流、controller.v1 情绪联动）+生成器与 wheel。
- **L5 server 会话编排**：`index.ts` 起 7007 WebSocket；`ChatSessionTask` 会话总管装配六类子任务。
- **L6 server 支撑**：buf/connect-es 生成的 gRPC TS 栈、473 行 UMIM 事件类族、emoji 语义检索。
- **L7 前端组件**：十一个 React 组件——BotFace 音量驱动头像、对话流、双模输入。
- **L8 前端状态与音频**：useServerState 状态机；useMicrophone 采 16kHz PCM；useAudioPlayer 流播+barge-in。
- **L9 工程化与容器**：Vite 5+React 18；compose 四种 server 模式；`shared/types.ts` 共享协议（全图 fanIn 最高）。
- **L10 npc_bots**：jin/elara 双 NPC，角色卡注入+SLM 流式台词。
- **L11 rag_bot**：bot 名 rag 前缀触发 RAG policy，可切 milvus/pgvector/redis。
- **L12 客户端三形态**：chat_client（HTTP）/speech_client（gRPC 语音）/event_client（Textual TUI 仿真器）。
- **L13 A2F 部署**：quick-start 三容器；api_client（NVCF）/interaction（本地双向流）/validation（A2F→动画图→渲染器全链）。
- **L14 tokkio llm-rag**：`bot.py` 以 FastAPI+nvidia_pipecat 组装全管线（ACE Controller 开源参考）。
- **L15 tokkio 六 Helm 变体**：1/3/6 流 × 有无 UI 同构伞 chart+UCS 拓扑。
- **L16 定制教学**：十二本 notebook；`start_dev.py` 本机改码注入集群。
## 3. 核心链路一：ACE Agent 会话编排

**入口**：`webui/server/index.ts:147` 解析 `--ace-agent-text-chat-interface`（server/grpc/event 三选一，`:156` 校验）与 `--speech`，按 SSL 环境变量定 wss/ws，7007 起 WebSocket；每连接 `new ChatSessionTask`（`:172`）；event 模式额外初始化 EmojiFinder（`:165`，emoji 加载可耗时数分钟）。

**会话总管**：`ChatSessionTask.ts:55` 按模式装配——grpc 挂 GRPCTextTask（`:151`）或语音下 GRPCSpeechTask（`:173`）；event 挂 UMIMTask（`:159`，事件流已含转写）；server 挂 HTTPChatTask（`:167`）；WebSocketTask 恒挂（`:142`）翻译成 WS 帧。六任务共享 AbstractTask（AbortController 停止信号）与 eventBus。三客户端单例：HTTPClient 打 `/chat`、GRPCClient 连 GRPC_URL（`GRPCClient.ts:37`，默认 50055）、RedisClient 订阅 UMIM 事件流。

**17 rpc**（`ace_agent.proto:24` 起）：管线 CreatePipeline(`:28`)/FreePipeline(`:33`)；音频 SendAudio 客户端流(`:37`)/ReceiveAudio 服务端流(`:41`)/StreamSpeechResults(`:48`)；识别控制(`:54-58`)；参数状态(`:62-70`)；SynthesizeSpeech(`:80`)；用户上下文 CRUD(`:86-103`)；Chat(`:110`)/Event(`:114`)。TS 客户端由仓内 proto 经 buf 生成（`server/grpc/gen/ace_agent_pb.js`）。

**前端**：`useServerState.ts:256` 建 WS、`:383` useReducer 状态机；协议类型唯一事实源 `shared/types.ts`。`linear-pcm-processor.worklet.js:24` 80ms 攒块、`:52` Float32→Int16。`docker-compose.yml:66-80` 四种 server 模式。三最小客户端对照三模式（`speech_client.py:49,94,106,154`：CreatePipeline→SendAudio→ReceiveAudio→FreePipeline）。**动画出口**：bot 音频既回传浏览器，也由部署侧 A2F/AnimGraph 消费成面部动画（下节）。

## 4. 核心链路二：tokkio 工作流（llm-rag pipecat 管线）

后端即 `src/llm-rag/src/bot.py`（276 行）：FastAPI 挂 websocket 路由，`ACEPipelineRunner(enable_rtsp=True)` 按流起管线，uvicorn 8100（`:275`）。管线拓扑（`create_pipeline_task` `bot.py:97`，`:231-253` 数组即顺序）：

```
ACETransport(SileroVAD:112) → user_presence → RivaASRService(:182, parakeet-1.1b)
→ 转写同步 → context.user() → llm(:143-165 三通道) → proactivity(主动搭话)
→ ElevenLabsTTS(:188, eleven_flash_v2_5) → 转写同步 → RAG 引用可视化
→ Audio2Face3DService(:116) → posture_provider → AnimationGraphService(:124)
→ context.assistant() → transport.output()
```

三通道 LLM 由 `configs/config.yaml:5` 的 `llm_processor` 单选：NvidiaLLMService（llama-3.1-8b）/NvidiaRAGService（:8081）/OpenAILLMService（gpt-4o）。`tokkio_llm.py:64` filler 填充语：超 `time_delay`（2.0s）未出首块先说 "Let me think" 降感知时延；`tokkio_rag.py` 对接 RAG chain 转发引用帧。**A2F→AnimGraph 是动画链末两跳**：A2F 把 TTS 音频换 blendshape，AnimGraph 驱动 Unreal 渲染器出像素流。

## 5. 六 Helm 变体与 Aki 人格单一事实源

`llm-rag/tokkio-{1,3,6}stream-{no,with}-ui` 六目录。**六份 Chart.yaml 逐字节相同**（md5 `159b55b2`），差异在三处：①`tokkio-app-params.yaml`——`ace-controller.replicas`（`tokkio-1stream-no-ui/tokkio-app-params.yaml:4`）与 `maxStreamCapacity`（`:17`）取 1/3/6，流数同步抬 WebRTC/GPU/SDR 副本，with-ui 额外挂 tokkio-ui 注入；②`values.yaml`（421 行）——ui 差异仅 `:370` 一行 `enabled`，3↔6 流差异仅 `:402` `MAX_NUM_SESSION`；③`tokkio-app.yaml`（124 行）UCS 拓扑六份同构——组件 ace-configurator/ace-controller（`:43`，挂 K8s secret+config.yaml`:53`）/三 SDR envoy/animation-graph/unreal-renderer/vms，外部端点 a2f/riva/redis，`connections:`（`:92`）接线。

**七份 config.yaml 逐字节同源**（md5 `7fcbe9f2`）：六 chart 挂载份全是 `src/llm-rag/configs/config.yaml`（91 行）的逐字节副本，`entrypoint.sh:12` 默认 `CONFIG_PATH=./configs/config.yaml` 证实源内即事实源。它定义化身 **Aki** 人格（`config.yaml:21-22`：NVIDIA 虚拟营销专家、单句 100 字符纪律）、三通道 LLM 段、主动搭话计时（`:17`）——**改 Aki 只改这一处**，六部署随 chart 生效。

## 6. 新人 16 步导览摘要

三阶段：**骨架**（①README+UCS 版图；②proto 17 rpc+三 OpenAPI——先读契约再看实现省一半迷路）；**ACE Agent 主线**（③index.ts 三模式→④三客户端→⑤AbstractTask+六任务→⑥UMIM 模型+emoji 检索→⑦gRPC 生成栈→⑧useServerState→⑨前端音频→⑩组件层→⑪npc_bots→⑫rag_bot→⑬三客户端对照——**建议 3→5→13 先跑通 server 模式 chat 最短路径**再下钻）；**A2F 与 tokkio**（⑭quick-start 三容器→interaction 双向流→validation 全链；⑮bot.py 按 §4 顺序读；⑯六变体+定制生态——notebook 十二本（改名/换声/帧处理器/换 LLM/换 TTS 等），`start_dev.py` 本机改 ACE Controller、SDR 切流即时验证）。

## 7. 已知坑与勘误（源码实证）

1. **`validate_url` 只认 IP:port**：`samples/rag_bot/plugins/utils.py:14` 正则不收域名/路径/尾斜杠——热切换 RAG 端点（`rag.py:67`）传 `http://my-rag:8081/` 被拒且不报原因。
2. **`parameters` 模块全仓无文件**：`slm_responder.py:20`、`prompt_former.py:12` 均 `from parameters import param` 而全仓零命中——它是 plugin-server 容器运行时注入的配置读取器，**本仓单跑插件脚本必 ImportError**，非缺文件事故。
3. **nvidia_ace 生成物只在 wheel 内**：`nvidia_ace.*_pb2` 模块不在源码树，只在 `proto/sample_wheel/nvidia_ace-1.0.0-py3-none-any.whl` 二进制里；改协议走 `generate_code_from_protos.py` 重生成+重打包。
4. **六份 Chart.yaml 逐字节相同**：变体差异不在 Chart.yaml，去 params/values 找（§5）。
5. **`files_to_compile.yaml` 重复+漏列**：`:23` 与 `:32` 重复列 `nvidia_ace.animation_data.v1.proto`；实际存在的 `nvidia_ace.services.animation_data.v1.proto` 反不在清单，不进生成物。
6. **`proto/requirements.txt` 重复声明**：`protobuf-gen==0.0.4` 第 1/5 行出现两次。
7. **AudioStream 同名异构**：`nvidia_ace.a2f.v1.proto:29` 与 `nvidia_ace.controller.v1.proto:28` 都定义 `message AudioStream` 但结构不同——a2f 版 oneof 两字段（连接关闭即结束）；controller 版三字段、内嵌 `EndOfAudio`（`controller.v1.proto:30`）须显式发结束标记，`a2f.py:251` 发的是 controller 版。跨包不通用。
8. **scope-cut 与 `/stock` 残留**：图谱裁掉 stock_bot 等 9 样例，但 `plugin_server_openapi.json:98,142` 仍留 `/stock/get_ticker`、`/stock/get_stock_price` 契约——stock 插件在库内唯一痕迹。被裁目录**磁盘仍在**只是图谱不收；引用认准 4.1/1.2/5.0.0-ga 在册版本。

## 8. 与生态的关系及 scope-cut 声明

**生态分工**（`README.md:17-29`+代码实证）：**ACE NIM/NVAIE/NGC** 是微服务许可与分发通道（`README.md:8`），部署里 `nvcr.io/nvidia/ace/*` 镜像（quick-start `docker-compose.yml:18`）均从此来。**Riva** 供 ASR（`bot.py:182`）；TTS 位默认由云端 **ElevenLabs** 承担（`bot.py:188`）——ASR 本地化、TTS 云端是 tokkio 5.0 默认取舍（notebook 07 演示换回）。**pipecat/nvidia_pipecat** 是开源实时语音对话框架，`bot.py:27-53` 显示 NVIDIA 在其上叠 ACETransport/Riva/A2F 等适配层——tokkio 本质是 pipecat 的全家桶预组装。**A2F/AnimGraph/Unreal** 是音频→blendshape→动画→像素流的渲染链，可独立消费（NVCF 通道 `nim_a2f_client.py:36`）。**UCS/UCF**（`tools/ucs_tools/README.md`）是部署拓扑框架——六变体的"参数表差异"正源于此。**ACE Controller** 是 tokkio 里跑 llm-rag 的容器角色（`tokkio-app.yaml:43`），与 `microservices/ace_agent` 是两代对话控制器，勿混称。

**scope-cut 声明**（`.understandignore`，2026-11-06 图谱口径）：以下磁盘存在但**未进图谱**——tokkio 4.0/4.1（`:4-5`）与 one-click 样板（`:7`）、ace_agent 4.0（`:9`）、audio_2_face 1.0（`:10`）、4.1 的 deploy（`:12`）与 9 个样例 bot（`:13-22`，留 rag_bot+npc_bots）、媒体资产（`:25-31`）。样例结论只覆盖在册两样例。
