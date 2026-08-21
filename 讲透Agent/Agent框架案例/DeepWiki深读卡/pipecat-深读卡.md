# pipecat 深读卡 —— 语音/实时多模态 Agent 框架：万物皆 Frame，毫秒级流上跑完 STT→LLM→TTS 全链路

> **定位**：Daily（pipecat-ai）出品的开源 Python 实时语音与多模态对话 Agent 框架。核心差异化：把音频块、文本 token、控制信号、中断全部统一为带优先级的类型化 Frame，流过 FrameProcessor 双向流水线，60+ AI 服务（STT/LLM/TTS/S2S）与传输层（WebRTC/WebSocket/MoQ/电话）全部可插拔；1.3.0 起每条 pipeline 就是一个 Worker，可经 WorkerBus（本地/Redis/PGMQ）组成分布式多 Agent 系统。语音 Agent 领域事实上的开源标准件，配套 RTVI 协议与全平台客户端 SDK。

> **本地**：`repos/pipecat`（pipecat-ai/pipecat）｜**深读**：deepwiki 51 子页归档 `deepwiki/pipecat/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 帧层 `frames/` | 一切数据与控制信号的统一表示 | `Frame`→`SystemFrame`(HIGH)/`DataFrame`/`ControlFrame`，`InterruptionFrame`、`UninterruptibleFrame` mixin，100+ 类型 + protobuf 序列化 |
| 处理器层 `processors/` | 帧的加工与聚合 | `FrameProcessor`（优先级双队列基类）、`LLMUserAggregator`/`LLMAssistantAggregator`、filters、`RTVIProcessor` |
| 编排层 `pipeline/` | 链式/并行组装与生命周期 | `Pipeline`/`ParallelPipeline`/`SyncParallelPipeline`、`PipelineWorker`+`WorkerRunner`、`ServiceSwitcher` |
| 服务层 `services/` | 60+ AI 提供商集成 | `LLMService`/`STTService`/`TTSService` + Speech-to-Speech（OpenAI Realtime、Gemini Live、Nova Sonic、Ultravox…） |
| 传输层 `transports/`+`serializers/` | 音视频 I/O 与线路协议 | `BaseInput/BaseOutputTransport`、Daily/LiveKit WebRTC、WebSocket、MoQ、Twilio 等电话 serializer |
| 总线层 `bus/` | 跨 worker/跨进程消息 | `WorkerBus`：`AsyncQueueBus`(本地)/`RedisBus`/`PgmqBus` + `BusBridgeProcessor`（frame 跨进程桥） |
| 轮次与音频 `turns/`+`audio/` | 用户轮次检测与音频增强 | turn start/stop 策略族、VAD（Silero/Krisp/AIC）、SmartTurn（ML 预测用户说完没）、RNNoise |
| 观测层 `observers/`+`metrics/` | 延迟/轮次/tracing | `UserBotLatencyObserver`、`TurnTrackingObserver`、OTel GenAI 语义约定、eval 框架 |

## 二、核心机制

1. **万物皆 Frame + 双优先级队列**（来源：Frame System and Processing、Core Architecture）：`SystemFrame`（Start/Interruption/Cancel，HIGH_PRIORITY=1）插队立即处理，`DataFrame`/`ControlFrame`（LOW_PRIORITY=2）排队保序；每个 `FrameProcessor` 内置两级队列 + 独立 asyncio task，本身就是一条并发流水级。**创新点本质**：把实时媒体流与 Agent 控制流压进同一套类型化消息系统——中断、flush、起止皆帧，于是 STT/LLM/TTS/transport 全部退化为同构处理器，这是与 LangChain 系"消息轮次"框架的根本分野。
2. **InterruptionFrame 广播 = 类型系统级 barge-in**（来源：Interruption Handling）：用户开口 → turn start 策略推 `UserStartedSpeakingFrame` → `InterruptionFrame` 向上下游双向广播，各处理器清队列、停生成、TTS 停播；`UninterruptibleFrame` mixin（EndFrame/StopFrame/FunctionCallResultFrame）免疫清除，函数结果永不丢。文本 Agent 框架几乎不碰的"抢占"难题在这里用帧类型+队列语义解决。
3. **Universal LLMContext + Aggregator Pair**（来源：Context System、Context Aggregators）：provider 无关的标准消息存储，adapter 翻译到各家 API 格式；`LLMUserAggregator`（用户轮次入上下文+触发 LLM）与 `LLMAssistantAggregator`（助手流式回复回写+函数调用）成对粘合 STT→LLM→TTS，"转写即用户消息"。换模型商不动应用逻辑。
4. **Pipeline 即 Worker，WorkerBus 网络化**（来源：Multi-Worker Framework、Worker Architecture and Bus）：1.3.0 起 PipelineTask→PipelineWorker，成为共享 `WorkerBus` 上的 peer；换 bus 后端（AsyncQueueBus→RedisBus/PgmqBus）即从单进程多 agent 变分布式，`BusBridgeProcessor` 把 frame 序列化跨进程搬运。**创新点本质**：多 Agent 协作不是叠加新抽象层，而是同一条帧流水线的网络化延伸——handoff/fan-out/sidecar 全是 bus 消息。

## 三、与讲透系列的对位

| pipecat 概念 | 讲透系列概念 | 对位要点 |
|---|---|---|
| Frame/FrameProcessor 双向流 | 讲透Agent / ReAct 循环与流式输出 | 把 Agent 循环的"一轮"打散成毫秒级 token/音频帧流，agent loop 的实时化形态 |
| InterruptionFrame / UninterruptibleFrame | 讲透Agent / 人机交互与控制流 | 罕见的抢占原语，可类比 OS 中断与不可屏蔽信号，讲"Agent 可被打断"的第一教材 |
| Universal LLMContext + Aggregator | 讲透Agent / 上下文工程 | 上下文=显式消息对象+adapter 翻译，比"记忆塞进 prompt"更工程化的范式 |
| WorkerBus / handoff / UIWorker | 讲透多Agent协作 / 编排模式 | 每条 pipeline 一个 agent，bus 消息即 handoff；对照黑板/主管-工人等编排模式 |
| Observer + OTel + eval 框架 | 讲透Agent / 评估与观测 | 帧→指标→trace→judge 全链路，实时 Agent 的可观测性范本 |
| mem0 记忆服务 / Context Summarizer | 讲透学习型Agent / 记忆机制 | 长期记忆与上下文摘要压缩的现成接入口 |

## 四、关键入口

```python
src/pipecat/frames/frames.py                            # Frame 类型宇宙：System(HIGH)/Data/Control 三分类
                                                        # + InterruptionFrame + UninterruptibleFrame mixin
src/pipecat/processors/frame_processor.py               # 一切组件的基类：FrameProcessorQueue 优先级队列
                                                        # + 双 asyncio task + push_frame() 双向流
src/pipecat/processors/aggregators/llm_response_universal.py
                                                        # L516 LLMUserAggregator / L987 LLMAssistantAggregator
                                                        # / L1678 LLMContextAggregatorPair：轮次↔上下文粘合剂
src/pipecat/pipeline/pipeline.py                        # Pipeline=处理器链；parallel_pipeline.py /
                                                        # sync_parallel_pipeline.py 为并行/同步并行分支
src/pipecat/pipeline/worker.py                          # PipelineWorker(原 PipelineTask)+WorkerRunner：
                                                        # 生命周期、source/sink、事件与心跳
src/pipecat/bus/bus.py                                  # WorkerBus 抽象：local/async_queue.py、
                                                        # network/redis.py、network/pgmq.py 三后端
src/pipecat/transports/base_transport.py                # BaseInput(VAD+轮次分析)/BaseOutput(MediaSender)；
                                                        # daily/ livekit/ moq/ websocket/ 为具体实现
examples/function-calling/function-calling-openai.py    # 入门标本：transport+context+aggregator+LLM+TTS 组装
examples/multi-worker/local-handoff/local-handoff-two-agents.py
                                                        # 双 agent handoff；distributed-handoff/redis-handoff
                                                        # 为 Redis/PGMQ 分布式版
```

## 五、深读子页地图（51 页精选 6）

1. **Core Architecture**（L508）— 五大架构原则总纲：帧优先级、双队列模型、multi-worker 全景，先读这页建骨架。
2. **Frame System and Processing**（L742）— 帧类型层次/双向流动/中断时序图/protobuf 序列化，理解一切的根基。
3. **Context Aggregators**（L2257，全 wiki 最大页 20KB）— 用户/助手轮次聚合、函数调用回写、mute 策略的完整机制。
4. **Interruption Handling**（L2884）— barge-in 全链路：广播、清队、TTS 死锁防护、按服务的处理差异。
5. **Turn Detection and User Idle**（L2638）— VAD 状态机 + SmartTurn（ML 判断用户说完没）+ start/stop 策略族，"自然对话感"的工程学。
6. **Worker Architecture and Bus**（L10360）— 三种 bus 后端 + BridgeProcessor 帧跨进程搬运 + 分布式 proxy 拓扑。

（其余值得点名：L1091 Pipeline Architecture、L2026 Context System、L3357 RTVI Protocol、L4969 OpenAI Realtime、L11264 Memory and Persistent Context、L11892 Glossary）

## 六、与"我们"的关系（一句话）

文本 Agent 框架教人"怎么想"，Pipecat 教人"怎么实时地听与说"——它是把 Agent 循环下沉到音频帧/毫秒级流、并直面中断/轮次/延迟三大实时难题的最完整开源实现，讲透系列讲流式与实时 Agent 时的首选对照代码。

---
生成：2026-08-21 · deepwiki 51 页全归档
