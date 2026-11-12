# 01 · ChatSessionTask——WebUI 服务端的会话编排总管

> 源：`microservices/ace_agent/4.1/webui/server/chat-session/tasks/ChatSessionTask.ts`（389 行）；配套 `AbstractTask.ts`（84 行）、`clients/` 三客户端、`index.ts`（186 行）

## 一、角色定位

WebUI 服务端是 Node WebSocket 网关：浏览器一条 WS 连接，背后可挂三种文本接口（Redis UMIM、gRPC、HTTP）+一条 gRPC 语音流。ChatSessionTask 是**每会话的总管任务**——`index.ts:169-183` 的 `wss.on("connection")` 每接受一条连接就 new 一个实例并 `session.start()`，一个标签页一个实例、一个 `randomUUID()` streamID（`ChatSessionTask.ts:64`）。它不碰协议，只做三件事：**装配**（按"文本 profile × 客户端可用性 × 语音开关"实例化子任务，`initTasks()` 137-186）、**调度**（文本/语音切换按子任务声明的 interactionModes 启停，`refreshTasks()` 246-266）、**收尾**（连接关闭/SIGTERM/子任务致命错误统一 stop+cleanup）。类头自述 "This task is responsible for managing other tasks"（43-54）——纯编排层，server 目录的入口文件。

## 二、内部结构

### 2.1 AbstractTask 生命周期契约

基类（`AbstractTask.ts:26`）契约极小：抽象属性 `interactionModes`（:30）声明本任务支持文本还是语音，是 refreshTasks 启停唯一判据；`start()`（51-53）只新建 `AbortController`；`stop()`（60-64）只 `abort()`；`isRunning()`（70-75）查信号；`cleanup()`（83）默认空钩子。**abort 信号是唯一停止通道**——子类不覆写 stop 而把长驻监听挂到 abortController 上，"可反复启停"由此成为语言机制。

### 2.2 构造（80-88）

四参：`ws`、`emojiFinder`（可空）、`aceAgentTextChatInterface: "server"|"grpc"|"event"`、`isSpeechEnabled`。`super(new EventEmitter())`（86）——**eventBus 会话级私有而非全局**，多标签页互不串音。构造里即调 `initTasks()`，装配先于 start。自身声明 SPEECH+TEXT 双支持（56-59），总管永不被模式切换关掉。

### 2.3 initTasks 装配矩阵（137-186）

先探测三客户端可用性（138-140）：**WebSocketTask 恒开**（142，浏览器侧听/说代理）；文本三分支（144-169）：`grpc`→GRPCTextTask、`event`→UMIMTask、`server`→HTTPChatTask，客户端不可用直接 throw（fail-fast）；语音叠加（171-185）：`--speech` 必须有 gRPC 否则 throw（181-184），开 GRPCSpeechTask，**唯独 event 模式不开 GRPCSpeechTranscriptionTask**（177-179）——该模式下 bot 转写已由 UMIMTask 经 Redis 处理，重复开会双路竞争。组合 = 3 profile × 语音开关，最多同时 4 个子任务。

### 2.4 start() 六路并行（111-131）

`Promise.all` 挂六路：四个监听 + `refreshTasks(TEXT)`（默认文本拉起）+ `sendServerConfig()`。`AbortError` 显式吞掉（123-127，自身 stop 时 once 被 abort 的正常形态），其余升级 `fatalError`（128-129）。监听器两型：关闭/SIGTERM 用 `once` 单发（283-288、294-303）；切换/致命错误用 `while(isRunning())` 循环 `once` 续订（308-318、323-332）。SIGTERM 分支 stop→cleanup→`sleep(1000)` 留优雅窗（301）→`process.exit()`——**一个会话替整个进程收尸**。

### 2.5 三条收尾路径

关标签页（`userClosedSocket`→283-288）；SIGTERM（294-303，exit 整进程）；子任务致命错误（`fatalError`→354-361，emit `shutdown` 带文案 + stop）。`stop()`（367-379）先发 `shutdown`（WebSocketTask 转发浏览器"请刷新"），再 super.stop()，最后逐个停子任务。`cleanup()`（94-105）逐任务 await 且**逐个 try/catch 吞异常**——清理是尽力而为，单任务炸不连累其余释放。

### 2.6 对外广播（271-277）

启动即发 `ServerConfig {CONFIG_CHANGE, speechSupported}`（`shared/types.ts:95-98`），前端据此渲染语音开关。

## 三、外部连接

**上游**：`index.ts:172-182` 创建并 start；`--speech` 开关（`index.ts:160`）；emojiFinder 只在 event 模式加载（`index.ts:163-165`），他模式传 null。**下游六类子任务**统一签名 `(eventBus, streamID)`（193/202/210/219/228），唯 WebSocketTask 加 emojiFinder 与原始 ws（237）。**客户端三件套**：GRPCClient 是 connect-rpc PromiseClient 单例（`GRPCClient.ts:30-50`，transport 强制 httpVersion "2"）；RedisClient 懒连接单例（`RedisClient.ts:23-41`）；HTTPClient 只是 fetch 加域名前缀的薄包装（`HTTPClient.ts:29-42`）。**事件名**：收 `userToggledSpeech`/`fatalError`/`userClosedSocket`，发 `serverConfigChange`/`shutdown`。

## 四、数据流

文本模式一条消息的旅程：浏览器→WS→WebSocketTask 事件化→eventBus→（UMIM|GRPCText|HTTPChat 三选一）→Redis pub-sub / gRPC 流 / HTTP→ACE Agent→回程事件→WebSocketTask→浏览器。**ChatSessionTask 不在数据路径上，只在控制面**：streamID（`getStreamID()` 386-388）注入每个子任务，是各 pipeline 关联同一会话的粘合剂；模式切换由它消费并转成子任务 start/stop（308-318→246-266）。

## 五、设计决策（从代码反推）

1. **编排与业务彻底分离**：总管 389 行零协议细节；加第四种接口只需 switch 加 case（144）加一个 enable 方法。
2. **AbortController 作统一生命周期语言**：`once(emitter, name, signal)` 原生支持信号，abort 后监听自动解除。
3. **fail-fast 不降级**：profile 与客户端不匹配直接 throw（146-149）——后端选型是部署期决策，运行期悄悄换通路比报错更糟。
4. **会话级私有 eventBus**（86）：跨会话要另走通道，换来多用户天然隔离。
5. **isAvailable 语义陷阱**：三 URL 在 `config.ts:18-28` 全有默认值（`REDIS_URL ?? "redis://localhost:6379"`），故 `!!REDIS_URL` 判断（`RedisClient.ts:38-40`）**未设环境变量时也返回 true**，throw 分支只有显式设空串才可达；`GRPCClient.ts:26-27` 注释与代码不符——真实语义是"未设即用 localhost 默认值"。
6. **cleanup 吞异常**（98-103）：避免一个 Redis 残留阻塞其他任务释放。

## 六、新人提示

- **先问"这是总管的活吗"**：协议细节一律去子任务文件。
- **event 模式转写去重**：加语音功能记得 175-179——UMIMTask 已覆盖 bot 转写，别在 event 模式再开 GRPCSpeechTranscriptionTask。
- **模式切换 bug 先看 refreshTasks**（246-266）：声明式启停——新任务忘在 `interactionModes` 声明 SPEECH，切语音时被静默停掉且无报错。
- **SIGTERM 是进程级**（294-303）。
- **测试入口**：无总管直接单测，仿照 `WebSocketTask.test.ts` 对 eventBus 事件断言最省事。

## 甄别记录

派发任务书称"四 profile 四运行形态"；源码实证为**三种文本 profile**（`index.ts:150-158`）×语音开关，本文按源码口径。图谱 lineRange [51,389] 与源码核对（类声明实为 55 行起），无冲突。
