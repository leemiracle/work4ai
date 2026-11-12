# 02 · Agent Loop：主循环、流式执行与上下文管理

> 证据：minified 源码偏移考古（主循环 `Vtr`[chunk-1kyfp16b offset=4214827] 等），
> 全部结论带 [file+偏移] 锚 [S]。深报告（伪代码全量还原+重试总表+不确定项清单）：
> `rea-claude/reports/02-agent-loop.md`（39KB）。

## 1. 启动链（六层）[S]

```
cli:Lt() → main(Dw)[smbbbrjq:150455]（commander 解析）
  ├ 无头路 Ei → runHeadless → py[ycbg2wrx:157629]
  └ 交互路 $a
       ↓ 两路汇入
  xu 会话工厂[ycbg2wrx:61652] → run:PL 注入 turn 引擎
```

`py`：headless 会话驱动（messageQueue/submitMessage 循环）；`xu`：会话对象工厂
（messages 持久化、abortController 重建、预算巡检 maxBudgetUsd 100ms）。

## 2. 主循环骨架 `Vtr` [4214827] [S]

OSS `query()` 的递归被改写成 **`while(!0)` 状态回卷**：

```
while(!0):                          # 外层 turn 循环 [4218197]
  A. 吸收排队命令/poll 事件折叠进 messages
  B. autocompact(mpt)：阈值判定 → compacted 则摘要替换历史
  C. 组装 systemPrompt 快照 + 流式工具执行器 Ept
  while(内层重试闸):                 # [4230434]
    D. for await DJn(callModel(...), streamingToolExecutor):
         - tool_drain_tick → 排水外发已完成工具结果
         - assistant 块 → tool_use 立即 addTool（★流中即起，不等流结束）
    E. abort 处理 / 补排空 → {reason:"aborted_streaming"}
    F. 恢复型 transition：截断恢复/malformed_tool_use 重试/thinking-only nudge/
       stop-hook 阻断（不打外层）
    G. 无 needsFollowUp → 终止：completed / max_turns / hook_stopped ...
       （reason 全集 11 种，含 rapid_refill_breaker/model_error/cancelled）
    H. 回卷：Me = {messages:[...mr,..._i,...Cl]} → 下一轮 API 调用 [4275397]
```

**消息三分账**：`mr`（turn 起始上下文）/`_i`（本 turn 助手消息）/`Cl`（tool_result+附件），
持有者 `Di`，refusal-fallback 回撤时 reset 重置。

## 3. 流式工具执行（不等流结束）[S]

- `DJn`[4092899] = `Promise.race(模型流 next(), 工具完成通知)`——**模型还在吐字，
  已完成的工具结果就能外发给 UI**；
- `Ept` StreamingToolExecutor[4085847]：队列状态机 `queued→executing→completed→yielded`；
  未知工具名立即产 `<tool_use_error>` tool_result（不中断循环）；
- **并发规则**：仅当无 executing 或全部 executing 并发安全才放行新工具——**串行工具
  会阻塞后续并行工具**；连续 concurrency-safe 工具归组走有界并行
  （`CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`，默认 **10**）；
- abort 时按原因生成合成 tool_result：ESC→interrupted / 转后台→cancelled / 其余→user-rejected。

## 4. autocompact：阈值、熔断、预计算 [S]

| 机制 | 实证 |
|---|---|
| compact 阈值 | `win − 13000`（百分比可覆盖）；分级 blocked(win−3000)/compact/warn(win−20000)/ok |
| 有效窗口 | `window − min(模型上限, 20000)`；auto 默认 1M（sonnet-5 特例 500k） |
| 熔断一 | 连续 3 次 compact 失败 → 本会话不再自动 compact |
| 熔断二 | compact 后 3 turn 内又触发、连续 3 次 → `rapid_refill_breaker`，提示改小批读取或 /clear |
| 摘要生成 | 独立调用："You are a helpful AI assistant tasked with summarizing conversations."，**8 段式模板**（Primary Request/Key Concepts/...），querySource="compact"，禁 prompt caching |
| 预计算 compact | turn 中 arm（Git 闸门），后台预跑分组摘要，下一 turn `precomputed_compact_swap` 换入 |

**microcompact**[4065638]：从时间线收集"大工具"（Read/批量型）的 tool_use id，
保留最近 5 个，仅当可省 ≥20k token 才把旧 tool_result 替换为
"[Old tool result content cleared]"或落盘为 persisted-output（提示用 Read 取回）。
**context_hint**（灰度）：把 compact 决策交给服务端（beta+target_tokens_saved 75000），
422/424 回退本地。

## 5. attachment 与中断 [S]

- 附件类型：queued_command/poll_events/hook_additional_context/edited_text_file/
  dir_sync_notice/hook_deferred_tool 等；注入时机三个（turn 启动/turn 中/工具轮之间）；
  **降级保护：附件产出 0 条则留在队列不丢弃**；
- ESC 中断：会话级 abortController 重建 + 工具级合成错误；abort 原因分类
  turn-abort/background/remote-cancel；
- transcript 重放带 `readFileState` 内容替换——旧文件内容按快照还原（checkpoint 基础）。

## 6. 重试与韧性总表（节选）[S]

| 错误 | 策略 |
|---|---|
| 429 | retry-after 头优先（≤6h）；否则指数退避 500ms·2ⁿ 封顶 32s + 25% jitter |
| 529 overloaded | 限 3 次重试；超限→fallback 换模型；后台查询直接丢弃 |
| 400 beta 不识别 | 剥 beta 重试（会话级 latch） |
| 400 坏媒体块 | 定点摘除 → retry:media-strip |
| thinking 签名被拒 | 全量剥 thinking 块重试 |
| 流空闲 | 事件级 5min 看门狗 + 字节级 watchdog；流式整体失败→非流式回退 |
| 认证失败 | OAuth/CCR/AWS/GCP/apiKeyHelper/WIF 各通道自愈 |
| 工具异常 | `<tool_use_error>` tool_result，**不中断循环** |

默认重试 **10 次**（`CLAUDE_CODE_MAX_RETRIES` 钳 15；watchdog 模式持久重试 6h）。

## 7. 手搓启示（→ rl-and-agents/）

1. **递归改 while 回卷**是生产实现的选择——栈深度可控、状态可打点；
2. 流中即起工具（不等 stop_reason）是延迟关键优化，mini 版可先做"流结束再执行"；
3. compact 三件套（阈值+双熔断+8 段模板）比"截断"聪明得多：失败有熔断、回填有诊断；
4. 中断合成 tool_result 保证 messages 永远闭合（无悬空 tool_use）——**上下文完整性
   是 API 协议层的硬约束**，手搓时最容易踩；
5. 恢复型 transition（F 步）不打外层循环：错误恢复是循环内部的一等状态机。
