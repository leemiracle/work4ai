# 讲透 personaplex（NVIDIA/personaplex 全链知识库）

moshi 语音对话全栈演示仓：`moshi/`（Python 服务端：Mimi 音频压缩 + Moshi-LM 流式对话 + WebSocket 服务）+ `client/`（TS/React+Vite 客户端：音频采集/WASM 解码/会话 UI）+ Docker 部署。

| 环节 | 状态 | 产物与指标 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | 28/28 页真一百分（INDEX+全页+_coverage-check） |
| understand 图谱 | ✅ 2026-11-04 | 263n/516e/16 层/16 步 tour；双 validator 0 issues 0 warnings；fingerprints 98 文件@3428dfd9；图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 2026-11-04 | ONBOARDING.md 8 节+勘误表，11262 字符（不计空格），29 锚终验 0 坏 |
| explain | ✅ 2026-11-04 | 12 篇 60264 字符（不计空格），553 锚终验 552 好+1 笔误修正=全好 |

## explain 索引（服务端 6 + 客户端 6）

01 WebSocket 会话服务 / 02 流式基座 streaming 与编译工具 / 03 网络积木 conv-seanet-resample / 04 RVQ 残差向量量化 / 05 模型层 Mimi 压缩与 Moshi-LM / 06 离线推理与服务端工具线 / 07 入口与工程配置 / 08 协议层 types-encoder-testMessages / 09 连接核心 useSocket 与 SocketContext / 10 音频引擎 decoderWorker 与 audio-processor / 11 会话页 Conversation 组件树 / 12 排队页 Queue 与 Docker 部署线

## 源码级勘误清单（12 条，全部行号锚实证）

1. **真实路由是 `/api/chat` 非 `/ws`**（server.py:460，图谱早期摘要勘误）
2. 客户端拼 12 个 URL 参数，服务端只消费 text_prompt/voice_prompt；采样参数读取整段被注释
3. **seed 双重死路**：`request["seed"]` 读的是 aiohttp `_state` 非查询参数；客户端发 `text_seed`/`audio_seed` 键名不匹配
4. `hasCriticalDelay` 断连横幅为不可达 UI（上游判定逻辑被裁剪）
5. core_vq 的 EMA/死码替换在本仓是死代码（`_ema_inplace`/`_replace_expired_codes` 零调用）
6. Queue.tsx useEffect 返回被忽略的箭头函数——eruda.destroy 永不执行
7. useModelParams 数值 setter 的 `<=max||>=min` 恒真式，上下界拦截形同虚设；resetParams 不重置 prompts/seed
8. useSocket onDisconnectProp 同一 CloseEvent 双调用（L38 无条件+L46 分支）
9. types.ts MessageType 5 种落后 WSMessage 7 种（缺 error/ping）；decodeMessage handshake 硬编码 version:0/model:0
10. Input.tsx / useUserEmail.ts 全仓零消费方=死代码
11. decoderWorker.min.js 未入任何批次，wasm 由 worker 按同名约定运行时 fetch
12. TorchAutocast vendored 自 Meta audiacraft（Kyutai+Meta 双版权头）；text_token_map 死代码；Depformer dep_q=16 硬覆盖字典的 8；offline 与 server 四段复刻双维护

## 流水线备注

- 2026-11-04 前会话死于 1308（10/12 批），本会话断点续跑补 3/4/12 收官；explain 两组同日死于 1308 后 SendMessage 复活零损失
- 字数口径=不计空格总字符；锚口径=`path:line` 提取+basename 消歧+界内判定（anchor_verify.py）
