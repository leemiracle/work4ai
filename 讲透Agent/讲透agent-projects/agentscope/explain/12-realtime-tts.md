# 12 realtime+tts 实时语音：双工模型桥与语音合成双形态

（锚相对 `src/agentscope/`，行号经源码核实）

## 1. 角色定位

语音双子包分工明确：**realtime** 是全双工实时对话通道——WebSocket 直连 OpenAI/Gemini/DashScope 的多模态实时模型，边收音频边出音频还带工具调用；**tts** 是单向文本转语音（5 家 6 模型）。两者都不做音频处理本身（重采样、播放归前端），只做"协议桥"：块翻译成各家 websocket/HTTP 方言，各家事件翻译回统一事件层。

## 2. 内部结构

**realtime 基座是模板方法**：`RealtimeModelBase`（`realtime/_base.py:13`）包揽连接生命周期——`connect` 建 websocket（`realtime/_base.py:86`）、起后台接收任务（`realtime/_base.py:91`）、发首帧 session 配置（`realtime/_base.py:96`）；接收循环 `_receive_model_event_loop`（`realtime/_base.py:134`）把每条消息交给子类的 `parse_api_message`（`realtime/_base.py:159`）翻译成统一事件再投 outgoing 队列。子类只实现 send、URL/header 构造、事件解析三件事，差异全部集中在构造期：OpenAI 用模板 URL 加 `Authorization: Bearer` 头（`realtime/_openai_realtime_model.py:76`）；DashScope 同样走 header（`realtime/_dashscope_realtime_model.py:88`）；Gemini 则把 key 拼进 URL（见坑 1）。

**事件层**：`realtime/_events/_model_event.py` 定义 `ModelEventType` 枚举（`realtime/_events/_model_event.py:13`）与 pydantic 化的 `EventBase`（`realtime/_events/_model_event.py:88`），17 种事件覆盖音频增量、转录增量、工具调用、错误（`realtime/_events/_model_event.py:318`）与 websocket 生死。

**tts 是真 ABC + 双形态**：`TTSModelBase(ABC)`（`tts/_tts_base.py:12`）用 `supports_streaming_input` 标志分流（`tts/_tts_base.py:31`）——非流式模型只须实现 `_call_api`；流式模型（CosyVoice Realtime）额外实现 connect/push/synthesize，async context manager 自动管理连接。响应统一为 `TTSResponse`（content 是 AudioBlock、带 is_last 结束标志），流式音频经回调类攒块。

## 3. 外部连接

`RealtimeAgent`（`agent/_realtime_agent.py:28`）是 realtime 的唯一仓内消费者：三队列架构（incoming/model_response/outgoing），`start` 时调 `model.connect`（`agent/_realtime_agent.py:110`），模型事件分拣后音频块出 outgoing 队列给前端、ToolUseDone 事件触发 toolkit 执行再回注。tts 反而**不依赖 agent**——可直接对任意 Msg 流做合成。依赖上 realtime extra 只需 websockets>=14 与 scipy。

## 4. 数据流

realtime 环：麦克风音频 → AudioBlock(base64) → `model.send` → websocket → 服务端事件 → `parse_api_message` → 统一 ModelEvent → outgoing 队列 → 前端播放/agent 执行工具 → ToolResultBlock 再 send 回流。tts 流式环：Msg 文本分块 `push` → SDK 回调 on_data 攒音频块 → `synthesize` 收尾返回最终 TTSResponse；非流式则一次 `_call_api` 直接拿完整音频。

## 5. 设计决策

①**模板方法收编连接生命周期**：重连、任务取消、关闭顺序只写一遍，三家实现退化成"方言表"。②**事件 pydantic 化**：agent 消费面与供应商解耦，新增供应商不触碰 agent 代码。③**tts 用正规 ABC+标志位双形态**：非流式实现者零负担，与 realtime 基座的装饰性 abstractmethod 形成对照。④**三家 key 位置跟随上游官方姿势**（两家 header、一家 URL query），不强推统一抽象。

## 6. 新人提示

- 坑 1（必写，密钥泄漏风险）：`GeminiRealtimeModel` 把 api_key 明文拼进 websocket URL——模板自带 `?key=` 后缀（`realtime/_gemini_realtime_model.py:32`），构造时 `self.websocket_url = self.websocket_url + api_key`（`realtime/_gemini_realtime_model.py:85`）。该 URL 是公开实例属性并被传入 `websockets.connect`（`realtime/_base.py:86`）：连接失败的异常链、代理/网关访问日志、任何打印该属性的行为都可能带出完整 key。对照 OpenAI/DashScope 均走 Authorization header。**切勿 log websocket_url**。
- 坑 2：`DashScopeCosyVoiceRealtimeTtsModel` 构造时执行 `dashscope.api_key = api_key`（`tts/_dashscope_cosyvoice_realtime_tts_model.py:103`）——这是**进程级全局赋值**，会波及同进程内所有 dashscope 调用（含 chat/embedding 模型）的默认凭据。
- 坑 3：`RealtimeModelBase` 的 `@abstractmethod` 同样没有 ABCMeta（`realtime/_base.py:13` 纯 class）——自研 realtime 模型漏实现 `send`/`parse_api_message` 不会在实例化期报错。
- 坑 4：误把 `supports_streaming_input=True` 却不实现 connect/push，进 async with 即抛 NotImplementedError——`tts/_tts_base.py:52` 起的上下文管理器会无条件调用它们。
- 坑 5：Gemini 换音色（默认 Puck，`realtime/_gemini_realtime_model.py:54`）只能在构造时指定，session 中途不支持改。
