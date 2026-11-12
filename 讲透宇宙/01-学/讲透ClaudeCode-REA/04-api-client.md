# 04 · API 客户端与模型路由

> 证据：minified 源码偏移考古 + 内嵌 SDK（完整 Anthropic TS SDK 打包在
> chunk-862be30b.js）+ 烘焙模型目录（chunk-454hy5ah.js）[S]；内嵌官方文档
> models/prompt-caching 缓存 [D]。深报告（19 模型全表+四层 fallback+SSE 累积器+
> gateway 附录）：`rea-claude/reports/04-api-client.md`（45KB）。

## 1. 端点与协议 [S]

- 端点族：`/v1/messages`（+ count_tokens / models / files / oauth）；
  `anthropic-version: 2023-06-01`；
- 会话头：`x-app: cli|cli-bg`、`X-Claude-Code-Session-Id`、
  `x-claude-code-agent-id/parent-agent-id`（subagent 链路）、7 个 x-claude-* 头；
  `ANTHROPIC_CUSTOM_HEADERS` 按行 `Name: value` 注入；
- 认证三形态：静态 `x-api-key` / OAuth Bearer（beta `oauth-2025-04-20`）/
  OIDC federation；**OAuth 过期由重试引擎自愈刷新（换凭据不换模型）**；
- **Bedrock 原生流是 AWS 二进制 eventstream 非 SSE**；3 个 beta
  （interleaved-thinking/context-1m/tool-search-tool）必须从 header 挪进 body
  `anthropic_beta`；**Bedrock 无 countTokens API**——兜底 = 发 `max_tokens:1`
  真请求读 usage.input_tokens；
- Vertex region 解析：14+ 个逐模型 env `VERTEX_REGION_CLAUDE_*`，全局默认
  `CLOUD_ML_REGION || "us-east5"`；region→endpoint 三分（global/us/eu/区域）。

## 2. SSE 累积器与服务端换模型 [S]

事件归并：message_start → content_block_start → delta 族 → message_delta(stop_reason)
→ message_stop。**关键协议：流内 `type:"fallback"` content block 携带
`to.model`，累积器直接改写 `message.model`**——服务端换模型对客户端零额外协商。
stop_reason 全集 8 种：end_turn/max_tokens/stop_sequence/tool_use/pause_turn/
compaction/refusal/model_context_window_exceeded。

首字节看门狗 30s（`tengu_api_slow_first_byte`）；代理指纹表按 Server 头识别 19 种
中间盒；gateway 规范：静默期自发 `event: ping` 防长思考空闲超时。

## 3. 模型目录（19+1 条目，v2.1.261 烘焙）[S]

| 梯队 | 条目 | 要点 |
|---|---|---|
| 旗舰 | fable-5 / **fable-5-1**（"best" 默认） | 1M 原生；tier_10_50；per_turn_effort（5.1） |
| 旗舰 | opus-4-7/4-8/**opus-5** | 1M 原生；fast_mode（4-8）；refusal_fallback（5） |
| 中坚 | **sonnet-5**（tier_2_10 最便宜 1M） | xhigh_effort；cost_index low .47→max 5.59 |
| 中坚 | sonnet-4-5/4-6, opus-4-5/4-6 | 200k+1m 后缀 |
| 轻量 | haiku-4-5 / 3.5 | advisor_rank 1（用作 advisor/小模型） |
| 隐藏 | mythos-5/5-1（仅 first-party）、mythos-preview | 目录外第 20 个 ID |

- 别名表：opus/sonnet/haiku/fable/best + `[1m]` 后缀 + `opusplan`（plan 用 Opus
  其余 Sonnet）；**别名解析是 per-provider 的**（gateway 的 opus→4-7、foundry→4-6）；
- **wire ID 映射 `AC(model)`**：剥后缀→反查短名→provider 表→**别名永不上线**；
- 退役表带 per-provider 日期（如 sonnet-4-0：first-party 2026-06-15、bedrock
  2026-10-14、vertex 2026-09-14）；
- 默认解析链：--model / 已保存选择 → `ANTHROPIC_MODEL` → settings → 分层默认
  （订阅→Opus；first-party→Sonnet；bedrock/vertex→Opus）。

## 4. 四层 fallback 链 [S]

1. **目录级 fallback_3p**（第三方专用）：opus-5→4-8→…逐级回退；
2. **first-party 可用性链**：fable 不可用→opus→sonnet→haiku 逐级找
   （`CLAUDE_CODE_NO_MODEL_FALLBACK=1` 可坍缩）；
3. **用户链**：`--fallback-model` 逗号分隔，**最多 3 个**；
4. **运行时触发**：连续 3 次 529→"overloaded" 换模；404→model_not_found；
   500 级→last_resort。UI 提示 "completed by X. Your session model is unchanged."
5. 叠加**服务端 fallback**（beta server-side-fallback + fallback-credit）——
   refusal 也能换模型重答。

subagent 模型继承：`CLAUDE_CODE_SUBAGENT_MODEL`（默认 inherit=父模型）；
frontmatter model 支持 alias/ID/'inherit'；FORCE=1 时 Task 的 model 参数被丢弃。

## 5. 请求组装与成本旋钮 [S]

- system 是**数组**（多块 + cache_control 断点分层缓存）；
- max_tokens 默认查目录（如 32000/64000），`max_tokens` 超 context 的 400 会
  **自愈式下调**重试；
- thinking 双形态：adaptive（预算由服务端）/ enabled（budget_tokens，上限
  upperLimit−1）；**effort 五档**（low/med/high/xhigh/max）带每模型 cost_index；
- prompt caching：`cache_control: ephemeral` 5m/1h 双 TTL（1h 需订阅白名单），
  cache_write_5m=1.25×input、1h=2×、read=0.1×；>200k token 自动切 1h（阈值 UF）；
- 配额探测：读 `anthropic-ratelimit-unified-*` 响应头族（五小时窗口）；
- 1M context：`[1m]` 后缀 + beta `context-1m-2025-08-07`。

## 6. 重试引擎 [S]

`UIe`（retries-with-recovery，替代 SDK maxRetries）：默认 **10 次**
（`CLAUDE_CODE_MAX_RETRIES` 钳 15；watchdog 模式持久重试 6h）；退避
500ms·2ⁿ 封顶 32s + 25% jitter；429 的 retry-after 头优先（≤6h）；认证失败
按通道自愈（OAuth/CCR/AWS/GCP/apiKeyHelper/WIF）。

## 7. 意外发现：内嵌 inference gateway [S]

chunk-nghm5b5a.js 打包了完整的**本地多上游 inference gateway 服务器**及
"如何写 Claude Code 兼容代理"规范文档（§8 of 深报告）——Bedrock 流转 SSE、
ping 保活、头转发白名单、501 兜底全有——第三方网关实现的免费参考实现。

## 8. 手搓启示（→ rl-and-agents/）

1. 别名→wire ID 在**发请求前最后一步解析**（目录+provider 双表）——路由是纯函数；
2. fallback 是多层防御纵深：目录级/可用性/用户/运行时触发/服务端，每层职责单一；
3. SSE 累积器把协议事件归并成 message 对象——手搓时这就是 60 行的状态机，
   `fallback` block 改 model 一行代码就接上服务端换模；
4. cache_control 分层断点是 agent 省钱的最大杠杆（system/tools 前缀稳定）；
5. "认证自愈不换模型"与"过载换模型不换凭据"分离——两类故障正交处理。
