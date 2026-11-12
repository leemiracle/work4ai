# 07 · 数字人与流式 RAG：digital-human-security-analyst 与 fm-asr-streaming-rag

## 角色定位

图谱 layer-8「数字人与流式 RAG」（183 节点）只含两个示例，却是全仓"非键盘交互"的两极：`community/digital-human-security-analyst`（103 节点）用语音+虚拟人脸做 SOC 安全分析副驾驶，`community/fm-asr-streaming-rag`（80 节点）把 FM 广播电台实时转写进 RAG。前者演示"AI 数字人怎么落地"，后者演示"无限长的音频流怎么持续入库"——都是对主线 RAG 示例（问答型、文档型）的形态扩展。

digital-human 的定位写在 README：SOC 分析师每天被告警淹没，示例做一个"能听、能说、有脸"的 RAG 副驾驶，技术栈横跨 Morpheus 数字指纹（DFP）、Riva ASR/TTS、NeMo Retriever、Omniverse Audio2Face 与 Unreal Engine 5.4（默认 Metahuman Omar）。fm-asr 则明确是"从射频到问答"的全链路：RTL-SDR 硬件 → GNU Radio → UDP 基带 I/Q → Holoscan GPU 信号处理 → Riva gRPC 流式 ASR → Milvus → RAG。

## 内部结构

**digital-human** 是三层拼装：

1. **数据准备层**（Morpheus DFP，可跳过）：`workspace/dfp/stages/` 下 14 个 Morpheus pipeline stage，核心是 `dfp_rag_upload_stage.py:33` 的 `DFPRAGUploadStage`——把上一阶段 LLM 生成的告警摘要上传到 NeMo Retriever collection，成为 RAG 知识源。仓库自带预生成摘要（`workspace/dfp_detections_triaged.csv`），所以 README 明说可以跳过 Section 1。
2. **Agent 层**（`workspace/ragbot/`）：`agent_tools.py` 构造 5 个独立 RetrieverClient（User Directory/Network Traffic/Threat Intel/Alert Summaries/Email Gateway，每个对应一个向量库，L20-66）；`voice_ragbot.py` 是主循环。
3. **渲染层**：`a2f_client.py` 通过 gRPC（`audio2face_pb2`/`audio2face_pb2_grpc`，proto 见 `ragbot/proto/audio2face.proto`）把 TTS 音频推给 Audio2Face。

**fm-asr** 是微服务集群：`gnuradio/`（RTL-SDR 采集，`grc_files/fm_radio.grc`）与 `file-replay/`（无硬件时用 wav 文件伪造 FM 信号）都往 UDP 发基带；`sdr-holoscan/` 是 GPU 解调器（`operators.py` 356 行）；`chain-server/` 是 RAG 后端；`frontend/` 是 Next.js 导出的静态页加 Python 服务。部署矩阵有四个 compose 文件（`deploy/docker-compose{,-nims,-milvus,-file-replay}.yaml`），Milvus 与 NIM 可拆机部署。

## 外部连接

digital-human 依赖五个外部系统：build.nvidia.com 的 LLM/Embedding/Rerank 三个 API key（`.env`），Riva 服务器（ASR+TTS），NeMo Retriever，Audio2Face gRPC（默认 50051），Unreal Engine。Morpheus 容器版本钉死 24.03（`docker/Dockerfile.morpheus`），自托管选项是 llama3-8b NIM 24.05（`docker-compose.yml` 里注释保留）。

fm-asr 的外部面更宽：Riva ASR 只支持本地部署 NIM（README 明确"The ASR endpoint has only been tested with locally deployed NIMs"）；LLM/embedding/rerank 走 build.nvidia.com 或本地；GNU Radio 在 WSL 下还要 Windows 侧 usbipd 绑定 USB 设备（README 给了完整 PowerShell 流程）。硬件建议 2x RTX 6000 Ada：GPU 0 跑 LLM，GPU 1 跑 SDR+embedding+rerank+ASR。

## 数据流

**digital-human 语音回路**（`voice_ragbot.py`）：麦克风采集（sounddevice，44.1kHz int16，L100-125）→ `ragbot()`（L127）把 numpy 数组转 WAV 字节 → `riva_asr.offline_recognize`（L139）→ 转写文本先过**路由提示词**（L155-158）：让 LLM 返回 `[use_tools, use_checklist]` 二元整数列表，`ast.literal_eval` 解析（L166）。三分支：
- 双 1：`generate_checklist` 生成 3 步清单（`generate_checklist.py` few-shot 模板）→ `deploy_tools` 用 `initialize_agent`+`AgentType.ZERO_SHOT_REACT_DESCRIPTION`（`agent_tools.py:85-92`）跑 ReAct，工具只有 4 个（L81）→ 再让 LLM 压成一句话；
- 仅 tools：普通 RAG，带 `prior_response` 做对话记忆（L203-206）；
- 双 0：直接闲聊。
最后 TTS：`riva_tts.synthesize` 整段合成（L230）写 `final_output.wav` 交给 Unreal/Audio2Face。长度闸门在 L217：`len(voice) > 100` 就降级为 "Here's what I found!"——数字人嘴长有限，长回答只播短句。

**fm-asr 射频回路**：UDP 收 I/Q → `fm_demod`（`operators.py:44`，angle unwrap + diff，cupy 全 GPU）→ 低通/降采样 → `float_to_pcm`（L58）→ PCM 进 `RivaThread`（`riva_asr.py:28`）的 Queue → `_request_generator`（L153）无限 `yield` 队列块，gRPC `StreamingRecognize` 开流，`interim_results=True`（L149）。转写结果双出口：final 进数据库（`/storeStreamingText`），partial 去重后只推前端（`_export_partial_transcript` L99、`extract_transcripts` L109）。chain-server 侧 `TextAccumulator.update`（`accumulator.py:40`）把新文本与残留尾巴拼接、用 `RecursiveCharacterTextSplitter` 切块——`docs[-1]` 留作下次的残尾，`docs[:-1]` 即完整块入库（L49）。查询侧 `RagChain.answer`（`chains.py:66`）先 `classify` 意图（RecentSummary/TimeWindow/SpecificTopic），时间类问题走 `TimestampDatabase`（SQLite 时间戳索引，绕过向量检索），超量文档时递归摘要压上下文（最多 3 次，L31）。

## 设计决策

1. **"每个工具一个向量库"而非共享库**（`agent_tools.py:19` 注释明说）——换来的是工具描述即检索边界，ReAct 的 tool call 天然完成"路由到正确语料"。
2. **流式 ASR 的残尾拼接**是 fm-asr 最聪明的一笔：partial 转写永远不完整，accumulator 把"未满一块"的尾巴滚入下一轮，保证跨块边界的话不丢。
3. **文件回放器等同真信号源**（`wav_replay.py:106` `fm_modulate` 再调制后发 UDP）——从流水线视角无法区分真假射频，这是教科书级的"测试替身与生产同构"。
4. **明示的技术债**：`accumulator.py:27-28` 两条 `#todo`（多流并发、时间触发 embed）诚实标注单流假设。
5. 值得警惕的点：`voice_ragbot.py:135` 用了 `wav.write(...)` 但全文件只 `import soundfile as sf`（L7），没有 `import wav`——按现状代码 ASR 前会 NameError，正确写法应是 `sf.write`（L233 就是这么写的）；同文件 L53/58 的 Riva 地址与 A2F 节点名仍是占位符 "YOUR RIVA IP AND PORT"。这个示例是"演示骨架"而非开箱即用。
6. `generate_checklist.py` 的 few-shot 列了 7 个工具（含 Server Logs、Asset Management），但 `agent_tools.py` 只实现 5 个、agent 只挂 4 个（Email Gateway 工具 L178 定义后从未入列）——清单可能指挥 agent 调用不存在的工具，靠 ReAct 的容错兜底。

## 新人提示

- 读 digital-human 先跳过 DFP（Section 1 可跳），从 `voice_ragbot.py:127 ragbot()` 入手，10 分钟能看完整个语音回路；Morpheus 部分只在你想理解"告警摘要怎么来的"时再回看。
- fm-asr 建议按 compose 文件分层读：先 `sdr-holoscan/operators.py`（信号处理）再 `riva_asr.py`（线程+断线重连，`run()` L53 的 except 里锁内重开 gRPC 流值得学），最后 `chains.py`（意图分类）。
- 两个示例合看会得到一个完整认知：**数字人示例解决"交互形态"，流式示例解决"数据形态"**，把它们拼起来就是"会说话、有脸、知识持续更新的直播数字人"。
- 甄别备注：任务书称"数字人流式示例"（digital-human），经源码核实其本体是 LangChain ReAct agent + Riva 语音壳，"流式"特性实际在 fm-asr 侧（gRPC 流式 ASR + 残尾累积器）；图谱把两者并为一层（layer-8）正是这个互补关系。本篇所有行号锚（voice_ragbot.py:53/58/135/155/166/190/193/217/230、agent_tools.py:81/85/178、accumulator.py:27/28/40/49、operators.py:44/58、riva_asr.py:28/53/99/109/149/153、chains.py:31/66/155、wav_replay.py:106）均已对照仓库源码逐一核实。
