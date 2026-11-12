# 01 · server.py：WebSocket 会话服务——PersonaPlex 推理服务端主入口

> 锚点基线：`moshi/moshi/server.py`（483 行，NVIDIA MIT 头 + Kyutai 版权双许可），客户端锚 `client/src/`。

## ① 角色定位

`server.py` 是整个服务端的"总装车间"：它把三个模型件（Mimi 编码器 ×2、Moshi LM）装配进 `ServerState`，用 aiohttp 挂一个 WebSocket 路由，然后以三协程循环把"用户麦克风 → 音频 token → 语言模型 → agent 音频"跑成实时闭环。`pyproject.toml` 里 `[project.scripts]` 注册的 `moshi-server = "moshi.server:main"` 就指向这里的 `main()`（server.py:357），Dockerfile 里 `moshi.server --ssl ...` 启动的也是它。

**实测勘误（重要）**：真实路由是 `/api/chat`（server.py:460 `app.router.add_get("/api/chat", state.handle_chat)`），不是早期图谱所说的 `/ws`。客户端也按此连接：`client/src/pages/Conversation/Conversation.tsx` 里 `new URL(`${wsProtocol}://${newWorkerAddr}/api/chat`)`。

## ② 内部结构

- `torch_auto_device`（server.py:57-65）：requested 优先，否则 cuda 可见即 cuda；mps 分支被注释掉（server.py:63-64），`DeviceString` 只剩 `"cuda" | "cpu"`（server.py:55）——这是 NVIDIA 发行版对 Kyutai 原版的裁剪。
- `seed_all`（server.py:68-76）：同时种 torch/cuda/random/numpy，但注意 `cudnn.deterministic = False`（server.py:75）——种了子却不锁确定性，可复现性只到"分布"不到"逐位"。
- `wrap_with_system_tags`（server.py:79-86）：把 persona 文本提示词包成 `<system> ... <system>` 双标签，已带标签则幂等返回。
- `ServerState`（server.py:89-95 字段，97-117 构造）：持有 `mimi`、`other_mimi`、`text_tokenizer`、`lm_gen`、`lock` 五件套。`frame_size = int(24000/12.5) = 1920` 样本/帧（server.py:105）；`LMGen` 以 `audio_silence_frame_cnt=int(0.5*12.5)=6` 构造（server.py:106-112）；最后三个组件全部 `streaming_forever(1)`（server.py:115-117）——批大小 1 永久流式。类标了 `@dataclass` 但手写了 `__init__`（server.py:97），装饰器不覆盖手写构造，dataclass 在此只是声明式的字段文档。
- `warmup`（server.py:119-132）：4 轮全零 chunk 走完 encode→step→decode 全链，给 CUDA graph 捕获热身，最后 `torch.cuda.synchronize()`（server.py:132）。
- `handle_chat`（server.py:135-309）：会话主体（见④）。
- `_get_voice_prompt_dir`（server.py:312-338）：无本地目录时从 HF 仓库下载 `voices.tgz` 解压出 18 个音色；`_get_static_path`（server.py:341-354）下载 `dist.tgz`（前端产物）做静态托管。
- `main`（server.py:357-479）：argparse → 下载 config.json 刷计数（server.py:429，注释明言不担心重复计数因会命中缓存）→ `get_mimi` 装**两份** Mimi（server.py:434-435）→ `get_moshi_lm` 支持 `--cpu-offload`（server.py:445）→ 建 `ServerState` + warmup → 注册 `/api/chat` 与可选静态路由（server.py:460-469）→ `--ssl` 时经 `create_ssl_context` 起 https（server.py:472-473）→ `web.run_app`（server.py:479）。
- 模块级 `with torch.no_grad(): main()`（server.py:482-483）：整个进程天生 no_grad，推理服务不需要反向图。

## ③ 外部连接

- **调用它的**：`pyproject.toml` 控制台脚本、根仓 `Dockerfile`（`moshi.server --ssl`）、`docker-compose.yaml`（映射 8998 端口）；浏览器客户端经 `wss://…/api/chat` 连入。
- **它调用的**：`loaders.get_mimi/get_moshi_lm`（server.py:434/445）拿模型；`LMGen` 的全套系统提示词流程 `step_system_prompts_async`（server.py:283）；`utils/connection.create_ssl_context/get_lan_ip`（server.py:473-474）；`utils/logging.setup_logger/ColorizedLog`（server.py:51/54/138）；`sphn.OpusStreamWriter/OpusStreamReader`（server.py:263-264）做 Opus↔PCM。
- **二进制线协议**（与客户端 `client/src/protocol/encoder.ts` 对齐）：客户端→服务端首字节 kind，`1`=Opus 音频（server.py:195-197）；服务端→客户端 `\x00` 握手（server.py:288）、`\x01`+Opus（server.py:251）、`\x02`+UTF-8 文本（server.py:239）。

## ④ 数据流

一次会话的时间线：

1. **建连**：`handle_chat` prepare WebSocket（server.py:136-137），`ColorizedLog.randomize()` 给每会话随机颜色前缀（server.py:138）。
2. **参数读取**：`voice_prompt` 拼 `voice_prompt_dir` 路径，不存在直接 `FileNotFoundError`（server.py:149-162）；`.pt` 后缀走预存嵌入 `load_voice_prompt_embeddings`，否则走 WAV `load_voice_prompt`（server.py:164-169）；`text_prompt` 经 `wrap_with_system_tags` + sentencepiece 编码成 `text_prompt_tokens`（server.py:170）。
3. **串行闸门**：`async with self.lock`（server.py:259）——**全服务同时只允许一个会话**，第二个连接会排队等前一个结束。
4. **系统提示词阶段**：`step_system_prompts_async`（音色 WAV → 0.5s 静音 → 文本提示词 → 0.5s 静音，server.py:283），期间 `is_alive`（server.py:268-281）每帧探活，客户端断线就提前止损；完成后发 `\x00` 握手（server.py:288）。
5. **三协程并发**（server.py:291-295）：`recv_loop` 收 Opus 进 reader；`opus_loop` 从 reader 读 PCM、按 1920 样本攒帧（server.py:218-221），每帧 `mimi.encode` 用户音频 + `other_mimi.encode` 同步喂第二路、`lm_gen.step` 逐帧出 token（server.py:224-227），`tokens[:, 1:9]` 的 8 个音频码本解码回 PCM 写 writer（server.py:231-234），文本 token 非 (0,3) 则 `\x02` 推送（server.py:235-240）；`send_loop` 把 writer 里的 Opus 字节 `\x01` 打包发出（server.py:244-251）。
6. **收尾**：`asyncio.wait(FIRST_COMPLETED)`（server.py:297），任一协程退出即 cancel 其余并关 ws（server.py:299-306）。

## ⑤ 设计决策

- **双 Mimi 实例**（server.py:434-435）：流式卷积/Transformer 各有内部状态，一套编解码器无法同时服务"用户流"与"agent 流"两条时间线；复制权重换状态隔离，是最省事也最省显存的方案（Mimi 只有约百 M 参数，远比 LM 便宜）。
- **全局锁 + 单会话**（server.py:95/114/259）：模型是批 1 流式（`streaming_forever(1)`），KV cache 与延迟敏感的 CUDA graph 都按单会话形状捕获，多路并发会打碎这两层假设，索性用锁把并发挡在协议层。
- **握手字节放在系统提示词之后**（server.py:283-288）：客户端只有收到 `\x00` 才开始发音频，保证 LM 吃到的第一帧用户音频一定在音色/人设提示词之后——提示词次序即模型条件化次序。
- **文本 token 过滤 (0, 3)**（server.py:236）：id 0/3 是 EPAD/PAD 类静默位，不推给前端，避免字幕区被填充符刷屏。
- **1ms 轮询**（server.py:210/248）：三协程用 sleep(0.001) 自旋衔接，靠 GPU 每帧 80ms 的节奏兜底，实现简单且延迟可控。

## ⑥ 新人提示（坑与勘误）

1. **路由勘误**：一切文档/图谱若写 `/ws` 皆过时，以 server.py:460 的 `/api/chat` 为准。
2. **seed 读取是双重死路**（server.py:171）：条件查的是 `request.query`，取值却用 `request["seed"]`——aiohttp 里 `request[key]` 走 `MutableMapping.__getitem__` 读的是请求应用状态 `request._state`，不是查询参数（aiohttp 3.13.3 源码实证 `BaseRequest.__getitem__` 即 `self._state[key]`）。就算客户端真传 `seed=123`，这行也会 KeyError 崩掉会话。而客户端实际发的是 `text_seed`/`audio_seed`（Conversation.tsx:68-69），键名根本对不上——所以 seed 分支在现网永远不触发。
3. **采样参数读取被注释**（server.py:143-146）：`audio_temperature/text_temperature/text_topk/audio_topk` 四行读取全部注释掉，LMGen 只用构造时的默认值（temp 0.8/0.7、top_k 250/25）。客户端 URL 上带的 12 个参数（Conversation.tsx:62-73：两类温度、topk、pad_mult、双 seed、repetition_penalty×2 等）服务端真正消费的只有 `text_prompt` 和 `voice_prompt` 两个。
4. **死代码**：server.py:242 的 `text_token_map = ['EPAD','BOS','EOS','PAD']` 定义后从未使用（离线版 offline.py:293 倒是真的用了它）。
5. **mps 不可用**：`--device mps` 会直接落进 `torch.device("mps")` 报错——支持分支被注释（server.py:63-64），别在 Mac 上指望它跑起来。
6. `other_mimi.encode/decode` 的返回值在 server.py:123/225/232 被丢弃（`_ =`）——它的作用只是维持第二路流式状态与首路同步，输出无人消费。
