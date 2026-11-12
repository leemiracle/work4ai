# PersonaPlex 新人导读（ONBOARDING）

> 基于仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/personaplex`（commit `3428dfd9`）源码逐文件核实撰写；图谱基线 263 节点 / 516 边 / 16 层 / 16 步 tour。文中行号锚均已验证。

## 1. 一句话定位

PersonaPlex 是 NVIDIA 开源的**实时全双工语音对话模型服务栈**：基于 Kyutai Moshi 架构与权重微调（arXiv 2602.06053，模型 `nvidia/personaplex-7b-v1`），卖点是**人格控制**——文本角色提示词（text prompt）决定"说什么"，18 个预置音色嵌入（voice prompt，NAT/VAR 两族）决定"用什么声音说"。服务三类人：推理工程师（`moshi/` Python 服务端 + Docker）、前端（`client/` React 客户端）、评测研究者（`moshi.offline` + `assets/test/` 夹具）。可打断、可插话、12.5 帧/秒低延迟，本质是"打电话"而非"对讲机"。

## 2. 仓库全貌

双语言单体仓。服务端 Python 约 7460 行（26 文件），客户端 TS 约 2860 行（41 文件）：

```
personaplex/
├── README.md / LICENSE-MIT      # 唯一全景文档；代码 MIT，权重 NVIDIA Open Model 许可
├── Dockerfile / docker-compose.yaml  # CUDA 12.4.1 + uv + moshi.server --ssl，8998；GPU×1 + .cache 卷
├── assets/test/                 # 离线夹具：input_assistant.wav(40s)/input_service.wav(20s)/prompt_service.txt
├── moshi/                       # Python 包（Kyutai MIT + Meta audiocraft MIT 双上游许可）
│   ├── pyproject.toml           # moshi-server / moshi-offline 两个控制台入口
│   └── moshi/
│       ├── server.py            # WS 推理服务主入口（路由 /api/chat）
│       ├── offline.py           # NVIDIA 新增：离线 WAV→WAV 评测
│       ├── client_utils.py      # 终端彩色令牌流渲染
│       ├── models/              # lm.py(LMGen 核心)/compression.py(Mimi)/loaders.py(HF 权重)
│       ├── modules/             # 流式积木：streaming/conv/seanet/transformer/rope/gating/resample
│       ├── quantization/        # RVQ 三件套（core_vq/vq/base）
│       └── utils/               # compile(CUDA graph)/sampling/connection(TLS)/logging
└── client/
    ├── vite.config.ts / .env.local   # dev 强制 https(麦克风要求)；/api 反代 → moshi.chat 排队后端
    ├── public/assets/           # decoderWorker.min.js/.wasm 预编译产物
    └── src/
        ├── app.tsx              # 单一路由 "/" → Queue
        ├── audio-processor.ts   # AudioWorklet 抖动缓冲（渲染线程）
        ├── protocol/ · decoder/ # 二进制 WS 协议 / Opus 解码 worker 预热池
        └── pages/Queue/         # 首页(麦克风+底座就绪) 与 pages/Conversation/(会话主战场)
```

服务端约半数是 vendored 的 Kyutai/Meta 推理代码；NVIDIA 增量集中在 `server.py` 的 voice prompt 接线、`offline.py` 整文件、`utils/logging.py` 与整个 `client/`。

## 3. 核心架构：端到端全双工链路

"**两个神经网 + 一条 WebSocket + 两端各自的 Opus 编解码**"：

```
浏览器                                   GPU 服务端
麦克风 getUserMedia                        sphn.OpusStreamReader
 ↓                                        ↓ PCM 攒 1920 样本/帧(24kHz÷12.5fps)
opus-recorder encoder worker ──0x01──▶  Mimi.encode → 8 码本音频 token
(24kHz/20ms 页)                            ↓ 逐帧
                                          Moshi LM（LMGen.step：主干+Depformer）
AudioWorklet 抖动缓冲                       ↓ 文本 token + agent 音频 token
 ↑ Float32 帧                              Mimi.decode → PCM → OpusStreamWriter
WASM Opus 解码 worker ◀──0x01/0x02────── 文本以 b"\x02"+text 推送
```

**服务端**（`moshi/moshi/server.py`）：`main()` L357-479 从 HF 拉三件权重（`loaders.py` L42-45，repo `nvidia/personaplex-7b-v1`），加载**两个 Mimi 实例** + Moshi LM 组成 `ServerState`，`warmup()` 跑 4 帧零输入预热 CUDA graph，挂 aiohttp 路由 **`/api/chat`**（L460；非上游文档说的 `/ws`）。`handle_chat()` L135-309 整个会话包在 `async with self.lock` 里——**全局锁，单卡同时只服务一个会话**，这是客户端排队体系存在的根因；先加载音色与文本提示词（`wrap_with_system_tags` 包 `<system>...</system>`），跑 `step_system_prompts_async` 四段预热（voice prompt→音频静音→文本提示→音频静音），**然后才**发 1 字节 handshake `b"\x00"`——所以客户端 connected 要等 handshake 而非 open。三协程：`recv_loop` 喂 Opus 流读取器；`opus_loop` 每 1ms 轮询，攒够一帧就 encode→`LMGen.step`→decode→Opus 写出器，文本 token（跳过 0/3 即 EPAD/PAD，`▁`→空格）发 `b"\x02"+text`；`send_loop` 每 1ms 发 `b"\x01"+Opus`。任一退出即 `FIRST_COMPLETED` 强杀其余。

**客户端**：Queue 页就绪音频底座（AudioContext、Worklet 模块、解码 worker 预热、麦克风授权）后切 Conversation；Conversation 把参数拼进 `/api/chat` WS URL 建连。**协议**（`client/src/protocol/types.ts`+`encoder.ts`）：首字节 0x00 handshake / 0x01 audio / 0x02 text / 0x03 control（start/endTurn/pause/restart）/ 0x04 metadata(JSON) / 0x05 error / 0x06 ping，共 7 种。

## 4. 关键模块深读（7 个必读文件）

**4.1 `moshi/moshi/modules/streaming.py` — 流式协议之根**。`StreamingModule`（L262-418）：`streaming(batch)` 上下文向全部子模块传播启停；每组件用 `_init_streaming_state` 声明步进状态（KV cache、卷积 partial 缓冲、环形 token 缓冲）；`streaming_forever(1)` 常驻模式被 `server.py` L115-117 用于双 Mimi 与 LMGen（跨会话复用状态，配合每会话 `reset_streaming`）。`StreamingContainer`（L429-431）是无自身状态的容器基类。看懂它，服务端一半骨架就懂。

**4.2 `moshi/moshi/models/lm.py` — Moshi LM 与 LMGen**。`LMModel`（L218-）：主干 StreamingTransformer 一次前向出下一帧全部流的隐状态，`Depformer` 逐码本（`dep_q=8`）级联生成 agent 音频 token（`depformer_step` L1129-，`torch.where(audio_provided,...)` 让用户侧 token 直通）。`LMGen`（L646-）：`_zero_frame`/`_sine_frame` 供系统提示预热；`_init_streaming_state`（L702-724）用 `CUDAGraphed` 捕获 `forward_codes`/`forward_embeddings`/`depformer_step` 成可重放 CUDA graph（CPU 自动 disable）——**全栈低延迟的隐形功臣**；`prepare_step_input`（L726-）按延迟表把用户 token 写入环形 cache。`step_system_prompts`（L1123-1127）四段预热顺序即人格注入顺序。

**4.3 `moshi/moshi/models/compression.py` + `quantization/vq.py` — Mimi tokenizer**。SEANet 流式卷积编解码 + `SplitResidualVectorQuantizer`：24kHz 波形 ↔ 12.5 帧/秒 8 码本 token；RVQ 拆**语义支路（首层）与声学支路（其余层）**——Mimi 的核心设计。`core_vq.py`（移植自 lucidrains）推理时只查表。

**4.4 `moshi/moshi/server.py` — 会话编排**（详见第 3 节）。补两点：URL 读温度/topk 的代码被注释（L143-146），LMGen 用构造默认值 temp 0.8/temp_text 0.7/top_k 250/top_k_text 25（lm.py L652-655）——**客户端采样参数服务端不消费**；`other_mimi` 与主实例跑完全相同的 encode/decode 且输出弃置（L225/L232 的 `_ =`；offline.py `decode_tokens_to_pcm` L113-122 同构），行为上是死计算。

**4.5 `client/src/audio-processor.ts` — 渲染线程抖动缓冲**（注册名 `moshi-processor`，`@ts-nocheck`）。80ms 起播门限；欠载时 `partialBufferSamples` 每次 +5ms 自适应扩容（上限 80ms）并重新蓄水（L169-177）；超限丢最旧包并抬高水位上限（L50-67）；首帧淡入/欠载淡除去爆音（L164-177）；统计经 port 回主线程。

**4.6 `client/src/decoder/decoderWorker.ts` — 解码 worker 预热池**。`new Worker(new URL("/assets/decoderWorker.min.js", import.meta.url))`（L41-43）按 public 目录约定加载预编译产物；`sendInitCommand` 后 100ms 发一页**手工按字节构造的最小合法 Ogg BOS 页**（`createWarmupBosPage` L6-37，OpusHead mono 48kHz，CRC 无效但解码器不检查）逼初始化；ready 靠 1 秒定时器兜底。`prewarm/getPrewarmed` 单例池在用户点 Connect、AudioContext 刚建时就启动（Queue.tsx L169 注释明言"给 WASM 加载留时间，用户同时在授权麦克风"）。

**4.7 `client/src/pages/Conversation/hooks/useSocket.ts` — 连接状态机**。open 只置 `connecting`，**收到 handshake 才 `connected`**（L57-60，与服务端"跑完系统提示才握手"配对）；500ms 轮询的 10 秒无消息看门狗（L99-115）；`event.target` 与 `socketRef.current` 比对防御陈旧连接事件（L41-49）。有 onDisconnectProp 双调用 bug（见第 7 节）。

## 5. 数据流走读：一句话从麦克风到耳机

1. **授权与底座**（Queue.tsx）：点 Connect → 建 `AudioContext` 并立即预热解码 worker；先直接 `new AudioWorkletNode('moshi-processor')`，抛错才 `addModule` 回退；`getUserMedia` 弹权限；三就绪切 Conversation。
2. **建连**（Conversation.tsx L116-123）：`buildURL` 拼参数 → `useSocket.start()`；open 后仍 `connecting`，等服务端人格预热完收到 handshake 才 `connected`。
3. **上行编码**（useUserAudio.ts L67-94）：opus-recorder 独立 encoder worker（`encoderPath` 走 npm 包 `?url` 导入）编码 mono/24kHz/20ms 页/每 2 页一块，经 `sendMessage` 打 0x01 头发出；麦克风同时接入立体声合并器右声道（左声道留服务端音频）供会话录制导出。
4. **服务端切帧**（server.py）：`OpusStreamReader` 还原 PCM，攒 1920 样本一帧；`mimi.encode` 得 8 码本 token；`LMGen.step` 内 `prepare_step_input` 按延迟表入环形 cache，主干+Depformer 采样出文本 token 与 agent 音频 token。
5. **下行**：agent token 经 `mimi.decode` → PCM → `OpusStreamWriter`；文本 token `id_to_piece`、`▁`→空格发 `b"\x02"+text`；`send_loop` 发 `b"\x01"+Opus`。
6. **解码播放**（useServerAudio.ts L110-121 → audio-processor.ts）：`decodeMessage` 认出 0x01 → postMessage（transferable）给解码 worker → Float32 帧连同 `micDuration` 入 worklet → 过 80ms 门限起播，水位自适应；`delay = micDuration - timeInStream` 即"说与答的实时差"，回传 `ServerAudioStats` 展示。

**一句话**：上行 20ms Opus 页 → 1920 样本帧 → 8 码本 token → LM 一步；下行文本 token 直通 UI、音频 token → PCM → Opus → WASM 解码 → 抖动缓冲 → 扬声器，往返以帧（80ms）为节拍。

## 6. 设计决策与取舍

1. **双语言仓**：Python（PyTorch/aiohttp）与 TS（Web Audio）独立构建（uv + npm），仅靠 WS 二进制协议 + Docker Compose 松耦合。代价是协议改动两头改；收益是前端可脱离 GPU 开发（`/?worker_addr=` 直连）、服务端可 headless。
2. **客户端 WASM worker 解码**：Opus 流式页须边收边解，浏览器原生 API 只能整段解；解码入 worker 避免争抢主线程。注意**不对称加载**：编码 worker 走 npm `?url` 导入（进构建管线），解码 worker 走 `public/assets/` 约定运行时 fetch——后者是**预编译产物直接进仓**，改不了源码。
3. **vendored 而非 pip 依赖**：整个 `moshi/` 子树搬进仓（Kyutai+audiocraft+lucidrains 三血统，三份 LICENSE 配套）。PersonaPlex 要在 LMGen/server 做侵入式改造（voice prompt 嵌入缓存、offline、双 Mimi），fork 比上游 PR 快，也锁死推理行为漂移。
4. **全局 asyncio.Lock 单会话**：7B + CUDA graph 常驻，单卡并发无意义，把并发推给外层排队系统（client 的 `Queue/api/`，`.env.local` 指向 moshi.chat）；自建部署 `/?worker_addr=` 绕过排队。
5. **音色 = 预存嵌入（.pt）**：18 音色离线算好进 `voices.tgz`，会话只读文件（`load_voice_prompt_embeddings`），不用现场编码几十秒参考音频——产品级延迟的关键取舍，代价是不支持任意用户音色。
6. **预热前置到 Connect 点击**：系统提示四段预热 + WASM 加载 + CUDA graph 都塞进用户感知的"等待连接"窗口（handshake 之前），connected 即满速——启动延迟换会话中零卡顿。
7. **Docker 单服务编排**：compose 只有服务端（前端镜像独立存在不进 compose）；`NO_TORCH_COMPILE=1` 换启动速度；`.dockerignore` 仅排除 `.cache` 防数 GB 模型缓存进镜像。

## 7. 已知坑与勘误（新人别踩清单）

全部为本轮源码逐行核实，行号可直接定位（完整表格见文末附录）：

1. **Queue.tsx:140-149 eruda 清理函数永不执行**：`useEffect` 回调里写 `() => {...}` 语句而**没有 return**，`eruda.destroy()` 永不跑；dev 模式反复进出页面残留实例。
2. **useModelParams.ts:86-118 边界校验恒真式**：守卫写成 `if (value <= max || value >= min)`，`||` 连接对任何数值至少成立一支，**校验形同虚设**（本意是 `&&` 区间）。
3. **useSocket.ts:38-46 onDisconnectProp 双调用**：L38-40 无条件调一次，L46"当前 socket"分支再调一次——正常关闭路径回调**连触两次**；现消费方幂等未爆雷，接新回调必踩。
4. **types.ts:1-6 MessageType 落后于协议**：只列 5 种（缺 `error`/`ping`），实际 `WSMessage`（L20-48）与 encoder 编解码 7 种；且 `MessageType` 全仓**零消费方**死类型。
5. **死代码**：`client/src/components/Input/Input.tsx`、`client/src/pages/Queue/hooks/useUserEmail.ts` 全仓零 import（排队流程裁剪后的孤儿），根 `package-lock.json` 空壳无对应 package.json。
6. **decoderWorker.min.js 未入源码批次**：预编译压缩产物放 `public/assets/`，运行时约定 URL 加载、不参与 Vite 构建；与编码 worker 的 npm `?url` 导入是**两套约定**，排查 404 别只查一边。
7. **客户端采样参数大半无效（最重要）**：`Conversation.tsx:63-73` 拼 12 个 URL 参数，服务端只消费 `text_prompt`（server.py L170）与 `voice_prompt`（L152）；温度/topk/pad_mult/repetition_penalty 读取被注释（server.py:143-146）；客户端发 `text_seed`/`audio_seed`（每次挂载随机，Conversation.tsx:113-114）而服务端读 `seed`（L171）——键名不匹配该分支走不到；`randomSeed` 根本没进 buildURL。**参数面板真正影响推理的只有提示词与音色**。
8. **hasCriticalDelay 永不触发**：`useServerAudio.ts:37` 初始 false，全仓无置 true 路径（上游延迟超限判定/跳帧逻辑被裁）；`ServerAudio.tsx:17-29` 断连横幅是**不可达 UI**。
9. **路由勘误**：实际 `/api/chat`（server.py:460 + Conversation.tsx:56 双向实证），图谱/上游文档的 `/ws` 是旧说法；8998 是服务端端口，前端 dev 是 5173。
10. **other_mimi 复读机**：server.py:225/232 与 offline.py:113-122 中第二 Mimi 跑与主实例相同的 encode/decode 且 `_ =` 弃置输出——白耗一份显存/算力，无注释解释，显存优化第一个可摘的果子。
11. **杂项**：audio-processor.ts 整文件 `@ts-nocheck`；useServerAudio.ts:85 `let midx=0` 在组件体每渲染重置（日志节流失效）；encoder.ts:61 未知控制动作直接 throw（TODO 自认应 log），异常帧可炸消息循环；`prompt_service.txt` 单行无换行 `wc -l` 报 0 但非空。

## 8. 上手路径（结合 16 步 tour 的前三天计划）

**Day 1 — 跑起来 + 全局（tour step 01-03、11）**：`README.md`（libopus、`pip install moshi/.`、HF_TOKEN、`moshi.server --ssl`）→ `docker-compose.yaml` 与两个 Dockerfile → 客户端骨架 `index.html`→`app.tsx`→`vite.config.ts`→`env.ts`。结束时应能回答：8998/5173 各是什么、WebUI 为何必须 https、`/?worker_addr=` 干嘛的。

**Day 2 — 服务端纵深（step 04-10）**：按依赖序 `modules/streaming.py`（最优先）→ `utils/compile.py`（CUDA graph）→ `modules/conv.py`+`seanet.py` → `modules/transformer.py`（RoPE+RingKVCache）→ `quantization/core_vq.py`+`vq.py` → `models/compression.py`+`lm.py`+`loaders.py` → `server.py`（三协程）→ `offline.py`（无 WS 版同一套逻辑，跑 `assets/test/` 夹具）。重点体会：所有层共享 `StreamingModule` 协议；`LMGen._init_streaming_state` 的 CUDA graph 捕获。

**Day 3 — 客户端纵深 + 联调（step 12-16）**：`protocol/types.ts`+`encoder.ts` → `Queue.tsx`（底座三件套）→ `Conversation.tsx`（组件编排）→ 四个核心 hook：`useSocket`（状态机）→ `useUserAudio`（上行）→ `useServerAudio`+`decoderWorker.ts`+`audio-processor.ts`（下行，实时性难点全在此）→ `useModelParams`/`ModelParams.tsx`（结合坑#7 理解哪些参数真生效）。收尾自测：关服务端跑客户端看 connecting 卡住（等 handshake）；抓一帧 WS 二进制手工按协议解出。

**改动前三句话**：改协议要 `encoder.ts` 与服务端首字节两头对齐；改音频先分清三个执行环境（主线程 React / 解码 worker / 渲染线程 worklet，仅能 postMessage 通信）；改参数面板先读坑#7，别在无效参数上做功能。

## 勘误与死代码清单（表格版）

| # | 类型 | 位置 | 问题 | 影响 |
|---|------|------|------|------|
| 1 | bug | `client/src/pages/Queue/Queue.tsx:140-149` | useEffect 清理函数无 return | 永不执行，dev 模式 eruda 残留 |
| 2 | bug | `client/src/pages/Conversation/hooks/useModelParams.ts:86-118` | 边界校验 `\|\|` 恒真式 | 全部参数校验失效 |
| 3 | bug | `client/src/pages/Conversation/hooks/useSocket.ts:38-46` | onDisconnectProp 双调用 | 现消费方幂等未爆雷，新回调必踩 |
| 4 | 勘误 | `client/src/protocol/types.ts:1-6` | MessageType 5 种 < WSMessage 7 种 | 死类型误导协议维护 |
| 5 | 死代码 | `client/src/components/Input/Input.tsx` | 全仓零消费方 | 可删 |
| 6 | 死代码 | `client/src/pages/Queue/hooks/useUserEmail.ts` | 全仓零消费方 | 可删 |
| 7 | 死文件 | 根 `package-lock.json` | 空壳无 package.json | 可删 |
| 8 | 架构 | `client/public/assets/decoderWorker.min.js` | 预编译产物未入构建批次；编码 worker 却走 npm `?url` | 两套 worker 加载约定不对称 |
| 9 | 跨端契约 | `Conversation.tsx:63-73` vs `server.py:143-171` | 拼 12 参数仅 text_prompt/voice_prompt 被消费；采样读取被注释；seed 键名不匹配 | 参数面板仅提示词与音色生效 |
| 10 | 不可达 UI | `useServerAudio.ts:37`+`ServerAudio.tsx:17` | hasCriticalDelay 无置 true 路径 | 断连横幅永不出现 |
| 11 | 勘误 | `moshi/moshi/server.py:460` | 实际路由 `/api/chat` 非 `/ws` | 导航联调按 /api/chat |
| 12 | 死计算 | `server.py:225,232`、`offline.py:113-122` | other_mimi 复读主 mimi 且弃置输出 | 白耗显存/算力 |
| 13 | 杂项 | `client/src/audio-processor.ts:1` | 整文件 `@ts-nocheck` | 类型保护缺位 |
| 14 | 杂项 | `client/src/pages/Conversation/hooks/useServerAudio.ts:85` | `let midx=0` 每渲染重置 | 日志节流失效 |
| 15 | 杂项 | `client/src/protocol/encoder.ts:61-64` | 未知控制动作 throw | 异常帧可炸消息处理 |
| 16 | 杂项 | `assets/test/prompt_service.txt` | 单行无换行符 | `wc -l` 报 0，勿按行数判空 |

（完）
