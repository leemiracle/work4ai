# webllm-web-worker.md — src/web_worker.ts 精讲：RPC 引擎双端

## 角色定位

`web_worker.ts`（844 行）解决一个浏览器工程问题：**LLM 推理会长时间占满主线程，把 UI 卡死**。它把整个推理引擎搬进 Web Worker 后台线程，同时在主线程提供一个"假引擎"——`WebWorkerMLCEngine` 与 `MLCEngine` 实现同一个 `MLCEngineInterface`，调用方无感切换。文件因此成对定义双端：worker 线程内的 `WebWorkerMLCEngineHandler`（包装真 MLCEngine，按消息 kind 分发任务）与主线程的 `WebWorkerMLCEngine`（把每次方法调用变成 postMessage + Promise）。工厂 `CreateWebWorkerMLCEngine(worker, modelId, ...)` 一步到位建好代理并完成首次加载。这是 WebLLM **最重要的运行时文件**——官方示例默认走 worker 模式。

## 内部结构

**Handler（worker 侧）**：构造器 `new MLCEngine()` 并劫持 `initProgressCallback`——加载进度不是请求-响应，而是主动推送（`{kind: "initProgressCallback", uuid: "", content}`）。核心 `onmessage(event, onComplete?, onError?)` 是一个 19 分支的 switch（消息 kind 见 message.ts）：reload / forwardTokensAndSample / chatCompletionNonStreaming / chatCompletionStreamInit / completionNonStreaming / completionStreamInit / completionStreamNextChunk / embedding / runtimeStatsText / interruptGenerate / unload / resetChat / getMaxStorageBufferBindingSize / getGPUVendor / getMessage / setLogLevel / setAppConfig / customRequest / keepAlive。每个分支走统一的 `handleTask(uuid, task)`：try 里执行并以 `{kind:"return", uuid, content}` 回包，catch 里以 `{kind:"throw", uuid, content: err.toString()}` 回包——**跨线程没有 Error 对象传递，只有字符串**。

**流式三段式**是本文件最精巧的设计：worker 里的 `asyncGenerate` 是 async generator，无法跨线程搬运，于是拆成——①`chatCompletionStreamInit`：在 worker 内调用 engine 拿到 generator，存进 `loadedModelIdToAsyncGenerator: Map<modelId, AsyncGenerator>`（多模型各一份）；②主线程每次要下一个 chunk 就发 `completionStreamNextChunk`（带 selectedModelId 路由），worker 调 `generator.next()` 把单个 chunk 回传；③generator 耗尽时 `next()` 返回 void，主线程据此终止循环。ChatCompletion 与 Completion 共用同一 generator 池。

**reloadIfUnmatched（状态自愈）**：每个推理请求都随带前端期望的 `modelId/chatOpts`（数组形态），handler 用 `areArraysEqual` 与自己记录的实态比对，不一致——典型场景是 service worker 被浏览器杀掉后复活、模型已丢——就自动 `engine.reload()` 重建，再执行本次任务。这让前端不必感知 worker 的死亡。代价是请求消息变胖（每次都携带完整期望状态），且 reload 期间该请求会长时间阻塞——对 Web Worker 这是罕见的边角情形，对随时可能被回收的 service worker 则是生命线，同一套机制服务两种运行时。

**Engine（主线程侧）**：`pendingPromise = Map<uuid, (msg) => void>` 是 RPC 桥的全部状态。`getPromise<T>(msg)` 创建 Promise，把 resolve/reject 包成回调按 uuid 注册，再 postMessage 发出。`onmessage` 按响应 kind 分派：return/throw 查表调回调并删除条目；initProgressCallback 直接调用户回调。`interruptGenerate()` 是唯一 fire-and-forget（不等回包）。`chatCompletion()` 在流式分支先发 StreamInit 再返回本地的 `asyncGenerate(selectedModelId)` 生成器（每次 next 内部发一次 NextChunk 消息）。

**ChatWorker 接口**：`{onmessage, postMessage}` 两成员的最小抽象，使任何形似 worker 的对象（测试 mock、Service Worker）都能复用——这也是为什么 service_worker.ts 与 extension_service_worker.ts 能以继承而非重写的方式扩展双端：传输通道被抽象掉了，消息协议与 RPC 骨架原样继承。

## 外部连接

依赖 message.ts（19 种 Params 与信封类型）、engine.ts（Handler 内包装）、openai 协议（类型）、utils.ts（数组深比较）、support.ts（getModelIdToUse——多模型时主线程也要本地选模型）。被 service_worker.ts / extension_service_worker.ts 继承扩展（Handler 侧改用 clientRegistry/端口回复，Engine 侧改传输通道）；`tests/web_worker_handler.test.ts` 专项守护；index.ts 导出三符号。

## 数据流

一次流式聊天完整时序：主线程 `engine.chat.completions.create({stream:true,...})` → `getModelIdToUse` 本地选定模型 → 发 `chatCompletionStreamInit{request, selectedModelId, modelId, chatOpts}` → Handler reloadIfUnmatched → worker 内建 generator 存 Map → 回 return(null) → 主线程返回本地 generator → UI 每 `next()` 触发一条 `completionStreamNextChunk{selectedModelId}` → worker `generator.next()` 回传 chunk（或 void 终止）→ 循环结束。非流式则一条消息直通：请求进、完整响应回。加载进度走独立推送通道，与请求流并行不悖。

## 设计决策

1. **uuid + 单 Map 的极简 RPC**：不建消息队列、不搞请求对象，回调注册表即全部协议状态，代码量最小且天然支持并发请求。
2. **generator 拆两半跨线程**：worker 持真 generator，主线程持"每次 next 发一条消息"的镜像 generator——流式语义在结构化消息上重建。
3. **期望状态随请求携带**（PR #533/#471 演化而来）：把恢复逻辑放在 handler 侧集中处理，前端零代码获得自愈能力。
4. **logitProcessorRegistry 在 worker 模式显式忽略并 warn**：CPU 回调无法跨线程序列化，注册了也只是警告——接口统一但能力有边界，文档明示。想用 logit processor 又要 worker 不卡 UI 的用户，只能在 worker 脚本内部直接构造 MLCEngine 并注册，再用自定义消息把控制信号传进去，官方示例 logit-processor 演示了这种混合姿势。
5. **错误降级为字符串**：承认跨线程 Error 语义丢失的现实，throw 消息只回 `err.toString()`。

## 新人提示

把 message.ts 当本文件的字典放在手边，对着 switch 画时序图比硬读代码快十倍。写自己的 worker 脚本只需三行：`import { WebWorkerMLCEngineHandler } from "@mlc-ai/web-llm"; const handler = new WebWorkerMLCEngineHandler(); onmessage = handler.onmessage;`。调试技巧：worker 里的 console 输出在 DevTools 的 worker 上下文（Sources 面板单独线程），主线程看不到。测试看 `tests/web_worker_handler.test.ts` 如何用假 worker 注入 onComplete/onError 回调模拟双端。配套精读：`webllm-engine.md`（被包装的真身）与 service_worker.ts（同模式的三态扩展）。
