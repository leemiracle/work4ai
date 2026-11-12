# 11 · ACE Agent samples 两代表——rag_bot 与 npc_bots

> 源：`microservices/ace_agent/4.1/samples/rag_bot/`（actions.py/plugins/colang/RAG 栈）与 `microservices/ace_agent/4.1/samples/npc_bots/`（elara/jin/plugins）；对照 4.0 版与 `deploy/ucs_apps/speech_bot/`

## 一、角色定位

ACE Agent（对话中间件，与 Tokkio 的 pipecat 线不同代不同轨）的样例双子星：**rag_bot** 演示"ACE Agent + 外挂 RAG chain server"——检索问答不进对话逻辑，全部转投独立部署的 RAG 服务（README.md 明言 "ACE Agent is not responsible for document ingestion"）；**npc_bots** 演示"游戏 NPC 的 LLM 人格化"——1860 年 Willowbrook 村两个角色（elara 鬼屋向导 / jin 拉面店老板），性格是**数值化八维参数**，运行时可经 Chat Engine API 动态改。两者共用同一套骨架：colang 对话流 + NeMo Guardrails actions + plugin-server fulfillment 插件 + riva 语音配置，是"如何用 ACE Agent 造 bot"的两份官方模板。

## 二、内部结构

### 2.1 rag_bot：三件插件 + colang 流 + RAG 后端栈

- **plugins/rag.py**（214 行）：`/chat`（rag.py:155-183）取 `Metadata.ChatHistory` 委托 stream（:85-152）——问题拼固定后缀"≤75 字符回答"（:93-95），request_json 带 temperature 0.2/seed 42/stream True（:97-107），aiohttp POST `/generate`，逐 chunk `chunk[6:]` 剥 `data: ` 前缀（:121-124，与 08 篇同一手法），包 ChatResponse JSON 逐块 yield，末尾补 `IsFinal` 帧（:147-150）；`/event`（:186-214）对三个系统事件回免响应；**`/rag_endpoint_url` GET/POST（:46-82）运行时热切端点**。
- **plugins/utils.py**：validate_url 正则只认 `http(s)://IP:port`（utils.py:14）——localhost/域名/带路径全拒，端口上界 99999 也不严谨。
- **colang/main.co**：`generate rag response` 流（main.co:8-18）`InvokeStreamingChatAction(endpoint="rag/chat")`+while 循环逐段 `bot say`；`rag` 流（:20-22）挂用户话语。
- **RAG/ 目录**：basic_rag 与 slm_rag 两套 docker-compose + NIM 微服务栈 + 向量库三选（milvus/pgvector/redis 按 profile）——端到端后端全家桶。

### 2.2 npc_bots：双角色目录 + 共享插件层

- **角色卡**：elara/plugin_config.yaml 给 slm_responder 注入整页角色卡（Thornbrook 家族史、Blackwood 鬼屋传说、"STRICTLY PLAY ELARA"指令）+ 八维参数 quality 9/humour 2/**creativity 7/helpfulness 8**；**jin** 同构反着调：拉面店老板、怕帮派头目 Kumon Aoki，**creativity 3/helpfulness 2**——同引擎不同参数即两种性格。
- **plugins/prompt_former.py**（119 行）：`POST /get_prompt`（prompt_former.py:26-59）以 `param.get("slm_responder")` 为底、请求 context 覆盖八维+player_name，formulate_custom_instructions（:62-119）拼 **Nemotron 专用 `<extra_id_1>` 提示词**——每轮 assistant 消息前置 `quality:9,toxicity:0,...` 数值串。
- **plugins/slm_responder.py**（174 行）：AsyncOpenAI 指向 integrate.api.nvidia.com（:39-43），默认 `nvidia/nemotron-mini-4b-instruct`（:52-54）；**:45 模块加载期 `get_prompt()` 取一次默认值**——动态通道在形参上，仓内调用方不传 context。
- **colang**：elara.co:8-18 打 `/slm_responder/chat` 流式取台词；玩家名缺省 "Kai"（:22-23）；speech.co 头注释即转写时序文档（partial 160ms/interim 240ms 静音/final 800ms 静音）。
- **actions.py**（54 行）：IsSpuriousAction（actions.py:46-54）FILTER_WORDS 词表（:19-41）+3 字符门滤碎片转写，白名单只放 "hi"（:43）。
- **speech_config.yaml**：elara 声线 Female-**Fearful**（elara/speech_config.yaml:32）+a2f 段挂 dragon 化身（:41-42）；rag_bot 是 Female-1 且**无 a2f 段**（rag_bot/speech_config.yaml:30）——文本 bot 与数字人 bot 的分界线。

## 三、外部连接

**上游**：`aceagent plugin-server deploy --config plugin_config.yaml` 起插件服务、`aceagent chat web --config bots/npc_bots` 托管多 bot（README.md 部署节）。**下游**：RAG chain server（GenerativeAIExamples）、NIM API（integrate.api.nvidia.com）、riva（model_config.yaml 的 localhost:8001，ASR parakeet-1.1b+TTS fastpitch-hifigan）。**部署侧对应物**：`deploy/ucs_apps/speech_bot/rag_bot/app-params.yaml:4` 的 `chatEndpointPrefix: "rag"` 是 K8s 形态下同一约定的参数化；npc_bots 的 ucs 版 app-params 指 `jin/speech_config.yaml`。**代际对照**：4.0 用 colang 1.0（`flows.co` 的 `define flow user ... execute chat_plugin`），4.1 全面切 colang 2.x（`flow` 语法）；4.0 rag_bot_config 是 `streaming: True`，4.1 增 `use_stateful_guardrails: True`、streaming 缺省。

## 四、数据流

rag_bot：用户话→ASR→speech.co 三级转写甄别（IsSpuriousAction 滤噪）→main.co `rag` 流→打插件 `rag/chat`→ChatEngine 组 ChatRequest（UserId/Query/Metadata.ChatHistory）→rag.py POST RAG /generate→SSE 逐块回 ChatResponse JSON→bot 话语流→TTS。npc_bots 同构打 `/slm_responder/chat`：用**模块加载期取好的 prompt**（:45/:70）+历史+问题打 NIM。游戏侧上下文走旁路：`/updateUserContext` 把八维键值挂用户上下文，README 称 fulfillment 可见——仓内兑现路径是 prompt_former 的 context 形参。

## 五、设计决策

1. **"bot 名前缀"约定换零配置启停**：README 钉版"bot 名以 rag 前缀开头即启用 RAG policy"——但样例实名 genai_rag_bot，且裁决逻辑在闭源 aceagent Chat Engine 内，仓内不可验；**仓内可见的机制只有两端**：colang 的 endpoint="rag/chat"（main.co:9）与部署侧 chatEndpointPrefix: "rag"（app-params.yaml:4）。改 bot 名前请以这两处为准。
2. **人格数值化**：八维 0-9 参数 + instructions 长文分离——长文定"知道什么"，数值定"怎么说"；运行时改数值即改性格，不动部署。
3. **actions.py 三胞胎**：elara/jin/rag_bot 三份 md5 全同（d5c0d844…）——转写降噪是所有语音 bot 的公共守门员，复制分发而非抽公共库，样例代码自包含优先。
4. **validate_url 只认 IP:port 是特性也是坑**：热切换端点文档示例就是 `http://10.222.22.23:8081`（rag.py:62），面向集群内 IP 直连场景；用域名部署 RAG 的用户会被正则拦在门外。
5. **prompt 在 import 期定格**：slm_responder.py:45 只调一次 get_prompt——八维动态覆盖的通道存在（形参）但仓内无人走，真正的运行时个性化要靠改这行或在 ChatEngine 侧接 /get_prompt。

## 六、新人提示

- 起 npc 双 bot 记得先起 plugin-server（README 部署顺序），`/slm_responder/chat` 404 多半是插件服务没起或 path 打错（colang 里带斜杠、rag_bot 里不带，两处风格不一致）。
- 热切换 RAG 端点用 POST /rag_endpoint_url 传 `http://<IP>:<Port>` 字面量，别带路径或 localhost。
- 想换 NPC 声线：elara 的 Female-Fearful 在 elara/speech_config.yaml:32；三份 speech_config 的 a2f 段有无决定能不能接 3D 脸。
- colang 1.0 项目迁移看 4.1/samples/colang_1.0/ 目录（同 bot 的旧语法保留版），对照改写最直观。
- `{$player_name}` 占位符由 prompt_former 的 character_details["player_name"] 填（prompt_former.py:56），不传则字面上桌。

## 甄别记录

任务书称 "bot 名 rag 前缀即启用 RAG policy 的约定"；源码实证：该约定**仅见于 README 文字**，样例 bot 名 genai_rag_bot 并不以 rag 开头，裁决代码在闭源 aceagent 包内（仓内 grep 零命中）——仓内可实证的机制是 colang endpoint（main.co:9-11）与部署侧 chatEndpointPrefix（app-params.yaml:4）。任务书称 "actions.py 三套逐字节相同" 经 md5 验证成立（d5c0d844abb3db33c892b9b517877388）。
