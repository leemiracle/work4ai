# 精讲：C++ 引擎核心与线程化外壳

> 位置：`cpp/serve/engine.cc`（1102 行）+ `threaded_engine.cc`（417 行）
> 图谱：engine.cc 扇出 16

## 角色定位

两文件是 C++ 引擎的「发动机+变速箱」：

- **EngineImpl 是发动机**——持模型/KV cache/采样器/动作列表，实现请求状态机与每步调度。
- **ThreadedEngineImpl 是变速箱**——包进后台线程，对外线程安全 AddRequest/Abort/Reload；注册为 TVM Module（`mlc.serve.async_threaded_engine`），Python/Swift/Kotlin 同入口驱动。

engine.cc 还有 `MockEchoEngineImpl` 回显测试替身。

## 内部结构

**EngineImpl::Create 是装配流水线**：①解析 model_lib 与 config → ②AutoDecideEngineConfig 按 mode 推断容量（server 吃满显存）→ ③prefix cache（radix+LRU 或 disable）→ ④逐模型 LoadParams+CreateKVCache+workspace → ⑤Tokenizer+**xgrammar 语法缓存** → ⑥投机解码建 DraftTokenWorkspaceManager（容量×2 乒乓，EAGLE 加 hidden states 区）→ ⑦`CreateEngineActions` 组动作 → ⑧SetThreadMaxConcurrency。

**Step() 是心跳，仅十几行**：

```cpp
for (EngineAction action : actions_) {
  processed = action->Step(estate_);
  if (!processed.empty()) {
    ActionStepPostProcess(...);  // 采样→收尾→流式回调
    return;                      // ★ 每步只执行一个动作
  }
}
```

「**一步一动作**」不变式：ThreadedEngine 每轮 drain 指令后调一次 Step，动作天然串行，estate_ 免动作级锁。

**AddRequest 分支树**：special_request（查 metrics）直接回调 → 超长 StreamBackError → **disagg**（PD 分离三型，KV 窗口截断+跨节点元数据校验）→ 正常路径：tokenize、push waiting_queue、按 n 建 RequestStateEntry 树（rng_seed 偏移保分支互异）、grammar 挂载。

**ThreadedEngineImpl 指令队列模型**：六指令（Add/Abort/Unload/Reload/Reset/Debug）进 instruction_queue_，`RunBackgroundLoop` 被 cv 唤醒后 drain 再 Step()。**双后台线程**：本循环+`RunBackgroundStreamBackLoop` 批量回传——回传与驱动分离，回调慢不阻塞 GPU。Reload/Unload 有完成信号量，「先置 flag 再发指令」否则死锁。

## 外部连接

- **imports**：engine_actions/、engine_state、logit_processor、sampler、xgrammar、NVTX
- **被依赖**：threaded_engine 持 background_engine_；json_ffi_engine 再包 ThreadedEngine
- **注册面**：`mlc.serve.create_threaded_engine` 由 STATIC_INIT_BLOCK 注册——Python 端 get_global_func 的正是它
- **多 GPU**：CreateDiscoSession 按 shards×stages 建 NCCL/RCCL 池（依赖 Python 启动器）

## 数据流

```
AddRequest → tokenize → waiting_queue → [NewRequestPrefill]
  ↘ radix match 命中跳过，分块 prefill → 首token → running_queue
→ [BatchDecode] 每步全 batch 一个 token
   ↘ token 边界变化 → RetokenizeWithNewToken 回退重分词
→ 停止/满长 → 移除请求、RecycleId、radix 保留待复用
→ 全程 RequestStreamOutput → StreamBackLoop → 宿主回调

投机解码: [BatchDraft 产候选]→[BatchVerify 概率接受]
EAGLE: EagleBatchDraft(tree 产树)→EagleBatchVerify(tree verify)
```

## 设计决策

1. **一步一动作**：牺牲吞吐上限换调度可预测+状态免锁；违约 ICHECK fatal。
2. **双线程回传**：推理线程只塞队列，回调尖峰不影响 Step 节奏。
3. **MockEcho 同接口**：参数传递回归用假引擎。
4. **disagg 走普通通道**：特殊请求+两专属动作复用 prefill 骨架——侵入面最小。
5. **Unload 清内存池**：显式调 `vm.builtin.memory_manager.clear`，防重载后显存虚高。

## 新人提示

- **读调度从 `action_commons.cc` 的 CreateEngineActions 入手**：动作按模式组装、优先级，一份函数看全貌。
- **改 prefill 先看 batch_prefill_base.cc**：四变体共享骨架，通用逻辑别加在单变体。
- **死锁排查**：Reload/Unload flag 顺序、StreamBack notify 时机、Exit 双 cv 唤醒。
- **性能剖析**：EventTraceRecorder 出 Chrome tracing；NVTX 已埋点。
- **契约**：引擎必回 usage 块（错误路径也补 dummy）——上层 final chunk 判定依赖它。
