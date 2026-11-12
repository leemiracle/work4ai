# 讲透 NVIDIA/ACE

> NVIDIA ACE（Avatar Cloud Engine）数字人套件样例仓：ACE Agent 微服务（webui 会话编排+grpc 三模式客户端）+ audio_2_face 音素驱动 + tokkio 数字人工作流（pipecat 管线 RivaASR→LLM→ElevenLabs→A2F→AnimGraph）。
> 本目录=understand 全链知识库产物（2026-11-06，kylin-fusion-search 会话，NV 舰队 v3.1 全量队列第 9 仓）。

## 全链状态表

| 阶段 | 状态 | 关键数据 |
|---|---|---|
| prepare（scope-cut） | ✅ | 1986→257 文件/33 批（裁 tokkio 4.x 旧版/one-click 五套云样板/ace_agent 4.0/samples 13 留 rag_bot+npc_bots 两代表/资产） |
| 批分析 | ✅ 33/33 | 488n/688e；TS ESM `.js` 后缀导入+裸 `from "."` scanner 全盲区 39 边手扫恢复；proto/生成物/运行时注入三类仓外依赖诚实 notes |
| 悬空边归因 | ✅ | 前缀错位 1 边手工回补（class:→function:）+跨批重复 config 节点删 1；merge 487n/687e 零 drop |
| layers/tour | ✅ | 16 层 324/324 全覆盖；16 步导览 |
| finalize | ✅ | 双 validator 0/0；fingerprints 257 文件@92a0ac1a |
| ONBOARDING | ✅ | 6998 不计空格字符/8 节/35 锚（主会话抽验 4/4 含主题归位） |
| explain | ✅ 12 篇 | 组1 核心链路 6 篇（3982-4055 字/281 锚）+组2 工作流样例线 6 篇（3900-4884 字/226 锚）；主会话抽验 6/6 命中 |

图谱：仓内 `.understand-anything/knowledge-graph.json`（487n/687e/16 层/16 步）。
1308 团灭两次（03:36 写作双 worker 零产物/06:07:42 重置后 20s 复活续跑），零最终损失。

## 勘误清单（源码级实证）

1. **helm 六变体矩阵**：六个 Chart.yaml md5 全同（159b55b2）、七份 config.yaml md5 全同（7fcbe9f2，Aki 数字人人格单一事实源经 entrypoint.sh:12 挂载）；差异文件**三份**非两份——tokkio-app-params.yaml+values.yaml:370/:402+tokkio-app.yaml:124 的 ui-on/off label。
2. **proto 双 Contract 勘误**：17 个 rpc 全在 `webui/server/grpc/ace_agent.proto`；`nvidia_ace.controller.v1.proto`（audio_2_face 侧）零 rpc 纯消息。AudioStream 同名异构：controller 版三分支含 EndOfAudio 哨兵无 ID，a2f 版两分支靠 half-close 带 AnimationIds（注释互指）。
3. **TS scanner 盲区**（流水线侧）：ESM `.js` 后缀导入指向 `.ts` 源+裸 `from "."`，batchImportData 全空——39 条 imports 边全手扫恢复；AbstractTask（export default abstract class）tree-sitter 零提取需人工。
4. **validate_url 只认 IP:port**（rag_bot utils.py:14）：域名（含默认 localhost:8081）判非法——set_rag_endpoint 热切换仅适用 IP 端点。
5. **parameters 运行时注入模块**全仓零文件（ACE Agent 容器注入）；nvidia_ace.* proto 生成物只在闭源 wheel 内（depends_on 边代指）。
6. **WebSocketTask 34 方法**非 35（12 listen+12 handle+8 send+构造+start）；三处 AbortError 判法不一致（e.name/e.code==="ABORT_ERR"/e.code===1）。
7. **RECEIVED_ASR reducer 非纯**（useServerState.ts:177-181）：mutate+return state 违反纯函数约定且不触发重渲染——图谱未载的新发现。
8. **AudioBuffer 线性非环形**：useAudioPlayer 实为一次性 60s 线性缓冲（offset 单调增、reset 整体重建）；:57-59 注释 "unsigned 16-bit" 系笔误（代码按有符号处理）。
9. **isAvailable() 恒真**（config.ts 全默认值致检查失效）；GRPCClient.ts:26-27 注释与行为不符。
10. **bot.py:181 `.replace` 返回值丢弃**（剥 http:// 前缀从未生效）+RivaTTSService 死 import 两处死代码。
11. **tokkio_rag 超时注释失实**：`:70` 注释称 timeout=120 请求超时，实证 self.timeout 零消费、真实超时 `:90` 的 15.0；vdb_top_k/reranker_top_k 形参收下但请求体 `:123-124` 注释掉（收了不发）。
12. **FacialGestureProviderProcessor 必填但闲置**（config.py:70 必填，llm-rag 管线零消费点）；confidence_threshold 三处各写各的（config.py:58 默认 0.5/yaml:53 实值 0.37/降级常量独立 0.5）。
13. **"bot 名 rag 前缀启 RAG policy" 仅 README 文字**：样例实名 genai_rag_bot 不以 rag 开头；裁决逻辑在闭源 aceagent 包不可验；仓内可实证机制=colang endpoint（main.co:9）+chatEndpointPrefix（app-params.yaml:4）。
14. **slm_responder prompt import 期定格**（:45；八维动态覆盖通道存在但仓内无调用方传 context）；EXTRA_CONFIG_PATH 全仓零消费；start_dev.py 218 行（wc -l 217=末行无换行符，图谱 217 是 wc 口径）。
15. **elara/jin 角色配置族**：三套 actions.py md5 全同（d5c0d844…）；speech_config 仅 bot_name/voice_name 两行之差；plugin_config 内嵌完整角色卡（1860 年鬼屋向导/拉面店老板剧情）。
16. **scope-cut 残留**：plugin_server openapi 的 /stock/* 端点指向被裁区（插件源码在 samples/stock_bot/plugins/yahoo_fin.py，宿主实现=openapi 快照+无源码 Dockerfile）。
17. **上游配置笔误**：files_to_compile.yaml 的 animation_data.v1 重复两次且漏列磁盘实存的 services.animation_data.v1；requirements.txt protobuf-gen 行重复。

## 生成口径

- 16 层层序：治理文档 → 包构建 → webui client 前端 → webui server 任务编排 → grpc 契约/生成物 → A2F 微服务与 proto → tokkio llm-rag 管线 → 六 helm chart 部署变体 → config 人格/角色 → samples 代表样例 → notebooks → local-dev/工具 → 测试。
- 字数口径：不计空格字符；explain 12 篇系列口径 3.9-4.9K。
